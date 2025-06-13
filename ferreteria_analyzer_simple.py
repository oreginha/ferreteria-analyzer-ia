#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versión simplificada del analizador que funciona sin IA
Para casos donde hay problemas con la API de Gemini
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import threading
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import Counter

class FerreteriaAnalyzerSimple:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Planillas de Ferretería (Versión Simple)")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.current_data = None
        self.selected_directory = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración de la grilla
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔧 Analizador de Planillas (Sin IA)", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Directorio de trabajo
        ttk.Label(config_frame, text="Directorio:").grid(row=0, column=0, sticky=tk.W)
        dir_entry = ttk.Entry(config_frame, textvariable=self.selected_directory, state="readonly")
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(config_frame, text="Seleccionar", 
                  command=self.select_directory).grid(row=0, column=2, padx=(5, 0))
        
        # Botones de acción
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(actions_frame, text="🔍 Extraer Datos con Detección Inteligente", 
                  command=self.extract_data).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="💾 Exportar Excel", 
                  command=self.export_excel).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="📊 Ver Estadísticas", 
                  command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                     font=('Consolas', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo - Versión sin IA")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def select_directory(self):
        """Selecciona el directorio de trabajo"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con archivos HTML")
        if directory:
            self.selected_directory.set(directory)
            self.log_message(f"📁 Directorio seleccionado: {directory}")
    
    def log_message(self, message):
        """Registra un mensaje en el área de resultados"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Actualiza la barra de estado"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def extract_data(self):
        """Extrae datos con análisis inteligente de proveedores"""
        selected_dir = self.selected_directory.get()
        if not selected_dir:
            messagebox.showerror("Error", "Por favor selecciona un directorio")
            return
            
        def extract_thread():
            try:
                self.update_status("Extrayendo datos...")
                self.log_message("🔍 Iniciando extracción de datos con análisis inteligente...")
                self.log_message(f"📂 Directorio de trabajo: {selected_dir}")
                
                # Verificar que el directorio existe
                if not os.path.exists(selected_dir):
                    self.log_message(f"❌ Error: El directorio no existe: {selected_dir}")
                    self.update_status("Error: Directorio no existe")
                    return
                    
                # Ejecutar extracción de datos con análisis inteligente
                data = self.extract_html_data_intelligent(selected_dir)
                if data:
                    self.current_data = data
                    
                    # Mostrar información de la estrategia de proveedores
                    estrategia = data.get('estrategia_proveedores', 'unknown')
                    proveedor_principal = data.get('proveedor_principal', 'No detectado')
                    
                    if estrategia == 'single_provider':
                        self.log_message(f"📊 Estrategia detectada: UN SOLO PROVEEDOR ({proveedor_principal})")
                        self.log_message("📝 Las hojas se han nombrado como listas del mismo proveedor")
                    elif estrategia == 'multiple_providers':
                        self.log_message(f"📊 Estrategia detectada: MÚLTIPLES PROVEEDORES")
                        self.log_message(f"📝 Proveedor principal: {proveedor_principal}")
                    else:
                        self.log_message(f"📊 Estrategia: Proveedores no identificados")
                    
                    self.log_message(f"✅ Extracción completada: {len(data['hojas'])} hojas procesadas")
                    
                    # Guardar datos en el directorio seleccionado
                    output_file = os.path.join(selected_dir, "datos_extraidos_simple.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        self.log_message(f"💾 Datos guardados en: {output_file}")
                    
                    # Mostrar resumen
                    self.mostrar_resumen_datos()
                    self.update_status("Extracción completada")
                else:
                    self.log_message("❌ No se pudieron extraer datos")
                    self.update_status("Error en extracción")
                    
            except Exception as e:
                self.log_message(f"❌ Error en extracción: {str(e)}")
                self.update_status("Error en extracción")
                
        threading.Thread(target=extract_thread, daemon=True).start()
    
    def extract_html_data_intelligent(self, directory):
        """Extrae datos con análisis inteligente de proveedores"""
        # Detectar archivos HTML
        html_files = []
        try:
            for file in os.listdir(directory):
                if file.lower().endswith(('.htm', '.html')) and not file.lower() in ['tabstrip.htm', 'filelist.xml']:
                    html_files.append(file)
            html_files.sort()
        except Exception as e:
            self.log_message(f"❌ Error listando archivos: {str(e)}")
            return None
        
        if not html_files:
            self.log_message("❌ No se encontraron archivos HTML en el directorio")
            return None
        
        self.log_message(f"📁 Archivos HTML detectados: {len(html_files)}")
        for file in html_files:
            self.log_message(f"   • {file}")
        
        # Análisis de proveedores en cada archivo
        self.log_message("🔍 Analizando contenido para detectar proveedores...")
        analisis_por_archivo = {}
        todos_los_proveedores = []
        
        for archivo in html_files:
            ruta_completa = os.path.join(directory, archivo)
            proveedores = self.detectar_proveedores_en_contenido(ruta_completa)
            analisis_por_archivo[archivo] = proveedores
            
            for proveedor in proveedores:
                todos_los_proveedores.append(proveedor['nombre'])
        
        # Determinar estrategia
        contador_proveedores = Counter(todos_los_proveedores)
        
        if not contador_proveedores:
            estrategia = 'multiple_unknown'
            proveedor_principal = None
            self.log_message("⚠️  No se detectaron proveedores conocidos")
        else:
            proveedor_principal, frecuencia_principal = contador_proveedores.most_common(1)[0]
            total_archivos = len(html_files)
            porcentaje_dominancia = (frecuencia_principal / total_archivos) * 100
            
            self.log_message(f"📊 Análisis de proveedores:")
            self.log_message(f"   • Proveedor dominante: {proveedor_principal} ({frecuencia_principal}/{total_archivos} archivos, {porcentaje_dominancia:.1f}%)")
            
            if porcentaje_dominancia >= 70:
                estrategia = 'single_provider'
                self.log_message(f"✅ Estrategia: UN SOLO PROVEEDOR con múltiples listas")
            else:
                estrategia = 'multiple_providers'
                self.log_message(f"✅ Estrategia: MÚLTIPLES PROVEEDORES")
                
                # Mostrar otros proveedores
                self.log_message("   • Otros proveedores detectados:")
                for proveedor, count in contador_proveedores.most_common()[1:]:
                    porcentaje = (count / total_archivos) * 100
                    self.log_message(f"     - {proveedor}: {count} archivo(s) ({porcentaje:.1f}%)")
        
        # Determinar nombre de planilla
        planilla_name = os.path.basename(directory).replace('_archivos', '').replace('_files', '')
        if not planilla_name or planilla_name == '.':
            planilla_name = 'ANALISIS_HTML'
        
        # Estructura de datos completa
        datos_completos = {
            'planilla': planilla_name.upper(),
            'directorio': directory,
            'fecha_extraccion': datetime.now().isoformat(),
            'total_hojas': len(html_files),
            'estrategia_proveedores': estrategia,
            'proveedor_principal': proveedor_principal,
            'analisis_proveedores': analisis_por_archivo,
            'hojas': []
        }
        
        # Procesar cada archivo con nomenclatura inteligente
        self.log_message("📝 Procesando archivos:")
        for i, html_file in enumerate(html_files):
            archivo_path = os.path.join(directory, html_file)
            proveedores_archivo = analisis_por_archivo.get(html_file, [])
            
            nombre_hoja = self.generar_nombre_hoja_inteligente(
                html_file, i, estrategia, proveedor_principal, proveedores_archivo
            )
            
            if os.path.exists(archivo_path):
                hoja_data = self.procesar_hoja_html(archivo_path, nombre_hoja)
                if hoja_data:
                    # Agregar información del análisis de proveedores
                    hoja_data['proveedores_detectados'] = proveedores_archivo
                    datos_completos['hojas'].append(hoja_data)
                    self.log_message(f"   📄 {nombre_hoja}: {hoja_data['total_tablas']} tabla(s)")
            else:
                self.log_message(f"   ⚠️ Archivo no encontrado: {html_file}")
        
        return datos_completos
    
    def detectar_proveedores_en_contenido(self, ruta_archivo):
        """Detecta proveedores en el contenido de un archivo"""
        proveedores_encontrados = []
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
                contenido = archivo.read()
            
            soup = BeautifulSoup(contenido, 'html.parser')
            
            # Lista de proveedores conocidos
            proveedores_conocidos = [
                'CRIMARAL', 'ANCAIG', 'DAFYS', 'HERRAMETAL', 'YAYI', 
                'DIST_CITY_BELL', 'BABUSI', 'FERRIPLAST', 'FERRETERIA',
                'DISTCITYBELL', 'CITY_BELL', 'DISTRIBUIDORA',
                'BRIMAX', 'PUMA', 'ROTAFLEX', 'STANLEY', 'BLACK_DECKER'
            ]
            
            texto_completo = soup.get_text().upper()
            
            for proveedor in proveedores_conocidos:
                if proveedor in texto_completo:
                    ocurrencias = texto_completo.count(proveedor)
                    proveedores_encontrados.append({
                        'nombre': proveedor,
                        'ocurrencias': ocurrencias,
                        'confianza': min(ocurrencias / 10, 1.0)
                    })
            
            # Buscar emails para detectar proveedores por dominio
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', texto_completo)
            for email in emails:
                domain_part = email.split('@')[1].split('.')[0].upper()
                if len(domain_part) > 3 and domain_part not in [p['nombre'] for p in proveedores_encontrados]:
                    proveedores_encontrados.append({
                        'nombre': domain_part,
                        'ocurrencias': 1,
                        'confianza': 0.8,
                        'tipo': 'email'
                    })
            
            # Ordenar por confianza/ocurrencias
            proveedores_encontrados.sort(key=lambda x: (x['confianza'], x['ocurrencias']), reverse=True)
            
            return proveedores_encontrados
            
        except Exception as e:
            self.log_message(f"Error analizando {ruta_archivo}: {str(e)}")
            return []
    
    def generar_nombre_hoja_inteligente(self, archivo, indice, estrategia, proveedor_principal, proveedores_archivo):
        """Genera nombres de hoja basados en la estrategia detectada"""
        
        if estrategia == 'single_provider':
            # Todas las hojas son del mismo proveedor - usar nomenclatura de listas
            if proveedores_archivo and proveedores_archivo[0]['confianza'] > 0.7:
                return f"{proveedor_principal}_LISTA_{indice + 1:02d}"
            else:
                return f"{proveedor_principal}_HOJA_{indice + 1:02d}"
        
        elif estrategia == 'multiple_providers':
            # Múltiples proveedores - usar el nombre específico detectado
            if proveedores_archivo and proveedores_archivo[0]['confianza'] > 0.5:
                return proveedores_archivo[0]['nombre']
            else:
                # Fallback al mapeo conocido
                mapeo_fallback = {
                    'sheet001.htm': 'PROVEEDOR_01',
                    'sheet002.htm': 'PROVEEDOR_02', 
                    'sheet003.htm': 'PROVEEDOR_03',
                    'sheet004.htm': 'PROVEEDOR_04',
                    'sheet005.htm': 'PROVEEDOR_05',
                    'sheet006.htm': 'PROVEEDOR_06',
                    'sheet007.htm': 'PROVEEDOR_07',
                    'sheet008.htm': 'PROVEEDOR_08',
                    'sheet009.htm': 'PROVEEDOR_09'
                }
                return mapeo_fallback.get(archivo, f'PROVEEDOR_{indice + 1:02d}')
        
        else:  # 'multiple_unknown'
            # No se detectaron proveedores conocidos
            nombre = os.path.splitext(archivo)[0]
            if nombre.startswith('sheet'):
                numero = nombre.replace('sheet', '').replace('0', '')
                return f'HOJA_{numero.zfill(2)}'
            return nombre.upper()
    
    def procesar_hoja_html(self, archivo_path, nombre_hoja):
        """Procesa una hoja HTML individual"""
        try:
            with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as archivo:
                contenido = archivo.read()
                
            soup = BeautifulSoup(contenido, 'html.parser')
            tablas = soup.find_all('table')
            
            datos_tablas = []
            for i, tabla in enumerate(tablas):
                filas = tabla.find_all('tr')
                if not filas:
                    continue
                    
                datos_tabla = []
                for fila in filas:
                    celdas = fila.find_all(['td', 'th'])
                    fila_datos = []
                    
                    for celda in celdas:
                        texto = self.limpiar_texto(celda.get_text())
                        fila_datos.append(texto)
                    
                    # Solo agregar filas que tengan contenido significativo
                    if any(celda.strip() for celda in fila_datos if celda):
                        datos_tabla.append(fila_datos)
                
                if datos_tabla:
                    datos_tablas.append({
                        'tabla_indice': i,
                        'filas': datos_tabla,
                        'total_filas': len(datos_tabla),
                        'total_columnas': max(len(fila) for fila in datos_tabla) if datos_tabla else 0
                    })
            
            return {
                'hoja': nombre_hoja,
                'archivo': os.path.basename(archivo_path),
                'total_tablas': len(datos_tablas),
                'tablas': datos_tablas,
                'procesado_en': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log_message(f"Error procesando {nombre_hoja}: {str(e)}")
            return None
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza texto"""
        if not texto:
            return ""
        texto = re.sub(r'\s+', ' ', texto.strip())
        texto = texto.replace('\xa0', ' ')
        return texto
    
    def mostrar_resumen_datos(self):
        """Muestra un resumen de los datos extraídos"""
        if not self.current_data:
            return
            
        self.log_message("\n" + "=" * 50)
        self.log_message("📊 RESUMEN DE DATOS EXTRAÍDOS")
        self.log_message("=" * 50)
        
        estrategia = self.current_data.get('estrategia_proveedores', 'No especificada')
        proveedor_principal = self.current_data.get('proveedor_principal', 'No detectado')
        
        self.log_message(f"📋 Planilla: {self.current_data['planilla']}")
        self.log_message(f"🎯 Estrategia: {estrategia}")
        if proveedor_principal:
            self.log_message(f"🏪 Proveedor principal: {proveedor_principal}")
        self.log_message(f"📄 Total hojas: {len(self.current_data['hojas'])}")
        
        total_productos = sum(sum(tabla['total_filas'] for tabla in hoja['tablas']) for hoja in self.current_data['hojas'])
        self.log_message(f"📦 Total productos: {total_productos:,}")
        
        self.log_message("\n📋 Detalle por hoja:")
        for hoja in self.current_data['hojas']:
            productos_hoja = sum(tabla['total_filas'] for tabla in hoja['tablas'])
            proveedores_info = ""
            if hoja.get('proveedores_detectados'):
                top_proveedor = hoja['proveedores_detectados'][0]
                proveedores_info = f" (confianza: {top_proveedor['confianza']:.2f})"
            self.log_message(f"  • {hoja['hoja']}: {productos_hoja:,} productos{proveedores_info}")
    
    def export_excel(self):
        """Exporta datos a Excel"""
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
            
        try:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar como Excel"
            )
            
            if output_file:
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    # Hoja de resumen
                    resumen_data = []
                    for hoja in self.current_data['hojas']:
                        productos = sum(tabla['total_filas'] for tabla in hoja['tablas'])
                        estrategia = self.current_data.get('estrategia_proveedores', 'No especificada')
                        proveedor_detectado = ""
                        if hoja.get('proveedores_detectados'):
                            proveedor_detectado = hoja['proveedores_detectados'][0]['nombre']
                        
                        resumen_data.append({
                            'Hoja': hoja['hoja'],
                            'Productos': productos,
                            'Tablas': hoja['total_tablas'],
                            'Proveedor_Detectado': proveedor_detectado,
                            'Estrategia': estrategia,
                            'Archivo': hoja['archivo']
                        })
                    
                    df_resumen = pd.DataFrame(resumen_data)
                    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    # Hojas individuales (primeras 5 para evitar archivos muy grandes)
                    for i, hoja in enumerate(self.current_data['hojas'][:5]):
                        if hoja['tablas']:
                            tabla_principal = hoja['tablas'][0]
                            if tabla_principal['filas']:
                                df = pd.DataFrame(tabla_principal['filas'])
                                sheet_name = hoja['hoja'][:30]  # Limitar nombre
                                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                
                self.log_message(f"📊 Exportado a Excel: {output_file}")
                messagebox.showinfo("Éxito", "Datos exportados a Excel correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando a Excel: {str(e)}")
    
    def show_statistics(self):
        """Muestra estadísticas detalladas"""
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
        
        self.mostrar_resumen_datos()

def main():
    """Función principal"""
    root = tk.Tk()
    app = FerreteriaAnalyzerSimple(root)
    root.mainloop()

if __name__ == "__main__":
    main()
