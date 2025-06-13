#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRUEBA COMPLETA: SIMULAR ANÁLISIS IA REAL
=========================================
Simula exactamente lo que hace analyze_with_ai() para identificar el problema
"""

import os
import json
import tempfile

def simular_analisis_ia_completo():
    """Simula el análisis completo de IA tal como lo hace la aplicación real"""
    print("🎭 SIMULANDO ANÁLISIS IA COMPLETO")
    print("=" * 50)
    
    # Cargar datos como lo hace la aplicación
    archivo_datos = "datos_extraidos_app.json"
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        return
    
    with open(archivo_datos, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    print(f"✅ Datos cargados: {len(current_data.get('hojas', []))} hojas")
    
    # Simular prepare_data_summary() exactamente como en la app
    try:
        # Importar los mismos módulos
        from analizador_datos_inteligente import AnalizadorDatosInteligente
        from reestructurador_simple import reestructurar_datos_simple
        
        # Crear archivo temporal como lo hace la app
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(current_data, temp_file, ensure_ascii=False, indent=2)
            temp_path = temp_file.name
        
        print(f"✅ Archivo temporal creado: {temp_path}")
        
        # Realizar análisis inteligente
        analizador = AnalizadorDatosInteligente()
        analisis = analizador.analizar_datos_estructurados(temp_path)
        
        # Realizar reestructuración
        datos_reestructurados = reestructurar_datos_simple(temp_path)
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
        if analisis and datos_reestructurados:
            print("✅ Análisis y reestructuración exitosos")
            
            # Generar resumen exacto como la app
            resumen = generar_resumen_completo(analisis, datos_reestructurados)
            
            # Crear prompt exacto como la app
            prompt_completo = f"""
                Analiza los siguientes DATOS ESTRUCTURADOS E INTELIGENTES de una ferretería.
                Estos datos han sido pre-procesados automáticamente identificando proveedores, 
                productos, precios, relaciones y estadísticas de calidad:

                {resumen}

                Basándote en esta información estructurada, proporciona:
                1. 📊 Análisis comparativo entre proveedores (variedad, precios, calidad de datos)
                2. 💰 Insights sobre tendencias de precios y monedas detectadas
                3. 🏪 Ranking de proveedores por diversidad y completitud de información
                4. 💡 Recomendaciones de negocio basadas en los patrones identificados
                5. 🔍 Oportunidades de mejora en la estructura y calidad de datos
                6. 📈 Estrategias para optimizar las listas de precios por proveedor

                Responde en español con análisis específicos basados en los datos estructurados proporcionados.
                """
            
            # Guardar prompt completo para inspección
            with open("prompt_completo_real.txt", 'w', encoding='utf-8') as f:
                f.write(prompt_completo)
            
            print("✅ Prompt completo guardado en 'prompt_completo_real.txt'")
            
            # Mostrar estadísticas del prompt
            print(f"\n📊 ESTADÍSTICAS DEL PROMPT COMPLETO:")
            print(f"   • Total caracteres: {len(prompt_completo):,}")
            print(f"   • Tamaño: {len(prompt_completo.encode('utf-8')) / 1024:.1f} KB")
            print(f"   • Total líneas: {len(prompt_completo.split())}")
            
            # Verificar contenido del resumen dentro del prompt
            verificar_datos_en_prompt(prompt_completo)
            
            # Mostrar muestra del prompt
            print(f"\n📄 MUESTRA DEL PROMPT REAL:")
            print("-" * 50)
            lineas = prompt_completo.split('\n')[:25]
            for i, linea in enumerate(lineas, 1):
                print(f"{i:2d}. {linea}")
            
            print(f"\n💡 REVISA EL ARCHIVO: prompt_completo_real.txt")
            
        else:
            print("❌ Falló análisis o reestructuración")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def generar_resumen_completo(analisis, datos_reestructurados):
    """Genera resumen exacto como lo hace _generar_resumen_con_reestructuracion"""
    resumen = []
    
    # Encabezado del análisis
    resumen.append("=== ANÁLISIS INTELIGENTE CON REESTRUCTURACIÓN DE DATOS ===")
    resumen.append(f"PLANILLA: {analisis['resumen_general']['planilla']}")
    resumen.append(f"TOTAL REGISTROS ORIGINALES: {analisis['resumen_general']['total_registros']:,}")
    
    # Estadísticas de reestructuración
    total_reestructurados = sum(len(productos) for productos in datos_reestructurados.values())
    resumen.append(f"TOTAL PRODUCTOS REESTRUCTURADOS: {total_reestructurados:,}")
    resumen.append(f"EFICIENCIA DE REESTRUCTURACIÓN: {(total_reestructurados/analisis['resumen_general']['total_registros']*100):.1f}%")
    resumen.append("")
    
    # Análisis por proveedor con datos reestructurados
    resumen.append("=== PROVEEDORES CON DATOS REESTRUCTURADOS ===")
    for proveedor, productos in datos_reestructurados.items():
        productos_con_precio = len([p for p in productos if p.get('PRECIO')])
        productos_con_codigo = len([p for p in productos if p.get('CODIGO')])
        productos_con_marca = len([p for p in productos if p.get('MARCA')])
        
        resumen.append(f"{proveedor}:")
        resumen.append(f"  • Productos reestructurados: {len(productos):,}")
        resumen.append(f"  • Con precio detectado: {productos_con_precio:,} ({productos_con_precio/len(productos)*100:.1f}%)")
        resumen.append(f"  • Con código identificado: {productos_con_codigo:,} ({productos_con_codigo/len(productos)*100:.1f}%)")
        resumen.append(f"  • Con marca detectada: {productos_con_marca:,} ({productos_con_marca/len(productos)*100:.1f}%)")
        
        # Muestra de productos reestructurados
        if productos:
            resumen.append(f"  • Muestra de productos reestructurados:")
            for i, producto in enumerate(productos[:2], 1):
                resumen.append(f"    {i}. CÓDIGO: {producto.get('CODIGO', 'N/A')}")
                resumen.append(f"       DESCRIPCIÓN: {producto.get('DESCRIPCION', 'N/A')[:50]}...")
                resumen.append(f"       PRECIO: {producto.get('PRECIO', 'N/A')} {producto.get('MONEDA', '')}")
                resumen.append(f"       MARCA: {producto.get('MARCA', 'N/A')}")
        
        resumen.append("")
    
    # Información contextual exacta como la app
    resumen.append("=== INFORMACIÓN CONTEXTUAL ===")
    resumen.append("Este análisis se basa en datos REESTRUCTURADOS INTELIGENTEMENTE.")
    resumen.append("Los datos han sido procesados para identificar correctamente:")
    resumen.append("- CÓDIGOS DE PRODUCTOS separados de descripciones")
    resumen.append("- PRECIOS extraídos y clasificados por moneda")
    resumen.append("- PROVEEDORES organizados por hoja")
    resumen.append("- MARCAS detectadas automáticamente")
    resumen.append("- DESCRIPCIONES limpias y optimizadas")
    resumen.append("- DUPLICADOS eliminados automáticamente")
    resumen.append("")
    resumen.append("USA ESTE ANÁLISIS PARA RECOMENDAR MEJORAS EN LA ESTRUCTURACIÓN DE DATOS.")
    
    return "\n".join(resumen)

def verificar_datos_en_prompt(prompt):
    """Verifica qué datos específicos están en el prompt"""
    print(f"\n🔍 VERIFICACIÓN DE DATOS EN EL PROMPT:")
    print("-" * 40)
    
    # Buscar proveedores específicos
    proveedores = ["CRIMARAL", "ANCAIG", "HERRAMETAL", "YAYI", "FERRIPLAST", "BABUSI"]
    proveedores_encontrados = []
    
    for proveedor in proveedores:
        if proveedor in prompt:
            # Buscar estadísticas específicas del proveedor
            lineas = prompt.split('\n')
            for i, linea in enumerate(lineas):
                if proveedor in linea and "Productos reestructurados:" in linea:
                    proveedores_encontrados.append(proveedor)
                    print(f"   ✅ {proveedor}: Encontrado con estadísticas")
                    break
    
    if len(proveedores_encontrados) > 1:
        print(f"   ✅ MÚLTIPLES PROVEEDORES DETECTADOS: {len(proveedores_encontrados)}")
        print(f"      Proveedores: {', '.join(proveedores_encontrados)}")
    else:
        print(f"   ❌ SOLO 1 PROVEEDOR DETECTADO")
    
    # Buscar estadísticas clave
    if "30,439" in prompt or "30439" in prompt:
        print("   ✅ Estadísticas totales presentes")
    if "EFICIENCIA DE REESTRUCTURACIÓN: 100.0%" in prompt:
        print("   ✅ Métricas de reestructuración presentes")
    if "DATOS REESTRUCTURADOS INTELIGENTEMENTE" in prompt:
        print("   ✅ Contexto de reestructuración presente")

if __name__ == "__main__":
    simular_analisis_ia_completo()
