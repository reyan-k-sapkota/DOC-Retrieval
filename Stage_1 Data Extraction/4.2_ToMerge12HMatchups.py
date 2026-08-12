""" Final Code for 4.2_ClassMeteo Merging Matchup Files. """

#Code for Properly Merge all the matchups for every coordinates into a single file. Then, create seperate columns for sampling_year, sampling_month, sampling_day, sampling_hour, sampling_minute, sampling_second for ERA5 GRIB File Download

import pandas as pd
import os
import re

matchup_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles12H_Chlorophyll"
matchup_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Matchfiles12H_DOC"
matchup_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Matchfiles12H_Pheophytin"
matchup_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles12H_TSS"

output_folder  = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"

class Meteo:
    def __init__(self, parameter):
        self.parameter = parameter
    
    def get_data(self, folder, lat, lon):
        file_name = f"matchup_{lat},{lon}.csv"
        file_name_path = os.path.join(folder, file_name) 
        print(f"Extracting data for {lat}, {lon} with Filename: {file_name_path}")
    
    def get_meteo (self):
        if self.parameter == 'Chlorophyll':
            folder = matchup_Chlorophyll
        elif self.parameter == 'TSS':
            folder = matchup_TSS
        elif self.parameter == 'DOC':
            folder = matchup_DOC
        elif self.parameter == 'Pheophytin':
            folder = matchup_Pheophytin
        
        csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        lat_lon_list = []

        for f in csv_files:
            # Use regex to extract lat and lon
            match = re.match(r"matchup_([-\d.]+),([-\d.]+).csv", f)
            #match = re.match(r"([-\d.]+)_([-\d.]+)_SurfaceReflectance_utc\.csv", f)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                lat_lon_list.append((lat, lon))
            
            self.get_data(folder, lat, lon)
        
        print(f"Completed for all files inside {folder}")
        return len(lat_lon_list)
    
    def merge_all (self):
        if self.parameter == 'Chlorophyll':
            folder = matchup_Chlorophyll
        elif self.parameter == 'TSS':
            folder = matchup_TSS
        elif self.parameter == 'DOC':
            folder = matchup_DOC
        elif self.parameter == 'Pheophytin':
            folder = matchup_Pheophytin
        
        param = self.parameter
        save_folder = os.path.join(output_folder, f"Combined12H_Revised_{param}.csv")

        csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        lat_lon_list = []
        all_dataframes = []

        for f in csv_files:
            # Use regex to extract lat and lon
            match = re.match(r"matchup_([-\d.]+),([-\d.]+).csv", f)
            #match = re.match(r"([-\d.]+)_([-\d.]+)_SurfaceReflectance_utc\.csv", f)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                lat_lon_list.append((lat, lon))
            
            df = pd.read_csv(os.path.join(folder, f))
            df['latitude'] = lat
            df['longitude'] = lon
            all_dataframes.append(df)
        
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        combined_df['sample_date'] = pd.to_datetime(combined_df['sample_date'])  # Replace with your column name

        combined_df['sampling_year'] = combined_df['sample_date'].dt.year
        combined_df['sampling_month'] = combined_df['sample_date'].dt.month
        combined_df['sampling_day'] = combined_df['sample_date'].dt.day
        combined_df['sampling_hour'] = combined_df['sample_date'].dt.hour
        combined_df['sampling_minute'] = combined_df['sample_date'].dt.minute
        combined_df['sampling_second'] = combined_df['sample_date'].dt.second

        combined_df.to_csv(save_folder, index=False)
        print(f"Combined CSV saved at: {save_folder}")
        
        
ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']

#param = ALL_PARAMETERS[0]
#Meteo(param).merge_all()

#param = ALL_PARAMETERS[1]
#Meteo(param).merge_all()

#param = ALL_PARAMETERS[2]
#Meteo(param).merge_all()

#param = ALL_PARAMETERS[3]
#Meteo(param).merge_all()
