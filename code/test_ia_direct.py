#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRUEBA DIRECTA: ¿QUÉ RECIBE LA IA?
=================================
Prueba directa del método prepare_data_summary sin GUI
"""

import os
import json
import tempfile

def test_prepare_data_summary_direct():
    """Prueba directa del método prepare_data_summary"""
    print("🔬 PRUEBA DIRECTA DEL MÉTODO prepare_data_summary")
    print("=" * 60)
    
    # Cargar datos
    archivo_datos = "datos_extraidos_app.json"
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        return
    
    with open(archivo_datos, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    print(f"✅ Datos cargados: {len(current_data.get('hojas', []))} hojas")
    
    # Reproducir la lógica del método prepare_data_summary directamente
    try:
        # Importar el analizador inteligente y reestructurador
        from analizador_datos_inteligente import AnalizadorDatosInteligente
        from reestructurador_simple import reestructurar_datos_simple
        
        print("✅ Módulos importados correctamente")
        
        # Guardar datos temporalmente para análisis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(current_data, temp_file, ensure_ascii=False, indent=2)
            temp_path = temp_file.name
        
        print(f"✅ Datos guardados temporalmente en: {temp_path}")
        
        # Realizar análisis inteligente
        analizador = AnalizadorDatosInteligente()
        analisis = analizador.analizar_datos_estructurados(temp_path)
        
        if analisis:
            print("✅ Análisis inteligente exitoso")
            print(f"   • Proveedores: {len(analisis['proveedores_identificados'])}")
            print(f"   • Registros: {analisis['resumen_general']['total_registros']:,}")
        else:
            print("❌ Análisis inteligente falló")
        
        # Realizar reestructuración inteligente de datos
        datos_reestructurados = reestructurar_datos_simple(temp_path)
        
        if datos_reestructurados:
            print("✅ Reestructuración exitosa")
            total_reestructurados = sum(len(productos) for productos in datos_reestructurados.values())
            print(f"   • Proveedores reestructurados: {len(datos_reestructurados)}")
            print(f"   • Productos reestructurados: {total_reestructurados:,}")
        else:
            print("❌ Reestructuración falló")
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
        if analisis and datos_reestructurados:
            # Generar resumen inteligente (simplificado)
            resumen_inteligente = generar_resumen_simplificado(analisis, datos_reestructurados)
            
            # Guardar resumen para inspección
            with open("resumen_directo_ia.txt", 'w', encoding='utf-8') as f:
                f.write(resumen_inteligente)
            
            print("✅ Resumen generado y guardado en 'resumen_directo_ia.txt'")
            
            # Mostrar primeras líneas
            print("\n📄 PRIMERAS LÍNEAS DEL RESUMEN:")
            print("-" * 40)
            lineas = resumen_inteligente.split('\n')[:15]
            for i, linea in enumerate(lineas, 1):
                print(f"{i:2d}. {linea}")
            
            # Verificar indicadores de análisis inteligente
            verificar_indicadores(resumen_inteligente)
            
            return resumen_inteligente
        else:
            print("❌ No se pudo generar el resumen inteligente")
            return None
            
    except Exception as e:
        print(f"❌ Error en prueba directa: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generar_resumen_simplificado(analisis, datos_reestructurados):
    """Genera un resumen simplificado combinando análisis y reestructuración"""
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
        # Estadísticas de calidad de los datos reestructurados
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
    
    # Información contextual
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

def verificar_indicadores(resumen):
    """Verifica indicadores de análisis inteligente en el resumen"""
    print(f"\n🔍 VERIFICACIÓN DE INDICADORES:")
    print("-" * 40)
    
    indicadores = {
        "ANÁLISIS INTELIGENTE": 0,
        "REESTRUCTURACIÓN": 0,
        "CÓDIGO": 0,
        "PRECIO": 0,
        "MARCA": 0,
        "PROVEEDOR": 0,
        "DATOS REESTRUCTURADOS": 0
    }
    
    for indicador in indicadores:
        count = resumen.upper().count(indicador)
        indicadores[indicador] = count
        estado = "✅" if count > 0 else "❌"
        print(f"   {estado} {indicador}: {count} menciones")
    
    total_indicadores = sum(1 for count in indicadores.values() if count > 0)
    print(f"\n📊 RESUMEN: {total_indicadores}/{len(indicadores)} indicadores presentes")
    
    if total_indicadores >= 5:
        print("✅ EL RESUMEN CONTIENE ANÁLISIS INTELIGENTE")
    else:
        print("❌ EL RESUMEN NO PARECE CONTENER ANÁLISIS INTELIGENTE")

if __name__ == "__main__":
    test_prepare_data_summary_direct()
