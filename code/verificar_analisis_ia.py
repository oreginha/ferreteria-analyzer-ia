#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACIÓN DEL ANÁLISIS IA - ¿Usa análisis inteligente o básico?
================================================================
"""

import sys
import os

def verificar_que_analisis_usa_ia():
    """Verifica qué tipo de análisis está usando realmente la IA"""
    print("🔍 VERIFICANDO QUÉ ANÁLISIS USA LA IA")
    print("=" * 50)
    
    # Agregar al path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from ferreteria_analyzer_app import FerreteriaAnalyzerApp
        import tkinter as tk
        import json
        
        print("✅ Importación exitosa")
        
        # Crear instancia de prueba
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        
        app = FerreteriaAnalyzerApp(root)
        print("✅ Instancia creada")
        
        # Cargar datos si existen
        datos_file = "datos_extraidos_app.json"
        if os.path.exists(datos_file):
            with open(datos_file, 'r', encoding='utf-8') as f:
                app.current_data = json.load(f)
            print(f"✅ Datos cargados desde {datos_file}")
        else:
            print(f"❌ No se encontró {datos_file}")
            return False
        
        # Probar prepare_data_summary
        print("\n🧪 PROBANDO prepare_data_summary()...")
        resumen = app.prepare_data_summary()
        
        # Analizar el tipo de resumen
        print("\n📋 ANÁLISIS DEL RESUMEN GENERADO:")
        print("-" * 40)
        
        if "=== ANÁLISIS INTELIGENTE DE DATOS ESTRUCTURADOS ===" in resumen:
            print("✅ USANDO ANÁLISIS INTELIGENTE")
            print("   🧠 La IA recibe datos estructurados y organizados")
            print("   📊 Con proveedores, precios y relaciones identificadas")
        elif "PLANILLA:" in resumen and "ESTRATEGIA:" in resumen:
            print("⚠️  USANDO ANÁLISIS BÁSICO (FALLBACK)")
            print("   📄 La IA recibe datos básicos sin estructura inteligente")
            print("   💡 Revisar por qué falló el análisis inteligente")
        else:
            print("❓ TIPO DE ANÁLISIS DESCONOCIDO")
        
        # Mostrar muestra del resumen
        print(f"\n📄 MUESTRA DEL RESUMEN (primeras 10 líneas):")
        print("-" * 50)
        lineas = resumen.split('\n')[:10]
        for i, linea in enumerate(lineas, 1):
            print(f"{i:2d}. {linea}")
        
        if len(resumen.split('\n')) > 10:
            print("    ... (continúa)")
        
        # Verificar indicadores específicos de análisis inteligente
        print(f"\n🔍 INDICADORES DE ANÁLISIS INTELIGENTE:")
        print("-" * 45)
        
        indicadores = [
            ("=== PROVEEDORES IDENTIFICADOS ===", "Detección automática de proveedores"),
            ("=== ANÁLISIS DE PRECIOS ===", "Análisis estructurado de precios"),
            ("=== MUESTRA DE PRODUCTOS ANALIZADOS ===", "Productos clasificados"),
            ("=== ESTADÍSTICAS DE CALIDAD ===", "Métricas de calidad automáticas"),
            ("=== RECOMENDACIONES ===", "Recomendaciones inteligentes"),
            ("Monedas detectadas:", "Detección de monedas"),
            ("Total precios encontrados:", "Conteo automático de precios")
        ]
        
        presentes = 0
        for indicador, descripcion in indicadores:
            if indicador in resumen:
                print(f"✅ {descripcion}")
                presentes += 1
            else:
                print(f"❌ {descripcion}")
        
        print(f"\n📊 RESULTADO:")
        print(f"   Indicadores presentes: {presentes}/{len(indicadores)}")
        if presentes >= 5:
            print("   🎉 LA IA ESTÁ USANDO ANÁLISIS INTELIGENTE")
        elif presentes >= 2:
            print("   ⚠️  LA IA ESTÁ USANDO ANÁLISIS PARCIALMENTE INTELIGENTE")
        else:
            print("   ❌ LA IA ESTÁ USANDO ANÁLISIS BÁSICO")
        
        root.destroy()
        return presentes >= 5
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def mostrar_solucion_si_es_necesario():
    """Muestra la solución si se detecta que no está usando análisis inteligente"""
    print("\n🔧 POSIBLES SOLUCIONES SI NO USA ANÁLISIS INTELIGENTE:")
    print("-" * 55)
    print("""
    1. 📁 VERIFICAR ARCHIVOS:
       • Asegurar que analizador_datos_inteligente.py existe
       • Verificar que datos_extraidos_app.json tiene datos válidos
    
    2. 🐛 DEPURAR ERRORES:
       • Revisar logs de errores en prepare_data_summary()
       • Verificar que la importación de AnalizadorDatosInteligente funciona
    
    3. 🔄 FORZAR ANÁLISIS INTELIGENTE:
       • Modificar prepare_data_summary() para mostrar errores
       • Agregar logs de depuración detallados
    
    4. ✅ VALIDAR FUNCIONAMIENTO:
       • Ejecutar demo_analisis_inteligente.py
       • Verificar que el analizador funciona independientemente
    """)

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN: ¿QUÉ ANÁLISIS USA REALMENTE LA IA?")
    print("=" * 60)
    
    usa_inteligente = verificar_que_analisis_usa_ia()
    
    if not usa_inteligente:
        mostrar_solucion_si_es_necesario()
    else:
        print("\n🎉 CONCLUSIÓN:")
        print("✅ La IA está usando correctamente el análisis inteligente")
        print("✅ Los datos estructurados se envían correctamente")
        print("✅ El sistema funciona como se esperaba")

if __name__ == "__main__":
    main()
