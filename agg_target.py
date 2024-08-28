import os, sys, pickle
import numpy as np
import functions as fcn

save_dir = fcn.env['save_dir']
target_dir = fcn.env['target_dir']

target_type = 'C'
target_ton = '20000'
target_number = sys.argv[1] # 0.01, 0.001, 0.0001, 1e-5
target_category = target_type + '_' + target_ton

water_filename = 'water'
dist_filename = 'dist_water'


# area of interest
MIN_RIDX = fcn.MIN_RIDX #12000 # south lim
MAX_RIDX= fcn.MAX_RIDX #6000 # north lim
MIN_CIDX = fcn.MIN_CIDX #2000 # west lim
MAX_CIDX = fcn.MAX_CIDX #8000 # east lim

water = np.load(f'{save_dir}/{water_filename}.npz')['water'] # 2D numpy array.
_water = water[MAX_RIDX:MIN_RIDX, MIN_CIDX:MAX_CIDX] 
knife_info = fcn.split_array(_water, 1000, 1000, mode='TARGET')

subgraph_position_list = list()
for i in range(1, 3):
    for j in range(1, 3):
        subgraph_position_list.append((i,j))

subgraph_position = dict()

for (i,j) in subgraph_position_list:
    search_target = f'{i}_{j}_{target_category}_{target_number}_check_target.npz'

    if os.path.exists(f'{target_dir}/{search_target}'):
        subgraph_position[(i, j)] = np.load(f'{target_dir}/{search_target}')['arr_0']
    else:
        subgraph_info = knife_info[(i, j)]
        _water = water[subgraph_info[0]:subgraph_info[1], subgraph_info[2]:subgraph_info[3]]
        subgraph_position[(i, j)] = _water

        print(f'{(i, j)} of {target_category} is just water')


# Create a larger array filled with zeros (3000x3000 for a 3x3 grid of 1000x1000 arrays)
row_grid_size = 2
col_grid_size = 2

subarray_size = 1000
larger_array = np.zeros((row_grid_size * subarray_size, col_grid_size * subarray_size))
print(larger_array.shape)


# Place each smaller array at the specified positions
for (i, j), subarray in subgraph_position.items():
    row_start = (i - 1) * subarray_size
    row_end = i * subarray_size
    col_start = (j - 1) * subarray_size
    col_end = j * subarray_size
    larger_array[row_start:row_end, col_start:col_end] = subarray

target_number = str(target_number)
np.savez(f'{target_dir}/agg_check_{target_category}_{target_number}.npz', larger_array)
print(f'{target_category} {target_number} agg_check has been saved!')