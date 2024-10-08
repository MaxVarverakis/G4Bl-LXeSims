import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from matplotlib.collections import PatchCollection
import copy
import numpy as np
import pandas as pd
import json

with open("../analysis/sim_info.json", "r") as f:
    info = json.load(f)

n_events = info["n_events"]
beamX = (info["LXeDim"][0]-info["LXeCubeDim"][0])/2 * 10 # mm
beamY = (info["LXeDim"][1]-info["LXeCubeDim"][1])/2 * 10 # mm

df = pd.read_csv('LXe_Edep.txt', skiprows=6, delim_whitespace=True)
WinIn = pd.read_csv('EntranceWin_Edep.txt', skiprows=6, delim_whitespace=True)
WinOut = pd.read_csv('ExitWin_Edep.txt', skiprows=6, delim_whitespace=True)

xz = df[['x','z','edep','pedd']][df['y'] == (df['y'].max()-info["LXeDim"][1]/2)].to_numpy()
xy = df[['x','y','edep','pedd']][df['z'] == df['z'].max()].to_numpy()

def edges(idx):
    return np.arange(0, info["LXeDim"][idx]+info["LXeCubeDim"][idx], info["LXeCubeDim"][idx])
xzBin = [edges(2), edges(0)]
xyBin = [edges(0), edges(1)]

######## Mean Edep per incident e- ########

print(f'######### Mean Edep/incident e- #########\n{df["edep"].sum()/n_events:.2f} MeV/e-\n')
print(f'Entrance Window: {WinIn["edep"].sum()/n_events:.2f} MeV/e-\nExit Window:\t{WinOut["edep"].sum()/n_events:.2f} MeV/e-\n')

print(f'\n######### Mean EDD/{n_events:.0f} e- #########\n{df["pedd"].mean():.2e} J/g\n')
print(f'Entrance Window: {WinIn["pedd"].mean():.2e} J/g\nExit Window:\t {WinOut["pedd"].mean():.2e} J/g\n')

print(f'\n######### Max EDD/{n_events:.0f} e- #########\n{df["pedd"].max():.2e} J/g\n')
print(f'Entrance Window: {WinIn["pedd"].max():.2e} J/g\nExit Window:\t {WinOut["pedd"].max():.2e} J/g\n')

# print(f'\n######### PEDD/incident e- #########\n{df["pedd"].sum()/n_events:.2e} J/g\n')
# print(f'Entrance Window: {WinIn["pedd"].sum()/n_events:.2e} J/g\nExit Window:\t {WinOut["pedd"].sum()/n_events:.2e} J/g\n')


######## Window Edep Plots ########

# Extract window information
r_window = info["WinProperties"]["r_window"] # cm
n_rings = info["WinProperties"]["n_rings"]
r_Divs = info["WinProperties"]["r_Divs"]
Win_thickness = info["WinProperties"]["Win_thickness"] # total thickness (in z) of window in cm
z_Divs = info["WinProperties"]["z_Divs"] # number of z-slices in windows

r0 = r_window/np.sqrt(n_rings*r_Divs+1)

center = (0,0) # central axis of window (for plotting)

patches = np.zeros(r_Divs*n_rings+1, dtype=object)
# Basically recreate the window construction from g4bl input file
for i in range(0, n_rings+1):
    if i == 0:
        # Add small disk at the center
        patches[i] = Circle(center, r0)
    else:
        for j in range(1, r_Divs+1):
            idx = (i - 1) * r_Divs + j # index for placing in `patches` array

            # Add wedge (tub)
            patches[idx] = Wedge(
                center=center,
                r=np.sqrt(i*r_Divs+1)*r0,
                theta1=(j-1)*360/r_Divs,
                theta2=j*360/r_Divs,
                width=(np.sqrt(i*r_Divs+1)-np.sqrt((i-1)*r_Divs+1))*r0
                )

# Create a patch collection with the simulation data as colors
base_collection = PatchCollection(patches, cmap='inferno')

WinKey = 'pedd' # edep or pedd
base_collection.set_clim(vmin=0, vmax=WinOut[WinKey].max())

fig, ax = plt.subplots(1, 2, sharey=True, figsize=(12,6), constrained_layout=True)
names = ['Entrance Window', 'Exit Window']
z_slice = z_Divs # pick out a z-slice from 1 to z_Divs
# for z_slice in range(1, z_Divs+1):
for i in range(2):
    WinEdep = [
        WinIn[WinKey].to_numpy(),
        WinOut[WinKey].to_numpy()
        ]
    # WinInEdep = WinIn[WinKey][WinIn['z'] == z_slice].to_numpy()
    # WinOutEdep = WinIn[WinKey][WinOut['z'] == z_slice].to_numpy()
    collection = copy.deepcopy(base_collection)
    
    collection.set_array(WinEdep[i])

    ax[i].add_collection(collection)
    ax[i].autoscale_view()
    ax[i].set_xlabel('x [cm]')
    ax[i].set_title(names[i])
    ax[i].set_aspect('equal')
ax[0].set_ylabel('y [cm]')
cb = fig.colorbar(collection, ax=ax[1], label=r'$PEDD\ \left[\ \mathrm{J}\cdot g^{-1}\right]$')
# cb = fig.colorbar(collection, ax=ax[1], label=r'$E_{dep}\ \left[\mathrm{MeV}\right]$')
cb.update_normal(collection)
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()


######## Exiting Positrons ########

ep = pd.read_csv('zDet.txt', skiprows=3, names='x y z Px Py Pz t PDGid EventID TrackID ParentID Weight'.split(' '), delim_whitespace=True).drop(index=0)
ep = ep[ep['PDGid'] == -11] # filter out positrons
ke_p = np.sqrt(np.square(ep[['Px','Py','Pz']]).sum(axis=1))

ep_win = pd.read_csv('zWinDet.txt', skiprows=3, names='x y z Px Py Pz t PDGid EventID TrackID ParentID Weight'.split(' '), delim_whitespace=True).drop(index=0)
ep_win = ep_win[ep_win['PDGid'] == -11] # filter out positrons
ke = np.sqrt(np.square(ep_win[['Px','Py','Pz']]).sum(axis=1))

# Filter outgoing positrons with transverse displacement < 10mm and energy between 2 MeV and 20 MeV
mask = (np.sqrt((ep_win['x'] - beamX)**2 + (ep_win['y'] - beamY)**2) < 10) & (ke > 2) & (ke < 20) # mm

n_ep = ep.shape[0] # total number of e^+ exiting the target
n_ep_win = ep_win.shape[0] # total number of e^+ exiting the target
print(f'######### Normalized Positron Yield #########\nRaw (LXe Exit): {n_ep/n_events} e+/incident e-\nFiltered:\t {ep_win[mask].shape[0]/n_events} e+/incident e-\n') # e^+ yield
# print(f'Yield with cutoffs: {ep[mask].shape[0]/n_events} e+/incident e-') # e^+ yield

plt.hist(ke_p, bins = 75, range = (0, 200))
plt.hist(ke[mask], bins = 75, range = (0, 200))
plt.xlim(0, 200)
plt.xlabel(r'Outgoing $e^+$ Energy [MeV]')
plt.ylabel(r'$e^+$ per $10^3$ Incident $e^-$')
plt.legend(['No filter','Filtered'])
plt.close()


######## Total LXe Edep plots ########

plt.hist2d(x=xz[:,1], y=xz[:,0], weights=xz[:,2]/n_events, bins=xzBin, cmap='inferno')
plt.xlabel('z [cm]')
plt.ylabel('x [cm]')
cb = plt.colorbar(label=r'$E_{dep}/\mathrm{incident}\ e^-\ \left[\mathrm{MeV}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
# plt.gca().set_aspect(aspect=info["LXeDim"][0]/info["LXeDim"][1])
plt.show()

plt.hist2d(x=xy[:,0], y=xy[:,1], weights=xy[:,2]/n_events, bins=xyBin, cmap='inferno')
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')
cb = plt.colorbar(label=r'$E_{dep}/\mathrm{incident}\ e^-\ \left[\mathrm{MeV}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()


######## LXe PEDD plots #########

plt.hist2d(x=xz[:,1], y=xz[:,0], weights=xz[:,3], bins=xzBin, cmap='inferno')
plt.xlabel('z [cm]')
plt.ylabel('x [cm]')
cb = plt.colorbar(label=r'PEDD $\left[\mathrm{J}\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
# plt.gca().set_aspect(aspect=info["LXeDim"][0]/info["LXeDim"][2])
plt.show()

plt.hist2d(x=xy[:,0], y=xy[:,1], weights=xy[:,3], bins=xyBin, cmap='inferno')
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')
cb = plt.colorbar(label=r'PEDD $\left[\mathrm{J}\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.close()





