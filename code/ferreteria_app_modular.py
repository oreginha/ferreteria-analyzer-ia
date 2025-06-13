"""
Controlador Principal - Ferretería Analyzer con IA
================================================
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Importar módulos locales
from ferreteria_ui import FerreteriaUI
from extraer_datos import extraer_datos_html
from data_analyzer import analizar_datos_con_ia

class FerreteriaController:
    """Controlador principal de la aplicación"""
    
    def __init__(self):
        self.ui = None
        self.current_data = None
        self.analyzed_data = None
        self.api_key = ""
        self.custom_prompt = ""
        self.last_saved_file = None  # Para rastrear el último archivo guardado por el usuario
        
        # Configurar UI
        self.ui = FerreteriaUI(self)
        
        # Cargar configuración si existe
        self.load_config()
        
        # Log inicial
        self.log_message("🔧 Ferretería Analyzer con IA - Iniciado")
        self.log_message("📋 Pipeline disponible: Extracción → Análisis → Exportación")
    
    def log_message(self, message):
        """Registra un mensaje en el log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        if self.ui:
            self.ui.log_message(full_message)
        print(full_message)
    
    def select_directory(self):
        """Selecciona el directorio de trabajo"""
        directory = self.ui.select_directory_dialog()
        if directory:
            self.ui.update_directory_label(directory)
            self.log_message(f"📁 Directorio seleccionado: {directory}")
              # Verificar archivos HTML
            html_files = list(Path(directory).glob("*.htm*"))
            if html_files:
                self.log_message(f"✅ Encontrados {len(html_files)} archivos HTML")
            else:
                self.ui.show_warning_dialog("Advertencia", 
                    "No se encontraron archivos HTML en el directorio seleccionado")
        else:
            self.log_message("❌ Selección de directorio cancelada")
    
    def extract_data(self):
        """Extrae datos desde archivos HTML con diálogo para guardar archivo"""
        if not self.ui.selected_dir:
            self.ui.show_warning_dialog("Directorio requerido", 
                "Por favor selecciona un directorio primero")
            return
          # Mostrar diálogo para seleccionar dónde guardar el archivo
        import tkinter as tk
        from tkinter import filedialog
        
        # Sugerir nombre por defecto basado en el directorio
        dir_name = os.path.basename(self.ui.selected_dir)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"datos_extraidos_{dir_name}_{timestamp}.json"
        
        archivo_salida = filedialog.asksaveasfilename(
            title="Guardar datos extraídos como...",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_name
        )
        
        if not archivo_salida:
            self.log_message("❌ Extracción cancelada por el usuario")
            return
        
        def extract_worker():
            try:
                self.log_message("🔍 Iniciando extracción de datos...")
                self.log_message(f"💾 Archivo de salida: {archivo_salida}")
                
                # Usar el extractor existente con archivo personalizado
                data, archivo_guardado = extraer_datos_html(self.ui.selected_dir, archivo_salida)
                if data:
                    self.current_data = data
                    self.last_saved_file = archivo_guardado  # Guardar la ruta del archivo
                    
                    # Actualizar UI
                    self.ui.update_data_tree(data)
                    
                    # Mostrar resumen
                    total_productos = data.get('resumen', {}).get('total_productos', 0)
                    total_hojas = data.get('resumen', {}).get('total_hojas', 0)
                    
                    self.log_message(f"✅ Extracción completada:")
                    self.log_message(f"   📊 {total_hojas} hojas procesadas")
                    self.log_message(f"   🛍️ {total_productos} productos encontrados")
                    self.log_message(f"   💾 Guardado en: {archivo_guardado}")
                    
                    # También guardar una copia para la app (compatibilidad)
                    with open('datos_extraidos_app.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    self.log_message("💾 Datos guardados en 'datos_extraidos_app.json'")
                    
                    # Mostrar botón para abrir directorio del archivo
                    self.mostrar_boton_abrir_directorio(archivo_guardado)
                    
                else:
                    self.log_message("❌ No se pudieron extraer datos")
                    self.ui.show_error_dialog("Error", "No se pudieron extraer datos del directorio")
            except Exception as e:
                error_msg = f"Error durante la extracción: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.ui.show_error_dialog("Error", error_msg)
          # Ejecutar en hilo separado
        self.ui.run_in_thread(extract_worker)
    
    def analyze_with_ai(self):
        """Analiza los datos con IA"""
        # Verificar si tenemos datos extraídos
        if not self.current_data and not self.last_saved_file:
            self.ui.show_warning_dialog("Datos requeridos", 
                "No hay datos para analizar. Extrae datos primero.")
            return
        
        # Verificar API key
        if not self.api_key:
            if self.ui.ask_yes_no("API Key requerida", 
                "No hay API Key configurada. ¿Deseas configurarla ahora?"):
                self.configure_api_key()
                if not self.api_key:
                    return
            else:
                return
        
        # Preguntar qué datos usar si hay archivo guardado
        data_to_analyze = self.current_data
        if self.last_saved_file and os.path.exists(self.last_saved_file):
            if self.ui.ask_yes_no("Origen de datos", 
                f"¿Deseas analizar los datos del archivo que guardaste?\n\n{self.last_saved_file}\n\n(No = usar datos en memoria)"):
                try:
                    with open(self.last_saved_file, 'r', encoding='utf-8') as f:
                        data_to_analyze = json.load(f)
                    self.log_message(f"📁 Datos cargados desde: {self.last_saved_file}")
                except Exception as e:
                    self.log_message(f"❌ Error cargando archivo: {e}")
                    self.ui.show_error_dialog("Error", f"No se pudo cargar el archivo:\n{e}")
                    return
        def analyze_worker():
            try:
                import os
                from datetime import datetime
                
                self.log_message("🤖 Iniciando análisis con IA...")
                
                # Usar el analizador existente con API key y prompt personalizado
                analysis = analizar_datos_con_ia(
                    data_to_analyze, 
                    api_key=self.api_key,
                    custom_prompt=self.custom_prompt if self.custom_prompt else None
                )
                
                if analysis:
                    self.analyzed_data = analysis
                    
                    # Mostrar resultados del análisis
                    self.log_message("✅ Análisis con IA completado:")
                    
                    if 'resumen_general' in analysis:
                        resumen = analysis['resumen_general']
                        self.log_message(f"   📊 Total analizado: {resumen.get('total_productos', 0)} productos")
                        self.log_message(f"   💰 Rango de precios: {resumen.get('rango_precios', 'N/A')}")
                    
                    if 'recomendaciones' in analysis:
                        self.log_message(f"   💡 {len(analysis['recomendaciones'])} recomendaciones generadas")
                      # Preguntar dónde guardar el análisis
                    import tkinter.filedialog as filedialog
                    
                    # Sugerir nombre basado en el archivo original si existe
                    if self.last_saved_file:
                        base_name = os.path.splitext(os.path.basename(self.last_saved_file))[0]
                        suggested_name = f"analisis_IA_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    else:
                        suggested_name = f"analisis_IA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    archivo_analisis = filedialog.asksaveasfilename(
                        title="Guardar análisis con IA como...",
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                        initialfile=suggested_name
                    )
                    
                    if archivo_analisis:
                        # Guardar análisis en la ubicación elegida
                        with open(archivo_analisis, 'w', encoding='utf-8') as f:
                            json.dump(analysis, f, ensure_ascii=False, indent=2)
                        
                        self.log_message(f"💾 Análisis guardado en: {archivo_analisis}")
                        
                        # También guardar una copia para la app (compatibilidad)
                        with open('analisis_ia_app.json', 'w', encoding='utf-8') as f:
                            json.dump(analysis, f, ensure_ascii=False, indent=2)
                        
                        # Preguntar si abrir la ubicación del archivo
                        self.mostrar_boton_abrir_directorio(archivo_analisis)
                    else:
                        # Si cancela, solo guardar copia local
                        with open('analisis_ia_app.json', 'w', encoding='utf-8') as f:
                            json.dump(analysis, f, ensure_ascii=False, indent=2)
                        self.log_message("💾 Análisis guardado en 'analisis_ia_app.json'")
                    
                else:
                    self.log_message("❌ No se pudo completar el análisis")
                    self.ui.show_error_dialog("Error", "No se pudo completar el análisis con IA")
                
            except Exception as e:
                error_msg = f"Error durante el análisis: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.ui.show_error_dialog("Error", error_msg)
          # Ejecutar en hilo separado
        self.ui.run_in_thread(analyze_worker)
    
    def export_excel(self):
        """Exporta los datos a Excel"""
        # Verificar si tenemos datos
        if not self.current_data and not self.last_saved_file:
            self.ui.show_warning_dialog("Datos requeridos", 
                "No hay datos para exportar. Extrae datos primero.")
            return
        
        # Preguntar qué datos usar si hay archivo guardado
        data_to_export = self.current_data
        if self.last_saved_file and os.path.exists(self.last_saved_file):
            if self.ui.ask_yes_no("Origen de datos", 
                f"¿Deseas exportar los datos del archivo que guardaste?\n\n{self.last_saved_file}\n\n(No = usar datos en memoria)"):
                try:
                    with open(self.last_saved_file, 'r', encoding='utf-8') as f:
                        data_to_export = json.load(f)
                    self.log_message(f"📁 Datos cargados desde: {self.last_saved_file}")
                except Exception as e:
                    self.log_message(f"❌ Error cargando archivo: {e}")
                    self.ui.show_error_dialog("Error", f"No se pudo cargar el archivo:\n{e}")
                    return
        
        if not data_to_export:
            self.ui.show_warning_dialog("Datos requeridos", 
                "No hay datos válidos para exportar.")
            return
        
        # Seleccionar archivo de destino
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"ferreteria_procesada_{timestamp}.xlsx"
        
        filename = self.ui.select_save_file_dialog(
            "Guardar archivo Excel",
            [("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )
        
        if not filename:
            self.log_message("❌ Exportación cancelada")
            return
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        def export_worker():
            try:
                self.log_message("📊 Iniciando exportación a Excel...")
                
                # Crear archivo Excel con múltiples hojas
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    
                    # Hoja de resumen
                    resumen_data = {
                        'Métrica': ['Total Productos', 'Total Hojas', 'Fecha Procesamiento'],
                        'Valor': [
                            data_to_export.get('resumen', {}).get('total_productos', 0),
                            data_to_export.get('resumen', {}).get('total_hojas', 0),
                            data_to_export.get('fecha_procesamiento', datetime.now().isoformat())
                        ]
                    }
                    
                    df_resumen = pd.DataFrame(resumen_data)
                    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    # Hojas por categoría
                    for i, hoja in enumerate(data_to_export.get('hojas', [])):
                        if 'productos' in hoja and hoja['productos']:
                            df_productos = pd.DataFrame(hoja['productos'])
                            
                            # Limpiar nombre de hoja para Excel
                            sheet_name = hoja.get('nombre', f'Hoja_{i+1}')
                            sheet_name = sheet_name[:31]  # Límite de Excel
                            sheet_name = ''.join(c for c in sheet_name if c.isalnum() or c in ' _-')
                            
                            df_productos.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Hoja de análisis si existe
                    if self.analyzed_data:
                        try:
                            analysis_summary = {
                                'Análisis': ['Total Analizado', 'Recomendaciones', 'Fecha Análisis'],
                                'Resultado': [
                                    self.analyzed_data.get('resumen_general', {}).get('total_productos', 0),
                                    len(self.analyzed_data.get('recomendaciones', [])),
                                    datetime.now().strftime("%Y-%m-%d %H:%M")
                                ]
                            }
                            df_analysis = pd.DataFrame(analysis_summary)
                            df_analysis.to_excel(writer, sheet_name='Análisis IA', index=False)
                        except:
                            pass
                
                self.log_message(f"✅ Archivo Excel creado: {filename}")
                self.log_message(f"📁 Archivo guardado en: {Path(filename).absolute()}")
                  # Mostrar estadísticas de exportación
                total_hojas = len(data_to_export.get('hojas', []))
                total_productos = data_to_export.get('resumen', {}).get('total_productos', 0)
                
                self.log_message(f"📊 Exportación completada:")
                self.log_message(f"   📋 {total_hojas} hojas exportadas")
                self.log_message(f"   🛍️ {total_productos} productos incluidos")
                
                self.ui.show_info_dialog("Exportación completada", 
                    f"Archivo Excel creado exitosamente:\n{filename}")
                
            except Exception as e:
                error_msg = f"Error durante la exportación: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.ui.show_error_dialog("Error", error_msg)
        
        # Ejecutar en hilo separado
        self.ui.run_in_thread(export_worker)
    
    def mostrar_boton_abrir_directorio(self, archivo_guardado):
        """Muestra un botón para abrir el directorio donde se guardó el archivo"""
        import subprocess
        import os
        
        def abrir_directorio():
            try:
                # Normalizar la ruta para Windows
                archivo_normalizado = os.path.normpath(os.path.abspath(archivo_guardado))
                directorio = os.path.dirname(archivo_normalizado)
                
                self.log_message(f"📂 Intentando abrir: {archivo_normalizado}")
                
                # Abrir el directorio en el explorador de archivos
                if os.name == 'nt':  # Windows
                    # Usar explorer con /select para resaltar el archivo
                    subprocess.run(['explorer', '/select', archivo_normalizado], check=True)
                else:  # macOS y Linux
                    import sys
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', '-R', archivo_normalizado], check=True)
                    else:  # Linux
                        subprocess.run(['xdg-open', directorio], check=True)
                
                self.log_message(f"✅ Directorio abierto correctamente")
                
            except Exception as e:
                # Si falla el comando con /select, intentar abrir solo el directorio
                try:
                    directorio = os.path.dirname(os.path.abspath(archivo_guardado))
                    self.log_message(f"📂 Intentando plan B - abrir directorio: {directorio}")
                    
                    if os.name == 'nt':
                        subprocess.run(['explorer', directorio], check=True)
                    else:
                        subprocess.run(['xdg-open', directorio], check=True)
                    self.log_message(f"✅ Directorio abierto (sin resaltar archivo)")
                except Exception as e2:
                    self.log_message(f"❌ Error al abrir directorio: {str(e2)}")
                    # Como último recurso, copiar ruta al clipboard si es posible
                    try:
                        import tkinter as tk
                        root = tk.Tk()
                        root.withdraw()
                        root.clipboard_clear()
                        root.clipboard_append(archivo_guardado)
                        root.update()
                        root.destroy()
                        self.log_message(f"📋 Ruta copiada al portapapeles: {archivo_guardado}")
                    except:
                        self.log_message(f"📁 Ubicación del archivo: {archivo_guardado}")
        
        # Agregar botón a la UI si tiene método para ello
        if hasattr(self.ui, 'add_action_button'):
            self.ui.add_action_button("📂 Abrir ubicación del archivo", abrir_directorio)
        else:
            # Log alternativo si no hay método en UI
            self.log_message("📂 Tip: El archivo se guardó en:")
            self.log_message(f"   {archivo_guardado}")
            
            # Mostrar diálogo con opción para abrir
            import tkinter.messagebox as msgbox
            result = msgbox.askyesno(
                "Archivo guardado", 
                f"El archivo se guardó exitosamente en:\n\n{archivo_guardado}\n\n¿Deseas abrir la ubicación del archivo?",
                icon='question'
            )
            if result:
                abrir_directorio()
    
    def configure_api_key(self):
        """Configura la API key de Gemini"""
        import tkinter.simpledialog as simpledialog
        
        current_key = "***configurada***" if self.api_key else "No configurada"
        new_key = simpledialog.askstring(
            "Configurar API Key",
            f"API Key actual: {current_key}\n\nIngresa tu API Key de Google Gemini:",
            show='*'
        )
        
        if new_key and new_key.strip():
            self.api_key = new_key.strip()
            self.log_message("🔑 API Key configurada correctamente")
            
            # Guardar en archivo de configuración
            try:
                import json
                config = {"api_key": self.api_key}
                with open("config.json", "w") as f:
                    json.dump(config, f)
                self.log_message("💾 Configuración guardada en config.json")
            except Exception as e:
                self.log_message(f"⚠️ No se pudo guardar la configuración: {e}")
        else:
            self.log_message("❌ Configuración de API Key cancelada")
    
    def load_config(self):
        """Carga la configuración guardada"""
        try:
            import json
            with open("config.json", "r") as f:
                config = json.load(f)
                self.api_key = config.get("api_key", "")
                if self.api_key:
                    self.log_message("📁 API Key cargada desde config.json")
        except FileNotFoundError:
            self.log_message("📝 No se encontró archivo de configuración")
        except Exception as e:
            self.log_message(f"❌ Error cargando configuración: {e}")
    
    def configure_custom_prompt(self):
        """Configura el prompt personalizado para el análisis con IA"""
        import tkinter as tk
        
        # Crear ventana para prompt personalizado
        prompt_window = tk.Toplevel(self.ui.root)
        prompt_window.title("Configurar Prompt Personalizado")
        prompt_window.geometry("600x400")
        prompt_window.resizable(True, True)
        
        # Frame principal
        main_frame = tk.Frame(prompt_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Etiqueta de instrucciones
        instructions = tk.Label(
            main_frame,
            text="Personaliza el prompt para el análisis con IA:\n(Deja vacío para usar el prompt por defecto)",
            font=('Arial', 10),
            justify=tk.LEFT
        )
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # Text widget para el prompt
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        prompt_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=prompt_text.yview)
        prompt_text.configure(yscrollcommand=scrollbar.set)
        
        # Insertar prompt actual
        if self.custom_prompt:
            prompt_text.insert(tk.END, self.custom_prompt)
        else:
            # Mostrar prompt por defecto como ejemplo
            default_prompt = """Analiza los siguientes datos de productos de ferretería y proporciona:

1. Resumen general de productos y categorías
2. Análisis de precios por categoría
3. Productos más caros y más baratos
4. Recomendaciones de inventario
5. Insights sobre el negocio

Datos de productos:
{productos_data}

Responde en formato estructurado y profesional."""
            prompt_text.insert(tk.END, default_prompt)
        
        prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_prompt():
            new_prompt = prompt_text.get(1.0, tk.END).strip()
            self.custom_prompt = new_prompt
            
            if new_prompt:
                self.log_message("📝 Prompt personalizado configurado")
            else:
                self.log_message("📝 Se usará el prompt por defecto")
            
            prompt_window.destroy()
        
        def cancel():
            prompt_window.destroy()
        
        def reset_to_default():
            prompt_text.delete(1.0, tk.END)
            self.custom_prompt = ""
            self.log_message("🔄 Prompt restablecido al valor por defecto")
            prompt_window.destroy()
        
        tk.Button(button_frame, text="💾 Guardar", command=save_prompt).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="❌ Cancelar", command=cancel).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="🔄 Por Defecto", command=reset_to_default).pack(side=tk.LEFT)
        
        # Centrar ventana
        prompt_window.transient(self.ui.root)
        prompt_window.grab_set()
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.ui.run()
        except Exception as e:
            print(f"Error ejecutando la aplicación: {e}")

def main():
    """Función principal"""
    try:
        app = FerreteriaController()
        app.run()
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
