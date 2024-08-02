from functions_analysis_general import calculate_distance, ordenar_datos_para_exc

def rellenar_vacios(filas, n_moscas):
    total_filas = []
    posicion_mosca = -1
    data_anterior = filas[8].strip().split(",")

    for i in range (1, n_moscas+1):
        posicion_mosca += 2
        filas_nuevas = []

        for i in range (8, len(filas)):
            data_actual = filas[i].strip().split(",")

            if data_actual[0] != "":
                #Si existe el frame
                frame = int(data_actual[0])
                if data_actual[posicion_mosca] != "":
                    #Si existen los datos y el frame
                    posicionx = float(data_actual[posicion_mosca])
                    posiciony = float(data_actual[posicion_mosca+1])
                else:
                    #Si no existen los datos pero si el frame
                    posicionx = float(data_anterior[1])
                    posiciony = float(data_anterior[2])
            else:
                #Si no existen los datos ni el frame
                frame = int(data_anterior[0])+1
                posicionx = float(data_anterior[1])
                posiciony = float(data_anterior[2])
            
            fila_nueva = [frame, posicionx, posiciony]
            filas_nuevas.append(fila_nueva)
            data_anterior = fila_nueva

        total_filas.append(filas_nuevas)    
       
    return total_filas
               
def saltarse_vacios(filas, n_moscas): 
    total_filas = []
    posicion_mosca = -1

    for i in range (1, n_moscas+1):
        posicion_mosca += 2
        filas_nuevas = []
        j = 8

        while j != len(filas):
            data_actual = filas[j].strip().split(",")

            if data_actual[posicion_mosca] != "":
                #Si existen los datos y el frame
                frame = int(data_actual[0])
                posicionx = data_actual[posicion_mosca]
                posiciony = data_actual[posicion_mosca+1]
                fila_nueva = [frame, posicionx, posiciony]
                filas_nuevas.append(fila_nueva)
            j += 1
        total_filas.append(filas_nuevas)

    return total_filas

def vacios_iguales(filas, n_moscas):
    total_filas = []
    posicion_mosca = -1
    data_anterior = filas[8].strip().split(",")

    for i in range (1, n_moscas+1):
        posicion_mosca += 2
        filas_nuevas = []
        for j in range (8, len(filas)):
            data_actual = filas[j].strip().split(",")

            if data_actual == "":
                frame = int(data_anterior[0])+1
                posicionx = 0
                posiciony = 0
            else:
                if data_actual[0] != "":
                    frame = int(data_actual[0])
                else: 
                    frame = int(data_anterior[0])+1
                if data_actual[posicion_mosca] != "":
                    #Si existen los datos y el frame
                    posicionx = float(data_actual[posicion_mosca])
                    posiciony = float(data_actual[posicion_mosca+1])
                else:
                    #Si no existen los datos pero si el frame
                    posicionx = 0
                    posiciony = 0

            fila_nueva = [frame, posicionx, posiciony]
            filas_nuevas.append(fila_nueva)
            data_anterior = fila_nueva

        total_filas.append(filas_nuevas)  
    return total_filas

def ROI_coordenadas(filas):
    filas_final = []

    for i in range (2, len(filas)):
        fila = filas[i].split(",")
        
        x = float(fila[0])
        y = float(fila[1])
        filas_final.append([x, y])
    
    return filas_final

#FUNCIONES RELACIONADAS CON CÁLCULO DE DISTANCIAS
def distancia_promediada(total_filas, n_moscas, mm_px, mm_py, filtro, tiempo_x_fr, frames):
    titulos = [
        "Frame", "Tiempo (seg)", "PosX", "PosY", 
        "Distancia (mm)", "Distancia Acumulada (mm)", 
        "Velocidad (mm/s)", "Aceleracion (mm/s2)"
    ]
    resultado = [[]]

    posicion_mosca = -1
    listado_final = []
    
    #Se recorre la lista mosca por mosca
    for i in range (1, n_moscas+1):
        #print(f"Obteniendo data de mosca {i}")
        #Se obtienen coordenadas de una mosca
        filas = total_filas[i-1]
        #Se obtiene el numero de frames de la mosca - 1
        final = len(filas)-1
        posicion_mosca += 2
        #Se inicia la distancia acumulada
        dist_acumulada = 0
        #Se inicia lista inicial
        listado = []

        #Parametros para contar frames vacios
        data_filas_vacias = []
        coord_inicio = []
        
        #Se recorren las coordenadas desde el inicio hasta el total - 1
        for j in range (0, final): 
            data_actual = filas[j]
            frame1 = int(data_actual[0])
            tiempo = frame1 * tiempo_x_fr
            posX1= float (data_actual[1])
            posY1 = float (data_actual[2])

            data_siguiente = filas[j+1]
            posX2 = float (data_siguiente[1])
            posY2 = float (data_siguiente[2])

            #------------------------------------------------------------------
            #Si el frame NO TIENE DATOS y dato siguiente ESTA VACIO
            if posX1 == 0 and posY1 == 0 and posX2 == 0 and posY2 == 0:
                #Se agregan los datos de frame, tiempo, y coordenadas a una lista
                data_filas_vacias.append([frame1, tiempo, 0, 0])

            #------------------------------------------------------------------
            #Si el frame NO TIENE DATOS y dato siguiente ESTA LLENO
            elif posX1 == 0 and posY1 == 0 and posX2 != 0 and posY2 != 0:
                data_filas_vacias.append([frame1, tiempo, 0, 0])
                coord_final = [posX2, posY2]
                dist_final = calculate_distance(coord_inicio[0],coord_inicio[1],
                                                coord_final[0], coord_final[1],
                                                mm_px,mm_py)
                
                division_distancia = dist_final/(len(data_filas_vacias))
                dist, vel, acel = apply_filter_distance(division_distancia, filtro, tiempo_x_fr)
                for k in range(0, len(data_filas_vacias)):
                    dist_acumulada += dist
                    data_filas_vacias[k].extend([dist, dist_acumulada, vel, acel])
                    listado.append(data_filas_vacias[k])

                data_filas_vacias = []
                coord_inicio = []

            #------------------------------------------------------------------
            #Si frame TIENE DATOS y el dato siguiente ESTA VACIO
            elif posX1 != 0 and posY1 != 0 and posX2 == 0 and posY2 == 0:
                #Se reinician valores para evaluar filas vacias
                coord_inicio = [posX1, posY1]
                #Se agregan los datos de frame, tiempo, y coordenadas a una lista
                data_filas_vacias.append([frame1, tiempo, posX1, posY1])

            #------------------------------------------------------------------
            #Si frame TIENE DATOS y el dato siguiente ESTA LLENO
            elif posX1 != 0 and posY1 != 0 and posX2 != 0 and posY2 != 0:  
                dist = calculate_distance(posX1, posY1, posX2, posY2, mm_px, mm_py)
                dist, vel, acel = apply_filter_distance(dist, filtro, tiempo_x_fr)
                dist_acumulada += dist
                fila_nueva = [frame1, tiempo, posX1, posY1, dist, dist_acumulada, vel, acel]
                listado.append(fila_nueva)
            #------------------------------------------------------------------

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado)
    
    
    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final, frames) 

    print("Terminado!")
    return resultado, listado_final

def distancia(total_filas, n_moscas, mm_px, mm_py, filtro, tiempo_x_fr, frames):
    titulos = [
        "Frame", "Tiempo (seg)", "PosX", "PosY", 
        "Distancia (mm)", "Distancia Acumulada (mm)", 
        "Velocidad (mm/s)", "Aceleracion (mm/s2)"
    ]
    resultado = [[]]
    posicion_mosca = -1
    listado_final = []
    
    #Se recorre la lista mosca por mosca
    for i in range (1, n_moscas+1):
        #print(f"Obteniendo data de mosca {i}")
        #Se obtienen coordenadas de una mosca
        filas = total_filas[i-1]
        #Se obtiene el numero de frames de la mosca - 1
        final = len(filas)-1
        posicion_mosca += 2
        #Se inicia la distancia acumulada
        dist_acumulada = 0
        #Se inicia lista inicial
        listado_inicial = []
        
        #Se recorren las coordenadas desde el inicio hasta el total - 1
        for j in range (final): 
            data_actual = filas[j]
            frame1 = int(data_actual[0])
            posicion_x1= float (data_actual[1])
            posicion_y1 = float (data_actual[2])
            
            tiempo = frame1 * tiempo_x_fr

            data_siguiente = filas[j+1]
            posicion_x2 = float (data_siguiente[1])
            posicion_y2 = float (data_siguiente[2])

            dist = calculate_distance(posicion_x1, posicion_y1, posicion_x2, posicion_y2, mm_px, mm_py)

            dist, vel, acel = apply_filter_distance(dist, filtro, tiempo_x_fr)

            #Se suma distancia a distancias acumuladas
            dist_acumulada += dist
            
            #Se guardan parametros en una lista para agregarlos a la lista inicial
            fila_nueva = [frame1, tiempo, posicion_x1, posicion_y1, 
                          dist, dist_acumulada, vel, acel]
            listado_inicial.append(fila_nueva)

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado_inicial)

    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final, frames)

    #print("Terminado!")
    return resultado, listado_final

def apply_filter_distance (dist, filtro, tiempo_x_fr):
    if dist < filtro:
        dist = 0
        vel = 0
        acel = 0
    else:
        vel = dist/tiempo_x_fr
        acel = vel/tiempo_x_fr
    return dist, vel, acel
