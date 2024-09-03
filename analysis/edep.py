# Original code courtesey of https://github.com/sanjeev-one/Liquid_Xenon_Sim.git

# * Run this file in the directory containing your data *

import pandas as pd
import numpy as np

# LXe divisions in x,y,z
nx = 10
ny = 10
nz = 13

Edep = np.zeros((nx, ny, nz))

# Electron charge in C
e_charge = 1.602176634e-19

# Material densities in g/cm^3 (https://www.fe.infn.it/u/paterno/Geant4_tutorial/slides_further/Geometry/G4_Nist_Materials.pdf)
rho_LXe = 2.953
rho_Be = 1.848
rho_Al = 2.699

# Cube dimensions in cm
cube_dim = [1.0, 1.0, 1.0]

# Tub dimensions in cm
tub_dim = [] # [inner radius, outer radius, initial phi, final phi, thickness]

# Mass of a cube in g
m_cube = rho_LXe * cube_dim[0] * cube_dim[1] * cube_dim[2]

# DataFrame to hold the final result
# edep = energy deposition
# pedd = peak energy deposition density
df_new = pd.DataFrame(columns=["x", "y", "z", "edep", "pedd"])

# Loop over all detectors
for i in range(0, nx):
    for j in range(0, ny):
        for k in range(0, nz):
            df = pd.read_csv(
                f"Det{i}.{j}.{k}.txt",
                skiprows=1,
                delim_whitespace=True,
            )

            # total Edep for the detector in MeV
            Edep_tot = df["Edep"].sum()

            # Calculate energy deposition density [J/g]
            pedd = Edep_tot * 1e6 * e_charge / m_cube

            df_temp = pd.DataFrame(
                {
                    "x": i,
                    "y": j,
                    "z": k,
                    "edep": Edep_tot,
                    "pedd": pedd,
                },
                index=[i*(ny*nz) + j*nz + k])
            
            # print(df_temp)

            # Append the result to the DataFrame
            df_new = pd.concat([df_new,df_temp])
            # print(df_new)

# Write the DataFrame to a text file
with open("pedd.txt", "w") as f:
    f.write(
        "# This file contains the peak energy deposition density for each cube in the detector array.\n"
    )
    f.write(
        "# Each line corresponds to one cube, with the following format: (x, y, z, pedd)\n"
    )
    f.write("# x, y, z: The coordinates of the cube in the detector array\n")
    f.write("# edep (energy deposition): The energy deposition in the cube, in units of J\n")
    f.write(
        "# pedd (peak energy deposition density): The maximum energy deposition density in the cube, in units of J/g\n"
    )
    df_new.to_csv(f, sep="\t", index=False)
