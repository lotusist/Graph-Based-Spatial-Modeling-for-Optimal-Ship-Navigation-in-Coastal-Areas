import os
import numpy as np
import pandas as pd
from scipy.ndimage import label, sum
import math
from itertools import product
from scipy import sparse
import csv
import tcod

env = {r[0]: r[1] for r in csv.reader(open('settings.csv'))}

# The entire Korean Water
minlat=int(env['minlat']) #31
maxlat=int(env['maxlat']) #39
minlon=int(env['minlon']) #124
maxlon=int(env['maxlon']) #132
gridsize=int(env['gridsize'])
C = 200  


type_ton_category = dict(B = '500 10000'.split(), 
                         C = '20000 100000'.split()
                         )

saved_dir = './save'
save_dir = './save/proc_traj'
DATAFD = 'D/data'

water = np.load(f'{saved_dir}/water.npz')['water']
b = ~water.astype(bool)

def lat2idx(lat):
  ridx = int((maxlat-lat)*gridsize)
  return ridx

def lon2idx(lon):
  cidx = int((lon-minlon)*gridsize)
  return cidx

# Target Water 
MIN_LAT = int(env['aoi_min_lat'])#33 # south 서귀포
MAX_LAT = int(env['aoi_max_lat'])#36 # north 군산
MIN_LON = int(env['aoi_min_lon'])#125 # west 가거도
MAX_LON = int(env['aoi_max_lon'])#128 # east 여수남해

# area of interest
MIN_RIDX = lat2idx(MIN_LAT) #12000 # south lim
MAX_RIDX= lat2idx(MAX_LAT) #6000 # north lim
MIN_CIDX = lon2idx(MIN_LON) #2000 # west lim
MAX_CIDX = lon2idx(MAX_LON) #8000 # east lim

def ll2idx(lat, lon):
  ridx = lat2idx(lat)
  cidx = lon2idx(lon)
  return (ridx, cidx)

def df_ll2idx(df: pd.DataFrame):
  df['ridx'] = df['lat'].apply(lat2idx)
  df['cidx'] = df['lon'].apply(lon2idx)
  return df

def df2list(df: pd.DataFrame):
  temp = [(ridx, cidx) for ridx, cidx in zip(df['ridx'], df['cidx'])]
  waypoints_list = []
  for i in temp:
    if i not in waypoints_list: waypoints_list.append(i)
  return waypoints_list



def split_array(input_array, sub_row_size, sub_col_size, mode='TARGET'):
    """
    Split a large 2D numpy array into smaller sub-arrays of uniform size.

    Parameters:
    input_array (numpy.ndarray): The large 2D input array.
    sub_row_size (int): The number of rows in each sub-array.
    sub_col_size (int): The number of columns in each sub-array.
    mode (str) : 'TARGET' or 'WHOLE'

    Returns:
    dict: A dictionary with keys as sub-array indices and values as tuples
          containing (min_row_index, max_row_index, min_col_index, max_col_index).
    """
    num_rows, num_cols = input_array.shape
    sub_arrays_info = {}
    row_index = 0
    col_index = 0

    for row_start in range(0, num_rows, sub_row_size):
        col_index= 0
        for col_start in range(0, num_cols, sub_col_size):
            row_end = min(row_start + sub_row_size, num_rows)
            col_end = min(col_start + sub_col_size, num_cols)
            if mode =='TARGET':
              t_row_start = row_index*sub_row_size + MAX_RIDX
              t_row_end = t_row_start + sub_row_size
              t_col_start = col_index*sub_col_size + MIN_CIDX
              t_col_end = t_col_start + sub_col_size
              sub_arrays_info[(row_index, col_index)] = [t_row_start, t_row_end, t_col_start, t_col_end]
            elif mode == 'WHOLE':
              sub_arrays_info[(row_index, col_index)] = [row_start,row_end,col_start,col_end]
            else:
              raise ValueError('mode must be either "TARGET" or "WHOLE". ')
            col_index += 1
        row_index += 1

    return sub_arrays_info



def nnz(a,x,y):
  if a[x,y]>0: return x, y
  tmp = a[x,y]
  a[x,y] = 0
  r,c = np.nonzero(a)
  a[x,y] = tmp
  min_idx = ((r - x)**2 + (c - y)**2).argmin()
  return r[min_idx], c[min_idx]

def lineOfSight(b, p1, p2):
  n = 4  # Steps per unit distance
  dxy = int((np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)) * n)
  i = np.rint(np.linspace(p1[0], p2[0], dxy)).astype(int)
  j = np.rint(np.linspace(p1[1], p2[1], dxy)).astype(int)
  has_collision = np.any(b[i, j])
  return ~has_collision

def PathSmoothing(b, df, distcap = int(C/100)):
  p = [(ridx, cidx) for ridx, cidx in zip(df['ridx'], df['cidx'])]
  if len(df)==0:
    return []
  n = len(df)-1
  k = 0
  previ = 0
  t = [] # stores the sampled waypoints (ridx, cidx)
  idxs = [] # stores the df idices of the sampled waypoints
  t.append(p[0])
  idxs.append(0)
  for i in range(1, n-1):
    if not lineOfSight(b, t[k], p[i+1]): # collision occured! 
      k += 1
      t.append(p[i])
      idxs.append(i)
      previ = i # saves the idx of the last collision point
    else:
      if i-previ>=distcap: 
        k += 1
        t.append(p[i])
        idxs.append(i)
        previ = i
  k += 1
  t.append(p[n])
  idxs.append(n)
  idxs = list(set(idxs))
  df = df.loc[idxs]

  return df#, t

# Filter the DataFrame
def proc_traj_phase1(df):
  filtered_df = df[(df['lat'] >= MIN_LAT) & (df['lat'] <= MAX_LAT) & (df['lon'] >= MIN_LON) & (df['lon'] <= MAX_LON)]
  filtered_df = filtered_df[filtered_df['sog'] > 2]
  if len(filtered_df) > 10:
    return filtered_df

def find_subgraph_key(row, subgraph_info):
    for key, (min_r, max_r, min_c, max_c) in subgraph_info.items():
        if min_r <= row['ridx'] < max_r and min_c <= row['cidx'] < max_c:
            return key
    return None

def convert_waypoint_sub(row, subgraph_info): 
  subgraph_key = row['subgraph_key']
  if subgraph_key == None:
    return (-999, -999)
  else:
    subgraph_info_list = subgraph_info[subgraph_key]
    ridx = row['ridx'] - subgraph_info_list[0]
    cidx = row['cidx'] - subgraph_info_list[2]
  return (ridx, cidx)


def proc_traj_phase2(df, subgraph_info):	
	# Group the dataframe by 'ship_id' and create a dictionary of dataframes
  # Attach subgraph indices and (ridx, cidx) within subgraph

  smoothed_grouped_dataframes = {}
  for name, group in df.groupby('ship_id'):
    temp_df = group.sort_values(by='timestamp', ascending=True)
    # print("Converting ll2idx...")
    temp_df = df_ll2idx(temp_df)
    temp_df = temp_df.reset_index()    
    # print("idx converting done! Path Sampling...")
    temp_df = PathSmoothing(b, temp_df)
    temp_df['subgraph_key'] = temp_df.apply(find_subgraph_key, axis=1, subgraph_info=subgraph_info)
    temp_df = temp_df[temp_df['subgraph_key'] != None]
    # print("converting ridx, cidx into subgraph version....")    
    temp_df['subgraph_rc_index'] = temp_df.apply(convert_waypoint_sub, axis=1, subgraph_info=subgraph_info)
    temp_df = temp_df[temp_df['subgraph_rc_index'] != (-999, -999)]
    smoothed_grouped_dataframes[name] = temp_df
	
  return smoothed_grouped_dataframes


def proc_ton(x, shiptype):
  if shiptype =='B':
    if 0<x<500: return '500'
    elif x<10000: return '10000'
    else: return 'NT'
  elif shiptype == 'C':
    if 0<x<20000: return '20000'
    elif 40000<x<100000: return '100000'
    else: return 'NT'
  else:
    return 'NT'


def remove_isolated_water_areas(cost_matrix, threshold=4138332):
  labeled_array, num_features = label(cost_matrix == 1)
  component_sizes = sum(cost_matrix, labeled_array, index=range(1, num_features+1))
  small_components = np.isin(labeled_array, np.where(component_sizes <= threshold)[0] + 1)
  cost_matrix[np.logical_and(small_components, cost_matrix == 1)] = 0
    
  return cost_matrix


def filter_shiptype(type_ton_dict: dict, ship_traj_dict: dict, target_type: str, target_ton:str):
    """ 
    This function gets a pkl file : many {ship_id: traj_df},
    And ship type tonnage dictionary,
    And target ship type and tonnage. 
    
    This function returns the list of ships_id whose type and ton is of targets in the input pkl file.
    """

    unfiltered_ships = list(ship_traj_dict.keys()) # ship ids in the input pkl file
    able_ships = list(type_ton_dict.keys()) # ships are able to be identified the target type and tonnage

    filtered_ships = []
    for ship in unfiltered_ships:
        if ship in able_ships:
            type_spec = type_ton_dict[ship][0] # for example, 'B103'
            ton_spec = type_ton_dict[ship][1] # for example, '364'
            _type = type_spec[0] # for example, 'B'
            _ton = proc_ton(int(float(ton_spec)), _type) # for example, 'NT'
            if (_type == target_type) and (_ton == target_ton):
                filtered_ships.append(ship)
        else: continue
    return filtered_ships
