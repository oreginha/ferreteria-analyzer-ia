#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación de Escritorio para Análisis de Planillas de Ferretería con IA
Utiliza la API de Gemini para análisis inteligente de datos
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import threading
from datetime import datetime
import google.generativeai as genai
from bs4 import BeautifulSoup
import pandas as pd
import re
import webbrowser

# Importar el purificador de datos
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Clase del purificador (integrada directamente)
class PurificadorDatos:
    def __init__(self):
        # Patrones para identificar filas irrelevantes
        self.patrones_irrelevantes = [
            r'BUSCADOR RAPIDO',
            r'distribuidora.*@.*\.com',
            r'Precios orientativos',
            r'CALCULADORA',
            r'COMPLETAR DONDE',
            r'FUNCIONAMIENTO',
            r'INGRESAR.*CENTIMETROS',
            r'MARGEN DE GANANCIA',
            r'POR DEFECTO',
            r'Recuerde que',
            r'UwU',
            r'AQU VER LA',
            r'CODIGO.*DESCRIPCION.*BASE',
            r'ESCRIBA AQUI MISMO',
            r'DIAMETRO DEL',
            r'CUANTO COBRAR',
            r'PESTAA para actualizacion',
            r'^YAYI$',
            r'^DESCRIPCION$',
            r'^CODIGO$',
            r'^BASE$',
            r'^PUBLICO$',
            r'^\.$',
            r'^-$',
            r'^\+$',
            r'OFERTAS',
            r'FECHA',
            r'% GANANCIA',
            r'SIN IVA',
            r'COSTO FINAL',
            r'CON OFERTAS'
        ]
        
        # Patrones para identificar campos específicos
        self.patron_codigo = re.compile(r'^[0-9]{6,8}$')
        self.patron_precio = re.compile(r'^[\d\.,]+$')
        self.patron_moneda = re.compile(r'[\$\s]*[\d\.,]+')
        self.patron_iva = re.compile(r'^[0-9]{1,2}$')
        self.patron_medida = re.compile(r'\d+/\d+|\d+x\d+|\d+mm|\d+cm|\d+"')
        
    def es_fila_irrelevante(self, fila):
        """Determina si toda la fila es irrelevante"""
        texto_fila = ' '.join(str(cell) for cell in fila).strip()
        
        # Si la fila está mayormente vacía
        celdas_vacias = sum(1 for cell in fila if not str(cell).strip())
        if celdas_vacias > len(fila) * 0.7:
            return True
            
        # Verificar patrones irrelevantes
        for patron in self.patrones_irrelevantes:
            if re.search(patron, texto_fila, re.IGNORECASE):
                return True
        
        return False
    
    def extraer_codigo(self, fila):
        """Extrae código de producto de una fila"""
        for cell in fila:
            cell_str = str(cell).strip()
            if self.patron_codigo.match(cell_str):
                return cell_str
        return None
    
    def extraer_descripcion(self, fila):
        """Extrae descripción de producto de una fila"""
        candidatos = []
        
        for cell in fila:
            cell_str = str(cell).strip()
            
            # Descartar si es muy corto, muy largo, o contiene patrones irrelevantes
            if len(cell_str) < 3 or len(cell_str) > 80:
                continue
                
            # Descartar códigos, precios, y otros campos específicos
            if (self.patron_codigo.match(cell_str) or 
                self.patron_precio.match(cell_str) or
                self.patron_iva.match(cell_str) or
                cell_str in ['.', '-', '+', '$']):
                continue
            
            # Descartar patrones irrelevantes
            es_irrelevante = False
            for patron in self.patrones_irrelevantes:
                if re.search(patron, cell_str, re.IGNORECASE):
                    es_irrelevante = True
                    break
            
            if not es_irrelevante:
                candidatos.append(cell_str)
        
        # Devolver la descripción más larga y específica
        if candidatos:
            return max(candidatos, key=len)
        return None
    
    def extraer_precios(self, fila):
        """Extrae precios de una fila"""
        precios = []
        
        for cell in fila:
            cell_str = str(cell).strip()
            
            # Buscar números que podrían ser precios
            if self.patron_moneda.match(cell_str):
                # Limpiar precio
                precio_limpio = re.sub(r'[^\d,.]', '', cell_str)
                
                # Verificar que no sea un código o valor muy pequeño
                if (precio_limpio and 
                    not self.patron_codigo.match(precio_limpio) and
                    ',' in precio_limpio or '.' in precio_limpio):
                    
                    # Convertir a float para validar
                    try:
                        valor_num = float(precio_limpio.replace(',', '.'))
                        if valor_num > 0.01:  # Precio mínimo razonable
                            precios.append(precio_limpio)
                    except:
                        continue
        
        return precios if precios else None
    
    def extraer_iva(self, fila):
        """Extrae porcentaje de IVA de una fila"""
        for cell in fila:
            cell_str = str(cell).strip()
            if self.patron_iva.match(cell_str):
                try:
                    valor = int(cell_str)
                    if 0 <= valor <= 50:  # Rango razonable para IVA
                        return valor
                except:
                    continue
        return None
    
    def extraer_medida(self, fila):
        """Extrae medidas de una fila"""
        for cell in fila:
            cell_str = str(cell).strip()
            if self.patron_medida.search(cell_str):
                return cell_str
        return None
    
    def procesar_fila(self, fila):
        """Procesa una fila y extrae información del producto"""
        # Verificar si la fila es irrelevante
        if self.es_fila_irrelevante(fila):
            return None
        
        # Extraer campos
        codigo = self.extraer_codigo(fila)
        descripcion = self.extraer_descripcion(fila)
        precios = self.extraer_precios(fila)
        iva = self.extraer_iva(fila)
        medida = self.extraer_medida(fila)
        
        # Crear producto si tiene información mínima relevante
        if codigo or (descripcion and len(descripcion) > 5):
            producto = {}
            
            if codigo:
                producto['codigo'] = codigo
            if descripcion:
                producto['descripcion'] = descripcion
            if precios:
                if len(precios) == 1:
                    producto['precio'] = precios[0]
                else:
                    producto['precios'] = precios
            if iva is not None:
                producto['iva'] = iva
            if medida:
                producto['medida'] = medida
            
            return producto
        
        return None
    
    def purificar_datos_json(self, datos_originales, log_callback=None):
        """Purifica los datos JSON eliminando información irrelevante"""
        if log_callback:
            log_callback("🧹 Iniciando purificación de datos...")
        
        productos_purificados = []
        total_filas_procesadas = 0
        productos_por_hoja = {}
        
        # Procesar cada hoja
        for hoja in datos_originales.get('hojas', []):
            nombre_hoja = hoja.get('hoja', 'Sin nombre')
            if log_callback:
                log_callback(f"  📄 Purificando hoja: {nombre_hoja}")
            productos_hoja = 0
            
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', []):
                    total_filas_procesadas += 1
                    producto = self.procesar_fila(fila)
                    
                    if producto:
                        producto['hoja'] = nombre_hoja
                        producto['proveedor'] = datos_originales.get('proveedor_principal', 'YAYI')
                        productos_purificados.append(producto)
                        productos_hoja += 1
            
            productos_por_hoja[nombre_hoja] = productos_hoja
        
        # Eliminar duplicados por código
        productos_unicos = {}
        productos_sin_codigo = []
        duplicados_eliminados = 0
        
        for producto in productos_purificados:
            codigo = producto.get('codigo')
            
            if codigo:
                if codigo in productos_unicos:
                    # Comparar cuál producto es más completo
                    producto_existente = productos_unicos[codigo]
                    
                    # Contar campos no vacíos en ambos productos
                    campos_existente = sum(1 for v in producto_existente.values() if v)
                    campos_nuevo = sum(1 for v in producto.values() if v)
                    
                    # Preferir el producto con más información
                    if campos_nuevo > campos_existente:
                        productos_unicos[codigo] = producto
                    
                    duplicados_eliminados += 1
                else:
                    productos_unicos[codigo] = producto
            else:
                # Productos sin código, verificar si tienen descripción única y útil
                descripcion = producto.get('descripcion', '')
                if len(descripcion) > 10:  # Solo si la descripción es útil
                    productos_sin_codigo.append(producto)
        
        # Combinar productos únicos
        productos_finales = list(productos_unicos.values()) + productos_sin_codigo
        
        # Filtrar productos de alta calidad
        productos_calidad = []
        for producto in productos_finales:
            # Criterios de calidad
            tiene_codigo = 'codigo' in producto
            tiene_descripcion = 'descripcion' in producto and len(producto['descripcion']) > 5
            tiene_precio = 'precio' in producto or 'precios' in producto
            
            # Solo incluir productos que cumplan criterios mínimos
            if (tiene_codigo and tiene_descripcion) or (tiene_descripcion and tiene_precio and len(producto['descripcion']) > 15):
                productos_calidad.append(producto)
        
        # Ordenar por código
        productos_calidad.sort(key=lambda x: x.get('codigo', '999999999'))
        
        # Estadísticas finales
        stats_finales = {
            'productos_con_codigo': sum(1 for p in productos_calidad if 'codigo' in p),
            'productos_con_precio': sum(1 for p in productos_calidad if 'precio' in p or 'precios' in p),
            'productos_con_descripcion': sum(1 for p in productos_calidad if 'descripcion' in p),
            'productos_con_medida': sum(1 for p in productos_calidad if 'medida' in p),
            'productos_con_iva': sum(1 for p in productos_calidad if 'iva' in p),
            'productos_completos': sum(1 for p in productos_calidad 
                                     if 'codigo' in p and 'descripcion' in p and ('precio' in p or 'precios' in p))
        }
        
        # Crear estructura purificada
        datos_purificados = {
            'metadata': {
                'planilla_original': datos_originales.get('planilla', ''),
                'proveedor': datos_originales.get('proveedor_principal', 'YAYI'),
                'fecha_purificacion': datetime.now().isoformat(),
                'version': 'Purificado por Aplicación v1.0',
                'total_productos': len(productos_calidad),
                'duplicados_eliminados': duplicados_eliminados,
                'filas_procesadas': total_filas_procesadas,
                'eficiencia_purificacion': f"{(len(productos_calidad)/total_filas_procesadas*100):.1f}%" if total_filas_procesadas > 0 else "0%",
                'criterios_calidad': [
                    'Productos con código y descripción válida',
                    'Productos sin código pero con descripción >15 caracteres y precio',
                    'Eliminación de duplicados por código',
                    'Descripción mínima de 5 caracteres'
                ]
            },
            'estadisticas': stats_finales,
            'productos': productos_calidad
        }
        
        if log_callback:
            log_callback(f"✅ Purificación completada: {len(productos_calidad):,} productos válidos")
            log_callback(f"   • Duplicados eliminados: {duplicados_eliminados:,}")
            log_callback(f"   • Eficiencia: {datos_purificados['metadata']['eficiencia_purificacion']}")
        
        return datos_purificados

class FerreteriaAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Planillas de Ferretería con IA")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
          # Variables
        self.current_data = None
        self.purified_data = None  # Datos purificados
        self.gemini_api_key = tk.StringVar()
        self.selected_directory = tk.StringVar()
        
        # Configurar Gemini
        self.genai_model = None
        
        # Inicializar purificador
        self.purificador = PurificadorDatos()
        
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
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔧 Analizador de Planillas de Ferretería con IA", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # API Key de Gemini
        ttk.Label(config_frame, text="API Key de Gemini:").grid(row=0, column=0, sticky=tk.W)
        api_key_entry = ttk.Entry(config_frame, textvariable=self.gemini_api_key, show="*", width=50)
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(config_frame, text="Configurar", 
                  command=self.configure_gemini).grid(row=0, column=2, padx=(5, 0))
        
        # Directorio de trabajo
        ttk.Label(config_frame, text="Directorio:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        dir_entry = ttk.Entry(config_frame, textvariable=self.selected_directory, state="readonly")
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        ttk.Button(config_frame, text="Seleccionar", 
                  command=self.select_directory).grid(row=1, column=2, padx=(5, 0), pady=(5, 0))
        
        # Frame de acciones
        actions_frame = ttk.LabelFrame(main_frame, text="Acciones", padding="10")
        actions_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
          # Botones de acción
        ttk.Button(actions_frame, text="🔍 Extraer Datos", 
                  command=self.extract_data).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(actions_frame, text="🧹 Purificar Datos", 
                  command=self.purify_data).grid(row=0, column=1, padx=5)
        
        ttk.Button(actions_frame, text="🤖 Analizar con IA", 
                  command=self.analyze_with_ai).grid(row=0, column=2, padx=5)
        
        ttk.Button(actions_frame, text="📊 Generar Reporte", 
                  command=self.generate_report).grid(row=0, column=3, padx=5)
        
        ttk.Button(actions_frame, text="💾 Exportar Excel", 
                  command=self.export_excel).grid(row=0, column=4, padx=5)
        
        ttk.Button(actions_frame, text="📈 Ver Estadísticas", 
                  command=self.show_statistics).grid(row=0, column=5, padx=(5, 0))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Pestaña de resultados
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📋 Resultados")
        
        # Text widget para mostrar resultados
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap=tk.WORD, 
                                                     font=('Consolas', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de análisis IA
        self.ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_frame, text="🤖 Análisis IA")
        
        # Frame para consulta IA
        ai_query_frame = ttk.Frame(self.ai_frame)
        ai_query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ai_query_frame, text="Consulta:").pack(side=tk.LEFT)
        self.ai_query_var = tk.StringVar()
        ai_query_entry = ttk.Entry(ai_query_frame, textvariable=self.ai_query_var)
        ai_query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Button(ai_query_frame, text="Consultar", 
                  command=self.custom_ai_query).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Text widget para análisis IA
        self.ai_text = scrolledtext.ScrolledText(self.ai_frame, wrap=tk.WORD, 
                                               font=('Arial', 10))
        self.ai_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de datos
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="📊 Datos")
        
        # Treeview para mostrar datos
        columns = ('Proveedor', 'Productos', 'Estado', 'Última actualización')
        self.data_tree = ttk.Treeview(self.data_frame, columns=columns, show='headings')
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=200)
        
        # Scrollbars para el treeview
        data_scrolly = ttk.Scrollbar(self.data_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        data_scrollx = ttk.Scrollbar(self.data_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=data_scrolly.set, xscrollcommand=data_scrollx.set)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        data_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        data_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def configure_gemini(self):
        """Configura la API de Gemini"""
        api_key = self.gemini_api_key.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Por favor ingresa tu API Key de Gemini")
            return
            
        try:
            genai.configure(api_key=api_key)
            
            # Lista actualizada de modelos disponibles (orden de preferencia)
            modelos_disponibles = [
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest', 
                'gemini-1.5-pro',
                'gemini-pro-latest',
                'gemini-pro',
                'gemini-1.0-pro-latest',
                'gemini-1.0-pro'
            ]
            
            modelo_exitoso = None
            self.log_message("🔍 Buscando modelo de Gemini disponible...")
            
            for modelo in modelos_disponibles:
                try:
                    self.log_message(f"🔄 Probando modelo: {modelo}")
                    test_model = genai.GenerativeModel(modelo)
                    
                    # Hacer una prueba simple
                    response = test_model.generate_content("Responde solo 'OK'")
                    
                    # Si llegamos aquí, el modelo funciona
                    self.genai_model = test_model
                    modelo_exitoso = modelo
                    self.log_message(f"✅ Modelo {modelo} funcionando correctamente")
                    break
                    
                except Exception as e_modelo:
                    self.log_message(f"❌ Modelo {modelo} no disponible: {str(e_modelo)[:100]}...")
                    continue
            
            if modelo_exitoso:
                messagebox.showinfo("Éxito", f"API de Gemini configurada correctamente\n\nModelo: {modelo_exitoso}\n\n¡Ya puedes usar el análisis con IA!")
                self.log_message(f"✅ API de Gemini configurada con modelo: {modelo_exitoso}")
            else:
                # Ofrecer continuar sin IA
                respuesta = messagebox.askyesno(
                    "Modelos no disponibles", 
                    "No se pudo conectar con ningún modelo de Gemini.\n\n"
                    "¿Deseas continuar sin análisis de IA?\n\n"
                    "Nota: Aún puedes usar la extracción inteligente de datos."
                )
                if respuesta:
                    self.log_message("⚠️ Continuando sin análisis de IA - Solo extracción de datos disponible")
                else:
                    self.log_message("❌ Configuración de Gemini cancelada")
            
        except Exception as e:
            error_msg = f"Error al configurar Gemini: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            
            # Ofrecer continuar sin IA
            respuesta = messagebox.askyesno(
                "Error de conexión", 
                f"{error_msg}\n\n"
                "¿Deseas continuar sin análisis de IA?\n\n"
                "Nota: La extracción inteligente de datos seguirá funcionando."
            )
            if respuesta:
                self.log_message("⚠️ Continuando sin análisis de IA")
            else:
                self.log_message("❌ Configuración cancelada")
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
        """Extrae datos de los archivos HTML usando análisis inteligente de proveedores"""
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
                    self.populate_data_tree()
                    
                    # Guardar datos en el directorio seleccionado
                    output_file = os.path.join(selected_dir, "datos_extraidos_app.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        self.log_message(f"💾 Datos guardados en: {output_file}")
                    self.update_status("Extracción completada")
                else:
                    self.log_message("❌ No se pudieron extraer datos")
                    self.update_status("Error en extracción")
                    
            except Exception as e:
                self.log_message(f"❌ Error en extracción: {str(e)}")
                self.update_status("Error en extracción")
                
        threading.Thread(target=extract_thread, daemon=True).start()
        
    def extract_html_data(self, directory):
        """Extrae datos de archivos HTML usando BeautifulSoup"""
        # Detectar automáticamente archivos HTML en el directorio
        html_files = []
        try:
            for file in os.listdir(directory):
                if file.lower().endswith(('.htm', '.html')) and not file.lower() in ['tabstrip.htm', 'filelist.xml']:
                    html_files.append(file)
            
            # Ordenar archivos para procesamiento consistente
            html_files.sort()
            self.log_message(f"📁 Archivos HTML detectados: {len(html_files)}")
            for file in html_files:
                self.log_message(f"   • {file}")
                
        except Exception as e:
            self.log_message(f"❌ Error listando archivos: {str(e)}")
            return None
        
        if not html_files:
            self.log_message("❌ No se encontraron archivos HTML en el directorio")
            return None
        
        # Determinar nombre de la planilla desde el directorio o archivo principal
        planilla_name = os.path.basename(directory).replace('_archivos', '').replace('_files', '')
        if not planilla_name or planilla_name == '.':
            planilla_name = 'ANALISIS_HTML'
        
        datos_completos = {
            'planilla': planilla_name.upper(),
            'directorio': directory,
            'fecha_extraccion': datetime.now().isoformat(),
            'total_hojas': len(html_files),
            'hojas': []        }
        
        # Procesar cada archivo HTML detectado
        for html_file in html_files:
            archivo_path = os.path.join(directory, html_file)
              # Determinar nombre del proveedor/hoja desde el nombre del archivo
            nombre_hoja = self.determinar_nombre_hoja(html_file)
            
            if os.path.exists(archivo_path):
                hoja_data = self.procesar_hoja_html(archivo_path, nombre_hoja)
                if hoja_data:
                    datos_completos['hojas'].append(hoja_data)
                    self.log_message(f"   📄 {nombre_hoja}: {hoja_data['total_tablas']} tabla(s)")
            else:
                self.log_message(f"   ⚠️ Archivo no encontrado: {html_file}")
                
        return datos_completos
    
    def extract_html_data_intelligent(self, directory):
        """Extrae datos con análisis inteligente de proveedores"""
        from collections import Counter
        
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
    
    def determinar_nombre_hoja(self, archivo_html):
        """Determina el nombre de la hoja/proveedor desde el nombre del archivo"""
        # Mapeo conocido para archivos comunes
        mapeo_archivos = {
            'sheet001.htm': 'CRIMARAL',
            'sheet002.htm': 'ANCAIG', 
            'sheet003.htm': 'DAFYS',
            'sheet004.htm': 'FERRETERIA',
            'sheet005.htm': 'HERRAMETAL',
            'sheet006.htm': 'YAYI',
            'sheet007.htm': 'DIST_CITY_BELL',
            'sheet008.htm': 'BABUSI',
            'sheet009.htm': 'FERRIPLAST'
        }
        
        # Si encontramos un mapeo conocido, usarlo
        if archivo_html in mapeo_archivos:
            return mapeo_archivos[archivo_html]
        
        # Para archivos no conocidos, generar nombre desde el archivo
        nombre = os.path.splitext(archivo_html)[0]
        nombre = nombre.replace('sheet', 'HOJA_').replace('_', '-')
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
            self.log_message(f"❌ Error procesando {nombre_hoja}: {str(e)}")
            return None
            
    def limpiar_texto(self, texto):
        """Limpia y normaliza texto"""
        if not texto:
            return ""
        texto = re.sub(r'\s+', ' ', texto.strip())
        texto = texto.replace('\xa0', ' ')
        return texto
        
    def populate_data_tree(self):
        """Puebla el treeview con datos extraídos"""
        # Limpiar datos existentes
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        if not self.current_data:
            return
            
        for hoja in self.current_data['hojas']:
            total_productos = sum(tabla['total_filas'] for tabla in hoja['tablas'])
            estado = "✅ Activo" if hoja['total_tablas'] > 0 else "❌ Vacío"
            fecha_proc = hoja.get('procesado_en', '')[:10] if hoja.get('procesado_en') else '-'
            self.data_tree.insert('', tk.END, values=(
                hoja['hoja'],
                f"{total_productos:,}",                estado,
                fecha_proc
            ))
    
    def analyze_with_ai(self):
        """Analiza los datos con IA usando Gemini"""
        if not self.genai_model:
            # Ofrecer análisis sin IA
            respuesta = messagebox.askyesno(
                "IA no disponible", 
                "La API de Gemini no está configurada o no está disponible.\n\n"
                "¿Deseas ver un análisis básico de los datos sin IA?\n\n"
                "Incluirá estadísticas y resumen de los datos extraídos."
            )
            if respuesta:
                self.generate_basic_analysis()
            return
            
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
        
        # Verificar si hay datos purificados disponibles
        datos_para_analisis = self.purified_data if self.purified_data else self.current_data
        tipo_datos = "PURIFICADOS" if self.purified_data else "ORIGINALES"
        
        if not self.purified_data:
            # Sugerir purificar primero
            respuesta = messagebox.askyesno(
                "Datos sin purificar",
                "Se recomienda purificar los datos antes del análisis IA.\n\n"
                "Los datos purificados proporcionan un análisis más preciso y útil.\n\n"
                "¿Deseas purificar los datos primero?\n\n"
                "Selecciona 'No' para analizar los datos originales."
            )
            if respuesta:
                self.purify_data()
                return
            
        def analyze_thread():
            try:
                self.update_status(f"Analizando datos {tipo_datos.lower()} con IA...")
                self.log_message(f"🤖 Iniciando análisis IA con datos {tipo_datos}...")
                  # Preparar resumen para IA
                resumen = self.prepare_data_summary()
                  # Extraer lista de proveedores del resumen para instrucciones explícitas
                proveedores_detectados = []
                if "=== PROVEEDORES CON DATOS REESTRUCTURADOS ===" in resumen:
                    lineas = resumen.split('\n')
                    for linea in lineas:
                        if ':' in linea and 'Productos reestructurados:' in linea:
                            proveedor = linea.split(':')[0].strip()
                            if proveedor and proveedor not in proveedores_detectados:
                                proveedores_detectados.append(proveedor)
                
                lista_proveedores = ""
                if proveedores_detectados:
                    lista_proveedores = "PROVEEDORES INCLUIDOS EN ESTE ANÁLISIS:\n"
                    for i, prov in enumerate(proveedores_detectados, 1):
                        lista_proveedores += f"{i}. {prov}\n"
                    lista_proveedores += f"TOTAL: {len(proveedores_detectados)} PROVEEDORES\n\n"

                prompt = f"""
                ANÁLISIS DE DATOS ESTRUCTURADOS DE FERRETERÍA

                {lista_proveedores}DATOS PROCESADOS E INTELIGENTEMENTE ORGANIZADOS:
                Los siguientes datos han sido limpiados, reestructurados y organizados automáticamente 
                para facilitar el análisis de calidad, estructura y oportunidades de mejora:

                {resumen}

                🎯 OBJETIVO DEL ANÁLISIS:
                Evaluar la calidad, estructura y organización de estos datos procesados,
                identificando patrones, oportunidades de mejora y insights de valor para el negocio.

                📋 ANÁLISIS SOLICITADO:

                1. **📊 EVALUACIÓN DE CALIDAD DE DATOS:**
                   - Revisar la completitud de información por proveedor
                   - Evaluar la consistencia en formatos de precios y códigos
                   - Identificar datos faltantes y áreas de mejora

                2. **💰 ANÁLISIS DE PRECIOS Y MONEDAS:**
                   - Detectar patrones en las estructuras de precios
                   - Analizar la diversidad de monedas utilizadas
                   - Identificar oportunidades de estandarización

                3. **🔍 INSIGHTS DE ORGANIZACIÓN:**
                   - Evaluar cómo están organizados los productos por categorías
                   - Identificar patrones en la nomenclatura y códigos
                   - Sugerir mejoras en la estructura de datos

                4. **💡 RECOMENDACIONES DE NEGOCIO:**
                   - Oportunidades basadas en los datos disponibles
                   - Estrategias para mejorar la calidad de la información
                   - Sugerencias para optimizar la gestión de inventario

                5. **📈 OPTIMIZACIÓN DE PROCESOS:**
                   - Identificar redundancias o inconsistencias
                   - Proponer mejoras en la organización de listas
                   - Recomendar estándares para futuras actualizaciones

                🎯 ENFOQUE: Analiza la información como un consultor de datos que busca optimizar 
                la organización, calidad y utilidad de estos datos para toma de decisiones comerciales.

                Proporciona análisis constructivo y práctico en español, enfocado en valor de negocio.
                """
                
                response = self.genai_model.generate_content(prompt)
                
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, response.text)
                
                self.log_message("✅ Análisis IA completado")
                self.update_status("Análisis IA completado")
                
                # Cambiar a pestaña IA
                self.notebook.select(self.ai_frame)
                
            except Exception as e:
                self.log_message(f"❌ Error en análisis IA: {str(e)}")
                self.update_status("Error en análisis IA")
                
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def generate_basic_analysis(self):
        """Genera un análisis básico sin IA"""
        try:
            self.update_status("Generando análisis básico...")
            self.log_message("📊 Generando análisis básico de datos...")
            
            if not self.current_data:
                return
            
            # Preparar análisis básico
            analysis = []
            analysis.append("📊 ANÁLISIS BÁSICO DE DATOS - SIN IA")
            analysis.append("=" * 50)
            analysis.append("")
            
            # Información general
            estrategia = self.current_data.get('estrategia_proveedores', 'No especificada')
            proveedor_principal = self.current_data.get('proveedor_principal', 'No detectado')
            
            analysis.append("🏢 INFORMACIÓN GENERAL:")
            analysis.append(f"   • Planilla: {self.current_data['planilla']}")
            analysis.append(f"   • Estrategia detectada: {estrategia}")
            analysis.append(f"   • Proveedor principal: {proveedor_principal}")
            analysis.append(f"   • Total de hojas: {len(self.current_data['hojas'])}")
            analysis.append("")
            
            # Análisis por hoja/proveedor
            total_productos = 0
            hojas_activas = 0
            
            analysis.append("📋 ANÁLISIS POR HOJA/PROVEEDOR:")
            analysis.append("-" * 40)
            
            for hoja in self.current_data['hojas']:
                productos_hoja = sum(tabla['total_filas'] for tabla in hoja['tablas'])
                total_productos += productos_hoja
                
                if productos_hoja > 0:
                    hojas_activas += 1
                    status = "✅ Activa"
                else:
                    status = "❌ Vacía"
                
                analysis.append(f"📄 {hoja['hoja']}:")
                analysis.append(f"   • Productos: {productos_hoja:,}")
                analysis.append(f"   • Tablas: {hoja['total_tablas']}")
                analysis.append(f"   • Estado: {status}")
                
                # Información de proveedores detectados
                if hoja.get('proveedores_detectados'):
                    top_proveedor = hoja['proveedores_detectados'][0]
                    analysis.append(f"   • Proveedor detectado: {top_proveedor['nombre']} (confianza: {top_proveedor['confianza']:.2f})")
                
                analysis.append("")
            
            # Estadísticas generales
            analysis.append("📊 ESTADÍSTICAS GENERALES:")
            analysis.append("-" * 40)
            analysis.append(f"   • Total de productos: {total_productos:,}")
            analysis.append(f"   • Hojas activas: {hojas_activas}/{len(self.current_data['hojas'])}")
            analysis.append(f"   • Promedio productos/hoja: {total_productos // len(self.current_data['hojas']) if self.current_data['hojas'] else 0:,}")
            analysis.append("")
            
            # Recomendaciones básicas
            analysis.append("💡 RECOMENDACIONES BÁSICAS:")
            analysis.append("-" * 40)
            
            if estrategia == 'single_provider':
                analysis.append("   ✅ Detección correcta de proveedor único")
                analysis.append("   📝 Las hojas están organizadas como listas del mismo proveedor")
                analysis.append("   💡 Considera consolidar las listas para mejor gestión")
            elif estrategia == 'multiple_providers':
                analysis.append("   ✅ Detección correcta de múltiples proveedores")
                analysis.append("   📝 Cada hoja representa un proveedor diferente")
                analysis.append("   💡 Utiliza esta información para comparar entre proveedores")
            
            if hojas_activas < len(self.current_data['hojas']):
                hojas_vacias = len(self.current_data['hojas']) - hojas_activas
                analysis.append(f"   ⚠️ Hay {hojas_vacias} hoja(s) vacías que podrían eliminarse")
            
            analysis.append("")
            analysis.append("🔧 FUNCIONALIDADES DISPONIBLES:")
            analysis.append("-" * 40)
            analysis.append("   📊 Generar Reporte - Crea un reporte en Markdown")
            analysis.append("   💾 Exportar Excel - Exporta datos a formato Excel") 
            analysis.append("   📈 Ver Estadísticas - Muestra estadísticas detalladas")
            analysis.append("")
            analysis.append("💡 Para análisis avanzado con IA, configura Gemini API")
            
            # Mostrar el análisis
            self.ai_text.delete(1.0, tk.END)
            self.ai_text.insert(tk.END, "\n".join(analysis))
            
            self.log_message("✅ Análisis básico completado")
            self.update_status("Análisis básico completado")
            
            # Cambiar a pestaña IA
            self.notebook.select(self.ai_frame)
            
        except Exception as e:
            self.log_message(f"❌ Error en análisis básico: {str(e)}")
            self.update_status("Error en análisis básico")
    
    def custom_ai_query(self):
        """Realiza una consulta personalizada a la IA"""
        if not self.genai_model:
            messagebox.showerror("Error", "Primero configura la API de Gemini")
            return
            
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
            
        query = self.ai_query_var.get().strip()
        if not query:
            messagebox.showwarning("Advertencia", "Ingresa una consulta")
            return
            
        def query_thread():            
            try:
                self.update_status("Procesando consulta...")
                resumen = self.prepare_data_summary()
                
                # Extraer lista de proveedores para contexto
                proveedores_detectados = []
                if "=== PROVEEDORES CON DATOS REESTRUCTURADOS ===" in resumen:
                    lineas = resumen.split('\n')
                    for linea in lineas:
                        if ':' in linea and 'Productos reestructurados:' in linea:
                            proveedor = linea.split(':')[0].strip()
                            if proveedor and proveedor not in proveedores_detectados:
                                proveedores_detectados.append(proveedor)
                
                contexto_proveedores = f"CONTEXTO: Tienes datos de {len(proveedores_detectados)} proveedores: {', '.join(proveedores_detectados)}\n" if proveedores_detectados else ""
                
                prompt = f"""
                {contexto_proveedores}
                DATOS ESTRUCTURADOS DE FERRETERÍA:
                {resumen}
                
                CONSULTA ESPECÍFICA: {query}
                
                Responde considerando TODOS los proveedores disponibles en los datos, no solo uno.
                Responde en español de manera clara y específica.
                """
                
                response = self.genai_model.generate_content(prompt)
                
                self.ai_text.insert(tk.END, f"\n\n{'='*50}\n")
                self.ai_text.insert(tk.END, f"CONSULTA: {query}\n")
                self.ai_text.insert(tk.END, f"{'='*50}\n\n")
                self.ai_text.insert(tk.END, response.text)
                self.ai_text.see(tk.END)
                
                self.ai_query_var.set("")
                self.update_status("Consulta completada")
                
            except Exception as e:
                self.log_message(f"❌ Error en consulta: {str(e)}")
                self.update_status("Error en consulta")
                
        threading.Thread(target=query_thread, daemon=True).start()
        
    def generate_report(self):
        """Genera un reporte completo"""
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
            
        try:
            output_dir = self.selected_directory.get()
            report_file = os.path.join(output_dir, f"reporte_ferreteria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_markdown_report())
                
            self.log_message(f"📊 Reporte generado: {report_file}")
            
            # Preguntar si abrir el archivo
            if messagebox.askyesno("Reporte generado", "¿Deseas abrir el reporte generado?"):
                os.startfile(report_file)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
            
    def generate_markdown_report(self):
        """Genera contenido del reporte en Markdown"""
        if not self.current_data:
            return ""
            
        report = f"""# REPORTE DE ANÁLISIS - PLANILLA FERRETERÍA

**Fecha de análisis:** {datetime.now().strftime('%d de %B de %Y')}  
**Fecha de extracción:** {self.current_data['fecha_extraccion'][:10]}

## 📊 RESUMEN EJECUTIVO

"""
        
        total_productos = sum(sum(tabla['total_filas'] for tabla in hoja['tablas']) for hoja in self.current_data['hojas'])
        hojas_activas = len([h for h in self.current_data['hojas'] if sum(t['total_filas'] for t in h['tablas']) > 0])
        
        report += f"- **Total de productos:** {total_productos:,}\n"
        report += f"- **Proveedores activos:** {hojas_activas}\n"
        report += f"- **Hojas procesadas:** {len(self.current_data['hojas'])}\n\n"
        
        report += "## 🏪 DETALLE POR PROVEEDOR\n\n"
        
        for hoja in self.current_data['hojas']:
            productos_hoja = sum(tabla['total_filas'] for tabla in hoja['tablas'])
            report += f"### {hoja['hoja']}\n"
            report += f"- **Productos:** {productos_hoja:,}\n"
            report += f"- **Tablas:** {hoja['total_tablas']}\n"
            report += f"- **Archivo:** {hoja['archivo']}\n\n"
            
        report += "\n---\n\n*Reporte generado automáticamente por Analizador de Ferretería*"        
        return report
        
    def export_excel(self):
        """Exporta datos a Excel"""
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
        
        # Priorizar datos purificados si están disponibles
        if self.purified_data:
            self.export_purified_to_excel()
        else:
            # Sugerir purificar primero
            respuesta = messagebox.askyesno(
                "Exportación mejorada",
                "Se recomienda purificar los datos antes de exportar.\n\n"
                "Los datos purificados están mejor organizados y son más útiles.\n\n"
                "¿Deseas purificar los datos primero?\n\n"
                "Selecciona 'No' para exportar los datos originales."
            )
            if respuesta:
                self.purify_data()
                return
            else:
                self.export_original_to_excel()
    
    def export_purified_to_excel(self):
        """Exporta datos purificados a Excel"""
        try:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar datos purificados como Excel"
            )
            
            if output_file:
                self.update_status("Exportando datos purificados...")
                self.log_message("📊 Exportando datos purificados a Excel...")
                
                productos = self.purified_data.get('productos', [])
                metadata = self.purified_data.get('metadata', {})
                estadisticas = self.purified_data.get('estadisticas', {})
                
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    # Hoja de resumen
                    resumen_data = [{
                        'Planilla Original': metadata.get('planilla_original', 'N/A'),
                        'Proveedor': metadata.get('proveedor', 'N/A'),
                        'Fecha Purificación': metadata.get('fecha_purificacion', 'N/A')[:19],
                        'Total Productos': metadata.get('total_productos', 0),
                        'Duplicados Eliminados': metadata.get('duplicados_eliminados', 0),
                        'Eficiencia': metadata.get('eficiencia_purificacion', '0%'),
                        'Productos Completos': estadisticas.get('productos_completos', 0),
                        'Con Código': estadisticas.get('productos_con_codigo', 0),
                        'Con Precio': estadisticas.get('productos_con_precio', 0),
                        'Con Descripción': estadisticas.get('productos_con_descripcion', 0)
                    }]
                    
                    df_resumen = pd.DataFrame(resumen_data)
                    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    # Hoja de productos purificados
                    productos_data = []
                    for producto in productos:
                        productos_data.append({
                            'Código': producto.get('codigo', ''),
                            'Descripción': producto.get('descripcion', ''),
                            'Precio': producto.get('precio', ''),
                            'Precios_Adicionales': ', '.join(producto.get('precios', [])) if producto.get('precios') else '',
                            'IVA': producto.get('iva', ''),
                            'Medida': producto.get('medida', ''),
                            'Hoja_Original': producto.get('hoja', ''),
                            'Proveedor': producto.get('proveedor', '')
                        })
                    
                    df_productos = pd.DataFrame(productos_data)
                    df_productos.to_excel(writer, sheet_name='Productos_Purificados', index=False)
                    
                    # Hoja de productos por categoría (agrupados por hoja)
                    productos_por_hoja = {}
                    for producto in productos:
                        hoja = producto.get('hoja', 'Sin_hoja')
                        if hoja not in productos_por_hoja:
                            productos_por_hoja[hoja] = []
                        productos_por_hoja[hoja].append(producto)
                    
                    for hoja, productos_hoja in productos_por_hoja.items():
                        if len(productos_hoja) > 0:
                            # Crear nombre de hoja válido para Excel (máximo 31 caracteres)
                            nombre_hoja = hoja.replace('/', '_').replace('\\', '_')[:31]
                            
                            productos_hoja_data = []
                            for producto in productos_hoja:
                                productos_hoja_data.append({
                                    'Código': producto.get('codigo', ''),
                                    'Descripción': producto.get('descripcion', ''),
                                    'Precio': producto.get('precio', ''),
                                    'IVA': producto.get('iva', ''),
                                    'Medida': producto.get('medida', '')
                                })
                            
                            if productos_hoja_data:
                                df_hoja = pd.DataFrame(productos_hoja_data)
                                df_hoja.to_excel(writer, sheet_name=nombre_hoja, index=False)
                
                self.log_message(f"✅ Datos purificados exportados: {output_file}")
                self.update_status("Exportación completada")
                
                messagebox.showinfo(
                    "Exportación Exitosa",
                    f"Datos purificados exportados correctamente:\n\n"
                    f"• Archivo: {os.path.basename(output_file)}\n"
                    f"• Productos: {len(productos):,}\n"
                    f"• Hojas creadas: {len(productos_por_hoja) + 2}\n\n"
                    f"El archivo incluye:\n"
                    f"- Hoja de resumen con estadísticas\n"
                    f"- Hoja con todos los productos purificados\n"
                    f"- Hojas separadas por categoría/proveedor"
                )
                
        except Exception as e:
            self.log_message(f"❌ Error en exportación: {str(e)}")
            self.update_status("Error en exportación")
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def export_original_to_excel(self):
        """Exporta datos originales a Excel (método original)"""
            
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
                        resumen_data.append({
                            'Proveedor': hoja['hoja'],
                            'Productos': productos,
                            'Tablas': hoja['total_tablas'],
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
            
        # Crear ventana de estadísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📈 Estadísticas Detalladas")
        stats_window.geometry("600x500")
        
        stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD, font=('Consolas', 10))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generar estadísticas
        stats = self.generate_statistics()
        stats_text.insert(tk.END, stats)
        
    def generate_statistics(self):
        """Genera estadísticas detalladas"""
        if not self.current_data:
            return "No hay datos disponibles"
            stats = "ESTADÍSTICAS DETALLADAS - PLANILLA FERRETERÍA\n"
        stats += "=" * 50 + "\n\n"
        
        total_productos = 0
        total_tablas = 0
        
        for hoja in self.current_data['hojas']:
            productos_hoja = sum(tabla['total_filas'] for tabla in hoja['tablas'])
            total_productos += productos_hoja
            total_tablas += hoja['total_tablas']
            
            stats += f"📋 {hoja['hoja']}:\n"
            stats += f"   • Productos: {productos_hoja:,}\n"
            stats += f"   • Tablas: {hoja['total_tablas']}\n"
            
            if hoja['tablas']:
                tabla_max = max(hoja['tablas'], key=lambda t: t['total_filas'])
                stats += f"   • Tabla más grande: {tabla_max['total_filas']} filas x {tabla_max['total_columnas']} columnas\n"
            
            stats += "\n"
            
        stats += f"📊 TOTALES:\n"
        stats += f"   • Total productos: {total_productos:,}\n"
        stats += f"   • Total tablas: {total_tablas}\n"
        stats += f"   • Proveedores activos: {len([h for h in self.current_data['hojas'] if sum(t['total_filas'] for t in h['tablas']) > 0])}\n"
        stats += f"   • Promedio productos/proveedor: {total_productos // len(self.current_data['hojas']) if self.current_data['hojas'] else 0:,}\n"
        
        return stats

    def prepare_data_summary(self):
        """Prepara un resumen INTELIGENTE de los datos para el análisis con IA"""
        if not self.current_data:
            return "No hay datos disponibles"
        
        try:
            # Importar el analizador inteligente y reestructurador
            from analizador_datos_inteligente import AnalizadorDatosInteligente
            from reestructurador_simple import reestructurar_datos_simple
            
            # Guardar datos actuales temporalmente para análisis
            import tempfile
            import json
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
                json.dump(self.current_data, temp_file, ensure_ascii=False, indent=2)
                temp_path = temp_file.name
            
            # Realizar análisis inteligente
            analizador = AnalizadorDatosInteligente()
            analisis = analizador.analizar_datos_estructurados(temp_path)
            
            # Realizar reestructuración inteligente de datos
            datos_reestructurados = reestructurar_datos_simple(temp_path)
            
            # Limpiar archivo temporal
            os.remove(temp_path)
            
            if analisis and datos_reestructurados:
                # Generar resumen inteligente con datos reestructurados
                resumen_inteligente = self._generar_resumen_con_reestructuracion(analisis, datos_reestructurados)
                
                # Agregar información adicional contextual
                resumen_inteligente += "\n\n=== INFORMACIÓN CONTEXTUAL ===\n"
                resumen_inteligente += f"Este análisis se basa en datos REESTRUCTURADOS INTELIGENTEMENTE.\n"
                resumen_inteligente += f"Los datos han sido procesados para identificar correctamente:\n"
                resumen_inteligente += f"- CÓDIGOS DE PRODUCTOS separados de descripciones\n"
                resumen_inteligente += f"- PRECIOS extraídos y clasificados por moneda\n"
                resumen_inteligente += f"- PROVEEDORES organizados por hoja\n"
                resumen_inteligente += f"- MARCAS detectadas automáticamente\n"
                resumen_inteligente += f"- DESCRIPCIONES limpias y optimizadas\n"
                resumen_inteligente += f"- DUPLICADOS eliminados automáticamente\n"
                resumen_inteligente += f"\nUSA ESTE ANÁLISIS PARA RECOMENDAR MEJORAS EN LA ESTRUCTURACIÓN DE DATOS.\n"
                
                return resumen_inteligente
            else:
                # Fallback al método básico si falla el análisis inteligente
                return self._prepare_basic_summary()
                
        except Exception as e:
            self.log_message(f"⚠️ Análisis inteligente falló, usando método básico: {str(e)}")
            return self._prepare_basic_summary()
    
    def _generar_resumen_con_reestructuracion(self, analisis, datos_reestructurados):
        """Genera resumen combinando análisis inteligente y datos reestructurados"""
        resumen = []
        
        # Encabezado del análisis
        resumen.append("=== ANÁLISIS INTELIGENTE CON REESTRUCTURACIÓN DE DATOS ===")
        resumen.append(f"PLANILLA: {analisis['resumen_general']['planilla']}")
        resumen.append(f"TOTAL REGISTROS ORIGINALES: {analisis['resumen_general']['total_registros']:,}")
        
        # Estadísticas de reestructuración
        total_reestructurados = sum(len(productos) for productos in datos_reestructurados.values())
        resumen.append(f"TOTAL PRODUCTOS REESTRUCTURADOS: {total_reestructurados:,}")
        resumen.append(f"EFICIENCIA DE REESTRUCTURACIÓN: {(total_reestructurados/analisis['resumen_general']['total_registros']*100):.1f}%")
        resumen.append("")
        
        # Análisis por proveedor con datos reestructurados
        resumen.append("=== PROVEEDORES CON DATOS REESTRUCTURADOS ===")
        for proveedor, productos in datos_reestructurados.items():
            # Estadísticas de calidad de los datos reestructurados
            productos_con_precio = len([p for p in productos if p.get('PRECIO')])
            productos_con_codigo = len([p for p in productos if p.get('CODIGO')])
            productos_con_marca = len([p for p in productos if p.get('MARCA')])
            
            resumen.append(f"{proveedor}:")
            resumen.append(f"  • Productos reestructurados: {len(productos):,}")
            resumen.append(f"  • Con precio detectado: {productos_con_precio:,} ({productos_con_precio/len(productos)*100:.1f}%)")
            resumen.append(f"  • Con código identificado: {productos_con_codigo:,} ({productos_con_codigo/len(productos)*100:.1f}%)")
            resumen.append(f"  • Con marca detectada: {productos_con_marca:,} ({productos_con_marca/len(productos)*100:.1f}%)")
            
            # Muestra de productos reestructurados
            if productos:
                resumen.append(f"  • Muestra de productos reestructurados:")
                for i, producto in enumerate(productos[:3], 1):
                    resumen.append(f"    {i}. CÓDIGO: {producto.get('CODIGO', 'N/A')}")
                    resumen.append(f"       DESCRIPCIÓN: {producto.get('DESCRIPCION', 'N/A')[:50]}...")
                    resumen.append(f"       PRECIO: {producto.get('PRECIO', 'N/A')} {producto.get('MONEDA', '')}")
                    resumen.append(f"       MARCA: {producto.get('MARCA', 'N/A')}")
        
        resumen.append("")
        
        # Análisis de calidad de reestructuración
        resumen.append("=== ANÁLISIS DE CALIDAD DE REESTRUCTURACIÓN ===")
        total_con_precio = sum(len([p for p in productos if p.get('PRECIO')]) for productos in datos_reestructurados.values())
        total_con_codigo = sum(len([p for p in productos if p.get('CODIGO')]) for productos in datos_reestructurados.values())
        
        resumen.append(f"Productos con precio extraído: {total_con_precio:,} ({total_con_precio/total_reestructurados*100:.1f}%)")
        resumen.append(f"Productos con código identificado: {total_con_codigo:,} ({total_con_codigo/total_reestructurados*100:.1f}%)")
        resumen.append("")
        
        # Recomendaciones específicas de reestructuración
        resumen.append("=== RECOMENDACIONES DE REESTRUCTURACIÓN ===")
        for proveedor, productos in datos_reestructurados.items():
            productos_sin_precio = len([p for p in productos if not p.get('PRECIO')])
            productos_sin_codigo = len([p for p in productos if not p.get('CODIGO')])
            
            if productos_sin_precio > len(productos) * 0.5:
                resumen.append(f"• {proveedor}: Mejorar formato de precios - {productos_sin_precio:,} productos sin precio detectado")
            
            if productos_sin_codigo > len(productos) * 0.8:
                resumen.append(f"• {proveedor}: Implementar códigos de producto - {productos_sin_codigo:,} productos sin código")
        
        return "\n".join(resumen)
    
    def _prepare_basic_summary(self):
        """Método básico de resumen (fallback)"""
        
        summary = []
        
        # Información general
        summary.append(f"PLANILLA: {self.current_data['planilla']}")
        summary.append(f"FECHA EXTRACCIÓN: {self.current_data['fecha_extraccion'][:10]}")
        
        # Estrategia de proveedores
        estrategia = self.current_data.get('estrategia_proveedores', 'No especificada')
        proveedor_principal = self.current_data.get('proveedor_principal', 'No detectado')
        summary.append(f"ESTRATEGIA: {estrategia}")
        if proveedor_principal:
            summary.append(f"PROVEEDOR PRINCIPAL: {proveedor_principal}")
        
        summary.append(f"TOTAL HOJAS: {len(self.current_data['hojas'])}")
        
        # Resumen por hoja/proveedor
        total_productos_global = 0
        hojas_activas = 0
        
        summary.append("\nDETALLE POR PROVEEDOR/HOJA:")
        for hoja in self.current_data['hojas']:
            productos_hoja = sum(tabla['total_filas'] for tabla in hoja['tablas'])
            total_productos_global += productos_hoja
            
            if productos_hoja > 0:
                hojas_activas += 1
                estado = "ACTIVA"
            else:
                estado = "VACÍA"
            
            summary.append(f"- {hoja['hoja']}: {productos_hoja:,} productos, {hoja['total_tablas']} tablas ({estado})")
            
            # Información de proveedores detectados
            if hoja.get('proveedores_detectados'):
                top_proveedor = hoja['proveedores_detectados'][0]
                summary.append(f"  • Proveedor detectado: {top_proveedor['nombre']} (confianza: {top_proveedor['confianza']:.2f})")
            
            # Muestra de datos si hay tablas
            if hoja['tablas'] and hoja['tablas'][0]['filas']:
                primera_tabla = hoja['tablas'][0]
                muestra_filas = primera_tabla['filas'][:3]  # Primeras 3 filas como muestra
                summary.append(f"  • Muestra de datos (primeras 3 filas):")
                for i, fila in enumerate(muestra_filas, 1):
                    fila_text = " | ".join(str(celda)[:30] for celda in fila[:5])  # Primeras 5 columnas
                    summary.append(f"    {i}. {fila_text}")
        
        # Estadísticas generales
        summary.append(f"\nESTADÍSTICAS GENERALES:")
        summary.append(f"- Total de productos: {total_productos_global:,}")
        summary.append(f"- Hojas activas: {hojas_activas}/{len(self.current_data['hojas'])}")
        summary.append(f"- Promedio productos/hoja: {total_productos_global // len(self.current_data['hojas']) if self.current_data['hojas'] else 0:,}")
        
        return "\n".join(summary)
    
    def purify_data(self):
        """Purifica los datos extraídos eliminando información irrelevante"""
        if not self.current_data:
            messagebox.showerror("Error", "Primero extrae los datos")
            return
            
        def purify_thread():
            try:
                self.update_status("Purificando datos...")
                self.log_message("🧹 Iniciando purificación de datos...")
                
                # Purificar datos usando el purificador integrado
                self.purified_data = self.purificador.purificar_datos_json(
                    self.current_data, 
                    log_callback=self.log_message
                )
                
                if self.purified_data:
                    # Mostrar estadísticas de purificación
                    metadata = self.purified_data.get('metadata', {})
                    estadisticas = self.purified_data.get('estadisticas', {})
                    
                    self.log_message("✅ Purificación completada")
                    self.log_message(f"📊 Productos válidos: {metadata.get('total_productos', 0):,}")
                    self.log_message(f"🗑️ Duplicados eliminados: {metadata.get('duplicados_eliminados', 0):,}")
                    self.log_message(f"📈 Eficiencia: {metadata.get('eficiencia_purificacion', '0%')}")
                    self.log_message(f"✅ Productos completos: {estadisticas.get('productos_completos', 0):,}")
                    
                    # Actualizar árbol de datos con productos purificados
                    self.update_data_tree_with_purified()
                    
                    # Cambiar a pestaña de datos
                    self.notebook.select(self.data_frame)
                    
                    self.update_status("Datos purificados exitosamente")
                    
                    # Mostrar mensaje de éxito
                    messagebox.showinfo(
                        "Purificación Exitosa",
                        f"Datos purificados correctamente:\n\n"
                        f"• Productos válidos: {metadata.get('total_productos', 0):,}\n"
                        f"• Productos completos: {estadisticas.get('productos_completos', 0):,}\n"
                        f"• Duplicados eliminados: {metadata.get('duplicados_eliminados', 0):,}\n"
                        f"• Eficiencia: {metadata.get('eficiencia_purificacion', '0%')}\n\n"
                        f"Los datos están listos para análisis IA y exportación."
                    )
                else:
                    self.log_message("❌ Error en purificación de datos")
                    self.update_status("Error en purificación")
                    
            except Exception as e:
                self.log_message(f"❌ Error en purificación: {str(e)}")
                self.update_status("Error en purificación")
                messagebox.showerror("Error", f"Error en purificación: {str(e)}")
                
        threading.Thread(target=purify_thread, daemon=True).start()
    
    def update_data_tree_with_purified(self):
        """Actualiza el árbol de datos con los productos purificados"""
        if not self.purified_data:
            return
            
        # Limpiar árbol existente
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Agregar datos purificados
        productos = self.purified_data.get('productos', [])
        metadata = self.purified_data.get('metadata', {})
        
        # Nodo raíz de resumen
        root_text = f"📊 Datos Purificados - {metadata.get('total_productos', 0):,} productos"
        root_node = self.data_tree.insert('', 'end', text=root_text, open=True)
          # Información de purificación
        self.data_tree.insert(root_node, 'end', text=f"📅 Fecha: {metadata.get('fecha_purificacion', 'N/A')[:19]}")
        self.data_tree.insert(root_node, 'end', text=f"🏪 Proveedor: {metadata.get('proveedor', 'N/A')}")
        self.data_tree.insert(root_node, 'end', text=f"⚡ Eficiencia: {metadata.get('eficiencia_purificacion', '0%')}")
        self.data_tree.insert(root_node, 'end', text=f"🗑️ Duplicados eliminados: {metadata.get('duplicados_eliminados', 0):,}")
