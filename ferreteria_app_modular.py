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
from purificador_datos import PurificadorDatos
from ferreteria_ui import FerreteriaUI
from extraer_datos import extraer_datos_html
from data_analyzer import analizar_datos_con_ia

class FerreteriaController:
    """Controlador principal de la aplicación"""
    
    def __init__(self):
        self.ui = None
        self.current_data = None
        self.purified_data = None
        self.analyzed_data = None
        self.purificador = PurificadorDatos()
        
        # Configurar UI
        self.ui = FerreteriaUI(self)
        
        # Log inicial
        self.log_message("🔧 Ferretería Analyzer con IA - Iniciado")
        self.log_message("📋 Pipeline disponible: Extracción → Purificación → Análisis → Exportación")
    
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
        """Extrae datos desde archivos HTML"""
        if not self.ui.selected_dir:
            self.ui.show_warning_dialog("Directorio requerido", 
                "Por favor selecciona un directorio primero")
            return
        
        def extract_worker():
            try:
                self.log_message("🔍 Iniciando extracción de datos...")
                
                # Usar el extractor existente
                data = extraer_datos_html(self.ui.selected_dir)
                
                if data:
                    self.current_data = data
                    
                    # Actualizar UI
                    self.ui.update_data_tree(data)
                    
                    # Mostrar resumen
                    total_productos = data.get('resumen', {}).get('total_productos', 0)
                    total_hojas = data.get('resumen', {}).get('total_hojas', 0)
                    
                    self.log_message(f"✅ Extracción completada:")
                    self.log_message(f"   📊 {total_hojas} hojas procesadas")
                    self.log_message(f"   🛍️ {total_productos} productos encontrados")
                    
                    # Guardar datos extraídos
                    with open('datos_extraidos_app.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    self.log_message("💾 Datos guardados en 'datos_extraidos_app.json'")
                    
                else:
                    self.log_message("❌ No se pudieron extraer datos")
                    self.ui.show_error_dialog("Error", "No se pudieron extraer datos del directorio")
                
            except Exception as e:
                error_msg = f"Error durante la extracción: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.ui.show_error_dialog("Error", error_msg)
        
        # Ejecutar en hilo separado
        self.ui.run_in_thread(extract_worker)
    
    def purify_data(self):
        """Purifica los datos extraídos"""
        if not self.current_data:
            if self.ui.ask_yes_no("Datos no encontrados", 
                "No hay datos extraídos. ¿Deseas cargar desde 'datos_extraidos_app.json'?"):
                try:
                    with open('datos_extraidos_app.json', 'r', encoding='utf-8') as f:
                        self.current_data = json.load(f)
                    self.log_message("📂 Datos cargados desde archivo")
                except:
                    self.ui.show_error_dialog("Error", "No se pudo cargar el archivo de datos")
                    return
            else:
                return
        
        def purify_worker():
            try:
                self.log_message("🧹 Iniciando purificación de datos...")
                
                # Reiniciar estadísticas
                self.purificador.reiniciar_estadisticas()
                
                # Purificar datos
                self.purified_data = self.purificador.purificar_datos_completos(self.current_data)
                
                # Obtener estadísticas
                stats = self.purificador.obtener_estadisticas()
                
                # Actualizar UI con datos purificados
                self.ui.update_data_tree(self.purified_data)
                
                # Mostrar estadísticas
                self.log_message("✅ Purificación completada:")
                self.log_message(f"   ✅ {stats['productos_procesados']} productos válidos")
                self.log_message(f"   🗑️ {stats['productos_eliminados']} productos eliminados")
                self.log_message(f"   🔄 {stats['duplicados_removidos']} duplicados removidos")
                self.log_message(f"   📂 {stats['categorias_detectadas']} categorías detectadas")
                
                # Guardar datos purificados
                with open('datos_purificados_app.json', 'w', encoding='utf-8') as f:
                    json.dump(self.purified_data, f, ensure_ascii=False, indent=2)
                
                self.log_message("💾 Datos purificados guardados en 'datos_purificados_app.json'")
                
                # Mostrar resumen de mejora
                productos_originales = self.current_data.get('resumen', {}).get('total_productos', 0)
                productos_purificados = self.purified_data.get('resumen', {}).get('total_productos', 0)
                mejora = ((productos_originales - productos_purificados) / productos_originales * 100) if productos_originales > 0 else 0
                
                self.log_message(f"📈 Calidad mejorada en {mejora:.1f}% (limpieza de datos)")
                
            except Exception as e:
                error_msg = f"Error durante la purificación: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.ui.show_error_dialog("Error", error_msg)
        
        # Ejecutar en hilo separado
        self.ui.run_in_thread(purify_worker)
    
    def analyze_with_ai(self):
        """Analiza los datos con IA"""
        # Priorizar datos purificados
        data_to_analyze = self.purified_data if self.purified_data else self.current_data
        
        if not data_to_analyze:
            self.ui.show_warning_dialog("Datos requeridos", 
                "No hay datos para analizar. Extrae y purifica datos primero.")
            return
        
        if not self.purified_data:
            if self.ui.ask_yes_no("Usar datos purificados", 
                "Se recomienda purificar los datos antes del análisis. ¿Deseas purificar ahora?"):
                self.purify_data()
                return
        
        def analyze_worker():
            try:
                self.log_message("🤖 Iniciando análisis con IA...")
                
                # Usar el analizador existente
                analysis = analizar_datos_con_ia(data_to_analyze)
                
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
                    
                    # Guardar análisis
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
        # Priorizar datos purificados
        data_to_export = self.purified_data if self.purified_data else self.current_data
        
        if not data_to_export:
            self.ui.show_warning_dialog("Datos requeridos", 
                "No hay datos para exportar. Extrae datos primero.")
            return
        
        if not self.purified_data:
            if self.ui.ask_yes_no("Usar datos purificados", 
                "Se recomienda exportar datos purificados. ¿Deseas purificar ahora?"):
                self.purify_data()
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
