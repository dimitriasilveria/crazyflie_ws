import nml_bag
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

bag = nml_bag.Reader('/home/bitdrones/rosbag2_2024_12_20-13_18_50', storage_id='sqlite3')
actual_pose_1 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
actual_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
actual_pose_3 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_1 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_3 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
phi_1 = pd.DataFrame(columns=[ 'phi_1'])
phi_2 = pd.DataFrame(columns=[ 'phi_2'])
phi_3 = pd.DataFrame(columns=[ 'phi_3'])

for message in bag:

    if message['topic'] == '/C04/phase':
        pphi_1 = message['data']
        phi_1= pd.concat([phi_1,pd.DataFrame([pphi_1],columns=[ 'phi_1'])], ignore_index=True)

    if message['topic'] == '/C20/phase':
        pphi_2 = message['data']
        phi_2 = pd.concat([phi_2,pd.DataFrame([pphi_2],columns=[ 'phi_2'])], ignore_index=True)
    
    if message['topic'] == '/C05/phase':
        pphi_3 = message['data']
        phi_3 = pd.concat([phi_3,pd.DataFrame([pphi_3],columns=[ 'phi_3'])], ignore_index=True)

    if message['topic'] == '/C04/pose':
        x = message['pose']['position']['x']
        y = message['pose']['position']['y']
        z = message['pose']['position']['z']
        actual_pose_1 = pd.concat([actual_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/C04/cmd_position':
        x = message['x']
        y = message['y']
        z = message['z']
        desired_pose_1 = pd.concat([desired_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/C20/pose':
        x = message['pose']['position']['x']
        y = message['pose']['position']['y']
        z = message['pose']['position']['z']
        actual_pose_2 = pd.concat([actual_pose_2,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/C20/cmd_position':
        x = message['x']
        y = message['y']
        z = message['z']
        desired_pose_2 = pd.concat([desired_pose_2,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/C05/pose':
        x = message['pose']['position']['x']
        y = message['pose']['position']['y']
        z = message['pose']['position']['z']
        actual_pose_3 = pd.concat([actual_pose_3,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    if message['topic'] == '/C05/cmd_position':
        x = message['x']
        y = message['y']
        z = message['z']
        desired_pose_3 = pd.concat([desired_pose_3,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)

print(actual_pose_1.head())
print(actual_pose_2.head())
print(actual_pose_3.head())
desired_pose_1.to_csv('desired_pose_1.csv')
desired_pose_2.to_csv('desired_pose_2.csv')
desired_pose_3.to_csv('desired_pose_3.csv')
actual_pose_1.to_csv('actual_pose_1.csv')
actual_pose_2.to_csv('actual_pose_2.csv')
actual_pose_3.to_csv('actual_pose_3.csv')
phi_1.to_csv('phi_1.csv')
phi_2.to_csv('phi_2.csv')
phi_3.to_csv('phi_3.csv')