"""
Módulo de Interfaz de Usuario para Ferretería Analyzer
=====================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

class FerreteriaUI:
    """Clase para manejar la interfaz de usuario"""
    
    def __init__(self, app_controller):
        self.app = app_controller
        self.root = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.root = tk.Tk()
        self.root.title("🔧 Ferretería Analyzer con IA - Pipeline Completo")
        self.root.geometry("1200x800")
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Crear widgets
        self.create_control_panel(main_frame)
        self.create_data_tree(main_frame)
        self.create_log_panel(main_frame)
        
        # Variables de UI
        self.selected_dir = None
        
    def create_control_panel(self, parent):
        """Crea el panel de controles"""
        control_frame = ttk.LabelFrame(parent, text="🔧 Controles Principales", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones principales
        buttons = [
            ("📁 Seleccionar Directorio", self.app.select_directory),
            ("🔍 Extraer Datos HTML", self.app.extract_data),
            ("🧹 Purificar Datos", self.app.purify_data),
            ("🤖 Analizar con IA", self.app.analyze_with_ai),
            ("📊 Exportar Excel", self.app.export_excel)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(control_frame, text=text, command=command, width=20)
            btn.grid(row=0, column=i, padx=5)
        
        # Label de directorio seleccionado
        self.dir_label = ttk.Label(control_frame, text="Ningún directorio seleccionado", 
                                  foreground="gray")
        self.dir_label.grid(row=1, column=0, columnspan=5, pady=(10, 0))
    
    def create_data_tree(self, parent):
        """Crea el árbol de datos"""
        tree_frame = ttk.LabelFrame(parent, text="📊 Datos Extraídos", padding="10")
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Crear treeview con scrollbar
        self.tree = ttk.Treeview(tree_frame, columns=('Valor',), show='tree headings')
        self.tree.heading('#0', text='Elemento')
        self.tree.heading('Valor', text='Valor')
        self.tree.column('#0', width=200)
        self.tree.column('Valor', width=300)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def create_log_panel(self, parent):
        """Crea el panel de logs"""
        log_frame = ttk.LabelFrame(parent, text="📝 Log de Actividades", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget para logs
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=50, height=20)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def update_directory_label(self, directory):
        """Actualiza el label del directorio seleccionado"""
        if directory:
            self.dir_label.config(text=f"📁 {directory}", foreground="blue")
            self.selected_dir = directory
        else:
            self.dir_label.config(text="Ningún directorio seleccionado", foreground="gray")
            self.selected_dir = None
    
    def log_message(self, message):
        """Añade un mensaje al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Limpia el log"""
        self.log_text.delete(1.0, tk.END)
    
    def update_data_tree(self, data):
        """Actualiza el árbol de datos"""
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not data:
            return
        
        # Añadir datos al árbol
        if isinstance(data, dict):
            self._add_dict_to_tree('', 'Datos', data)
    
    def _add_dict_to_tree(self, parent, key, data):
        """Añade un diccionario al árbol de manera recursiva"""
        if isinstance(data, dict):
            node = self.tree.insert(parent, 'end', text=key, values=('',))
            for k, v in data.items():
                if k == 'productos' and isinstance(v, list):
                    self._add_products_to_tree(node, v)
                else:
                    self._add_dict_to_tree(node, k, v)
        elif isinstance(data, list):
            node = self.tree.insert(parent, 'end', text=f"{key} ({len(data)} elementos)", values=('',))
            for i, item in enumerate(data):
                self._add_dict_to_tree(node, f"Item {i+1}", item)
        else:
            # Truncar valores muy largos
            value_str = str(data)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            self.tree.insert(parent, 'end', text=key, values=(value_str,))
    
    def _add_products_to_tree(self, parent, products):
        """Añade productos al árbol de manera optimizada"""
        products_node = self.tree.insert(parent, 'end', 
                                       text=f"productos ({len(products)} items)", 
                                       values=('',))
        
        # Mostrar solo los primeros 10 productos para performance
        for i, product in enumerate(products[:10]):
            if isinstance(product, dict):
                desc = product.get('descripcion', f'Producto {i+1}')
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                
                product_node = self.tree.insert(products_node, 'end', 
                                               text=desc, values=('',))
                
                # Añadir detalles del producto
                for key, value in product.items():
                    if key != 'descripcion':
                        self.tree.insert(product_node, 'end', 
                                       text=key, values=(str(value),))
        
        # Si hay más de 10 productos, mostrar un indicador
        if len(products) > 10:
            self.tree.insert(products_node, 'end', 
                           text=f"... y {len(products) - 10} productos más", 
                           values=('',))
    
    def show_info_dialog(self, title, message):
        """Muestra un diálogo de información"""
        messagebox.showinfo(title, message)
    
    def show_warning_dialog(self, title, message):
        """Muestra un diálogo de advertencia"""
        messagebox.showwarning(title, message)
    
    def show_error_dialog(self, title, message):
        """Muestra un diálogo de error"""
        messagebox.showerror(title, message)
    
    def ask_yes_no(self, title, message):
        """Muestra un diálogo de pregunta sí/no"""
        return messagebox.askyesno(title, message)
    
    def select_directory_dialog(self):
        """Muestra el diálogo de selección de directorio"""
        return filedialog.askdirectory(title="Seleccionar directorio con archivos HTML")
    
    def select_save_file_dialog(self, title, filetypes):
        """Muestra el diálogo de guardar archivo"""
        return filedialog.asksaveasfilename(title=title, filetypes=filetypes)
    
    def run_in_thread(self, target, *args, **kwargs):
        """Ejecuta una función en un hilo separado"""
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()
    
    def quit(self):
        """Cierra la aplicación"""
        self.root.quit()
