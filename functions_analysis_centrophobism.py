from functions_analysis_general import calculate_distance, ordenar_datos_para_exc

def closest_node(node, nodes):
    from scipy.spatial import distance
    return nodes[distance.cdist([node], nodes).argmin()]

def calculate_radius(roi_boundary_points):
    import math
    # Se calcula el centro del ROI
    x_sum = sum(x for x, y in roi_boundary_points)
    y_sum = sum(y for x, y in roi_boundary_points)
    center_x = x_sum / len(roi_boundary_points)
    center_y = y_sum / len(roi_boundary_points)
    
    # Se calcula la distancia del centro respecto a puntos del borde
    distances = [math.sqrt((x - center_x)**2 + (y - center_y)**2) for x, y in roi_boundary_points]
    roi_radius = max(distances)
    
    return roi_radius

def find_arena_center(roi_coordinates):
    avg_x = sum(x for x, _ in roi_coordinates) / len(roi_coordinates)
    avg_y = sum(y for _, y in roi_coordinates) / len(roi_coordinates)

    return avg_x, avg_y

def classify_point_in_ring(x, y, rings, center):
    import math
    center_x, center_y = center

    # Calculate the distance from the origin (center of the arena) to the point
    point_distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)

    # Calculate the distances from the center to each ring
    ring_distances = [math.sqrt((ring[0][0] - center_x)**2 + (ring[0][1] - center_y)**2) for ring in rings]

    # Find the ring that the point is closest to
    closest_ring = min(range(len(ring_distances)), key=lambda i: abs(ring_distances[i] - point_distance))

    return closest_ring

def generate_equal_area_rings(arena_center, arena_radius, num_rings):
    import math

    ring_coordinates = []

    # Calculate the area of the circular arena
    arena_area = math.pi * arena_radius**2

    # Calculate the area of each ring
    target_ring_area = arena_area / num_rings

    for i in range(1, num_rings + 1):  # Start from 1 to exclude the center
        # Use the formula to calculate the radius of the current ring
        current_ring_area = target_ring_area * i
        current_ring_radius = math.sqrt(current_ring_area / math.pi)

        current_ring_circumference = 2 * math.pi * current_ring_radius
        num_points = int(current_ring_circumference)

        # Generate coordinates for the ring
        ring_points = []
        for j in range(num_points):
            angle = 2 * math.pi * j / num_points
            x = arena_center[0] + current_ring_radius * math.cos(angle)
            y = arena_center[1] + current_ring_radius * math.sin(angle)
            ring_points.append((x, y))
        
        ring_coordinates.append(ring_points)

    return ring_coordinates
    
def plot_rings(ring_coordinates, arena_radius):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='datalim')

    # Plot the circular arena
    #arena_circle = plt.Circle((0, 0), arena_radius, fill=False, color='b')
    #ax.add_patch(arena_circle)

    for i, ring_points in enumerate(ring_coordinates):
        x = [point[0] for point in ring_points]
        y = [point[1] for point in ring_points]

        # Plot each ring
        plt.plot(x, y, label=f'Ring {i}')

    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.title('Equal-Area Rings')
    plt.legend()
    plt.grid(True)
    plt.show()

#----------------------------------------------------------------------------------------------------
def distance_from_wall(total_filas, coord_circulo, n_moscas, mm_px, mm_py, n_anillos, tiempo_x_fr, frames):
    import numpy as np
    titulos = ["Frame", "Tiempo (seg)", "Distancia Pared", "Anillo"]
    resultado = [[]]

    posicion_mosca = -1
    listado_final = []

    #Se obtiene array de coordenadas de circulo
    x_array = []
    y_array = []
    
    for k in range(0, len(coord_circulo)):
        coord_actual = coord_circulo[k]
        x_c = float(coord_actual[0])
        y_c = float(coord_actual[1])
        x_array.append(x_c)
        y_array.append(y_c)
    nodes = np.column_stack((x_array, y_array))

    radio_arena = calculate_radius(coord_circulo)
    centro_arena = find_arena_center(coord_circulo)
    ring_coords = generate_equal_area_rings(centro_arena, radio_arena, n_anillos)
    #plot_rings(ring_coords, radio_arena)


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

            anillo = classify_point_in_ring(x, y, ring_coords, centro_arena)

            node = (x, y)

            idx, idy = closest_node(node, nodes)
            min_dist = calculate_distance(x, y, idx, idy, mm_px, mm_py)
            #Se guardan parametros en una lista para agregarlos a la lista inicial
            fila_nueva = [frame, tiempo, min_dist, anillo]
            listado_inicial.append(fila_nueva)

        #Se añade lista (representa una mosca) a lista final (todas las moscas)
        listado_final.append(listado_inicial)
    
    resultado = ordenar_datos_para_exc(resultado, titulos, n_moscas, listado_final, frames)

    print("Terminado!")
    return resultado, listado_final  
