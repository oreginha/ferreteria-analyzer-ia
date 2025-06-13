#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar un resumen legible de los datos extraídos de la planilla de ferretería
"""

import json
import os
from datetime import datetime

def crear_resumen_hoja(hoja_datos):
    """Crea un resumen de una hoja específica"""
    resumen = {
        'nombre': hoja_datos['hoja'],
        'archivo': hoja_datos['archivo'],
        'total_tablas': hoja_datos['total_tablas'],
        'tablas': []
    }
    
    for tabla in hoja_datos['tablas']:
        # Obtener encabezados (primera fila con contenido)
        encabezados = []
        datos_muestra = []
        
        if tabla['filas']:
            # Buscar la fila de encabezados
            for i, fila in enumerate(tabla['filas'][:10]):  # Revisar primeras 10 filas
                if len([celda for celda in fila if celda.strip()]) >= 3:  # Al menos 3 celdas con contenido
                    if any(keyword in ' '.join(fila).upper() for keyword in ['NUMERO', 'DESCRIP', 'PRECIO', 'CODIGO', 'PRODUCTO', 'ARTICULO']):
                        encabezados = fila
                        datos_muestra = tabla['filas'][i+1:i+6]  # Primeras 5 filas de datos
                        break
            
            # Si no encontró encabezados específicos, usar la primera fila con más contenido
            if not encabezados and tabla['filas']:
                encabezados = tabla['filas'][0]
                datos_muestra = tabla['filas'][1:6] if len(tabla['filas']) > 1 else []
        
        tabla_resumen = {
            'indice': tabla['tabla_indice'],
            'dimensiones': f"{tabla['total_filas']} filas x {tabla['total_columnas']} columnas",
            'encabezados': encabezados[:10],  # Máximo 10 columnas para legibilidad
            'muestra_datos': datos_muestra
        }
        
        resumen['tablas'].append(tabla_resumen)
    
    return resumen

def generar_resumen_completo():
    """Genera el resumen completo de todos los datos"""
    
    archivo_datos = r'd:\Documentos y Archivos\Excel\PLANILLA FERRETERIA _archivos\datos_estructurados.json'
    
    print("=== RESUMEN DE DATOS EXTRAÍDOS - PLANILLA FERRETERÍA ===")
    print(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"📄 Planilla: {datos['planilla']}")
        print(f"📅 Fecha de extracción: {datos['fecha_extraccion']}")
        print(f"📊 Total de hojas procesadas: {datos['total_hojas']}")
        print()
        
        resumen_completo = {
            'metadata': {
                'planilla': datos['planilla'],
                'fecha_extraccion': datos['fecha_extraccion'],
                'fecha_analisis': datetime.now().isoformat(),
                'total_hojas': datos['total_hojas']
            },
            'hojas': []
        }
        
        total_registros = 0
        
        for hoja_datos in datos['hojas']:
            print(f"🏪 HOJA: {hoja_datos['hoja']}")
            print(f"   📁 Archivo: {hoja_datos['archivo']}")
            print(f"   📋 Tablas encontradas: {hoja_datos['total_tablas']}")
            
            hoja_resumen = crear_resumen_hoja(hoja_datos)
            resumen_completo['hojas'].append(hoja_resumen)
            
            for i, tabla in enumerate(hoja_datos['tablas']):
                print(f"   📊 Tabla {i}: {tabla['total_filas']} filas x {tabla['total_columnas']} columnas")
                total_registros += tabla['total_filas']
                
                # Mostrar encabezados si los hay
                if tabla['filas'] and len(tabla['filas']) > 0:
                    primera_fila = tabla['filas'][0]
                    # Mostrar solo si parece ser encabezados
                    if any(keyword in ' '.join(primera_fila).upper() for keyword in ['NUMERO', 'DESCRIP', 'PRECIO', 'CODIGO', 'PRODUCTO', 'ARTICULO']):
                        print(f"      🏷️  Encabezados: {primera_fila[:5]}")  # Primeros 5 para legibilidad
                
                print()
            
            print("-" * 60)
            print()
        
        print(f"📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total de registros aproximados: {total_registros:,}")
        print(f"   • Hojas con datos: {len([h for h in datos['hojas'] if h['total_tablas'] > 0])}")
        print(f"   • Hojas vacías: {len([h for h in datos['hojas'] if h['total_tablas'] == 0])}")
        
        # Guardar resumen
        archivo_resumen = r'd:\Documentos y Archivos\Excel\PLANILLA FERRETERIA _archivos\resumen_datos.json'
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            json.dump(resumen_completo, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resumen guardado en: {archivo_resumen}")
        
        return resumen_completo
        
    except Exception as e:
        print(f"❌ Error al procesar los datos: {str(e)}")
        return None

def mostrar_muestra_datos():
    """Muestra una muestra de los datos de cada hoja principal"""
    
    archivo_resumen = r'd:\Documentos y Archivos\Excel\PLANILLA FERRETERIA _archivos\resumen_datos.json'
    
    try:
        with open(archivo_resumen, 'r', encoding='utf-8') as f:
            resumen = json.load(f)
        
        print("\n" + "="*80)
        print("🔍 MUESTRA DE DATOS POR HOJA")
        print("="*80)
        
        for hoja in resumen['hojas']:
            if hoja['total_tablas'] > 0:
                print(f"\n🏪 {hoja['nombre']}:")
                
                tabla_principal = hoja['tablas'][0]  # Tabla principal (la más grande)
                
                if tabla_principal['encabezados']:
                    print("   📋 Columnas:")
                    for i, col in enumerate(tabla_principal['encabezados'][:8]):
                        if col.strip():
                            print(f"      {i+1}. {col}")
                
                if tabla_principal['muestra_datos']:
                    print("   📊 Muestra de datos:")
                    for i, fila in enumerate(tabla_principal['muestra_datos'][:3]):
                        fila_limpia = [celda[:30] + "..." if len(celda) > 30 else celda for celda in fila[:5]]
                        print(f"      Fila {i+1}: {fila_limpia}")
                
                print(f"   📏 Dimensiones: {tabla_principal['dimensiones']}")
                print()
        
    except Exception as e:
        print(f"❌ Error al mostrar muestra: {str(e)}")

if __name__ == "__main__":
    resumen = generar_resumen_completo()
    
    if resumen:
        mostrar_muestra_datos()
        
        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*80)
        print("\nArchivos generados:")
        print("   📄 datos_estructurados.json - Datos completos extraídos")
        print("   📋 resumen_datos.json - Resumen estructurado")
        print("\n🎯 Los datos están listos para su análisis y procesamiento.")
