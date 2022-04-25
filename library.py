import camb
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import mpi
import pickle as pk

class camb_spectra:
    def __init__(self,ini,lmax=3000):
        self.ini = ini
        self.lmax = lmax
    
    @property
    def get_powers(self):
        pars = camb.read_ini(self.ini)
        results = camb.get_results(pars)
        return results.get_cmb_power_spectra(pars, CMB_unit='muK')
    
    @property
    def get_temperature(self):
        results = self.get_powers
        temp = results['total'].T[0]
        return temp[:self.lmax+1]

class cl:
    
    def __init__(self,fname):
        spectra = np.loadtxt(fname).T
        ell = spectra[0].astype(int)
        if ell[0] == 2:
            l = np.array([0,1])
            self.ell = np.concatenate((l,ell),axis=0)
            ml = np.array([0,0])
            self.TT = np.concatenate((ml,spectra[1]),axis=0)
        else:
            raise NotImplementedError
        self.lmax = self.ell[-1]

class MakeSpectra:
    
    def __init__(self,lib_dir,fname,ini_list):
        self.lib_dir = lib_dir
        self.data = cl(fname)
        self.theory1 = camb_spectra(ini_list[0],lmax=self.data.lmax)
        self.theory2 = camb_spectra(ini_list[1],lmax=self.data.lmax)
        
        if mpi.rank == 0:
            os.makedirs(lib_dir,exist_ok=True)
            
        self.spectra = self.make
        
    def get_cl(self,Dl):
        l = self.data.ell
        dl = l*(l+1)/(2*np.pi)
        cl = Dl/dl
        cl[0] = 0
        cl[1] = 0
        return cl
        
    @property    
    def make(self):
        fname = os.path.join(self.lib_dir,'spectra.pkl')
        if os.path.isfile(fname):
            return pk.load(open(fname,'rb'))
        else:
            obj = {}
            obj['ell'] = self.data.ell
            obj['data'] = self.get_cl(self.data.TT)
            obj['theory1'] =  self.get_cl(self.theory1.get_temperature)
            obj['theory2'] =  self.get_cl(self.theory2.get_temperature)
            pk.dump(obj,open(fname,'wb'))
            return obj
    @property   
    def plot_spectra(self):
        plt.figure(figsize=(8,8))
        plt.loglog(m.spectra['ell'],m.spectra['data'],label='Data')
        plt.loglog(m.spectra['ell'],m.spectra['theory1'],label='Theory 1')
        plt.loglog(m.spectra['ell'],m.spectra['theory2'],label='Theory 2')
        plt.legend(fontsize=15)

