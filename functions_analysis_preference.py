from functions_analysis_general import ordenar_datos_para_exc

def preference(total_filas, coord_circulo, n_moscas, tiempo, frames, formato): 
    if formato == "Left/Right":
        resultado, listado_final = preference_left_right(
            total_filas=total_filas, coord_circulo=coord_circulo, 
            n_moscas=n_moscas, tiempo_x_fr=tiempo, frames=frames
            )
    elif formato == "Top/Bottom":
        resultado, listado_final = preference_up_down(
            total_filas=total_filas, coord_circulo=coord_circulo, 
            n_moscas=n_moscas, tiempo_x_fr=tiempo, frames=frames
        )
    print("Terminado!")
    return resultado, listado_final    

def preference_left_right(total_filas, coord_circulo, n_moscas, tiempo_x_fr, frames):
    import numpy as np
    import math
    titulos = ["Frame", "Tiempo (seg)", "Preference"]
    resultado = [[]]

    posicion_mosca = -1
    listado_final = []

    #Se obtiene array de coordenadas de circulo
    array = []
    for k in range(0, len(coord_circulo)):
        coord_actual = coord_circulo[k]
        x_c = float(coord_actual[0])
        y_c = float(coord_actual[1])
        array.append([x_c, y_c])
    nodes = np.array(array)

    # Encuentra el índice del valor mínimo en la columna 'x'.
    indice_valor_min_x = np.argmin(nodes[:, 0])
    # Obtiene el valor mínimo de 'x' y su valor correspondiente de 'y'.
    valor_min_x = nodes[indice_valor_min_x, 0]
    valor_min_y = nodes[indice_valor_min_x, 1]
    coord_izq = [valor_min_x, valor_min_y]

    # Encuentra el índice del valor máximo en la columna 'x'.
    indice_valor_max_x = np.argmax(nodes[:, 0])
    # Obtiene el valor máximo de 'x' y su valor correspondiente de 'y'.
    valor_max_x = nodes[indice_valor_max_x, 0]
    valor_max_y = nodes[indice_valor_max_x, 1]
    coord_der = [valor_max_x, valor_max_y]

    #Se recorre la lista mosca por mosca
    for i in range (1, n_moscas+1):
        #Se obtienen coordenadas de una mosca
        filas = total_filas[i-1]

        #Se obtiene el numero de frames de la mosca 
        final = len(filas)
        posicion_mosca += 2
        listado_inicial = []

        #Se recorren las coordenadas desde el inicio hasta el total
        for j in range (final): 
            data_actual = filas[j]
            x = float(data_actual[1])
            y = float(data_actual[2])

            frame = int(data_actual[0])
            tiempo = frame * tiempo_x_fr

            node = (x, y)

            # Calcula la distancia entre el tercer punto y los dos puntos de referencia
            dist_izq = math.sqrt((coord_izq[0] - node[0])**2 + (coord_izq[1] - node[1])**2)
            dist_der = math.sqrt((coord_der[0] - node[0])**2 + (coord_der[1] - node[1])**2)
            
            # Compara las distancias para determinar cuál es más cercano
            if dist_izq < dist_der:
                preference = "Left"
            elif dist_der < dist_izq:
                preference = "Right"
            else:
                preference = "Tie"

            #Se guardan parametros en una lista para agregarlos a la lista inicial
            fila_nueva = [frame, tiempo, preference]
            listado_inicial.append(fila_nueva)

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado_inicial)

    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final, frames)

    return resultado, listado_final

def preference_up_down(total_filas, coord_circulo, n_moscas, tiempo_x_fr, frames):
    import numpy as np
    import math
    titulos = ["Frame", "Tiempo (seg)", "Preference"]
    resultado = [[]]

    posicion_mosca = -1
    listado_final = []

    #Se obtiene array de coordenadas de circulo
    array = []
    for k in range(0, len(coord_circulo)):
        coord_actual = coord_circulo[k]
        x_c = float(coord_actual[0])
        y_c = float(coord_actual[1])
        array.append([x_c, y_c])
    nodes = np.array(array)

    # Encuentra el índice del valor mínimo en la columna 'y'.
    indice_valor_min_y = np.argmin(nodes[:, 1])
    # Obtiene el valor mínimo de 'y' y su valor correspondiente de 'x'.
    valor_min_x = nodes[indice_valor_min_y, 0]
    valor_min_y = nodes[indice_valor_min_y, 1]
    coord_sup = [valor_min_x, valor_min_y]

    # Encuentra el índice del valor máximo en la columna 'y'.
    indice_valor_max_y = np.argmax(nodes[:, 1])
    # Obtiene el valor máximo de 'y' y su valor correspondiente de 'x'.
    valor_max_x = nodes[indice_valor_max_y, 0]
    valor_max_y = nodes[indice_valor_max_y, 1]
    coord_inf = [valor_max_x, valor_max_y]

    #Se recorre la lista mosca por mosca
    for i in range (1, n_moscas+1):
        #Se obtienen coordenadas de una mosca
        filas = total_filas[i-1]

        #Se obtiene el numero de frames de la mosca 
        final = len(filas)
        posicion_mosca += 2
        listado_inicial = []

        #Se recorren las coordenadas desde el inicio hasta el total
        for j in range (final): 
            data_actual = filas[j]
            x = float(data_actual[1])
            y = float(data_actual[2])

            frame = int(data_actual[0])
            tiempo = frame * tiempo_x_fr

            node = (x, y)

            # Calcula la distancia entre el tercer punto y los dos puntos de referencia
            dist_sup = math.sqrt((coord_sup[0] - node[0])**2 + (coord_sup[1] - node[1])**2)
            dist_inf = math.sqrt((coord_inf[0] - node[0])**2 + (coord_inf[1] - node[1])**2)
            
            # Compara las distancias para determinar cuál es más cercano
            if dist_sup < dist_inf:
                preference = "Top"
            elif dist_inf < dist_sup:
                preference = "Bottom"
            else:
                preference = "Tie"

            #Se guardan parametros en una lista para agregarlos a la lista inicial
            fila_nueva = [frame, tiempo, preference]
            listado_inicial.append(fila_nueva)

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado_inicial)

    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final, frames)

    return resultado, listado_final