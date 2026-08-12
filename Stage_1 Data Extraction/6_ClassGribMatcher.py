import pandas as pd
import xarray as xr
import os
import scipy

GRIB_folder_Chlorophyll = r"D:\\Shukra_sir\\ERA5 MeteoData\\Chlorophyll_12H_Final"  
GRIB_folder_DOC = r"D:\\Shukra_sir\\ERA5 MeteoData\\DOC_12H_Final"
GRIB_folder_TSS = r"D:\\Shukra_sir\\ERA5 MeteoData\\TSS_12H_Final"
GRIB_folder_Pheophytin = r"D:\\Shukra_sir\\ERA5 MeteoData\\TSS_12H_Final"

matchup_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles12H_Chlorophyll"
matchup_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Matchfiles12H_DOC"
matchup_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Matchfiles12H_Pheophytin"
matchup_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\MatchFiles12H_TSS"

output_folder_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Meteorology_Chlorophyll"
output_folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Meteorology_DOC"
output_folder_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Meteorology_TSS"
output_folder_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\Meteorology_Pheophytin"

ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
VARIABLES = ['Temperature', 'DewPoint Temperature', 'V10', 'U10']
VARIABLES_CODE = ['t2m', 'd2m', 'v10n', 'u10n']

class GRIB_Matcher:
    def __init__(self, parameter):
        self.parameter = parameter
    
    def get_value_from_grib(self, ds, lat, lon, timestamp):
        
        point1 = ds["t2m"].interp(
        latitude=lat,
        longitude=lon,
        method="cubic")
        
        point2 = ds["d2m"].interp(
        latitude=lat,
        longitude=lon,
        method="cubic")
        
        point3 = ds["v10n"].interp(
        latitude=lat,
        longitude=lon,
        method="cubic")
        
        point4 = ds["u10n"].interp(
        latitude=lat,
        longitude=lon,
        method="cubic")

        temperature = float(point1.interp(
            time=timestamp,
            method = "cubic"
        ).values)
        
        dewpoint = float(point2.interp(
            time=timestamp,
            method = "cubic"
        ).values)
        
        v10 = float(point3.interp(
            time=timestamp,
            method = "cubic"
        ).values)
        
        u10 = float(point4.interp(
            time=timestamp,
            method = "cubic"
        ).values)

        return temperature, dewpoint, v10, u10


    def match_GRIB(self):
        
        PARAM = self.parameter
        print(f"Matching ERA5 GRIB data for parameter: {PARAM}...")

        if PARAM == 'Chlorophyll':
            combined_file_name = f"NewCombinedFiles12H_Chlorophyll.csv"
            combined_file_name_path = os.path.join(matchup_Chlorophyll, combined_file_name)
            grib_folder = GRIB_folder_Chlorophyll
            output_folder = output_folder_Chlorophyll

        elif PARAM == 'TSS':
            combined_file_name = f"NewCombinedFiles12H_TSS.csv"
            combined_file_name_path = os.path.join(matchup_TSS, combined_file_name)
            grib_folder = GRIB_folder_TSS
            output_folder = output_folder_TSS

        elif PARAM == 'DOC':    
            combined_file_name = f"NewCombinedFiles12H_DOC.csv"
            combined_file_name_path = os.path.join(matchup_DOC, combined_file_name)
            grib_folder = GRIB_folder_DOC
            output_folder = output_folder_DOC

        elif PARAM == 'Pheophytin':
            combined_file_name = f"NewCombinedFiles12H_Pheophytin.csv"
            combined_file_name_path = os.path.join(matchup_Pheophytin, combined_file_name)
            grib_folder = GRIB_folder_Pheophytin
            output_folder = output_folder_Pheophytin
        
        df = pd.read_csv(combined_file_name_path)
        
        Temperature = []
        Dewpoint = []
        v10_list = []
        u10_list = []
        count = 0
        for __, row in df.iterrows():
            lat = row['latitude']
            lon = row['longitude']
            year = row['year']
            month = row['month']
            day = row['day']
            hour = row['hour']
            minute = row['minute']
            second = row['second']

            time = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
            timestamp = pd.Timestamp(time)

            grib_file_path = os.path.join(grib_folder, f'ERA5GRIB_{year}_{PARAM}.grib')
            ds = xr.open_dataset(grib_file_path)

            temperature, dewpoint, v10_val, u10_val = self.get_value_from_grib(ds, lat, lon, timestamp)
            ds.close()


            #temperature = self.get_value_from_grib(ds, lat, lon, timestamp)[0]
            #dewpoint = self.get_value_from_grib(ds, lat, lon, timestamp)[1]
            #v10_val = self.get_value_from_grib(ds, lat, lon, timestamp)[2]
            #u10_val = self.get_value_from_grib(ds, lat, lon, timestamp)[3]

            Temperature.append(temperature)
            Dewpoint.append(dewpoint)
            v10_list.append(v10_val)
            u10_list.append(u10_val)
            count +=1
            print("Processed for row:", count)

        
        df["Temperature"] = Temperature
        df["DewPoint"] = Dewpoint
        df["v10n"] = v10_list
        df["u10n"] = u10_list

        output_file_name = f"ERA5_Sentinel_{PARAM}_12H.csv"
        output_file_name_path = os.path.join(output_folder, output_file_name)
        df.to_csv(output_file_name_path, index=False)
        
        print(f"Matched data saved as: {output_file_name_path}")


#For Chlorophyll
#ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#param = ALL_PARAMETERS[0]
#GRIB_Matcher(param).match_GRIB()

#FOR TSS
#ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#param = ALL_PARAMETERS[1]
#GRIB_Matcher(param).match_GRIB()

#FOR DOC
#ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#param = ALL_PARAMETERS[2]
#GRIB_Matcher(param).match_GRIB()


