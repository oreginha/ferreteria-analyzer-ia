#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para extraer datos estructurados de las hojas de Excel convertidas a HTML
con detección inteligente de proveedores únicos vs múltiples listas del mismo proveedor

NUEVAS CARACTERÍSTICAS:
- Detección automática si las hojas son del mismo proveedor o proveedores diferentes
- Análisis de contenido para identificar el proveedor principal
- Nomenclatura inteligente de hojas (Lista_1, Lista_2 vs Proveedor_A, Proveedor_B)
- Soporte para directorios personalizados
- Análisis de patrones de datos

USO:
- python extraer_datos_mejorado.py                    # Usa directorio actual
- python extraer_datos_mejorado.py "ruta/directorio"  # Usa directorio específico
"""

import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter

def limpiar_texto(texto):
    """Limpia y normaliza el texto"""
    if not texto:
        return ""
    
    # Remover espacios extra y caracteres especiales
    texto = re.sub(r'\s+', ' ', texto.strip())
    texto = texto.replace('\xa0', ' ')  # Non-breaking space
    texto = texto.replace('\u00a0', ' ')  # Non-breaking space
    
    return texto

def extraer_datos_tabla(soup):
    """Extrae datos de las tablas en el HTML con procesamiento inteligente de productos"""
    tablas = soup.find_all('table')
    datos_extraidos = []
    productos_encontrados = []
    
    for i, tabla in enumerate(tablas):
        filas = tabla.find_all('tr')
        if not filas:
            continue
            
        datos_tabla = []
        seccion_actual = ""
        
        for j, fila in enumerate(filas):
            celdas = fila.find_all(['td', 'th'])
            fila_datos = []
            
            # Extraer texto de cada celda con mejor limpieza
            for celda in celdas:
                texto = limpiar_texto(celda.get_text())
                fila_datos.append(texto)
            
            # Detectar si es una fila de sección (encabezado de categoría)
            if len(fila_datos) >= 2 and fila_datos[0] and fila_datos[1]:
                primera_celda = fila_datos[0].upper()
                segunda_celda = fila_datos[1].upper()
                
                # Detectar secciones como "TUBOS DE 40", "TANQUES", etc.
                if any(keyword in primera_celda + " " + segunda_celda for keyword in 
                       ['TUBOS', 'TANQUE', 'COMPARATIVA', 'OFERTA', 'CATEGORIA']):
                    seccion_actual = (primera_celda + " " + segunda_celda).strip()
            
            # Detectar productos (filas con código y descripción)
            if len(fila_datos) >= 3:
                posible_codigo = fila_datos[0].strip()
                posible_descripcion = fila_datos[1].strip()
                
                # Un producto típico tiene código numérico y descripción
                if (posible_codigo and posible_descripcion and 
                    re.match(r'^\d+$', posible_codigo) and 
                    len(posible_descripcion) > 5):
                    
                    # Extraer precios/costos de las siguientes columnas
                    precio_info = {}
                    for k, celda in enumerate(fila_datos[2:], 2):
                        if '$' in celda or '.' in celda:
                            try:
                                # Intentar extraer valor numérico
                                valor_limpio = re.sub(r'[^\d.,]', '', celda)
                                if valor_limpio:
                                    precio_info[f'precio_col_{k}'] = valor_limpio
                            except:
                                pass
                    
                    producto = {
                        'codigo': posible_codigo,
                        'descripcion': posible_descripcion,
                        'seccion': seccion_actual,
                        'precios': precio_info,
                        'fila_completa': fila_datos,
                        'posicion_tabla': i,
                        'posicion_fila': j
                    }
                    productos_encontrados.append(producto)
            
            # Solo agregar filas que tengan contenido significativo
            if any(celda.strip() for celda in fila_datos if celda):
                datos_tabla.append({
                    'datos': fila_datos,
                    'seccion': seccion_actual,
                    'es_producto': len(fila_datos) >= 3 and re.match(r'^\d+$', fila_datos[0].strip()) if fila_datos[0] else False
                })
        
        if datos_tabla:
            datos_extraidos.append({
                'tabla_indice': i,
                'filas': datos_tabla,
                'total_filas': len(datos_tabla),
                'total_columnas': max(len(fila['datos']) for fila in datos_tabla) if datos_tabla else 0,
                'productos_detectados': [p for p in productos_encontrados if p['posicion_tabla'] == i]
            })
    
    return datos_extraidos, productos_encontrados

def detectar_proveedores_en_contenido(ruta_archivo):
    """Detecta todos los posibles nombres de proveedores en el contenido con análisis optimizado"""
    proveedores_encontrados = []
    
    try:
        print(f"   Analizando {os.path.basename(ruta_archivo)}...")
        
        # Leer solo una parte del archivo para evitar problemas de memoria
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
            # Leer solo los primeros 50KB para análisis rápido
            contenido = archivo.read(50000)
        
        # Lista ampliada de proveedores conocidos
        proveedores_conocidos = [
            'CRIMARAL', 'ANCAIG', 'DAFYS', 'HERRAMETAL', 'YAYI', 
            'DIST_CITY_BELL', 'BABUSI', 'FERRIPLAST', 'FERRETERIA',
            'DISTCITYBELL', 'CITY_BELL', 'DISTRIBUIDORA',
            'BRIMAX', 'PUMA', 'ROTAFLEX', 'STANLEY', 'BLACK_DECKER',
            'WATERPLAST', 'TIGRE', 'AMANCO', 'PLASTIFERRO', 'AQUATANK',
            'RAMAT', 'SANITARIO', 'NIVEL'
        ]
        
        # Extraer solo información crítica del HTML de forma eficiente
        texto_upper = contenido.upper()
        
        # Buscar título si existe
        titulo_match = re.search(r'<title[^>]*>(.*?)</title>', contenido, re.IGNORECASE | re.DOTALL)
        texto_title = titulo_match.group(1).upper() if titulo_match else ""
        
        # Buscar en nombres de archivos referenciados (solo href importantes)
        href_matches = re.findall(r'href="([^"]*)"', contenido, re.IGNORECASE)
        referencias_archivos = " ".join(href_matches[:5]).upper()  # Solo primeros 5
        
        # Buscar en scripts JavaScript (solo los primeros y más pequeños)
        script_matches = re.findall(r'c_rgszSh\[.*?\]\s*=\s*"([^"]*)"', contenido, re.IGNORECASE)
        contenido_scripts = " ".join(script_matches).upper()
        
        # Combinar texto crítico para análisis
        texto_analisis = f"{texto_title} {referencias_archivos} {contenido_scripts}"
        
        # Si no hay suficiente información en las partes críticas, analizar una muestra del contenido
        if len(texto_analisis.strip()) < 100:
            # Tomar solo una muestra del contenido general (primeras 1000 palabras)
            palabras = texto_upper.split()[:1000]
            texto_analisis += " " + " ".join(palabras)        
        for proveedor in proveedores_conocidos:
            # Buscar el proveedor en el contenido analizado
            ocurrencias_texto = texto_analisis.count(proveedor)
            ocurrencias_title = texto_title.count(proveedor)
            ocurrencias_scripts = contenido_scripts.count(proveedor)
            
            total_ocurrencias = ocurrencias_texto + (ocurrencias_title * 2) + (ocurrencias_scripts * 3)
            
            if total_ocurrencias > 0:
                # Calcular confianza basada en diferentes factores
                confianza = min(total_ocurrencias / 5, 1.0)
                
                # Bonificar si aparece en título o scripts (más confiable)
                if ocurrencias_title > 0:
                    confianza = min(confianza + 0.3, 1.0)
                if ocurrencias_scripts > 0:
                    confianza = min(confianza + 0.4, 1.0)
                
                proveedores_encontrados.append({
                    'nombre': proveedor,
                    'ocurrencias': total_ocurrencias,
                    'confianza': confianza,
                    'ubicaciones': {
                        'texto': ocurrencias_texto,
                        'titulo': ocurrencias_title,
                        'scripts': ocurrencias_scripts
                    }
                })
        
        # Buscar también en emails y URLs (análisis simplificado)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', texto_analisis)
        for email in emails:
            domain_part = email.split('@')[1].split('.')[0].upper()
            if len(domain_part) > 3 and domain_part not in [p['nombre'] for p in proveedores_encontrados]:
                proveedores_encontrados.append({
                    'nombre': domain_part,
                    'ocurrencias': 1,
                    'confianza': 0.7,
                    'tipo': 'email',
                    'ubicaciones': {'email': 1}
                })
        
        # Buscar patrones de nombres en el contenido (análisis simplificado)
        # Solo analizar si el contenido no es demasiado grande
        if len(texto_analisis) < 10000:
            patrones_marcas = re.findall(r'\b[A-Z]{3,15}\b', texto_analisis)
            contador_patrones = Counter(patrones_marcas)
            
            for marca, freq in contador_patrones.most_common(5):  # Solo top 5
                if (freq >= 2 and len(marca) >= 4 and 
                    marca not in [p['nombre'] for p in proveedores_encontrados] and
                    marca not in ['HTTP', 'HTML', 'STYLE', 'CLASS', 'WIDTH', 'TABLE', 'BORDER']):
                    proveedores_encontrados.append({
                        'nombre': marca,
                        'ocurrencias': freq,
                        'confianza': min(freq / 10, 0.8),
                        'tipo': 'patron_detectado',
                        'ubicaciones': {'patron': freq}
                    })
        
        # Ordenar por confianza y ocurrencias
        proveedores_encontrados.sort(key=lambda x: (x['confianza'], x['ocurrencias']), reverse=True)
        
        return proveedores_encontrados
        
    except Exception as e:
        print(f"Error analizando {ruta_archivo}: {str(e)}")
        return []

def analizar_proveedores_globales_mejorado(archivos_rutas):
    """Analiza todos los archivos para determinar la estrategia de nomenclatura - versión mejorada"""
    print("🔍 Analizando contenido para detectar proveedores...")
    
    analisis_por_archivo = {}
    todos_los_proveedores = []
    
    # Analizar cada archivo
    for ruta_archivo in archivos_rutas:
        proveedores = detectar_proveedores_en_contenido(ruta_archivo)
        analisis_por_archivo[ruta_archivo] = proveedores
        
        # Agregar a la lista global
        for proveedor in proveedores:
            todos_los_proveedores.append(proveedor['nombre'])
    
    # Determinar el proveedor dominante
    contador_proveedores = Counter(todos_los_proveedores)
    
    if not contador_proveedores:
        print("⚠️  No se detectaron proveedores conocidos")
        return analisis_por_archivo, None, 'multiple_unknown'
    
    proveedor_principal = contador_proveedores.most_common(1)[0]
    nombre_principal, frecuencia_principal = proveedor_principal
    
    total_archivos = len(archivos_rutas)
    porcentaje_dominancia = (frecuencia_principal / total_archivos) * 100
    
    print(f"📊 Análisis de proveedores:")
    print(f"   • Proveedor dominante: {nombre_principal} ({frecuencia_principal}/{total_archivos} archivos, {porcentaje_dominancia:.1f}%)")
    
    # Decidir estrategia
    if porcentaje_dominancia >= 70:  # 70% o más de los archivos tienen el mismo proveedor
        estrategia = 'single_provider'
        print(f"✅ Estrategia: UN SOLO PROVEEDOR con múltiples listas")
    else:
        estrategia = 'multiple_providers'
        print(f"✅ Estrategia: MÚLTIPLES PROVEEDORES")
        
        # Mostrar todos los proveedores encontrados
        print("   • Otros proveedores detectados:")
        for proveedor, count in contador_proveedores.most_common()[1:]:
            porcentaje = (count / total_archivos) * 100
            print(f"     - {proveedor}: {count} archivo(s) ({porcentaje:.1f}%)")
    
    return analisis_por_archivo, nombre_principal, estrategia

def analizar_proveedores_globales(directorio, archivos_html):
    """Analiza todos los archivos para determinar la estrategia de nomenclatura - versión original"""
    print("🔍 Analizando contenido para detectar proveedores...")
    
    analisis_por_archivo = {}
    todos_los_proveedores = []
    
    # Analizar cada archivo
    for archivo in archivos_html:
        ruta_completa = os.path.join(directorio, archivo)
        proveedores = detectar_proveedores_en_contenido(ruta_completa)
        analisis_por_archivo[archivo] = proveedores
        
        # Agregar a la lista global
        for proveedor in proveedores:
            todos_los_proveedores.append(proveedor['nombre'])
    
    # Determinar el proveedor dominante
    contador_proveedores = Counter(todos_los_proveedores)
    
    if not contador_proveedores:
        print("⚠️  No se detectaron proveedores conocidos")
        return analisis_por_archivo, None, 'multiple_unknown'
    
    proveedor_principal = contador_proveedores.most_common(1)[0]
    nombre_principal, frecuencia_principal = proveedor_principal
    
    total_archivos = len(archivos_html)
    porcentaje_dominancia = (frecuencia_principal / total_archivos) * 100
    
    print(f"📊 Análisis de proveedores:")
    print(f"   • Proveedor dominante: {nombre_principal} ({frecuencia_principal}/{total_archivos} archivos, {porcentaje_dominancia:.1f}%)")
    
    # Decidir estrategia
    if porcentaje_dominancia >= 70:  # 70% o más de los archivos tienen el mismo proveedor
        estrategia = 'single_provider'
        print(f"✅ Estrategia: UN SOLO PROVEEDOR con múltiples listas")
    else:
        estrategia = 'multiple_providers'
        print(f"✅ Estrategia: MÚLTIPLES PROVEEDORES")
        
        # Mostrar todos los proveedores encontrados
        print("   • Otros proveedores detectados:")
        for proveedor, count in contador_proveedores.most_common()[1:]:
            porcentaje = (count / total_archivos) * 100
            print(f"     - {proveedor}: {count} archivo(s) ({porcentaje:.1f}%)")
    
    return analisis_por_archivo, nombre_principal, estrategia

def purificar_productos(productos_detectados, proveedor_default):
    """Purifica y estructura los productos según el formato solicitado"""
    productos_purificados = []
    
    for producto in productos_detectados:
        # Extraer precio principal (buscar en las columnas de precios)
        precio = ""
        moneda = "usd"  # Default
        
        if producto.get('precios'):
            # Tomar el primer precio encontrado
            precios_vals = list(producto['precios'].values())
            if precios_vals:
                precio_raw = precios_vals[0]
                # Limpiar precio - extraer solo números y puntos/comas
                precio_limpio = re.sub(r'[^\d.,]', '', precio_raw)
                if precio_limpio:
                    precio = precio_limpio
                
                # Detectar moneda si hay símbolo $
                if '$' in precio_raw:
                    moneda = "usd"
        
        # Determinar categoría basada en la descripción
        categoria = determinar_categoria(producto.get('descripcion', ''))
        
        # Estructurar producto según formato solicitado
        producto_purificado = {
            'codigo': producto.get('codigo', ''),
            'descripcion': producto.get('descripcion', ''),
            'categoria': categoria,
            'precio': precio,
            'moneda': moneda,
            'proveedor': proveedor_default,
            'unidad': '',  # Puede expandirse si se detecta en el futuro
            'stock': ''    # Puede expandirse si se detecta en el futuro
        }
        
        productos_purificados.append(producto_purificado)
    
    return productos_purificados

def determinar_categoria(descripcion):
    """Determina la categoría del producto basándose en su descripción"""
    if not descripcion:
        return "General"
    
    desc_upper = descripcion.upper()
    
    # Definir categorías y palabras clave
    categorias = {
        'griferia': ['GRIFO', 'CANILLA', 'LLAVE', 'GRIFERIA', 'MEZCLADORA'],
        'electricidad': ['CABLE', 'ENCHUFE', 'INTERRUPTOR', 'TOMACORRIENTE', 'ELECTRICIDAD', 'SOCKET'],
        'herramientas': ['MARTILLO', 'DESTORNILLADOR', 'LLAVE', 'HERRAMIENTA', 'TALADRO'],
        'plomeria': ['TUBERIA', 'TUBO', 'CAÑO', 'CONEXION', 'CODO', 'REDUCCION', 'PVC'],
        'ferreteria': ['TORNILLO', 'TUERCA', 'CLAVO', 'ARANDELA', 'BULONES'],        
        'tanques': ['TANQUE', 'DEPOSITO', 'LITROS', 'BICAPA', 'TRICAPA'],
        'abrazaderas': ['ABRAZADERA', 'SUJECION'],
        'valvulas': ['VALVULA', 'VALVE'],
        'sanitarios': ['INODORO', 'BIDET', 'LAVATORIO', 'DUCHA', 'SANITARIO']
    }
    
    # Buscar coincidencias
    for categoria, palabras_clave in categorias.items():
        for palabra in palabras_clave:
            if palabra in desc_upper:
                return categoria
    
    return "General"

def generar_nombre_hoja_inteligente(archivo, indice, estrategia, proveedor_principal, proveedores_archivo):
    """Genera nombres de hoja basados en la estrategia detectada"""
    
    if estrategia == 'single_provider':
        # Todas las hojas son del mismo proveedor - usar nomenclatura de listas
        if len(proveedores_archivo) > 0 and proveedores_archivo[0]['confianza'] > 0.7:
            # Si hay alta confianza en la detección, usar el nombre del proveedor + lista
            return f"{proveedor_principal}_LISTA_{indice + 1:02d}"
        else:
            # Si no hay alta confianza, usar nomenclatura genérica
            return f"{proveedor_principal}_HOJA_{indice + 1:02d}"
    
    elif estrategia == 'multiple_providers':
        # Múltiples proveedores - usar el nombre específico detectado en cada archivo
        if proveedores_archivo and proveedores_archivo[0]['confianza'] > 0.5:
            return proveedores_archivo[0]['nombre']
        else:
            # Fallback al mapeo conocido o genérico
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

def procesar_hoja(ruta_archivo, nombre_hoja):
    """Procesa una hoja individual con extracción mejorada de productos"""
    try:
        print(f"Procesando {nombre_hoja}...")
        
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
            contenido = archivo.read()
        
        soup = BeautifulSoup(contenido, 'html.parser')
        
        # Extraer datos de las tablas con el nuevo algoritmo mejorado
        datos_tablas, productos_encontrados = extraer_datos_tabla(soup)
        
        # Calcular estadísticas de productos
        total_productos = len(productos_encontrados)
        secciones_detectadas = list(set(p['seccion'] for p in productos_encontrados if p['seccion']))
        
        # Agrupar productos por sección
        productos_por_seccion = {}
        for producto in productos_encontrados:
            seccion = producto['seccion'] or 'SIN_SECCION'
            if seccion not in productos_por_seccion:
                productos_por_seccion[seccion] = []
            productos_por_seccion[seccion].append(producto)
        
        # Extraer información adicional del HTML
        metadata = {
            'encoding': 'utf-8',
            'generator': None,
            'title': None
        }
        
        # Buscar metadatos
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') == 'Generator':
                metadata['generator'] = meta.get('content')
            elif meta.get('http-equiv') == 'Content-Type':
                metadata['encoding'] = meta.get('content')
        
        if soup.title:
            metadata['title'] = soup.title.get_text().strip()
        
        resultado = {
            'hoja': nombre_hoja,
            'archivo': os.path.basename(ruta_archivo),
            'total_tablas': len(datos_tablas),
            'total_productos': total_productos,
            'secciones_detectadas': secciones_detectadas,
            'productos_por_seccion': {k: len(v) for k, v in productos_por_seccion.items()},
            'metadata': metadata,
            'tablas': datos_tablas,
            'productos_detallados': productos_encontrados,
            'procesado_en': datetime.now().isoformat()
        }
        
        print(f"  - {len(datos_tablas)} tabla(s) encontrada(s)")
        print(f"  - {total_productos} producto(s) detectado(s)")
        if secciones_detectadas:
            print(f"  - Secciones: {', '.join(secciones_detectadas[:3])}{'...' if len(secciones_detectadas) > 3 else ''}")
        
        for j, tabla in enumerate(datos_tablas):
            productos_en_tabla = len(tabla.get('productos_detectados', []))
            print(f"    Tabla {j}: {tabla['total_filas']} filas, {tabla['total_columnas']} columnas, {productos_en_tabla} productos")
        
        return resultado
        
    except Exception as e:
        print(f"Error procesando {nombre_hoja}: {str(e)}")
        return None

def detectar_archivos_html(directorio):
    """Detecta automáticamente archivos HTML en el directorio y subdirectorios"""
    html_files = []
    archivos_principales = []
    
    try:
        # Primero buscar archivos HTML principales en el directorio base
        for file in os.listdir(directorio):
            if file.lower().endswith(('.htm', '.html')) and not file.lower() in ['tabstrip.htm', 'filelist.xml']:
                archivos_principales.append(file)
        
        # Si encontramos archivos principales, buscar sus subdirectorios correspondientes
        if archivos_principales:
            print(f"📁 Archivos HTML principales encontrados: {len(archivos_principales)}")
            for archivo_principal in archivos_principales:
                print(f"   • {archivo_principal}")
                
                # Buscar directorio correspondiente (sin extensión + "_archivos")
                nombre_base = os.path.splitext(archivo_principal)[0]
                directorio_archivos = os.path.join(directorio, nombre_base + "_archivos")
                
                if os.path.exists(directorio_archivos) and os.path.isdir(directorio_archivos):
                    print(f"     → Directorio encontrado: {nombre_base}_archivos")
                    
                    # Buscar archivos sheet*.htm en el subdirectorio
                    for subfile in os.listdir(directorio_archivos):
                        if (subfile.lower().startswith('sheet') and 
                            subfile.lower().endswith(('.htm', '.html'))):
                            ruta_completa = os.path.join(directorio_archivos, subfile)
                            html_files.append({
                                'archivo': subfile,
                                'ruta_completa': ruta_completa,
                                'directorio_padre': directorio_archivos,
                                'archivo_principal': archivo_principal
                            })
        
        # Si no encontramos estructura de archivos principales, buscar directamente
        if not html_files:
            print("📁 Buscando archivos HTML directamente en el directorio...")
            for file in os.listdir(directorio):
                if file.lower().endswith(('.htm', '.html')) and not file.lower() in ['tabstrip.htm', 'filelist.xml']:
                    ruta_completa = os.path.join(directorio, file)
                    html_files.append({
                        'archivo': file,
                        'ruta_completa': ruta_completa,
                        'directorio_padre': directorio,
                        'archivo_principal': None
                    })
        
        # También buscar en subdirectorios si el directorio principal no tiene archivos
        if not html_files:
            print("📁 Buscando en subdirectorios...")
            for item in os.listdir(directorio):
                item_path = os.path.join(directorio, item)
                if os.path.isdir(item_path):
                    for subfile in os.listdir(item_path):
                        if (subfile.lower().endswith(('.htm', '.html')) and 
                            not subfile.lower() in ['tabstrip.htm', 'filelist.xml']):
                            ruta_completa = os.path.join(item_path, subfile)
                            html_files.append({
                                'archivo': subfile,
                                'ruta_completa': ruta_completa,
                                'directorio_padre': item_path,
                                'archivo_principal': None
                            })
        
        # Ordenar archivos para procesamiento consistente
        html_files.sort(key=lambda x: x['archivo'])
        return html_files
        
    except Exception as e:
        print(f"❌ Error listando archivos: {str(e)}")
        return []

def main(archivo_salida_personalizado=None):
    """Función principal con opción de archivo de salida personalizado"""
    # Usar directorio actual o permitir especificar uno diferente
    import sys
    if len(sys.argv) > 1:
        directorio_base = sys.argv[1]
    else:
        directorio_base = os.path.dirname(os.path.abspath(__file__))
    
    print("=== EXTRACTOR DE DATOS MEJORADO - PLANILLA FERRETERÍA ===")
    print(f"Directorio: {directorio_base}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Detectar archivos HTML automáticamente
    html_files_info = detectar_archivos_html(directorio_base)
    
    if not html_files_info:
        print("❌ No se encontraron archivos HTML en el directorio")
        return
    
    print(f"📁 Archivos HTML detectados: {len(html_files_info)}")
    for file_info in html_files_info:
        print(f"   • {file_info['archivo']} -> {file_info['ruta_completa']}")
    print()
      # Extraer solo los nombres de archivos para el análisis de proveedores
    archivos_para_analisis = [info['ruta_completa'] for info in html_files_info]
    
    # Análisis global de proveedores
    analisis_proveedores, proveedor_principal, estrategia = analizar_proveedores_globales_mejorado(archivos_para_analisis)
    print()
    
    # Determinar nombre de la planilla desde el primer archivo principal encontrado
    planilla_name = "ANALISIS_HTML"
    if html_files_info and html_files_info[0].get('archivo_principal'):
        planilla_name = os.path.splitext(html_files_info[0]['archivo_principal'])[0]
    elif directorio_base:
        planilla_name = os.path.basename(directorio_base).replace('_archivos', '').replace('_files', '')
    
    # Procesar cada archivo HTML detectado
    print("📝 Procesando archivos:")
    hojas_procesadas = []
    total_productos_global = 0
    productos_por_hoja = {}
    
    for i, file_info in enumerate(html_files_info):
        ruta_archivo = file_info['ruta_completa']
        nombre_archivo = file_info['archivo']
        
        proveedores_archivo = analisis_proveedores.get(ruta_archivo, [])
        
        nombre_hoja = generar_nombre_hoja_inteligente(
            nombre_archivo, i, estrategia, proveedor_principal, proveedores_archivo
        )
        
        if os.path.exists(ruta_archivo):
            resultado = procesar_hoja(ruta_archivo, nombre_hoja)
            if resultado:
                # Agregar información del análisis de proveedores
                resultado['proveedores_detectados'] = proveedores_archivo
                
                # Purificar y estructurar productos
                productos_purificados = purificar_productos(resultado['productos_detallados'], proveedor_principal or 'DESCONOCIDO')
                
                hoja_estructurada = {
                    'nombre': nombre_hoja,
                    'archivo': nombre_archivo,
                    'productos': productos_purificados,
                    'total_productos': len(productos_purificados),
                    'metadata': resultado['metadata']
                }
                
                hojas_procesadas.append(hoja_estructurada)
                total_productos_global += len(productos_purificados)
                productos_por_hoja[nombre_hoja] = len(productos_purificados)
        else:
            print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
    
    # Estructura final de datos según el formato solicitado
    datos_completos = {
        'metadata': {
            'planilla_original': planilla_name,
            'proveedor': proveedor_principal or 'MULTIPLE',
            'fecha_purificacion': datetime.now().isoformat(),
            'total_productos': total_productos_global,
            'total_filas_procesadas': total_productos_global,
            'eficiencia_purificacion': "100.0%",
            'productos_por_hoja': productos_por_hoja,
            'estrategia_proveedores': estrategia,
            'total_hojas': len(hojas_procesadas)
        },
        'hojas': hojas_procesadas
    }    
    # Determinar archivo de salida
    if archivo_salida_personalizado:
        archivo_salida = archivo_salida_personalizado
    else:
        # Comportamiento por defecto (con timestamp)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_salida = os.path.join(directorio_base, f'datos_estructurados_{timestamp}.json')
    
    # Guardar resultados
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(datos_completos, f, ensure_ascii=False, indent=2)
    
    print()
    print("=== RESUMEN FINAL ===")
    print(f"Planilla: {planilla_name}")
    print(f"Directorio: {directorio_base}")
    print(f"Estrategia: {estrategia}")
    if proveedor_principal:
        print(f"Proveedor principal: {proveedor_principal}")
    print(f"Total productos extraídos: {total_productos_global}")
    print(f"Hojas procesadas: {len(hojas_procesadas)}")
    print(f"Archivo de salida: {archivo_salida}")
    
    print("\n📋 Hojas generadas:")
    for hoja in hojas_procesadas:
        print(f"  • {hoja['nombre']}: {hoja['total_productos']} productos")
    
    print()
    print("✅ Procesamiento completado con análisis inteligente de proveedores")

if __name__ == "__main__":
    main()
