"Final Code for Class: Intermediate"

import pandas as pd
from zoneinfo import ZoneInfo  

all_after_2015_chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\Parameters\\ChlorophyllAfter2015.csv"
all_after_2015_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\Parameters\\TSSAfter2015.csv"
all_after_2015_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\Parameters\\DOCAfter2015.csv"
all_after_2015_pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\Parameters\\PheophytinAfter2015.csv"

#all_after_2015_chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Waterbodies\\ChlorophyllAfter2015\\AllChlorophyllAfter2015.csv"
#all_after_2015_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Waterbodies\\TSSAfter2015\\AllTSSAfter2015.csv"
#all_after_2015_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Waterbodies\\Dissolved Organic CarbonAfter2015\\AllDOCAfter2015.csv"
#all_after_2015_pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Waterbodies\\PheophytinAfter2015\\AllPheophytinafter2015.csv"

output_folder_chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Chlorophyll"
outpur_folder_tss = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_TSS"
output_folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_DissolvedOrganicCarbon"
output_folder_pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Pheophytin"

#output_folder_chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\Unique and UTC_Chlorophyll"
#output_folder_tss = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\Unique and UTC_TSS"
#output_folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\Unique and UTC_DissolvedOrganicCarbon"
#output_folder_pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\Unique and UTC_Pheophytin"

class Intermediate_New:
    def __init__(self, all_after_2015, output_folder):
        self.all_after_2015 = all_after_2015
        self.output_folder = output_folder
    
    def unique_locations (self, parameter):
        lat_col = 'latitude'
        lon_col = 'longitude'
        df_allafter2015 = pd.read_csv(f'{self.all_after_2015}')
        df_coords = df_allafter2015[[lat_col, lon_col]].dropna()
        
        all_locations = list(df_coords.itertuples(index=False, name=None))
        
        unique_locations = list(dict.fromkeys(all_locations))
        
        print(f"Total locations: {len(all_locations)}")
        print(f"Unique locations: {len(unique_locations)}")
        
        df_unique_locations = pd.DataFrame(unique_locations, columns=[lat_col, lon_col])
        output_path = f"{self.output_folder}\\unique_locations_Param_{parameter}.csv"
        df_unique_locations.to_csv(output_path, index=False)
        
        print(f"✅ Unique locations saved to: {output_path}")
    
    def allafter2015_UTC (self, parameter):
        df = pd.read_csv (f"{self.all_after_2015}")
        df['sample_date'] = pd.to_datetime(df['sample_date'], format='%Y-%m-%d %H:%M:%S')
        
        # Localize to Pacific Time
        df['sample_date'] = df['sample_date'].dt.tz_localize(ZoneInfo('America/Los_Angeles'))
        
        # Convert to UTC
        df['sample_date_utc'] = df['sample_date'].dt.tz_convert('UTC')
        
        # Convert to ISO 8601 string format
        df['sample_date_utc'] = df['sample_date_utc'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        output_path = f"{self.output_folder}\\AllAfter2015_{parameter}_to_UTC.csv"
        
        df.to_csv(output_path, index=False)
        print(f"Done: Saved to {output_path}")

    def sampling_dates_PST_under_coordinate (self, parameter):
        path_unique = f"{self.output_folder}\\unique_locations_Param_{parameter}.csv"
        path_allafter2015_PST = self.all_after_2015
        df_coords = pd.read_csv(path_unique)     
        df_all = pd.read_csv(path_allafter2015_PST)          

        # Merge only matching coordinates
        merged = df_all.merge(df_coords, on=['latitude', 'longitude'], how='inner')
        grouped = merged.groupby(['latitude', 'longitude'])['sample_date'].apply(list).reset_index()
        grouped['coord'] = grouped['latitude'].astype(str) + ',' + grouped['longitude'].astype(str)
        
        max_len = grouped['sample_date'].apply(len).max()
        data = {coord: dates + [None]*(max_len - len(dates)) for coord, dates in zip(grouped['coord'], grouped['sample_date'])}
        df_out = pd.DataFrame(data)
        
        
        
        df_out.to_csv(f"{self.output_folder}\\PST_{parameter}_Sampling_dates_under_coordinate.csv", index=False)
        print(f"Done: Saved to {self.output_folder}\\PST_{parameter}_Sampling_dates_under_coordinate.csv")


    def sampling_dates_UTC_under_coordinate (self, parameter):
        path_unique = f"{self.output_folder}\\unique_locations_Param_{parameter}.csv"
        path_allafter2015_UTC = f"{self.output_folder}\\AllAfter2015_{parameter}_to_UTC.csv"
        df_coords = pd.read_csv(path_unique)     # unique coordinates
        df_all = pd.read_csv(path_allafter2015_UTC)           # all data with sample_date

        
        merged = df_all.merge(df_coords, on=['latitude', 'longitude'], how='inner')
        grouped = merged.groupby(['latitude', 'longitude'])['sample_date_utc'].apply(list).reset_index()
        grouped['coord'] = grouped['latitude'].astype(str) + ',' + grouped['longitude'].astype(str)

        max_len = grouped['sample_date_utc'].apply(len).max()
        data = {coord: dates + [None]*(max_len - len(dates)) for coord, dates in zip(grouped['coord'], grouped['sample_date_utc'])}
        df_out = pd.DataFrame(data)
        
      
        
        df_out.to_csv(f"{self.output_folder}\\UTC_{parameter}_Sampling_dates_under_coordinate.csv", index=False)
        print(f"Done: Saved to {self.output_folder}\\UTC_{parameter}_Sampling_dates_under_coordinate.csv")


        
""" 
INSTRUCTIONS
a. First, run unique_locations (self, parameter)
b. Second, run allafter2015_UTC (self, parameter)
c. Third, run sampling_dates_PST_under_coordinate (self, parameter)
d. Fourth, run sampling_dates_UTC_under_coordinate (self, parameter)
"""

#For Chlorophyll
Intermediate_New(all_after_2015_chlorophyll, output_folder_chlorophyll).unique_locations("Chlorophyll")
Intermediate_New(all_after_2015_chlorophyll, output_folder_chlorophyll).allafter2015_UTC('Chlorophyll')
Intermediate_New(all_after_2015_chlorophyll, output_folder_chlorophyll).sampling_dates_PST_under_coordinate('Chlorophyll')
Intermediate_New(all_after_2015_chlorophyll, output_folder_chlorophyll).sampling_dates_UTC_under_coordinate('Chlorophyll')

#For TSS
#Intermediate(all_after_2015_TSS, output_folder_tss).unique_locations("TSS")
#Intermediate (all_after_2015_TSS, output_folder_tss).allafter2015_UTC('TSS')
#Intermediate (all_after_2015_TSS, output_folder_tss).sampling_dates_PST_under_coordinate('TSS')
#Intermediate (all_after_2015_TSS, output_folder_tss).sampling_dates_UTC_under_coordinate('TSS')

#For DissolvedOrganicCarbon 
#Intermediate(all_after_2015_DOC, output_folder_DOC).unique_locations("DOC")
#Intermediate (all_after_2015_DOC, output_folder_DOC).allafter2015_UTC('DOC')
#Intermediate (all_after_2015_DOC, output_folder_DOC).sampling_dates_PST_under_coordinate('DOC')
#Intermediate (all_after_2015_DOC, output_folder_DOC).sampling_dates_UTC_under_coordinate('DOC')

#For Pheophytin
#Intermediate(all_after_2015_pheophytin, output_folder_pheophytin).unique_locations("Pheophytin")
#Intermediate (all_after_2015_pheophytin, output_folder_pheophytin).allafter2015_UTC('Pheophytin')
#Intermediate (all_after_2015_pheophytin, output_folder_pheophytin).sampling_dates_PST_under_coordinate('Pheophytin')
#Intermediate (all_after_2015_pheophytin, output_folder_pheophytin).sampling_dates_UTC_under_coordinate('Pheophytin')


        
    
    