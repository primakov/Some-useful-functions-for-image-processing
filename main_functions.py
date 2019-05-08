# -*- coding: utf-8 -*-
"""
Created on Wed May  8 20:44:42 2019

@author: s.primakov
"""

import pydicom
import numpy as np
import pandas as pd
from tqdm import tqdm
import os,re,sys

def val_check(file,value):
    try:
        val = getattr(file,value)
        if val == '' or val==' ':
            return 'NaN'
        else:
            return val
    except:
        return 'NaN'
    
def rename_dcms(folders,dir_path,replace_names_with_numbers=False):
    for folder in tqdm(folders):
        for roots,dirs,files in os.walk(os.path.join(dir_path,folder)):
            if replace_names_with_numbers: ind=0
            for file in files:
                if file[-4:]!='.dcm':
                    try:
                        temp_dcm_file = pydicom.read_file(os.path.join(roots, file),force=True)
                    except:
                        temp_dcm_file = None
                        print('Some problems with: ',file)

                    if val_check(temp_dcm_file,'Modality') != 'NaN' and not(replace_names_with_numbers):
                        os.rename(os.path.join(roots, file),os.path.join(roots,'%s.dcm'%file))
                    elif val_check(temp_dcm_file,'Modality') != 'NaN' and replace_names_with_numbers:
                        os.rename(os.path.join(roots, file),os.path.join(roots,'%d_%s.dcm'%(ind,str(temp_dcm_file.Modality))))
                        ind+=1
    
    return 'Done!'

def parse_dataset(dir_path,columns_list,spl_char='_'):
    dataset_stats = pd.DataFrame(data=None,columns = columns_list )
    n_of_scans = 0 # in case if some values in header is nan it'll check n_of_scans following scans
    patients = os.listdir(dir_path)
    for patient in tqdm(patients):
        for roots,dirs,files in os.walk(os.path.join(dir_path,patient)):
            for file in files:
                if file.endswith('.dcm'): 
                    dcm_img = pydicom.read_file(os.path.join(roots,file),force=True)
                    
                    if any([val_check(dcm_img,x)=='NaN' for x in columns_list]):
                        n_of_scans+=1   # if one of the values is missing for patient then check next slices
                        if n_of_scans == 3: # if 3 slices missing same values for patient then probably rest scans also missing these values so writing nans instead of these values
                            dataset_stats = dataset_stats.append(pd.Series([val_check(dcm_img,x) for x in columns_list],
                                                                           index = columns_list),ignore_index=True)           

                            n_of_scans=0
                            break
                        pass
                    else:
                        dataset_stats = dataset_stats.append(pd.Series([val_check(dcm_img,x) for x in columns_list],
                                                                           index = columns_list),ignore_index=True)
                        break
                    
    return dataset_stats

