import pandas as pd
import numpy as np

# Define the dimensions of your detector array
num_x = 11
num_y = 11
num_z = 21

# Initialize a 3D numpy array to hold the Edep sums
Edep_sums = np.zeros((num_x, num_y, num_z))

# Define column names
column_names = [
    "x",
    "y",
    "z",
    "Px",
    "Py",
    "Pz",
    "t",
    "PDGid",
    "EventID",
    "TrackID",
    "ParentID",
    "Weight",
    "Edep",
    "VisibleEdep",
    "Ntracks",
]

# Electron charge in C
e_charge = 1.602176634e-19

# LXe density in g/cm^3
density = 2.953

# Cube dimensions in cm
cube_dim = [1, 1, 1]

# Mass of a cube in g
m_cube = density * cube_dim[0] * cube_dim[1] * cube_dim[2]

# DataFrame to hold the final result
df_result = pd.DataFrame(columns=["x", "y", "z", "peak_energy_deposition_density"])

# Loop over all detectors
for x in range(num_x):
    for y in range(num_y):
        for z in range(num_z):
            # Read the file, skipping the first two rows
            df = pd.read_csv(
                f"./Det{x}_{y}_{z}.txt",
                skiprows=2,
                delim_whitespace=True,
                names=column_names,
            )

            sum_value = df["Edep"].sum()

            # Convert MeV to J and then calculate energy deposition density
            peak_edep_density = sum_value * 1e6 * e_charge / m_cube

            # Add the result to the DataFrame
            df_result = df_result.append(
                {
                    "x": x,
                    "y": y,
                    "z": z,
                    "peak_energy_deposition_density": peak_edep_density,
                },
                ignore_index=True,
            )

# Write the DataFrame to a text file
with open("peak_energy_deposition_density.txt", "w") as f:
    f.write(
        "# This file contains the peak energy deposition density for each cube in the detector array.\n"
    )
    f.write(
        "# Each line corresponds to one cube, with the following format: (x, y, z, peak energy deposition density)\n"
    )
    f.write("# x, y, z: The coordinates of the cube in the detector array\n")
    f.write(
        "# peak energy deposition density: The maximum energy deposition density in the cube, in units of J/g\n"
    )
    df_result.to_csv(f, sep="\t", index=False)
