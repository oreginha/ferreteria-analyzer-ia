#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERCEPTOR DE PROMPT PARA IA
==============================
Muestra exactamente qué datos recibe la IA
"""

import sys
import os

def interceptar_prompt_ia():
    """Intercepta y muestra el prompt exacto que recibe la IA"""
    print("🎯 INTERCEPTANDO PROMPT PARA IA")
    print("=" * 40)
    
    # Agregar al path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from ferreteria_analyzer_app import FerreteriaAnalyzerApp
        import tkinter as tk
        import json
        
        # Crear instancia
        root = tk.Tk()
        root.withdraw()
        app = FerreteriaAnalyzerApp(root)
        
        # Cargar datos
        datos_file = "datos_extraidos_app.json"
        if os.path.exists(datos_file):
            with open(datos_file, 'r', encoding='utf-8') as f:
                app.current_data = json.load(f)
            print(f"✅ Datos cargados desde {datos_file}")
        else:
            print(f"❌ No se encontró {datos_file}")
            return
        
        # Obtener el resumen que se envía a la IA
        print("\n🔍 OBTENIENDO RESUMEN PARA IA...")
        resumen = app.prepare_data_summary()
        
        # Crear el prompt completo como lo hace analyze_with_ai()
        prompt_completo = f"""
Analiza los siguientes datos de una planilla de ferretería y proporciona insights valiosos:

{resumen}

Por favor proporciona:
1. Análisis de tendencias de precios
2. Identificación de productos más costosos y económicos por categoría
3. Análisis de la diversidad de productos por proveedor
4. Recomendaciones de negocio
5. Detección de posibles oportunidades o inconsistencias
6. Análisis de actualización de listas de precios

Responde en español de manera clara y estructurada.
"""
        
        # Guardar el prompt completo
        with open("prompt_interceptado_ia.txt", 'w', encoding='utf-8') as f:
            f.write(prompt_completo)
        
        print("✅ Prompt interceptado y guardado en 'prompt_interceptado_ia.txt'")
        
        # Análisis del contenido
        print(f"\n📊 ANÁLISIS DEL PROMPT:")
        print("-" * 30)
        
        lineas = prompt_completo.split('\n')
        total_lineas = len(lineas)
        tamano_kb = len(prompt_completo.encode('utf-8')) // 1024
        
        print(f"📏 Tamaño: {tamano_kb} KB")
        print(f"📄 Líneas: {total_lineas}")
        
        # Buscar indicadores de tipo de datos
        if "=== ANÁLISIS INTELIGENTE DE DATOS ESTRUCTURADOS ===" in prompt_completo:
            print("✅ CONFIRMADO: Envía análisis inteligente estructurado")
        elif "PLANILLA:" in prompt_completo and "TOTAL HOJAS:" in prompt_completo:
            print("⚠️  DETECTADO: Envía análisis básico")
        
        # Conteo de elementos estructurados
        indicadores = {
            "proveedores": prompt_completo.count("=== PROVEEDORES IDENTIFICADOS ==="),
            "precios": prompt_completo.count("=== ANÁLISIS DE PRECIOS ==="),
            "productos": prompt_completo.count("=== MUESTRA DE PRODUCTOS ANALIZADOS ==="),
            "estadisticas": prompt_completo.count("=== ESTADÍSTICAS DE CALIDAD ==="),
            "recomendaciones": prompt_completo.count("=== RECOMENDACIONES ===")
        }
        
        print("\n🏷️  SECCIONES ESTRUCTURADAS DETECTADAS:")
        for seccion, cantidad in indicadores.items():
            if cantidad > 0:
                print(f"✅ {seccion.upper()}: {cantidad} sección(es)")
            else:
                print(f"❌ {seccion.upper()}: No encontrado")
        
        # Muestra del contenido
        print(f"\n📖 MUESTRA DEL PROMPT (primeras 20 líneas):")
        print("-" * 50)
        for i, linea in enumerate(lineas[:20], 1):
            print(f"{i:2d}. {linea}")
        
        if total_lineas > 20:
            print(f"    ... (+{total_lineas-20} líneas más)")
        
        # Verificar presencia de datos crudos vs estructurados
        print(f"\n🔍 VERIFICACIÓN DE TIPO DE DATOS:")
        print("-" * 35)
        
        if "6,494" in prompt_completo and "CRIMARAL" in prompt_completo:
            print("✅ Contiene datos de proveedores estructurados")
        if "69551" in prompt_completo or "69,551" in prompt_completo:
            print("✅ Contiene análisis de precios automático")
        if "30,439" in prompt_completo or "30439" in prompt_completo:
            print("✅ Contiene estadísticas de registros totales")
        if "USD, ARS" in prompt_completo:
            print("✅ Contiene detección automática de monedas")
        
        # Buscar datos crudos de tablas
        if "sheet001" in prompt_completo.lower() or "tabla" in prompt_completo.lower():
            print("⚠️  POSIBLE: Contiene referencias a datos crudos")
        
        root.destroy()
        
        print(f"\n🎯 CONCLUSIÓN:")
        if sum(indicadores.values()) >= 4:
            print("✅ La IA recibe DATOS ESTRUCTURADOS INTELIGENTES")
            print("✅ No son datos crudos de planilla")
        else:
            print("❌ La IA puede estar recibiendo datos básicos")
        
        print(f"\n💡 REVISAR: prompt_interceptado_ia.txt para ver contenido completo")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    interceptar_prompt_ia()
