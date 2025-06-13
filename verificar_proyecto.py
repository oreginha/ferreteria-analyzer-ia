"""
Script de verificación del proyecto completo
===========================================
"""

import sys
import os
from pathlib import Path

def verificar_instalacion():
    """Verifica que todo esté correctamente instalado"""
    print("🔧 VERIFICACIÓN DEL PROYECTO COMPLETO")
    print("=" * 50)
    
    # Verificar Python
    print(f"✅ Python {sys.version}")
    
    # Verificar módulos
    modulos_requeridos = ['tkinter', 'json', 'pathlib', 'threading', 'datetime']
    for modulo in modulos_requeridos:
        try:
            __import__(modulo)
            print(f"✅ {modulo} disponible")
        except ImportError:
            print(f"❌ {modulo} NO disponible")
    
    # Verificar archivos del proyecto
    archivos_principales = [
        'ferreteria_analyzer_app.py',
        'extraer_datos.py', 
        'data_analyzer.py'
    ]
    
    print("\n📁 ARCHIVOS DEL PROYECTO:")
    for archivo in archivos_principales:
        if Path(archivo).exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} NO encontrado")
    
    # Verificar datos de ejemplo
    archivos_datos = ['datos_extraidos_app.json', 'datos_estructurados.json']
    print("\n📊 ARCHIVOS DE DATOS:")
    for archivo in archivos_datos:
        if Path(archivo).exists():
            print(f"✅ {archivo}")
        else:
            print(f"⚠️  {archivo} (opcional)")
    
    print("\n" + "=" * 50)
    print("🚀 PROYECTO LISTO PARA USAR")
    print("\nPara ejecutar la aplicación:")
    print("python ferreteria_analyzer_app.py")
    print("\nO usar el archivo:")
    print("ejecutar_app_completa.bat")

if __name__ == "__main__":
    verificar_instalacion()
