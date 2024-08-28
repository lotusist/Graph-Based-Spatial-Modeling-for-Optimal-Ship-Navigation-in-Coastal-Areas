import numpy as np
import pandas as pd
import pickle
import sys
import os 
import pickle
import zipfile

import functions as fcn

zip_file = sys.argv[1] # AIS0701-0730.zip
file     = sys.argv[2] # SV00_AIS_TRACK_20220701_12.csv

save_dir = fcn.env['save_dir'] 
traj_dir = fcn.env['traj_dir']
DATAFD = fcn.env['datafd']
subgraph_info_filename = 'subgraph_info.pkl'

os.makedirs(traj_dir, exist_ok=True)


with open(f"{save_dir}/header.pickle", 'rb') as header_file:
    HCOL = pickle.load(header_file)
    # TTD  = pickle.load(file3)

with open(f"{save_dir}/{subgraph_info_filename}", 'rb') as sub_info_file: 
    subgraph_info = pickle.load(sub_info_file)    


columns_order = ['SHIP_ID', 'RECPTN_DT', 'LA', 'LO', 'SOG', 'COG']
data_types = {
    'SHIP_ID': 'str',
    'RECPTN_DT': 'str',
    'LA': 'float32',
    'LO': 'float32',
    'SOG': 'int',
    'COG': 'int'
}

zip_file = zipfile.ZipFile(f'{DATAFD}/{zip_file}')
csv_file = zip_file.open(file)
usecols = [HCOL[file][col] for col in columns_order]

if len(file.split("_")) == 5:
    df = pd.read_csv(csv_file, header= None, usecols=usecols, skiprows=1)
else:
    df = pd.read_csv(csv_file, header= None, usecols=usecols)
df.columns = columns_order
df = df.astype(data_types)


df = df.rename(columns={'SHIP_ID': 'ship_id', 'RECPTN_DT':'timestamp', 'LA':'lat', 'LO':'lon', 'SOG':'sog', 'COG':'cog'})
df['timestamp'] = pd.to_datetime(df['timestamp'])

_name = file.split('.')[0].split('_')[3:]
pickle_name = '_'.join(_name)

print(f"{pickle_name}.csv enters phase 1")
df = fcn.proc_traj_phase1(df)
print(f"{pickle_name}.csv enters phase 2")
ship_df_dict = fcn.proc_traj_phase2(df, subgraph_info)


with open(f'{traj_dir}/{pickle_name}.pkl', 'wb') as dict_:
    pickle.dump(ship_df_dict, dict_)
print(f"{pickle_name}.pkl has been saved!")