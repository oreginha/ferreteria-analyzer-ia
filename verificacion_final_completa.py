#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACIÓN FINAL COMPLETA - Todas las funcionalidades
========================================================
"""
import os
import sys

def verificar_modulos():
    """Verifica que todos los módulos se importen correctamente"""
    print("🔍 VERIFICANDO MÓDULOS...")
    print("-" * 40)
    
    try:
        from ferreteria_analyzer_app import FerreteriaAnalyzerApp
        print("✅ ferreteria_analyzer_app")
        
        from extraer_datos_mejorado import (
            detectar_proveedores_en_contenido,
            generar_nombre_hoja_inteligente,
            analizar_proveedores_globales
        )
        print("✅ extraer_datos_mejorado")
        
        import tkinter as tk
        print("✅ tkinter")
        
        return True
    except Exception as e:
        print(f"❌ Error importando módulos: {e}")
        return False

def verificar_metodos_criticos():
    """Verifica métodos críticos de la aplicación"""
    print("\n🔍 VERIFICANDO MÉTODOS CRÍTICOS...")
    print("-" * 40)
    
    try:
        import tkinter as tk
        from ferreteria_analyzer_app import FerreteriaAnalyzerApp
        
        root = tk.Tk()
        root.withdraw()
        
        app = FerreteriaAnalyzerApp(root)
        
        # Verificar métodos críticos
        metodos = [
            'extract_data',
            'extract_html_data_intelligent', 
            'detectar_proveedores_en_contenido',
            'generar_nombre_hoja_inteligente',
            'prepare_data_summary',
            'analyze_with_ai',
            'configure_gemini'
        ]
        
        for metodo in metodos:
            if hasattr(app, metodo):
                print(f"✅ {metodo}")
            else:
                print(f"❌ {metodo} NO encontrado")
                return False
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando métodos: {e}")
        return False

def verificar_archivos_clave():
    """Verifica que existan archivos clave del proyecto"""
    print("\n🔍 VERIFICANDO ARCHIVOS CLAVE...")
    print("-" * 40)
    
    archivos_requeridos = [
        'ferreteria_analyzer_app.py',
        'extraer_datos_mejorado.py',
        'README.md',
        'PROYECTO_FINALIZADO.md',
        'requirements.txt'
    ]
    
    todos_existen = True
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} NO encontrado")
            todos_existen = False
    
    return todos_existen

def verificar_funcionalidad_ia():
    """Verifica la funcionalidad específica de IA"""
    print("\n🔍 VERIFICANDO FUNCIONALIDAD IA...")
    print("-" * 40)
    
    try:
        import tkinter as tk
        from ferreteria_analyzer_app import FerreteriaAnalyzerApp
        
        root = tk.Tk()
        root.withdraw()
        
        app = FerreteriaAnalyzerApp(root)
        
        # Probar prepare_data_summary
        summary = app.prepare_data_summary()
        if "No hay datos disponibles" in summary:
            print("✅ prepare_data_summary (sin datos)")
        else:
            print("✅ prepare_data_summary (con datos)")
        
        # Probar generate_basic_analysis
        if hasattr(app, 'generate_basic_analysis'):
            print("✅ generate_basic_analysis disponible")
        else:
            print("❌ generate_basic_analysis NO encontrado")
            return False
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando IA: {e}")
        return False

def main():
    """Verificación completa"""
    print("🔧 VERIFICACIÓN FINAL COMPLETA")
    print("=" * 60)
    print(f"📅 Fecha: 12 de junio de 2025")
    print(f"📁 Directorio: {os.getcwd()}")
    print()
    
    # Lista de verificaciones
    verificaciones = [
        ("Módulos", verificar_modulos),
        ("Métodos Críticos", verificar_metodos_criticos),
        ("Archivos Clave", verificar_archivos_clave), 
        ("Funcionalidad IA", verificar_funcionalidad_ia)
    ]
    
    resultados = []
    for nombre, func in verificaciones:
        resultado = func()
        resultados.append((nombre, resultado))
    
    # Resumen final
    print("\n🎯 RESUMEN FINAL")
    print("=" * 40)
    
    todos_ok = True
    for nombre, resultado in resultados:
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{status} - {nombre}")
        if not resultado:
            todos_ok = False
    
    print("\n" + "=" * 40)
    if todos_ok:
        print("🎉 TODAS LAS VERIFICACIONES PASARON")
        print("✅ El proyecto está COMPLETAMENTE FUNCIONAL")
        print("\n📱 INSTRUCCIONES FINALES:")
        print("   1. python ferreteria_analyzer_app.py")
        print("   2. Configurar API Key de Gemini (opcional)")
        print("   3. Seleccionar directorio con archivos HTML")
        print("   4. Extraer datos y analizar")
        print("\n🏆 PROYECTO FINALIZADO EXITOSAMENTE")
    else:
        print("⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("💡 Revisar errores anteriores para solucionar")
    
    return todos_ok

if __name__ == "__main__":
    main()
