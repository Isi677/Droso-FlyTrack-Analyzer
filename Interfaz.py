import tkinter as tk
from tkinter import filedialog, ttk
from threading import Thread, Event
from extractor_locomotor_main import main_backend

#--------------------------------
# Funciones si valor entregado es valido para analisis
def validate_int_number(value, threshold):
    return value.isdigit() and int(value) >= threshold
    
def validate_float_number(value):
    try:
        return float(value) >= 0
    except ValueError:
        return False
#--------------------------------
#Funciones que fuerzan al usuario a solo colocar ciertos valores en las casillas
def validate_int(value):
    return (value.isdigit() and 1 <= int(value) <= 10) or value == ""
def validate_numbers(value):
    return value.isdigit() and int(value) >= 1 or value == ""
def validate_rings_number(value):
    return value.isdigit() and int(value) >= 1 or value == ""
def validate_thresholds(value):
    if value == "":
        return True
    try:
        return float(value) >= 0
    except ValueError:
        return False

def validate_string(str):
    banned_characters = ["/", '\"', ":", "*", "?", '\\', "|", "<", ">", ".", ";", ","]
    for c in banned_characters:
        if c in str:
            return False
    return True
#---------------------------------------------------------------------------
# Función para seleccionar archivos excels de coordenadas
def select_files():
    filepaths = filedialog.askopenfilenames(title="Select Files", filetypes=[("Excel Files", "*.xlsx")])
    for filepath in filepaths:
        if filepath not in Lista_cute:
            Lista_cute.append(filepath)
            tree.insert("", tk.END, values=(filepath, ""))
    update_buttons()

# Función para eliminar archivos excels de coordenadas seleccionados por el usuario
def delete_files():
    selected_items = tree.selection()
    for item in selected_items:
        filepath = tree.item(item, "values")[0]
        if filepath in Lista_cute:
            Lista_cute.remove(filepath)
        tree.delete(item)
    update_buttons()

# Función para añadir, con la info entregada, un grupo de archivos xlsx de videos de moscas bajo un nombre de grupo definido por usuario
def add_group_files():
    group_name = name_entry.get()
    # Se evalúa si hay archivos excels seleccionados + nombre de grupo
    if Lista_cute and group_name:
        excels_coordenadas[group_name] = [[tree.item(item, "values")[0], int(tree.item(item, "values")[1])] for item in tree.get_children()]
        listbox_right.insert(tk.END, f"{group_name}")
        Lista_cute.clear()
        tree.delete(*tree.get_children())
        name_entry.delete(0, tk.END) 
    else:
        print("No hay archivos seleccionados o nombre ingresado.")
    update_buttons()

# Funcion para eliminar grupos seleccionados de archivos
def delete_selected_right():
    selected_indices = listbox_right.curselection()
    for i in selected_indices[::-1]:
        name = listbox_right.get(i)
        if name in excels_coordenadas:
            del excels_coordenadas[name]
        listbox_right.delete(i)
    print(excels_coordenadas)
    update_buttons()

# Función para crear los radiobuttons y asociar el evento de cambio
def create_radiobuttons(frame):
    options = ["No", "Left/Right", "Top/Bottom", "Quadrants"]
    for index, option in enumerate(options):
        rb = tk.Radiobutton(frame, text=option, variable=selected_option, value=index, command=update_buttons)
        rb.grid(row=3, column=1 + index, padx=5, pady=5)

# Funcion que actualiza disponibilidad de botones "Analyze" y "Delete"
def update_buttons():
    all_have_numbers = all(tree.item(item, "values")[1] for item in tree.get_children())
    numberframe_valid = validate_int_number(numberframes_entry.get(), 1)
    video_duration_valid = validate_int_number(video_duration_entry.get(), 1)
    activity_threshold_valid = validate_float_number(activity_threshold_entry.get())
    distance_filter_valid = validate_float_number(distance_filter_entry.get())
    rings_valid = validate_int_number(rings_entry.get(), 3)
     
    if Lista_cute:
        delete_button.config(state=tk.NORMAL)
        group_button.config(state=tk.NORMAL if name_entry.get().strip() and all_have_numbers and validate_string(name_entry.get())
                            else tk.DISABLED)
    else:
        delete_button.config(state=tk.DISABLED)
        group_button.config(state=tk.DISABLED)
    
    analyze_button.config(state=tk.NORMAL 
                          if listbox_right.size() > 0 
                          and numberframe_valid 
                          and video_duration_valid 
                          and activity_threshold_valid 
                          and distance_filter_valid
                          and rings_valid
                          else tk.DISABLED)
    
    delete_right_button.config(state=tk.NORMAL 
                               if listbox_right.size() > 0 
                               else tk.DISABLED)

# Funciones para agregar números de moscas por video
def on_double_click(event):
    if hasattr(on_double_click, 'entry') and on_double_click.entry:
        save_and_destroy_entry()
    item = tree.selection()[0]
    col = tree.identify_column(event.x)
    if col == '#2':  # Second column
        create_entry(item)

def create_entry(item):
    entry = tk.Entry(tree, validate="key")
    x, y, width, height = tree.bbox(item, 1)
    entry.place(x=x + tree.winfo_x(), y=y + tree.winfo_y(), width=width, height=height)
    entry.insert(0, tree.item(item, "values")[1])
    entry.config(validatecommand=(entry.register(validate_int), '%P'))
    entry.bind("<FocusOut>", lambda e: save_and_destroy_entry(entry, item))
    entry.focus()
    on_double_click.entry = entry
    on_double_click.item = item

def save_and_destroy_entry(entry=None, item=None):
    if entry and item:
        new_value = entry.get()
        tree.item(item, values=(tree.item(item, "values")[0], new_value))
        entry.destroy()
        update_buttons()
    on_double_click.entry = None
    on_double_click.item = None

def on_input_change(event):
    update_buttons()

#-------------------------------------------------------------------
# Funciones de analisis, que llaman a la logica o backend del codigo
def analyze_files():
    selected_indices = listbox_right.curselection()
    selected_files = [listbox_right.get(i) for i in selected_indices]
    if selected_files:
        print("Archivos seleccionados para análisis")
        for file in selected_files:
            print(file)
        
        analizar_preferencia = selected_option.get()
        frames_totales = int(numberframes_entry.get())
        record_time = int(video_duration_entry.get())
        filtro_distancia = float(distance_filter_entry.get())
        filtro_actividad_pausas = float(activity_threshold_entry.get())
        n_rings = int(rings_entry.get())
        
        root.withdraw()
        open_analyze_window(selected_files, frames_totales, record_time, filtro_distancia, filtro_actividad_pausas, analizar_preferencia, n_rings)
    else:
        print("No hay archivos seleccionados para análisis.")

# Funcion que genera nueva ventana tras apretar boton "Analyze"
def open_analyze_window(selected_files, frames_totales, record_time, filtro_distancia, filtro_actividad_pausas, analizar_preferencia, n_rings):
    analyze_window = tk.Toplevel(root)
    analyze_window.title("Analysis in Progress")
    analyze_window.geometry("400x400")

    stop_event = Event()

    def abort_analysis():
        stop_event.set()
        analyze_window.destroy()
        root.deiconify()

    def on_close():
        stop_event.set()
        analyze_window.destroy()
        root.destroy()

    def check_thread():
        if not analyze_thread.is_alive():
            print("TERMINADO")
            abort_analysis()
        else:
            analyze_window.after(100, check_thread)  # Verifica nuevamente después de 100 ms
            
    analyze_window.protocol("WM_DELETE_WINDOW", on_close)

    abort_button = tk.Button(analyze_window, text="Abort", command=abort_analysis, bg="lightcoral", font=("Helvetica", 10, "bold"))
    abort_button.pack(pady=20)

    # Iniciar el hilo para el análisis
    analyze_thread = Thread(target=main_backend, args=(selected_files, excels_coordenadas, filtro_distancia, filtro_actividad_pausas, analizar_preferencia, n_rings, frames_totales, record_time, stop_event))
    analyze_thread.start()

    check_thread()

#-----------------------------------------------------------------------
Lista_cute = []
excels_coordenadas = {}
#-----------------------------------------------------------------------
root = tk.Tk()
root.title("Droso-FlyTrack-Analyzer by Isidora Almonacid Torres")
root.geometry("1000x700")

selected_option = tk.StringVar(value="") 

style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

select_button = tk.Button(top_frame, text="Select Excel Files with Track Coordinates", command=select_files, bg="steelblue1")
select_button.grid(row=0, column=0, padx=5, pady=10)

delete_button = tk.Button(top_frame, text="Delete Selected Files", command=delete_files, state=tk.DISABLED, bg="tomato")
delete_button.grid(row=0, column=1, padx=5, pady=10)

group_button = tk.Button(top_frame, text="Add Group", command=add_group_files, state=tk.DISABLED, bg="palegreen2")
group_button.grid(row=0, column=2, padx=5, pady=10)

group_name_label = tk.Label(top_frame, text="Enter Group Name:")
group_name_label.grid(row=1, column=0, padx=5, pady=5)
name_entry = tk.Entry(top_frame)
name_entry.grid(row=1, column=1, padx=5, pady=5)
name_entry.bind("<KeyRelease>", on_input_change)

tree_frame = tk.Frame(root)
tree_frame.grid(row=1, column=0, padx=10, pady=10)

columns = ("File Path", "Number of Flies")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
tree.heading("File Path", text="File Path")
tree.heading("Number of Flies", text="Number of Flies")
tree.column("File Path", width=600)
tree.column("Number of Flies", width=150)

tree.pack(side=tk.LEFT, fill=tk.BOTH)
tree.bind("<Double-1>", on_double_click)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

right_frame = tk.Frame(root)
right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

right_label = tk.Label(right_frame, text="Groups", font=("Helvetica", 12, "bold"))
right_label.grid(row=0, column=0, padx=5, pady=5)

listbox_right = tk.Listbox(right_frame, selectmode=tk.MULTIPLE, width=30, height=15)
listbox_right.grid(row=1, column=0, padx=5, pady=5)

delete_right_button = tk.Button(right_frame, text="Delete Selected Group", command=delete_selected_right, state=tk.DISABLED, bg="tomato")
delete_right_button.grid(row=2, column=0, padx=5, pady=10)

parameters_frame = tk.Frame(root, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
parameters_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

tk.Label(parameters_frame, text="Number of Frames to Analyze:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
numberframes_entry = tk.Entry(parameters_frame, validate="key", validatecommand=(root.register(validate_numbers), '%P'))
numberframes_entry.grid(row=0, column=1, padx=5, pady=5)
numberframes_entry.bind("<KeyRelease>", on_input_change)

tk.Label(parameters_frame, text="Recording Duration (seconds):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
video_duration_entry = tk.Entry(parameters_frame, validate="key", validatecommand=(root.register(validate_numbers), '%P'))
video_duration_entry.grid(row=0, column=3, padx=5, pady=5)
video_duration_entry.bind("<KeyRelease>", on_input_change)

tk.Label(parameters_frame, text="Minimum Distance for Movement:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
distance_filter_entry = tk.Entry(parameters_frame, validate="key", validatecommand=(root.register(validate_thresholds), '%P'))
distance_filter_entry.grid(row=1, column=1, padx=5, pady=5)
distance_filter_entry.bind("<KeyRelease>", on_input_change)

tk.Label(parameters_frame, text="Pause Activity Threshold:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
activity_threshold_entry = tk.Entry(parameters_frame, validate="key", validatecommand=(root.register(validate_thresholds), '%P'))
activity_threshold_entry.grid(row=1, column=3, padx=5, pady=5)
activity_threshold_entry.bind("<KeyRelease>", on_input_change)

tk.Label(parameters_frame, text="Preference Analysis:").grid(row=2, column=0, padx=5, pady=5, sticky="w")

selected_option = tk.IntVar()
preference_options = ["No", "Left/Right", "Top/Bottom", "Quadrants"]
for index, option in enumerate(preference_options):
    rb = tk.Radiobutton(parameters_frame, text=option, variable=selected_option, value=index)
    rb.grid(row=2, column=1+index, padx=5, pady=5)

tk.Label(parameters_frame, text="Number of Rings:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
rings_entry = tk.Entry(parameters_frame, validate="key", validatecommand=(root.register(validate_rings_number), '%P'))
rings_entry.grid(row=3, column=1, padx=5, pady=5)
rings_entry.bind("<KeyRelease>", on_input_change)

analyze_button = tk.Button(root, text="Analyze Selected Files", command=analyze_files, state=tk.DISABLED, bg="palegreen")
analyze_button.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
