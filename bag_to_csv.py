import nml_bag
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

bag = nml_bag.Reader('/home/bitdrones/rosbag2_2024_12_18-17_26_53', storage_id='sqlite3')
actual_pose_1 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
actual_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
actual_pose_3 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_1 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
desired_pose_2 = pd.DataFrame(columns=[ 'x', 'y', 'z'])
phases = pd.DataFrame(columns=[ 'phi_1', 'phi_2', 'phi_3'])

for message in bag:

    if message['topic'] == '/C13/phases':
        phi_1 = message['data'][0]
        phi_2 = message['data'][1]
        phi_3 = message['data'][2]
        phases = pd.concat([phases,pd.DataFrame([[phi_1,  phi_2, phi_3]],columns=[ 'phi_1', 'phi_2', 'phi_3'])], ignore_index=True)

    # if message['topic'] == '/C05/pose':
    #     x = message['pose']['position']['x']
    #     y = message['pose']['position']['y']
    #     z = message['pose']['position']['z']
    #     actual_pose_1 = pd.concat([actual_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    # if message['topic'] == '/C05/cmd_position':
    #     x = message['x']
    #     y = message['y']
    #     z = message['z']
    #     desired_pose_1 = pd.concat([desired_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    # if message['topic'] == '/C13/pose':
    #     x = message['pose']['position']['x']
    #     y = message['pose']['position']['y']
    #     z = message['pose']['position']['z']
    #     actual_pose_2 = pd.concat([actual_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    # if message['topic'] == '/C13/cmd_position':
    #     x = message['x']
    #     y = message['y']
    #     z = message['z']
    #     desired_pose_2 = pd.concat([desired_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    # if message['topic'] == '/C20/pose':
    #     x = message['pose']['position']['x']
    #     y = message['pose']['position']['y']
    #     z = message['pose']['position']['z']
    #     actual_pose_3 = pd.concat([actual_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)
    # if message['topic'] == '/C20/cmd_position':
    #     x = message['x']
    #     y = message['y']
    #     z = message['z']
    #     desired_pose_3 = pd.concat([desired_pose_1,pd.DataFrame([[x,  y, z]],columns=[ 'x', 'y', 'z'])], ignore_index=True)

# desired_pose_1.to_csv('desired_pose_1.csv')
# desired_pose_2.to_csv('desired_pose_2.csv')
# desired_pose_3.to_csv('desired_pose_3.csv')
# actual_pose_1.to_csv('actual_pose_1.csv')
# actual_pose_2.to_csv('actual_pose_2.csv')
# actual_pose_3.to_csv('actual_pose_3.csv')
phases.to_csv('phases.csv')