from statistics import mean

def calculate_distance (posX1, posY1, posX2, posY2, mm_px, mm_py):
    #Se calculan las diferencias cuadradas de posiciones
    diferencia_x = ((posX1-posX2)*mm_px)**2
    diferencia_y = ((posY1-posY2)*mm_py)**2
    #Se calcula la distancia
    dist = (diferencia_x + diferencia_y)**0.5
    return dist

def ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final, frames):
    for i in range(0, n_moscas):
        resultado[-1] += titulos
    for i in range (0, frames):
        resultado.append([])

    for j in range (0, n_moscas):
        largo = len(listado_final[j])
        for i in range (0, largo):
            resultado[i+1] += listado_final[j][i]
    
    return resultado

#---------------------------------------------------------------------------------
#Se genera la clase DROSOPHILA (o mosca), la cual almacena:
#Datos de filtros, velocidades, aceleraciones, numero de detenciones,
#  numero de pausas, numero de inicio de movimiento, 
class Drosophila:
    def __init__(self):
        self.speed_with_0 = 0
        self.aceleration_with_0 = 0
        self.speed_without_0 = 0
        self.aceleration_without_0 = 0
        self.speed_with_filter = 0
        self.aceleration_with_filter = 0

        self.number_data_with_0 = 0
        self.number_data_without_0 = 0
        self.number_data_with_filter = 0

        self.moving = False
        self.paused = False
        self.stopped = False

        self.number_moving = 0
        self.number_paused = 0
        self.number_stop = 0

        self.continued_moving = 0
        self.continued_pause = 0
        self.continued_stop = 0

        self.time_moving = 0
        self.time_paused = 0
        self.time_stopped = 0

        self.avg_moving = []
        self.avg_paused = []
        self.avg_stopped = []

        self.avg_speed_with_0 = None
        self.avg_speed_without_0 = None
        self.avg_speed_with_filter = None

        self.avg_acceleration_with_0 = None
        self.avg_acceleration_without_0 = None
        self.avg_acceleration_with_filter = None

    def __str__(self) -> str:
        return f"Drosophila Object"

    def average_data(self):
        if self.number_data_with_0 == 0:
            self.avg_speed_with_0 = 0
            self.avg_acceleration_with_0 = 0
        else: 
            self.avg_speed_with_0 = self.speed_with_0/self.number_data_with_0   
            self.avg_acceleration_with_0 = self.aceleration_with_0/self.number_data_with_0 
        
        if self.number_data_without_0 == 0:
            self.avg_speed_without_0 = 0
            self.avg_acceleration_without_0 = 0
        else: 
            self.avg_speed_without_0 = self.speed_without_0/self.number_data_without_0
            self.avg_acceleration_without_0 = self.aceleration_without_0/self.number_data_without_0
        
        if self.number_data_with_filter == 0:
            self.avg_speed_with_filter = 0
            self.avg_acceleration_with_filter = 0
        else: 
           self.avg_speed_with_filter = self.speed_with_filter/self.number_data_with_filter
           self.avg_acceleration_with_filter = self.aceleration_with_filter/self.number_data_with_filter
        
        self.avg_moving = self.mean_time(self.avg_moving)
        self.avg_paused = self.mean_time(self.avg_paused)
        self.avg_stopped = self.mean_time(self.avg_stopped)

        self.activity = (self.number_data_with_filter / self.number_data_with_0) * 100

        return None
    
    def add_data(self, filter, speed, acel, timexfr):
        self.number_data_with_0 += 1
        self.speed_with_0 += speed
        self.aceleration_with_0 += acel
        #-------------------------------------------------
        #Si la velocidad es mayor a 0, es incluye el dato a las velocidades y aceleraciones que no incluyen 0
        if speed > 0:
           self.speed_without_0 += speed
           self.aceleration_without_0 += acel
           self.number_data_without_0 += 1
        
        #-------------------------------------------------
        #Se determina si la mosca esta detenida ("Detencion" es distinta de "Pausa")        
        if speed == 0:
            #Si la velocidad es 0, se considera Detenida
            self.number_stop += 1
            self.continued_stop += 1

            if self.continued_stop >= 2:
                self.time_stopped += timexfr
            self.stopped = True
    
        elif speed != 0 and self.stopped:
            #Si la velocidad es distinta de 0 y la mosca estaba detenida:
            self.continued_stop = 0
            self.stopped = False

            self.avg_stopped.append(self.time_stopped)
            self.time_stopped = 0   

        #----------------------------------------------------------------------
        #Se determina si la mosca esta pausada ("Pausa" es distinta de "Detencion")

        #Si la mosca está bajo del filtro, se considera en "Pausa"
        if (filter != 0 and speed < filter) or (filter == 0 and speed == 0):
            self.number_paused += 1
            self.continued_pause += 1
            self.paused = True
            self.time_paused += timexfr

            if self.moving:
                #Si la mosca se estaba moviendo pero ahora esta pausada:
                self.continued_moving = 0
                self.continued_moving = False
                self.avg_moving.append (self.time_moving)
                self.time_moving = 0
    
        #Si la mosca está sobre el filtro, se considera en "Movimiento"
        elif (filter != 0 and speed >= filter) or (filter == 0 and speed != 0):
            self.number_data_with_filter += 1

            self.speed_with_filter += speed
            self.aceleration_with_filter += acel
            
            self.number_moving += 1
            self.continued_moving += 1
            self.moving = True
            self.time_moving += timexfr
    
            if self.paused:
                #Si la mosca estaba pausada pero ahora se mueve:
                self.continued_pause = 0
                self.paused = False
                self.avg_paused.append(self.time_paused)
                self.time_paused = 0

    def mean_time (self, lista):
        if lista == []:
            tiempo_promedio = 0
        else:
            tiempo_promedio = mean(lista)
        
        return tiempo_promedio

#---------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON LA GENERACIÓN DE UN ARCHIVO RESUMEN
def calculate_scores (n_rings):
    score_list = []
    if (n_rings%2) == 0:
        if n_rings == 2:
            score_list = [1, 1]
        else:
           half_length = n_rings // 2
           score_list = [half_length] + list(range(half_length - 1, 0, -1)) + list(range(1, half_length + 1))
    elif (n_rings%2) != 0:
        half_length = (n_rings + 1) // 2
        score_list = [abs(half_length - i) for i in range(1, half_length + 1)]
        score_list.extend(score_list[:n_rings // 2][::-1])
        score_list = [x+1 for x in score_list]
    return score_list

def summary(datos_videos, n_moscas, filtro, 
            analizar_centrofobismo, datos_dist_pared,
            analizar_preferencia, datos_preferencia,
            n_ring, datos_social, tiempo_x_fr):
    data_final = [["# Fly", "Travelled Distance (mm)", 
                    "Mean velocity (mm/s)", "Mean velocity, not considering zeros", 
                    f"Mean velocity, considering values higher than {filtro} mm/s", 
                    "Mean acceleration (mm/s2)", "Mean accelaration, not considerging zeros",
                    f"Mean acceleration, considering values higher than {filtro} mm/s", 
                    "Activity %", "Pause bouts frequency", "Average pause time (s)", 
                    "Walking bouts frequency (s)", "Average walking time (s)", 
                    "Detention frequency", "Average Detention time (s)"]]
    
    #Se agregan títulos de centrofobismo
    if analizar_centrofobismo:    
        data_final[0] += ["Centrophobism index"]
        data_final[0] += ["Centrophobism index moving", "Centrophobism index paused"]
        data_final[0] += ["% Time in Center", "% Time in Periphery"]
        ring_scores = calculate_scores(n_ring)
        #print(ring_scores)
    
    #Se agregan títulos de preferencia
    if analizar_preferencia == "Left/Right": 
        data_final[0] += ["Time in left zone", "Time in right zone", "Left preference index", "Right preference index"]
    elif analizar_preferencia == "Top/Bottom":
        data_final[0] += ["Time in top zone", "Time in bottom zone", "Top preference index", "Bottom preference index"]
    
    #Se agregan títulos de sociabilidad
    if n_moscas > 1 and datos_social != []:
        analizar_sociabilidad = True
        data_final[0] += ["Interaction Time (seg)", "Mean Distance to Closest Neighbour", "Mean Distance to all Neighbours"]
    else:
        analizar_sociabilidad = False
    
    #Se recorre cada video
    for j in range (len(datos_videos)):
        mosca_video = 0
        video = datos_videos[j]

        #Se recorre cada mosca del video
        for k in range (len(video)):
            mosca_video += 1
            data_mosca = video[k]

            #Se genera objeto Drosophila
            fly = Drosophila()

            #Parametros centrofobismo
            cf_periphery = 0
            cf_center = 0
            fr_periphery = 0
            fr_center = 0
            cf_periphery_moving = 0
            cf_center_moving = 0
            cf_center_pause = 0
            cf_periphery_pause = 0

            #Parametros preferencia
            pf_left = 0
            pf_right = 0
            pf_top = 0
            pf_bottom = 0

            #Parametros social
            time_interaction = 0
            distances_closest_neighbour = []
            distances_all_neighbours = []
            
            #Se recorren las coordenadas de la mosca particular 
            for i in range (0, len(data_mosca)):
                data_actual = data_mosca[i]
                velocidad = float(data_actual[6])
                aceleracion = float(data_actual[7])

                #Se evalua tiempo de interaccion
                #Si la distancia entre la mosca y otra es menor a 3 mm, se suma tiempo de interaccion
                if analizar_sociabilidad: 
                   dict_dist_between_flies = datos_social[j]
                   dist_between_flies_per_frame = dict_dist_between_flies[i+1]

                   dist_all_neighbours = dist_between_flies_per_frame[k]
                   dist_all_neighbours.pop(k)
                   dist_closest_neighbour = min(dist_all_neighbours)
                   
                   distances_closest_neighbour.append(dist_closest_neighbour)
                   distances_all_neighbours.extend(dist_all_neighbours)

                   if dist_closest_neighbour <= 3:
                       time_interaction += tiempo_x_fr
                
                #Se evalua centrobismo
                if analizar_centrofobismo:
                    score_cf = int(datos_dist_pared[j][k][i][3])
                    if (n_ring%2) == 0:
                        if score_cf < (n_ring/2):
                            fr_center += 1
                            cf_center += ring_scores[score_cf]
                            if (filtro != 0 and velocidad < filtro) or (filtro == 0 and velocidad == 0):
                                cf_center_pause += ring_scores[score_cf]
                            elif (filtro != 0 and velocidad >= filtro) or (filtro == 0 and velocidad != 0):
                                cf_center_moving += ring_scores[score_cf]
                        elif score_cf >= (n_ring/2):
                            fr_periphery += 1
                            cf_periphery += ring_scores[score_cf]
                            if (filtro != 0 and velocidad < filtro) or (filtro == 0 and velocidad == 0):
                                cf_periphery_pause += ring_scores[score_cf]
                            elif (filtro != 0 and velocidad >= filtro) or (filtro == 0 and velocidad != 0):
                                cf_periphery_moving += ring_scores[score_cf]
    
                    elif (n_ring%2) != 0:
                        if score_cf <= ((n_ring//2)+1):
                            fr_center += 1
                            cf_center += ring_scores[score_cf]
                            if (filtro != 0 and velocidad < filtro) or (filtro == 0 and velocidad == 0):
                                cf_center_pause += ring_scores[score_cf]
                            elif (filtro != 0 and velocidad >= filtro) or (filtro == 0 and velocidad != 0):
                                cf_center_moving += ring_scores[score_cf]
                        elif score_cf > (n_ring//2+1):
                            fr_periphery += 1
                            cf_periphery += ring_scores[score_cf]
                            if (filtro != 0 and velocidad < filtro) or (filtro == 0 and velocidad == 0):
                                cf_periphery_pause += ring_scores[score_cf]
                            elif (filtro != 0 and velocidad >= filtro) or (filtro == 0 and velocidad != 0):
                                cf_periphery_moving += ring_scores[score_cf]
                            
                #Se evalua preferencia
                if analizar_preferencia == "Left/Right":
                    if datos_preferencia[j][k][i][2] == "Left":
                        pf_left += tiempo_x_fr
                    elif datos_preferencia[j][k][i][2] == "Right":
                        pf_right += tiempo_x_fr
                elif analizar_preferencia == "Top/Bottom":
                    if datos_preferencia[j][k][i][2] == "Top":
                        pf_top += tiempo_x_fr
                    elif datos_preferencia[j][k][i][2] == "Bottom":
                        pf_bottom += tiempo_x_fr

                fly.add_data(filter=filtro, speed=velocidad, acel=aceleracion, timexfr=tiempo_x_fr)

            fly.average_data()
            dist_final = data_mosca[-1][5]

            data_agregar = [mosca_video, dist_final,
                            fly.avg_speed_with_0, fly.avg_speed_without_0, fly.avg_speed_with_filter, 
                            fly.avg_acceleration_with_0, fly.avg_acceleration_without_0, fly.avg_acceleration_with_filter, 
                            fly.activity, fly.number_paused, fly.avg_paused, 
                            fly.number_moving, fly.avg_moving,
                            fly.number_stop, fly.avg_stopped]
        
            #Se evalua centrofobismo
            if analizar_centrofobismo:
                cf_index = (cf_periphery-cf_center)/ (cf_center+cf_periphery)
                if cf_center_moving+cf_periphery_moving != 0:
                    cf_index_moving = (cf_periphery_moving-cf_center_moving)/ (cf_center_moving+cf_periphery_moving)
                else:
                    cf_index_moving = "Can't be calculated"
                cf_index_pause = (cf_periphery_pause-cf_center_pause)/ (cf_center_pause+cf_periphery_pause)
                fr_center_fraction = fr_center/(fr_center+fr_periphery)*100
                fr_periphery_fraction = fr_periphery/(fr_center+fr_periphery)*100
                data_agregar += [cf_index, cf_index_moving, cf_index_pause, fr_center_fraction, fr_periphery_fraction]

            #Se evalua preferencia
            if analizar_preferencia == "Left/Right":
                pf_left_index = pf_left/(pf_left+pf_right)
                pf_right_index = pf_right/(pf_left+pf_right)
                data_agregar += [pf_left, pf_right, pf_left_index, pf_right_index]
            elif analizar_preferencia == "Top/Bottom":
                pf_top_index = pf_top/(pf_bottom+pf_top)
                pf_bottom_index = pf_bottom/(pf_bottom+pf_top)
                data_agregar += [pf_top, pf_bottom, pf_top_index, pf_bottom_index]

            #Se evalua sociabilidad
            if analizar_sociabilidad:
                mean_dist_closest_neighbour = mean(distances_closest_neighbour)
                mean_dist_all_neighbour = mean(distances_all_neighbours)
                data_agregar += [time_interaction, mean_dist_closest_neighbour, mean_dist_all_neighbour]
    
            data_final.append(data_agregar)  

    return data_final