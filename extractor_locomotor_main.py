<<<<<<< HEAD
import os
import pandas as pd
from extractor_parametros import excels_coordenadas, filtro_distancia, filtro_actividad_pausas, analizar_preferencia, n_rings, tiempo
import extractor_locomotor_funciones_extraccion as f
import extractor_locomotor_funciones_analisis as fa
import extractor_locomotor_funciones_extra as fe

datos_grupos = list(excels_coordenadas.keys())

for grupo in datos_grupos:
    #Se obtienen los videos de cada grupo
    info_videos = excels_coordenadas[grupo]
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
    ROI_coords = []

    #Se va a ver video por video dentro del grupo
    for video in info_videos:
        print(f"Empezando analisis de: {video[0]}.xlsx...")
        path_video = f"{video[0]}.xlsx" #Ruta de excel de coordenadas
        n_moscas_video = video[1] #Numero de moscas por video

        nombre_video = video[0].split("/")
        nombre_video = nombre_video[-1]   

        #-----------------------------------------------------------------------
        print("Obteniendo datos de ROI...")
        #El archivo excel se transforma csv
        df = pd.read_excel(path_video, sheet_name = 1) 
        df.to_csv(f"{video[0]}-ROI.csv", index = None)

        with open(f"{video[0]}-ROI.csv", "r") as file:
            filas = file.readlines()

            coord_ROI  = f.ROI_coordenadas(filas)
        ROI_coords.append(coord_ROI)
        os.remove(f"{video[0]}-ROI.csv")
        #-----------------------------------------------------------------------
        print(f"Obteniendo coordenadas de moscas del video")

        #El archivo excel se transforma csv
        print(f"Creando {video[0]}.csv...")                
        df1 = pd.read_excel(path_video, sheet_name = 0) 
        df1.to_csv(f"{video[0]}.csv", index = None)

        #Se abre el csv creado para leer cada fila
        with open(f"{video[0]}.csv", "r") as file:
            filas = file.readlines()

            #Se obteninen los datos de mm por pixel
            mm_px = filas[4].strip().split(",")
            mm_py = filas[5].strip().split(",")
            mm_px = float(mm_px[1])
            mm_py = float(mm_py[1])

            #Se procesan las coordenadas para:
            filas_sin_vacios = f.saltarse_vacios(filas, n_moscas_video) #que no tengan datos vacios
            filas_vacios_rellenados = f.rellenar_vacios(filas, n_moscas_video) #que los datos vacios se rellenen con el dato anterior
            filas_con_vacios = f.vacios_iguales(filas, n_moscas_video) #datos con vacios llenados con posicion x e y igual a 0
        os.remove(f"{video[0]}.csv")
        
        #-----------------------------------------------------------------------
        #Se obtienen datos crudos por frame con la funcion distancia
        #Funcion distancia: entrega una lista para pasarla a excel y una lista con sub-listas que reflejan cada mosca

        distancia_R, listado_R = fa.distancia(filas_vacios_rellenados, n_moscas_video, mm_px, mm_py, filtro_distancia, tiempo)
        df_rellenado = pd.DataFrame(distancia_R)
        distancia_E, listado_E = fa.distancia(filas_sin_vacios, n_moscas_video, mm_px, mm_py, filtro_distancia, tiempo)
        df_eliminado = pd.DataFrame(distancia_E)
        distancia_C, listado_C = fa.distancia_promediada(filas_con_vacios, n_moscas_video, mm_px, mm_py, filtro_distancia, tiempo)
        df_convacios = pd.DataFrame(distancia_C)
        
        if not os.path.exists(f"./Analisis Datos Crudos/{grupo}"):
            os.makedirs(f"./Analisis Datos Crudos/{grupo}")
            
        print("Guardando datos crudos...")
        with pd.ExcelWriter(f"Analisis Datos Crudos/{grupo}/{nombre_video}.xlsx") as writer:
            df_rellenado.to_excel(writer, sheet_name="Data Vacios Rellenados")
            df_eliminado.to_excel(writer, sheet_name="Data Vacios Eliminados")
            df_convacios.to_excel(writer, sheet_name="Data Vacios Incluidos")
        print("")
    
        #En una misma lista final, se acumulan las listas con las distancias de un video 
        # (si hay más de una mosca por video, se representan en sublistas)
        listados_E.append(listado_E)
        listados_R.append(listado_R)   
        listados_C.append(listado_C)

        #-----------------------------------------------------------------------
        #Código para analizar centrofobismo
        print("Iniciando análisis centrofobismo...")
        
        dist_pared_C, listado_pared_C = fe.distancia_pared(filas_con_vacios, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo)
        dist_pared_R, listado_pared_R = fe.distancia_pared(filas_vacios_rellenados, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo)
        dist_pared_E, listado_pared_E = fe.distancia_pared(filas_sin_vacios, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo)
        
        df_rellenado_pared = pd.DataFrame(dist_pared_R)
        df_convacios_pared = pd.DataFrame(dist_pared_C)
        df_eliminado_pared = pd.DataFrame(dist_pared_E)
        if not os.path.exists(f"./Analisis Centrofobismo/{grupo}"):
            os.makedirs(f"./Analisis Centrofobismo/{grupo}")
        with pd.ExcelWriter(f"Analisis Centrofobismo/{grupo}/{nombre_video}.xlsx") as writer:
            df_rellenado_pared.to_excel(writer, sheet_name="Data Vacios Rellenados")
            df_eliminado_pared.to_excel(writer, sheet_name="Data Vacios Eliminados")
            df_convacios_pared.to_excel(writer, sheet_name="Data Vacios Incluidos")
        
        listados_pared_R.append(listado_pared_R)
        listados_pared_E.append(listado_pared_E)
        listados_pared_C.append(listado_pared_C)

        #-----------------------------------------------------------------------
        if n_moscas_video > 1:
            #Código para analizar sociabilidad
            print("Iniciando análisis de sociabilidad...")
            listado_social_C = fe.interaccion(filas_con_vacios, mm_px, mm_py)
            listado_social_R = fe.interaccion(filas_vacios_rellenados,  mm_px, mm_py)
            listados_social_C.append(listado_social_C)
            listados_social_R.append(listado_social_R)
            

        #-----------------------------------------------------------------------
        #Código para analizar preferencia de la arena
        if analizar_preferencia[0]:
            print("Iniciando análisis de preferencia...")
            
            pref_C, listado_pref_C = fa.preference(filas_con_vacios, coord_ROI, n_moscas_video, tiempo)
            pref_R, listado_pref_R = fa.preference(filas_vacios_rellenados, coord_ROI, n_moscas_video, tiempo)
            pref_E, listado_pref_E = fa.preference(filas_sin_vacios, coord_ROI, n_moscas_video, tiempo)
            
            df_rellenado_pref = pd.DataFrame(pref_R)
            df_convacios_pref = pd.DataFrame(pref_C)
            df_eliminado_pref = pd.DataFrame(pref_E)

            if not os.path.exists(f"./Analisis Preferencia/{grupo}"):
                os.makedirs(f"./Analisis Preferencia/{grupo}")

            with pd.ExcelWriter(f"Analisis Preferencia/{grupo}/{nombre_video}.xlsx") as writer:
                df_rellenado_pref.to_excel(writer, sheet_name="Data Vacios Rellenados")
                df_convacios_pref.to_excel(writer, sheet_name="Data Vacios Eliminados")
                df_eliminado_pref.to_excel(writer, sheet_name="Data Vacios Incluidos")
            
            listados_pref_R.append(listado_pref_R)
            listados_pref_E.append(listado_pref_E)
            listados_pref_C.append(listado_pref_C)

    print() 
    print("Calculando parámetros finales...")   
    #Con los listados finales, se calculan parámetros generales de cada video y mosca por video
    print("Parámetros de data con vacios promediados")
    summary_C = fa.summary(listados_C, n_moscas_video, 
                          filtro_actividad_pausas, 
                          listados_pared_C, ROI_coords,
                          analizar_preferencia[0], listados_pref_C, n_rings, 
                          listados_social_C, tiempo)
    print("Parámetros de data con vacios rellenados")
    summary_R = fa.summary(listados_R, n_moscas_video, 
                          filtro_actividad_pausas, 
                          listados_pared_R, ROI_coords,
                          analizar_preferencia[0], listados_pref_R, n_rings, 
                          listados_social_R, tiempo)
    print("Parámetros de data con vacios eliminados")
    summary_E = fa.summary(listados_E, n_moscas_video, 
                          filtro_actividad_pausas, 
                          listados_pared_E, ROI_coords,
                          analizar_preferencia[0], listados_pref_C, n_rings, 
                          listados_social_E, tiempo)
    
    summary_E = pd.DataFrame(summary_E)
    summary_R = pd.DataFrame(summary_R)
    summary_C = pd.DataFrame(summary_C)
    print()
    print("Guardando excel resumen...")
    if not os.path.exists(f"./Analisis Resumen"):
        os.makedirs(f"./Analisis Resumen")
    writer = pd.ExcelWriter(f"Analisis Resumen/Summary - {grupo}.xlsx", engine='openpyxl')
    summary_R.to_excel(writer, sheet_name="Data Vacios Rellenados")
    summary_E.to_excel(writer, sheet_name="Data Vacios Eliminados")
    summary_C.to_excel(writer, sheet_name="Data Vacios Promediados")
    writer.save()


        

            


=======
import os
import pandas as pd
from extractor_parametros import excels_coordenadas, filtro_distancia, filtro_actividad_pausas, analizar_preferencia, n_rings, tiempo
import extractor_locomotor_funciones_extraccion as f
import extractor_locomotor_funciones_analisis as fa
import extractor_locomotor_funciones_extra as fe

datos_grupos = list(excels_coordenadas.keys())

for grupo in datos_grupos:
    #Se obtienen los videos de cada grupo
    info_videos = excels_coordenadas[grupo]
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
    ROI_coords = []

    #Se va a ver video por video dentro del grupo
    for video in info_videos:
        print(f"Empezando analisis de: {video[0]}.xlsx...")
        path_video = f"{video[0]}.xlsx" #Ruta de excel de coordenadas
        n_moscas_video = video[1] #Numero de moscas por video

        nombre_video = video[0].split("/")
        nombre_video = nombre_video[-1]   

        #-----------------------------------------------------------------------
        print("Obteniendo datos de ROI...")
        #El archivo excel se transforma csv
        df = pd.read_excel(path_video, sheet_name = 1) 
        df.to_csv(f"{video[0]}-ROI.csv", index = None)

        with open(f"{video[0]}-ROI.csv", "r") as file:
            filas = file.readlines()

            coord_ROI  = f.ROI_coordenadas(filas)
        ROI_coords.append(coord_ROI)
        os.remove(f"{video[0]}-ROI.csv")
        #-----------------------------------------------------------------------
        print(f"Obteniendo coordenadas de moscas del video")

        #El archivo excel se transforma csv
        print(f"Creando {video[0]}.csv...")                
        df1 = pd.read_excel(path_video, sheet_name = 0) 
        df1.to_csv(f"{video[0]}.csv", index = None)

        #Se abre el csv creado para leer cada fila
        with open(f"{video[0]}.csv", "r") as file:
            filas = file.readlines()

            #Se obteninen los datos de mm por pixel
            mm_px = filas[4].strip().split(",")
            mm_py = filas[5].strip().split(",")
            mm_px = float(mm_px[1])
            mm_py = float(mm_py[1])

            #Se procesan las coordenadas para:
            filas_sin_vacios = f.saltarse_vacios(filas, n_moscas_video) #que no tengan datos vacios
            filas_vacios_rellenados = f.rellenar_vacios(filas, n_moscas_video) #que los datos vacios se rellenen con el dato anterior
            filas_con_vacios = f.vacios_iguales(filas, n_moscas_video) #datos con vacios llenados con posicion x e y igual a 0
        os.remove(f"{video[0]}.csv")
        
        #-----------------------------------------------------------------------
        #Se obtienen datos crudos por frame con la funcion distancia
        #Funcion distancia: entrega una lista para pasarla a excel y una lista con sub-listas que reflejan cada mosca

        distancia_R, listado_R = fa.distancia(filas_vacios_rellenados, n_moscas_video, mm_px, mm_py, filtro_distancia, tiempo)
        df_rellenado = pd.DataFrame(distancia_R)
        distancia_E, listado_E = fa.distancia(filas_sin_vacios, n_moscas_video, mm_px, mm_py, filtro_distancia, tiempo)
        df_eliminado = pd.DataFrame(distancia_E)
        distancia_C, listado_C = fa.distancia_promediada(filas_con_vacios, n_moscas_video, mm_px, mm_py, filtro_distancia, tiempo)
        df_convacios = pd.DataFrame(distancia_C)
        
        if not os.path.exists(f"./Analisis Datos Crudos/{grupo}"):
            os.makedirs(f"./Analisis Datos Crudos/{grupo}")
            
        print("Guardando datos crudos...")
        with pd.ExcelWriter(f"Analisis Datos Crudos/{grupo}/{nombre_video}.xlsx") as writer:
            df_rellenado.to_excel(writer, sheet_name="Data Vacios Rellenados")
            df_eliminado.to_excel(writer, sheet_name="Data Vacios Eliminados")
            df_convacios.to_excel(writer, sheet_name="Data Vacios Incluidos")
        print("")
    
        #En una misma lista final, se acumulan las listas con las distancias de un video 
        # (si hay más de una mosca por video, se representan en sublistas)
        listados_E.append(listado_E)
        listados_R.append(listado_R)   
        listados_C.append(listado_C)

        #-----------------------------------------------------------------------
        #Código para analizar centrofobismo
        print("Iniciando análisis centrofobismo...")
        
        dist_pared_C, listado_pared_C = fe.distancia_pared(filas_con_vacios, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo)
        dist_pared_R, listado_pared_R = fe.distancia_pared(filas_vacios_rellenados, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo)
        dist_pared_E, listado_pared_E = fe.distancia_pared(filas_sin_vacios, coord_ROI, n_moscas_video, mm_px, mm_py, n_rings, tiempo)
        
        df_rellenado_pared = pd.DataFrame(dist_pared_R)
        df_convacios_pared = pd.DataFrame(dist_pared_C)
        df_eliminado_pared = pd.DataFrame(dist_pared_E)
        if not os.path.exists(f"./Analisis Centrofobismo/{grupo}"):
            os.makedirs(f"./Analisis Centrofobismo/{grupo}")
        with pd.ExcelWriter(f"Analisis Centrofobismo/{grupo}/{nombre_video}.xlsx") as writer:
            df_rellenado_pared.to_excel(writer, sheet_name="Data Vacios Rellenados")
            df_eliminado_pared.to_excel(writer, sheet_name="Data Vacios Eliminados")
            df_convacios_pared.to_excel(writer, sheet_name="Data Vacios Incluidos")
        
        listados_pared_R.append(listado_pared_R)
        listados_pared_E.append(listado_pared_E)
        listados_pared_C.append(listado_pared_C)

        #-----------------------------------------------------------------------
        if n_moscas_video > 1:
            #Código para analizar sociabilidad
            print("Iniciando análisis de sociabilidad...")
            listado_social_C = fe.interaccion(filas_con_vacios, mm_px, mm_py, n_moscas_video)
            listado_social_R = fe.interaccion(filas_vacios_rellenados,  mm_px, mm_py, n_moscas_video)
            
            print(len(listado_social_C[0]))
            print(listado_social_C[0])
            listados_social_R.append(listado_social_R)
            listados_social_C.append(listado_social_C)
        #-----------------------------------------------------------------------
        #Código para analizar preferencia de la arena
        if analizar_preferencia[0]:
            print("Iniciando análisis de preferencia...")
            
            pref_C, listado_pref_C = fa.preference(filas_con_vacios, coord_ROI, n_moscas_video, tiempo)
            pref_R, listado_pref_R = fa.preference(filas_vacios_rellenados, coord_ROI, n_moscas_video, tiempo)
            pref_E, listado_pref_E = fa.preference(filas_sin_vacios, coord_ROI, n_moscas_video, tiempo)
            
            df_rellenado_pref = pd.DataFrame(pref_R)
            df_convacios_pref = pd.DataFrame(pref_C)
            df_eliminado_pref = pd.DataFrame(pref_E)

            if not os.path.exists(f"./Analisis Preferencia/{grupo}"):
                os.makedirs(f"./Analisis Preferencia/{grupo}")

            with pd.ExcelWriter(f"Analisis Preferencia/{grupo}/{nombre_video}.xlsx") as writer:
                df_rellenado_pref.to_excel(writer, sheet_name="Data Vacios Rellenados")
                df_convacios_pref.to_excel(writer, sheet_name="Data Vacios Eliminados")
                df_eliminado_pref.to_excel(writer, sheet_name="Data Vacios Incluidos")
            
            listados_pref_R.append(listado_pref_R)
            listados_pref_E.append(listado_pref_E)
            listados_pref_C.append(listado_pref_C)

    print() 
    print("Calculando parámetros finales...")   
    #Con los listados finales, se calculan parámetros generales de cada video y mosca por video
    print("Parámetros de data con vacios promediados")
    summary_C = fa.summary(listados_C, n_moscas_video, 
                          filtro_actividad_pausas, 
                          listados_pared_C, ROI_coords,
                          analizar_preferencia[0], listados_pref_C, n_rings, 
                          listados_social_C, tiempo)
    print("Parámetros de data con vacios rellenados")
    summary_R = fa.summary(listados_R, n_moscas_video, 
                          filtro_actividad_pausas, 
                          listados_pared_R, ROI_coords,
                          analizar_preferencia[0], listados_pref_R, n_rings, 
                          listados_social_R, tiempo)
    print("Parámetros de data con vacios eliminados")
    summary_E = fa.summary(listados_E, n_moscas_video, 
                          filtro_actividad_pausas, 
                          listados_pared_E, ROI_coords,
                          analizar_preferencia[0], listados_pref_C, n_rings, 
                          listados_social_E, tiempo)
    
    summary_E = pd.DataFrame(summary_E)
    summary_R = pd.DataFrame(summary_R)
    summary_C = pd.DataFrame(summary_C)
    print()
    print("Guardando excel resumen...")
    if not os.path.exists(f"./Analisis Resumen"):
        os.makedirs(f"./Analisis Resumen")
    writer = pd.ExcelWriter(f"Analisis Resumen/Summary - {grupo}.xlsx", engine='openpyxl')
    summary_R.to_excel(writer, sheet_name="Data Vacios Rellenados")
    summary_E.to_excel(writer, sheet_name="Data Vacios Eliminados")
    summary_C.to_excel(writer, sheet_name="Data Vacios Promediados")
    writer.save()


        

            


>>>>>>> ffaa2eb307a719dfcc9e8527f960eb498e9a81b9
            