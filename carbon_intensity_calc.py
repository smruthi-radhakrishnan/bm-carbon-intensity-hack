#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 13:48:41 2024

@author: joshuabrooke
"""

import pandas as pd
import json
import numpy as np

def main():
    # 1. Read all the data files
    boas_df = pd.read_csv('data/all-boas-april2023-march2024.csv')
    carbon_intensity_df = pd.read_csv('data/carbon_intensity.csv')
    alternative_boa_df = pd.read_csv('data/potential-alternatives-actions-april2023-march2024.csv')
    
    # Load BMU mapping data
    with open('data/response_1733913471428.json', 'r') as f:
        bmu_data = json.load(f)
    
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
    
    # 3. Add fuel type to BOAs dataframe
    boas_df['fuel_type'] = boas_df['ACCEPTED BMU'].map(bmu_to_fuel_mapping)
    alternative_boa_df['fuel_type'] = alternative_boa_df['ALTERNATIVE BMU'].map(bmu_to_fuel_mapping)
    
    # 4. Standardize fuel type names to match carbon intensity data
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
    boas_df['fuel_type'] = boas_df['ACCEPTED BMU'].map(fuel_type_mapping)
    alternative_boa_df['fuel_type'] = alternative_boa_df['ALTERNATIVE BMU'].map(fuel_type_mapping)
    
    merged_df = pd.merge(boas_df, alternative_boa_df, on=['BOA REF', 'ACCEPTED BMU'], how='inner')
    
    # Calculate the new alternative price
    merged_df['NET VOL (MWh)'] = merged_df['NET VOL (MWh)'] + merged_df['APPROX ALTERNATIVE VOL (MWh)']
    
    merged_df['ACCEPTED BMU'] = merged_df['ALTERNATIVE BMU_y']
    merged_df['fuel_type'] = merged_df['fuel_type_y']
    merged_df['ALTERNATIVE BMU'] = np.nan
    
    merged_df = merged_df[boas_df.columns.to_list()]
    
    merged_df['accepted'] = 0
    boas_df['accepted'] = 1
    
    result_df = pd.concat([merged_df, boas_df])
    
    # 5. Merge with carbon intensity data and calculate emissions
    result_df = result_df.merge(carbon_intensity_df, on='fuel_type', how='left')
    result_df['carbon_emissions_g'] = result_df['NET VOL (MWh)'].fillna(0) * result_df['carbon_intensity'] * 1000
    result_df['carbon_emissions_tonnes'] = result_df['carbon_emissions_g'] / 1000000
    
    result_df = result_df.rename(columns=dict(zip(result_df.columns.to_list(), [x.lower().replace(' ', '_').split('_(')[0] for x in result_df.columns.to_list()])))
    # 6. Print analysis
    print("\nTotal carbon emissions (tonnes):", f"{result_df['carbon_emissions_tonnes'].sum():,.2f}")
    print("\nEmissions by fuel type:")
    print(result_df.groupby('fuel_type')['carbon_emissions_tonnes'].sum().sort_values(ascending=False))
    
    # 7. Check for unmapped BMUs
    unmapped_bmus = boas_df[boas_df['fuel_type'] == 'Other']['ACCEPTED BMU'].unique()
    print(f"\nNumber of unmapped BMUs: {len(unmapped_bmus)}")
    print("\nSample of unmapped BMUs (first 10):")
    print(unmapped_bmus[:10])
    
    all_boas = result_df
    all_boas['start_time'] = pd.to_datetime(all_boas['accept_time']) + pd.to_timedelta(all_boas['time_to_target'], unit='m')
    all_boas['end_time'] = pd.to_datetime(all_boas['start_time']) + pd.to_timedelta(all_boas['target_duration'], unit='m')

    local_timezone = 'Europe/London'
    all_boas['start_time'] = all_boas['start_time'].dt.tz_localize(local_timezone, ambiguous=True)
    all_boas['end_time'] = all_boas['end_time'].dt.tz_localize(local_timezone, ambiguous=True)

    all_boas['start_time_gmt'] = all_boas['start_time'].dt.tz_convert('UTC')
    all_boas['end_time_gmt'] = all_boas['end_time'].dt.tz_convert('UTC')

    # Optional: Save results to CSV
    all_boas.to_parquet('data/carbon_emissions_results.parquet', index=False)
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
