#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACIÓN: ¿QUÉ ESTÁ RECIBIENDO LA IA?
=======================================
Script para verificar exactamente qué datos está recibiendo la IA
y por qué sigue analizando datos crudos en lugar de datos reestructurados.
"""

import os
import json
from ferreteria_analyzer_app import FerreteriaAnalyzerApp
import tempfile

def verificar_datos_ia():
    """Verifica exactamente qué datos está recibiendo la IA"""
    print("🔍 VERIFICANDO QUÉ RECIBE LA IA")
    print("=" * 50)
    
    # Cargar datos de ejemplo
    archivo_datos = "datos_extraidos_app.json"
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        return
    
    # Crear instancia de la aplicación
    app = FerreteriaAnalyzerApp(None)
    
    # Cargar datos
    with open(archivo_datos, 'r', encoding='utf-8') as f:
        app.current_data = json.load(f)
    
    print(f"✅ Datos cargados: {len(app.current_data.get('hojas', []))} hojas")
    
    # Obtener el resumen que va a la IA
    print("\n🧠 OBTENIENDO RESUMEN PARA IA...")
    resumen_ia = app.prepare_data_summary()
    
    # Guardar el resumen para inspección
    with open("resumen_que_recibe_ia.txt", 'w', encoding='utf-8') as f:
        f.write(resumen_ia)
    
    print("✅ Resumen guardado en 'resumen_que_recibe_ia.txt'")
    
    # Mostrar primeras líneas del resumen
    print("\n📄 PRIMERAS LÍNEAS DEL RESUMEN PARA IA:")
    print("-" * 40)
    lineas = resumen_ia.split('\n')[:20]
    for i, linea in enumerate(lineas, 1):
        print(f"{i:2d}. {linea}")
    
    print(f"\n📊 ESTADÍSTICAS DEL RESUMEN:")
    print(f"   • Total líneas: {len(resumen_ia.split())}")
    print(f"   • Total caracteres: {len(resumen_ia):,}")
    print(f"   • Tamaño estimado: {len(resumen_ia.encode('utf-8')) / 1024:.1f} KB")
    
    # Verificar si contiene indicadores de análisis inteligente
    indicadores_inteligentes = [
        "ANÁLISIS INTELIGENTE",
        "REESTRUCTURACIÓN",
        "CÓDIGO",
        "PRECIO",
        "MARCA",
        "PROVEEDOR"
    ]
    
    print(f"\n🔍 INDICADORES DE ANÁLISIS INTELIGENTE:")
    for indicador in indicadores_inteligentes:
        count = resumen_ia.upper().count(indicador)
        estado = "✅" if count > 0 else "❌"
        print(f"   {estado} {indicador}: {count} menciones")
    
    # Verificar si hay menciones de datos crudos vs reestructurados
    menciones_crudos = resumen_ia.upper().count("CRUDO")
    menciones_reestructurados = resumen_ia.upper().count("REESTRUCTURADO")
    
    print(f"\n⚖️ ANÁLISIS DE CONTENIDO:")
    print(f"   • Menciones 'CRUDO': {menciones_crudos}")
    print(f"   • Menciones 'REESTRUCTURADO': {menciones_reestructurados}")
    
    if menciones_reestructurados > menciones_crudos:
        print("   ✅ LA IA ESTÁ RECIBIENDO DATOS REESTRUCTURADOS")
    else:
        print("   ❌ LA IA PODRÍA ESTAR RECIBIENDO DATOS CRUDOS")
    
    return resumen_ia

def verificar_analisis_inteligente():
    """Verifica si el análisis inteligente está funcionando"""
    print("\n" + "=" * 50)
    print("🧠 VERIFICANDO ANÁLISIS INTELIGENTE")
    print("=" * 50)
    
    try:
        from analizador_datos_inteligente import AnalizadorDatosInteligente
        from reestructurador_simple import reestructurar_datos_simple
        
        archivo_datos = "datos_extraidos_app.json"
        
        # Probar análisis inteligente directamente
        analizador = AnalizadorDatosInteligente()
        analisis = analizador.analizar_datos_estructurados(archivo_datos)
        
        if analisis:
            print("✅ AnalizadorDatosInteligente: FUNCIONAL")
            print(f"   • Proveedores identificados: {len(analisis['proveedores_identificados'])}")
            print(f"   • Total registros: {analisis['resumen_general']['total_registros']:,}")
        else:
            print("❌ AnalizadorDatosInteligente: FALLA")
        
        # Probar reestructuración
        datos_reestructurados = reestructurar_datos_simple(archivo_datos)
        
        if datos_reestructurados:
            print("✅ Reestructurador: FUNCIONAL")
            print(f"   • Proveedores reestructurados: {len(datos_reestructurados)}")
            total_productos = sum(len(productos) for productos in datos_reestructurados.values())
            print(f"   • Total productos reestructurados: {total_productos:,}")
        else:
            print("❌ Reestructurador: FALLA")
            
    except Exception as e:
        print(f"❌ Error en verificación: {str(e)}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🔬 DIAGNÓSTICO: ¿QUE RECIBE LA IA?")
    print("=" * 60)
    
    # Verificar análisis inteligente
    if not verificar_analisis_inteligente():
        print("❌ El análisis inteligente tiene problemas")
        return
    
    # Verificar qué recibe la IA
    resumen = verificar_datos_ia()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSIÓN:")
    
    if "ANÁLISIS INTELIGENTE CON REESTRUCTURACIÓN" in resumen:
        print("✅ LA IA ESTÁ RECIBIENDO DATOS REESTRUCTURADOS CORRECTAMENTE")
        print("   El problema podría estar en:")
        print("   • La configuración de la API de Gemini")
        print("   • El prompt enviado a la IA")
        print("   • La interpretación de los datos por la IA")
    else:
        print("❌ LA IA NO ESTÁ RECIBIENDO DATOS REESTRUCTURADOS")
        print("   • Revisa el método prepare_data_summary()")
        print("   • Verifica las importaciones")
        print("   • Comprueba los archivos de análisis inteligente")
    
    print(f"\n📋 REVISA EL ARCHIVO: resumen_que_recibe_ia.txt")

if __name__ == "__main__":
    main()
