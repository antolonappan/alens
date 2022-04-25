from diff import DiffCMB
import os

lib_dir =  "/global/u2/l/lonappan/workspace/alens/Data"
data_file = os.path.join(lib_dir,"COM_PowerSpect_CMB-TT-full_R3.01.txt")
inifile1 = os.path.join(lib_dir,"LCDM_params.ini")
inifile2 = os.path.join(lib_dir,"LCDM+Alens_params.ini")
inifiles = [inifile1,inifile2]
nside = 1024
nsim = 100

Diff = DiffCMB(lib_dir,data_file,inifiles,nsim,nside)

if __name__ == '__main__':
    
    Diff.get_stat_mpi()