#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMOSTRACIÓN DEL ANÁLISIS INTELIGENTE COMPLETO
===============================================
Muestra todas las capacidades del AnalizadorDatosInteligente
"""

import json
import os
from analizador_datos_inteligente import AnalizadorDatosInteligente

def demo_analisis_completo():
    """Demuestra el análisis inteligente completo"""
    print("🧠 DEMOSTRACIÓN ANÁLISIS INTELIGENTE COMPLETO")
    print("=" * 60)
    
    # Verificar archivo de datos
    archivo_datos = "datos_extraidos_app.json"
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        print("💡 Primero ejecuta la extracción de datos")
        return
    
    # Crear analizador
    print("🔍 Inicializando AnalizadorDatosInteligente...")
    analizador = AnalizadorDatosInteligente()
    
    # Realizar análisis completo
    print("📊 Analizando datos estructurados...")
    analisis = analizador.analizar_datos_estructurados(archivo_datos)
    
    if not analisis:
        print("❌ No se pudo realizar el análisis")
        return
    
    print("✅ Análisis completado exitosamente!")
    print("-" * 60)
    
    # MOSTRAR RESULTADOS DETALLADOS
    print("\n📋 RESUMEN GENERAL:")
    general = analisis['resumen_general']
    print(f"   • Planilla: {general['planilla']}")
    print(f"   • Estrategia: {general['estrategia_proveedores']}")
    print(f"   • Total registros: {general['total_registros']:,}")
    
    print("\n🏪 PROVEEDORES IDENTIFICADOS:")
    proveedores = analisis['proveedores_identificados']
    for nombre, info in proveedores.items():
        print(f"   📦 {nombre}:")
        print(f"      • Productos: {info['total_productos']:,}")
        print(f"      • Hojas: {len(info['hojas'])}")
        if info['precios_detectados']:
            print(f"      • Precios: {len(info['precios_detectados'])} detectados")
        if info['categorias_identificadas']:
            print(f"      • Categorías: {', '.join(info['categorias_identificadas'][:3])}")
    
    print("\n💰 ANÁLISIS DE PRECIOS:")
    precios = analisis['precios_detectados']
    print(f"   • Total precios encontrados: {precios['total_precios_encontrados']}")
    print(f"   • Monedas detectadas: {', '.join(precios['monedas_detectadas'])}")
    if precios.get('muestra_precios'):
        print(f"   • Muestra: {', '.join(precios['muestra_precios'][:5])}")
    
    print("\n📊 MUESTRA DE PRODUCTOS ANALIZADOS:")
    productos = analisis['productos_analizados'][:5]
    for i, producto in enumerate(productos, 1):
        print(f"   {i}. {producto.get('descripcion', 'Sin descripción')[:50]}...")
        if producto.get('precio'):
            print(f"      💰 Precio: {producto['precio']}")
        if producto.get('codigo'):
            print(f"      🏷️  Código: {producto['codigo']}")
        if producto.get('marca'):
            print(f"      🔖 Marca: {producto['marca']}")
    
    print("\n📈 ESTADÍSTICAS INTELIGENTES:")
    stats = analisis['estadisticas_inteligentes']
    print(f"   • Calidad de datos: {stats.get('calidad_datos', 0):.1f}%")
    if 'completitud_informacion' in stats:
        comp = stats['completitud_informacion']
        print(f"   • Productos con precio: {comp.get('productos_con_precio', 0):.1f}%")
        print(f"   • Productos con código: {comp.get('productos_con_codigo', 0):.1f}%")
    
    print("\n💡 RECOMENDACIONES IA:")
    for rec in analisis['recomendaciones_ia']:
        print(f"   • {rec}")
    
    print("\n🔗 MAPEO DE RELACIONES:")
    relaciones = analisis['relaciones_datos']
    if 'proveedor_productos' in relaciones:
        print("   📦 Proveedor → Productos:")
        for prov, cant in relaciones['proveedor_productos'].items():
            print(f"      {prov}: {cant:,} productos")
    
    # GENERAR RESUMEN PARA IA
    print("\n" + "=" * 60)
    print("🤖 GENERANDO RESUMEN ESTRUCTURADO PARA IA...")
    resumen_ia = analizador.generar_resumen_para_ia(analisis)
    
    # Guardar resumen
    with open("resumen_analisis_inteligente.txt", 'w', encoding='utf-8') as f:
        f.write(resumen_ia)
    
    print("✅ Resumen guardado en 'resumen_analisis_inteligente.txt'")
    
    # Mostrar muestra del resumen
    print("\n📄 MUESTRA DEL RESUMEN PARA IA:")
    print("-" * 40)
    lineas = resumen_ia.split('\n')[:15]
    for linea in lineas:
        print(f"   {linea}")
    print("   ... (continúa)")
    
    print("\n🎯 CAPACIDADES DEMOSTRADAS:")
    print("   ✅ Detección automática de proveedores")
    print("   ✅ Identificación de precios y monedas")
    print("   ✅ Análisis de productos y categorías")
    print("   ✅ Mapeo de relaciones entre datos")
    print("   ✅ Estadísticas de calidad de datos")
    print("   ✅ Recomendaciones inteligentes")
    print("   ✅ Resumen estructurado para IA")
    
    print(f"\n🎉 ANÁLISIS INTELIGENTE COMPLETADO!")
    print(f"📊 {general['total_registros']:,} registros analizados")
    print(f"🏪 {len(proveedores)} proveedores identificados")
    print(f"💰 {precios['total_precios_encontrados']} precios detectados")

if __name__ == "__main__":
    demo_analisis_completo()
