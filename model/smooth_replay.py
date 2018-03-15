from dolfin import *
import numpy as np
from forward_inputs_replay import *
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt


"""
Takes in a forward model replay file, and smooths the SMB parameter.
"""

class SmoothReplay(ForwardInputsReplay):

    def __init__(self, input_file_name, adot_inputs, output_file_name, window, degree = 3):

        super(SmoothReplay, self).__init__(input_file_name, adot_inputs)


        ### Smooth the SMB parameter
        ########################################################################
        adot_params = np.zeros(self.N)

        for i in range(self.N):
            self.input_file.read(self.adot_param, "adot0/vector_" + str(i))
            adot_params[i] = float(self.adot_param)

        adot_params = savgol_filter(adot_params, window, degree)


        ### Write a new replay file
        ########################################################################
        output_file = HDF5File(mpi_comm_world(), output_file_name + '.hdf5', 'w')

        ### Write bed data
        output_file.write(self.B_mesh, "B_mesh")
        output_file.write(self.B_data, "B_data")
        output_file.write(self.domain_length, "domain_length")

        ### Write variables
        output_file.write(self.mesh, "mesh")
        output_file.write(self.H0, "H0")
        output_file.write(self.H0_c, "H0_c")
        output_file.write(self.L0, "L0")
        output_file.write(self.boundaries, "boundaries")

        ### Time step
        dt_write = Function(self.V_r)
        dt_write.assign(Constant(self.dt))
        output_file.write(dt_write, 'dt')

        ### SMB parameter
        for i in range(self.N):
            t = i*self.dt
            self.adot_param.assign(Constant(adot_params[i]))
            output_file.write(self.adot_param, "adot0", t)

        output_file.flush()
        output_file.close()
