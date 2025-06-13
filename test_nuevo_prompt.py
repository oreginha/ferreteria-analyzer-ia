#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba del nuevo prompt mejorado
Verifica que la IA ahora se enfoque en calidad de datos vs. comparaciones entre proveedores
"""

import os
import sys
import json

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simular_nuevo_prompt():
    """Simula el nuevo prompt mejorado"""
    print("🧪 PRUEBA DEL NUEVO PROMPT MEJORADO")
    print("=" * 60)
    
    # Simular datos de proveedores
    proveedores_simulados = ["CRIMARAL", "HERRAMETAL", "YAYI", "FERRIPLAST", "ANCAIG"]
    
    # Crear lista de proveedores
    lista_proveedores = "PROVEEDORES INCLUIDOS EN ESTE ANÁLISIS:\n"
    for i, prov in enumerate(proveedores_simulados, 1):
        lista_proveedores += f"{i}. {prov}\n"
    lista_proveedores += f"TOTAL: {len(proveedores_simulados)} PROVEEDORES\n\n"
    
    # Simular resumen de datos
    resumen_simulado = """=== ANÁLISIS INTELIGENTE CON REESTRUCTURACIÓN DE DATOS ===
PLANILLA: FERRETERIA
TOTAL REGISTROS ORIGINALES: 30,439
TOTAL PRODUCTOS REESTRUCTURADOS: 30,433
EFICIENCIA DE REESTRUCTURACIÓN: 100.0%

=== PROVEEDORES CON DATOS REESTRUCTURADOS ===
CRIMARAL:
  • Productos reestructurados: 6,493
  • Con precio detectado: 6,491 (100.0%)
  • Con código identificado: 2,653 (40.9%)

HERRAMETAL:
  • Productos reestructurados: 7,747
  • Con precio detectado: 7,745 (100.0%)
  • Con código identificado: 3,105 (40.1%)

YAYI:
  • Productos reestructurados: 7,541
  • Con precio detectado: 7,539 (100.0%)
  • Con código identificado: 2,261 (30.0%)

FERRIPLAST:
  • Productos reestructurados: 5,858
  • Con precio detectado: 5,856 (100.0%)
  • Con código identificado: 2,343 (40.0%)"""
    
    # Crear el nuevo prompt
    nuevo_prompt = f"""
                ANÁLISIS DE DATOS ESTRUCTURADOS DE FERRETERÍA

                {lista_proveedores}DATOS PROCESADOS E INTELIGENTEMENTE ORGANIZADOS:
                Los siguientes datos han sido limpiados, reestructurados y organizados automáticamente 
                para facilitar el análisis de calidad, estructura y oportunidades de mejora:

                {resumen_simulado}

                🎯 OBJETIVO DEL ANÁLISIS:
                Evaluar la calidad, estructura y organización de estos datos procesados,
                identificando patrones, oportunidades de mejora y insights de valor para el negocio.

                📋 ANÁLISIS SOLICITADO:

                1. **📊 EVALUACIÓN DE CALIDAD DE DATOS:**
                   - Revisar la completitud de información por proveedor
                   - Evaluar la consistencia en formatos de precios y códigos
                   - Identificar datos faltantes y áreas de mejora

                2. **💰 ANÁLISIS DE PRECIOS Y MONEDAS:**
                   - Detectar patrones en las estructuras de precios
                   - Analizar la diversidad de monedas utilizadas
                   - Identificar oportunidades de estandarización

                3. **🔍 INSIGHTS DE ORGANIZACIÓN:**
                   - Evaluar cómo están organizados los productos por categorías
                   - Identificar patrones en la nomenclatura y códigos
                   - Sugerir mejoras en la estructura de datos

                4. **💡 RECOMENDACIONES DE NEGOCIO:**
                   - Oportunidades basadas en los datos disponibles
                   - Estrategias para mejorar la calidad de la información
                   - Sugerencias para optimizar la gestión de inventario

                5. **📈 OPTIMIZACIÓN DE PROCESOS:**
                   - Identificar redundancias o inconsistencias
                   - Proponer mejoras en la organización de listas
                   - Recomendar estándares para futuras actualizaciones

                🎯 ENFOQUE: Analiza la información como un consultor de datos que busca optimizar 
                la organización, calidad y utilidad de estos datos para toma de decisiones comerciales.

                Proporciona análisis constructivo y práctico en español, enfocado en valor de negocio.
                """
    
    print("📝 NUEVO PROMPT GENERADO:")
    print("-" * 60)
    print(nuevo_prompt)
    
    # Guardar el prompt para revisión
    with open("nuevo_prompt_prueba.txt", "w", encoding="utf-8") as f:
        f.write(nuevo_prompt)
    
    print("\n✅ Prompt guardado en 'nuevo_prompt_prueba.txt'")
    print("\n🔍 DIFERENCIAS CLAVE DEL NUEVO PROMPT:")
    print("─" * 40)
    print("✅ ANTES: Enfoque en 'análisis comparativo entre proveedores'")
    print("✅ AHORA: Enfoque en 'calidad y estructura de datos'")
    print()
    print("✅ ANTES: 'Ranking de proveedores por diversidad'")
    print("✅ AHORA: 'Evaluación de completitud de información'")
    print()
    print("✅ ANTES: '⚠️ VALIDACIÓN: confirma que ves X proveedores'")
    print("✅ AHORA: 'Analiza como consultor de datos para optimizar'")
    print()
    print("✅ ANTES: Forzaba comparación ('NO analices solo un proveedor')")
    print("✅ AHORA: Se enfoca en valor de negocio independiente del número")

def comparar_prompts():
    """Compara el prompt anterior vs el nuevo"""
    print("\n" + "=" * 60)
    print("📊 COMPARACIÓN DE PROMPTS")
    print("=" * 60)
    
    print("\n🔴 PROBLEMA CON EL PROMPT ANTERIOR:")
    print("─" * 40)
    print("• La IA priorizaba 'análisis comparativo entre proveedores'")
    print("• Cuando había pocos proveedores, decía 'no se puede comparar'")
    print("• Se enfocaba en ranking y competencia entre proveedores")
    print("• Ignoraba el valor individual de los datos por proveedor")
    
    print("\n🟢 SOLUCIÓN CON EL NUEVO PROMPT:")
    print("─" * 40)
    print("• Se enfoca en 'calidad y organización de datos'")
    print("• Funciona igual con 1 o múltiples proveedores")
    print("• Busca valor de negocio y mejoras operativas")
    print("• Analiza cada proveedor por su aporte individual")
    
    print("\n🎯 RESULTADO ESPERADO:")
    print("─" * 40)
    print("• La IA analizará los datos estructurados correctamente")
    print("• Dará insights útiles independientemente del número de proveedores")
    print("• Se enfocará en calidad, organización y oportunidades")
    print("• Proporcionará recomendaciones prácticas de negocio")

if __name__ == "__main__":
    simular_nuevo_prompt()
    comparar_prompts()
    
    print("\n" + "=" * 60)
    print("🚀 SIGUIENTE PASO: Probar el nuevo prompt con la aplicación real")
    print("=" * 60)
