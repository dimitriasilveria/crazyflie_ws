import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True
# plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
from mpl_toolkits.mplot3d import Axes3D
beg = 60
end = 491
desired_pose_1 = pd.read_csv('desired_pose_1.csv').to_numpy()
desired_pose_2 = pd.read_csv('desired_pose_2.csv').to_numpy()
desired_pose_3 = pd.read_csv('desired_pose_3.csv').to_numpy()
actual_pose_1 = pd.read_csv('actual_pose_1.csv').to_numpy()
actual_pose_2 = pd.read_csv('actual_pose_2.csv').to_numpy()
actual_pose_3 = pd.read_csv('actual_pose_3.csv').to_numpy()
phases = pd.read_csv('phases.csv').to_numpy()
print(phases.shape)
phi_diff = np.zeros((phases.shape[0],3))
for i in range(phases.shape[0]):
    phi_1 = phases[i,1]
    phi_2 = phases[i,2]
    phi_3 = phases[i,3]
    unit1 = np.array([np.cos(phi_1), np.sin(phi_1), 0])
    unit2 = np.array([np.cos(phi_2), np.sin(phi_2), 0])
    unit3 = np.array([np.cos(phi_3), np.sin(phi_3), 0])
    phi_diff[i,0] = np.rad2deg(np.mod(np.arccos(np.dot(unit1,unit2)),2*np.pi))
    phi_diff[i,1] = np.rad2deg(np.mod(np.arccos(np.dot(unit2,unit3)),2*np.pi))
    phi_diff[i,2] = np.rad2deg(np.mod(np.arccos(np.dot(unit3,unit1)),2*np.pi))
n_agents = 3
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
legends = []
colors = plt.cm.viridis(np.linspace(0, 1, n_agents))
ax.plot(desired_pose_1[beg:end,1], desired_pose_1[beg:end,2], desired_pose_1[beg:end,3], label='Des Pose Agent 1',color=colors[0])
ax.plot(actual_pose_1[beg:end,1], actual_pose_1[beg:end,2], actual_pose_1[beg:end,3], label='Actual Pose Agent 1',color=colors[0],linestyle='dashed')
# ax.plot(desired_pose_2[beg:end,1], desired_pose_2[beg:end,2], desired_pose_2[beg:end,3], label='Des Pose Agent 2',color=colors[1])
# ax.plot(actual_pose_2[beg:end,1], actual_pose_2[beg:end,2], actual_pose_2[beg:end,3], label='Actual Pose Agent 2',color=colors[1],linestyle='dashed')
# ax.plot(desired_pose_3[beg:end,1], desired_pose_3[beg:end,2], desired_pose_3[beg:end,3], label='Des Pose Agent 3',color=colors[2])
# ax.plot(actual_pose_3[beg:end,1], actual_pose_3[beg:end,2], actual_pose_3[beg:end,3], label='Actual Pose Agent 3',color=colors[2],linestyle='dashed')
ax.legend()
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('Desired and Actual Poses of Agents')
# plt.show()

fig = plt.figure()
plt.subplot(3,1,1)
plt.plot(desired_pose_1[beg:end,1], label='Des Pose Agent 1',color='blue')
plt.plot(actual_pose_1[beg:end,1], label='Actual Pose Agent 1',linestyle='dashed',color='blue')
plt.ylabel('X Axis')
plt.subplot(3,1,2)
plt.plot(desired_pose_1[beg:end,2], label='Des Pose Agent 1')
plt.plot(actual_pose_1[beg:end,2], label='Actual Pose Agent 1',linestyle='dashed',color='blue')
plt.ylabel('Y Axis')
plt.subplot(3,1,3)
plt.plot(desired_pose_1[beg:end,3], label='Des Pose Agent 1')
plt.plot(actual_pose_1[beg:end,3], label='Actual Pose Agent 1',linestyle='dashed',color='blue')
plt.ylabel('Z Axis')
plt.xlabel('Time Steps')
plt.title('Desired and Actual Poses of Agent 1')
plt.legend()

fig = plt.figure()
plt.plot(phi_diff[:,0], label='Phase Diff Agent 1')
plt.plot(phi_diff[:,1], label='Phase Diff Agent 2')
plt.plot(phi_diff[:,2], label='Phase Diff Agent 3')
plt.show()