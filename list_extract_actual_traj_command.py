import os, sys, pickle
import functions as fcn

save_dir = fcn.env['save_dir'] 
type_ton_category = fcn.type_ton_category

type_list = list(type_ton_category.keys())


with open(f"{save_dir}/extract_actual_traj.sh", 'w') as sh_file:
    for target_type in type_list:
        for target_ton in type_ton_category[target_type]:
            sh_file.write(f"time python3 extract_actual_traj.py {target_type} {target_ton}\n")