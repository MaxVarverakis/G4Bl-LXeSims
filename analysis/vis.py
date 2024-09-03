import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

n_events = 1000
beamX = 45 # mm
beamY = 45 # mm

df = pd.read_csv('LXe_Edep.txt', skiprows=6, delim_whitespace=True)
WinIn = pd.read_csv('EntranceWin_Edep.txt', skiprows=6, delim_whitespace=True)
WinOut = pd.read_csv('ExitWin_Edep.txt', skiprows=6, delim_whitespace=True)

xz = df[['z','x','edep','pedd']][df['y'] == df['y'].max()//2].to_numpy()
xy = df[['x','y','edep','pedd']][df['z'] == df['z'].max()].to_numpy()

######## Mean Edep per incident e- ########

print(f'######### Mean Edep/incident e- #########\n{df["edep"].sum()/n_events:.2f} MeV/e-\n')
print(f'Entrance Window: {WinIn["edep"].sum()/n_events:.2f} MeV/e-\nExit Window:\t{WinOut["edep"].sum()/n_events:.2f} MeV/e-\n')

######## Exiting Positrons ########

ep = pd.read_csv('zDet.txt', skiprows=3, names='x y z Px Py Pz t PDGid EventID TrackID ParentID Weight'.split(' '), delim_whitespace=True).drop(index=0)
ep = ep[ep['PDGid'] == -11] # filter out positrons
ke = np.sqrt(np.square(ep[['Px','Py','Pz']]).sum(axis=1))

# Filter outgoing positrons with transverse displacement < 10mm and energy between 2 MeV and 20 MeV
mask = (np.sqrt((ep['x'] - beamX)**2 + (ep['y'] - beamY)**2) < 10) & (ke > 2) & (ke < 20) # mm

n_ep = ep.shape[0] # total number of e^+ exiting the target
print(f'######### Normalized Positron Yield #########\nRaw:\t {n_ep/n_events} e+/incident e-\nFiltered: {ep[mask].shape[0]/n_events} e+/incident e-\n') # e^+ yield
# print(f'Yield with cutoffs: {ep[mask].shape[0]/n_events} e+/incident e-') # e^+ yield

plt.hist(ke, bins = 75, range = (0, 200))
plt.hist(ke[mask], bins = 75, range = (0, 200))
plt.xlim(0, 200)
plt.xlabel(r'Outgoing $e^+$ Energy [MeV]')
plt.ylabel(r'$e^+$ per $10^3$ Incident $e^-$')
plt.legend(['No filter','Filtered'])
plt.show()

######## Total Edep plots ########

plt.hist2d(x=xz[:,0], y=xz[:,1], weights=xz[:,2]/n_events, cmap='inferno')
plt.xlabel('z [Detector No.]')
plt.ylabel('x [Detector No.]')
cb = plt.colorbar(label=r'$E_{dep}/\mathrm{incident}\ e^- \left[\mathrm{MeV}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()

plt.hist2d(x=xy[:,0], y=xy[:,1], weights=xy[:,2]/n_events, cmap='inferno')
plt.xlabel('x [Detector No.]')
plt.ylabel('y [Detector No.]')
cb = plt.colorbar(label=r'$E_{dep}/\mathrm{incident}\ e^- \left[\mathrm{MeV}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()

######## PEDD plots #########

plt.hist2d(x=xz[:,0], y=xz[:,1], weights=xz[:,3], cmap='inferno')
plt.xlabel('z [Detector No.]')
plt.ylabel('x [Detector No.]')
cb = plt.colorbar(label=r'PEDD $\left[\mathrm{J}\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.close()

plt.hist2d(x=xy[:,0], y=xy[:,1], weights=xy[:,3], cmap='inferno')
plt.xlabel('x [Detector No.]')
plt.ylabel('y [Detector No.]')
cb = plt.colorbar(label=r'PEDD $\left[\mathrm{J}\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.close()





