#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 16:45:12 2024

@author: joshuabrooke
"""

import json
import pandas as pd
import datetime as dt


settlement_date = '2024-01-15'
date = dt.datetime.strptime(settlement_date, '%Y-%m-%d').date()
settlement_period = 1
url = f"https://data.elexon.co.uk/bmrs/api/v1/balancing/bid-offer/all?settlementDate={settlement_date}&settlementPeriod={settlement_period}&format=csv"

boas_df = pd.read_csv('data/all-boas-april2023-march2024.csv')

options_df = pd.DataFrame()
for settlement_period in  range(1, 51):
    df_sp = pd.read_csv(url)
    options_df =  pd.concat([options_df, df_sp])
    

with open('data/response_1733913471428.json', 'r') as f:
    bmu_data = json.load(f)

carbon_intensity_df = pd.read_csv('data/carbon_intensity.csv')

# Rest of the code remains the same
bmu_to_fuel_mapping = {}
for unit in bmu_data:
    national_grid_bmu = unit['nationalGridBmUnit']
    elexon_bmu = unit['elexonBmUnit']
    fuel_type = unit['fuelType']
    
    if fuel_type:
        # Map both National Grid and Elexon BMU codes
        bmu_to_fuel_mapping[national_grid_bmu] = fuel_type
        bmu_to_fuel_mapping[elexon_bmu] = fuel_type
        
fuel_type_mapping = {
    'WIND': 'Wind',
    'CCGT': 'Gas (Combined Cycle)',
    'OCGT': 'Gas (Open Cycle)',
    'COAL': 'Coal',
    'NUCLEAR': 'Nuclear',
    'PS': 'Pumped Storage',
    'BIOMASS': 'Biomass',
    'SOLAR': 'Solar',
    'HYDRO': 'Hydro',
    'OIL': 'Oil'
}

boas_df['fuel_type'] = boas_df['ACCEPTED BMU'].map(bmu_to_fuel_mapping)
boas_df['fuel_type'] = boas_df['fuel_type'].map(fuel_type_mapping).fillna('Other')

result_df = boas_df.merge(carbon_intensity_df, on='fuel_type', how='left')
result_df['carbon_emissions_g'] = result_df['NET VOL (MWh)'].fillna(0) * result_df['carbon_intensity'] * 1000
result_df['carbon_emissions_tonnes'] = result_df['carbon_emissions_g'] / 1000000
result_df = result_df.rename(columns=dict(zip(result_df.columns.to_list(), [x.lower().replace(' ', '_').split('_(')[0] for x in result_df.columns.to_list()])))


local_timezone = 'Europe/London'
result_df['start_time'] = pd.to_datetime(result_df['accept_time']) + pd.to_timedelta(result_df['time_to_target'], unit='m')
result_df['end_time'] = pd.to_datetime(result_df['start_time']) + pd.to_timedelta(result_df['target_duration'], unit='m')
result_df['start_time'] = result_df['start_time'].dt.tz_localize(local_timezone, ambiguous=True)
result_df['end_time'] = result_df['end_time'].dt.tz_localize(local_timezone, ambiguous=True)
result_df['start_time_gmt'] = result_df['start_time'].dt.tz_convert('UTC')
result_df['end_time_gmt'] = result_df['end_time'].dt.tz_convert('UTC')


options_df['fuel_type'] = options_df['NationalGridBmUnit'].map(bmu_to_fuel_mapping)
options_df['fuel_type'] = options_df['fuel_type'].map(fuel_type_mapping)

options_df['start_time'] = pd.to_datetime(options_df['TimeFrom'])
options_df['end_time'] = pd.to_datetime(options_df['TimeTo'])
options_df['start_time_gmt'] = options_df['start_time'].dt.tz_convert('UTC')
options_df['end_time_gmt'] = options_df['end_time'].dt.tz_convert('UTC')


options_df = options_df.merge(carbon_intensity_df, on='fuel_type', how='left')

result_df['start_date'] = result_df['start_time'].dt.date
result_df = result_df[result_df['start_date'] == date] 
merged_df = pd.merge(options_df, result_df, left_on=['NationalGridBmUnit', 'SettlementPeriod'],
                     right_on=['accepted_bmu', 'main_sp'], how='inner')

merged_df = merged_df[(merged_df['net_vol'] > 0) & (merged_df['LevelTo']>0) | (merged_df['net_vol'] < 0) & (merged_df['LevelTo'] < 0)]

# Add a column 'match_flag' which will contain 1 if both conditions match, otherwise 0
merged_df['accepted'] = 1
options_df = pd.merge(options_df, merged_df[['SettlementDate', 'SettlementPeriod', 'accepted', 'net_vol', 'NationalGridBmUnit']], 
                       on=['NationalGridBmUnit', 'SettlementPeriod'], how='left')
options_df['accepted'].fillna(0, inplace=True)

# Convert match_flag to integer
options_df['accepted'] = options_df['accepted'].astype(int)

# df = df.rename(columns=dict(zip(result_df.columns.to_list(), [x.lower().replace(' ', '_').split('_(')[0] for x in result_df.columns.to_list()])))










