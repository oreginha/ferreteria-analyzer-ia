#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer datos estructurados de las hojas de Excel convertidas a HTML

CARACTERÍSTICAS:
- Detección automática de archivos HTML en el directorio
- Mapeo inteligente de nombres de proveedores
- Soporte para directorios personalizados
- Generación dinámica de nombres de planilla

USO:
- python extraer_datos.py                    # Usa directorio actual
- python extraer_datos.py "ruta/directorio"  # Usa directorio específico
"""

import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

def limpiar_texto(texto):
    """Limpia y normaliza el texto"""
    if not texto:
        return ""
    
    # Remover espacios extra y caracteres especiales
    texto = re.sub(r'\s+', ' ', texto.strip())
    texto = texto.replace('\xa0', ' ')  # Non-breaking space
    texto = texto.replace('\u00a0', ' ')  # Non-breaking space
    
    return texto

def identificar_columnas_precios(tabla):
    """
    Identifica las columnas de diferentes tipos de precios en una tabla
    Busca: BASE, SIN IVA, SIN IVA CON OFERTAS, COSTO FINAL, PUBLICO
    """
    columnas_precios = {
        'base': None,
        'sin_iva': None,
        'sin_iva_ofertas': None,
        'costo_final': None,
        'publico': None
    }
    
    # Buscar en las primeras filas headers
    for i, fila in enumerate(tabla[:5]):  # Buscar en las primeras 5 filas
        for j, celda in enumerate(fila):
            celda_upper = str(celda).upper().strip()
            
            # Identificar tipos de precio por palabras clave
            if 'BASE' in celda_upper and columnas_precios['base'] is None:
                columnas_precios['base'] = j
            elif 'SIN IVA CON OFERTAS' in celda_upper or 'SIN IVA OFERTAS' in celda_upper:
                columnas_precios['sin_iva_ofertas'] = j
            elif 'SIN IVA' in celda_upper and 'OFERTAS' not in celda_upper:
                columnas_precios['sin_iva'] = j
            elif 'COSTO FINAL' in celda_upper or 'FINAL' in celda_upper:
                columnas_precios['costo_final'] = j
            elif 'PUBLICO' in celda_upper or 'PÚBLICO' in celda_upper:
                columnas_precios['publico'] = j
    
    return columnas_precios

def extraer_precios_estructurados(fila_datos, columnas_precios):
    """
    Extrae precios estructurados según las columnas identificadas
    """
    precios = {}
    
    for tipo_precio, columna_idx in columnas_precios.items():
        if columna_idx is not None and columna_idx < len(fila_datos):
            celda = fila_datos[columna_idx]
            precio_normalizado = normalizar_precio_avanzado(celda)
            if precio_normalizado:
                precios[tipo_precio] = precio_normalizado
    
    return precios

def es_numero_precio(texto):
    """Verifica si un texto parece ser un precio"""
    if not texto or len(str(texto).strip()) == 0:
        return False
    
    # Buscar patrones de precio
    patron_precio = re.compile(r'^[\$\s]*[\d\.,]+$')
    return bool(patron_precio.match(str(texto).strip()))

def normalizar_precio_avanzado(precio_str):
    """Normaliza un string de precio a formato numérico"""
    if not precio_str:
        return None
    
    # Limpiar caracteres no numéricos excepto puntos y comas
    precio_limpio = re.sub(r'[^\d,.]', '', str(precio_str))
    
    if precio_limpio and precio_limpio not in ['0', '0,00', '0.00']:
        # Convertir comas a puntos para formato decimal
        precio_limpio = precio_limpio.replace(',', '.')
        try:
            return float(precio_limpio)
        except ValueError:
            return precio_limpio  # Retornar como string si no se puede convertir
    
    return None

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
        
        resultado = {
            'hoja': nombre_hoja,
            'archivo': os.path.basename(ruta_archivo),
            'total_tablas': len(datos_tablas),
            'tablas': datos_tablas,
            'procesado_en': datetime.now().isoformat()
        }
        
        print(f"  - {len(datos_tablas)} tabla(s) encontrada(s)")
        for j, tabla in enumerate(datos_tablas):
            print(f"    Tabla {j}: {tabla['total_filas']} filas, {tabla['total_columnas']} columnas")
        
        return resultado
        
    except Exception as e:
        print(f"Error procesando {nombre_hoja}: {str(e)}")
        return None

def detectar_nombre_desde_contenido(ruta_archivo):
    """Intenta detectar el nombre del proveedor desde el contenido del HTML"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
            contenido = archivo.read()
        
        soup = BeautifulSoup(contenido, 'html.parser')
        
        # Buscar en el título de la página
        titulo = soup.find('title')
        if titulo:
            texto_titulo = limpiar_texto(titulo.get_text()).upper()
            # Buscar nombres de proveedores conocidos en el título
            proveedores_conocidos = ['CRIMARAL', 'ANCAIG', 'DAFYS', 'HERRAMETAL', 'YAYI', 
                                   'DIST_CITY_BELL', 'BABUSI', 'FERRIPLAST', 'FERRETERIA']
            for proveedor in proveedores_conocidos:
                if proveedor in texto_titulo:
                    return proveedor
        
        # Buscar en encabezados de tabla
        encabezados = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for encabezado in encabezados:
            texto = limpiar_texto(encabezado.get_text()).upper()
            for proveedor in proveedores_conocidos:
                if proveedor in texto:
                    return proveedor
        
        # Buscar en las primeras celdas de las tablas
        tablas = soup.find_all('table')
        for tabla in tablas[:2]:  # Solo revisar las primeras 2 tablas
            filas = tabla.find_all('tr')[:3]  # Solo las primeras 3 filas
            for fila in filas:
                celdas = fila.find_all(['td', 'th'])
                for celda in celdas[:3]:  # Solo las primeras 3 celdas
                    texto = limpiar_texto(celda.get_text()).upper()
                    for proveedor in proveedores_conocidos:
                        if proveedor in texto:
                            return proveedor
        
        return None
        
    except Exception:
        return None

def determinar_nombre_hoja(archivo_html, ruta_completa=None):
    """Determina el nombre de la hoja/proveedor de forma inteligente"""
    
    # 1. Intentar detectar desde el contenido del archivo
    if ruta_completa and os.path.exists(ruta_completa):
        nombre_detectado = detectar_nombre_desde_contenido(ruta_completa)
        if nombre_detectado:
            return nombre_detectado
    
    # 2. Mapeo conocido para archivos comunes (fallback)
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
    
    if archivo_html in mapeo_archivos:
        return mapeo_archivos[archivo_html]
    
    # 3. Generar nombre inteligente desde el nombre del archivo
    nombre = os.path.splitext(archivo_html)[0]
    
    # Detectar patrones comunes
    if nombre.startswith('sheet'):
        numero = nombre.replace('sheet', '').replace('0', '')
        if numero.isdigit():
            return f'PROVEEDOR_{numero.zfill(2)}'
        else:
            return f'HOJA_{numero.upper()}'
    elif nombre.lower().startswith(('proveedor', 'supplier', 'vendor')):
        return nombre.upper().replace('_', '-')
    else:
        # Limpiar y formatear nombre genérico
        nombre_limpio = re.sub(r'[^a-zA-Z0-9_]', '_', nombre)
        return nombre_limpio.upper()
    
    return nombre.upper()

def detectar_archivos_html(directorio):
    """Detecta automáticamente archivos HTML en el directorio"""
    html_files = []
    try:
        for file in os.listdir(directorio):
            if file.lower().endswith(('.htm', '.html')) and not file.lower() in ['tabstrip.htm', 'filelist.xml']:
                html_files.append(file)
        
        # Ordenar archivos para procesamiento consistente
        html_files.sort()
        return html_files
        
    except Exception as e:
        print(f"❌ Error listando archivos: {str(e)}")
        return []

def extraer_datos_html(directorio, archivo_salida_personalizado=None):
    """
    Función mejorada para extraer datos con algoritmo v2 superior
    Replica la funcionalidad de la primera versión exitosa
    
    Args:
        directorio: Directorio que contiene los archivos HTML
        archivo_salida_personalizado: Ruta completa del archivo de salida (opcional)
    """
    try:
        import json
        import os
        from datetime import datetime
        from bs4 import BeautifulSoup
        import re
        
        # Detectar archivos HTML
        archivos_html = detectar_archivos_html(directorio)
        if not archivos_html:
            print("❌ No se encontraron archivos HTML")
            return None, None
        
        print(f"📁 Encontrados {len(archivos_html)} archivos HTML")
        
        # Inicializar estadísticas
        hojas_procesadas = []
        total_productos = 0
        total_filas_procesadas = 0
        productos_por_hoja = {}
        productos_con_codigo = 0
        productos_con_precio = 0
        productos_con_iva = 0
        
        # Detectar nombre de planilla desde directorio
        planilla_name = os.path.basename(directorio).replace('_archivos', '').replace('_files', '')
        if not planilla_name or planilla_name == '.':
            planilla_name = 'ANALISIS_HTML'
        
        # Procesar cada archivo
        for i, archivo_nombre in enumerate(archivos_html):
            try:
                # Construir ruta completa
                ruta_completa = os.path.join(directorio, archivo_nombre)
                
                print(f"🔍 Procesando: {archivo_nombre}")
                
                # Procesar archivo HTML usando algoritmo mejorado
                datos_hoja = procesar_archivo_html_completo(ruta_completa, archivo_nombre, i)
                
                if datos_hoja and datos_hoja.get('productos'):
                    hojas_procesadas.append(datos_hoja)
                    num_productos = len(datos_hoja['productos'])
                    total_productos += num_productos
                    
                    # Estadísticas por hoja
                    nombre_hoja = datos_hoja['nombre']
                    productos_por_hoja[nombre_hoja] = num_productos
                    
                    # Estadísticas de calidad de datos
                    for producto in datos_hoja['productos']:
                        total_filas_procesadas += 1
                        if producto.get('codigo'):
                            productos_con_codigo += 1
                        if producto.get('precio') or producto.get('precios'):
                            productos_con_precio += 1
                        if producto.get('iva') is not None:
                            productos_con_iva += 1
                    
                    print(f"   ✅ {num_productos} productos extraídos ({datos_hoja.get('proveedor', 'N/A')})")
                else:
                    print(f"   ⚠️ Sin productos válidos en {archivo_nombre}")
                    
            except Exception as e:
                print(f"❌ Error procesando {archivo_nombre}: {e}")
                continue
        if not hojas_procesadas:
            print("❌ No se procesaron hojas válidas")
            return None, None
        
        # Calcular eficiencia de purificación
        eficiencia = (total_productos / total_filas_procesadas * 100) if total_filas_procesadas > 0 else 0
        
        # Detectar proveedor principal
        proveedores_detectados = {}
        for hoja in hojas_procesadas:
            proveedor = hoja.get('proveedor', 'VARIOS')
            proveedores_detectados[proveedor] = proveedores_detectados.get(proveedor, 0) + 1
        
        proveedor_principal = max(proveedores_detectados.items(), key=lambda x: x[1])[0] if proveedores_detectados else 'VARIOS'
        
        # Crear estructura de datos completa con metadatos (como en v2)
        resultado = {
            'metadata': {
                'planilla_original': planilla_name.upper(),
                'proveedor': proveedor_principal,
                'fecha_purificacion': datetime.now().isoformat(),
                'total_productos': total_productos,
                'total_filas_procesadas': total_filas_procesadas,
                'eficiencia_purificacion': f"{eficiencia:.1f}%",
                'productos_por_hoja': productos_por_hoja
            },
            'estadisticas': {
                'productos_con_codigo': productos_con_codigo,
                'productos_con_precio': productos_con_precio,
                'productos_con_medida': 0,  # Implementar si es necesario
                'productos_con_iva': productos_con_iva
            },
            'productos': [],
            # Mantener compatibilidad con estructura anterior
            'hojas': hojas_procesadas,
            'resumen': {
                'total_hojas': len(hojas_procesadas),
                'total_productos': total_productos,
                'directorio_origen': directorio
            },
            'fecha_procesamiento': datetime.now().isoformat(),
            'estrategia_proveedores': 'single_provider' if len(proveedores_detectados) == 1 else 'multiple_providers',
            'proveedor_principal': proveedor_principal
        }
          # Agregar todos los productos a la lista plana (como en v2)
        for hoja in hojas_procesadas:
            for producto in hoja['productos']:
                resultado['productos'].append(producto)
        
        print(f"✅ Extracción completada con metadatos:")
        print(f"   📊 {len(hojas_procesadas)} hojas procesadas")
        print(f"   🛍️ {total_productos} productos únicos")
        print(f"   📈 Eficiencia: {eficiencia:.1f}%")
        print(f"   🏷️ Proveedor principal: {proveedor_principal}")
        print(f"   📋 Productos con código: {productos_con_codigo}")
        print(f"   💰 Productos con precio: {productos_con_precio}")
        print(f"   📊 Productos con IVA: {productos_con_iva}")
        
        # Determinar archivo de salida
        if archivo_salida_personalizado:
            archivo_salida = archivo_salida_personalizado
        else:
            # Comportamiento por defecto (con timestamp)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_salida = os.path.join(directorio, f'datos_estructurados_{timestamp}.json')
        
        # Guardar resultados
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Archivo guardado en: {archivo_salida}")
        
        return resultado, archivo_salida
    except Exception as e:
        print(f"❌ Error en extraer_datos_html: {e}")
        return None, None

def procesar_archivo_html_completo(ruta_archivo, nombre_archivo, indice):
    """Procesa un archivo HTML completo y extrae productos con algoritmo mejorado"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
            contenido = archivo.read()
        
        soup = BeautifulSoup(contenido, 'html.parser')
        tablas = soup.find_all('table')
        
        if not tablas:
            return None
        
        # Detectar proveedor en el contenido
        proveedor = detectar_proveedor_en_contenido(contenido)
        
        # Extraer productos de todas las tablas
        productos = []
        
        for tabla in tablas:
            productos_tabla = extraer_productos_de_tabla(tabla)
            productos.extend(productos_tabla)
        
        if not productos:
            return None
        
        # Determinar nombre de hoja inteligente
        nombre_hoja = generar_nombre_hoja_inteligente(nombre_archivo, proveedor, indice)
        
        # Agregar proveedor a cada producto
        for producto in productos:
            if not producto.get('proveedor'):
                producto['proveedor'] = proveedor
            producto['hoja'] = nombre_hoja
        
        return {
            'nombre': nombre_hoja,
            'archivo': nombre_archivo,
            'productos': productos,
            'total_productos': len(productos),
            'proveedor': proveedor
        }
        
    except Exception as e:
        print(f"Error procesando archivo HTML {nombre_archivo}: {e}")
        return None

def detectar_proveedor_en_contenido(contenido):
    """Detecta el proveedor principal en el contenido del archivo"""
    import re
    
    # Lista de proveedores conocidos con patrones
    proveedores_conocidos = {
        'YAYI': [r'YAYI', r'yayi'],
        'CRIMARAL': [r'CRIMARAL', r'crimaral'],
        'ANCAIG': [r'ANCAIG', r'ancaig'],
        'DAFYS': [r'DAFYS', r'dafys'],
        'HERRAMETAL': [r'HERRAMETAL', r'herrametal'],
        'FERRIPLAST': [r'FERRIPLAST', r'ferriplast'],
        'BABUSI': [r'BABUSI', r'babusi'],
        'DIST_CITY_BELL': [r'DIST.*CITY.*BELL', r'DISTRIBUIDORA.*CITY', r'CITY.*BELL'],
        'BRIMAX': [r'BRIMAX', r'brimax'],
        'PUMA': [r'PUMA', r'puma'],
        'ROTAFLEX': [r'ROTAFLEX', r'rotaflex'],
        'STANLEY': [r'STANLEY', r'stanley'],
        'BLACK_DECKER': [r'BLACK.*DECKER', r'BLACK&DECKER']
    }
    
    texto_contenido = contenido.upper()
    detecciones = {}
    
    for proveedor, patrones in proveedores_conocidos.items():
        conteo = 0
        for patron in patrones:
            matches = re.findall(patron, texto_contenido, re.IGNORECASE)
            conteo += len(matches)
        
        if conteo > 0:
            detecciones[proveedor] = conteo
    
    # Devolver el proveedor con más apariciones
    if detecciones:
        proveedor_principal = max(detecciones.items(), key=lambda x: x[1])[0]
        return proveedor_principal
    
    return 'VARIOS'

def generar_nombre_hoja_inteligente(nombre_archivo, proveedor, indice):
    """Genera un nombre de hoja inteligente basado en el proveedor y contenido"""
    
    # Limpiar nombre de archivo
    nombre_base = nombre_archivo.replace('.htm', '').replace('.html', '')
    
    # Si detectamos un proveedor específico
    if proveedor != 'VARIOS':
        if 'sheet' in nombre_base.lower():
            numero_hoja = nombre_base.replace('sheet', '').replace('0', '')
            try:
                num = int(numero_hoja)
                if num <= 2:
                    return f"{proveedor}_LISTA_{num:02d}"
                else:
                    return f"{proveedor}_HOJA_{num:02d}"
            except:
                pass
        
        return f"{proveedor}_LISTA_{indice+1:02d}"
    
    # Nombre genérico
    return f"HOJA_{indice+1:02d}"

def extraer_productos_de_tabla(tabla):
    """Extrae productos de una tabla HTML usando algoritmo mejorado v2"""
    productos = []
    
    try:
        filas = tabla.find_all('tr')
        
        if len(filas) < 1:
            return productos
        
        # Convertir tabla HTML a matriz de datos
        matriz_tabla = []
        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            fila_datos = [limpiar_texto(celda.get_text()) for celda in celdas]
            if fila_datos:  # Solo agregar filas con datos
                matriz_tabla.append(fila_datos)
        
        if not matriz_tabla:
            return productos
        
        # Identificar columnas de precios
        columnas_precios = identificar_columnas_precios(matriz_tabla)
        
        # Procesar cada fila con algoritmo sofisticado
        for fila_datos in matriz_tabla:
            # Usar algoritmo de clasificación inteligente con precios estructurados
            producto = procesar_fila_inteligente_v2(fila_datos, columnas_precios)
            
            if producto:
                productos.append(producto)
    
    except Exception as e:
        print(f"Error extrayendo productos de tabla: {e}")
    
    return productos

def procesar_fila_inteligente(fila):
    """Procesa una fila usando algoritmo de clasificación inteligente"""
    import re
    
    # Patrones especializados (basados en v2)
    patron_codigo = re.compile(r'^[0-9]{6,8}$')
    patron_precio = re.compile(r'^[\$\s]*[\d\.,]+$')
    patron_medida = re.compile(r'^\d+/\d+$|^\d+x\d+$|^\d+mm$|^\d+cm$|^\d+"$')
    patron_iva = re.compile(r'^\d{1,2}$')
    
    # Patrones irrelevantes
    patrones_irrelevantes = [
        r'BUSCADOR RAPIDO', r'distribuidora.*@.*\.com', r'Precios orientativos',
        r'CALCULADORA.*', r'COMPLETAR DONDE DICE', r'FUNCIONAMIENTO',
        r'INGRESAR.*CENTIMETROS', r'MARGEN DE GANANCIA', r'POR DEFECTO VIENE',
        r'UwU', r'AQU VER LA DESCRIPCIN', r'CODIGO.*DESCRIPCION.*BASE',
        r'ESCRIBA AQUI MISMO UN CODIGO', r'DIAMETRO DEL CAO',
        r'^DESCRIPCION$', r'^YAYI$', r'^Gs\s*-$', r'^\.$', r'^-$', r'^\+$',
        r'OFERTAS', r'FECHA', r'% GANANCIA', r'PUBLICO', r'CODIGO DE FABRICA',
        r'SIN IVA.*', r'COSTO FINAL', r'BASE', r'CON OFERTAS'
    ]
    
    def es_texto_irrelevante(texto):
        if not texto or texto.strip() == '':
            return True
        texto = str(texto).strip()
        
        for patron in patrones_irrelevantes:
            if re.search(patron, texto, re.IGNORECASE):
                return True
        
        if len(texto) > 100 and any(palabra in texto.lower() for palabra in 
                                   ['ingresar', 'completar', 'funcionamiento', 'recuerde', 'defecto']):
            return True
        
        if len(texto) <= 2 and texto not in ['MM', 'CM', 'M', 'L', 'XL']:
            return True
        
        return False
    
    def normalizar_precio(precio_str):
        precio_limpio = re.sub(r'[^\d,.]', '', str(precio_str))
        if precio_limpio and precio_limpio not in ['0', '0,00', '0.00']:
            return precio_limpio
        return None
    
    def clasificar_campo(valor):
        valor_str = str(valor).strip()
        
        if not valor_str or valor_str == '':
            return None
        
        # Código de producto (6-8 dígitos)
        if patron_codigo.match(valor_str):
            return {'tipo': 'codigo', 'valor': valor_str}
        
        # IVA (1-2 dígitos)
        if patron_iva.match(valor_str) and valor_str.isdigit() and int(valor_str) <= 50:
            return {'tipo': 'iva', 'valor': valor_str}
        
        # Precio (contiene números y separadores)
        precio_normalizado = normalizar_precio(valor_str)
        if precio_normalizado:
            return {'tipo': 'precio', 'valor': precio_normalizado}
        
        # Medida específica
        if patron_medida.match(valor_str):
            return {'tipo': 'medida', 'valor': valor_str}
        
        # Descripción (texto útil)
        if not es_texto_irrelevante(valor_str) and 3 <= len(valor_str) <= 80:
            descripcion_limpia = re.sub(r'\s+', ' ', valor_str).strip()
            if descripcion_limpia and len(descripcion_limpia) >= 3:
                return {'tipo': 'descripcion', 'valor': descripcion_limpia}
        
        return None
    
    # Clasificar todos los campos de la fila
    campos_clasificados = []
    for valor in fila:
        clasificacion = clasificar_campo(valor)
        if clasificacion:
            campos_clasificados.append(clasificacion)
    
    if not campos_clasificados:
        return None
    
    # Organizar producto
    producto = {}
    precios_encontrados = []
    
    for campo in campos_clasificados:
        tipo = campo['tipo']
        valor = campo['valor']
        
        if tipo == 'codigo':
            producto['codigo'] = valor
        elif tipo == 'precio':
            precios_encontrados.append(valor)
        elif tipo == 'descripcion':
            # Solo usar la descripción más larga y específica
            if 'descripcion' not in producto or len(valor) > len(producto['descripcion']):
                producto['descripcion'] = valor
        elif tipo == 'medida':
            producto['medida'] = valor
        elif tipo == 'iva':
            producto['iva'] = int(valor)
    
    # Agregar precios
    if precios_encontrados:
        precios_unicos = []
        for precio in precios_encontrados:
            if precio not in precios_unicos:
                precios_unicos.append(precio)
        
        if len(precios_unicos) == 1:
            producto['precio'] = precios_unicos[0]
        else:
            producto['precios'] = precios_unicos
    
    # Validar producto
    tiene_codigo = 'codigo' in producto
    tiene_descripcion = 'descripcion' in producto
    descripcion_especifica = tiene_descripcion and len(producto['descripcion']) > 10
    
    if (tiene_codigo and tiene_descripcion) or descripcion_especifica:
        # Agregar campos por defecto
        if 'categoria' not in producto:
            producto['categoria'] = 'General'
        if 'proveedor' not in producto:
            producto['proveedor'] = ''
        
        return producto
    
    return None

def procesar_fila_inteligente_v2(fila_datos, columnas_precios):
    """
    Procesa una fila usando algoritmo de clasificación inteligente v2
    con identificación específica de tipos de precios
    """
    import re
    
    # Patrones especializados
    patron_codigo = re.compile(r'^[0-9]{6,8}$')
    patron_medida = re.compile(r'^\d+/\d+$|^\d+x\d+$|^\d+mm$|^\d+cm$|^\d+"$')
    patron_iva = re.compile(r'^\d{1,2}$')
      # Clasificar campos
    campos_clasificados = {
        'codigo': None,
        'descripcion': None,
        'iva': None,
        'medida': None,
        'precios': {}
    }
    
    # Extraer precios estructurados usando las columnas identificadas
    precios_estructurados = extraer_precios_estructurados(fila_datos, columnas_precios)
    campos_clasificados['precios'] = precios_estructurados
      # Clasificar otros campos
    for i, valor in enumerate(fila_datos):
        if i in columnas_precios.values():
            continue  # Skip price columns, already processed
        
        campo = clasificar_campo_v2(valor)
        if campo:
            tipo, valor_limpio = campo['tipo'], campo['valor']
            
            if tipo == 'codigo' and not campos_clasificados['codigo']:
                campos_clasificados['codigo'] = valor_limpio
            elif tipo == 'descripcion' and not campos_clasificados['descripcion']:
                campos_clasificados['descripcion'] = valor_limpio
            elif tipo == 'iva' and not campos_clasificados['iva']:
                campos_clasificados['iva'] = valor_limpio
            elif tipo == 'medida' and not campos_clasificados['medida']:
                campos_clasificados['medida'] = valor_limpio
    
    # Validar que el producto tenga información suficiente
    if (campos_clasificados['descripcion'] and len(campos_clasificados['descripcion']) > 3) or \
       (campos_clasificados['codigo']) or \
       (campos_clasificados['precios']):
          producto = {
            'codigo': campos_clasificados['codigo'],
            'descripcion': campos_clasificados['descripcion'] or 'Sin descripción',
            'precios_estructurados': campos_clasificados['precios'],  # Nuevo campo estructurado
            'iva': campos_clasificados['iva'],
            'medida': campos_clasificados['medida'],
            'fila_completa': fila_datos
        }
        
        # También mantener formato legacy para compatibilidad
        if campos_clasificados['precios']:
            # Usar el primer precio encontrado como precio principal
            precio_principal = None
            for tipo in ['publico', 'costo_final', 'sin_iva', 'base']:
                if tipo in campos_clasificados['precios'] and campos_clasificados['precios'][tipo]:
                    precio_principal = campos_clasificados['precios'][tipo]
                    break
            
            if precio_principal:
                producto['precio'] = precio_principal
        
        return producto
    
    return None

def clasificar_campo_v2(valor):
    """Versión mejorada de clasificación de campos"""
    import re
    
    valor_str = str(valor).strip()
    
    if not valor_str or valor_str == '':
        return None
    
    # Patrones irrelevantes actualizados para no incluir tipos de precio
    patrones_irrelevantes = [
        r'BUSCADOR RAPIDO', r'distribuidora.*@.*\.com', r'Precios orientativos',
        r'CALCULADORA.*', r'COMPLETAR DONDE DICE', r'FUNCIONAMIENTO',
        r'INGRESAR.*CENTIMETROS', r'MARGEN DE GANANCIA', r'POR DEFECTO VIENE',
        r'UwU', r'AQU VER LA DESCRIPCIN', r'CODIGO.*DESCRIPCION.*BASE',
        r'ESCRIBA AQUI MISMO UN CODIGO', r'DIAMETRO DEL CAO',
        r'^DESCRIPCION$', r'^YAYI$', r'^Gs\s*-$', r'^\.$', r'^-$', r'^\+$',
        r'OFERTAS', r'FECHA', r'% GANANCIA', r'CODIGO DE FABRICA'
    ]
    
    # Verificar si es texto irrelevante
    for patron in patrones_irrelevantes:
        if re.search(patron, valor_str, re.IGNORECASE):
            return None
    
    # Código de producto (6-8 dígitos)
    patron_codigo = re.compile(r'^[0-9]{6,8}$')
    if patron_codigo.match(valor_str):
        return {'tipo': 'codigo', 'valor': valor_str}
    
    # IVA (1-2 dígitos, valor <= 50)
    patron_iva = re.compile(r'^\d{1,2}$')
    if patron_iva.match(valor_str) and valor_str.isdigit() and int(valor_str) <= 50:
        return {'tipo': 'iva', 'valor': valor_str}
    
    # Medida específica
    patron_medida = re.compile(r'^\d+/\d+$|^\d+x\d+$|^\d+mm$|^\d+cm$|^\d+"$')
    if patron_medida.match(valor_str):
        return {'tipo': 'medida', 'valor': valor_str}
    
    # Descripción (texto útil)
    if 3 <= len(valor_str) <= 80:
        descripcion_limpia = re.sub(r'\s+', ' ', valor_str).strip()
        if descripcion_limpia and len(descripcion_limpia) >= 3:
            return {'tipo': 'descripcion', 'valor': descripcion_limpia}
    
    return None
def encontrar_columna(headers, posibles_nombres):
    """Encuentra la columna que coincide con los posibles nombres"""
    for i, header in enumerate(headers):
        header_lower = header.lower().strip()
        for nombre in posibles_nombres:
            if nombre.lower() in header_lower:
                return i
    return -1

def obtener_valor_columna(fila_datos, columna_index):
    """Obtiene el valor de una columna específica"""
    if columna_index >= 0 and columna_index < len(fila_datos):
        return fila_datos[columna_index]
    return ''

def main():
    """Función principal"""
    # Usar directorio actual o permitir especificar uno diferente
    import sys
    if len(sys.argv) > 1:
        directorio_base = sys.argv[1]
    else:
        directorio_base = os.path.dirname(os.path.abspath(__file__))
    
    print("=== EXTRACTOR DE DATOS - PLANILLA FERRETERÍA ===")
    print(f"Directorio: {directorio_base}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Detectar archivos HTML automáticamente
    html_files = detectar_archivos_html(directorio_base)
    
    if not html_files:
        print("❌ No se encontraron archivos HTML en el directorio")
        return
    
    print(f"📁 Archivos HTML detectados: {len(html_files)}")
    for file in html_files:
        print(f"   • {file}")
    print()
    
    # Determinar nombre de la planilla desde el directorio
    planilla_name = os.path.basename(directorio_base).replace('_archivos', '').replace('_files', '')
    if not planilla_name or planilla_name == '.':
        planilla_name = 'ANALISIS_HTML'
    
    # Estructura principal de datos
    datos_completos = {
        'planilla': planilla_name.upper(),
        'directorio': directorio_base,
        'fecha_extraccion': datetime.now().isoformat(),
        'total_hojas': len(html_files),
        'hojas': []
    }      # Procesar cada archivo HTML detectado
    for html_file in html_files:
        ruta_archivo = os.path.join(directorio_base, html_file)
        nombre_hoja = determinar_nombre_hoja(html_file)
        
        if os.path.exists(ruta_archivo):
            resultado = procesar_hoja(ruta_archivo, nombre_hoja)
            if resultado:
                datos_completos['hojas'].append(resultado)
        else:
            print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
    
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
    print(f"Planilla: {datos_completos['planilla']}")
    print(f"Archivo guardado en: {archivo_salida}")
    print(f"Directorio: {directorio_base}")
    print(f"Hojas procesadas: {len(datos_completos['hojas'])}")
    
    for hoja in datos_completos['hojas']:
        print(f"  {hoja['hoja']}: {hoja['total_tablas']} tabla(s)")
    
    print()
    print("✅ Procesamiento completado")
    
    # Retornar datos y ubicación del archivo
    return datos_completos, archivo_salida

if __name__ == "__main__":
    main()
