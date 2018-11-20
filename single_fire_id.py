#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 19:30:08 2018

@author: ehsan
"""

import pandas as pd

import numpy as np

##############################################################

cleaning_date = '2014-08-15'

rows_to_skip = 0

# input files - should be output file from my LANDIS code
ptinv_FullFilePath = '/Users/ehsan/Documents/PYTHON_CODES/USFS_fire/outputs/ptinv_14_dropped.csv'

ptday_FullFilePath = '/Users/ehsan/Documents/PYTHON_CODES/USFS_fire/outputs/ptday_14_dropped.csv'

# output files
output_dir = '/Users/ehsan/Documents/PYTHON_CODES/USFS_fire/outputs/'

ptinv_output_name = 'ptinv_15_singleFID.csv'

ptday_output_name ='ptday_15_singleFID.csv'

##############################################################

print('----------------------------------------------------')
print('-> input files are = ')

print(ptinv_FullFilePath)

print(ptday_FullFilePath)

print('----------------------------------------------------')

df_input_ptday = pd.read_csv( ptday_FullFilePath , skiprows=rows_to_skip , quoting=3 , quotechar='"', infer_datetime_format=True)

df_input_ptday['new_date'] = pd.to_datetime( df_input_ptday.DATE , format='"%m/%d/%y"')

# filter for a specific date
filter_date = ( df_input_ptday.new_date == cleaning_date )

# take the date out
df_date = df_input_ptday[ filter_date ].copy()

print('-> no. of rows in inputDF before dropping is = %s' %df_input_ptday.shape[0])

# remove the chunck from input DF
df_input_ptday.drop( df_date.index , inplace=True )

print('-> no. of extracted rows is = %s ' %df_date.shape[0] )

print('-> no. of remaining rows in inputDF after deleting the chunck is now = %s' %df_input_ptday.shape[0])

FID_list_tot = np.array([])

# list of all FIDs inside the chunck for filtered date
FID_list_tot = df_date.FIREID

print('-> before dropping duplicate FIDs, (%s) FireID are in FID total list ...' %FID_list_tot.shape)

# pick the first FID to keep
FID_selected = FID_list_tot.iloc[0]

# filter on selected FID to keep it
filter_FID_selected = ( df_date.FIREID == FID_selected )

# filter the chunck to extract the first fire
fire_selected = df_date[filter_FID_selected].copy()

print('-> selected fire is = %s' %fire_selected.FIREID.iloc[0])

print('-> no. of pollutants selected is = %s' %fire_selected.shape[0])

# define concatinating DFs
concat_list = [ df_input_ptday , fire_selected]

# add selected fire to the end of inputDF
df_input_ptday = pd.concat( concat_list , axis=0)

print('-> tail of updated ptday df is ...' )

print(df_input_ptday.tail())

# drop duplicate FIDs in FID total list
FID_list_dup_droped = FID_list_tot.drop_duplicates( keep='first' ) #, inplace=True)

print('-> after dropping duplicate FIDs, (%s) unique FireID remains in FID total list ...' %FID_list_dup_droped.shape)

##############################################################

print('-> now removing redundant FIDs from PTINV file ... ')

df_input_ptinv = pd.read_csv( ptinv_FullFilePath , skiprows=rows_to_skip , quoting=3 , quotechar='"', infer_datetime_format=True)


for FID in FID_list_dup_droped:

        #print('-> working on FID = %s' %FID)

        if FID == FID_selected:

            print('-> we kept FireID = %s inside PTINV file!' %FID)

        else:

            print('-> FireID = %s deleted from PTINV file!' %FID)

            filter_FID_drop = ( df_input_ptinv.FIREID == FID )

            redundant_fire = df_input_ptinv[filter_FID_drop]

            df_input_ptinv.drop( redundant_fire.index , inplace=True)

# delete redundant columns before writing files out
df_input_ptday.drop( 'new_date' , axis=1 , inplace=True)

df_input_ptday.to_csv ( output_dir+ptday_output_name , sep=',' , index=False , quoting=3 , quotechar='"' )

df_input_ptinv.to_csv ( output_dir+ptinv_output_name , sep=',' , index=False , quoting=3 , quotechar='"' )

print('---------------------------------------------------')

print('-> following files are written out:')

print('-> PTDAY =  "%s"' %(output_dir + ptday_output_name))

print('-> PTINV =  "%s"' %(output_dir + ptinv_output_name))

print('---------------------------------------------------')
