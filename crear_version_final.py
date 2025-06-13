#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar duplicados y crear versión final limpia
"""

import json
from datetime import datetime


def crear_version_final_limpia():
    """Crea una versión final sin duplicados y con datos de alta calidad"""
    
    print("🧹 CREANDO VERSIÓN FINAL LIMPIA")
    print("=" * 40)
    
    # Cargar datos purificados
    try:
        with open('datos_purificados_final.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar archivo: {e}")
        return False
    
    productos = datos.get('productos', [])
    print(f"📊 Productos originales: {len(productos):,}")
    
    # Diccionario para productos únicos por código
    productos_unicos = {}
    productos_sin_codigo = []
    duplicados_eliminados = 0
    
    for producto in productos:
        codigo = producto.get('codigo')
        
        if codigo:
            if codigo in productos_unicos:
                # Comparar cuál producto es más completo
                producto_existente = productos_unicos[codigo]
                
                # Contar campos no vacíos en ambos productos
                campos_existente = sum(1 for v in producto_existente.values() if v)
                campos_nuevo = sum(1 for v in producto.values() if v)
                
                # Preferir el producto con más información
                if campos_nuevo > campos_existente:
                    productos_unicos[codigo] = producto
                
                duplicados_eliminados += 1
            else:
                productos_unicos[codigo] = producto
        else:
            # Productos sin código, verificar si tienen descripción única y útil
            descripcion = producto.get('descripcion', '')
            if len(descripcion) > 10:  # Solo si la descripción es útil
                productos_sin_codigo.append(producto)
    
    print(f"📦 Productos únicos con código: {len(productos_unicos):,}")
    print(f"📝 Productos sin código (descripción única): {len(productos_sin_codigo):,}")
    print(f"🗑️ Duplicados eliminados: {duplicados_eliminados:,}")
    
    # Combinar productos únicos
    productos_finales = list(productos_unicos.values()) + productos_sin_codigo
    
    # Filtrar productos de alta calidad
    productos_calidad = []
    for producto in productos_finales:
        # Criterios de calidad
        tiene_codigo = 'codigo' in producto
        tiene_descripcion = 'descripcion' in producto and len(producto['descripcion']) > 5
        tiene_precio = 'precio' in producto or 'precios' in producto
        
        # Solo incluir productos que cumplan criterios mínimos
        if (tiene_codigo and tiene_descripcion) or (tiene_descripcion and tiene_precio and len(producto['descripcion']) > 15):
            productos_calidad.append(producto)
    
    print(f"✨ Productos finales de calidad: {len(productos_calidad):,}")
    
    # Ordenar por código
    productos_calidad.sort(key=lambda x: x.get('codigo', '999999999'))
    
    # Crear estadísticas finales
    stats_finales = {
        'productos_con_codigo': sum(1 for p in productos_calidad if 'codigo' in p),
        'productos_con_precio': sum(1 for p in productos_calidad if 'precio' in p or 'precios' in p),
        'productos_con_descripcion': sum(1 for p in productos_calidad if 'descripcion' in p),
        'productos_con_medida': sum(1 for p in productos_calidad if 'medida' in p),
        'productos_con_iva': sum(1 for p in productos_calidad if 'iva' in p),
        'productos_completos': sum(1 for p in productos_calidad 
                                 if 'codigo' in p and 'descripcion' in p and ('precio' in p or 'precios' in p))
    }
    
    # Crear estructura final
    datos_finales = {
        'metadata': {
            'planilla_original': datos['metadata'].get('planilla_original'),
            'proveedor': datos['metadata'].get('proveedor'),
            'fecha_purificacion_final': datetime.now().isoformat(),
            'version': 'Final Limpia v1.0',
            'total_productos': len(productos_calidad),
            'duplicados_eliminados': duplicados_eliminados,
            'criterios_calidad': [
                'Productos con código y descripción válida',
                'Productos sin código pero con descripción >15 caracteres y precio',
                'Eliminación de duplicados por código',
                'Descripción mínima de 5 caracteres'
            ]
        },
        'estadisticas': stats_finales,
        'productos': productos_calidad
    }
    
    # Guardar archivo final
    archivo_final = 'datos_ferreteria_limpio_final.json'
    try:
        with open(archivo_final, 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Archivo final guardado: {archivo_final}")
        print()
        print("📊 ESTADÍSTICAS FINALES:")
        print("-" * 25)
        print(f"   • Total productos: {len(productos_calidad):,}")
        print(f"   • Con código: {stats_finales['productos_con_codigo']:,}")
        print(f"   • Con descripción: {stats_finales['productos_con_descripcion']:,}")
        print(f"   • Con precio: {stats_finales['productos_con_precio']:,}")
        print(f"   • Completos: {stats_finales['productos_completos']:,}")
        print(f"   • Completitud: {(stats_finales['productos_completos']/len(productos_calidad)*100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False


def mostrar_muestra_final():
    """Muestra una muestra del archivo final"""
    try:
        with open('datos_ferreteria_limpio_final.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        productos = datos.get('productos', [])
        
        print()
        print("🎯 MUESTRA DE PRODUCTOS FINALES:")
        print("-" * 40)
        
        # Mostrar primeros 5 productos completos
        productos_completos = [p for p in productos[:50] 
                             if 'codigo' in p and 'descripcion' in p and ('precio' in p or 'precios' in p)]
        
        for i, producto in enumerate(productos_completos[:5]):
            print(f"Producto {i+1}:")
            for clave, valor in producto.items():
                if clave == 'precios' and isinstance(valor, list):
                    print(f"  {clave}: {valor[0]} (+ {len(valor)-1} más)")
                elif isinstance(valor, str) and len(valor) > 50:
                    print(f"  {clave}: {valor[:50]}...")
                else:
                    print(f"  {clave}: {valor}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error al mostrar muestra: {e}")


def main():
    if crear_version_final_limpia():
        mostrar_muestra_final()
        print("\n🎉 ¡Proceso completado con éxito!")
        print("📁 Archivo final: datos_ferreteria_limpio_final.json")


if __name__ == "__main__":
    main()
