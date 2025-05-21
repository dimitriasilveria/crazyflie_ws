import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from icecream import ic
import pickle
plt.rcParams['text.usetex'] = True
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 13
})
import os
# plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
from mpl_toolkits.mplot3d import Axes3D
data_folder = "/home/bitdrones/ros2_ws/src/data/"
sufix = "video"
desired_pose_1 = pd.read_csv(f"{data_folder}desired_pose_1_{sufix}.csv").to_numpy()
desired_pose_2 = pd.read_csv(f"{data_folder}desired_pose_2_{sufix}.csv").to_numpy()
desired_pose_3 = pd.read_csv(f"{data_folder}desired_pose_3_{sufix}.csv").to_numpy()
actual_pose_1 =  pd.read_csv(f"{data_folder}actual_pose_1_{sufix}.csv").to_numpy()
actual_pose_2 =  pd.read_csv(f"{data_folder}actual_pose_2_{sufix}.csv").to_numpy()
actual_pose_3 =  pd.read_csv(f"{data_folder}actual_pose_3_{sufix}.csv").to_numpy()
min_pose = np.min([desired_pose_1.shape[0],desired_pose_2.shape[0],desired_pose_3.shape[0],actual_pose_1.shape[0],actual_pose_2.shape[0],actual_pose_3.shape[0]])
beg = 38
end = 200

phi_1= pd.read_csv(f"{data_folder}phi_1_{sufix}.csv").to_numpy()[:,1].reshape(-1,1)
phi_2= pd.read_csv(f"{data_folder}phi_2_{sufix}.csv").to_numpy()[:,1].reshape(-1,1)
phi_3= pd.read_csv(f"{data_folder}phi_3_{sufix}.csv").to_numpy()[:,1].reshape(-1,1)

min = np.min([desired_pose_1.shape[0],desired_pose_2.shape[0],desired_pose_3.shape[0],actual_pose_1.shape[0],actual_pose_2.shape[0],actual_pose_3.shape[0],phi_1.shape[0],phi_2.shape[0],phi_3.shape[0]])
min_phases = np.min([phi_1.shape[0],phi_2.shape[0],phi_3.shape[0]])
phi_1 = phi_1[len(phi_1)-min_phases:,:]
phi_2 = phi_2[len(phi_2)-min_phases:,:]
phi_3 = phi_3[len(phi_3)-min_phases:,:]
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
colors = plt.cm.viridis(np.linspace(0, 1, n_agents))
fig = plt.figure()

plt.subplot(3,1,1)
#plt.title('Desired and Real Poses of Agent 1')
plt.plot(desired_pose_1[len(desired_pose_1)-min_pose+beg:end,1],label='Desired Pose 1', color=colors[0])
# plt.plot(actual_pose_1[:min,1],label = 'Real Pose 1',linestyle='dashed',color=colors[0])
plt.ylabel('X Axis (m)')

plt.legend(loc="upper right")
plt.subplot(3,1,2)
plt.plot(desired_pose_1[len(desired_pose_1)-min_pose+beg:end,2], label='Des Pose 1',color=colors[0])
# plt.plot(t, actual_pose_1[:min,2], label='Real Pose 1',linestyle='dashed',color=colors[0])
plt.ylabel('Y Axis (m)')
plt.subplot(3,1,3)
plt.plot(desired_pose_1[len(desired_pose_1)-min_pose+beg:end,3], label='Des Pose 1',color=colors[0])
# plt.plot(t, actual_pose_1[:min,3], label='Real Pose  1',linestyle='dashed',color=colors[0])
plt.ylabel('Z Axis (m)')
plt.xlabel('Time (s)')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
legends = []

ax.plot(desired_pose_1[len(desired_pose_1)-min_pose+beg:end,1],desired_pose_1[len(desired_pose_1)-min_pose+beg:end,2], desired_pose_1[len(desired_pose_1)-min_pose+beg:end,3], label='Des Pose Agent 1',color=colors[0])
ax.plot( actual_pose_1[len(actual_pose_1) -min_pose+beg:end,1], actual_pose_1[len(actual_pose_1) -min_pose+beg:end,2],  actual_pose_1[len(actual_pose_1) -min_pose+beg:end,3], label='Real Pose Agent 1',color=colors[0],linestyle='dashed')
ax.plot(desired_pose_2[len(desired_pose_2)-min_pose+beg:end,1],desired_pose_2[len(desired_pose_2)-min_pose+beg:end,2], desired_pose_2[len(desired_pose_2)-min_pose+beg:end,3], label='Des Pose Agent 2',color=colors[1])
ax.plot( actual_pose_2[len(actual_pose_2) -min_pose+beg:end,1], actual_pose_2[len(actual_pose_2) -min_pose+beg:end,2],  actual_pose_2[len(actual_pose_2) -min_pose+beg:end,3], label='Real Pose Agent 2',color=colors[1],linestyle='dashed')
ax.plot(desired_pose_3[len(desired_pose_3)-min_pose+beg:end,1],desired_pose_3[len(desired_pose_3)-min_pose+beg:end,2], desired_pose_3[len(desired_pose_3)-min_pose+beg:end,3], label='Des Pose Agent 3',color=colors[2])
ax.plot( actual_pose_3[len(actual_pose_3) -min_pose+beg:end,1], actual_pose_3[len(actual_pose_3) -min_pose+beg:end,2],  actual_pose_3[len(actual_pose_3) -min_pose+beg:end,3], label='Real Pose Agent 3',color=colors[2],linestyle='dashed')
ax.legend()
ax.set_xlabel('X Axis (m)')
ax.set_ylabel('Y Axis (m)')
ax.set_zlabel('Z Axis (m)')
plt.show()

#ax.set_title('Desired and Real Poses of Agent 1')
# plt.savefig(f"{figures_dir}/real_agent_1_3D.pdf", bbox_inches='tight', pad_inches=0.1)
# plt.close()

# t = np.arange(0,min*0.1,0.1)
# fig = plt.figure()

# plt.subplot(3,1,1)
# #plt.title('Desired and Real Poses of Agent 1')
# plt.plot(t, desired_pose_1[:min,1],label='Desired Pose 1', color=colors[0])
# plt.plot(t, actual_pose_1[:min,1],label = 'Real Pose 1',linestyle='dashed',color=colors[0])
# plt.ylabel('X Axis (m)')

# plt.legend(loc="upper right")
# plt.subplot(3,1,2)
# plt.plot(t, desired_pose_1[:min,2], label='Des Pose 1',color=colors[0])
# plt.plot(t, actual_pose_1[:min,2], label='Real Pose 1',linestyle='dashed',color=colors[0])
# plt.ylabel('Y Axis (m)')
# plt.subplot(3,1,3)
# plt.plot(t, desired_pose_1[:min,3], label='Des Pose 1',color=colors[0])
# plt.plot(t, actual_pose_1[:min,3], label='Real Pose  1',linestyle='dashed',color=colors[0])
# plt.ylabel('Z Axis (m)')
# plt.xlabel('Time (s)')

# plt.savefig(f"{figures_dir}/real_agent_1_x_y_z.pdf", bbox_inches='tight', pad_inches=0.1)
# plt.close()
# t = np.arange(0,min_phases*0.1,0.1)
# fig = plt.figure()
# plt.plot(t, phi_diff[:,0], label='Phase Diff Agents 1-2')
# plt.plot(t, phi_diff[:,1], label='Phase Diff Agents 2-3')
# plt.plot(t, phi_diff[:,2], label='Phase Diff Agents 3-1')
# #plt.title('Phase Differences between Agents')
# plt.ylabel("$\phi$ (degrees)")
# #plt.ylim([90,150])
# plt.legend(loc="upper right")
# plt.xlabel('Time (s)')
# # plt.savefig(f"{figures_dir}/real_phase_separation.pdf", bbox_inches='tight', pad_inches=0.1)
# # plt.close()

# t = np.arange(0,min_dist*0.1,0.1)
# fig = plt.figure()
# plt.plot(t, distances[:min_dist,0], label='Distance Agents 1-2')
# plt.plot(t, distances[:min_dist,1], label='Distance Agents 2-3')
# plt.plot(t, distances[:min_dist,2], label='Distance Agents 3-1')
# plt.xlabel('Time (s)')
# plt.ylabel('Distance (m)')
# plt.legend(loc="upper right", bbox_to_anchor=(1, 1))
# #plt.title('Distances between Agents')
# # plt.savefig(f"{figures_dir}/real_distance_agents.pdf", bbox_inches='tight', pad_inches=0.1)
# # plt.close()
# plt.show()
length = end - (len(actual_pose_1) -min_pose+beg)


agents_r = np.zeros((3,3,length))
for i in range(length):
    agents_r[0,0,i] = desired_pose_1[len(desired_pose_1)-min_pose+beg+i,1]
    agents_r[1,0,i] = desired_pose_1[len(desired_pose_1)-min_pose+beg+i,2]
    agents_r[2,0,i] = desired_pose_1[len(desired_pose_1)-min_pose+beg+i,3]
    agents_r[0,1,i] = desired_pose_2[len(desired_pose_2)-min_pose+beg+i,1]
    agents_r[1,1,i] = desired_pose_2[len(desired_pose_2)-min_pose+beg+i,2]
    agents_r[2,1,i] = desired_pose_2[len(desired_pose_2)-min_pose+beg+i,3]
    agents_r[0,2,i] = desired_pose_3[len(desired_pose_3)-min_pose+beg+i,1]
    agents_r[1,2,i] = desired_pose_3[len(desired_pose_3)-min_pose+beg+i,2]
    agents_r[2,2,i] = desired_pose_3[len(desired_pose_3)-min_pose+beg+i,3]

with open ('positions_video.pkl','wb') as f:
    pickle.dump(agents_r,f)