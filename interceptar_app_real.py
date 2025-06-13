#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERCEPTOR DE PROMPT IA - MÉTODO REAL
=====================================
Intercepta exactamente qué está enviando la aplicación real a la IA
"""

import os
import json

def interceptar_llamada_real():
    """Intercepta la llamada real del método analyze_with_ai"""
    print("🕵️ INTERCEPTANDO LLAMADA REAL A LA IA")
    print("=" * 50)
    
    # Verificar si existe el archivo de datos
    archivo_datos = "datos_extraidos_app.json"
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        return
    
    # Simular crear una app con datos reales
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana
    
    from ferreteria_analyzer_app import FerreteriaAnalyzerApp
    
    # Crear app real
    app = FerreteriaAnalyzerApp(root)
    
    # Cargar datos reales
    with open(archivo_datos, 'r', encoding='utf-8') as f:
        app.current_data = json.load(f)
    
    print(f"✅ App creada con {len(app.current_data.get('hojas', []))} hojas")
    
    # Obtener el resumen que iría a la IA
    print("\n🧠 OBTENIENDO RESUMEN REAL PARA IA...")
    try:
        resumen_real = app.prepare_data_summary()
        
        # Guardar para inspección
        with open("resumen_real_app_ia.txt", 'w', encoding='utf-8') as f:
            f.write(resumen_real)
        
        print("✅ Resumen real guardado en 'resumen_real_app_ia.txt'")
        
        # Mostrar estadísticas
        print(f"\n📊 ESTADÍSTICAS DEL RESUMEN REAL:")
        print(f"   • Total líneas: {len(resumen_real.split())}")
        print(f"   • Total caracteres: {len(resumen_real):,}")
        print(f"   • Tamaño: {len(resumen_real.encode('utf-8')) / 1024:.1f} KB")
        
        # Verificar contenido
        verificar_contenido(resumen_real)
        
        # Simular envío a IA (solo mostrar primeras líneas)
        print(f"\n📄 PRIMERAS LÍNEAS QUE VE LA IA:")
        print("-" * 40)
        lineas = resumen_real.split('\n')[:20]
        for i, linea in enumerate(lineas, 1):
            print(f"{i:2d}. {linea}")
        
        print(f"\n💡 REVISA EL ARCHIVO COMPLETO: resumen_real_app_ia.txt")
        
    except Exception as e:
        print(f"❌ Error al obtener resumen: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()

def verificar_contenido(resumen):
    """Verifica el contenido del resumen"""
    print(f"\n🔍 ANÁLISIS DE CONTENIDO:")
    print("-" * 30)
    
    # Palabras clave del análisis inteligente
    palabras_inteligentes = [
        "ANÁLISIS INTELIGENTE",
        "REESTRUCTURACIÓN", 
        "DATOS REESTRUCTURADOS",
        "CÓDIGO",
        "PRECIO",
        "MARCA",
        "PROVEEDOR"
    ]
    
    # Palabras clave de datos básicos/crudos
    palabras_basicas = [
        "ANÁLISIS BÁSICO",
        "SIN IA",
        "FALLBACK",
        "MÉTODO BÁSICO"
    ]
    
    # Contar menciones
    menciones_inteligentes = 0
    menciones_basicas = 0
    
    for palabra in palabras_inteligentes:
        count = resumen.upper().count(palabra)
        if count > 0:
            menciones_inteligentes += count
            print(f"   ✅ {palabra}: {count}")
    
    for palabra in palabras_basicas:
        count = resumen.upper().count(palabra)
        if count > 0:
            menciones_basicas += count
            print(f"   ❌ {palabra}: {count}")
    
    print(f"\n⚖️ BALANCE:")
    print(f"   • Menciones inteligentes: {menciones_inteligentes}")
    print(f"   • Menciones básicas: {menciones_basicas}")
    
    if menciones_inteligentes > menciones_basicas:
        print("   ✅ LA APP ESTÁ USANDO ANÁLISIS INTELIGENTE")
    else:
        print("   ❌ LA APP ESTÁ USANDO ANÁLISIS BÁSICO")
    
    # Verificar estructura específica
    if "=== ANÁLISIS INTELIGENTE CON REESTRUCTURACIÓN" in resumen:
        print("   ✅ ESTRUCTURA DE REESTRUCTURACIÓN DETECTADA")
    else:
        print("   ❌ NO SE DETECTÓ ESTRUCTURA DE REESTRUCTURACIÓN")

if __name__ == "__main__":
    interceptar_llamada_real()
