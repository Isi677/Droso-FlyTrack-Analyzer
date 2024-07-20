from functions_analysis_general import calculate_distance

#FUNCIONES DE SOCIABILIDAD
def calculate_distance_between_flies(points, mm_px, mm_py):
    #Se obtiene el número de puntos/moscas
    num_points = len(points)
    #Creacion de lista con listas de de 5 elementos, siendo estos elementos valores = 0
    distances = [[0] * num_points for _ in range(num_points)]
    #Por cada punto
    for i in range(num_points):
        for j in range(i + 1, num_points):
            dist = calculate_distance(points[i][0], points[i][1], points[j][0], points[j][1], mm_px, mm_py)
            distances[i][j] = distances[j][i] = dist
    return distances

def interaction(total_filas, mm_px, mm_py):
    n_flies = len(total_filas)    
    d = {}
    d1 = {}

    #Transformar lista de listas en dict, donde la llave corresponde al frame y contenido es una lista de listas con coordenadas de cada mosca en dicho frame
    for i in range(len(total_filas[0])):
        d[total_filas[0][i][0]] = []

    for i in range(n_flies):
        for frame in d:
            d[frame].append(total_filas[i][frame-1][1:])

    #Construir un segundo dict, en donde cada frame es una llave 
    #Y el contenido es una lista de listas con las distancias entre cada mosca
    for frame in d:
        distancias_entre_moscas = calculate_distance_between_flies(d[frame], mm_px, mm_py)
        d1[frame] = distancias_entre_moscas

    return d1
