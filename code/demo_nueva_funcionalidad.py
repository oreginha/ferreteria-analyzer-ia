#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de demostración de las nuevas funcionalidades de detección inteligente de proveedores
"""

import os
import sys
import json
from datetime import datetime

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demostrar_analisis_yayi():
    """Demuestra el análisis inteligente en el directorio YAYI"""
    print("🔧 DEMOSTRACIÓN: Análisis Inteligente de Proveedores")
    print("=" * 60)
    print()
    
    # Importar el script mejorado
    import extraer_datos_mejorado
    
    # Directorio de YAYI
    yayi_dir = "d:\\Documentos y Archivos\\Excel\\YAYI FULL - 3 FEBRERO_archivos"
    
    print(f"📂 Analizando directorio: {yayi_dir}")
    print()
    
    # Cambiar directorio temporalmente
    original_dir = os.getcwd()
    try:
        os.chdir(yayi_dir)
        
        # Ejecutar análisis
        print("🔍 Ejecutando análisis inteligente...")
        extraer_datos_mejorado.main()
        
        print()
        print("📊 Resultados del análisis:")
        
        # Leer y mostrar los resultados
        if os.path.exists("datos_estructurados.json"):
            with open("datos_estructurados.json", 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            print(f"✅ Planilla: {datos['planilla']}")
            print(f"✅ Estrategia: {datos.get('estrategia_proveedores', 'No especificada')}")
            print(f"✅ Proveedor principal: {datos.get('proveedor_principal', 'No detectado')}")
            print(f"✅ Total hojas: {len(datos['hojas'])}")
            
            print("\n📋 Hojas procesadas:")
            for hoja in datos['hojas']:
                proveedores_info = ""
                if hoja.get('proveedores_detectados'):
                    top_proveedor = hoja['proveedores_detectados'][0]
                    proveedores_info = f" (confianza: {top_proveedor['confianza']:.2f})"
                print(f"  • {hoja['hoja']}: {hoja['total_tablas']} tabla(s){proveedores_info}")
        
    finally:
        os.chdir(original_dir)

def demostrar_analisis_multiple():
    """Demuestra el análisis en directorio con múltiples proveedores"""
    print("\n" + "=" * 60)
    print("🔧 DEMOSTRACIÓN: Múltiples Proveedores")
    print("=" * 60)
    print()
    
    # Directorio original
    ferreteria_dir = "d:\\Documentos y Archivos\\Excel\\PLANILLA FERRETERIA _archivos"
    
    print(f"📂 Analizando directorio: {ferreteria_dir}")
    print()
    
    # Importar el script mejorado
    import extraer_datos_mejorado
    
    # Cambiar directorio temporalmente
    original_dir = os.getcwd()
    try:
        os.chdir(ferreteria_dir)
        
        # Ejecutar análisis
        print("🔍 Ejecutando análisis inteligente...")
        extraer_datos_mejorado.main()
        
        print()
        print("📊 Resultados del análisis:")
        
        # Leer y mostrar los resultados
        if os.path.exists("datos_estructurados.json"):
            with open("datos_estructurados.json", 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            print(f"✅ Planilla: {datos['planilla']}")
            print(f"✅ Estrategia: {datos.get('estrategia_proveedores', 'No especificada')}")
            print(f"✅ Proveedor principal: {datos.get('proveedor_principal', 'No detectado')}")
            print(f"✅ Total hojas: {len(datos['hojas'])}")
            
            print("\n📋 Hojas procesadas:")
            for hoja in datos['hojas']:
                proveedores_info = ""
                if hoja.get('proveedores_detectados'):
                    top_proveedor = hoja['proveedores_detectados'][0]
                    proveedores_info = f" (detectado: {top_proveedor['nombre']}, confianza: {top_proveedor['confianza']:.2f})"
                print(f"  • {hoja['hoja']}: {hoja['total_tablas']} tabla(s){proveedores_info}")
        
    finally:
        os.chdir(original_dir)

def mostrar_comparacion():
    """Muestra una comparación de las estrategias"""
    print("\n" + "=" * 60)
    print("📊 COMPARACIÓN DE ESTRATEGIAS")
    print("=" * 60)
    print()
    
    print("🏪 CASO YAYI (Un solo proveedor):")
    print("   ✅ Detecta que todas las hojas pertenecen a YAYI")
    print("   ✅ Nomenclatura: YAYI_LISTA_01, YAYI_LISTA_02, etc.")
    print("   ✅ Estrategia: single_provider")
    print()
    
    print("🏪 CASO MÚLTIPLES PROVEEDORES:")
    print("   ✅ Detecta diferentes proveedores en cada hoja")
    print("   ✅ Nomenclatura: STANLEY, HERRAMETALSA, YAYI, etc.")
    print("   ✅ Estrategia: multiple_providers")
    print()
    
    print("🎯 BENEFICIOS:")
    print("   • Organización automática inteligente")
    print("   • Nombres descriptivos y coherentes")
    print("   • Adaptación automática al contenido")
    print("   • Mejor comprensión de la estructura de datos")

def main():
    """Función principal de demostración"""
    print(f"🚀 NUEVA FUNCIONALIDAD IMPLEMENTADA")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Demostrar con YAYI (un solo proveedor)
        demostrar_analisis_yayi()
        
        # Demostrar con múltiples proveedores
        demostrar_analisis_multiple()
        
        # Mostrar comparación
        mostrar_comparacion()
        
        print("\n" + "=" * 60)
        print("✅ DEMOSTRACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print("🎉 La nueva funcionalidad está lista para usar!")
        print("📱 Puedes probarla en la aplicación gráfica o usar el script mejorado directamente.")
        
    except Exception as e:
        print(f"❌ Error en la demostración: {str(e)}")

if __name__ == "__main__":
    main()
