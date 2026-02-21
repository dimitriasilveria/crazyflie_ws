import nml_bag
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from icecream import ic

bag = nml_bag.Reader('/home/bitdrones/bags_filter/baselines/modelA/rosbag2_2025_11_20-17_44_22/', storage_id='sqlite3')
sufix = "video"
actual_pose_1 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
actual_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
actual_pose_3 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_1 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_3 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
phi_1 = pd.DataFrame(columns=['phi_1'])
phi_2 = pd.DataFrame(columns=['phi_2'])
phi_3 = pd.DataFrame(columns=['phi_3'])
data_folder = "/home/bitdrones/ros2_ws/src/data/"

for message in bag:
    if message['topic'] == '/encircle':
        print(message)

input('Press Enter to continue...')
#finding what drone was agent 1, 2 and 3
for message in bag:
    if message['topic'] == '/agents_order':
        phi_1_drone = message['data'][0]
        phi_2_drone = message['data'][1]
        phi_3_drone = message['data'][2]
        break

#reading the data
for message in bag:

    if message['topic'] == '/'+phi_1_drone+'/phase':
        pphi_1 = message['data']
        phi_1= pd.concat([phi_1,pd.DataFrame([pphi_1],columns=[ 'phi_1'])], ignore_index=True)

    if message['topic'] == '/'+phi_2_drone+'/phase':
        pphi_2 = message['data']
        phi_2 = pd.concat([phi_2,pd.DataFrame([pphi_2],columns=[ 'phi_2'])], ignore_index=True)
    
    if message['topic'] == '/'+phi_3_drone+'/phase':
        pphi_3 = message['data']
        phi_3 = pd.concat([phi_3,pd.DataFrame([pphi_3],columns=[ 'phi_3'])], ignore_index=True)

    if message['topic'] == '/'+phi_1_drone+'/pose':
        x = message['pose']['position']['x']
        y = message['pose']['position']['y']
        z = message['pose']['position']['z']
        actual_pose_1 = pd.concat([actual_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/'+phi_1_drone+'/cmd_position':
        x = message['x']
        y = message['y']
        z = message['z']
        desired_pose_1 = pd.concat([desired_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/'+phi_2_drone+'/pose':
        x = message['pose']['position']['x']
        y = message['pose']['position']['y']
        z = message['pose']['position']['z']
        actual_pose_2 = pd.concat([actual_pose_2,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/'+phi_2_drone+'/cmd_position':
        x = message['x']
        y = message['y']
        z = message['z']
        desired_pose_2 = pd.concat([desired_pose_2,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/'+phi_3_drone+'/pose':
        x = message['pose']['position']['x']
        y = message['pose']['position']['y']
        z = message['pose']['position']['z']
        actual_pose_3 = pd.concat([actual_pose_3,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/'+phi_3_drone+'/cmd_position':
        x = message['x']
        y = message['y']
        z = message['z']
        desired_pose_3 = pd.concat([desired_pose_3,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)

print(actual_pose_1.head())
print(actual_pose_2.head())
print(actual_pose_3.head())
desired_pose_1.to_csv(f"{data_folder}desired_pose_1_{sufix}.csv")
desired_pose_2.to_csv(f"{data_folder}desired_pose_2_{sufix}.csv")
desired_pose_3.to_csv(f"{data_folder}desired_pose_3_{sufix}.csv")
actual_pose_1.to_csv(f"{data_folder}actual_pose_1_{sufix}.csv")
actual_pose_2.to_csv(f"{data_folder}actual_pose_2_{sufix}.csv")
actual_pose_3.to_csv(f"{data_folder}actual_pose_3_{sufix}.csv")
phi_1.to_csv(f"{data_folder}phi_1_{sufix}.csv")
phi_2.to_csv(f"{data_folder}phi_2_{sufix}.csv")
phi_3.to_csv(f"{data_folder}phi_3_{sufix}.csv")
