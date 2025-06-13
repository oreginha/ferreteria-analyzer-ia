#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación para datos purificados de ferretería
Verifica la calidad y consistencia de los datos finales
"""

import json
import re
from collections import Counter


def validar_datos_purificados(archivo_json):
    """Valida y genera reporte de calidad de datos purificados"""
    
    print("🔍 VALIDADOR DE DATOS PURIFICADOS")
    print("=" * 50)
    
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar archivo: {e}")
        return False
    
    productos = datos.get('productos', [])
    metadata = datos.get('metadata', {})
    estadisticas = datos.get('estadisticas', {})
    
    print(f"📊 INFORMACIÓN GENERAL")
    print(f"   • Archivo: {archivo_json}")
    print(f"   • Planilla original: {metadata.get('planilla_original')}")
    print(f"   • Proveedor: {metadata.get('proveedor')}")
    print(f"   • Total productos: {len(productos):,}")
    print(f"   • Eficiencia: {metadata.get('eficiencia_purificacion')}")
    print()
    
    # Validaciones de calidad
    errores = []
    advertencias = []
    
    print("🔎 VALIDACIONES DE CALIDAD:")
    print("-" * 30)
    
    # 1. Verificar productos duplicados por código
    codigos = [p.get('codigo') for p in productos if p.get('codigo')]
    duplicados = [codigo for codigo, count in Counter(codigos).items() if count > 1]
    
    if duplicados:
        errores.append(f"Se encontraron {len(duplicados)} códigos duplicados")
        print(f"   ❌ Códigos duplicados: {len(duplicados)}")
        print(f"      Ejemplos: {duplicados[:5]}")
    else:
        print(f"   ✅ Sin códigos duplicados")
    
    # 2. Verificar formato de códigos
    codigos_invalidos = []
    patron_codigo = re.compile(r'^[0-9]{6,8}$')
    for producto in productos:
        codigo = producto.get('codigo')
        if codigo and not patron_codigo.match(codigo):
            codigos_invalidos.append(codigo)
    
    if codigos_invalidos:
        advertencias.append(f"Se encontraron {len(codigos_invalidos)} códigos con formato inválido")
        print(f"   ⚠️  Códigos con formato inválido: {len(codigos_invalidos)}")
        print(f"      Ejemplos: {codigos_invalidos[:5]}")
    else:
        print(f"   ✅ Todos los códigos tienen formato válido")
    
    # 3. Verificar precios
    productos_sin_precio = [p for p in productos if not p.get('precio') and not p.get('precios')]
    if productos_sin_precio:
        advertencias.append(f"{len(productos_sin_precio)} productos sin precio")
        print(f"   ⚠️  Productos sin precio: {len(productos_sin_precio)}")
    else:
        print(f"   ✅ Todos los productos tienen precio")
    
    # 4. Verificar descripciones
    descripciones_cortas = [p for p in productos if p.get('descripcion') and len(p['descripcion']) < 5]
    if descripciones_cortas:
        advertencias.append(f"{len(descripciones_cortas)} productos con descripción muy corta")
        print(f"   ⚠️  Descripciones muy cortas: {len(descripciones_cortas)}")
    else:
        print(f"   ✅ Descripciones tienen longitud adecuada")
    
    # 5. Verificar completitud
    productos_completos = [p for p in productos 
                          if p.get('codigo') and p.get('descripcion') and 
                          (p.get('precio') or p.get('precios'))]
    
    porcentaje_completos = (len(productos_completos) / len(productos)) * 100 if productos else 0
    print(f"   📈 Productos completos: {len(productos_completos):,} ({porcentaje_completos:.1f}%)")
    
    print()
    print("📋 ESTADÍSTICAS DETALLADAS:")
    print("-" * 30)
    
    # Análisis por campo
    campos_stats = {}
    for producto in productos:
        for campo in producto.keys():
            if campo not in campos_stats:
                campos_stats[campo] = 0
            campos_stats[campo] += 1
    
    for campo, cantidad in sorted(campos_stats.items()):
        porcentaje = (cantidad / len(productos)) * 100 if productos else 0
        print(f"   {campo}: {cantidad:,} ({porcentaje:.1f}%)")
    
    # Análisis de precios
    print()
    print("💰 ANÁLISIS DE PRECIOS:")
    print("-" * 20)
    
    precios_unicos = []
    for producto in productos:
        if producto.get('precio'):
            try:
                precio_num = float(producto['precio'].replace(',', '.'))
                precios_unicos.append(precio_num)
            except:
                pass
        elif producto.get('precios'):
            for precio in producto['precios']:
                try:
                    precio_num = float(precio.replace(',', '.'))
                    precios_unicos.append(precio_num)
                except:
                    pass
    
    if precios_unicos:
        precio_min = min(precios_unicos)
        precio_max = max(precios_unicos)
        precio_promedio = sum(precios_unicos) / len(precios_unicos)
        
        print(f"   Precio mínimo: ${precio_min:,.2f}")
        print(f"   Precio máximo: ${precio_max:,.2f}")
        print(f"   Precio promedio: ${precio_promedio:,.2f}")
        print(f"   Total precios analizados: {len(precios_unicos):,}")
    
    # Análisis por hoja
    print()
    print("📄 ANÁLISIS POR HOJA:")
    print("-" * 20)
    
    productos_por_hoja = {}
    for producto in productos:
        hoja = producto.get('hoja', 'Sin hoja')
        if hoja not in productos_por_hoja:
            productos_por_hoja[hoja] = 0
        productos_por_hoja[hoja] += 1
    
    for hoja, cantidad in sorted(productos_por_hoja.items()):
        porcentaje = (cantidad / len(productos)) * 100 if productos else 0
        print(f"   {hoja}: {cantidad:,} ({porcentaje:.1f}%)")
    
    # Resumen final
    print()
    print("📝 RESUMEN DE VALIDACIÓN:")
    print("-" * 25)
    
    if not errores and not advertencias:
        print("   ✅ Todos los datos están correctos")
        calidad = "EXCELENTE"
    elif errores:
        print("   ❌ Se encontraron errores críticos:")
        for error in errores:
            print(f"      • {error}")
        calidad = "REQUIERE CORRECCIÓN"
    elif advertencias:
        print("   ⚠️  Se encontraron advertencias:")
        for advertencia in advertencias:
            print(f"      • {advertencia}")
        calidad = "BUENA (con observaciones)"
    
    print()
    print(f"🎯 CALIDAD DE DATOS: {calidad}")
    print(f"📊 EFICIENCIA FINAL: {porcentaje_completos:.1f}% productos completos")
    
    return True


def main():
    archivo = "datos_purificados_final.json"
    validar_datos_purificados(archivo)


if __name__ == "__main__":
    main()
