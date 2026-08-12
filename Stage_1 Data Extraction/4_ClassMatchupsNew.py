""" Final Code for Class: Matchups_New"""

import pandas as pd
import os
import re


folder_reflectance_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_Chlorophyll"
folder_reflectance_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_TSS"
folder_reflectance_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_DOC"
folder_reflectance_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_Pheophytin"

unique_locations_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Chlorophyll\\unique_locations_Param_Chlorophyll.csv"
insitu_sample_dates_utc_by_coordinate_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Chlorophyll\\UTC_Chlorophyll_Sampling_dates_under_coordinate.csv"
output_folder_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles1D_Chlorophyll"

unique_locations_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_TSS\\unique_locations_Param_TSS.csv"
insitu_sample_dates_utc_by_coordinate_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_TSS\\UTC_TSS_Sampling_dates_under_coordinate.csv"
output_folder_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles1D_TSS"

unique_locations_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_DOC\\unique_locations_Param_DOC.csv"
insitu_sample_dates_utc_by_coordinate_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_DOC\\UTC_DOC_Sampling_dates_under_coordinate.csv"
output_folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles1D_DOC"

unique_locations_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Pheophytin\\unique_locations_Param_Pheophytin.csv"
insitu_sample_dates_utc_by_coordinate_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Pheophytin\\UTC_Pheophytin_Sampling_dates_under_coordinate.csv"
output_folder_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles1D_Pheophytin"



# Load coordinate list
coords_Chlorophyll = pd.read_csv(unique_locations_Chlorophyll)
coords_TSS = pd.read_csv(unique_locations_TSS)
coords_DOC = pd.read_csv(unique_locations_DOC)
coord_Pheophytin = pd.read_csv(unique_locations_Pheophytin)

# Load in-situ sampling table (columns = "{lat}_{lon}")
insitu_all_Chlorophyll = pd.read_csv(insitu_sample_dates_utc_by_coordinate_Chlorophyll)
insitu_all_TSS = pd.read_csv(insitu_sample_dates_utc_by_coordinate_TSS)
insitu_all_DOC = pd.read_csv(insitu_sample_dates_utc_by_coordinate_DOC)
insitu_all_Pheophytin = pd.read_csv(insitu_sample_dates_utc_by_coordinate_Pheophytin)


ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']

class Matchups_New:
    
    def __init__(self, parameter):
        self.parameter = parameter

    def match_insitu_sentinel(self, insitu_df, sat_df, tolerance='1D'):
        insitu_df['sample_date'] = pd.to_datetime(insitu_df['sample_date'], errors='coerce')
        sat_df['datetime_utc'] = pd.to_datetime(sat_df['datetime_utc'], errors='coerce')
        
        insitu_df = insitu_df.sort_values('sample_date')
        sat_df = sat_df.sort_values('datetime_utc')
        
        matched = pd.merge_asof(
            insitu_df,
            sat_df,
            left_on='sample_date',
            right_on='datetime_utc',
            direction='nearest',
            tolerance=pd.Timedelta(tolerance)
        )
        
        matched = matched.dropna(subset=['datetime_utc'])
        matched['time_difference'] = matched['datetime_utc'] - matched['sample_date']
        matched['time_difference_hours'] = matched['time_difference'].dt.total_seconds() / 3600
        matched.drop(columns=['time_difference'], inplace=True)
        return matched

    def available_lat_lon(self):

        if self.parameter == 'Chlorophyll':
            folder_reflectance = folder_reflectance_Chlorophyll
        elif self.parameter == 'TSS':
            folder_reflectance = folder_reflectance_TSS
        elif self.parameter == 'DOC':
            folder_reflectance = folder_reflectance_DOC
        elif self.parameter == 'Pheophytin':
            folder_reflectance = folder_reflectance_Pheophytin

        available_surface_reflectances = [f for f in os.listdir(folder_reflectance) if f.endswith(".csv")]
        lat_lon_list = []
        for f in available_surface_reflectances:
            # Use regex to extract lat and lon
            match = re.match(r"([-\d.]+)_([-\d.]+)_SurfaceReflectance_utc\.csv", f)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                lat_lon_list.append((lat, lon))
        return lat_lon_list
    
    def operation(self):
        stations = self.available_lat_lon()
        idx = 1
        if self.parameter == 'Chlorophyll':
            folder_reflectance = folder_reflectance_Chlorophyll
        elif self.parameter == 'TSS':
            folder_reflectance = folder_reflectance_TSS
        elif self.parameter == 'DOC':
            folder_reflectance = folder_reflectance_DOC
        elif self.parameter == 'Pheophytin':
            folder_reflectance = folder_reflectance_Pheophytin

        if self.parameter == 'Chlorophyll':
            output_folder = output_folder_Chlorophyll
        elif self.parameter == 'TSS':
            output_folder = output_folder_TSS
        elif self.parameter == 'DOC':
            output_folder = output_folder_DOC
        elif self.parameter == 'Pheophytin':
            output_folder = output_folder_Pheophytin

        for lat, lon in stations:
            coord_key = f"{lat},{lon}"
            coords = f"{lat}_{lon}"
            
            if self.parameter == 'Chlorophyll':
                insitu_dates = insitu_all_Chlorophyll[coord_key].dropna().tolist()
            elif self.parameter == 'TSS':
                insitu_dates = insitu_all_TSS[coord_key].dropna().tolist()
            elif self.parameter == 'DOC':
                insitu_dates = insitu_all_DOC[coord_key].dropna().tolist()  # Update with correct variable
            elif self.parameter == 'Pheophytin':     
                insitu_dates = insitu_all_Pheophytin[coord_key].dropna().tolist()  # Update with correct variable

            insitu_df = pd.DataFrame({"sample_date": insitu_dates})
            surface_reflectance_path = os.path.join(folder_reflectance, f"{coords}_SurfaceReflectance_utc.csv")

            if not os.path.exists(surface_reflectance_path):
                print(f"⚠️ Surface Reflectance file missing for {coord_key} in {surface_reflectance_path}")
                continue

            sat_df = pd.read_csv(surface_reflectance_path)
            matched = self.match_insitu_sentinel(insitu_df, sat_df, tolerance='1D')
            output_path = os.path.join(output_folder, f"matchup_{coord_key}.csv")
            matched.to_csv(output_path, index=False)
            print(f"{idx} Saved matchup file for coordinate {coords} at {output_path}")
            idx = idx + 1

    def merge_and_check_length(self, folder):
        csv_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".csv")]
        df_list = [pd.read_csv(f) for f in csv_files]
        df_all = pd.concat(df_list, ignore_index=True)
        return len (df_all)
      

#For Chlorophyll
#params1 = ALL_PARAMETERS[0]
#Matchups_New(params1).operation()
#print(Matchups_New(params1).merge_and_check_length(output_folder_Chlorophyll))
#print(Matchups_New(params1).merge_and_check_length(folder_reflectance_Chlorophyll))

#For TSS
#params2 = ALL_PARAMETERS[1]
#Matchups_New(params2).operation()
#print(Matchups_New(params2).merge_and_check_length(output_folder_TSS))
#print(Matchups_New(params2).merge_and_check_length(folder_reflectance_TSS))

#For DOC
#params3 = ALL_PARAMETERS[2]
#Matchups_New(params3).operation()
#print(Matchups_New(params3).merge_and_check_length(output_folder_DOC))
#print(Matchups_New(params3).merge_and_check_length(folder_reflectance_DOC))

#For DOC
#params4 = ALL_PARAMETERS[3]
#Matchups_New(params4).operation()
#print(Matchups_New(params4).merge_and_check_length(output_folder_Pheophytin))
#print(Matchups_New(params4).merge_and_check_length(folder_reflectance_Pheophytin))

