import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True
import os
# plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
from mpl_toolkits.mplot3d import Axes3D

desired_pose_1 = pd.read_csv('desired_pose_1.csv').to_numpy()
desired_pose_2 = pd.read_csv('desired_pose_2.csv').to_numpy()
desired_pose_3 = pd.read_csv('desired_pose_3.csv').to_numpy()
actual_pose_1 = pd.read_csv('actual_pose_1.csv').to_numpy()
actual_pose_2 = pd.read_csv('actual_pose_2.csv').to_numpy()
actual_pose_3 = pd.read_csv('actual_pose_3.csv').to_numpy()
beg = 20
end = 800
phi_1= pd.read_csv('phi_1.csv').to_numpy()[:,1].reshape(-1,1)
phi_2= pd.read_csv('phi_2.csv').to_numpy()[:,1].reshape(-1,1)
phi_3= pd.read_csv('phi_3.csv').to_numpy()[:,1].reshape(-1,1)
min = np.min([phi_1.shape[0],phi_2.shape[0],phi_3.shape[0]])
phi_1 = phi_1[0:min,:]
phi_2 = phi_2[0:min,:]
phi_3 = phi_3[0:min,:]
t = np.arange(0,(end-beg)*0.1,0.1)

figures_dir = 'figures_article'
os.makedirs(figures_dir, exist_ok=True)
phases = np.concatenate((phi_1,phi_2,phi_3),axis=1)

phi_diff = np.zeros((phases.shape[0],3))
min_dist = np.min([actual_pose_1.shape[0],actual_pose_2.shape[0],actual_pose_3.shape[0]])
distances = np.zeros((min_dist,3))
for i in range(phases.shape[0]):
    phi_1 = phases[i,0]
    phi_2 = phases[i,1]
    phi_3 = phases[i,2]
    unit1 = np.array([np.cos(phi_1), np.sin(phi_1), 0])
    unit2 = np.array([np.cos(phi_2), np.sin(phi_2), 0])
    unit3 = np.array([np.cos(phi_3), np.sin(phi_3), 0])
    phi_diff[i,0] = np.rad2deg(np.mod(np.arccos(np.dot(unit1,unit2)),2*np.pi))
    phi_diff[i,1] = np.rad2deg(np.mod(np.arccos(np.dot(unit2,unit3)),2*np.pi))
    phi_diff[i,2] = np.rad2deg(np.mod(np.arccos(np.dot(unit3,unit1)),2*np.pi))


for i in range(min_dist):
    distances[i,0] = np.linalg.norm(actual_pose_1[i,1:4]-actual_pose_2[i,1:4])
    distances[i,1] = np.linalg.norm(actual_pose_2[i,1:4]-actual_pose_3[i,1:4])
    distances[i,2] = np.linalg.norm(actual_pose_3[i,1:4]-actual_pose_1[i,1:4])
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
ax.set_xlabel('X Axis (m)')
ax.set_ylabel('Y Axis (m)')
ax.set_zlabel('Z Axis (m)')
ax.set_title('Desired and Actual Poses of Agent 1')
plt.savefig(f"{figures_dir}/real_agent_1_3D.png", bbox_inches='tight', pad_inches=0.1)
plt.close()

t = np.arange(0,min*0.1,0.1)
fig = plt.figure()

plt.subplot(3,1,1)
plt.title('Desired and Actual Poses of Agent 1')
plt.plot(t, desired_pose_1[:min,1], label='Des Pose Agent 1',color=colors[0])
plt.plot(t, actual_pose_1[:min,1], label='Actual Pose Agent 1',linestyle='dashed',color=colors[0])
plt.ylabel('X Axis (m)')
plt.legend()
plt.subplot(3,1,2)
plt.plot(t, desired_pose_1[:min,2], label='Des Pose Agent 1',color=colors[0])
plt.plot(t, actual_pose_1[:min,2], label='Actual Pose Agent 1',linestyle='dashed',color=colors[0])
plt.ylabel('Y Axis (m)')
plt.subplot(3,1,3)
plt.plot(t, desired_pose_1[:min,3], label='Des Pose Agent 1',color=colors[0])
plt.plot(t, actual_pose_1[:min,3], label='Actual Pose Agent 1',linestyle='dashed',color=colors[0])
plt.ylabel('Z Axis (m)')
plt.xlabel('Time (s)')

plt.savefig(f"{figures_dir}/real_agent_1_x_y_z.png", bbox_inches='tight', pad_inches=0.1)
plt.close()

fig = plt.figure()
plt.plot(t, phi_diff[:min,0], label='Phase Diff Agents 1 and 2')
plt.plot(t, phi_diff[:min,1], label='Phase Diff Agents 2 and 3')
plt.plot(t, phi_diff[:min,2], label='Phase Diff Agents 3 and 1')
plt.title('Phase Differences between Agents')
plt.ylabel("$\phi$ (degrees)")
plt.legend()
plt.xlabel('Time (s)')
plt.savefig(f"{figures_dir}/real_phase_separation.png", bbox_inches='tight', pad_inches=0.1)
plt.close()

t = np.arange(0,min_dist*0.1,0.1)
fig = plt.figure()
plt.plot(t, distances[:min_dist,0], label='Distance Agents 1 and 2')
plt.plot(t, distances[:min_dist,1], label='Distance Agents 2 and 3')
plt.plot(t, distances[:min_dist,2], label='Distance Agents 3 and 1')
plt.xlabel('Time (s)')
plt.ylabel('Distance (m)')
plt.legend()
plt.title('Distances between Agents')
plt.savefig(f"{figures_dir}/real_distance_agents.png", bbox_inches='tight', pad_inches=0.1)
plt.close()
plt.show()