#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para purificar datos JSON de ferretería
Elimina información irrelevante y mantiene solo datos esenciales de productos
"""

import json
import re
from datetime import datetime
import sys


class PurificadorDatos:
    def __init__(self):
        self.patrones_irrelevantes = [
            r'BUSCADOR RAPIDO',
            r'distribuidora.*@.*\.com',
            r'Precios orientativos pueden sufrir variaciones',
            r'CALCULADORA.*',
            r'COMPLETAR DONDE DICE',
            r'FUNCIONAMIENTO',
            r'INGRESAR.*CENTIMETROS',
            r'MARGEN DE GANANCIA',
            r'POR DEFECTO VIENE',
            r'Recuerde que \d+ metro',
            r'UwU',
            r'AQU VER LA DESCRIPCIN',
            r'CODIGO.*DESCRIPCION.*BASE',
            r'^\.$',  # Solo puntos
            r'^-$',   # Solo guiones
            r'^\+$',  # Solo más
            r'^$',    # Vacíos
            r'OFERTAS',
            r'FECHA',
            r'% GANANCIA',
            r'PUBLICO',
            r'CODIGO DE FABRICA',
            r'SIN IVA.*',
            r'COSTO FINAL'
        ]
        
        self.patron_codigo = re.compile(r'^[0-9]{6,8}$')
        self.patron_precio = re.compile(r'[\$\s]*[\d\.,]+')
        self.patron_medida = re.compile(r'\d+/\d+|\d+x\d+|\d+mm|\d+cm|\d+"')
        
    def es_texto_irrelevante(self, texto):
        """Determina si un texto es irrelevante y debe ser eliminado"""
        if not texto or texto.strip() == '':
            return True
            
        texto = str(texto).strip()
        
        # Verificar patrones irrelevantes
        for patron in self.patrones_irrelevantes:
            if re.search(patron, texto, re.IGNORECASE):
                return True
                
        # Si tiene más de 100 caracteres y contiene instrucciones, probablemente sea irrelevante
        if len(texto) > 100 and any(palabra in texto.lower() for palabra in 
                                   ['ingresar', 'completar', 'funcionamiento', 'recuerde', 'defecto']):
            return True
            
        return False
    
    def clasificar_campo(self, valor):
        """Clasifica un campo según su contenido"""
        valor_str = str(valor).strip()
        
        if not valor_str or valor_str == '':
            return None
            
        # Código de producto
        if self.patron_codigo.match(valor_str):
            return {'tipo': 'codigo', 'valor': valor_str}
            
        # Precio
        if self.patron_precio.match(valor_str) and any(char in valor_str for char in ['$', ',']):
            # Limpiar y normalizar precio
            precio_limpio = re.sub(r'[^\d,.]', '', valor_str)
            return {'tipo': 'precio', 'valor': precio_limpio}
            
        # Medida
        if self.patron_medida.search(valor_str):
            return {'tipo': 'medida', 'valor': valor_str}
            
        # IVA o porcentaje
        if re.search(r'\d+%?$', valor_str) and len(valor_str) <= 3:
            return {'tipo': 'iva', 'valor': valor_str}
            
        # Descripción (si no es irrelevante y tiene longitud razonable)
        if not self.es_texto_irrelevante(valor_str) and 3 <= len(valor_str) <= 80:
            return {'tipo': 'descripcion', 'valor': valor_str}
            
        return None
    
    def procesar_fila(self, fila):
        """Procesa una fila de datos y extrae información relevante"""
        producto = {}
        campos_clasificados = []
        
        for valor in fila:
            clasificacion = self.clasificar_campo(valor)
            if clasificacion:
                campos_clasificados.append(clasificacion)
        
        # Organizar campos por tipo
        for campo in campos_clasificados:
            tipo = campo['tipo']
            valor = campo['valor']
            
            if tipo == 'codigo':
                producto['codigo'] = valor
            elif tipo == 'precio':
                if 'precios' not in producto:
                    producto['precios'] = []
                producto['precios'].append(valor)
            elif tipo == 'descripcion':
                if 'descripcion' not in producto:
                    producto['descripcion'] = valor
                elif len(valor) > len(producto.get('descripcion', '')):
                    producto['descripcion'] = valor  # Usar la descripción más larga
            elif tipo == 'medida':
                producto['medida'] = valor
            elif tipo == 'iva':
                producto['iva'] = valor
        
        # Solo devolver productos que tengan al menos código o descripción
        if 'codigo' in producto or 'descripcion' in producto:
            return producto
        return None
    
    def purificar_json(self, archivo_entrada, archivo_salida=None):
        """Purifica el archivo JSON eliminando información irrelevante"""
        print(f"🔄 Cargando datos de: {archivo_entrada}")
        
        try:
            with open(archivo_entrada, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            print(f"❌ Error al cargar el archivo: {e}")
            return False
        
        print("🧹 Purificando datos...")
        
        productos_purificados = []
        total_filas_procesadas = 0
        total_productos_validos = 0
        
        # Procesar cada hoja
        for hoja in datos.get('hojas', []):
            nombre_hoja = hoja.get('hoja', 'Sin nombre')
            print(f"  📄 Procesando hoja: {nombre_hoja}")
            
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', []):
                    total_filas_procesadas += 1
                    producto = self.procesar_fila(fila)
                    
                    if producto:
                        producto['hoja'] = nombre_hoja
                        producto['proveedor'] = datos.get('proveedor_principal', 'YAYI')
                        productos_purificados.append(producto)
                        total_productos_validos += 1
        
        # Crear estructura de datos purificada
        datos_purificados = {
            'metadata': {
                'planilla_original': datos.get('planilla', ''),
                'proveedor': datos.get('proveedor_principal', 'YAYI'),
                'fecha_purificacion': datetime.now().isoformat(),
                'total_productos': total_productos_validos,
                'total_filas_procesadas': total_filas_procesadas,
                'eficiencia_purificacion': f"{(total_productos_validos/total_filas_procesadas*100):.1f}%" if total_filas_procesadas > 0 else "0%"
            },
            'productos': productos_purificados
        }
        
        # Guardar archivo purificado
        if archivo_salida is None:
            archivo_salida = archivo_entrada.replace('.json', '_purificado.json')
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(datos_purificados, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Datos purificados guardados en: {archivo_salida}")
            print(f"📊 Estadísticas:")
            print(f"   • Filas procesadas: {total_filas_procesadas:,}")
            print(f"   • Productos válidos extraídos: {total_productos_validos:,}")
            print(f"   • Eficiencia de purificación: {datos_purificados['metadata']['eficiencia_purificacion']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")
            return False
    
    def mostrar_muestra(self, archivo_purificado, cantidad=5):
        """Muestra una muestra de los datos purificados"""
        try:
            with open(archivo_purificado, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            productos = datos.get('productos', [])
            print(f"\n📋 Muestra de {min(cantidad, len(productos))} productos purificados:")
            print("-" * 80)
            
            for i, producto in enumerate(productos[:cantidad]):
                print(f"Producto {i+1}:")
                for clave, valor in producto.items():
                    print(f"  {clave}: {valor}")
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error al mostrar muestra: {e}")


def main():
    purificador = PurificadorDatos()
    
    # Archivo de entrada
    archivo_entrada = "datos_extraidos_app.json"
    archivo_salida = "datos_purificados.json"
    
    print("🧽 PURIFICADOR DE DATOS DE FERRETERÍA")
    print("=" * 50)
    
    # Purificar datos
    if purificador.purificar_json(archivo_entrada, archivo_salida):
        # Mostrar muestra
        purificador.mostrar_muestra(archivo_salida)
        print(f"\n🎯 ¡Proceso completado! Archivo purificado: {archivo_salida}")
    else:
        print("❌ Error en el proceso de purificación")
        sys.exit(1)


if __name__ == "__main__":
    main()
