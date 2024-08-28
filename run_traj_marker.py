import subprocess
import multiprocessing
import os

cpus = 100
sh_filename = './traj_marker.sh'

def run(cmd):
    subprocess.run(cmd, shell=True)

commands = []
commands += [line.strip() for line in open(sh_filename).readlines()]
p = multiprocessing.Pool(processes=cpus)
p.map(run, commands)