
from statistics import mean
# OTRAS FUNCIONES 
def ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final):
    for i in range(0, n_moscas):
        resultado[-1] += titulos
    for i in range (0, 1200):
        resultado.append([])

    for j in range (0, n_moscas):
        largo = len(listado_final[j])
        for i in range (0, largo):
            resultado[i+1] += listado_final[j][i]
    
    return resultado

def calcular_distancia (posX1, posY1, posX2, posY2, mm_px, mm_py):
    #Se calculan las diferencias cuadradas de posiciones
    diferencia_x = ((posX1-posX2)*mm_px)**2
    diferencia_y = ((posY1-posY2)*mm_py)**2
    #Se calcula la distancia
    dist = (diferencia_x + diferencia_y)**0.5
    return dist

#FUNCIONES RELACIONADAS CON CÁLCULO DE DISTANCIAS
def distancia_promediada(total_filas, n_moscas, mm_px, mm_py, filtro):
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
            tiempo = frame1 * 0.2857
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
                dist_final = calcular_distancia(coord_inicio[0],coord_inicio[1],
                                                coord_final[0], coord_final[1],
                                                mm_px,mm_py)
                
                division_distancia = dist_final/(len(data_filas_vacias))
                dist, vel, acel = aplicar_filtro_distancia(division_distancia, filtro)
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
                dist = calcular_distancia(posX1, posY1, posX2, posY2, mm_px, mm_py)
                dist, vel, acel = aplicar_filtro_distancia(dist, filtro)
                dist_acumulada += dist
                fila_nueva = [frame1, tiempo, posX1, posY1, dist, dist_acumulada, vel, acel]
                listado.append(fila_nueva)
            #------------------------------------------------------------------

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado)
    
    
    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final) 

    print("Terminado!")
    return resultado, listado_final

def distancia(total_filas, n_moscas, mm_px, mm_py, filtro):

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
            
            tiempo = frame1 * 0.2857

            data_siguiente = filas[j+1]
            posicion_x2 = float (data_siguiente[1])
            posicion_y2 = float (data_siguiente[2])

            dist = calcular_distancia(posicion_x1, posicion_y1, posicion_x2, posicion_y2, mm_px, mm_py)

            dist, vel, acel = aplicar_filtro_distancia(dist, filtro)

            #Se suma distancia a distancias acumuladas
            dist_acumulada += dist
            
            #Se guardan parametros en una lista para agregarlos a la lista inicial
            fila_nueva = [frame1, tiempo, posicion_x1, posicion_y1, 
                          dist, dist_acumulada, vel, acel]
            listado_inicial.append(fila_nueva)

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado_inicial)

    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final)

    print("Terminado!")
    return resultado, listado_final

def aplicar_filtro_distancia (dist, filtro):
    #Se calula distancias con filtro si es necesario
    if filtro[0]:
        if dist < filtro[1]:
            dist = 0
            vel = 0
            acel = 0
        else:
            vel = dist/0.2857
            acel = dist/((0.2857)**2)
    #Si no hay filtro, se calcula velocidad y aceleracion sin restricciones
    else:
        vel = dist/0.2857
        acel = dist/((0.2857)**2)
    return dist, vel, acel

#FUNCIONES RELACIONADAS CON LA GENERACIÓN DE UN ARCHIVO RESUMEN
def aplicar_filtro_velocidad (filtro, aceleracion, velocidad, tiempo,
                              avg_acel, avg_acel_filtro,
                              avg_vel, avg_vel_filtro,
                              length_no0, length_filt, fr_actividad,
                              mosca_detenida, tiempo_detencion, tiempos_detencion, n_detentions, n_detentions_seguido,
                              mosca_pausada, tiempo_pause, tiempos_pause, n_pause, n_pause_seguido,
                              mosca_moving, tiempo_moving, tiempos_moving, n_moving, n_moving_seguido):

    if velocidad > 0:
        avg_acel += aceleracion
        avg_vel += velocidad
        length_no0 +=1
    #-------------------------------------------------
    #Se determina si la mosca esta detenida ("Detencion" es distinta de "Pausa")
    if velocidad == 0:
        #Si la velocidad es 0, se considera Detenida
        n_detentions += 1
        n_detentions_seguido += 1
        if n_detentions_seguido >= 2:
            tiempo_detencion += tiempo
        mosca_detenida = True

    elif velocidad != 0 and mosca_detenida:
        #Si la velocidad es distinta de 0 y la mosca estaba detenida:
        n_detentions_seguido = 0
        mosca_detenida = False
        tiempos_detencion.append(tiempo_detencion)
        tiempo_detencion = 0
        
    #----------------------------------------------------------------------
    #Se determina si la mosca esta pausada ("Pausa" es distinta de "Detencion")
    
    #Si la mosca está bajo del filtro, se considera en "Pausa"
    if velocidad < filtro:
        n_pause += 1
        n_pause_seguido += 1
        mosca_pausada = True
        tiempo_pause += tiempo

        if mosca_moving:
            #Si la mosca se estaba moviendo pero ahora esta pausada:
            n_moving_seguido = 0
            mosca_moving = False
            tiempos_moving.append(tiempo_moving)
            tiempo_moving = 0

    #Si la mosca está sobre el filtro, se considera en "Movimiento"
    elif velocidad >= filtro:
        n_moving += 1
        n_moving_seguido += 1
        mosca_moving = True
        tiempo_moving += 1

        if mosca_pausada:
            #Si la mosca estaba pausada pero ahora se mueve:
            n_pause_seguido = 0
            mosca_pausada = False
            tiempos_pause.append(tiempo_pause)
            tiempo_pause = 0

        avg_acel += aceleracion
        avg_acel_filtro += aceleracion
        avg_vel += velocidad
        avg_vel_filtro += velocidad
        length_filt += 1
        length_no0 += 1
        fr_actividad += 1

    #--------------------------------------------------------
    
    res= [
        avg_acel, avg_acel_filtro, avg_vel, avg_vel_filtro,
        length_no0, length_filt, fr_actividad, 
        mosca_detenida, tiempo_detencion, tiempos_detencion, n_detentions, n_detentions_seguido,
        mosca_pausada, tiempo_pause, tiempos_pause, n_pause, n_pause_seguido,
        mosca_moving, tiempo_moving, tiempos_moving, n_moving, n_moving_seguido
        ]

    return res 

def summary(datos_videos, n_moscas, filtro, 
            datos_dist_pared, coord_ROI,
            analizar_preferencia, datos_preferencia,
            n_ring, datos_social):
    data_final = [["# Fly", "Travelled Distance (mm)", 
                    "Mean velocity (mm/s)", "Mean velocity, not considering zeros", 
                    f"Mean velocity, considering values higher than {filtro} mm/s", 
                    "Mean acceleration (mm/s2)", "Mean accelaration, not considerging zeros",
                    f"Mean acceleration, considering values higher than {filtro} mm/s", 
                    "Activity %", "Pause bouts frequency", "Average pause time (s)", 
                    "Walking bouts frequency (s)", "Average walking time (s)", 
                    "Detention frequency", "Average Detention time (s)"]]
    
    data_final[0] += ["Center Score", "Periphery Score", "Centrophobism index"]
    data_final[0] += ["Centrophobism index moving", "Centrophobism index paused"]

    ring_scores = calculate_scores(n_ring)
    print(ring_scores)

    if analizar_preferencia: 
        data_final[0] += ["Time in left zone", "Time in right zone", "Left preference index", "Right preferencia index"]

    if n_moscas > 3 and datos_social != []:
        analizar_sociabilidad = True
        data_final[0] += ["Tiempo interaccion"]
    else:
        analizar_sociabilidad = False

    print(len(datos_videos), len(datos_social))

    for j in range (len(datos_videos)):
        mosca_video = 0
        video = datos_videos[j]
        print(len(datos_videos[j]), len(datos_social[j]))


        #Se recorre cada mosca del video
        for k in range (len(video)):
            mosca_video += 1
            data_mosca = video[k]

            avg_vel_0 = 0
            avg_vel = 0
            avg_vel_filtro = 0
            avg_acel_0 = 0
            avg_acel = 0
            avg_acel_filtro = 0
            
            mosca_detenida = False
            n_detentions = 0
            n_detentions_seguido = 0
            tiempos_detencion = []
            tiempo_detencion = 0

            mosca_pausada = False
            n_pause = 0
            n_pause_seguido = 0
            tiempos_pause = []
            tiempo_pause = 0

            mosca_moving= False
            n_moving= 0
            n_moving_seguido = 0
            tiempos_moving = []
            tiempo_moving = 0

            fr_actividad = 0

            length_no0 = 0
            length_filt = 0

            #Parametros centrofobismo
            cf_periphery = 0
            cf_center = 0
            cf_periphery_moving = 0
            cf_center_moving = 0
            cf_center_pause = 0
            cf_periphery_pause = 0

            #Parametros preferencia
            pf_left = 0
            pf_right = 0

            #Parametros social
            time_interaction = 0
            
            #Se recorren las coordenadas de la mosca particular 
            for i in range (0, len(data_mosca)):
                data_actual = data_mosca[i]
                velocidad = float(data_actual[6])
                aceleracion = float(data_actual[7])
                tiempo = 0.2857


                #Se evalua tiempo de interaccion
                #Si la distancia entre la mosca y otra es menor a 3 mm, se suma tiempo de interaccion
                if analizar_sociabilidad and i != 0: 
                   social_mosca_coordenada = datos_social[j][k][i-1]
                   print(social_mosca_coordenada)
                   dist_social = social_mosca_coordenada[2]
                   if dist_social < 3:
                       time_interaction += tiempo

                
                #Se evalua centrobismo
                score_cf = int(datos_dist_pared[j][k][i][3])
                if (n_ring%2) == 0:
                    if score_cf < (n_ring/2):
                        cf_center += ring_scores[score_cf]
                        if velocidad < filtro:
                            cf_center_pause += ring_scores[score_cf]
                        elif velocidad >= filtro:
                            cf_center_moving += ring_scores[score_cf]
                    elif score_cf >= (n_ring/2):
                        cf_periphery += ring_scores[score_cf]
                        if velocidad < filtro:
                            cf_periphery_pause += ring_scores[score_cf]
                        elif velocidad >= filtro:
                            cf_periphery_moving += ring_scores[score_cf]

                elif (n_ring%2) != 0:
                    if score_cf <= ((n_ring//2)+1):
                        cf_center += ring_scores[score_cf]
                        if velocidad < filtro:
                            cf_center_pause += ring_scores[score_cf]
                        elif velocidad >= filtro:
                            cf_center_moving += ring_scores[score_cf]
                    elif score_cf > (n_ring//2+1):
                        cf_periphery += ring_scores[score_cf]
                        if velocidad < filtro:
                            cf_periphery_pause += ring_scores[score_cf]
                        elif velocidad >= filtro:
                            cf_periphery_moving += ring_scores[score_cf]
                
                
                #Se evalua preferencia
                if analizar_preferencia:
                    if datos_preferencia[j][k][i][2] == "Left":
                        pf_left += tiempo
                    elif datos_preferencia[j][k][i][2] == "Right":
                        pf_right += tiempo

                avg_acel_0 += aceleracion
                avg_vel_0 += velocidad

                resultado = aplicar_filtro_velocidad (
                    filtro, aceleracion, velocidad, tiempo,
                    avg_acel, avg_acel_filtro,
                    avg_vel, avg_vel_filtro,
                    length_no0, length_filt, fr_actividad,
                    mosca_detenida, tiempo_detencion, tiempos_detencion, n_detentions, n_detentions_seguido,
                    mosca_pausada, tiempo_pause, tiempos_pause, n_pause, n_pause_seguido,
                    mosca_moving, tiempo_moving, tiempos_moving, n_moving, n_moving_seguido
                    )
                
                avg_acel = resultado[0]
                avg_acel_filtro = resultado[1]
                avg_vel = resultado[2]
                avg_vel_filtro = resultado[3]
                length_no0 = resultado[4]
                length_filt = resultado[5]
                fr_actividad = resultado[6]
                mosca_detenida = resultado[7]
                tiempo_detencion = resultado[8]
                tiempos_detencion = resultado[9]
                n_detentions = resultado[10]
                n_detentions_seguido = resultado[11]
                mosca_pausada = resultado[12]
                tiempo_pause = resultado[13]
                tiempos_pause = resultado[14]
                n_pause = resultado[15]
                n_pause_seguido = resultado[16]
                mosca_moving = resultado[17]
                tiempo_moving = resultado[18]
                tiempos_moving = resultado[19]
                n_moving = resultado[20]
                n_moving_seguido = resultado[21]

            avg_acel_0 /= (len(data_mosca))
            avg_vel_0 /= (len(data_mosca))

            if length_no0 == 0:
                avg_acel = 0
                avg_vel = 0
            else:
                avg_acel /= length_no0
                avg_vel /= length_no0

            if length_filt == 0:
                avg_acel_filtro = 0
                avg_vel_filtro = 0
            else:
                avg_acel_filtro /= length_filt
                avg_vel_filtro /= length_filt

            actividad = (fr_actividad/(len(data_mosca)))*100

            detencion_promedio = mean_time(tiempos_detencion) 
            pausa_promedio = mean_time(tiempos_pause)
            moving_promedio = mean_time(tiempos_moving)
            dist_final = data_mosca[-1][5]

            data_agregar = [mosca_video, dist_final,
                              avg_vel_0, avg_vel, avg_acel_filtro,
                              avg_acel_0, avg_acel, avg_acel_filtro,
                              actividad, 
                              n_pause, pausa_promedio, n_moving, moving_promedio,
                              n_detentions, detencion_promedio]
        
            #Se evalua centrofobismo
            cf_index = (cf_periphery-cf_center)/ (cf_center+cf_periphery)
            cf_index_moving = (cf_periphery_moving-cf_center_moving)/ (cf_center_moving+cf_periphery_moving)
            cf_index_pause = (cf_periphery_pause-cf_center_pause)/ (cf_center_pause+cf_periphery_pause)
            data_agregar += [cf_center, cf_periphery, cf_index, cf_index_moving, cf_index_pause]

            #Se evalua sociabilidad
            if analizar_sociabilidad:
                data_agregar += [time_interaction]
            
            #Se evalua preferencia
            if analizar_preferencia:
                pf_left_index = pf_left/(pf_left+pf_right)
                pf_right_index = pf_right/(pf_left+pf_right)
                data_agregar += [pf_left, pf_right, pf_left_index, pf_right_index]
    
            data_final.append(data_agregar)  

    return data_final




def mean_time (lista):
    if lista == []:
        tiempo_promedio = 0
    else:
        tiempo_promedio = mean(lista)
    
    return tiempo_promedio

def calculate_scores (n_rings):
    score_list = []
    if (n_rings%2) == 0:
        print("Numero par!")
        if n_rings == 2:
            score_list = [1, 1]
        else:
           half_length = n_rings // 2
           score_list = [half_length] + list(range(half_length - 1, 0, -1)) + list(range(1, half_length + 1))
    elif (n_rings%2) != 0:
        print("Numero impar!")
        half_length = (n_rings + 1) // 2
        score_list = [abs(half_length - i) for i in range(1, half_length + 1)]
        score_list.extend(score_list[:n_rings // 2][::-1])
        score_list = [x+1 for x in score_list]
    return score_list


