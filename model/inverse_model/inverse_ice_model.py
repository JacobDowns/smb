#import h5py
from dolfin import *
from support.physical_constants import *
from support.momentum_form import *
from support.mass_form import *
from support.length_form1 import *

parameters['form_compiler']['cpp_optimize'] = True
parameters["form_compiler"]["representation"] = "uflacs"
parameters['form_compiler']['quadrature_degree'] = 4
parameters['allow_extrapolation'] = True


""" Solves for surface mass balance given length. """

class InverseIceModel(object):

    def __init__(self, model_inputs, out_dir, replay_file, constants = None, set_forms = None):

        # Model inputs object
        self.model_inputs = model_inputs
        # Mesh
        self.mesh = model_inputs.mesh
        # Model time
        self.t = 0.
        # Physical constants / parameters
        self.constants = pcs


        #### Function spaces
        ########################################################################

        # Define finite element function spaces.  Here we use CG1 for
        # velocity computations, DG0 (aka finite volume) for mass cons,
        # and "Real" (aka constant) elements for adot

        E_cg = self.model_inputs.E_cg
        E_dg = self.model_inputs.E_dg
        E_r = self.model_inputs.E_r
        E_V = MixedElement(E_cg, E_cg, E_cg, E_dg, E_r)

        V_cg = self.model_inputs.V_cg
        V_dg = self.model_inputs.V_dg
        V_r = self.model_inputs.V_r
        V = FunctionSpace(self.mesh, E_V)

        # For moving data between vector functions and scalar functions
        self.assigner_inv = FunctionAssigner([V_cg, V_cg, V_cg, V_dg, V_r], V)
        self.assigner     = FunctionAssigner(V, [V_cg, V_cg, V_cg, V_dg, V_r])

        self.V_cg = V_cg
        self.V_dg = V_dg
        self.V_r = V_r
        self.V = V


        ### Model unknowns + trial and test functions
        ########################################################################

        # U contains both velocity components, the DG thickness, the CG-projected thickness,
        # and the length
        U = Function(V)
        # Trial Function
        dU = TrialFunction(V)
        # Test Function
        Phi = TestFunction(V)

        # Split vector functions into scalar components
        ubar, udef, H_c, H, adot = split(U)
        phibar, phidef, xsi_c, xsi, chi = split(Phi)

        # Values of model variables at previous time step
        un = Function(V_cg)
        u2n = Function(V_cg)
        H0_c = Function(V_cg)
        H0 = Function(V_dg)
        adot0 = Function(V_r)

        self.ubar = ubar
        self.udef = udef
        self.H_c = H_c
        self.H = H
        self.adot = adot
        self.phibar = phibar
        self.phidef = phidef
        self.xsi_c = xsi_c
        self.xsi = xsi
        self.chi = chi
        self.U = U
        self.Phi = Phi
        self.un = un
        self.u2n = u2n
        self.H0_c = H0_c
        self.H0 = H0
        self.adot0 = adot0

        # Time step
        dt = Constant(1.0)
        self.dt = dt
        # 0 function used as an initial velocity guess if velocity solve fails
        self.zero_guess = Function(V_cg)


        ### Input functions
        ########################################################################

        # Bed elevation
        B = Function(V_cg)
        # Basal traction
        beta2 = Function(V_cg)
        # Length
        L = Constant(0.0)
        # Rate of change of length
        dLdt = Constant(0.0)
        # Ice stream width
        width = Function(V_cg)

        self.B = B
        self.beta2 = beta2
        self.L = L
        self.dLdt = dLdt
        self.width = width
        # Facet function marking divide and margin boundaries
        self.boundaries = model_inputs.boundaries


        ### Function initialization
        ########################################################################

        # Initialize initial thickness
        H0.assign(model_inputs.H0)
        #H0.vector()[:] += 1.0
        H0_c.assign(model_inputs.H0_c)
        # Initialize adot
        adot0.assign(Constant(2.))
        # Initialize guesses for unknowns
        self.assigner.assign(U, [self.un, self.u2n, H0_c, H0, adot0])


        ### Derived expressions
        ########################################################################

        # Ice surface
        S = B + H_c
        # Ice surface as DG function
        S_dg = B + H
        # Time derivative
        dHdt = (H - H0) / dt
        # Overburden pressure
        P_0 = Constant(self.constants['rho']*self.constants['g'])*H_c
        # Water pressure
        P_w = Constant(0.8)*P_0
        # Effective pressure
        N = P_0 - P_w
        # Surface mass balance expression
        self.adot_prime = model_inputs.get_adot_exp(S_dg, adot)


        self.S = S
        self.S_dg = S_dg
        self.dHdt = dHdt
        self.dt = dt
        self.P_0 = P_0
        self.P_w = P_w
        self.N = N


        ### Variational Forms
        ########################################################################

        # Momentum balance residual
        momentum_form = MomentumForm(self)
        R_momentum = momentum_form.R_momentum

        # Continuous thickness residual
        R_thickness = (H_c - H)*xsi_c*dx

        # Mass balance residual
        mass_form = MassForm(self)
        R_mass = mass_form.R_mass
        # Function for writing adot prime
        self.adot_prime_func = Function(V_cg)

        # Length residual
        length_form = LengthForm(self)
        R_length = length_form.R_length

        # Total residual
        R = R_momentum + R_thickness + R_mass + R_length
        J = derivative(R, U, dU)


        ### Variational solver
        ########################################################################

        # Define variational problem subject to no Dirichlet BCs, but with a
        # thickness bound, plus form compiler parameters for efficiency.
        ffc_options = {"optimize": True}
        problem = NonlinearVariationalProblem(R, U, bcs=[], J=J, form_compiler_parameters = ffc_options)

        # Solver parameters
        self.snes_params = {'nonlinear_solver': 'newton',
                      'newton_solver': {
                       'relative_tolerance' : 5e-14,
                       'absolute_tolerance' : 8e-5,
                       'linear_solver': 'mumps',
                       'maximum_iterations': 100,
                       'report' : False
                       }}

        self.problem = problem


        ### Start a replay file, that allows replaying the run in the forward model
        ########################################################################
        self.out_file = HDF5File(mpi_comm_world(), out_dir + '/' + replay_file + ".hdf5", 'w')

        ### Write bed data
        self.out_file.write(self.model_inputs.B_mesh, "B_mesh")
        self.out_file.write(self.model_inputs.B_data, "B_data")
        self.out_file.write(self.model_inputs.domain_length, "domain_length")

        ### Write variables
        self.out_file.write(self.mesh, "mesh")
        self.out_file.write(self.H0, "H0")
        self.out_file.write(self.H0_c, "H0_c")
        L0_write = Function(self.V_r)
        L0_write.assign(Constant(self.model_inputs.L_init))
        self.out_file.write(L0_write, "L0")
        self.out_file.write(self.boundaries, "boundaries")
        self.out_file.flush()


        ### Setup some stuff for time iteration
        ########################################################################

        # Get the time step from input file
        self.dt.assign(self.model_inputs.dt)
        # Number of steps
        self.steps = self.model_inputs.N
        # Iteration count
        self.i = 0
        # Write the time step we used
        dt_write = Function(self.V_r)
        dt_write.assign(self.dt)
        self.out_file.write(dt_write, 'dt')


    # Assign input functions from model_inputs
    def update_inputs(self, i, t, dt):
        self.model_inputs.update_inputs(i, t, dt)
        # Update time
        self.L.assign(self.model_inputs.L)
        self.dLdt.assign(self.model_inputs.dLdt)
        self.B.assign(self.model_inputs.B)
        self.beta2.assign(self.model_inputs.beta2)
        self.width.assign(self.model_inputs.width)


    # Take N steps of size dt
    def step(self):
        if self.i < self.steps:
            # Update input functions which depend on length L
            self.update_inputs(self.i, self.t,  float(self.dt))

            print self.i, self.t, float(self.L), float(self.adot0)
            #plot(self.H0_c, interactive = True)

            try:
                solver = NonlinearVariationalSolver(self.problem)
                solver.parameters.update(self.snes_params)
                solver.solve()
            except:
                solver = NonlinearVariationalSolver(self.problem)
                solver.parameters.update(self.snes_params)
                solver.parameters['newton_solver']['error_on_nonconvergence'] = False
                solver.parameters['newton_solver']['relaxation_parameter'] = 0.9
                solver.parameters['newton_solver']['report'] = True
                #self.assigner.assign(self.U, [self.zero_guess, self.zero_guess,self.H0_c, self.H0, self.adot0])
                solver.solve()

            # Update previous solutions
            self.assigner_inv.assign([self.un, self.u2n, self.H0_c, self.H0, self.adot0], self.U)
            # Print current time, max thickness, and adot parameter
            print self.t, self.H0.vector().max(), self.H0.vector().min(), float(self.adot0), float(self.dLdt)
            # Write inputs for this time
            #self.checkpoint()
            self.adot_prime_func.assign(project(self.adot_prime, self.V_cg))
            #plot(self.adot_prime_func, interactive = False)

            # Update time
            self.t += float(self.dt)
            self.i += 1

            return float(self.adot0), float(self.L)


    # Reset the model so we can re-run the simulation
    def reset(self):

        print "reset"
        self.t = 0.0
        self.i = 0
        self.H0.assign(self.model_inputs.H0)
        self.H0_c.assign(self.model_inputs.H0_c)
        self.adot0.assign(Constant(2.))
        self.un.assign(self.zero_guess)
        self.u2n.assign(self.zero_guess)
        self.assigner.assign(self.U, [self.un, self.u2n, self.H0_c, self.H0, self.adot0])


    # Write inputs for forward model
    def checkpoint(self):
        #self.adot_prime_func.assign(project(self.adot_prime, self.V_cg))
        #self.out_file.write(self.adot_prime_func, "adot", self.t)
        self.out_file.write(self.adot0, "adot0", self.t)
        self.out_file.flush()


    # Write out a steady state file
    def write_steady_file(self, output_file_name):
        output_file = HDF5File(mpi_comm_world(), output_file_name + '.hdf5', 'w')

        ### Write bed data
        output_file.write(self.model_inputs.B_mesh, "B_mesh")
        output_file.write(self.model_inputs.B_data, "B_data")
        output_file.write(self.model_inputs.width_data, "width_data")
        output_file.write(self.model_inputs.domain_length, "domain_length")

        ### Write variables
        output_file.write(self.mesh, "mesh")
        output_file.write(self.H0, "H0")
        output_file.write(self.H0_c, "H0_c")
        L0_write = Function(self.V_r)
        L0_write.assign(self.L)
        output_file.write(L0_write, "L0")
        output_file.write(self.boundaries, "boundaries")
        output_file.flush()
        output_file.close()
