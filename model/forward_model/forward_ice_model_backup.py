#import h5py
from dolfin import *
from support.physical_constants import *
from support.momentum_form import *
#from support.momentum_form_fixed_domain import *
from support.mass_form import *
#from support.mass_form_fixed_domain import *
from support.length_form import *
import matplotlib.pyplot as plt

parameters['form_compiler']['cpp_optimize'] = True
parameters["form_compiler"]["representation"] = "uflacs"
parameters['form_compiler']['quadrature_degree'] = 4
parameters['allow_extrapolation'] = True

class ForwardIceModel(object):

    def __init__(self, model_inputs, out_dir, checkpoint_file, model_options = {}):

        # Model inputs object
        self.model_inputs = model_inputs
        # Mesh
        self.mesh = model_inputs.mesh
        # Model time
        self.t = 0.
        # Physical constants / parameters
        self.constants = pcs
        # Model options dictionary
        self.model_options = model_options
        # Max domain length
        #if 'fix_domain' in model_options:
        #    self.fix_domain = model_options['fix_domain']


        #### Function spaces
        ########################################################################

        # Define finite element function spaces.  Here we use CG1 for
        # velocity computations, DG0 (aka finite volume) for mass cons,
        # and "Real" (aka constant) elements for the length

        E_cg = self.model_inputs.E_cg
        E_dg = self.model_inputs.E_dg
        E_r =  self.model_inputs.E_r
        # Mixed element for full problem
        E_V = MixedElement(E_cg, E_cg, E_cg, E_dg, E_r)
        # Mixed function space for fixed domain problem
        E_V_f = MixedElement(E_cg, E_cg, E_cg, E_dg)

        V_cg = self.model_inputs.V_cg
        V_dg = self.model_inputs.V_dg
        V_r = FunctionSpace(self.mesh, E_r)
        # Function space for full problem
        V = FunctionSpace(self.mesh, E_V)
        # Function space for fixed domain problem
        V_f = FunctionSpace(self.mesh, E_V_f)

        # For moving data between vector functions and scalar functions
        self.assigner_inv = FunctionAssigner([V_cg, V_cg, V_cg, V_dg, V_r], V)
        self.assigner     = FunctionAssigner(V, [V_cg, V_cg, V_cg, V_dg, V_r])
        # Same for fixed domain problem
        self.assigner_inv_f = FunctionAssigner([V_cg, V_cg, V_cg, V_dg], V_f)
        self.assigner_f     = FunctionAssigner(V_f, [V_cg, V_cg, V_cg, V_dg])

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

        # U for fixed domain problem, containting both velocity components, DG thickness, CG thickness
        U_f = Function(V_f)
        dU_f = TrialFunction(V_f)
        Phi_f = TestFunction(V_f)

        # Split vector functions into scalar components
        ubar, udef, H_c, H, L = split(U)
        phibar, phidef, xsi_c, xsi, chi = split(Phi)

        # Components for fixed domain problem
        ubar_f, udef_f, H_c_f, H_f = split(U_f)
        phibar_f, phidef_f, xsi_c_f, xsi_f = split(Phi_f)

        # Values of model variables at previous time step
        un = Function(V_cg)
        u2n = Function(V_cg)
        H0_c = Function(V_cg)
        H0 = Function(V_dg)
        L0 = Function(V_r)

        self.ubar = ubar
        self.ubar_f = ubar_f
        self.udef = udef
        self.udef_f = udef_f
        self.H_c = H_c
        self.H_c_f = H_c_f
        self.H = H
        self.H_f = H_f
        self.L = L
        self.L_f = Function(self.V_r)
        self.phibar = phibar
        self.phibar_f = phibar_f
        self.phidef = phidef
        self.phidef_f = phidef_f
        self.xsi_c = xsi_c
        self.xsi_c_f = xsi_c_f
        self.xsi = xsi
        self.xsi_f = xsi_f
        self.chi = chi
        self.U = U
        self.U_f = U_f
        self.Phi = Phi
        self.Phi_f = Phi_f
        self.un = un
        self.u2n = u2n
        self.H0_c = H0_c
        self.H0 = H0
        self.L0 = L0
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
        # SMB
        adot = Function(V_cg)
        # Ice stream width
        width = Function(V_cg)

        self.B = B
        self.beta2 = beta2
        self.adot = adot
        self.width = width
        # Facet function marking divide and margin boundaries
        self.boundaries = model_inputs.boundaries


        ### Function initialization
        ########################################################################

        # Assign initial ice sheet length from data
        L0.vector()[:] = model_inputs.L_init
        # Initialize initial thickness
        H0.assign(model_inputs.input_functions['H0'])
        #H0.vector()[:] += 1.0
        H0_c.assign(model_inputs.input_functions['H0_c'])

        # Initialize guesses for unknowns
        self.assigner.assign(U, [self.zero_guess, self.zero_guess, H0_c, H0, L0])


        ### Derived expressions
        ########################################################################

        # Ice surface
        S = B + H_c
        # Same for fixed domain problem
        S_f = B + H_c_f
        # Ice surface as DG function
        S_dg = B + H
        # Same for fixed domain problem
        S_dg_f = B + H_f
        # Time derivatives
        dLdt = (L - L0) / dt
        dHdt = (H - H0) / dt
        # Same for fixed domain problem
        dHdt_f = (H_f - H0) / dt
        # Overburden pressure
        P_0 = Constant(self.constants['rho']*self.constants['g'])*H_c
        # Water pressure
        #P_w = Constant(self.constants['rho_w']*self.constants['g'])*B
        P_w = Constant(0.8)*P_0
        # Effective pressure
        N = P_0 - P_w
        # CG ice thickness at last time step
        self.S0_c = Function(self.V_cg)
        # SMB expression
        self.adot_prime = model_inputs.get_adot_exp(self.S0_c)
        # Same for fixed domain problem
        self.adot_prime_f = model_inputs.get_adot_exp(self.S0_c)
        # SMB as a function
        self.adot_prime_func = Function(self.V_cg)

        self.S = S
        self.S_f = S_f
        self.dLdt = dLdt
        self.dHdt = dHdt
        self.dHdt_f = dHdt_f
        self.dt = dt
        self.P_0 = P_0
        self.P_w = P_w
        self.N = N


        ### Initialize inputs
        ########################################################################

        self.update_inputs(model_inputs.L_init)
        self.S0_c.assign(self.B + self.H0_c)
        self.update_inputs(model_inputs.L_init)


        ### Variational forms
        ########################################################################

        # Momentum balance residual
        momentum_form = MomentumForm(self)
        R_momentum = momentum_form.R_momentum

        # Continuous thickness residual
        R_thickness = (H_c - H)*xsi_c*dx

        # Mass balance residual
        mass_form = MassForm(self)
        R_mass = mass_form.R_mass

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

        self.snes_params = {'nonlinear_solver': 'newton',
                      'newton_solver': {
                       'relative_tolerance' : 5e-14,
                       'absolute_tolerance' : 7e-5,
                       'linear_solver': 'mumps',
                       'maximum_iterations': 100,
                       'report' : True
                       }}

        self.problem = problem


        ### Setup the iterator for replaying a run
        ########################################################################

        # Get the time step from input file
        self.dt.assign(self.model_inputs.dt)
        # Iteration count
        self.i = 0


        ### Output files
        ########################################################################
        #self.out_file = HDF5File(mpi_comm_world(), out_dir + checkpoint_file + ".hdf5", 'w')
        #self.out_file.write(self.H0, "H_init")
        #self.out_file.write(self.get_S(), "S_init")
        #self.out_file.write(self.L0, "L_init")
        #self.out_file.close()


    # Assign input functions from model_inputs
    def update_inputs(self, L):
        print "update inputs", L
        self.model_inputs.update_inputs(L)
        self.B.assign(self.model_inputs.input_functions['B'])
        self.beta2.assign(self.model_inputs.input_functions['beta2'])
        self.adot_prime_func.assign(project(self.adot_prime, self.V_cg))
        self.width.assign(self.model_inputs.input_functions['B'])


    def step(self):

        self.update_inputs(float(self.L0))
        quit()



        try:
            self.assigner.assign(self.U, [self.zero_guess, self.zero_guess,self.H0_c, self.H0, self.L0])
            solver = NonlinearVariationalSolver(self.problem)
            solver.parameters.update(self.snes_params)
            solver.solve()
        except:
            solver = NonlinearVariationalSolver(self.problem)
            solver.parameters.update(self.snes_params)
            solver.parameters['newton_solver']['error_on_nonconvergence'] = False
            solver.parameters['newton_solver']['relaxation_parameter'] = 0.9
            solver.parameters['newton_solver']['report'] = True
            #self.assigner.assign(self.U, [self.zero_guess, self.zero_guess,self.H0_c, self.H0, self.L0])
            solver.solve()

        # Update previous solutions
        self.assigner_inv.assign([self.un,self.u2n, self.H0_c, self.H0, self.L0], self.U)
        # Print current time, max thickness, and adot parameter
        print self.t, self.H0.vector().max(), float(self.L0)
        # Update time
        self.t += float(self.dt)
        self.i += 1

        return float(self.L0)


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
      output_file.write(self.L0, "L0")
      output_file.write(self.boundaries, "boundaries")
      output_file.flush()
      output_file.close()