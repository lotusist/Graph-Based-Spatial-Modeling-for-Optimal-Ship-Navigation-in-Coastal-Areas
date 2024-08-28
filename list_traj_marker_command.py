import os, sys, pickle
import functions as fcn

save_dir = fcn.env['save_dir']
traj_dir = fcn.env['traj_dir']

subgraph_info_filename = 'subgraph_info_more.pkl'

with open(f"{save_dir}/{subgraph_info_filename}", 'rb') as file: 
    subgraph_info = pickle.load(file)

subgraph_index_list = list()
for key in list(subgraph_info.keys()):
    i = str(key[0])
    j = str(key[1])
    converted_key = i + '_' + j
    subgraph_index_list.append(converted_key)

type_ton_category = fcn.type_ton_category

type_list = list(type_ton_category.keys())

with open(f"{save_dir}/traj_marker.sh", 'w') as sh_file:
    for target_subgraph in subgraph_index_list:
        for target_type in type_list:
            for target_ton in type_ton_category[target_type]:
                sh_file.write(f"time python3 traj_marker.py {target_subgraph} {target_type} {target_ton}\n")
