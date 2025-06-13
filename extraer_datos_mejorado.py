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
    """Extrae datos de las tablas en el HTML"""
    tablas = soup.find_all('table')
    datos_extraidos = []
    
    for i, tabla in enumerate(tablas):
        filas = tabla.find_all('tr')
        if not filas:
            continue
            
        datos_tabla = []
        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            fila_datos = []
            
            for celda in celdas:
                texto = limpiar_texto(celda.get_text())
                fila_datos.append(texto)
            
            # Solo agregar filas que tengan contenido significativo
            if any(celda.strip() for celda in fila_datos if celda):
                datos_tabla.append(fila_datos)
        
        if datos_tabla:
            datos_extraidos.append({
                'tabla_indice': i,
                'filas': datos_tabla,
                'total_filas': len(datos_tabla),
                'total_columnas': max(len(fila) for fila in datos_tabla) if datos_tabla else 0
            })
    
    return datos_extraidos

def detectar_proveedores_en_contenido(ruta_archivo):
    """Detecta todos los posibles nombres de proveedores en el contenido"""
    proveedores_encontrados = []
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
            contenido = archivo.read()
        
        soup = BeautifulSoup(contenido, 'html.parser')
        
        # Lista de proveedores conocidos (expandible)
        proveedores_conocidos = [
            'CRIMARAL', 'ANCAIG', 'DAFYS', 'HERRAMETAL', 'YAYI', 
            'DIST_CITY_BELL', 'BABUSI', 'FERRIPLAST', 'FERRETERIA',
            'DISTCITYBELL', 'CITY_BELL', 'DISTRIBUIDORA',
            'BRIMAX', 'PUMA', 'ROTAFLEX', 'STANLEY', 'BLACK_DECKER'
        ]
        
        # Buscar en todo el texto
        texto_completo = soup.get_text().upper()
        
        for proveedor in proveedores_conocidos:
            # Buscar el proveedor en el texto
            if proveedor in texto_completo:
                # Contar las ocurrencias para determinar relevancia
                ocurrencias = texto_completo.count(proveedor)
                proveedores_encontrados.append({
                    'nombre': proveedor,
                    'ocurrencias': ocurrencias,
                    'confianza': min(ocurrencias / 10, 1.0)  # Normalizar confianza
                })
        
        # Buscar también en emails y direcciones web
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', texto_completo)
        for email in emails:
            # Extraer nombre del dominio como posible proveedor
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
        print(f"Error analizando {ruta_archivo}: {str(e)}")
        return []

def analizar_proveedores_globales(directorio, archivos_html):
    """Analiza todos los archivos para determinar la estrategia de nomenclatura"""
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
    """Procesa una hoja individual"""
    try:
        print(f"Procesando {nombre_hoja}...")
        
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
            contenido = archivo.read()
        
        soup = BeautifulSoup(contenido, 'html.parser')
        
        # Extraer datos de las tablas
        datos_tablas = extraer_datos_tabla(soup)
        
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

def main():
    """Función principal"""
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
    html_files = detectar_archivos_html(directorio_base)
    
    if not html_files:
        print("❌ No se encontraron archivos HTML en el directorio")
        return
    
    print(f"📁 Archivos HTML detectados: {len(html_files)}")
    for file in html_files:
        print(f"   • {file}")
    print()
    
    # Análisis global de proveedores
    analisis_proveedores, proveedor_principal, estrategia = analizar_proveedores_globales(directorio_base, html_files)
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
        'estrategia_proveedores': estrategia,
        'proveedor_principal': proveedor_principal,
        'analisis_proveedores': analisis_proveedores,
        'hojas': []
    }
    
    # Procesar cada archivo HTML detectado
    print("📝 Procesando archivos:")
    for i, html_file in enumerate(html_files):
        ruta_archivo = os.path.join(directorio_base, html_file)
        proveedores_archivo = analisis_proveedores.get(html_file, [])
        
        nombre_hoja = generar_nombre_hoja_inteligente(
            html_file, i, estrategia, proveedor_principal, proveedores_archivo
        )
        
        if os.path.exists(ruta_archivo):
            resultado = procesar_hoja(ruta_archivo, nombre_hoja)
            if resultado:
                # Agregar información del análisis de proveedores
                resultado['proveedores_detectados'] = proveedores_archivo
                datos_completos['hojas'].append(resultado)
        else:
            print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
    
    # Guardar resultados
    archivo_salida = os.path.join(directorio_base, 'datos_estructurados.json')
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(datos_completos, f, ensure_ascii=False, indent=2)
    
    print()
    print("=== RESUMEN FINAL ===")
    print(f"Planilla: {datos_completos['planilla']}")
    print(f"Directorio: {directorio_base}")
    print(f"Estrategia: {estrategia}")
    if proveedor_principal:
        print(f"Proveedor principal: {proveedor_principal}")
    print(f"Hojas procesadas: {len(datos_completos['hojas'])}")
    print(f"Archivo de salida: {archivo_salida}")
    
    print("\n📋 Hojas generadas:")
    for hoja in datos_completos['hojas']:
        proveedores_info = ""
        if hoja.get('proveedores_detectados'):
            top_proveedor = hoja['proveedores_detectados'][0]
            proveedores_info = f" (detectado: {top_proveedor['nombre']}, confianza: {top_proveedor['confianza']:.2f})"
        print(f"  • {hoja['hoja']}: {hoja['total_tablas']} tabla(s){proveedores_info}")
    
    print()
    print("✅ Procesamiento completado con análisis inteligente de proveedores")

if __name__ == "__main__":
    main()
