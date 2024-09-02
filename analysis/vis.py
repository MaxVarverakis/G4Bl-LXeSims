import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('pedd.txt', skiprows=5, delim_whitespace=True)
xz = df[['z','x','pedd']][df['y'] == df['y'].max()/2].to_numpy()
xy = df[['x','y','pedd']][df['z'] == df['z'].max()/2].to_numpy()


pz = pd.read_csv('Det5.5.0.txt', skiprows=1, delim_whitespace=True)['Pz']
print(max(pz))
plt.hist(pz.to_numpy(), bins=100)
plt.xlabel(r'$P_z \ [MeV/c]$')
plt.show()


plt.hist2d(x=xz[:,0], y=xz[:,1], weights=xz[:,2], cmap='inferno')
plt.xlabel('z')
plt.ylabel('x')
cb = plt.colorbar(label=r'PEDD $\left[\mathrm{J}\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()

plt.hist2d(x=xy[:,0], y=xy[:,1], weights=xy[:,2], cmap='inferno')
plt.xlabel('x')
plt.ylabel('y')
cb = plt.colorbar(label=r'PEDD $\left[\mathrm{J}\cdot g^{-1}\right]$')
cb.formatter.set_useMathText(True)
cb.formatter.set_powerlimits((0, 0))
plt.show()





