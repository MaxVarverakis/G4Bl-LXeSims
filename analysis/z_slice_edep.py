import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import json

# NOTE: The x column header for the raw output files is `#x`

# Set window material (str: must be a `rho_Window` key)
WinMat = "Be"

eps = 4 # width of slice of LXe to plot (mm)

cols = 'x y z Px Py Pz t PDGid EventID TrackID ParentID Weight Edep VisibleEdep Ntracks'.split(' ')

with open("../analysis/z_sim_info.json", "r") as f:
    info = json.load(f)
    
n_events = info["n_events"]

df_LXe = pd.read_csv("LXe.txt", skiprows=1, header=0, delim_whitespace=True, names=cols)

df_EntranceWin = pd.read_csv("WinIn.txt", skiprows=1, header=0, delim_whitespace=True, names=cols)
df_ExitWin = pd.read_csv("WinOut.txt", skiprows=1, header=0, delim_whitespace=True, names=cols)

# Electron charge in C
e_charge = 1.602176634e-19

# Material densities in g/cm^3 (https://www.fe.infn.it/u/paterno/Geant4_tutorial/slides_further/Geometry/G4_Nist_Materials.pdf)

WinVol = np.pi * info["WinProperties"]["r_window"]**2 * info["WinProperties"]["Win_thickness"] # cm^3
WinMass = WinVol * info["rho"][WinMat] # g

df_EntranceWin_PEDD = df_EntranceWin["Edep"] * 1e6 * e_charge / WinMass
df_ExitWin_PEDD = df_ExitWin["Edep"] * 1e6 * e_charge / WinMass

print(f'######### Mean Edep/incident e- #########\n{df_LXe["Edep"].sum()/n_events:.2f} MeV/e-\n')
print(f'Entrance Window: {df_EntranceWin["Edep"].sum()/n_events:.2f} MeV/e-\nExit Window:\t{df_ExitWin["Edep"].sum()/n_events:.2f} MeV/e-\n')

LXe_mass = info["LXeDim"][0] * info["LXeDim"][1] * info["LXeDim"][2] * info["rho"]["LXe"] # g
print(f'\n######### Total PEDD/{n_events:.0f} e- #########\n{df_LXe["Edep"].sum() * LXe_mass:.2e} J/g\n')
print(f'Entrance Window: {df_EntranceWin_PEDD.sum():.2e} J/g\nExit Window:\t{df_ExitWin_PEDD.sum():.2e} J/g\n')

print(f'\n######### PEDD/incident e- #########\n{df_LXe["Edep"].sum() * LXe_mass/n_events:.2e} J/g\n')
print(f'Entrance Window: {df_EntranceWin_PEDD.sum()/n_events:.2e} J/g\nExit Window:\t{df_ExitWin_PEDD.sum()/n_events:.2e} J/g\n')

xmask = abs(df_LXe['x']) <= eps/2
ymask = abs(df_LXe['y']) <= eps/2
z_pos = (info["LXeDim"][2]*10-eps/2) # z-coordinate of (center of) slice to plot (mm)
zmask = ((df_LXe['z'] >= z_pos - eps/2) & (df_LXe['z'] <= z_pos + eps/2))

slice_masks = {'x': xmask, 'y': ymask, 'z': zmask}

xz = df_LXe[slice_masks['y']]
xy = df_LXe[slice_masks['z']]

plt.hist(df_LXe['z'], bins=50)
plt.hist(xz['z'], bins=50)
plt.xlabel('z [mm]')
plt.show()

# plt.hist(df_LXe['x'], bins=500)
# plt.hist(xz['x'], bins=500)
# plt.hist(xy['x'], bins=500)
# plt.xlabel('x [mm]')
# plt.show()

# plt.hist(df_LXe['y'], bins=500)
# plt.hist(xy]['y'], bins=500)
# plt.xlabel('y [mm]')
# plt.show()


######## Window Edep Plots ########

WinKey = 'pedd' # edep or pedd
mass = {'edep': 1, 'pedd': WinMass}
names = ['Entrance Window', 'Exit Window']
labels = {'edep': r'$E_{dep}\ \left[\mathrm{MeV}\right]$', 'pedd': r'$PEDD\ \left[\ \mathrm{J}\cdot g^{-1}\right]$'}
WinEdep = [
    df_EntranceWin,
    df_ExitWin
    ]

vmin = 0
vmax = 10
n = 100 # 100 by 100 grid

fig, ax = plt.subplots(1, 2, sharey=True, figsize=(12,6), constrained_layout=True)
for i in range(2):
    h = ax[i].hist2d(x=WinEdep[i]['x']/10, y=WinEdep[i]['y']/10, weights=WinEdep[i]['Edep']/mass[WinKey], bins=n, cmap='inferno', vmin=vmin, vmax=vmax)
    # ax[i].autoscale_view()
    ax[i].set_xlabel('x [cm]')
    # ax[i].set_xticks(np.arange(-1,1.25,0.25))
    # ax[i].set_yticks(np.arange(-1,1.25,0.25))
    ax[i].set_xlim(-1,1)
    ax[i].set_title(names[i])
    ax[i].set_aspect('equal')
ax[0].set_ylabel('y [cm]')
ax[0].set_ylim(-1,1)
ax[0].set_facecolor('black')
cb = fig.colorbar(h[3], ax=ax[1], label=labels[WinKey])
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()


######## LXe Edep plots ########

plt.hist(x=df_LXe['z']/10, weights=df_LXe['Edep']/n_events, bins=50)
plt.xlabel('z [cm]')
plt.ylabel(r'$E_{dep}/\mathrm{incident}\ e^-\ \left[\mathrm{MeV}\right]$')
plt.show()

plt.hist2d(x=xz['z']/10, y=xz['x']/10, weights=xz['Edep']/n_events, bins=[50,35], cmap='inferno')
plt.xlabel('z [cm]')
plt.ylabel('x [cm]')
cb = plt.colorbar(label=r'$E_{\mathrm{dep}}/\mathrm{incident}\ e^-\ \left[\mathrm{MeV}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
# plt.gca().set_aspect(aspect=info["LXeDim"][0]/info["LXeDim"][1])
plt.show()

plt.hist2d(x=xy['x']/10, y=xy['y']/10, weights=xy['Edep']/n_events, bins=100, cmap='inferno')
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')
plt.title(f'z={(z_pos-eps/2)/10} cm to z={(z_pos+eps/2)/10} cm')
cb = plt.colorbar(label=r'$E_{\mathrm{dep}}/\mathrm{incident}\ e^-\ \left[\mathrm{MeV}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()


######## LXe PEDD plots ########

def calculate_PEDD(projection: str, bins: list) -> pd.DataFrame:
    '''
    Parameters
    ----------
        projectrion : str
            Desired plane to project onto for plotting. Options are 'x', 'y', and 'z'.
        bins : list
            List of integers describing the number of horizontal and vertical bins, respectively.

    Returns
    -------
        PEDD : pd.DataFrame
            Pandas DataFrame containing PEDD values corresponding to [nx,ny] bins for hist2d.

    '''
    d = {'z': 0, 'x': 1, 'y': 2} # Arranged so that the 'x' and 'y' projections puts z on the x-axis of the histogram
    axes = [val for key,val in d.items() if key != projection]
    volume = eps/10 * bins[0]/info["LXeDim"][axes[0]] * bins[0]/info["LXeDim"][axes[1]] # cm^3
    mass = volume * info["rho"]["LXe"] # g

    # Electron charge in C
    e_charge = 1.602176634e-19

    # Extract Edep, convert MeV to J, divide by mass of bin
    PEDD = df_LXe[slice_masks[projection]]['Edep'] * 1e6 * e_charge / mass # J/g

    return PEDD



xz_bins=[50,35]
xz_PEDD = calculate_PEDD(projection='y', bins=xz_bins)
plt.hist2d(x=xz['z']/10, y=xz['x']/10, weights=xz_PEDD/n_events, bins=xz_bins, cmap='inferno')
plt.xlabel('z [cm]')
plt.ylabel('x [cm]')
cb = plt.colorbar(label=r'$PEDD/\mathrm{incident}\ e^-\ \left[\ J\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
# plt.gca().set_aspect(aspect=info["LXeDim"][0]/info["LXeDim"][1])
plt.show()

n = 100
xy_bins=[n, n]
xy_PEDD = calculate_PEDD(projection='z', bins=xy_bins)
plt.hist2d(x=xy['x']/10, y=xy['y']/10, weights=xy_PEDD/n_events, bins=n, cmap='inferno')
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')
plt.title(f'z={(z_pos-eps/2)/10} cm to z={(z_pos+eps/2)/10} cm')
cb = plt.colorbar(label=r'$PEDD/\mathrm{incident}\ e^-\ \left[\ J\cdot g^{-1}\right]$')
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
mask = (np.sqrt(ep_win['x']**2 + ep_win['y']**2) < 10) & (ke > 2) & (ke < 20) # mm

n_ep = ep.shape[0] # total number of e^+ exiting the target
n_ep_win = ep_win.shape[0] # total number of e^+ exiting the target
print(f'######### Normalized Positron Yield #########\nRaw (LXe Exit): {n_ep/n_events} e+/incident e-\nFiltered:\t {ep_win[mask].shape[0]/n_events} e+/incident e-\n') # e^+ yield

plt.hist(ke_p, bins = 75, range = (0, 200))
plt.hist(ke[mask], bins = 75, range = (0, 200))
plt.xlim(0, 200)
plt.xlabel(r'Outgoing $e^+$ Energy [MeV]')
plt.ylabel(r'$e^+$ per $10^3$ Incident $e^-$')
plt.legend(['No filter','Filtered'])
plt.close()