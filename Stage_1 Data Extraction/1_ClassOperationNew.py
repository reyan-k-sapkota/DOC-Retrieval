import pandas as pd

PARAMETERS = ['Chlorophyll a', 'Total Suspended Solids', 'Dissolved Organic Carbon', 'Pheophytin a', 'Turbidity', 'Color']
df_lab_results_1GB = pd.read_csv ("D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\FromLabResults1GB\\lab_results.csv")
df_Surface_Water_All = df_Surface_Water_only = df_lab_results_1GB[df_lab_results_1GB["station_type"] == "Surface Water"]
output_folder  = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\Parameters"

PARAM_FILE_NAME = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin', 'Turbidity', 'Color']

class Operation_new():
    def __init__(self, df_Surface_Water_All, parameter, output_folder):
        self.df_Surface_Water_All = df_Surface_Water_All
        self.parameter = parameter 
        self.output_folder = output_folder

    def make_ascending(self, df):
        df_Param = df
        df_Param["sample_date"] = pd.to_datetime(df_Param["sample_date"], errors="coerce")
        df_Param = df_Param.sort_values(by="sample_date", ascending=True).reset_index(drop=True)
        return df_Param

    def filter_by_parameter(self, ParamFileName):
        parameter_name = self.parameter
        df_param = self.df_Surface_Water_All[self.df_Surface_Water_All["parameter"] == parameter_name]
        df_param_asc = self.make_ascending(df_param)
        df_param_asc.to_csv(f"{self.output_folder}\\{ParamFileName}All.csv", index=False)
        print(f"Saved {parameter_name} data to {self.output_folder}\\{ParamFileName}All.csv ")
    
    
    def parameter_after_2015(self, ParamFileName):
        cutoff_date = pd.Timestamp('2015-06-01 00:00:00')
        parameter_name = self.parameter
        #df_param = self.df_Surface_Water_All[self.df_Surface_Water_All["parameter"] == parameter_name]

        df_param = pd.read_csv(f"{self.output_folder}\\{ParamFileName}All.csv")

        df_param['sample_date'] = pd.to_datetime(df_param['sample_date'], errors='coerce')
        df_paramfinal = df_param[df_param['sample_date'] >= cutoff_date].reset_index(drop=True)
        df_paramfinal.to_csv(f"{self.output_folder}\\{ParamFileName}After2015.csv", index=False)
        print(f"Saved {parameter_name} data after 2015 to {self.output_folder}\\{ParamFileName}After2015.csv ")

"""
Instructions:
a. First run filter_by_parameter
b. Then run parameter_after_2015
"""

#For Chlorophyll
#param = PARAMETERS[0]
#param_file_name = PARAM_FILE_NAME[0]
#Operation_new(df_Surface_Water_All, param, output_folder).filter_by_parameter(param_file_name)
#Operation_new(df_Surface_Water_All, param, output_folder).parameter_after_2015(param_file_name)

#For TSS
#param = PARAMETERS[1]
#param_file_name = PARAM_FILE_NAME[1]
#Operation_new(df_Surface_Water_All, param, output_folder).filter_by_parameter(param_file_name)
#Operation_new(df_Surface_Water_All, param, output_folder).parameter_after_2015(param_file_name)

#For DOC
#param = PARAMETERS[2]
#param_file_name = PARAM_FILE_NAME[2]
#Operation_new(df_Surface_Water_All, param, output_folder).filter_by_parameter(param_file_name)
#Operation_new(df_Surface_Water_All, param, output_folder).parameter_after_2015(param_file_name)

#For Pheophytin
#param = PARAMETERS[3]
#param_file_name = PARAM_FILE_NAME[3]
#Operation_new(df_Surface_Water_All, param, output_folder).filter_by_parameter(param_file_name)
#Operation_new(df_Surface_Water_All, param, output_folder).parameter_after_2015(param_file_name)


#For Turbidity
#param = PARAMETERS[4]
#param_file_name = PARAM_FILE_NAME[4]
#Operation_new(df_Surface_Water_All, param, output_folder).filter_by_parameter(param_file_name)
#Operation_new(df_Surface_Water_All, param, output_folder).parameter_after_2015(param_file_name)

#For Color
#param = PARAMETERS[5]
#param_file_name = PARAM_FILE_NAME[5]
#Operation_new(df_Surface_Water_All, param, output_folder).filter_by_parameter(param_file_name)
#Operation_new(df_Surface_Water_All, param, output_folder).parameter_after_2015(param_file_name)
