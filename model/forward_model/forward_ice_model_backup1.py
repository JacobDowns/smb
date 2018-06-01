#import h5py
from dolfin import *
from support.physical_constants import *
from support.momentum_form import *
from support.momentum_form_fixed_domain import *
from support.mass_form import *
from support.mass_form_fixed_domain import *
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
        self.domain_len = float(self.model_inputs.input_functions['domain_len'])
        # Fix the domain length?
        self.fixed_domain = True
        if 'fixed_domain' in model_options:
            self.fixed_domain = model_options['fixed_domain']


        #### Function spaces
        ########################################################################

        # Define finite element function spaces.  Here we use CG1 for
        # velocity computations, DG0 (aka finite volume) for mass cons,
        # and "Real" (aka constant) elements for the length

        E_cg = self.model_inputs.E_cg
        E_dg = self.model_inputs.E_dg
        E_r =  self.model_inputs.E_r

        V_cg = self.model_inputs.V_cg
        V_dg = self.model_inputs.V_dg
        V_r =  self.model_inputs.V_r

        self.V_cg = V_cg
        self.V_dg = V_dg
        self.V_r = V_r


        ### Mixed function spaces
        ########################################################################

        # Mixed element
        E_V = MixedElement(E_cg, E_cg, E_cg, E_dg, E_r)
        # Mixed space
        V = FunctionSpace(self.mesh, E_V)
        # For moving data between vector functions and scalar functions
        self.assigner_inv = FunctionAssigner([V_cg, V_cg, V_cg, V_dg, V_r], V)
        self.assigner     = FunctionAssigner(V, [V_cg, V_cg, V_cg, V_dg, V_r])

        # Mixed element for fixed domain problem
        E_V_f = MixedElement(E_cg, E_cg, E_cg, E_dg)
        # Mixed space for fixed domain problem
        V_f = FunctionSpace(self.mesh, E_V_f)
        # Same for fixed domain problem
        self.assigner_inv_f = FunctionAssigner([V_cg, V_cg, V_cg, V_dg], V_f)
        self.assigner_f     = FunctionAssigner(V_f, [V_cg, V_cg, V_cg, V_dg])

        self.V = V
        self.V_f = V_f


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
        ubar, udef, H_c, H, L = split(U)
        phibar, phidef, xsi_c, xsi, chi = split(Phi)

        # Same stuff for fixed domain problem
        U_f = Function(V_f)
        dU_f = TrialFunction(V_f)
        Phi_f = TestFunction(V_f)
        # Split vector functions into scalar components
        ubar_f, udef_f, H_c_f, H_f = split(U_f)
        phibar_f, phidef_f, xsi_c_f, xsi_f = split(Phi_f)
        # For fixed domain problem L is fixed
        L_f = Constant(0.0)

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
        self.L_f = L_f
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
        dt = Constant(1.)
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
        H0_c.assign(model_inputs.input_functions['H0_c'])
        # Initialize guesses for unknowns
        self.assigner.assign(U, [self.zero_guess, self.zero_guess, H0_c, H0, L0])

        # Same stuff for fixed domain problem
        self.L_f.assign(model_inputs.L_init)
        self.assigner_f.assign(U_f, [self.zero_guess, self.zero_guess, H0_c, H0])


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
        P_w = Constant(0.6)*P_0
        # Effective pressure
        N = P_0 - P_w
        # Effective pressure for fixed domain problem
        P_0_f = Constant(self.constants['rho']*self.constants['g'])*H_c_f
        P_w_f = Constant(0.6)*P_0_f
        N_f = P_0_f - P_w_f
        # CG ice thickness at last time step
        self.S0_c = Function(self.V_cg)
        # SMB expression
        self.adot_prime = model_inputs.get_adot_exp(self.S0_c)
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
        self.N_f = N_f


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


        ### Variational form for fixed domain problem
        ########################################################################

        # Momentum balance residual
        momentum_form_f = MomentumFormFixedDomain(self)
        R_momentum_f = momentum_form_f.R_momentum

        # Continuous thickness residual
        R_thickness_f = (H_c_f - H_f)*xsi_c_f*dx

        # Mass balance residual
        mass_form_f = MassFormFixedDomain(self)
        R_mass_f = mass_form_f.R_mass

        # Total residual
        R_f = R_momentum_f + R_thickness_f + R_mass_f
        J_f = derivative(R_f, U_f, dU_f)


        ### Variational solver
        ########################################################################

        # Bounds for snes_vi_rsls.  Only thickness bound is ever used.
        thklim = 10.0

        l_v_bound = interpolate(Constant(-1e10), V_cg)
        u_v_bound = interpolate(Constant(1e10), V_cg)

        l_thickc_bound = interpolate(Constant(thklim), V_cg)
        u_thickc_bound = interpolate(Constant(1e10), V_cg)

        l_thick_bound = interpolate(Constant(thklim), V_dg)
        # Allow thinner ice near terminus
        l_thickc_bound.vector()[-2:] = 0.
        u_thick_bound = interpolate(Constant(1e10), V_dg)

        l_r_bound = interpolate(Constant(-1e16), V_r)
        u_r_bound = interpolate(Constant(1e16), V_r)

        l_bound = Function(V)
        u_bound = Function(V)

        self.assigner.assign(l_bound,[l_v_bound]*2+[l_thickc_bound]+[l_thick_bound]+[l_r_bound])
        self.assigner.assign(u_bound,[u_v_bound]*2+[u_thickc_bound]+[u_thick_bound]+[u_r_bound])

        # Define variational problem subject to no Dirichlet BCs, but with a
        # thickness bound, plus form compiler parameters for efficiency.
        ffc_options = {"optimize": True}

        # SNES parameters for variable length problem
        self.snes_params = {'nonlinear_solver': 'snes',
                      'snes_solver': {
                       'method' : 'vinewtonrsls',
                       'relative_tolerance' : 5e-14,
                       'absolute_tolerance' : 7e-5,
                       'linear_solver': 'mumps',
                       'maximum_iterations': 35,
                       'report' : False
                       }}

        # SNES parameters for fixed domain problem
        self.snes_params_f = {'nonlinear_solver': 'newton',
                      'newton_solver': {
                       'relative_tolerance' : 5e-14,
                       'absolute_tolerance' : 7e-5,
                       'linear_solver': 'mumps',
                       'maximum_iterations': 35,
                       'report' : False
                       }}

        # Variable length problem
        self.problem = NonlinearVariationalProblem(R, U, bcs=[], J=J, form_compiler_parameters = ffc_options)
        self.problem.set_bounds(l_bound,u_bound)
        # Fixed domain problem
        self.problem_f = NonlinearVariationalProblem(R_f, U_f, bcs=[], J=J_f, form_compiler_parameters = ffc_options)


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

        self.var_flag = False


    # Assign input functions from model_inputs
    def update_inputs(self, L):
        print "update inputs", L
        self.S0_c.assign(self.B + self.H0_c)
        self.model_inputs.update_inputs(L, t = self.t)
        self.B.assign(self.model_inputs.input_functions['B'])
        self.beta2.assign(self.model_inputs.input_functions['beta2'])
        self.adot_prime_func.assign(project(self.adot_prime, self.V_cg))
        self.width.assign(self.model_inputs.input_functions['width'])



    def step(self):
        self.update_inputs(float(self.L0))

        # Switch of the fixed domain solver if the ice sheet terminus gets thin
        if not self.var_flag:
            self.fixed_domain = self.H0_c([1.]) > 10.
            if self.fixed_domain == False:
                self.var_flag = True

        print "fixed domain", self.fixed_domain

        if self.fixed_domain:
            try:
                self.assigner_f.assign(self.U_f, [self.zero_guess, self.zero_guess,self.H0_c, self.H0])
                solver = NonlinearVariationalSolver(self.problem_f)
                solver.parameters.update(self.snes_params)
                solver.solve()
            except:
                solver = NonlinearVariationalSolver(self.problem_f)
                solver.parameters.update(self.snes_params)
                solver.parameters['newton_solver']['error_on_nonconvergence'] = False
                solver.parameters['newton_solver']['relaxation_parameter'] = 0.9
                solver.parameters['newton_solver']['report'] = True
                solver.solve()

            # Update previous solutions
            self.assigner_inv_f.assign([self.un,self.u2n, self.H0_c, self.H0], self.U_f)
        else :
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
                solver.solve()

            # Update previous solutions
            self.assigner_inv.assign([self.un,self.u2n, self.H0_c, self.H0, self.L0], self.U)

        # Print current time, max thickness, and adot parameter
        print self.t, self.H0.vector().max(), self.H0.vector().min(), float(self.L0)
        # Update time
        self.t += float(self.dt)
        self.i += 1
        return float(self.L0)


    # Write out a steady state file
    def write_steady_file(self, output_file_name):
      output_file = HDF5File(mpi_comm_world(), output_file_name + '.hdf5', 'w')

      ### Write bed data
      output_file.write(self.model_inputs.original_cg_functions['B'], 'B')
      output_file.write(self.model_inputs.original_cg_functions['width'], 'width')
      output_file.write(self.model_inputs.original_cg_functions['beta2'], 'beta2')
      output_file.write(self.model_inputs.input_functions['domain_len'], 'domain_len')

      ### Write variables
      output_file.write(self.mesh, "mesh")
      output_file.write(self.H0, "H0")
      output_file.write(self.H0_c, "H0_c")
      output_file.write(self.L0, "L0")
      output_file.write(self.boundaries, "boundaries")
      output_file.write(self.adot_prime_func, "adot_prime_func")
      output_file.flush()

      for field in self.model_inputs.additional_cg_fields:
          output_file.write(self.model_inputs.original_cg_functions[field], field)

      output_file.close()
