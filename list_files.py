# run examples
# python3 list_files.py AIS0601-0630.zip AIS0701-0730.zip AIS0801-0830.zip AIS0901-0930.zip AIS1001-1030.zip AIS1101-1118.zip AIS1119-1130.zip

import sys, os, zipfile, pickle, csv, codecs
from multiprocessing import cpu_count
import functions as fcn


save_dir = fcn.env['save_dir'] #fcn.saved_dir 

def process():
    hcol = {}
    h    = {}
    # cnt  = 0
    
    with open(f"{save_dir}/traj_proc.sh", 'w') as sh_file:
        for zip_file_name in sorted(ZIP_FILE_NAMES):
            zip_file = zipfile.ZipFile(f"{DATAFD}/{zip_file_name}", 'r')
            files    = sorted([file for file in zip_file.namelist() if file.endswith('.csv')])

            for file in files:
                # cnt += 1

                sh_file.write(f"time python3 traj_proc.py {zip_file_name} {file}\n")

                if len(file.split('_')) == 5:
                    cur  = csv.reader(codecs.iterdecode(zip_file.open(files[0]), "UTF-8"))
                    head = next(cur)

                    LA, LO, SOG, COG, RECPTN_DT, SHIP_ID = [head.index(v) for v in HSTUBS]

                    h          = dict(LA=LA, LO=LO, SOG=SOG, COG=COG, RECPTN_DT=RECPTN_DT, SHIP_ID=SHIP_ID)
                    hcol[file] = h
                elif len(file.split('_')) == 6:
                    if len(h) == 0:
                        raise ValueError(f"Header row is not found for {file} in {zip_file_name}.")
                    hcol[file] = h
                else:
                    raise ValueError("Filenames should contain only 4 or 5 '_' characters.")
    
    
    os.chmod(f'{save_dir}/traj_proc.sh', 0o755)

    with open(f'{save_dir}/header.pickle', 'wb') as pfile:
        pickle.dump(hcol, pfile)



def get_info():
    # read only vars are const global vars
    global DATAFD
    global ZIP_FILE_NAMES
    global HSTUBS

    DATAFD   = fcn.env['datafd'] 
    cores    = int(fcn.env['cores']) # 120
    args     = sys.argv[1:]
    HSTUBS = 'LA LO SOG COG RECPTN_DT MMSI'.split()

    ZIP_FILE_NAMES = args[1:]

    print(f'CPU cores identified: {cpu_count()}')
    print(f'{cores} CPU cores are requested.')
    print(f'Processing the following files: {ZIP_FILE_NAMES}')


def main():
    get_info()
    process()


if __name__ == "__main__":
    main()