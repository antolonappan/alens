#!/bin/bash
#SBATCH --qos=debug
#SBATCH --constraint=haswell
#SBATCH --nodes=10
#SBATCH --ntasks=100
#SBATCH --cpus-per-task=1
#SBATCH -J Diff
#SBATCH -o out/Diff.out
#SBATCH -e out/Diff.err
#SBATCH --time=00:30:00



source /global/homes/l/lonappan/.bashrc
conda activate PC2
cd /global/u2/l/lonappan/workspace/alens

mpirun -np $SLURM_NTASKS python Stat.py