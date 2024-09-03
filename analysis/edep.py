# Based off of https://github.com/sanjeev-one/Liquid_Xenon_Sim.git

# * Run this file in the directory containing your data *

import pandas as pd
import numpy as np

headers = ["x", "y", "z", "edep", "pedd"]

# Set window material (str: must be a `rho_Window` key)
WinMat = 'Be'

# LXe divisions in x,y,z
nx = 10
ny = 10
nz = 13

Edep = np.zeros((nx, ny, nz))

# Electron charge in C
e_charge = 1.602176634e-19

# Material densities in g/cm^3 (https://www.fe.infn.it/u/paterno/Geant4_tutorial/slides_further/Geometry/G4_Nist_Materials.pdf)
rho_LXe = 2.953
rho_Window = {'Be': 1.848, 'Al': 2.699}

# Cube dimensions in cm
cube_dim = [1.0, 1.0, 1.0]

# Tub volume = volume of center circlular window detector
r_window = 1.0 # cm
n_rings = 7
r_Divs = 12
Win_thickness = 0.2 # total thickness (in z) of window [cm]
z_Divs = 2 # number of z-slices in windows
r0 = r_window/np.sqrt(n_rings*r_Divs+1)
tub_vol = np.pi*r0**2*(Win_thickness/z_Divs) # cm^3

# Mass of a LXe cube
m_cube = rho_LXe * cube_dim[0] * cube_dim[1] * cube_dim[2] # g

# Mass of window chunk (tub)
m_tub = rho_Window[WinMat] * tub_vol # g

###########################################
#    Function for extracting Edep/PEDD    #
###########################################

def get_Edep(df: pd.DataFrame, i: int, j: int, k: int, mass: float) -> pd.DataFrame:
    # total Edep for the detector in MeV
    Edep_tot = df["Edep"].sum()

    # Calculate energy deposition density [J/g]
    pedd = Edep_tot * 1e6 * e_charge / mass

    df_temp = pd.DataFrame(
        {
            "x": i,
            "y": j,
            "z": k,
            "edep": Edep_tot,
            "pedd": pedd,
        },
        index=[i*(ny*nz) + j*nz + k])

    return df_temp


###########################################
#           Create new datasets           #
###########################################

# DataFrame to hold the final result
# edep = energy deposition
# pedd = peak energy deposition density
df_LXe = pd.DataFrame(columns=headers)

# Loop over all LXe detectors
for i in range(0, nx):
    for j in range(0, ny):
        for k in range(0, nz):
            df = pd.read_csv(
                f"Det{i}.{j}.{k}.txt",
                skiprows=1,
                delim_whitespace=True,
            )

            df_temp = get_Edep(df, i, j, k, m_cube)

            # Append the result to the DataFrame
            df_LXe = pd.concat([df_LXe,df_temp])


# initialize DataFrames for entrance & exit windows
WinIn = pd.DataFrame(columns=headers)
WinOut = pd.DataFrame(columns=headers)

# Loop over all window detectors
for i in range(0, n_rings+1):
    for j in range(0, r_Divs+1):
        for k in range(1, z_Divs+1):
            # There's only 1 circular detector at the window center
            # So the only index for those is k (the z-slice)
            if ((i==0) & (j!=0)) | ((i!=0) & (j==0)):
                continue
            
            # * Entrance window *
            df = pd.read_csv(
                f"WinIn{i}.{j}.{k}.txt",
                skiprows=1,
                delim_whitespace=True,
            )
            
            df_temp = get_Edep(df, i, j, k, m_tub)

            # Append the result to the DataFrame
            WinIn = pd.concat([WinIn, df_temp]) # Roundoff error?

            # * Exit window *
            df = pd.read_csv(
                f"WinOut{i}.{j}.{k}.txt",
                skiprows=1,
                delim_whitespace=True,
            )

            df_temp = get_Edep(df, i, j, k, m_tub)

            # Append the result to the DataFrame
            WinOut = pd.concat([WinOut, df_temp])

data = {"LXe": df_LXe, "EntranceWin": WinIn, "ExitWin": WinOut}
fnames = [s+"_Edep.txt" for s in data.keys()]

# Write the DataFrame to a text file
for idx,file in enumerate(fnames):
    with open(file, "w") as f:
        f.write(
            "# This file contains the energy deposition and PEDD for each detector.\n"
        )
        f.write(
            "# Each line corresponds to one detector, with the following format: (x, y, z, edep, pedd)\n"
        )
        f.write("# x, y, z: The cartesian ID of the cube in the detector array (if LXe)\n")
        f.write("# x, y, z: The annulus number, angle section, and z ID of the tub in the array (if window)\n")
        f.write("# edep (energy deposition): The energy deposition in the cube, in units of J\n")
        f.write(
            "# pedd (peak energy deposition density): The maximum energy deposition density in the cube, in units of J/g\n"
        )
        list(data.values())[idx].to_csv(f, sep="\t", index=False)
