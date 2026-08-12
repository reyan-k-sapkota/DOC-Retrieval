import os
import pandas as pd
import cdsapi 
import xarray as xr

os.environ['CDSAPI_RC'] = r"D:\\Shukra_sir\\CDSAPI_ERA5\\.cdsapirc.txt"

output_folder_Chlorophyll = r"D:\\Shukra_sir\\ERA5 MeteoData\\Chlorophyll_12H"  
output_folder_DOC = r"D:\\Shukra_sir\\ERA5 MeteoData\\DOC_12H"
output_folder_TSS = r"D:\\Shukra_sir\\ERA5 MeteoData\\TSS_12H"

matchup_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles12H_Chlorophyll"
matchup_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Matchfiles12H_DOC"
matchup_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Matchfiles12H_Pheophytin"
matchup_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles12H_TSS"

ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
folder = matchup_Chlorophyll

def get_data(folder):
    param = ALL_PARAMETERS[0]
    file_name = f"NewCombinedFiles12H_{param}.csv"
    file_name_path = os.path.join(folder, file_name)
    combined_df = pd.read_csv(file_name_path)

    lat_min, lat_max = combined_df['latitude'].min(), combined_df['latitude'].max()
    lon_min, lon_max = combined_df['longitude'].min(), combined_df['longitude'].max()
    year_min, year_max = combined_df['year'].min(), combined_df['year'].max()

    unique_years = combined_df['year'].unique().tolist()
    unique_years.sort()
    unique_months = combined_df['month'].unique().tolist()
    unique_months.sort()
    unique_days = combined_df['day'].unique().tolist()
    unique_days.sort()
    unique_hours = combined_df['hour'].unique().tolist()
    unique_hours.sort()

    # Add buffer (1 degrees)
    area = [lat_max + 1, lon_min - 1, lat_min - 1, lon_max + 1]  # N, W, S, E
    return area, year_min, year_max, unique_years, unique_months, unique_days, unique_hours, param


area = get_data(folder)[0]
year_start = get_data(folder)[1]
year_end = get_data(folder)[2]
#unique_years = [2023]
unique_years = get_data(folder)[3]
unique_months = get_data(folder)[4]
unique_days = get_data(folder)[5]
unique_hours = get_data(folder)[6]

print (area)
print (year_start)
print (year_end)
print (unique_years)
print (unique_months)
print(unique_days) 
print(unique_hours)
print(get_data(folder)[7])

def get_GRIB(folder):

    param = ALL_PARAMETERS[3]
    area = get_data(folder)[0]
    unique_years = get_data(folder)[3]
    unique_months = get_data(folder)[4]
    unique_days = get_data(folder)[5]
    unique_hours = get_data(folder)[6]
    year = 2024 #change year manually from 2017 to 2024. Loop is avoided to prevent server overload (specifically, to avoid RuntimeError: Mars runtime error)
    output_folder = output_folder_DOC

    c = cdsapi.Client()

    print(f"Downloading ERA5 data_{year} for {param}...")
    grib_file = os.path.join(output_folder, f'ERA5GRIB_{year}_{param}.grib')
        
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
    


#get_GRIB(matchup_Chlorophyll)
#get_GRIB(matchup_TSS)
#get_GRIB(matchup_DOC)
#get_GRIB(matchup_Pheophytin)