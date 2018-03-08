from dolfin import *

mesh = UnitSquareMesh(4,4)
V = FunctionSpace(mesh, "CG", 1)

att1 = Function(V)
cite_att1 = 'Turing, Alan M. "Computing machinery and intelligence." Mind (1950): 433-460.'

f = HDF5File(mesh.mpi_comm(), "example.h5", 'w')
f.write(mesh, "mesh")
f.write(att1, "att1")
attrs = f.attributes("att1")
attrs.set("Citation", cite_att1)
f.close()
