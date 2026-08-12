#Code for extracting ERA5 GRIB Files as per Sampling Dates, not the matched date
#Code "variable": ['2m_temperature', '2m_dewpoint_temperature', '10m_v_component_of_neutral_wind', '10m_u_component_of_neutral_wind']

import os
import pandas as pd
import cdsapi 
import xarray as xr

os.environ['CDSAPI_RC'] = r"D:\\Shukra_sir\\CDSAPI_ERA5\\.cdsapirc.txt"

output_folder_Chlorophyll = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_Chlorophyll_12H" 
output_folder_TSS = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_TSS_12H"
output_folder_DOC = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_DOC_12H"
output_folder_Pheophytin = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_Pheophytin_12H"

matchup_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"
matchup_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"
matchup_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"
matchup_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"

ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']

def get_data(folder, param):
    file_name = f"Combined12H_Revised_{param}.csv"
    file_name_path = os.path.join(folder, file_name)
    combined_df = pd.read_csv(file_name_path)

    lat_min, lat_max = combined_df['latitude'].min(), combined_df['latitude'].max()
    lon_min, lon_max = combined_df['longitude'].min(), combined_df['longitude'].max()
    year_min, year_max = combined_df['sampling_year'].min(), combined_df['sampling_year'].max()

    unique_years = combined_df['sampling_year'].unique().tolist()
    unique_years.sort()
    unique_months = combined_df['sampling_month'].unique().tolist()
    unique_months.sort()
    unique_days = combined_df['sampling_day'].unique().tolist()
    unique_days.sort()
    unique_hours = combined_df['sampling_hour'].unique().tolist()
    unique_hours.sort()

    # Add buffer (1 degrees)
    area = [lat_max + 1, lon_min - 1, lat_min - 1, lon_max + 1]  # N, W, S, E
    return area, year_min, year_max, unique_years, unique_months, unique_days, unique_hours, param

"""
folder = matchup_TSS
PARAM = ALL_PARAMETERS[1]

area = get_data(folder, PARAM)[0]
year_start = get_data(folder, PARAM)[1]
year_end = get_data(folder, PARAM)[2]
unique_years = get_data(folder, PARAM)[3]
unique_months = get_data(folder, PARAM)[4]
unique_days = get_data(folder, PARAM)[5]
unique_hours = get_data(folder, PARAM)[6]

print (area)
print (year_start)
print (year_end)
print (unique_years)
print (unique_months)
print(unique_days) 
print(unique_hours)
print(get_data(folder, PARAM)[7])
"""

def get_GRIB(folder, parameter):

    param = parameter
    area = get_data(folder, param)[0]
    #unique_years = get_data(folder, param)[3]
    #unique_months = get_data(folder, param)[4]
    #unique_days = get_data(folder, param)[5]
    unique_hours = get_data(folder, param)[6]
    year = 2024 #change year manually from 2017 to 2024. Loop is avoided to prevent server overload (specifically, to avoid RuntimeError: Mars runtime error)
    
    if param == "Chlorophyll":
        output_folder = output_folder_Chlorophyll
    elif param == "TSS":
        output_folder = output_folder_TSS
    elif param == "DOC":
        output_folder = output_folder_DOC
    elif param == "Pheophytin":
        output_folder = output_folder_Pheophytin
    
    c = cdsapi.Client()

    print(f"Downloading ERA5 data_{year} for {param}...")
    grib_file = os.path.join(output_folder, f'Revised_ERA5GRIB_{year}_{param}.grib')
        
    c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": ['2m_temperature', '2m_dewpoint_temperature', '10m_v_component_of_neutral_wind', '10m_u_component_of_neutral_wind'],
                "year": f"{year}",
                "month": [f"{m:02d}" for m in range(1,13)],
                "day": [f"{d:02d}" for d in range(1,32)],
                "time": [f"{h:02d}:00" for h in unique_hours],   # ONLY unique hours needed
                "format": "grib",
                "area": area
            },
            grib_file)
        
    print(f"GRIB saved for {year} and for {param} as: {grib_file}")
    

ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']

#PARAM = ALL_PARAMETERS[0]
#get_GRIB(matchup_Chlorophyll, PARAM)

#PARAM = ALL_PARAMETERS[1]
#get_GRIB(matchup_TSS, PARAM)

#PARAM = ALL_PARAMETERS[2]
#get_GRIB(matchup_DOC, PARAM)
