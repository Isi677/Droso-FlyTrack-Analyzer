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
        




