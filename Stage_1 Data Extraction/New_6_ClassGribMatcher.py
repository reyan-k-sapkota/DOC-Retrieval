""" Final Code for 6_ClassGribMatcher. To extracting data for Air temp, Dew Point temp, wind speed (northward component of neutral wind only) from NEW GRIBS and storing as new compiled final csv """

#Using Linear Interpolation

import pandas as pd
import xarray as xr
import os
import scipy

NEW_GRIB_folder_Chlorophyll = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_Chlorophyll_12H"  
NEW_GRIB_folder_DOC = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_DOC_12H"
NEW_GRIB_folder_TSS = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_TSS_12H"
NEW_GRIB_folder_Pheophytin = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_Pheophytin_12H"

matchup_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"
matchup_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"
matchup_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"
matchup_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithSurfaceReflectanceCompiled"

output_for_meteo = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithAllMeteorology"

VARIABLES = ['Temperature', 'DewPoint Temperature', 'V10', 'U10']
VARIABLES_CODE = ['t2m', 'd2m', 'v10n', 'u10n']

class GRIB_Matcher:
    def __init__(self, parameter):
        self.parameter = parameter
    
    def get_value_from_grib(self, ds, lat, lon, timestamp):
        
        point1 = ds["t2m"].interp(
        latitude=lat,
        longitude=lon,
        method="linear")  #linear is recommended by ERA5
        
        point2 = ds["d2m"].interp(
        latitude=lat,
        longitude=lon,
        method="linear")
        
        point3 = ds["v10n"].interp(
        latitude=lat,
        longitude=lon,
        method="linear")
        
        #point4 = ds["u10n"].interp(
        #latitude=lat,
        #longitude=lon,
        #method="linear")

        temperature = float(point1.interp(
            time=timestamp,
            method = "linear"
        ).values)
        
        dewpoint = float(point2.interp(
            time=timestamp,
            method = "linear"
        ).values)
        
        v10 = float(point3.interp(
            time=timestamp,
            method = "linear"
        ).values)
        
        #u10 = float(point4.interp(
        #    time=timestamp,
        #    method = "cubic"
        #).values)

        return temperature, dewpoint, v10


    def match_GRIB(self):
        
        PARAM = self.parameter
        print(f"Matching ERA5 GRIB data for parameter: {PARAM}...")

        if PARAM == 'Chlorophyll':
            combined_file_name = f"Combined12H_Revised_Chlorophyll.csv"
            combined_file_name_path = os.path.join(matchup_Chlorophyll, combined_file_name)
            grib_folder = NEW_GRIB_folder_Chlorophyll
            output_folder = output_for_meteo

        elif PARAM == 'TSS':
            combined_file_name = f"Combined12H_Revised_TSS.csv"
            combined_file_name_path = os.path.join(matchup_TSS, combined_file_name)
            grib_folder = NEW_GRIB_folder_TSS
            output_folder = output_for_meteo

        elif PARAM == 'DOC':    
            combined_file_name = f"Combined12H_Revised_DOC.csv"
            combined_file_name_path = os.path.join(matchup_DOC, combined_file_name)
            grib_folder = NEW_GRIB_folder_DOC
            output_folder = output_for_meteo

        elif PARAM == 'Pheophytin':
            combined_file_name = f"Combined12H_Revised_Pheophytin.csv"
            combined_file_name_path = os.path.join(matchup_Pheophytin, combined_file_name)
            grib_folder = NEW_GRIB_folder_Pheophytin
            output_folder = output_for_meteo
        
        df = pd.read_csv(combined_file_name_path)
        
        count = 0

        for year, df_year in df.groupby("sampling_year"):

            print(f"  → Processing year: {year}")

            grib_path = os.path.join(
                grib_folder,
                f"Revised_ERA5GRIB_{year}_{PARAM}.grib"
            )

            if not os.path.exists(grib_path):
                print(f"    ⚠ GRIB missing: {grib_path}")
                continue

            # Open GRIB ONCE per year
            ds = xr.open_dataset(grib_path)[["t2m", "d2m", "v10n"]]

            for idx, row in zip(df_year.index, df_year.itertuples(index=False)):

                timestamp = pd.Timestamp(
                    year=row.sampling_year,
                    month=row.sampling_month,
                    day=row.sampling_day,
                    hour=row.sampling_hour,
                    minute=row.sampling_minute,
                    second=row.sampling_second
                )
                lat = row.latitude
                lon = row.longitude

                
                temperature, dewpoint, v10_val = self.get_value_from_grib(ds, lat, lon, timestamp)
                
               
                df.at[idx, "Temperature"] = temperature
                df.at[idx, "DewPoint"] = dewpoint
                df.at[idx, "v10n"] = v10_val
                #df.at[idx, "u10n"] = u10_val
                
                count +=1
                
                print("Processed for row:", count)


            ds.close()

        
       
        output_file_name = f"Revised_WQPERA5AndSentinel_{PARAM}_12H.csv"
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






