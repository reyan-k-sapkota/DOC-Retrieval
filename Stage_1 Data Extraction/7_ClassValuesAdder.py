""" Final Code for 7_ClassValuesAdder"""

#Adding corresponding of the params besides the final csv

#FINAL DONE

#Adding corresponding of the params besides the final csv


import pandas as pd
import os

chlorophyll_without_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithPrecipitationAll\\RevisedWithPrecip_WQPERA5AndSentinel_Chlorophyll_12H.csv"
chlorophyll_with_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Chlorophyll\\AllAfter2015_Chlorophyll_to_UTC.csv"

doc_without_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithPrecipitationAll\\RevisedWithPrecip_WQPERA5AndSentinel_DOC_12H.csv"
doc_with_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_DOC\\AllAfter2015_DOC_to_UTC.csv"

tss_without_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithPrecipitationAll\\RevisedWithPrecip_WQPERA5AndSentinel_TSS_12H.csv"
tss_with_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_TSS\\AllAfter2015_TSS_to_UTC.csv"

pheophytin_without_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\WithPrecipitationAll\\RevisedWithPrecip_WQPERA5AndSentinel_Pheophytin_12H.csv"
pheophytin_with_values = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_Pheophytin\\AllAfter2015_Pheophytin_to_UTC.csv"


class ValuesAdder:
    def __init__(self, parameter):
        self.parameter = parameter

    def _check_duplicates(self, df, keys, label, show_rows=False, n=5):
        dups = df.duplicated(subset=keys, keep=False)
        n_rows = dups.sum()
        n_groups = (
            df.loc[dups, keys]
            .drop_duplicates()
            .shape[0]
            if n_rows > 0 else 0
            )
        
        print(f"\n[Duplicate check] {label}")
        print(f"  → duplicated rows      : {n_rows}")
        print(f"  → duplicated key groups: {n_groups}")
        
        if show_rows and n_rows > 0:
            print(df.loc[dups, keys].head(n))


    def add_values (self):
        PARAM = self.parameter
        print(f"Adding values for parameter: {PARAM}...")

        if PARAM == 'Chlorophyll':
            df_without = pd.read_csv(chlorophyll_without_values)
            df_with = pd.read_csv(chlorophyll_with_values)

        elif PARAM == 'TSS':
            df_without = pd.read_csv(tss_without_values)
            df_with = pd.read_csv(tss_with_values)
        elif PARAM == 'DOC':
            df_without = pd.read_csv(doc_without_values)
            df_with = pd.read_csv(doc_with_values)
        elif PARAM == 'Pheophytin': 
            df_without = pd.read_csv(pheophytin_without_values)
            df_with = pd.read_csv(pheophytin_with_values)
            
        
        df_without['sample_date'] = pd.to_datetime(df_without['sample_date'])
        df_with['sample_date_utc'] = pd.to_datetime(df_with['sample_date_utc'])
        
        output = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\New Fair Python for GRIB and ERA\\ForStatisticsandMLTraining\\Correctly_Merged\\DuplicatesNotRemovedFinal"
        
        #status_column = "status"
        county_name_column = "county_name"
        sample_code_column = "sample_code"
        parameter_column = "parameter"
        sample_depth_column = "sample_depth"
        sample_depth_units_column = "sample_depth_units"
        value_column = "result" # <-- CHANGE THIS to the actual column name
        reporting_limit_column = "reporting_limit"
        units_column = "units"
        method_name_column = "method_name"
        
        df_with_small = df_with[["sample_date_utc", "latitude", "longitude", county_name_column, sample_code_column, parameter_column, sample_depth_column, sample_depth_units_column, value_column, reporting_limit_column, units_column, method_name_column]].copy()
        

        df_with_small["result"] = pd.to_numeric(
            df_with_small["result"],
            errors="coerce"
        )


        # ---------------------------
        # Aggregate BEFORE merge (CRITICAL FIX)
        # ---------------------------
        df_with_agg = (
            df_with_small
            .groupby(
                ["sample_date_utc", "latitude", "longitude"],
                as_index=False
            )
            .agg(
                **{
                    f"result_{PARAM}": ("result", "mean"),
                    f"{PARAM}_Merged_How_many_n": ("result", "count"),
                    "county_name": ("county_name", "first"),
                    "sample_code": ("sample_code", "first"),
                    "parameter": ("parameter", "first"),
                    "sample_depth": ("sample_depth", "first"),
                    "sample_depth_units": ("sample_depth_units", "first"),
                    "reporting_limit": ("reporting_limit", "first"),
                    "units": ("units", "first"),
                    "method_name": ("method_name", "first"),
                }
            )
        )

        # ---------------------------
        # Rename coordinates for merge
        # ---------------------------
        df_with_agg = df_with_agg.rename(
            columns={
                "latitude": "latitude_with",
                "longitude": "longitude_with",
            }
        )

        # ---------------------------
        # Safe left merge (now one-to-one)
        # ---------------------------

        

        
        df_without = df_without.drop_duplicates(
            subset=["sample_date", "latitude", "longitude"]   
        ) #add this portion of code if you want to drop duplicates before merging.
    

        df_final = df_without.merge(
            df_with_agg,
            left_on=["sample_date", "latitude", "longitude"],
            right_on=["sample_date_utc", "latitude_with", "longitude_with"],
            how="left",
            validate="many_to_one"
        )

        

        print(df_final.head())
        output_file = os.path.join(output, f'DropDupliCorrected_WithValuesFinal_{PARAM}.csv') #name as DropDupli for file with duplicates that are dropper before merging
        df_final.to_csv(output_file, index=False)
        print("Values successfully added. Saved as:", output_file)

        self._check_duplicates(
            df_final,
            ["sample_date", "latitude", "longitude"],
            label="df_final (merged output)"
        )


        #dups_right = df_with_agg.duplicated(
        #    subset=["sample_date_utc", "latitude_with", "longitude_with"],
        #    keep=False
        #    )
        
        #print("Duplicated rows in df_with_agg:", dups_right.sum()) 



#ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#param = ALL_PARAMETERS[0]
#ValuesAdder(param).add_values()

#ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#param = ALL_PARAMETERS[1]
#ValuesAdder(param).add_values()

#ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#param = ALL_PARAMETERS[2]
#ValuesAdder(param).add_values()

ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
param = ALL_PARAMETERS[3]
ValuesAdder(param).add_values()
