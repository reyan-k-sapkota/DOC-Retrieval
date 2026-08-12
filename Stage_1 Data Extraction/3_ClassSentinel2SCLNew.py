""" Extraction Code using SCL masking"""
"""Final Code for Class: Extraction_Sentinel2_with_SCL"""

import ee
import pandas as pd
import math

PROJECT_ID = 'Google Earth Engine Project ID: from reyansapkota.108@gmail.com'

ee.Initialize(project=PROJECT_ID)


PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']

folder_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_Chlorophyll"
folder_TSS ="D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_TSS"
folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_DOC"
folder_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\SurfaceReflectanceNew\\SurfaceReflectance_EachStations_Pheophytin"


#Many key surface-reflectance and classification bands (including SCL) are natively 20 m, so it’s a balanced scale. 
#It avoids mixing 10 m and 20 m resolutions inconsistently. 
#It speeds up the operation compared to 10 m without much accuracy loss.

 # Sentinel-2 Level-2A Scene Classification Layer (SCL) codes:
# 0 - No data
# 1 - Saturated / defective
# 2 - Dark area pixels
# 3 - Cloud shadow
# 4 - Vegetation
# 5 - Bare soils
# 6 - Water
# 7 - Cloud low probability / Unclassified
# 8 - Cloud medium probability
# 9 - Cloud high probability
# 10 - Thin cirrus
# 11 - Snow or ice

class Extraction_Sentinel2_with_SCL_3x3:
    def __init__(self, folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin):
        self.folder_Chlorophyll = folder_Chlorophyll
        self.folder_TSS = folder_TSS
        self.folder_DOC = folder_DOC
        self.folder_Pheophytin = folder_Pheophytin
    
    def batching(self, parameter):
        
        df_stations = pd.read_csv(f"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel_New\\New_Unique and UTC_{parameter}\\unique_locations_Param_{parameter}.csv")
        coords_list = [(i+1, row['latitude'], row['longitude']) for i, row in df_stations.iterrows()]
        num_batches = 5
        batch_size = math.ceil(len(coords_list) / num_batches)
        coords_batches = [coords_list[i:i+batch_size] for i in range(0, len(coords_list), batch_size)]
        return coords_batches

    # --- Pixel-level cloud masking using SCL ---
    def mask_clouds(self, img):
        scl = img.select("SCL")
        # Remove cloud shadows (3) and clouds (7-10)
        # ✅ Keep only “clear” surface classes (recommended by ESA and GEE docs) mask = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6))
        #this code below removes 3, 5, 8, 9, 10, 0, 1. 0 refers to no data and 1 refers to defective data.
        cloud_mask = scl.neq(3).And(scl.neq(7)).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(0)).And(scl.neq(1))
        return img.updateMask(cloud_mask)

    
    def extraction_from_sentinel_2(self, station, latitude, longitude, parameter):
        point = ee.Geometry.Point([longitude, latitude])
        region = point.buffer(30).bounds()   # 3×3 pixel equivalent (~60m × 60m)
        bands = ["B1","B2","B3","B4","B5","B6","B7","B8","B8A","B9","B11","B12"]
        
        # Load Sentinel-2 SR collection
        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
          .filterBounds(region)
          .filterDate("2017-03-28", "2025-10-08")
          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))
          .map(self.mask_clouds) #applying SCL cloud masking
        )
        
        """
        # --- Define extraction logic ---
        def extract_values(img):
            # Count valid pixels (unmasked)
            valid_count = img.select("B2").reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=region,
                scale=20,
                bestEffort=True
            ).get("B2")
           
            # Condition: only accept if 5 or more valid pixels remain
            img_valid = ee.Algorithms.If(
                ee.Number(valid_count).gte(5),
                img,
                None  # skip image if fewer than 5 valid pixels
            )
            
            # Proceed only if valid image
            
            return ee.Algorithms.If(
                img_valid,
                ee.Feature(
                    None,
                    img.select(bands).reduceRegion(
                        reducer=ee.Reducer.median(), #median() to reduce the influence of outliers
                        geometry=region,
                        scale=20,
                        bestEffort=True
                    ).set("datetime_utc", ee.Date(img.get("system:time_start")).format("YYYY-MM-dd HH:mm:ss"))
                ),
                None
            )
        """

        def extract_values(img):
            # Count valid pixels (unmasked)
            valid_count = img.select("B2").reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=region,
                scale=20,
                bestEffort=True
            ).get("B2")
            
            # Only process if 5 or more valid pixels
            is_valid = ee.Number(valid_count).gte(5)
            
            # Extract median values or fill with nulls if not enough pixel
            props = ee.Dictionary(ee.Algorithms.If(
                is_valid,
                img.select(bands).reduceRegion(
                    reducer=ee.Reducer.median(),
                    geometry=region,
                    scale=20,
                    bestEffort=True
                ),
                ee.Dictionary.fromLists(bands, [None]*len(bands))
            ))
            # Add datetime
            
            props = props.set("datetime_utc", ee.Date(img.get("system:time_start")).format("YYYY-MM-dd HH:mm:ss"))
            return ee.Feature(None, props)

        
        # Apply extraction and remove nulls
        results = s2.map(extract_values).filter(ee.Filter.notNull(["B2"]))
        data = results.aggregate_array("datetime_utc").getInfo()
        print(f"Found {len(data)} valid images.")
        
        features = results.getInfo()["features"]
        rows = [f["properties"] for f in features]
        df = pd.DataFrame(rows)
        
        # Scale reflectance to 0–1
        df[bands] = df[bands] / 10000.0
        
        # Choose output folder
        if parameter == 'Chlorophyll':
            output_folder = self.folder_Chlorophyll
        elif parameter == 'TSS':
            output_folder = self.folder_TSS
        elif parameter == 'DOC':
            output_folder = self.folder_DOC
        elif parameter == 'Pheophytin':
            output_folder = self.folder_Pheophytin
            
        
        df.to_csv(f"{output_folder}\\{latitude}_{longitude}_SurfaceReflectance_utc.csv", index=False)
        print(f"Done for Station {station}")
        
    def extraction_from_sentinel_2_per_batch(self, coords_list, parameter):
        for idx, lat, lon in coords_list:
            self.extraction_from_sentinel_2(idx, lat, lon, parameter)
            print(f"Finished Station {idx}")

#FOR CHLOROPHYLL
#param1 = PARAMETERS[0]
#all_coords_list1 = Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param1)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list1

#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param1)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param1)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param1)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param1)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param1)

#For TSS
#param2 = PARAMETERS[1]
#all_coords_list2 = Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param2)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list2

#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param2)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param2)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param2)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param2)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param2)

#For DOC
#param3 = PARAMETERS[2]
#all_coords_list3 = Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param3)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list3

#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param3)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param3)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param3)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param3)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param3)

#For Pheophytin
#param4 = PARAMETERS[3]
#all_coords_list4 = Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param4)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list4

#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param4)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param4)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param4)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param4)
#Extraction_Sentinel2_with_SCL_3x3(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param4)















"""  

The follwing Code below is the old extraction code without 3x3 (60m x 60m) pixel window

"""

"""
PARAMETERS = ['Chlorophyll', 'TSS', 'DOC', 'Pheophytin']
folder_Chlorophyll = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\SurfaceReflectance\\SurfaceReflectance_EachStations_Chlorophyll_after2017"
folder_TSS ="D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\SurfaceReflectance\\SurfaceReflectance_EachStations_TSS"
folder_DOC = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\SurfaceReflectance\\SurfaceReflectance_EachStations_DOC"
folder_Pheophytin = "D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\SurfaceReflectance\\SurfaceReflectance_EachStations_Pheophytin"

#Many key surface-reflectance and classification bands (including SCL) are natively 20 m, so it’s a balanced scale. 
#It avoids mixing 10 m and 20 m resolutions inconsistently. 
#It speeds up the operation compared to 10 m without much accuracy loss.

 # Sentinel-2 Level-2A Scene Classification Layer (SCL) codes:
# 0 - No data
# 1 - Saturated / defective
# 2 - Dark area pixels
# 3 - Cloud shadow
# 4 - Vegetation
# 5 - Bare soils
# 6 - Water
# 7 - Cloud low probability / Unclassified
# 8 - Cloud medium probability
# 9 - Cloud high probability
# 10 - Thin cirrus
# 11 - Snow or ice

class Extraction_Sentinel2_with_SCL:
    def __init__(self, folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin):
        self.folder_Chlorophyll = folder_Chlorophyll
        self.folder_TSS = folder_TSS
        self.folder_DOC = folder_DOC
        self.folder_Pheophytin = folder_Pheophytin
    
    def batching(self, parameter):
        
        df_stations = pd.read_csv(f"D:\\Shukra_sir\\WQI_Research\\Scripts and Data\\Datasets\\Sentinel\\Unique and UTC_{parameter}\\unique_locations_Param_{parameter}.csv")
        coords_list = [(i+1, row['latitude'], row['longitude']) for i, row in df_stations.iterrows()]
        num_batches = 5
        batch_size = math.ceil(len(coords_list) / num_batches)
        coords_batches = [coords_list[i:i+batch_size] for i in range(0, len(coords_list), batch_size)]
        return coords_batches

    # --- Pixel-level cloud masking using SCL ---
    def mask_clouds(self, img):
        scl = img.select("SCL")
        # Remove cloud shadows (3) and clouds (7-10)
        # ✅ Keep only “clear” surface classes (recommended by ESA and GEE docs) mask = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6))
        #this code below removes 3, 5, 8, 9, 10, 0, 1. 0 refers to no data and 1 refers to defective data.
        cloud_mask = scl.neq(3).And(scl.neq(7)).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(0)).And(scl.neq(1))
        return img.updateMask(cloud_mask)

    def extraction_from_sentinel_2(self, station, latitude, longitude, parameter):
        point = ee.Geometry.Point([longitude, latitude])
        region = point.buffer(100).bounds()  #buffer (100) creates 3X3 pixel window with 200mx200m. buffer(30) creates 3x3 pixel window with 60mx60m.
        
        bands = ["B1","B2","B3","B4","B5","B6","B7","B8","B8A","B9","B11","B12"]
        
        # Load Sentinel-2 SR collection
        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(region)
              .filterDate("2017-03-28", "2025-10-08") #change the date from 2017-03-28 because  COPERNICUS/S2_SR_HARMONIZED starts from 2017-03-28 
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))  # image-level filter #You can delete it as well. No need to add cloud pixel percentage. But, 30 percent is recommened. 
            )
        
        # Apply SCL pixel-level cloud masking
        s2_clean = s2.map(self.mask_clouds)
        
        # Extract mean reflectance and UTC datetime
        def extract_values(img):
            stats = img.select(bands).reduceRegion(
                reducer=ee.Reducer.mean(),   #if you want the averaging to be done without considering outlier effects, choose ee.Reducer.median() over ee.Reducer.mean()
                geometry=region,
                scale=20, #re-samples every bands' resolution to 20m. This is recommended. Search for papers that recommend this re-sampling resolution.
                bestEffort=True
            )
            time_utc = ee.Date(img.get("system:time_start")).format("YYYY-MM-dd HH:mm:ss")
            return ee.Feature(None, stats).set("datetime_utc", time_utc)
        
        results = s2_clean.map(extract_values).filter(ee.Filter.notNull(["B2"]))
        data = results.aggregate_array("datetime_utc").getInfo()
        print(f"Found {len(data)} valid images.")

    
        features = results.getInfo()["features"]
        rows = [f["properties"] for f in features]
        df = pd.DataFrame(rows)

        # Scale reflectance to 0-1
        df[bands] = df[bands] / 10000.0
        
        
        if parameter == 'Chlorophyll':
            output_folder = self.folder_Chlorophyll
        elif parameter == 'TSS':
            output_folder = self.folder_TSS
        elif parameter == 'DOC':
            output_folder = self.folder_DOC  
        elif parameter == 'Pheophytin':
            output_folder = self.folder_Pheophytin
        
        df.to_csv(f"{output_folder}\\{latitude}_{longitude}_SurfaceReflectance_utc.csv", index=False)
        print(f"Done for Station {station}")

    def extraction_from_sentinel_2_per_batch(self, coords_list, parameter):
        for idx, lat, lon in coords_list:
            self.extraction_from_sentinel_2(idx, lat, lon, parameter)
            print(f"Finished Station {idx}")

#FOR CHLOROPHYLL
#param1 = PARAMETERS[0]
#all_coords_list1 = Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param1)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list1

#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param1)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param1)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param1)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param1)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param1)

#For TSS
#param2 = PARAMETERS[1]
#all_coords_list2 = Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param2)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list2

#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param2)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param2)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param2)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param2)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param2)

#For DOC
#param3 = PARAMETERS[2]
#all_coords_list3 = Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param3)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list3

#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param3)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param3)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param3)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param3)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param3)

#For Pheophytin
#param4 = PARAMETERS[3]
#all_coords_list4 = Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).batching(param4)
#coords_list1, coords_list2, coords_list3, coords_list4, coords_list5 = all_coords_list4

#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list1, param4)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list2, param4)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list3, param4)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list4, param4)
#Extraction_Sentinel2_with_SCL(folder_Chlorophyll, folder_TSS, folder_DOC, folder_Pheophytin).extraction_from_sentinel_2_per_batch(coords_list5, param4)

"""