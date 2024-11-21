import main_backend_roi as br
import main_backend as ba
import tkinter as tk
import cv2
from tkinter import filedialog, ttk
from threading import Thread, Event
from PIL import Image, ImageTk

#------------------------------------------------------------------------------------------------------
#Logica Aplicacion
class App:
    def __init__(self):
        self.menu_window = None
        self.create_menu()

    def create_menu(self):
        self.menu_window = tk.Tk()
        self.menu_window.title("Main Menu")
        
        title_label = ttk.Label(self.menu_window, text="Droso-FlyTrack-Analyzer", font=("Helvetica", 12))
        title_label.pack(pady=20)

        buttonArena = ttk.Button(self.menu_window, text="Arena Selection", command=self.open_window_Arena)
        buttonArena.pack(pady=10, padx=20)

        button_ROI = ttk.Button(self.menu_window, text="Selection of Objects (Object Recognition Assay)", command=self.open_window_ROI)
        button_ROI.pack(pady=10, padx=20)

        button1 = ttk.Button(self.menu_window, text="Excel Coordinates Analysis", command=self.open_window_Analysis)
        button1.pack(pady=10, padx=20)
        
        self.menu_window.mainloop()

    def open_window_ROI(self):
        self.menu_window.destroy()
        window = Window_ROI_Selection(self)
        window.show()

    def open_window_Analysis(self):
        self.menu_window.destroy()
        window = Analysis_Window(self)
        window.show()

    def open_window_Arena(self):
        self.menu_window.destroy()
        window = ArenaROI_Window_Selection(self)
        window.show()

    def back_to_menu(self, current_window):
        current_window.destroy()
        self.create_menu()

class BaseWindow:
    def __init__(self, app, title):
        self.app = app
        self.window = tk.Tk()
        self.window.title(title)
        

    def show(self):
        self.window.mainloop()

    def back_to_menu(self):
        self.app.back_to_menu(self.window)

#------------------------------------------------------------------------------------------------------
#Ventana asociada a Analisis de Coordenadas
class Analysis_Window(BaseWindow):
    def __init__ (self, app):
        super().__init__(app, "Ventana de Análisis de Coordenadas")
        self.window.title("Droso-FlyTrack-Analyzer by Isidora Almonacid Torres")
    
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.list_excels = []
        self.excels_coordinates = {}

        # Atributos para guardar la referencia al Entry y al item
        self.current_entry = None
        self.current_item = None

        self.create_widgets()

    def create_widgets(self):
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        #Inicialización de sub-región superior izquierda
        self.top_frame = tk.Frame(self.window)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=1)
        self.top_frame.grid(row=0, column=0, pady=10, padx=2, sticky="ew", columnspan=2)

        self.group_name_label = tk.Label(self.top_frame, text="Enter Group Name:", font=("Helvetica", 10, "bold"))
        self.group_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.top_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=4, sticky="nsew")
        self.name_entry.bind("<KeyRelease>", self.on_input_change)
        
        self.select_button = tk.Button(self.top_frame, text="Select Excel Files with Track Coordinates", command=self.select_files, bg="steelblue1")
        self.select_button.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        self.delete_button = tk.Button(self.top_frame, text="Delete Selected Files", command=self.delete_files, state=tk.DISABLED, bg="tomato")
        self.delete_button.grid(row=1, column=2, padx=5, pady=10, sticky="ew")
        
        self.group_button = tk.Button(self.top_frame, text="Add Group", command=self.add_group_files, state=tk.DISABLED, bg="palegreen2")
        self.group_button.grid(row=2, column=1, padx=5, pady=10, sticky="ew", columnspan=2)
        
        #Inicialización de sub-región media izquierda (donde se agregan los excels y números de moscas)        
        self.tree_frame = tk.Frame(self.window)
        self.tree_frame.grid(row=1, column=0, padx=2, pady=10, sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(1, weight=1)
        
        columns = ("File Path", "Number of Flies")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("File Path", text="File Path")
        self.tree.heading("Number of Flies", text="Number of Flies")
        self.tree.column("File Path", width=600)
        self.tree.column("Number of Flies", width=150)
        #self.tree.pack(side=tk.LEFT, fill=tk.BOTH)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=0)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="nsw", padx=0)

        #Inicialización sub-región derecha     
        self.right_frame = tk.Frame(self.window)
        self.right_frame.grid(row=1, column=1, padx=2, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        self.right_label = tk.Label(self.right_frame, text="Groups", font=("Helvetica", 12, "bold"))
        self.right_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.listbox_right = tk.Listbox(self.right_frame, selectmode=tk.MULTIPLE, width=30, height=15)
        self.listbox_right.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        x_scrollbar = ttk.Scrollbar(self.right_frame, orient="horizontal", command=self.listbox_right.xview)
        x_scrollbar.grid(row=2, column=0, sticky="ew")

        self.delete_right_button = tk.Button(self.right_frame, text="Delete Selected Group", command=self.delete_selected_right, state=tk.DISABLED, bg="tomato")
        self.delete_right_button.grid(row=3, column=0, padx=5, pady=10)
        
        #Inicialización de sub-región inferior: Donde se seleccionan los parametros de analisis
        self.parameters_frame = tk.Frame(self.window, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
        self.parameters_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.parameters_frame.grid_columnconfigure(1, weight=1)
        self.parameters_frame.grid_columnconfigure(3, weight=1)
        self.parameters_frame.grid_columnconfigure(5, weight=1)
        
        tk.Label(self.parameters_frame, text="Number of Frames to Analyze:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.numberframes_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_numbers), '%P'))
        self.numberframes_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.numberframes_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Recording Duration (seconds):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.video_duration_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_numbers), '%P'))
        self.video_duration_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.video_duration_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Min Distance for Movement:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.distance_filter_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_thresholds), '%P'))
        self.distance_filter_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        self.distance_filter_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Activity Threshold (mm/sec):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.activity_threshold_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_thresholds), '%P'))
        self.activity_threshold_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.activity_threshold_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Preference Analysis:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.dropdown_preference = ttk.Combobox(self.parameters_frame, state="readonly", values=["No", "Left/Right", "Top/Bottom"])
        self.dropdown_preference.set("No")
        self.dropdown_preference.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        tk.Label(self.parameters_frame, text="Number of Rings:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.rings_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_rings_number), '%P'))
        self.rings_entry.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
        self.rings_entry.bind("<KeyRelease>", self.on_input_change)
        self.rings_entry.config(state=tk.DISABLED)

        tk.Label(self.parameters_frame, text="Scaling Factor (OBR):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.scaling_factor_entry = tk.Entry(self.parameters_frame)
        self.scaling_factor_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.scaling_factor_entry.bind("<KeyRelease>", self.on_input_change)
        self.scaling_factor_entry.config(state=tk.DISABLED)

        self.var_centrophobism = tk.IntVar()
        centrophobism = tk.Checkbutton(self.parameters_frame, text="Centrophobism Analysis", variable=self.var_centrophobism,
                                       command=lambda: self.on_input_change("Checkbutton toggled"))
        centrophobism.grid(row=3, column=0, padx=5, pady=5)

        self.var_raw_data = tk.IntVar()
        raw_data = tk.Checkbutton(self.parameters_frame, text="Save Raw Data?", variable=self.var_raw_data)
        raw_data.grid(row=3, column=2, padx=5, pady=5)

        self.var_object_recognition = tk.IntVar()
        object_recognition = tk.Checkbutton(self.parameters_frame, text="Object Recognition Analysis", variable=self.var_object_recognition,
                                            command=lambda: self.on_input_change("Checkbutton toggled"))
        object_recognition.grid(row=3, column=4, padx=5, pady=5)

        #Botones al final de la ventana
        self.analyze_button = tk.Button(self.window, text="Analyze Selected Files", command=self.analyze_files, state=tk.DISABLED, bg="palegreen")
        self.analyze_button.grid(row=4, pady=5, padx=5, columnspan=2) 

        back_button = ttk.Button(self.window, text="Back to Menu", command=self.back_to_menu)
        back_button.grid(row=5, pady=5, padx=5, columnspan=2)

    # Función para seleccionar archivos excels de coordenadas
    def select_files(self):
        filepaths = filedialog.askopenfilenames(title="Select Files", filetypes=[("Excel Files", "*.xlsx")])
        for filepath in filepaths:
            if filepath not in self.list_excels:
                self.list_excels.append(filepath)
                self.tree.insert("", tk.END, values=(filepath, ""))
        self.update_buttons()

    # Función para eliminar archivos excels de coordenadas seleccionados por el usuario
    def delete_files(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            filepath = self.tree.item(item, "values")[0]
            if filepath in self.list_excels:
                self.list_excels.remove(filepath)
            self.tree.delete(item)
        self.update_buttons()

    # Función para añadir, con la info entregada, un grupo de archivos xlsx de videos de moscas bajo un nombre de grupo definido por usuario
    def add_group_files(self):
        group_name = self.name_entry.get()
        # Se evalúa si hay archivos excels seleccionados + nombre de grupo
        if self.list_excels and group_name:
            self.excels_coordinates[group_name] = [[self.tree.item(item, "values")[0], int(self.tree.item(item, "values")[1])] for item in self.tree.get_children()]
            self.listbox_right.insert(tk.END, f"{group_name}")
            self.list_excels.clear()
            self.tree.delete(*self.tree.get_children())
            self.name_entry.delete(0, tk.END) 
        else:
            print("No hay archivos seleccionados o nombre ingresado.")
        self.update_buttons()

    # Funcion que actualiza disponibilidad de botones "Analyze" y "Delete"
    def update_buttons(self):
        all_have_numbers = all(self.tree.item(item, "values")[1] for item in self.tree.get_children())
        numberframe_valid = self.validate_int_number(self.numberframes_entry.get(), 1)
        video_duration_valid = self.validate_int_number(self.video_duration_entry.get(), 1)
        activity_threshold_valid = self.validate_float_number(self.activity_threshold_entry.get())
        distance_filter_valid = self.validate_float_number(self.distance_filter_entry.get())
        rings_valid = self.validate_int_number(self.rings_entry.get(), 3)
        sf_valid = self.validate_float_number(self.scaling_factor_entry.get())
        
        if self.list_excels:
            self.delete_button.config(state=tk.NORMAL)
            self.group_button.config(state=tk.NORMAL if self.name_entry.get().strip() and all_have_numbers and self.validate_string(self.name_entry.get())
                                else tk.DISABLED)
        else:
            self.delete_button.config(state=tk.DISABLED)
            self.group_button.config(state=tk.DISABLED)
        
        self.analyze_button.config(state=tk.NORMAL 
                              if self.listbox_right.size() > 0 
                              and numberframe_valid 
                              and video_duration_valid 
                              and activity_threshold_valid 
                              and distance_filter_valid
                              and ((bool(self.var_centrophobism.get() and rings_valid) or not bool(self.var_centrophobism.get())))
                              and ((bool(self.var_object_recognition.get() and sf_valid) or not bool(self.var_object_recognition.get())))
                              else tk.DISABLED)
        
        self.delete_right_button.config(state=tk.NORMAL 
                                   if self.listbox_right.size() > 0 
                                   else tk.DISABLED)
        
        self.scaling_factor_entry.config(state=tk.NORMAL if bool(self.var_object_recognition.get()) else tk.DISABLED)
        self.rings_entry.config(state=tk.NORMAL if bool(self.var_centrophobism.get()) else tk.DISABLED)

    # Funciones para agregar números de moscas por video
     # Cuando se hace doble clic en el número de moscas, se edita el valor
    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.create_entry(item)
   
    # Crear una entrada para editar el número de moscas
    def create_entry(self, item):
        entry = tk.Entry(self.tree, validate="key")
        x, y, width, height = self.tree.bbox(item, 1)
        entry.place(x=x + self.tree.winfo_x(), y=y + self.tree.winfo_y(), width=width, height=height)
        entry.insert(0, self.tree.item(item, "values")[1])
        entry.config(validatecommand=(entry.register(self.validate_int), '%P'))
        entry.bind("<FocusOut>", lambda e: self.save_and_destroy_entry(entry, item))
        entry.focus()
        self.current_entry = entry
        self.current_item = item
   
    # Guardar el valor editado y destruir la entrada
    def save_and_destroy_entry(self, entry, item):
        value = entry.get()
        if self.validate_int(value):
            self.tree.item(item, values=(self.tree.item(item, "values")[0], value))
        entry.destroy()
        self.current_entry = None
        self.current_item = None
        self.update_buttons()
       
    # Funcion para eliminar grupos seleccionados de archivos
    def delete_selected_right(self):
        selected_indices = self.listbox_right.curselection()
        for i in selected_indices[::-1]:
            name = self.listbox_right.get(i)
            if name in self.excels_coordinates:
                del self.excels_coordinates[name]
            self.listbox_right.delete(i)
        self.update_buttons()

    def on_input_change(self, event):
        self.update_buttons()

#----------------------------------------------------------------------------------------------------------- 
    # Funciones si valor entregado es valido para analisis
    def validate_int_number(self, value, threshold):
        return value.isdigit() and int(value) >= threshold
    def validate_float_number(self, value):
        try:
            return float(value) >= 0
        except ValueError:
            return False
    def validate_int(self, value):
        return (value.isdigit() and 1 <= int(value) <= 10) or value == ""
    def validate_numbers(self, value):
        return value.isdigit() and int(value) >= 1 or value == ""
    def validate_rings_number(self, value):
        return value.isdigit() and int(value) >= 1 or value == ""
    def validate_thresholds(self, value):
        if value == "":
            return True
        try:
            return float(value) >= 0
        except ValueError:
            return False
    def validate_string(self, str):
        banned_characters = ["/", '\"', ":", "*", "?", '\\', "|", "<", ">", ".", ";", ","]
        return not any(c in str for c in banned_characters)

#----------------------------------------------------------------------------------------------------------- 
    # Funciones de analisis, que llaman a la logica o backend del codigo
    def analyze_files(self):
        selected_groups = [self.listbox_right.get(i) for i in self.listbox_right.curselection()]
        if not selected_groups:
            return

        number_frames = int(self.numberframes_entry.get().strip())
        video_duration = int(self.video_duration_entry.get().strip())
        distance_filter = float(self.distance_filter_entry.get().strip())
        activity_threshold = float(self.activity_threshold_entry.get().strip())
        preference_analysis = self.dropdown_preference.get()

        object_analysis = bool(self.var_object_recognition.get())
        if self.validate_float_number(self.scaling_factor_entry.get()) and object_analysis:
            scaling_factor = float(self.scaling_factor_entry.get().strip())
        else:
            scaling_factor = None

        raw_data = bool(self.var_raw_data.get())
        centrophobism_analysis = bool(self.var_centrophobism.get())
        if centrophobism_analysis:
            rings_number = int(self.rings_entry.get().strip())
        else:
            rings_number = None

        analyze_window = tk.Toplevel(self.window)
        analyze_window.title("Analyzing Files...")
        analyze_window.geometry("600x200")

        # Etiqueta de análisis en curso
        text_var = tk.StringVar()
        text_var.set("Analyzing...")
        self.label = tk.Label(analyze_window, textvariable=text_var, font=("Helvetica", 10))
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Barra de progreso
        progress = tk.IntVar()
        self.progressbar = ttk.Progressbar(analyze_window, mode="determinate", variable=progress)
        self.progressbar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Botón de abortar
        self.abort_button = tk.Button(analyze_window, text="Abort", command=self.abort_analysis, bg="tomato")
        self.abort_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Ajustar las columnas para que se expandan
        analyze_window.grid_columnconfigure(0, weight=1)
        
        self.abort_event = Event()
        self.hide_window()

        # Función que corre en un hilo separado
        def run_analysis():
            try:
                ba.main_backend(
                    data_type="Bonsai", 
                    data_groups=selected_groups, excels_coordinates=self.excels_coordinates, 
                    filter_distance=distance_filter, filter_activity=activity_threshold, 
                    preference_analysis=preference_analysis, 
                    centrophobism_analysis=centrophobism_analysis, n_rings=rings_number, 
                    total_frame_number=number_frames, record_time=video_duration, 
                    stop_event=self.abort_event, progress=progress, text_var=text_var, raw_data_save=raw_data,
                    object_analysis=object_analysis, scaling_factor=scaling_factor
                )
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                analyze_window.destroy()
                self.show_window()
            """
            ba.main_backend(
                    data_type = "Bonsai",
                    data_groups=selected_groups, excels_coordinates=self.excels_coordinates, 
                    filter_distance=distance_filter, filter_activity=activity_threshold, 
                    preference_analysis=preference_analysis, 
                    centrophobism_analysis=centrophobism_analysis, n_rings=rings_number, 
                    total_frame_number=number_frames, record_time=video_duration, 
                    stop_event=self.abort_event, progress=progress, text_var=text_var, raw_data_save=raw_data,
                    object_analysis=object_analysis
                )
            """

        self.analysis_thread = Thread(target=run_analysis)
        self.analysis_thread.start()

    # Función para abortar el análisis
    def abort_analysis(self, a_windows):
        if self.abort_event:
            self.abort_event.set()
            a_windows.destroy()
        #self.analysis_thread.join()
    
    # Funcion que genera nueva ventana tras apretar boton "Analyze"
    def open_analyze_window(self, selected_files, total_frame_number, record_time, filter_distance, filter_activity, preference_analysis, n_rings):
        analyze_window = tk.Toplevel(self.window)
        analyze_window.title("Analysis in Progress")
        analyze_window.geometry("600x200")

        stop_event = Event()

        def abort_analysis():
            stop_event.set()
            analyze_window.destroy()
            self.window.deiconify()
    
        def on_close():
            stop_event.set()
            analyze_window.destroy()
            self.window.destroy()
    
        def check_thread():
            if not analyze_thread.is_alive():
                print("TERMINADO")
                abort_analysis()
            else:
                analyze_window.after(100, check_thread)  # Verifica nuevamente después de 100 ms
                
        analyze_window.protocol("WM_DELETE_WINDOW", on_close)

        text_var = tk.StringVar()
        text_var.set("Starting analysis...")
        label_progress = tk.Label(analyze_window, textvariable=text_var, width=500, height=60)
        label_progress.grid(row=0, column=0,sticky="ew", pady=5, padx=5)
        progress = tk.IntVar()
        progressbar = ttk.Progressbar(analyze_window, variable=progress)    
        progressbar.grid(row=1, column=0,sticky="ew", pady=5, padx=5)

        abort_button = tk.Button(analyze_window, text="Abort", command=abort_analysis, bg="lightcoral", font=("Helvetica", 10, "bold"))
        abort_button.grid(row=2, column=0,sticky="ew", pady=5, padx=5)
        
        # Ajustar las columnas para que se expandan
        analyze_window.grid_columnconfigure(0, weight=1)

        # Iniciar el hilo para el análisis
        analyze_thread = Thread(target=ba.main_backend, args=(selected_files, 
                                                           self.excels_coordinates, 
                                                           filter_distance, 
                                                           filter_activity, 
                                                           preference_analysis, n_rings, 
                                                           total_frame_number, record_time, 
                                                           stop_event, progress, text_var))
        analyze_thread.start()
        check_thread()
    
    def hide_window(self):
        self.window.withdraw()

    def show_window(self):
        self.window.deiconify()

#------------------------------------------------------------------------------------------------------
#Ventana asociada a Seleccion de Objetos
class Window_ROI_Selection(BaseWindow):
    def __init__(self, app):
        super().__init__(app, "Object Selection Window")
        self.file_paths = []
        self.csv_paths = []
        self.current_index = 0
        self.roi_coordinates = {}
        self.create_widgets()

    def create_widgets(self):
        #Widgets de la izquierda
        left_frame = tk.Frame(self.window)
        left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        select_button = ttk.Button(left_frame, text="Select mp4 files", command=self.select_files)
        select_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        delete_button = ttk.Button(left_frame, text="Delete mp4 selected files", command=self.delete_selected_file)
        delete_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_listbox = tk.Listbox(left_frame, width=80, height=15)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.file_listbox.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.file_listbox.xview)
        x_scrollbar.grid(row=2, column=0, sticky="ew")
        self.file_listbox.config(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        #Widgets de la derecha
        right_frame = tk.Frame(self.window)
        right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        select_button = ttk.Button(right_frame, text="Select Excel files", command=self.select_files_csv)
        select_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        delete_button = ttk.Button(right_frame, text="Delete selected Excel files", command=self.delete_selected_file_csv)
        delete_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.csv_listbox = tk.Listbox(right_frame, width=80, height=15)
        self.csv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar_csv = ttk.Scrollbar(right_frame, orient="vertical", command=self.csv_listbox.yview)
        y_scrollbar_csv.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar_csv = ttk.Scrollbar(self.window, orient="horizontal", command=self.csv_listbox.xview)
        x_scrollbar_csv.grid(row=2, column=1, sticky="ew")
        self.csv_listbox.config(yscrollcommand=y_scrollbar_csv.set, xscrollcommand=x_scrollbar_csv.set)

        #Widgets inferiores
        self.start_roi_button = ttk.Button(self.window, text="Select Objects ROI", command=self.open_roi_window, state=tk.DISABLED)
        self.start_roi_button.grid(row=3, pady=5, padx=5, columnspan=2)

        back_button = ttk.Button(self.window, text="Back to Menu", command=self.back_to_menu)
        back_button.grid(row=4, pady=5, padx=5, columnspan=2)

    def select_files_csv(self):
        self.csv_paths = list(filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx")]))
        if self.csv_paths:
            self.csv_listbox.delete(0, tk.END)
            for path in self.csv_paths:
                self.csv_listbox.insert(tk.END, path)
        self.update_buttons()

    def select_files(self):
        self.file_paths = list(filedialog.askopenfilenames(filetypes=[("MP4 files", "*.mp4")]))
        if self.file_paths:
            self.file_listbox.delete(0, tk.END)
            for path in self.file_paths:
                self.file_listbox.insert(tk.END, path)
        self.update_buttons()

    def delete_selected_file_csv(self):
        selected_indices = self.csv_listbox.curselection()
        if selected_indices:
            for index in reversed(selected_indices):
                del self.csv_paths[index]
                self.csv_listbox.delete(index)
            if self.current_index >= len(self.csv_paths):
                self.current_index = len(self.csv_paths) - 1
        self.update_buttons()

    def delete_selected_file(self):
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            for index in reversed(selected_indices):
                del self.file_paths[index]
                self.file_listbox.delete(index)
            if self.current_index >= len(self.file_paths):
                self.current_index = len(self.file_paths) - 1
        self.update_buttons()

    def update_buttons(self):
        if len(self.file_paths) == len(self.csv_paths):
            self.start_roi_button.config(state=tk.NORMAL)
        else:
            self.start_roi_button.config(state=tk.DISABLED)

    def open_roi_window(self):
        self.window.withdraw()
        roi_window = tk.Toplevel(self.window)
        roi_window = ROI_Window(
            roi_window, 
            file_paths=self.file_paths, 
            csv_paths=self.csv_paths,
            roi_coordinates=self.roi_coordinates, 
            root_window=self.window
            )
        roi_window.show()

class ROI_Window:
    def __init__(self, top_window, file_paths, csv_paths, roi_coordinates, root_window):
        self.file_paths = file_paths
        self.csv_paths = csv_paths
        self.current_index = 0
        self.roi_coordinates = roi_coordinates
        self.window = top_window
        self.root_window = root_window
        self.objects_ids = []
        self.object_identities = []

        self.mm_px, self.mm_py = br.obtain_mmpx_mmpy_Bonsai(self.csv_paths[self.current_index])
        #print(self.mm_px, self.mm_py)
        
        self.create_widgets()

    def create_widgets(self):
        self.frame=tk.Frame(self.window)
        self.frame.pack(side=tk.LEFT, anchor="center", pady=2)
        
        label_objecttype = tk.Label(self.frame, text="Type of object:")
        label_objecttype.grid(row=0, column=0, pady=5, padx=5)
        self.dropdown_objecttype = ttk.Combobox(self.frame, state="readonly", values=["Square", "Rectangle", "Oval"])
        self.dropdown_objecttype.set("Square")
        self.dropdown_objecttype.grid(row=0, column=1, pady=5, padx=5)
        self.dropdown_objecttype.bind("<<ComboboxSelected>>", self.on_input_change)

        #Entries for users to select the real size of the object
        label_radius = tk.Label(self.frame, text="Oval radius (mm):")
        label_radius.grid(row=1, column=0, padx=5, pady=5)
        self.radius = tk.Entry(self.frame)
        self.radius.grid(row=1, column=1,padx=5, pady=5)
        self.radius.config(state="disabled")
        label_side1 = tk.Label(self.frame, text="Side 1 rectangle (mm):")
        label_side1.grid(row=2, column=0, padx=5, pady=5)
        self.side1 = tk.Entry(self.frame)
        self.side1.grid(row=2, column=1, padx=5, pady=5)
        self.side1.config(state="normal")
        label_side2 = tk.Label(self.frame, text="Side 2 rectangle (mm):")
        label_side2.grid(row=3, column=0, padx=5, pady=5)
        self.side2 = tk.Entry(self.frame)
        self.side2.grid(row=3, column=1, padx=5, pady=5)
        self.side2.config(state="disabled")

        # Start drawing selection button
        self.start_selection_button = ttk.Button(self.frame, text="Draw ROI", command=self.start_roi_selection)
        self.start_selection_button.grid(row=4, pady=10, columnspan=2)

        # Add clear button for restarting ROI selection
        self.clear_button = ttk.Button(self.frame, text="Clear", command=self.clear_canvas)
        self.clear_button.grid(row=5, pady=10, columnspan=2)
        self.clear_button.config(state=tk.DISABLED)

        # Add Approve Button
        self.approve_button = ttk.Button(self.frame, text="Approve Object Selection", command=self.on_end_selection)
        self.approve_button.grid(row=6, pady = 10, columnspan=2)
        self.approve_button.config(state=tk.DISABLED)

        #Next video button
        self.next_button = ttk.Button(self.frame, text="Next File", state=tk.DISABLED, command=self.next_video)
        self.next_button.grid(row=7, pady=20, columnspan=2)

        #Canvas
        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.pack(side='top', fill='both', expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, scrollregion=(0, 0, 1000, 1000))  # Placeholder size
        self.canvas.pack(side='left', fill='both', expand=True)

        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.v_scrollbar.pack(side='right', fill='y')
        self.canvas.config(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = ttk.Scrollbar(self.window, orient='horizontal', command=self.canvas.xview)
        self.h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.config(xscrollcommand=self.h_scrollbar.set)
    
    def on_input_change(self, event):
        selection = self.dropdown_objecttype.get()
        if selection == "Square":
            self.radius.config(state="disabled")
            self.side2.config(state="disabled")
            self.side1.config(state="normal")
        elif selection == "Rectangle":
            self.radius.config(state="disabled")
            self.side2.config(state="normal")
            self.side1.config(state="normal")
        elif selection == "Oval":
            self.radius.config(state="normal")
            self.side2.config(state="disabled")
            self.side1.config(state="disabled")
    
    def show(self):
        self.load_video()
        self.window.deiconify()
    
    def load_video(self):
        path = self.file_paths[self.current_index]
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"Can't open file: {path}")
            return
        
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.config(width=self.photo.width(), height=self.photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        else:
            print(f"Couldn't the frame from the file: {path}")
            
    def clear_canvas(self):
        self.canvas.delete(self.current_object)
        self.start_selection_button.config(state=tk.NORMAL)
        self.dropdown_objecttype.config(state="readonly")
        self.clear_button.config(state=tk.DISABLED)
    
    #Funcion que inicia el dibujo del ROI/Objeto
    def start_roi_selection(self):
        self.canvas.bind("<ButtonPress-1>", self.on_start_selection)
        self.start_selection_button.config(state=tk.DISABLED)
        self.dropdown_objecttype.config(state=tk.DISABLED)
        
    def on_start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.dropdown_objecttype.get() == "Square":
            size_in_mm = float(self.side1.get())
            end_x = self.start_x + (size_in_mm/self.mm_px)
            end_y = self.start_y + (size_in_mm/self.mm_py)
            self.current_object = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='red', width=2)
        elif self.dropdown_objecttype.get() == "Rectangle":
            size1_in_mm = float(self.side1.get())
            size2_in_mm = float(self.side2.get())
            end_x = self.start_x + (size1_in_mm/self.mm_px)
            end_y = self.start_y + (size2_in_mm/self.mm_py)
            self.current_object = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='red', width=2)
        elif self.dropdown_objecttype.get() == "Oval":
            radius_in_mm = float(self.radius.get())
            start_x = self.start_x - (radius_in_mm/self.mm_px)
            start_y = self.start_y - (radius_in_mm/self.mm_py)
            end_x = self.start_x + (radius_in_mm/self.mm_px)
            end_y = self.start_y + (radius_in_mm/self.mm_py)
            self.current_object = self.canvas.create_oval(start_x, start_y, end_x, end_y)
        # Allow approving of the drawing or clearing it
        self.approve_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        # Unable another drawing
        self.canvas.unbind("<ButtonPress-1>")
        # Allow moving the object
        self.window.bind("<Up>", self.move_up)
        self.window.bind("<Down>", self.move_down)
        self.window.bind("<Left>", self.move_left)
        self.window.bind("<Right>", self.move_right)

    # Functions to move the rectangle
    def move_up(self, event):
        self.canvas.move(self.current_object, 0, -1)  
    def move_down(self, event):
        self.canvas.move(self.current_object, 0, 1)   
    def move_left(self, event):
        self.canvas.move(self.current_object, -1, 0)  
    def move_right(self, event):
        self.canvas.move(self.current_object, 1, 0)   
    
    # Function when you approve an object
    def on_end_selection(self):
        self.objects_ids.append(self.current_object)
        self.object_identities.append(self.dropdown_objecttype.get())
        self.canvas.itemconfig(self.current_object, outline="blue")
        self.window.unbind("<Up>")
        self.window.unbind("<Down>")
        self.window.unbind("<Left>")
        self.window.unbind("<Right>")

        # Ready for next object selection
        self.next_button.config(state=tk.NORMAL)
        self.start_selection_button.config(state=tk.NORMAL)
        self.dropdown_objecttype.config(state="readonly")
        self.clear_button.config(state=tk.DISABLED)
        self.approve_button.config(state=tk.DISABLED)

    # Functions to move to next video
    def next_video(self):
        self.roi_coordinates[self.current_index] = [
            self.file_paths[self.current_index],
            self.csv_paths[self.current_index],
            [self.canvas.coords(obj) for obj in self.objects_ids],
            self.object_identities
        ]

        self.current_index += 1
        if self.current_index < len(self.file_paths):
            self.load_video()
            self.objects_ids.clear()  # Clear previous squares
            self.start_selection_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.DISABLED)
            self.mm_px, self.mm_py = br.obtain_mmpx_mmpy_Bonsai(self.csv_paths[self.current_index])
        else:
            self.window.destroy()
            self.update_csv_with_roi()
            self.root_window.deiconify()

    def update_csv_with_roi(self):
        length = len(self.file_paths)
        br.add_roi_to_csvdata(length=length, roi_coordinates_dict=self.roi_coordinates)        

#------------------------------------------------------------------------------------------------------
#Ventana asociada a Seleccion de Arena
class ArenaROI_Window_Selection(BaseWindow):
    def __init__(self, app):
        super().__init__(app, "Arena Selection Window")
        self.file_paths = []
        self.csv_paths = []
        self.current_index = 0
        self.roi_coordinates = {}
        self.create_widgets()

    def create_widgets(self):
    #Widgets de la izquierda
        left_frame = tk.Frame(self.window)
        left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        select_button = ttk.Button(left_frame, text="Select mp4 files", command=self.select_files)
        select_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        delete_button = ttk.Button(left_frame, text="Delete mp4 selected files", command=self.delete_selected_file)
        delete_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_listbox = tk.Listbox(left_frame, width=80, height=15)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.file_listbox.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.file_listbox.xview)
        x_scrollbar.grid(row=2, column=0, sticky="ew")
        self.file_listbox.config(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        #Widgets de la derecha
        right_frame = tk.Frame(self.window)
        right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        select_button = ttk.Button(right_frame, text="Select CSV files", command=self.select_files_csv)
        select_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        delete_button = ttk.Button(right_frame, text="Delete CSV selected files", command=self.delete_selected_file_csv)
        delete_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.csv_listbox = tk.Listbox(right_frame, width=80, height=15)
        self.csv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar_csv = ttk.Scrollbar(right_frame, orient="vertical", command=self.csv_listbox.yview)
        y_scrollbar_csv.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar_csv = ttk.Scrollbar(self.window, orient="horizontal", command=self.csv_listbox.xview)
        x_scrollbar_csv.grid(row=2, column=1, sticky="ew")
        self.csv_listbox.config(yscrollcommand=y_scrollbar_csv.set, xscrollcommand=x_scrollbar_csv.set)

        #Widgets inferiores
        self.start_roi_button = ttk.Button(self.window, text="Select Arena ROI", command=self.open_roi_window, state=tk.DISABLED)
        self.start_roi_button.grid(row=3, column=0, pady=10)

        back_button = ttk.Button(self.window, text="Back to Menu", command=self.back_to_menu)
        back_button.grid(row=4, pady=5, padx=5, columnspan=2)

    def select_files_csv(self):
        self.csv_paths = list(filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")]))
        if self.csv_paths:
            self.csv_listbox.delete(0, tk.END)
            for path in self.csv_paths:
                self.csv_listbox.insert(tk.END, path)
        self.update_buttons()

    def select_files(self):
        self.file_paths = list(filedialog.askopenfilenames(filetypes=[("MP4 files", "*.mp4")]))
        print(self.file_paths)
        if self.file_paths:
            self.file_listbox.delete(0, tk.END)
            for path in self.file_paths:
                self.file_listbox.insert(tk.END, path)
        self.update_buttons()

    def delete_selected_file_csv(self):
        selected_indices = self.csv_listbox.curselection()
        if selected_indices:
            for index in reversed(selected_indices):
                del self.csv_paths[index]
                self.csv_listbox.delete(index)
            if self.current_index >= len(self.csv_paths):
                self.current_index = len(self.csv_paths) - 1
        self.update_buttons()

    def delete_selected_file(self):
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            for index in reversed(selected_indices):
                del self.file_paths[index]
                self.file_listbox.delete(index)
            if self.current_index >= len(self.file_paths):
                self.current_index = len(self.file_paths) - 1
        self.update_buttons()

    def update_buttons(self):
        if len(self.file_paths) == len(self.csv_paths):
            self.start_roi_button.config(state=tk.NORMAL)
        else:
            self.start_roi_button.config(state=tk.DISABLED)

    def open_roi_window(self):
        self.window.withdraw()
        roi_window = tk.Toplevel(self.window)
        roi_window = ArenaROI_Window(
            roi_window, 
            file_paths=self.file_paths, 
            csv_paths=self.csv_paths,
            current_index=self.current_index, 
            roi_coordinates=self.roi_coordinates, 
            root_window=self.window
            )
        roi_window.show()

class ArenaROI_Window:
    def __init__(self, top_window, file_paths, csv_paths, current_index, roi_coordinates, root_window):
        self.file_paths = file_paths
        self.csv_paths = csv_paths
        self.current_index = current_index
        self.roi_coordinates = roi_coordinates
        self.window = top_window
        self.root_window = root_window
        self.oval_id = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.create_widgets()

    def create_widgets(self):
        self.frame=tk.Frame(self.window)
        self.frame.pack(side="left", anchor="center", pady=2)
        
        self.label_radius = tk.Label(self.frame, text="Arena Radius (mm):")
        self.label_radius.pack(side=tk.TOP, anchor="center",pady=5)
        self.entry_radius = tk.Entry(self.frame, validate="key", validatecommand=(self.window.register(self.validate_radius), '%P'))
        self.entry_radius.pack(side=tk.TOP, anchor="center", pady=5)
        self.entry_radius.bind("<KeyRelease>", self.update_button)

        self.start_selection_button = ttk.Button(self.frame, text="Dibujar ROI", command=self.start_roi_selection)
        self.start_selection_button.pack(side=tk.BOTTOM, anchor='center', pady=5)

        self.next_button = ttk.Button(self.frame, text="Siguiente", state=tk.DISABLED, command=self.next_video)
        self.next_button.pack(side=tk.BOTTOM, anchor='center', pady=5)

        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.pack(side='top', fill='both', expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, scrollregion=(0, 0, 1000, 1000))  # Placeholder size
        self.canvas.pack(side='left', fill='both', expand=True)

        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.v_scrollbar.pack(side='right', fill='y')
        self.canvas.config(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = ttk.Scrollbar(self.window, orient='horizontal', command=self.canvas.xview)
        self.h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.config(xscrollcommand=self.h_scrollbar.set)

    def show(self):
        self.load_video()
        self.window.deiconify()

    def validate_radius(self, value):
        try:
            return float(value) >= 0
        except ValueError:
            return False
        
    def update_button(self, value):
        if self.entry_radius.get() != "" and self.oval_id:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def load_video(self):
        path = self.file_paths[self.current_index]
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"No se puede abrir el archivo {path}")
            return
        
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.config(width=self.photo.width(), height=self.photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        else:
            print(f"No se pudo leer el frame del archivo {path}")

    def start_roi_selection(self):
        self.canvas.bind("<ButtonPress-1>", self.on_start_selection)
        self.canvas.bind("<B1-Motion>", self.on_move_selection)
        self.canvas.bind("<ButtonRelease-1>", self.on_end_selection)
        self.start_selection_button.config(state=tk.DISABLED)

    def on_start_selection(self, event):
        if self.oval_id:
            self.canvas.delete(self.oval_id)
        self.start_x = event.x
        self.start_y = event.y
        self.oval_id = self.canvas.create_oval(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=1)

    def on_move_selection(self, event):
        self.canvas.coords(self.oval_id, self.start_x, self.start_y, event.x, event.y)

    def on_end_selection(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.next_button.config(state=tk.NORMAL)
        
        # Hacer el óvalo editable
        self.canvas.tag_bind(self.oval_id, "<ButtonPress-1>", self.on_oval_press)
        self.canvas.tag_bind(self.oval_id, "<B1-Motion>", self.on_oval_move)

        # Agregar puntos de anclaje en los bordes del óvalo
        self.create_resize_handles()

    def on_oval_press(self, event):
        self.oval_start_x = event.x
        self.oval_start_y = event.y
        self.oval_bbox = self.canvas.coords(self.oval_id)

    def on_oval_move(self, event):
        dx = event.x - self.oval_start_x
        dy = event.y - self.oval_start_y
        new_bbox = [self.oval_bbox[0] + dx, self.oval_bbox[1] + dy, self.oval_bbox[2] + dx, self.oval_bbox[3] + dy]
        self.canvas.coords(self.oval_id, *new_bbox)
        self.update_resize_handles()

    def create_resize_handles(self):
        x0, y0, x1, y1 = self.canvas.coords(self.oval_id)
        self.handles = [
            self.canvas.create_rectangle(x0-5, y0-5, x0+5, y0+5, outline="darkblue", fill="darkblue"),
            self.canvas.create_rectangle(x1-5, y0-5, x1+5, y0+5, outline="darkblue", fill="darkblue"),
            self.canvas.create_rectangle(x0-5, y1-5, x0+5, y1+5, outline="darkblue", fill="darkblue"),
            self.canvas.create_rectangle(x1-5, y1-5, x1+5, y1+5, outline="darkblue", fill="darkblue")
        ]

        for handle in self.handles:
            self.canvas.tag_bind(handle, "<ButtonPress-1>", self.on_handle_press)
            self.canvas.tag_bind(handle, "<B1-Motion>", self.on_handle_move)

    def update_resize_handles(self):
        x0, y0, x1, y1 = self.canvas.coords(self.oval_id)
        handle_coords = [
            (x0-5, y0-5, x0+5, y0+5),
            (x1-5, y0-5, x1+5, y0+5),
            (x0-5, y1-5, x0+5, y1+5),
            (x1-5, y1-5, x1+5, y1+5)
        ]

        for handle, coords in zip(self.handles, handle_coords):
            self.canvas.coords(handle, *coords)

    def on_handle_press(self, event):
        self.handle_start_x = event.x
        self.handle_start_y = event.y
        self.oval_bbox = self.canvas.coords(self.oval_id)
        self.active_handle = event.widget.find_closest(event.x, event.y)[0]

    def on_handle_move(self, event):
        dx = event.x - self.handle_start_x
        dy = event.y - self.handle_start_y

        x0, y0, x1, y1 = self.oval_bbox
        if self.active_handle == self.handles[0]:  # Top-left
            new_coords = [x0 + dx, y0 + dy, x1, y1]
        elif self.active_handle == self.handles[1]:  # Top-right
            new_coords = [x0, y0 + dy, x1 + dx, y1]
        elif self.active_handle == self.handles[2]:  # Bottom-left
            new_coords = [x0 + dx, y0, x1, y1 + dy]
        elif self.active_handle == self.handles[3]:  # Bottom-right
            new_coords = [x0, y0, x1 + dx, y1 + dy]

        self.canvas.coords(self.oval_id, *new_coords)
        self.update_resize_handles()

    def next_video(self):
        self.roi_coordinates[self.current_index] = [
            self.file_paths[self.current_index], 
            self.csv_paths[self.current_index], 
            self.canvas.coords(self.oval_id),
            float(self.entry_radius.get())
            ]

        self.current_index += 1
        if self.current_index < len(self.file_paths):
            self.load_video()
            self.start_selection_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.DISABLED)
        else:
            self.window.destroy()
            self.update_csv_with_roi()
            self.root_window.deiconify()

    def update_csv_with_roi(self):
        length = len(self.file_paths)
        br.add_arenaroi_to_csvdata(length=length, roi_coordinates_dict=self.roi_coordinates)       

#------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app = App()