import tkinter as tk
from tkinter import filedialog, ttk
from threading import Thread, Event
from main_backend import main_backend

class Main_Window_PreAnalysis(ttk.Frame):
    def __init__ (self, main_window):
        self.window = main_window
        super().__init__(self.window)
        self.window.title("Droso-FlyTrack-Analyzer by Isidora Almonacid Torres")
        self.window.geometry("1000x700")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.list_excels = []
        self.excels_coordinates = {}

        # Atributos para guardar la referencia al Entry y al item
        self.current_entry = None
        self.current_item = None

        self.create_widgets()

    def create_widgets(self):
        #Inicialización de sub-región superior izquierda
        self.top_frame = tk.Frame(self.window)
        self.top_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.select_button = tk.Button(self.top_frame, text="Select Excel Files with Track Coordinates", command=self.select_files, bg="steelblue1")
        self.select_button.grid(row=0, column=0, padx=5, pady=10)
        
        self.delete_button = tk.Button(self.top_frame, text="Delete Selected Files", command=self.delete_files, state=tk.DISABLED, bg="tomato")
        self.delete_button.grid(row=0, column=1, padx=5, pady=10)
        
        self.group_button = tk.Button(self.top_frame, text="Add Group", command=self.add_group_files, state=tk.DISABLED, bg="palegreen2")
        self.group_button.grid(row=0, column=2, padx=5, pady=10)
        
        self.group_name_label = tk.Label(self.top_frame, text="Enter Group Name:")
        self.group_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.top_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.name_entry.bind("<KeyRelease>", self.on_input_change)

        #Inicialización de sub-región media izquierda (donde se agregan los excels y números de moscas)        
        self.tree_frame = tk.Frame(self.window)
        self.tree_frame.grid(row=1, column=0, padx=10, pady=10)
        
        columns = ("File Path", "Number of Flies")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("File Path", text="File Path")
        self.tree.heading("Number of Flies", text="Number of Flies")
        self.tree.column("File Path", width=600)
        self.tree.column("Number of Flies", width=150)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #Inicialización sub-región derecha     
        self.right_frame = tk.Frame(self.window)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
        
        self.right_label = tk.Label(self.right_frame, text="Groups", font=("Helvetica", 12, "bold"))
        self.right_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.listbox_right = tk.Listbox(self.right_frame, selectmode=tk.MULTIPLE, width=30, height=15)
        self.listbox_right.grid(row=1, column=0, padx=5, pady=5)
        
        self.delete_right_button = tk.Button(self.right_frame, text="Delete Selected Group", command=self.delete_selected_right, state=tk.DISABLED, bg="tomato")
        self.delete_right_button.grid(row=2, column=0, padx=5, pady=10)
        
        #Inicialización de sub-región inferior: Donde se seleccionan los parametros de analisis
        self.parameters_frame = tk.Frame(self.window, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
        self.parameters_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        tk.Label(self.parameters_frame, text="Number of Frames to Analyze:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.numberframes_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_numbers), '%P'))
        self.numberframes_entry.grid(row=0, column=1, padx=5, pady=5)
        self.numberframes_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Recording Duration (seconds):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.video_duration_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_numbers), '%P'))
        self.video_duration_entry.grid(row=0, column=3, padx=5, pady=5)
        self.video_duration_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Min Distance for Movement:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.distance_filter_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_thresholds), '%P'))
        self.distance_filter_entry.grid(row=0, column=5, padx=5, pady=5)
        self.distance_filter_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Activity Threshold (mm/sec):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.activity_threshold_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_thresholds), '%P'))
        self.activity_threshold_entry.grid(row=1, column=1, padx=5, pady=5)
        self.activity_threshold_entry.bind("<KeyRelease>", self.on_input_change)
        
        tk.Label(self.parameters_frame, text="Preference Analysis:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.dropdown_preference = ttk.Combobox(self.parameters_frame, state="readonly", values=["No", "Left/Right", "Top/Bottom"])
        self.dropdown_preference.set("No")
        self.dropdown_preference.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        tk.Label(self.parameters_frame, text="Number of Rings:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.rings_entry = tk.Entry(self.parameters_frame, validate="key", validatecommand=(self.window.register(self.validate_rings_number), '%P'))
        self.rings_entry.grid(row=3, column=1, padx=5, pady=5)
        self.rings_entry.bind("<KeyRelease>", self.on_input_change)

        self.var_centrophobism = tk.IntVar()
        centrophobism = tk.Checkbutton(self.parameters_frame, text="Centrophobism Analysis", variable=self.var_centrophobism)
        centrophobism.grid(row=3, column=2, padx=5, pady=5)
        
        self.analyze_button = tk.Button(self.window, text="Analyze Selected Files", command=self.analyze_files, state=tk.DISABLED, bg="palegreen")
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=10) 

        self.var_raw_data = tk.IntVar()
        raw_data = tk.Checkbutton(self.window, text="Save Raw Data?", variable=self.var_raw_data)
        raw_data.grid(row=3, column=1, padx=5, pady=5)

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
                              and rings_valid
                              else tk.DISABLED)
        
        self.delete_right_button.config(state=tk.NORMAL 
                                   if self.listbox_right.size() > 0 
                                   else tk.DISABLED)

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
        print(self.excels_coordinates)
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
        rings_number = int(self.rings_entry.get().strip())
        preference_analysis = self.dropdown_preference.get()

        raw_data = bool(self.var_raw_data.get())
        centrophobism_analysis = bool(self.var_centrophobism.get())

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

        # Función que corre en un hilo separado
        def run_analysis():
            try:
                main_backend(
                    data_groups=selected_groups, excels_coordinates=self.excels_coordinates, 
                    filter_distance=distance_filter, filter_activity=activity_threshold, 
                    preference_analysis=preference_analysis, 
                    centrophobism_analysis=centrophobism_analysis, n_rings=rings_number, 
                    total_frame_number=number_frames, record_time=video_duration, 
                    stop_event=self.abort_event, progress=progress, text_var=text_var, raw_data_save=raw_data
                )
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                analyze_window.destroy()

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
            main_window.deiconify()
    
        def on_close():
            stop_event.set()
            analyze_window.destroy()
            main_window.destroy()
    
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
        analyze_thread = Thread(target=main_backend, args=(selected_files, 
                                                           self.excels_coordinates, 
                                                           filter_distance, 
                                                           filter_activity, 
                                                           preference_analysis, n_rings, 
                                                           total_frame_number, record_time, 
                                                           stop_event, progress, text_var))
        analyze_thread.start()
        check_thread()

if __name__ == "__main__":
    main_window = tk.Tk()
    app = Main_Window_PreAnalysis(main_window)
    app.mainloop()
