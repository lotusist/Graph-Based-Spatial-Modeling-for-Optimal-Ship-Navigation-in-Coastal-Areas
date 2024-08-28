import numpy as np
import pandas as pd
import os
import pickle
import sys
from tqdm import tqdm
import functions as fcn

target_subgraph = sys.argv[1] # 3_2 
target_type = sys.argv[2] # 'C'
target_ton = sys.argv[3] # '100000'

save_dir = fcn.env['save_dir'] 
traj_dir = fcn.env['traj_dir'] 
target_dir = './save/traj_markers'
# os.makedirs(target_dir, exist_ok=True)

target_subgraph_keys = target_subgraph.split('_')
target_subgraph_keys = (int(target_subgraph_keys[0]), int(target_subgraph_keys[1]))

with open(f"{save_dir}/typeton_ais.pickle", 'rb') as file:
    type_ton_dict = pickle.load(file)
   
pkl_files = []
for root, dirs, files in os.walk(traj_dir):
    for file in files:
        if file.endswith('pkl'): pkl_files.append(file)

_waypoint_list = []
for pkl_file in tqdm(pkl_files):
    print(f"Marking traj {pkl_file} for {target_subgraph}, {target_type}, {target_ton}")
    with open(f"{traj_dir}/{pkl_file}", 'rb') as file: # for example, 
        ship_traj_dict = pickle.load(file)

    filtered_ships = fcn.filter_shiptype(type_ton_dict, ship_traj_dict, target_type, target_ton) 
    for ship in filtered_ships:
        traj_df = ship_traj_dict[ship]
        traj_df = traj_df[traj_df['subgraph_key'] == target_subgraph_keys]
        if len(traj_df) > 0 :
            waypoints = [(ridx, cidx) for (ridx, cidx) in traj_df['subgraph_rc_index']]
            if len(waypoints) > 0: _waypoint_list += waypoints

if len(_waypoint_list) > 0:
    result_dict = dict()
    savefile_name_subgraph = f'{target_subgraph_keys[0]}_{target_subgraph_keys[1]}'
    savefile_name_type = str(target_type)
    savefile_name_ton = str(target_ton) 
    savefile_name = savefile_name_subgraph + '_' + savefile_name_type + '_' + savefile_name_ton
    result_dict[savefile_name] = _waypoint_list

    with open(f'{target_dir}/count_{savefile_name}.pkl', 'wb') as dict_:
        pickle.dump(result_dict, dict_)
    print(f"{savefile_name}.pkl has been saved!")
else:
    print(f'No waypoints !')