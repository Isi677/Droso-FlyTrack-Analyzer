import os
import pandas as pd
import functions_extraction as f
from functions_analysis_social import interaction
from functions_analysis_centrophobism import distance_from_wall, generate_circle
from functions_analysis_preference import preference
from functions_analysis_general import summary

def main_backend(data_type, data_groups, excels_coordinates, 
                 filter_distance, filter_activity, 
                 preference_analysis, centrophobism_analysis, n_rings, 
                 total_frame_number, record_time, 
                 stop_event, progress, text_var, raw_data_save,
                 object_analysis, scaling_factor):
    
    tiempo = record_time / total_frame_number
    
    for group_name in data_groups:
        #Se obtienen los videos de cada grupo
        info_videos = excels_coordinates[group_name]
        listados_R = []
        listados_E = []
        listados_C = []
        listados_pared_R = []
        listados_pared_E = []
        listados_pared_C = []
        listados_pref_R = []
        listados_pref_E = []
        listados_pref_C = []
        listados_social_R = []
        listados_social_C = []
        listados_social_E = []
        listados_objetos = []

        num_total = len(info_videos)
        contador = 0
        
        #Se va a ver video por video dentro del grupo
        for video in info_videos:
            coord_ROI = []
            if not stop_event.is_set():
                print(f"Starting analysis: {video[0]}...")
                
                contador += 1
                progress.set(round(contador/num_total*100)) 
                path_video = video[0] #Ruta de excel de coordenadas
                n_moscas_video = video[1] #Numero de moscas por video
        
                nombre_video = video[0].split("/")
                nombre_video = nombre_video[-1]   
                text_var.set(f"Analyzing: {nombre_video}...")

            if not stop_event.is_set():
                print("Fetching ROI data...")
                #El archivo excel se transforma csv
                if data_type == "Bonsai":
                    df = pd.read_excel(path_video, sheet_name = "Data ROI + mm per pixel") 
                    df.to_csv(f"{video[0]}-ROI.csv", index = None)
                    with open(f"{video[0]}-ROI.csv", "r") as file:
                        filas = file.readlines()
                    os.remove(f"{video[0]}-ROI.csv")
    
                    roi_parameters = filas[1].strip().split(",")
                    coords_0 = min(float(roi_parameters[0]), float(roi_parameters[1]))
                    coords_1 = max(float(roi_parameters[2]), float(roi_parameters[3]))
                    coord_ROI.append((coords_0, coords_0))
                    coord_ROI.append((coords_1, coords_1))
                    coord_ROI = generate_circle(coords=coord_ROI)
                    mm_px = float(roi_parameters[4])
                    mm_py = float(roi_parameters[5])

                elif data_type == "IOWA":
                    df = pd.read_excel(path_video, sheet_name = 1) 
                    df.to_csv(f"{video[0]}-ROI.csv", index = None)
                    with open(f"{video[0]}-ROI.csv", "r") as file:
                        filas = file.readlines()
                        coord_ROI  = f.ROI_coordenadas(filas)
                    os.remove(f"{video[0]}-ROI.csv")

            if not stop_event.is_set():
                print(f"Fetching flies coordinates from video...")
                #El archivo excel se transforma csv         
                df1 = pd.read_excel(path_video, sheet_name = 0) 
                df1.to_csv(f"{video[0]}.csv", index = None)
        
                #Se abre el csv creado para leer cada fila
                with open(f"{video[0]}.csv", "r") as file:
                    filas = file.readlines()
                    if data_type == "IOWA":        
                        #Se obtienen los datos de mm por pixel
                        mm_px = filas[4].strip().split(",")
                        mm_py = filas[5].strip().split(",")
                        mm_px = float(mm_px[1])
                        mm_py = float(mm_py[1])
                        filas = filas[8:]

                        print("Proccesing coordinates...")
                        filas_sin_vacios = f.saltarse_vacios(filas, n_moscas_video) #que no tengan datos vacios
                        filas_vacios_rellenados = f.rellenar_vacios(filas, n_moscas_video) #que los datos vacios se rellenen con el dato anterior
                        filas_con_vacios = f.vacios_iguales(filas, n_moscas_video) #datos con vacios llenados con posicion x e y igual a 0

                    elif data_type == "Bonsai":
                        print("Proccesing coordinates...")
                        filas_sin_vacios = f.saltarse_vacios_bonsai(filas) #que no tengan datos vacios
                        filas_vacios_rellenados = f.rellenar_vacios_bonsai(filas) #que los datos vacios se rellenen con el dato anterior
                        filas_con_vacios = f.vacios_iguales_bonsai(filas) #datos con vacios llenados con posicion x e y igual a 0
                os.remove(f"{video[0]}.csv")
                
                #-----------------------------------------------------------------------
                #Se obtienen datos crudos por frame con la funcion distancia
                #Funcion distancia: entrega una lista para pasarla a excel y una lista con sub-listas que reflejan cada mosca    
                distancia_R, listado_R = f.distancia(
                    total_filas=filas_vacios_rellenados, n_moscas=n_moscas_video, 
                    mm_px=mm_px, mm_py=mm_py, filtro=filter_distance, tiempo_x_fr=tiempo, 
                    frames=total_frame_number)
                df_rellenado = pd.DataFrame(distancia_R)
                distancia_E, listado_E = f.distancia(
                    total_filas=filas_sin_vacios, n_moscas=n_moscas_video, 
                    mm_px=mm_px, mm_py=mm_py, filtro=filter_distance, tiempo_x_fr=tiempo, 
                    frames=total_frame_number)
                df_eliminado = pd.DataFrame(distancia_E)
                distancia_C, listado_C = f.distancia_promediada(filas_con_vacios, n_moscas_video, mm_px, mm_py, filter_distance, tiempo, total_frame_number)
                df_convacios = pd.DataFrame(distancia_C)

                #En una misma lista final, se acumulan las listas con las distancias de un video 
                # (si hay más de una mosca por video, se representan en sublistas)
                listados_E.append(listado_E)
                listados_R.append(listado_R)   
                listados_C.append(listado_C)
                
            if not stop_event.is_set() and raw_data_save:
                print("Saving Raw Data...")
                if not os.path.exists(f"./Analisis Datos Crudos/{group_name}"):
                    os.makedirs(f"./Analisis Datos Crudos/{group_name}")
                with pd.ExcelWriter(f"Analisis Datos Crudos/{group_name}/{nombre_video}.xlsx") as writer:
                    df_rellenado.to_excel(writer, sheet_name="Data Vacios Rellenados")
                    df_eliminado.to_excel(writer, sheet_name="Data Vacios Eliminados")
                    df_convacios.to_excel(writer, sheet_name="Data Vacios Incluidos")
            
            if not stop_event.is_set() and centrophobism_analysis:
                #Código para analizar centrofobismo
                print("Starting centrophobism analysis...")
                
                dist_pared_C, listado_pared_C = distance_from_wall(filas_con_vacios, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo, total_frame_number)
                dist_pared_R, listado_pared_R = distance_from_wall(filas_vacios_rellenados, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo, total_frame_number)
                dist_pared_E, listado_pared_E = distance_from_wall(filas_sin_vacios, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo, total_frame_number)
                
                if raw_data_save:
                    df_rellenado_pared = pd.DataFrame(dist_pared_R)
                    df_convacios_pared = pd.DataFrame(dist_pared_C)
                    df_eliminado_pared = pd.DataFrame(dist_pared_E)
                    if not os.path.exists(f"./Analisis Centrofobismo/{group_name}"):
                        os.makedirs(f"./Analisis Centrofobismo/{group_name}")
                    with pd.ExcelWriter(f"Analisis Centrofobismo/{group_name}/{nombre_video}.xlsx") as writer:
                        df_rellenado_pared.to_excel(writer, sheet_name="Data Vacios Rellenados")
                        df_eliminado_pared.to_excel(writer, sheet_name="Data Vacios Eliminados")
                        df_convacios_pared.to_excel(writer, sheet_name="Data Vacios Incluidos")
                
                listados_pared_R.append(listado_pared_R)
                listados_pared_E.append(listado_pared_E)
                listados_pared_C.append(listado_pared_C)

            if not stop_event.is_set():      
                if n_moscas_video > 1:
                    #Código para analizar sociabilidad
                    print("Iniciando análisis de sociabilidad...")
                    listado_social_C = interaction(filas_con_vacios, mm_px, mm_py)
                    listado_social_R = interaction(filas_vacios_rellenados,  mm_px, mm_py)
                    listados_social_C.append(listado_social_C)
                    listados_social_R.append(listado_social_R)

            if not stop_event.is_set() and preference_analysis != "No":        
                #Código para analizar preferencia de la arena
                print("Iniciando análisis de preferencia...")
                
                pref_C, listado_pref_C = preference(
                    total_filas=filas_con_vacios, coord_circulo=coord_ROI, n_moscas=n_moscas_video, 
                    tiempo=tiempo, frames=total_frame_number, formato=preference_analysis
                    )
                pref_R, listado_pref_R = preference(
                    total_filas=filas_vacios_rellenados, coord_circulo=coord_ROI, n_moscas=n_moscas_video, 
                    tiempo=tiempo, frames=total_frame_number, formato=preference_analysis
                    )
                pref_E, listado_pref_E = preference(
                    total_filas=filas_sin_vacios, coord_circulo=coord_ROI, n_moscas=n_moscas_video, 
                    tiempo=tiempo, frames=total_frame_number, formato=preference_analysis
                    )
                
                df_rellenado_pref = pd.DataFrame(pref_R)
                df_convacios_pref = pd.DataFrame(pref_C)
                df_eliminado_pref = pd.DataFrame(pref_E)
    
                if not os.path.exists(f"./Analisis Preferencia/{group_name}"):
                    os.makedirs(f"./Analisis Preferencia/{group_name}")
    
                with pd.ExcelWriter(f"Analisis Preferencia/{group_name}/{nombre_video}.xlsx") as writer:
                    df_rellenado_pref.to_excel(writer, sheet_name="Data Vacios Rellenados")
                    df_convacios_pref.to_excel(writer, sheet_name="Data Vacios Eliminados")
                    df_eliminado_pref.to_excel(writer, sheet_name="Data Vacios Incluidos")
                
                listados_pref_R.append(listado_pref_R)
                listados_pref_E.append(listado_pref_E)
                listados_pref_C.append(listado_pref_C)
            
            if not stop_event.is_set() and object_analysis:
                print("Starting object analysis...")
                #El archivo excel se transforma csv              
                df1 = pd.read_excel(path_video, sheet_name = "Data Objects Coordinates") 
                df1.to_csv(f"{video[0]}.csv", index = None)
        
                #Se abre el csv creado para leer cada fila
                with open(f"{video[0]}.csv", "r") as file:
                    filas = file.readlines()
                    data = filas[1:]
                    updated_data = []
                    for e in data:
                        e = e.strip().split(",")
                        updated_data.append(e)
                    #print(updated_data)
                    listados_objetos.append(updated_data)
        
                os.remove(f"{video[0]}.csv")
        
        if not stop_event.is_set():
            print() 
            print("Calculating final parameters..")   
            #Con los listados finales, se calculan parámetros generales de cada video y mosca por video
            summary_C = summary(
                datos_videos=listados_C, n_moscas=n_moscas_video, filtro=filter_activity,
                analizar_centrofobismo=centrophobism_analysis, datos_dist_pared=listados_pared_C, 
                analizar_preferencia=preference_analysis, datos_preferencia=listados_pref_C, 
                n_ring=n_rings, datos_social=listados_social_C, tiempo_x_fr=tiempo, objetos=listados_objetos,
                scaling_factor=scaling_factor
                )
            summary_R = summary(
                datos_videos=listados_R, n_moscas=n_moscas_video, filtro=filter_activity,
                analizar_centrofobismo=centrophobism_analysis, datos_dist_pared=listados_pared_R,
                analizar_preferencia=preference_analysis, datos_preferencia=listados_pref_R, 
                n_ring=n_rings, datos_social=listados_social_R, tiempo_x_fr=tiempo, 
                objetos=listados_objetos, scaling_factor=scaling_factor
                )
            summary_E = summary(
                datos_videos=listados_E, n_moscas=n_moscas_video, filtro=filter_activity, 
                analizar_centrofobismo=centrophobism_analysis,datos_dist_pared=listados_pared_E, 
                analizar_preferencia=preference_analysis, datos_preferencia=listados_pref_C, 
                n_ring=n_rings, datos_social=listados_social_E, tiempo_x_fr=tiempo, 
                objetos=listados_objetos, scaling_factor=scaling_factor
                )
            
            summary_E = pd.DataFrame(summary_E)
            summary_R = pd.DataFrame(summary_R)
            summary_C = pd.DataFrame(summary_C)
            print("Saving summary excel...")
            if not os.path.exists(f"./Analisis Resumen"):
                os.makedirs(f"./Analisis Resumen")
            writer = pd.ExcelWriter(f"Analisis Resumen/Summary - {group_name}.xlsx", engine='openpyxl')
            summary_C.to_excel(writer, sheet_name="Data Vacios Promediados")
            summary_R.to_excel(writer, sheet_name="Data Vacios Rellenados")
            summary_E.to_excel(writer, sheet_name="Data Vacios Eliminados")
            try: 
                writer.save()
            except:
                writer._save()                