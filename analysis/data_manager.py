# * Run this file in the directory containing your data *

import pandas as pd
import numpy as np
import json

cols = 'x y z Px Py Pz t PDGid EventID TrackID ParentID Weight Edep VisibleEdep Ntracks'.split(' ')

with open("../analysis/z_sim_info.json", "r") as f:
    info = json.load(f)

# LXe divisions in z
nz = int(info["LXeDim"][2]/info["LXeSliceDim"][2])


###########################################
#           Create new dataset            #
###########################################

df_LXe = pd.DataFrame(columns=cols)

# Loop over all LXe z-slices (detectors)
for k in range(0, nz):
    # Print progress
    print(f'Slice {k+1}/{nz}')
    
    df_temp = pd.read_csv(
        f"Det{k}.txt",
        skiprows=1,
        delim_whitespace=True,
        header=0,
        names=cols,
    )

    # Append the result to the DataFrame
    df_LXe = pd.concat([df_LXe,df_temp])


# initialize DataFrames for entrance & exit windows
# WinIn = pd.read_csv(
#     f"WinIn.txt",
#     skiprows=1,
#     delim_whitespace=True,
#     header=0,
#     names=cols,
# )

# WinOut = pd.read_csv(
#     f"WinOut.txt",
#     skiprows=1,
#     delim_whitespace=True,
#     header=0,
#     names=cols,
# )


# data = {"LXe": df_LXe, "EntranceWin": WinIn, "ExitWin": WinOut}
# fnames = [s+".txt" for s in data.keys()]

# Write the DataFrame to a text file
# for idx,file in enumerate(fnames):
#     with open(file, "w") as f:
#         list("data.values()")[idx].to_csv(f, sep="\t", index=False)

with open("LXe.txt", "w") as f:
    df_LXe.to_csv(f, sep="\t", index=False)
