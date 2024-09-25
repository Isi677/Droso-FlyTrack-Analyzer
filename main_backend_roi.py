import pandas as pd
import os
from openpyxl import load_workbook

def obtain_mmpx_mmpy(excel_file):
    #El archivo excel se transforma csv                
    df1 = pd.read_excel(excel_file, sheet_name = 0) 
    name_file = excel_file.split(".")
    name_file = name_file[0]
    df1.to_csv(f"{name_file}.csv", index = None)

    #Se abre el csv creado para leer cada fila
    with open(f"{name_file}.csv", "r") as file:
        filas = file.readlines()
        #Se obtenien los datos de mm por pixel
        mm_px = filas[4].strip().split(",")
        mm_py = filas[5].strip().split(",")
        mm_px = float(mm_px[1])
        mm_py = float(mm_py[1])
    os.remove(f"{name_file}.csv")

    return mm_px, mm_py

def add_roi_to_csvdata(length, roi_coordinates_dict):
    for i in range (0, length):
        excel_file = roi_coordinates_dict[i][1]
        coords = roi_coordinates_dict[i][2] #List of lists containing the coordinates of each object
        identities = roi_coordinates_dict[i][3]
        data = []
        for i in range (0, len(coords)):
            data.append(coords[i] + [identities[i]])
        df_roi = pd.DataFrame(data, columns=["x0", "y0", "x1", "y1", "Type of Object"])
        print(data)

        # Load the existing workbook if it exists
        try:
            workbook = load_workbook(excel_file)
            # Remove the sheet if it already exists
            if "Data Objects Coordinates" in workbook.sheetnames:
                std = workbook["Data Objects Coordinates"]
                workbook.remove(std)
            writer = pd.ExcelWriter(excel_file, engine='openpyxl')
            writer.book = workbook
        except FileNotFoundError:
            # Create a new workbook if the file does not exist
            writer = pd.ExcelWriter(excel_file, engine='openpyxl')

        # Write the new DataFrame to the specific sheet
        df_roi.to_excel(writer, sheet_name="Data Objects Coordinates", index=False)
        writer.save()