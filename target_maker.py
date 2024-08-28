import numpy as np
import pandas as pd
import os
import pickle
import sys

import functions as fcn

target_subgraph = sys.argv[1] # 3_2 
target_type = sys.argv[2] # 'C'
target_ton = sys.argv[3] # '100000'

target_category = target_subgraph + '_' + target_type + '_' + target_ton

save_dir = fcn.env['save_dir'] 
traj_dir =  './save/traj_markers'# fcn.env['traj_dir'] 
target_dir = fcn.env['target_dir'] 


subgraph_info_filename = 'subgraph_info_more.pkl'

water_filename = 'water'
dist_filename = 'dist_water'


traj_maker_path = f"{traj_dir}/count_{target_category}.pkl"
if os.path.exists(traj_maker_path):

    with open(f"{save_dir}/{subgraph_info_filename}", 'rb') as file: 
        subgraph_info = pickle.load(file)    
    target_subgraph_keys = target_subgraph.split('_')
    target_subgraph_keys = (int(target_subgraph_keys[0]), int(target_subgraph_keys[1]))
    subgraph_info = subgraph_info[target_subgraph_keys] 

    with open(traj_maker_path, 'rb') as file: # for example, 
        waypoint_dict = pickle.load(file)
    waypoint_list = waypoint_dict[target_category]
    print(f'{target_category} Length of the waypoint list : {len(waypoint_list)}')

    water = np.load(f'{save_dir}/{water_filename}.npz')['water'] # 2D numpy array.
    dist = np.load(f'{save_dir}/{dist_filename}.npz')['dist_water']

    water = water[subgraph_info[0]:subgraph_info[1], subgraph_info[2]:subgraph_info[3]] 
    water = water.astype('float')
    dist = dist[subgraph_info[0]:subgraph_info[1], subgraph_info[2]:subgraph_info[3]] 

    # 1_1_C_20000_math_target.npz
    _water = water.copy()
    row_indices, col_indices = zip(*waypoint_list)
    _water[row_indices, col_indices] = dist[row_indices, col_indices] * (1e-4)
    target_map = _water

    # count
    _water = water.copy()
    count_dict = {}

    for idx in waypoint_list:
        if idx in count_dict: count_dict[idx] +=1
        else: count_dict[idx] = 1
    for (ridx, cidx), count in count_dict.items():
        _water[ridx, cidx] = 1 / count

    _waypoint_list = list(count_dict.keys())

    row_indices, col_indices = zip(*_waypoint_list)
    _water[row_indices, col_indices] *= dist[row_indices, col_indices] 
    target_map = _water


    np.savez(f'{target_dir}/{target_category}_math_count_target.npz', target_map)

    print(f"{target_category} target npz file has been saved!")

else:
    print(f"The file {traj_maker_path} does not exist.") 


