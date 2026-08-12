"""Final Code 1"""

#FINAL: Descriptive Statistics for Params, BOA SR Bands, and Meteorological Data

import pandas as pd


chl_csv = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\EmptyRowRemovedData\\Chlorophyll.csv"
df_of_chl = pd.read_csv(chl_csv)

tss_csv = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\EmptyRowRemovedData\\TSS.csv"
df_of_tss = pd.read_csv(tss_csv)

doc_csv = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\EmptyRowRemovedData\\DOC.csv"
df_of_doc = pd.read_csv(doc_csv) 

pheo_csv = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\EmptyRowRemovedData\\Pheophytin.csv"
df_of_pheo = pd.read_csv(pheo_csv) 


class DescriptiveStats:

    @staticmethod
    def save_csv_Params ():
        cols = ["result_Chlorophyll", "result_TSS", "result_DOC", "result_Pheophytin"] 

        df_chl = df_of_chl['result_Chlorophyll']
        df_tss = df_of_tss['result_TSS']
        df_doc = df_of_doc['result_DOC']
        df_pheo = df_of_pheo['result_Pheophytin']

        stats_dict = {
            "mean": [],
            "min": [],
            "max": [],
            "Q1_25%": [],
            "Median_Q2_50%": [],
            "Q3_75%": [],
            "Std_Deviation": [],
            "Coeff_of_Variation": [],
            "length":[]
        }

        
        combined_df = pd.concat([df_chl, df_tss, df_doc, df_pheo], axis=1)

        for col in cols:
            #numeric_series = pd.to_numeric(combined_df[col], errors='coerce')
            mean_val = combined_df[col].mean()
            std_val = combined_df[col].std()
            cv_val = std_val / mean_val if mean_val != 0 else float("nan")
            length = combined_df[col].count()

            stats_dict["mean"].append(mean_val)
            stats_dict["min"].append(combined_df[col].min())
            stats_dict["max"].append(combined_df[col].max())
            stats_dict["Q1_25%"].append(combined_df[col].quantile(0.25))
            stats_dict["Median_Q2_50%"].append(combined_df[col].quantile(0.5))
            stats_dict["Q3_75%"].append(combined_df[col].quantile(0.75))
            stats_dict["Std_Deviation"].append(std_val)
            stats_dict["Coeff_of_Variation"].append(cv_val)
            stats_dict["length"].append(length)
            
        stats_df = pd.DataFrame(stats_dict, index=cols).T
        output_csv = r"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\Mean\\ParamsDescStats.csv"
        stats_df.to_csv(output_csv, index=True)

        print(f"Saved descriptive statistics to:{output_csv}")

    
    @staticmethod
    def save_csv_Surface_Reflectance (parameter):
        cols = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B11", "B12"]

        if parameter == 'Chlorophyll':
            csv = chl_csv #give respective file location 
            df = pd.read_csv(csv)
        elif parameter == 'TSS':
            csv = tss_csv #give respective file location 
            df = pd.read_csv(csv)

        elif parameter == 'DOC':
            csv = doc_csv #give respective file location 
            df = pd.read_csv(csv)

        elif parameter == 'Pheophytin':
            csv = pheo_csv #give respective file location 
            df = pd.read_csv(csv) 

        stats_dict = {
            "mean": [],
            "min": [],
            "max": [],
            "Q1_25%": [],
            "Median_Q2_50%": [],
            "Q3_75%": [],
            "Std_Deviation": [],
            "Coeff_of_Variation": [],
            "length":[]
        }

        combined_df = df

        for col in cols:
            mean_val = combined_df[col].mean()
            std_val = combined_df[col].std()
            cv_val = std_val / mean_val if mean_val != 0 else float("nan")
            len = combined_df[col].count()


            stats_dict["mean"].append(mean_val)
            stats_dict["min"].append(combined_df[col].min())
            stats_dict["max"].append(combined_df[col].max())
            stats_dict["Q1_25%"].append(combined_df[col].quantile(0.25))
            stats_dict["Median_Q2_50%"].append(combined_df[col].quantile(0.5))
            stats_dict["Q3_75%"].append(combined_df[col].quantile(0.75))
            stats_dict["Std_Deviation"].append(std_val)
            stats_dict["Coeff_of_Variation"].append(cv_val)
            stats_dict["length"].append(len)
            
        stats_df = pd.DataFrame(stats_dict, index=cols).T

        output_csv = f"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\Mean\\{parameter}_BOA_SR_DescStats.csv"
        stats_df.to_csv(output_csv, index=True)

        print(f"Saved descriptive statistics for Bottom of Atmosphere Surface Reflectances for {parameter} to:{output_csv}")

    


    def save_csv_Meteorology (parameter):
        cols = ["Temperature", "DewPoint", "v10n", "Precipitation(mm)"]
        #Temperature	DewPoint	v10n

        if parameter == 'Chlorophyll':
            csv = chl_csv #give respective file location 
            df = pd.read_csv(csv)
        elif parameter == 'TSS':
            csv = tss_csv #give respective file location 
            df = pd.read_csv(csv)

        elif parameter == 'DOC':
            csv = doc_csv #give respective file location 
            df = pd.read_csv(csv)

        elif parameter == 'Pheophytin':
            csv = pheo_csv #give respective file location 
            df = pd.read_csv(csv) 

        stats_dict = {
            "mean": [],
            "min": [],
            "max": [],
            "Q1_25%": [],
            "Median_Q2_50%": [],
            "Q3_75%": [],
            "Std_Deviation": [],
            "Coeff_of_Variation": [],
            "length":[]
        }

        combined_df = df

        for col in cols:
            mean_val = combined_df[col].mean()
            std_val = combined_df[col].std()
            cv_val = std_val / mean_val if mean_val != 0 else float("nan")
            len = combined_df[col].count()

            stats_dict["mean"].append(mean_val)
            stats_dict["min"].append(combined_df[col].min())
            stats_dict["max"].append(combined_df[col].max())
            stats_dict["Q1_25%"].append(combined_df[col].quantile(0.25))
            stats_dict["Median_Q2_50%"].append(combined_df[col].quantile(0.5))
            stats_dict["Q3_75%"].append(combined_df[col].quantile(0.75))
            stats_dict["Std_Deviation"].append(std_val)
            stats_dict["Coeff_of_Variation"].append(cv_val)
            stats_dict["length"].append(len)
            
        stats_df = pd.DataFrame(stats_dict, index=cols).T
        output_csv = f"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\StatisticsAnalysis\\Mean\\{parameter}_Meteo_DescStats.csv"
        stats_df.to_csv(output_csv, index=True)

        print(f"Saved descriptive statistics for Meteorological Variables of {parameter} to:{output_csv}")


#Run the follwing in order as follows:

ALL_PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
#DescriptiveStats.save_csv_Params()

#params = ALL_PARAMETERS[0]
#DescriptiveStats.save_csv_Surface_Reflectance(params)

#params = ALL_PARAMETERS[1]
#DescriptiveStats.save_csv_Surface_Reflectance(params)

#params = ALL_PARAMETERS[2]
#DescriptiveStats.save_csv_Surface_Reflectance(params)

#params = ALL_PARAMETERS[3]
#DescriptiveStats.save_csv_Surface_Reflectance(params)




#params = ALL_PARAMETERS[0]
#DescriptiveStats.save_csv_Meteorology(params)

#params = ALL_PARAMETERS[1]
#DescriptiveStats.save_csv_Meteorology(params)

#params = ALL_PARAMETERS[2]
#DescriptiveStats.save_csv_Meteorology(params)

#params = ALL_PARAMETERS[3]
#DescriptiveStats.save_csv_Meteorology(params)


        
