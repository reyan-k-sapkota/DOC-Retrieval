""" Final Code for 6.1_ClassGribMatcher.  
To extracting data for Preciitation only from NEW GRIBS of precipitation and storing as new compiled final csv """

#NEW CODE: "Extracting data for Precipitation from NEW GRIBS of precipitation and storing as new compiled final csv"


import pandas as pd
import xarray as xr
import os
import scipy


NEW_GRIB_Precip_folder_Chlorophyll = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_Chlorophyll_Precip_12H"  
NEW_GRIB_Precip_folder_DOC = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_DOC_Precip_12H"
NEW_GRIB_Precip_folder_TSS = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_TSS_Precip_12H"
NEW_GRIB_Precip_folder_Pheophytin = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\All GRIBS\\New_Pheophytin_Precip_12H"

folder_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithAllMeteorology"
folder_TSS = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithAllMeteorology"
folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithAllMeteorology"
folder_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithAllMeteorology"

output_for_meteo = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithPrecipitationAll"

VARIABLES = ['Temperature', 'DewPoint Temperature', 'V10', 'U10']
VARIABLES_CODE = ['t2m', 'd2m', 'v10n', 'u10n']

class GRIB_Matcher:
    def __init__(self, parameter):
        self.parameter = parameter
    
    def get_value_from_grib(self, ds, lat, lon, timestamp):
        
        tp_flat = ds["tp"].stack(datetime=("time", "step"))
        tp_flat = tp_flat.assign_coords(datetime=ds["valid_time"].values.flatten())

        point = tp_flat.sel(
             latitude=lat,
             longitude=lon,
             method="nearest"
             )
        
        precipitation = float(point.sel(datetime=timestamp, method="nearest").values)

        return precipitation


    def match_GRIB(self):
        
        PARAM = self.parameter
        print(f"Matching ERA5 GRIB data for parameter: {PARAM}...")

        if PARAM == 'Chlorophyll':
            combined_file_name = f"Revised_WQPERA5AndSentinel_Chlorophyll_12H.csv"
            combined_file_name_path = os.path.join(folder_Chlorophyll, combined_file_name)
            grib_folder = NEW_GRIB_Precip_folder_Chlorophyll
            output_folder = output_for_meteo

        elif PARAM == 'TSS':
            combined_file_name = f"Revised_WQPERA5AndSentinel_TSS_12H.csv"
            combined_file_name_path = os.path.join(folder_TSS, combined_file_name)
            grib_folder = NEW_GRIB_Precip_folder_TSS
            output_folder = output_for_meteo

        elif PARAM == 'DOC':    
            combined_file_name = f"Revised_WQPERA5AndSentinel_DOC_12H.csv"
            combined_file_name_path = os.path.join(folder_DOC, combined_file_name)
            grib_folder = NEW_GRIB_Precip_folder_DOC
            output_folder = output_for_meteo

        elif PARAM == 'Pheophytin':
            combined_file_name = f"Revised_WQPERA5AndSentinel_Pheophytin_12H.csv"
            combined_file_name_path = os.path.join(folder_Pheophytin, combined_file_name)
            grib_folder = NEW_GRIB_Precip_folder_Pheophytin
            output_folder = output_for_meteo
        
        df = pd.read_csv(combined_file_name_path)
        
        count = 0

        for year, df_year in df.groupby("sampling_year"):

            print(f"  → Processing year: {year}")

            grib_path = os.path.join(
                grib_folder,
                f"RevisedPrecipOnly_ERA5GRIB_{year}_{PARAM}.grib"
            )

            if not os.path.exists(grib_path):
                print(f"GRIB missing: {grib_path}")
                continue

            # Open GRIB ONCE per year
            ds = xr.open_dataset(grib_path)[["tp"]]

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

                
                precipitation = self.get_value_from_grib(ds, lat, lon, timestamp)
                
               
                df.at[idx, "Precipitation(mm)"] = precipitation*1000
                
                
                count +=1
                
                print("Processed for row:", count)


            ds.close()

        
       
        output_file_name = f"RevisedWithPrecip_WQPERA5AndSentinel_{PARAM}_12H.csv"
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
