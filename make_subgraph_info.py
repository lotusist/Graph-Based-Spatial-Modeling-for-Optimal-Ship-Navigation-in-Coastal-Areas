import os
import numpy as np
import pickle
import functions as fcn

save_dir = fcn.env['save_dir']

water_filename = 'water'


# area of interest
MIN_RIDX = fcn.MIN_RIDX #12000 # south lim
MAX_RIDX= fcn.MAX_RIDX #6000 # north lim
MIN_CIDX = fcn.MIN_CIDX #2000 # west lim
MAX_CIDX = fcn.MAX_CIDX #8000 # east lim

water = np.load(f'{save_dir}/{water_filename}.npz')['water'] # 2D numpy array.
_water = water[MAX_RIDX:MIN_RIDX, MIN_CIDX:MAX_CIDX] 

knife_info = fcn.split_array(_water, 1000, 1000, mode='TARGET')

print("Selecting the useful subgraphs...")
useful_subgraphs = list()
for key, (min_r, max_r, min_c, max_c) in knife_info.items():
    subgraph = water[min_r:max_r, min_c:max_c]
    num_zeros = np.count_nonzero(subgraph == 0)
    total_elements = subgraph.size
    ratio_of_zeros = num_zeros / total_elements
    if ratio_of_zeros < 0.9:
        useful_subgraphs.append(key)
 

print("USEFUL SUBGRAPHS IDX : ", len(useful_subgraphs), useful_subgraphs)

sublist_knife_info = {key: knife_info[key] for key in useful_subgraphs if key in knife_info}

more_useful_subgraphs = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]
sublist_knife_info = {key: knife_info[key] for key in more_useful_subgraphs if key in knife_info}

with open(f'{save_dir}/subgraph_info_more.pkl', 'wb') as file:
    pickle.dump(sublist_knife_info, file)
print(f"subgraph_info_more.pkl has been saved!")