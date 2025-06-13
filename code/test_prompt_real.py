#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del nuevo prompt con datos reales
Verifica que la IA ahora analice correctamente los datos reestructurados
"""

import os
import sys
import json

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ferreteria_analyzer_app import FerreteriaAnalyzerApp
    from analizador_datos_inteligente import AnalizadorDatosInteligente
    from reestructurador_simple import ReestructuradorSimple
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    sys.exit(1)

def test_nuevo_prompt_real():
    """Prueba el nuevo prompt con datos reales"""
    print("🧪 PRUEBA DEL NUEVO PROMPT CON DATOS REALES")
    print("=" * 60)
    
    # Verificar que existen los datos
    datos_file = "datos_extraidos_app.json"
    if not os.path.exists(datos_file):
        print(f"❌ Error: No se encuentra el archivo {datos_file}")
        print("   Ejecuta primero la extracción de datos en la aplicación.")
        return False
    
    print(f"✅ Archivo de datos encontrado: {datos_file}")
    
    try:
        # Cargar datos extraídos
        with open(datos_file, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"✅ Datos cargados: {len(datos.get('hojas', []))} hojas")
        
        # Crear instancia del analizador
        analizador = AnalizadorDatosInteligente()
        analisis_inteligente = analizador.analizar(datos)
        
        print("✅ Análisis inteligente completado")
        
        # Reestructurar datos
        reestructurador = ReestructuradorSimple()
        datos_reestructurados = reestructurador.reestructurar(datos)
        
        print("✅ Reestructuración completada")
        
        # Simular el método prepare_data_summary
        resumen = generar_resumen_datos(analisis_inteligente, datos_reestructurados)
        
        # Extraer lista de proveedores
        proveedores_detectados = []
        if "=== PROVEEDORES CON DATOS REESTRUCTURADOS ===" in resumen:
            lineas = resumen.split('\n')
            for linea in lineas:
                if ':' in linea and 'Productos reestructurados:' in linea:
                    proveedor = linea.split(':')[0].strip()
                    if proveedor and proveedor not in proveedores_detectados:
                        proveedores_detectados.append(proveedor)
        
        print(f"✅ Proveedores detectados: {len(proveedores_detectados)}")
        for prov in proveedores_detectados:
            print(f"   • {prov}")
        
        # Crear lista de proveedores
        lista_proveedores = ""
        if proveedores_detectados:
            lista_proveedores = "PROVEEDORES INCLUIDOS EN ESTE ANÁLISIS:\n"
            for i, prov in enumerate(proveedores_detectados, 1):
                lista_proveedores += f"{i}. {prov}\n"
            lista_proveedores += f"TOTAL: {len(proveedores_detectados)} PROVEEDORES\n\n"
        
        # Generar el nuevo prompt
        nuevo_prompt = f"""
                ANÁLISIS DE DATOS ESTRUCTURADOS DE FERRETERÍA

                {lista_proveedores}DATOS PROCESADOS E INTELIGENTEMENTE ORGANIZADOS:
                Los siguientes datos han sido limpiados, reestructurados y organizados automáticamente 
                para facilitar el análisis de calidad, estructura y oportunidades de mejora:

                {resumen}

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
        
        # Guardar el prompt real
        with open("nuevo_prompt_real.txt", "w", encoding="utf-8") as f:
            f.write(nuevo_prompt)
        
        print("✅ Nuevo prompt guardado en 'nuevo_prompt_real.txt'")
        
        # Mostrar resumen del prompt
        print("\n📊 RESUMEN DEL NUEVO PROMPT:")
        print("-" * 50)
        print(f"• Proveedores incluidos: {len(proveedores_detectados)}")
        print(f"• Tamaño del resumen: {len(resumen)} caracteres")
        print(f"• Enfoque: Calidad y organización de datos")
        print(f"• Objetivo: Valor de negocio y optimización")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el test: {str(e)}")
        return False

def generar_resumen_datos(analisis_inteligente, datos_reestructurados):
    """Genera el resumen de datos como lo hace prepare_data_summary"""
    
    try:
        # Estadísticas básicas
        total_original = analisis_inteligente.get('total_registros', 0)
        total_reestructurado = len(datos_reestructurados)
        eficiencia = (total_reestructurado / total_original * 100) if total_original > 0 else 0
        
        resumen = []
        resumen.append("=== ANÁLISIS INTELIGENTE CON REESTRUCTURACIÓN DE DATOS ===")
        resumen.append(f"PLANILLA: FERRETERIA")
        resumen.append(f"TOTAL REGISTROS ORIGINALES: {total_original:,}")
        resumen.append(f"TOTAL PRODUCTOS REESTRUCTURADOS: {total_reestructurado:,}")
        resumen.append(f"EFICIENCIA DE REESTRUCTURACIÓN: {eficiencia:.1f}%")
        resumen.append("")
        
        # Análisis por proveedor
        proveedores_stats = {}
        for producto in datos_reestructurados:
            proveedor = producto.get('proveedor', 'DESCONOCIDO')
            if proveedor not in proveedores_stats:
                proveedores_stats[proveedor] = {
                    'total': 0,
                    'con_precio': 0,
                    'con_codigo': 0
                }
            
            proveedores_stats[proveedor]['total'] += 1
            if producto.get('precio'):
                proveedores_stats[proveedor]['con_precio'] += 1
            if producto.get('codigo'):
                proveedores_stats[proveedor]['con_codigo'] += 1
        
        resumen.append("=== PROVEEDORES CON DATOS REESTRUCTURADOS ===")
        for proveedor, stats in proveedores_stats.items():
            if stats['total'] > 0:  # Solo mostrar proveedores con datos
                precio_pct = (stats['con_precio'] / stats['total'] * 100) if stats['total'] > 0 else 0
                codigo_pct = (stats['con_codigo'] / stats['total'] * 100) if stats['total'] > 0 else 0
                
                resumen.append(f"{proveedor}:")
                resumen.append(f"  • Productos reestructurados: {stats['total']:,}")
                resumen.append(f"  • Con precio detectado: {stats['con_precio']:,} ({precio_pct:.1f}%)")
                resumen.append(f"  • Con código identificado: {stats['con_codigo']:,} ({codigo_pct:.1f}%)")
                resumen.append("")
        
        # Información adicional
        resumen.append("=== INFORMACIÓN DE REESTRUCTURACIÓN ===")
        resumen.append("• DATOS INTELIGENTEMENTE PROCESADOS:")
        resumen.append("  - PRECIOS extraídos y normalizados automáticamente")
        resumen.append("  - CÓDIGOS identificados mediante patrones avanzados")
        resumen.append("  - CATEGORÍAS detectadas por análisis semántico")
        resumen.append("  - PROVEEDORES organizados por hoja")
        resumen.append("  - MARCAS detectadas automáticamente")
        resumen.append("  - DESCRIPCIONES limpias y optimizadas")
        resumen.append("  - DUPLICADOS eliminados automáticamente")
        resumen.append("")
        resumen.append("USA ESTE ANÁLISIS PARA RECOMENDAR MEJORAS EN LA ESTRUCTURACIÓN DE DATOS.")
        
        return "\n".join(resumen)
        
    except Exception as e:
        return f"Error generando resumen: {str(e)}"

def comparar_con_anterior():
    """Compara con el resultado anterior"""
    print("\n" + "=" * 60)
    print("📈 COMPARACIÓN CON PROBLEMA ANTERIOR")
    print("=" * 60)
    
    print("\n🔴 PROBLEMA ANTERIOR:")
    print("La IA respondía: 'solo se cuenta con datos del proveedor Yayi'")
    print("Ignoraba otros proveedores como CRIMARAL, HERRAMETAL, etc.")
    
    print("\n🟢 SOLUCIÓN ESPERADA AHORA:")
    print("La IA debería analizar TODOS los proveedores detectados")
    print("Se enfocará en calidad de datos, no en comparaciones")
    print("Dará recomendaciones útiles para cada proveedor")

if __name__ == "__main__":
    if test_nuevo_prompt_real():
        comparar_con_anterior()
        print("\n" + "=" * 60)
        print("🚀 PRÓXIMO PASO: Probar en la aplicación real con IA")
        print("=" * 60)
    else:
        print("\n❌ Test fallido. Revisa los datos de entrada.")
