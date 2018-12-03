
############################################################################
# usage: Convert LANDIS-II model output to SMOKE input.
# date: Sep 20, 2018
# auther: Ehsan Mosadegh (ehsanm@dri.edu)
#
# NOTES:
#	- each unique fire is defined by = region + fireID
#
# NEED TODO:
#	- add header row
#	- add spinup day from previous month to both PTDAY and PTINV
#
############################################################################

import os
import pandas as pd
import datetime as dt

#############################################################################

#+--------------------------------------------------------+
#      select run mode and input parameters               |
#+--------------------------------------------------------+
mode_index  = 1    #
POL_input_emis_unit = 'megagrams'
POL_output_emis_unit = 'tons'
emis_conv_factr_2tone = 1   # unit convert factor for POL emissin; what is POL emission units? kg? tons?  |
pixel_area_in_Ha = 1 # Hactare (= 10^4 m2); convert hactare-> acres; pixel size is 1-hactare; convert to Acres for SMOKE!
region_code = '"06017"'#                                  |
fire_modeling_yr = 14  # year w/o century
LANDIS_yr = 30
LANDIS_Scenario = 1                           #       |
Ha_to_Acre_rate = 2.47105 # rate to change to Ha to Acre  |
input_file = 'Scenario1_year30latlon.csv'#                      |
modeling_month = '08'#                                    |
write_output = 'no' #   (yes, no)                        |
#+--------------------------------------------------------+
#       select run mode based on here                     |
#+--------------------------------------------------------+
mode_ref_index = [      0       ,     1      ]  #         |
mode_list      = ['SCC_devided' , 'SCC_total']  #         |
mode      	     = mode_list[mode_index]          #         |
jday_annual_list = range(213,244)                  #         |
#+--------------------------------------------------------+
#############################################################################


#############################################################################
# set pathes, directory names, read-in data

print('+----------------------------------------------------+')
print('-> run time settings are ...')
print('+----------------------------------------------------+')
#print('| mode index is     = %s         ' %mode_index)
print('| input emission unit is = %s' %POL_input_emis_unit )
print('| output emission unit is = %s' %POL_output_emis_unit )
print('| emission convertor factor ( %s to %s ) is = %s' %(POL_input_emis_unit , POL_output_emis_unit , emis_conv_factr_2tone ))
print('| run mode is       = %s         ' %mode)
print('| size of pixel is  = %s hactares (100m * 100m)' %pixel_area_in_Ha)
print('| SMOKE fire year is      = 20%s         ' %fire_modeling_yr)
print('| LANDIS fire scenario year is = %s' %LANDIS_yr)
print('| input file is     = %s         ' %input_file)
print('| modeling month is = %s         ' %modeling_month)
print('| fire region is    = %s         ' %region_code)
print('| write output?     = %s         ' %write_output)
print('+----------------------------------------------------+')

work_dir = '/Users/ehsan/Documents/PYTHON_CODES/USFS_fire'
repository_name = 'LANDIS_to_SMOKE'
script_dir = work_dir+'/github/'+repository_name
input_dir = work_dir+'/inputs'
output_dir = work_dir+'/outputs'

if os.path.isdir(work_dir) == True :
    print('-> work directory exists!')
else:
    print('-> there is an issue with work directory')

input_FilePath = os.path.join(input_dir , input_file)

if os.path.isfile(input_FilePath) == True :
    print('-> input file exists!')
else:
    print('-> input file is NOT there!')
print('+----------------------------------------------------+')

user_input = input('-> do you want to continue with these settings? (Y/N)')

if (user_input == 'n' or user_input == 'N' or user_input == 'no'):
    print('-> setting not approved, or there is an error!')
    print('-> program exits!')

elif (user_input == 'y' or user_input == 'Y' or user_input == 'yes'):
    print('------------------------------')
    print('-> *** start of program ***')

    # --- read-in the input CSV file:

    input_csv = pd.read_csv(input_FilePath)

    # doing some statistics ...
    #filter_Aug_Jdays = (input_csv['Day-of-Fire'] >= 213) & (input_csv['Day-of-Fire'] <= 243)
    #df_filter_Aug = input_csv[filter_Aug_Jdays].copy()

    # --- define a condition (filter) to filter zero-rows:

    #threshold = 0.00001
    #filter_NoZero = (input_csv['Heat-25'] != 0) & (input_csv['NOx-Flaming'] != 0) & (input_csv['N2O-Flaming-25'] != 0)
    filter_NoZero = ( input_csv['Day-of-Fire-%s' %LANDIS_yr] != 0 )
    print('-> Julian days with index=0 are cleaned out!')

    # --- filter the inputDF and copy the chunck to a new DF

    input_csv_filter_NoZero = input_csv[filter_NoZero].copy()
    input_csv_filter_NoZero = input_csv_filter_NoZero.reset_index()  # reset is one-time operation; we should update master DF again!
    print('-> non-zero rows were filtered!')

# set pathes, directory names, read-in data
#########################################################################################################


#########################################################################################################
    # define POL list based on available variables/columns in LANDIS output + S or F labels:

    POL_list_4SCC_devided = ['CO_S','CO_F','CO2_S','CO2_F','CH4_S','CH4_F','SO2_S','SO2_F','NH3_S','NH3_F','NMOC_S','NMOC_F','NOx_S','NOx_F','PM10_S','PM10_S','PM2.5_S','PM2.5_F','heat_flux','acres_burned']

    POL_list_4SCC_total = ['CO_tot','CO2_tot','CH4_tot','SO2_tot','NH3_tot','NMOC_tot','NOx_tot','PM10_tot','PM2.5_tot','heat_flux','acres_burned']

    # header of dictionary: keys= what I define in POL_list_4SCC_devided and as a key; pollutant label based on NEI PTDAY labeling format in DATA column; corresponding value from LANDIS CSV file; SCC=S or F!
    # -> { keys from POL_list_4SCC_devided: [ POL label from DATA col , DATA-VALUE , SCC ] }

    LANDISrow = 0
    # --- for NEI 2014 - devided SCC mode
    #POL_dict_4SCC_devided = {
    #        'CO_S':['CO',input_csv_filter_NoZero['CO-Smoldering'][LANDISrow],'2810001001'],
    #        'CO_F':['CO',input_csv_filter_NoZero['CO-Flaming'][LANDISrow],'2810001002'],
    #        'CO2_S':['CO2',input_csv_filter_NoZero['CO2-Smoldering'][LANDISrow],'2810001001'],
    #        'CO2_F':['CO2',input_csv_filter_NoZero['CO2-Flaming'][LANDISrow],'2810001002'],
    #        'CH4_S':['CH4',input_csv_filter_NoZero['CH4-Smoldering'][LANDISrow],'2810001001'],
    #        'CH4_F':['CH4',input_csv_filter_NoZero['CH4-Flaming'][LANDISrow],'2810001002'],
    #        'SO2_S':['SO2',input_csv_filter_NoZero['SO2-Smoldering-25'][LANDISrow],'2810001001'],
    #        'SO2_F':['SO2',input_csv_filter_NoZero['SO2-Flaming-25'][LANDISrow],'2810001002'],
    #        'NH3_S':['NH3',input_csv_filter_NoZero['NH3-Smoldering-25'][LANDISrow],'2810001001'],
    #        'NH3_F':['NH3',input_csv_filter_NoZero['NH3-Flaming-25'][LANDISrow],'2810001002'],
    #        'NMOC_S':['VOC',input_csv_filter_NoZero['NMOC-Smoldering-25'][LANDISrow],'2810001001'],
    #        'NMOC_F':['VOC',input_csv_filter_NoZero['NMOC-Flaming-25'][LANDISrow],'2810001002'],
    #        'NOx_S':['NOx',input_csv_filter_NoZero['NOx-Smoldering'][LANDISrow],'2810001001'],
    #        'NOx_F':['NOx',input_csv_filter_NoZero['NOx-Flaming'][LANDISrow],'2810001002'],
    #        'PM10_S':['PM10',input_csv_filter_NoZero['PM10-Smoldering-25'][LANDISrow],'2810001001'],
    #        'PM10_F':['PM10',input_csv_filter_NoZero['PM10-Flaming-25'][LANDISrow],'2810001002'],
    #        'PM2.5_S':['PM2.5',input_csv_filter_NoZero['PM2.5-Smoldering-25'][LANDISrow],'2810001001'],
    #        'PM2.5_F':['PM2.5',input_csv_filter_NoZero['PM2.5-Flaming-25'][LANDISrow],'2810001002'],
    #        'heat_flux':['HFLUX',input_csv_filter_NoZero['Heat-25'][LANDISrow],'2810001002'],
    #        'acres_burned':['ACRESBURNED',pixel_area_in_Ha,'2810001002'],
    #        }

    # --- for NEI 2011 - devided SCC mode
#    POL_dict_4SCC_devided = {
#            'CO_S':         ['CO',          input_csv_filter_NoZero['CO-Smoldering'][LANDISrow],      '28100010S0'],
#            'CO_F':         ['CO',          input_csv_filter_NoZero['CO-Flaming'][LANDISrow],         '28100010F0'],
#            'CO2_S':        ['CO2',         input_csv_filter_NoZero['CO2-Smoldering'][LANDISrow],     '28100010S0'],
#            'CO2_F':        ['CO2',         input_csv_filter_NoZero['CO2-Flaming'][LANDISrow],        '28100010F0'],
#            'CH4_S':        ['CH4',         input_csv_filter_NoZero['CH4-Smoldering'][LANDISrow],     '28100010S0'],
#            'CH4_F':        ['CH4',         input_csv_filter_NoZero['CH4-Flaming'][LANDISrow],        '28100010F0'],
#            'SO2_S':        ['SO2',         input_csv_filter_NoZero['SO2-Smoldering-25'][LANDISrow],  '28100010S0'],
#            'SO2_F':        ['SO2',         input_csv_filter_NoZero['SO2-Flaming-25'][LANDISrow],     '28100010F0'],
#            'NH3_S':        ['NH3',         input_csv_filter_NoZero['NH3-Smoldering-25'][LANDISrow],  '28100010S0'],
#            'NH3_F':        ['NH3',         input_csv_filter_NoZero['NH3-Flaming-25'][LANDISrow],     '28100010F0'],
#            'NMOC_S':       ['VOC',         input_csv_filter_NoZero['NMOC-Smoldering-25'][LANDISrow], '28100010S0'],
#            'NMOC_F':       ['VOC',         input_csv_filter_NoZero['NMOC-Flaming-25'][LANDISrow],    '28100010F0'],
#            'NOx_S':        ['NOX',         input_csv_filter_NoZero['NOx-Smoldering'][LANDISrow],     '28100010S0'],
#            'NOx_F':        ['NOX',         input_csv_filter_NoZero['NOx-Flaming'][LANDISrow],        '28100010F0'],
#            'PM10_S':       ['PM10',        input_csv_filter_NoZero['PM10-Smoldering-25'][LANDISrow], '28100010S0'],
#            'PM10_F':       ['PM10',        input_csv_filter_NoZero['PM10-Flaming-25'][LANDISrow],    '28100010F0'],
#            'PM2.5_S':      ['PM2_5',       input_csv_filter_NoZero['PM2.5-Smoldering-25'][LANDISrow],'28100010S0'],
#            'PM2.5_F':      ['PM2_5',       input_csv_filter_NoZero['PM2.5-Flaming-25'][LANDISrow],   '28100010F0'],
#            'heat_flux':    ['HFLUX',       input_csv_filter_NoZero['Heat-25'][LANDISrow],            '28100010F0'],
#            'acres_burned': ['ACRESBURNED', pixel_area_in_Ha,                                         '28100010F0'],
#            }

    # --- for NEI 2011 - total SCC mode
    POL_dict_4SCC_total = {
            'CO_tot':       ['CO',      input_csv_filter_NoZero['CO-Smoldering-%s'%LANDIS_yr][LANDISrow]        +   input_csv_filter_NoZero['CO-Flaming-%s'%LANDIS_yr][LANDISrow],    '2810001000'],
            'CO2_tot':      ['CO2',     input_csv_filter_NoZero['CO2-Smoldering-%s'%LANDIS_yr][LANDISrow]       +   input_csv_filter_NoZero['CO2-Flaming-%s'%LANDIS_yr][LANDISrow],   '2810001000'],
            'CH4_tot':      ['CH4',     input_csv_filter_NoZero['CH4-Smoldering-%s'%LANDIS_yr][LANDISrow]       +   input_csv_filter_NoZero['CH4-Flaming-%s'%LANDIS_yr][LANDISrow],   '2810001000'],
            'SO2_tot':      ['SO2',     input_csv_filter_NoZero['SO2-Smoldering-%s'%LANDIS_yr][LANDISrow]       +   input_csv_filter_NoZero['SO2-Flaming-%s'%LANDIS_yr][LANDISrow],   '2810001000'],
            'NH3_tot':      ['NH3',     input_csv_filter_NoZero['NH3-Smoldering-%s'%LANDIS_yr][LANDISrow]       +   input_csv_filter_NoZero['NH3-Flaming-%s'%LANDIS_yr][LANDISrow],   '2810001000'],
            'NMOC_tot':     ['VOC',     input_csv_filter_NoZero['NMOC-Smoldering-%s'%LANDIS_yr][LANDISrow]      +   input_csv_filter_NoZero['NMOC-Flaming-%s'%LANDIS_yr][LANDISrow],  '2810001000'],
            'NOx_tot':      ['NOX',     input_csv_filter_NoZero['NOx-Smoldering-%s'%LANDIS_yr][LANDISrow]       +   input_csv_filter_NoZero['NOx-Flaming-%s'%LANDIS_yr][LANDISrow],   '2810001000'],
            'PM10_tot':     ['PM10',    input_csv_filter_NoZero['PM10-Smoldering-%s'%LANDIS_yr][LANDISrow]      +   input_csv_filter_NoZero['PM10-Flaming-%s'%LANDIS_yr][LANDISrow],  '2810001000'],
            'PM2.5_tot':    ['PM2_5',   input_csv_filter_NoZero['PM2.5-Smoldering-%s'%LANDIS_yr][LANDISrow]     +   input_csv_filter_NoZero['PM2.5-Flaming-%s'%LANDIS_yr][LANDISrow], '2810001000'],
            'heat_flux':    ['HFLUX',   input_csv_filter_NoZero['Heat-%s'%LANDIS_yr][LANDISrow],                                                                                               '2810001000'],
            'acres_burned': ['ACRESBURNED',pixel_area_in_Ha,                                                                                                                                            '2810001000'],
            }

    # define POL list based on available variables in LANDIS output + S or F labels:
#########################################################################################################


#########################################################################################################
    # define master DF line-by-line with all columns:

    master_header_list = ['FIPS','FIREID','LOCID','SCC','DATA','DATE','DATAVALUE','BEGHOUR','ENDHOUR','LAT','LON','FIRENAME','NFDRSCODE','MATBURNED','HEATCONTENT','DATE_obj','LANDIS_jday'] # DF will be organized bbased on this order!

    df_master = pd.DataFrame( columns = master_header_list )

    total_row_no = input_csv_filter_NoZero.shape[0]

    print('-> start calculating LANDIS conversion for %s rows (fires) ...' %total_row_no)

    # loop for each day and for each element inside POL_list_4SCC_devided:
    # maps mode to a list and we have to select the index
    SCCmode_toPOL_mapper = {
            'SCC_total'   : [POL_list_4SCC_total   , POL_dict_4SCC_total] }#,

#            'SCC_devided' : [POL_list_4SCC_devided , POL_dict_4SCC_devided] ,
#                    }

    print('-> some run info are:')
#    print('-> POL list is = %s' %SCCmode_toPOL_mapper[mode][0])
#    print('-> POL dictionary is = %s' %SCCmode_toPOL_mapper[mode][1])

    print('-> LANDIS columns/variables that we use in this run are...')

    for pol in SCCmode_toPOL_mapper[mode][0]:

        print('-> LANDIS col = %s ' %SCCmode_toPOL_mapper[mode][1][pol][0])

    for LANDISrow in range(total_row_no):  #

        if (LANDISrow/100)==int(LANDISrow/100):

            print('-----------> row no.=%s from %s' %(LANDISrow,total_row_no))

        for pol in SCCmode_toPOL_mapper[mode][0]:  # pol = LANDIS col ; processes all elements inside POL_list_4SCC_devided 1-by-1; and calculates every row of PTDAY
            #print('-> row=%s' %LANDISrow)
            #print('-> POL is = %s' %pol)

            # --- modify data and datavlues files -----------------------------

            DATA = '"'+str(SCCmode_toPOL_mapper[mode][1][pol][0])+'"'  # maps POL key to POL name ; extracts the name of pollutant
            #print('-> DATA is = %s' %DATA)
            DATAVALUE = SCCmode_toPOL_mapper[mode][1][pol][1]  # extracts the value of pollutant
            SCC = '"'+SCCmode_toPOL_mapper[mode][1][pol][2]+'"'   # extracts SCC
            #print('-> SCC is = %s' %SCC)

            # --- change units ----------------------------------------------

            if DATA == '"ACRESBURNED"':

                DATAVALUE = DATAVALUE*Ha_to_Acre_rate

            elif DATA == '"HFLUX"':

                KW_per_day_pixel = DATAVALUE*pixel_area_in_Ha*10000  # change from KW/m2 to KW/pixel; both per day!
                BTU_per_day_pixel = KW_per_day_pixel*3412.14  # change from KW/pixel to BTU/pixel; both per day!
                DATAVALUE = BTU_per_day_pixel

            else:
                DATAVALUE = DATAVALUE * emis_conv_factr_2tone  # to change POL units from kg/ha to tons/day

            # --- modify dates from julian to calendar dates ------------------------------------------------

            LANDIS_Jday = input_csv_filter_NoZero['Day-of-Fire-%s'%LANDIS_yr][LANDISrow]

            if LANDIS_Jday == 0:

                print('-> there is an issue with filtering')

            if 1 <= LANDIS_Jday <= 99:

                fire_Jdate = str(LANDIS_Jday).rjust(3, '0')  # 3 is string length in total! also, there should be a space before '0'!

            else:

                fire_Jdate = str(LANDIS_Jday)

            yy_jjj = str(fire_modeling_yr) + fire_Jdate
            day_dt = dt.datetime.strptime(yy_jjj , '%y%j').date()  # strptime accepts str
            day_str = day_dt.strftime('%m/%d/%y')
            DATE = '"'+day_str+'"'  # to produce "string_dates" to write out to CSV
            DATE_obj = day_str      # to be able to put filter on it later for favorable month

            # --- set fire labling/identifying parameters ----------------------

            FIREID = '"'+'FID_'+str(input_csv_filter_NoZero['pointid'][LANDISrow])+'"'
#            LOCID = '"'+'PID_'+str(input_csv_filter_NoZero['pointid'][LANDISrow])+'"'
            LOCID = '"-9"'

            # --- set lat/lon ----------------------

            LAT = input_csv_filter_NoZero['Long'][LANDISrow]  # the file I used had Lat in Long place
            LON = input_csv_filter_NoZero['Lat'][LANDISrow]   # so I used them in place of each other

            # --- fixed parameters ---------------------------------------------

            FIPS = region_code
            BEGHOUR = 0
            ENDHOUR = 23
            FIRENAME = '"'+'USFS_FireScen_'+LANDIS_Scenario+'"'
            NFDRSCODE = '"-9"'
            MATBURNED = 12
            HEATCONTENT = 8000

            # --- joining section ----------------------------------------------

            new_row = [[FIPS,FIREID,LOCID,SCC,DATA,DATE,DATAVALUE,BEGHOUR,ENDHOUR,LAT,LON,FIRENAME,NFDRSCODE,MATBURNED,HEATCONTENT,DATE_obj,LANDIS_Jday]] # first make a new row; NOTE: define a row of list with [[x,y]]
            new_df_line = pd.DataFrame( new_row , columns = master_header_list )  # define a DF from a list with columns.
            real_frames_list = [df_master , new_df_line]
            df_master = pd.concat(real_frames_list , axis=0)  # then concat(both DFs together along x-axis=0= vertical ???)

    # define master DF line-by-line with all columns:
#########################################################################################################


#########################################################################################################
    # modify and filter master DF
    print('-> NOTE: pollutant (DATAVALUE) units converted from POL_input_emis_unit --> POL_output_emis_unit')
    print('-> NOTE: pointID column from LANDIS is selected as FIREID for SMOKE!')

    # --- change dtype of BEGHOUR and ENDHOUR columns inside master DF from float->int

    df_master.BEGHOUR = df_master.BEGHOUR.astype(int)
    df_master.ENDHOUR = df_master.ENDHOUR.astype(int)
    df_master.MATBURNED = df_master.MATBURNED.astype(int)

    #list_of_cols = ['BEGHOUR','ENDHOUR']
    #df_master[list_of_cols] = df_master[list_of_cols].astype(int)
    #->>>>>>>>> I can add <if> syntax later here for each month ###########

    # --- change DATE_obj col to new date-time col to filter later

    df_master['DATE_date_time'] = pd.to_datetime(df_master['DATE_obj'])# , format= '%m%d%y')
    print('-> a new col = "DATE_date_time" added to the end of df_master; to filter date-time DATA for a month!')

    # --- filter date-time col for favorable month

    filter_Month = (df_master['DATE_date_time'] >= '2014-'+modeling_month+'-01') & (df_master['DATE_date_time'] <= '2014-'+modeling_month+'-30')
    df_master_filtered_month = df_master[filter_Month].copy()
    print('-> input-DF is filtered for month = %s' %modeling_month)

    # modify and filter master DF
#########################################################################################################


#########################################################################################################
    # dealing with missing dates and fake data

    # --- looking for missing jdays

    df_master_filtered_month.LANDIS_jday = df_master_filtered_month.LANDIS_jday.astype(int)

    LANDIS_jday_col = df_master_filtered_month.LANDIS_jday

    LANDIS_jday_col.drop_duplicates( keep='first' , inplace=True)

    LANDIS_jday_list = LANDIS_jday_col.tolist()

    # --- define julian day annual list

    leap_yr_list = [2000,2004,2008,2012,2016,2020]

    if fire_modeling_yr in leap_yr_list:

        jday_annual_list = range(1,367)

    else:

        jday_annual_list = range(1,366)

    # --- define new col headers

    master_header_list_updated = ['FIPS','FIREID','LOCID','SCC','DATA','DATE','DATAVALUE','BEGHOUR','ENDHOUR','LAT','LON','FIRENAME','NFDRSCODE','MATBURNED','HEATCONTENT','DATE_obj','LANDIS_jday','DATE_date_time'] # DF will be organized bbased on this order!

    # --- define fire date list

    fire_days_list    = []  # list of fire days in LANDIS

    missing_jdays_list = []  # list of jdays that is not inside LANDIS and therefore LANDIS does not have fires for them

    for jday in jday_annual_list :

        if jday in LANDIS_jday_list:

            print('Jday = %s is in LANDIS data file!' %jday)

            fire_days_list.append(jday)

        else:

            print('-> LANDIS has NO fire for Jday (%s) !' %jday)

            missing_jdays_list.append(jday)


    for missing_jday in missing_jdays_list :

        print('-> making fake fire emissions for Jday %s...' %missing_jday)

        for pol_fake in SCCmode_toPOL_mapper[mode][0]:

            #print('-> doing for fake day = %s and POL = %s' %(missing_jday,pol_fake))

            # --- extract pollutant and data value from dictionary ----------------

            FIPS_fake   = region_code
            FIREID_fake = '"'+'FID_fake_'+str(missing_jday)+'"'
#            LOCID_fake  = '"'+'PID_fake_'+str(missing_jday)+'"'
            LOCID_fake  = '"-9"'
            SCC_fake    = '"'+SCCmode_toPOL_mapper[mode][1][pol_fake][2]+'"'
            DATA_fake   = '"'+str(SCCmode_toPOL_mapper[mode][1] [pol_fake] [0])+'"'

            # --- preparing jday to dt --------------------------------------------

            yy_jjj_str  = str(fire_modeling_yr) + str(missing_jday)
            day_dt      = dt.datetime.strptime(yy_jjj_str , '%y%j')  # strptime( str ) produces dt; need for filtering
            day_str     = day_dt.strftime('%m/%d/%y')               # change format of dt
            DATE_fake   = '"'+day_str+'"'                         # make this to produce "string_dates" to write out to CSV; need for CSV file

            # --- other fixed fields ----------------------------------------------

            DATAVALUE_fake  = '1'

            BEGHOUR_fake    = 0
            ENDHOUR_fake    = 23
            LAT_fake        = 38.95456
            LON_fake        = -120.07861
            FIRENAME_fake   = '"USFS_fakefire"'
            NFDRSCODE_fake  = '"-9"'
            MATBURNED_fake  = 12
            HEATCONTENT_fake = 8000

            # --- form fake row --------------------------------------------------

            fake_row = [[FIPS_fake,FIREID_fake,LOCID_fake,SCC_fake,DATA_fake,DATE_fake,DATAVALUE_fake,BEGHOUR_fake,ENDHOUR_fake,LAT_fake,LON_fake,FIRENAME_fake,NFDRSCODE_fake,MATBURNED_fake,HEATCONTENT_fake,day_str,missing_jday,day_dt]] # first make a new row; NOTE: define a row of list with [[x,y]]
            fake_row_df = pd.DataFrame( fake_row , columns = master_header_list_updated )  # define a DF from a list with columns.
            fake_frames_list = [ df_master_filtered_month , fake_row_df ]
            df_master_filtered_month = pd.concat( fake_frames_list , axis=0 )  # then concat(both DFs together along x-axis=0)

    # print number of fire days
    print('-----------------------------------------------------------------')
    print('-> we have (%s) fire days in LANDIS file for month (%s)...' %( len(fire_days_list) , modeling_month ) )
    print('-> Julian days with fire in LANDIS are:')
    for fireday in fire_days_list:
        print( '-> Jday (%s)' %fireday )
    print('-----------------------------------------------------------------')

    # --- sort month DF by date-time (DATE) column for favorable month for writing out to csv as object
    print('-> NOTE: fake DATAVALUE of (%s) was replaced at missing fire days!' %DATAVALUE_fake)
    print('-> NOTE: fake lat= %s and lon= %s was set for missing fire days!' %(LAT_fake , LON_fake))
    print('-> in-place sorting based on date-time...')
    df_master_filtered_month.sort_values('DATE_date_time' , inplace=True)  # sorts the whole DF based on a col and inplace

    # dealing with missing dates and fake data
#########################################################################################################


#########################################################################################################
    # set output file names

    # --- for PTDAY
    ptday_output_file_name = 'USFS_LANDIS_PTDAY_month_'+modeling_month+'_mode_'+mode+'_firescenario_'+str(LANDIS_yr)+'_fakevalue_'+DATAVALUE_fake+'.csv'  # must include file format at the end (.csv)

    ptday_header_list = ['FIPS','FIREID','LOCID','SCC','DATA','DATE','DATAVALUE','BEGHOUR','ENDHOUR']

    ptday_output_file_FullPath = os.path.join( output_dir , ptday_output_file_name )

    # --- for PTINV
    ptinv_output_file_name = 'USFS_LANDIS_PTINV_month_'+modeling_month+'_mode_'+mode+'_firescenario_'+str(LANDIS_yr)+'_fakevalue_'+DATAVALUE_fake+'.csv'  # must include file format at the end (.csv)

    ptinv_header_list = ['FIPS','FIREID','LOCID','SCC','FIRENAME','LAT','LON','NFDRSCODE','MATBURNED','HEATCONTENT']

    # --- copy a subset=PTINV from df_master
    ptinv_df = df_master_filtered_month[ ptinv_header_list ].copy()

    # --- remove duplicates in FIREID col
    ptinv_df.drop_duplicates( ['FIREID'] , keep = 'first' , inplace = True )

    ptinv_output_file_FullPath = os.path.join( output_dir , ptinv_output_file_name )

    # set output file names
#########################################################################################################


#########################################################################################################
    # write out output files

    if write_output == 'yes':

        df_master_filtered_month.to_csv( ptday_output_file_FullPath , columns = ptday_header_list , sep=',' , index=False , quoting=3 , quotechar='"' ) # last 2 fields for not adding three """ around each field.

        print( '-> output file is written as: %s' %ptday_output_file_name )

        ptinv_df.to_csv( ptinv_output_file_FullPath , columns = ptinv_header_list , sep=',' , index=False , quoting=3 , quotechar='"' ) # last 2 fields for not adding three """ around each field.

        print( '-> output file is written as: %s' %ptinv_output_file_name )

    else:

        print('-> NOTE: write-output key is set to "no", so NO output file will be written out!')

    # write out output files
#########################################################################################################

    print('-> *** SUCCESSFULL finish ***')

else:
    print('-> user input is not correct!')
