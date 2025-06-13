#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demostración de la transformación de datos crudos a datos purificados
"""

import json


def demostrar_transformacion():
    """Demuestra la diferencia entre datos originales y purificados"""
    
    print("🔄 DEMOSTRACIÓN DE TRANSFORMACIÓN DE DATOS")
    print("=" * 60)
    
    # Cargar datos originales
    try:
        with open('datos_extraidos_app.json', 'r', encoding='utf-8') as f:
            datos_originales = json.load(f)
        
        with open('datos_ferreteria_limpio_final.json', 'r', encoding='utf-8') as f:
            datos_purificados = json.load(f)
            
    except Exception as e:
        print(f"❌ Error al cargar archivos: {e}")
        return
    
    print("📊 COMPARACIÓN DE VOLUMEN DE DATOS:")
    print("-" * 35)
    
    # Obtener algunas filas originales como ejemplo
    filas_originales = []
    for hoja in datos_originales.get('hojas', [])[:1]:  # Solo primera hoja
        for tabla in hoja.get('tablas', [])[:1]:  # Solo primera tabla
            filas_originales = tabla.get('filas', [])[:10]  # Primeras 10 filas
            break
        break
    
    productos_finales = datos_purificados.get('productos', [])[:5]
    
    print(f"Datos originales (ejemplo de filas crudas):")
    print(f"Total de hojas procesadas: {len(datos_originales.get('hojas', []))}")
    print()
    
    print("🔍 EJEMPLO DE DATOS ORIGINALES (CRUDO):")
    print("-" * 40)
    for i, fila in enumerate(filas_originales[:3]):
        print(f"Fila {i+1}: {fila}")
    print("...")
    print()
    
    print("✨ DATOS DESPUÉS DE PURIFICACIÓN:")
    print("-" * 35)
    print(f"Productos finales de calidad: {len(productos_finales)} (de {datos_purificados['metadata']['total_productos']} totales)")
    print()
    
    for i, producto in enumerate(productos_finales):
        print(f"Producto {i+1}:")
        for clave, valor in producto.items():
            if isinstance(valor, list) and len(valor) > 2:
                print(f"  {clave}: {valor[0]} (+ {len(valor)-1} más)")
            elif isinstance(valor, str) and len(valor) > 40:
                print(f"  {clave}: {valor[:40]}...")
            else:
                print(f"  {clave}: {valor}")
        print()
    
    print("📈 MEJORAS LOGRADAS:")
    print("-" * 20)
    
    # Calcular mejoras
    filas_procesadas = datos_purificados['metadata'].get('total_productos', 0)
    productos_validos = len(productos_finales)
    
    mejoras = [
        "✅ Eliminación de instrucciones y textos irrelevantes",
        "✅ Estructuración de datos en campos específicos (código, descripción, precio, etc.)",
        "✅ Eliminación de duplicados por código",
        "✅ Validación de formatos (códigos numéricos, precios válidos)",
        "✅ Normalización de datos (precios, medidas, IVA)",
        f"✅ Reducción de ruido: {filas_procesadas:,} → {productos_validos:,} productos válidos",
        f"✅ Completitud: {datos_purificados['estadisticas']['productos_completos']:,} productos completos",
        "✅ Estructura JSON organizada y consulta fácil"
    ]
    
    for mejora in mejoras:
        print(f"  {mejora}")
    
    print()
    print("🎯 ESTRUCTURA FINAL:")
    print("-" * 18)
    print("  {")
    print("    'metadata': { información de procesamiento },")
    print("    'estadisticas': { métricas de calidad },")
    print("    'productos': [")
    print("      {")
    print("        'codigo': '1000000',")
    print("        'descripcion': 'ARANDELA FIBRA...',")
    print("        'precio': '5648,37',")
    print("        'iva': 24,")
    print("        'medida': '1/2\"',")
    print("        'hoja': 'YAYI_LISTA_01',")
    print("        'proveedor': 'YAYI'")
    print("      },")
    print("      ...")
    print("    ]")
    print("  }")
    
    print()
    print("🏆 RESULTADO FINAL:")
    print("=" * 20)
    print("✨ Datos listos para:")
    print("  • Análisis de inventario")
    print("  • Búsquedas por código o descripción")
    print("  • Análisis de precios y márgenes")
    print("  • Integración con sistemas de gestión")
    print("  • Reportes automatizados")
    print("  • APIs y aplicaciones web")


if __name__ == "__main__":
    demostrar_transformacion()
