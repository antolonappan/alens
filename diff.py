import healpy as hp
import numpy as np
import library as lib
import mpi
import os
import pickle as pk


class DiffCMB:
    
    def __init__(self,lib_dir,datafile,inifiles,nsim,nside):
        self.lib_dir = lib_dir
        self.nsim = nsim
        self.nside = nside
        
        if mpi.rank == 0:
            os.makedirs(lib_dir,exist_ok=True)
        
        self.spectra = lib.MakeSpectra(lib_dir,datafile,inifiles).spectra
        
        fname = os.path.join(lib_dir,f'seeds_{nsim}.pkl')
        if (not os.path.isfile(fname)) and (mpi.rank == 0):
            seeds = self.get_seeds
            pk.dump(seeds, open(fname,'wb'), protocol=2)
        mpi.barrier()
        self.seeds = pk.load(open(fname,'rb'))
        self.fname = os.path.join(self.lib_dir,f'diff_spectra_{nsim}_{nside}.pkl')
    
    
    @property
    def get_seeds(self):
        seeds =[]
        no = 0
        while no <= self.nsim-1:
            r = np.random.randint(11111,99999)
            if r not in seeds:
                seeds.append(r)
                no+=1
        return seeds
    
    def get_diff(self,idx):
        
        np.random.seed(self.seeds[idx])
        data_map = hp.synfast(self.spectra['data'],nside=self.nside)
        
        np.random.seed(self.seeds[idx])
        theory_map1 = hp.synfast(self.spectra['theory1'],nside=self.nside)
        
        diff1 = hp.anafast(data_map - theory_map1)
        del theory_map1
        
        np.random.seed(self.seeds[idx])
        theory_map2 = hp.synfast(self.spectra['theory2'],nside=self.nside)
        
        diff2 = hp.anafast(data_map - theory_map2)
        del (data_map,theory_map2)
        

        print('Difference computed')
        return diff1,diff2
    
    
    def get_stat_mpi(self):
        
        diff1,diff2 = self.get_diff(mpi.rank)
        
        if mpi.rank == 0:
            total_diff1 = np.zeros_like(diff1)
            total_diff2 = np.zeros_like(diff2)
        else:
            total_diff1 = None
            total_diff2 = None
            diff1_mean = None
            diff2_mean = None
        
        mpi.com.Reduce(diff1,total_diff1, op=mpi.mpi.SUM,root=0)
        mpi.com.Reduce(diff2,total_diff2, op=mpi.mpi.SUM,root=0)
        
        if mpi.rank == 0:
            diff1_mean = total_diff1/mpi.size
            diff2_mean = total_diff2/mpi.size
            
        diff1_mean  = mpi.com.bcast(diff1_mean,root=0)
        diff2_mean  = mpi.com.bcast(diff2_mean,root=0)
        
        print("Mean Computed")
        
        var1 = (diff1 - diff1_mean)**2
        var2 = (diff2 - diff2_mean)**2

        if mpi.rank == 0:
            total_var1 = np.zeros_like(var1)
            total_var2 = np.zeros_like(var2)
        else:
            total_var1 = None
            total_var2 = None

        mpi.com.Reduce(var1,total_var1,op=mpi.mpi.SUM,root=0)
        mpi.com.Reduce(var2,total_var2,op=mpi.mpi.SUM,root=0)
        
        mpi.barrier()

        if mpi.rank == 0:
            std1 = np.sqrt(total_var1/(mpi.size))
            std2 = np.sqrt(total_var2/(mpi.size))
            
            result = {}
            
            result['mean1'] = diff1_mean
            result['mean2'] = diff2_mean
            result['std1'] = std1
            result['std2'] = std2
            
            pk.dump(result,open(self.fname,'wb'))
        
        mpi.barrier()
        print('file saved')

    def get_stat_nompi(self):
         raise NotImplementedError

    @property
    def get_stat(self):
        if os.path.isfile(self.fname):
            return pk.load(open(self.fname,'rb'))
        else:
            self.get_stat_nompi()
               