#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALIZADOR INTELIGENTE DE DATOS ESTRUCTURADOS
==============================================
Analiza el JSON de datos estructurados para identificar automáticamente:
- Proveedores, productos, precios, marcas, fechas, cantidades, etc.
- Mantiene las relaciones entre datos
- Genera análisis contextual para IA
"""

import json
import re
from datetime import datetime
from collections import defaultdict, Counter
import os

class AnalizadorDatosInteligente:
    def __init__(self):
        self.patrones_datos = {
            'precios': [
                r'\$\s*[\d,]+\.?\d*',  # $1,234.56
                r'[\d,]+\.?\d*\s*\$',  # 1,234.56 $
                r'ARS\s*[\d,]+\.?\d*', # ARS 1234
                r'USD\s*[\d,]+\.?\d*', # USD 1234
                r'[\d,]+\.?\d*\s*(ARS|USD|PESOS?|DOLARES?)',
                r'PRECIO[\s:]*[\d,]+\.?\d*',
                r'COST[O|E][\s:]*[\d,]+\.?\d*'
            ],
            'cantidades': [
                r'STOCK[\s:]*\d+',
                r'CANTIDAD[\s:]*\d+',
                r'QTY[\s:]*\d+',
                r'UNIDADES[\s:]*\d+',
                r'\d+\s*(UND|UNIT|PCS|KG|GR|LT|ML)',
                r'x\s*\d+'  # x 5, x 10
            ],
            'fechas': [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{2,4}[-/]\d{1,2}[-/]\d{1,2}',
                r'(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)',
                r'(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)',
                r'FECHA[\s:]*\d',
                r'\d{4}'  # Años
            ],
            'codigos_productos': [
                r'COD[\s:]*[A-Z0-9\-]+',
                r'SKU[\s:]*[A-Z0-9\-]+',
                r'REF[\s:]*[A-Z0-9\-]+',
                r'ART[\s:]*[A-Z0-9\-]+',
                r'[A-Z]{2,}\d{3,}',  # ABC123
                r'\d{3,}[A-Z]{2,}'   # 123ABC
            ],
            'marcas': [
                r'MARCA[\s:]*[A-Z][A-Za-z\s]+',
                r'BRAND[\s:]*[A-Z][A-Za-z\s]+',
                # Marcas conocidas de ferretería
                r'\b(STANLEY|DEWALT|MAKITA|BOSCH|BLACK\s*DECKER|TRUPER|BAHCO|IRWIN|MILWAUKEE)\b'
            ],
            'categorias': [
                r'CATEGORIA[\s:]*[A-Z][A-Za-z\s]+',
                r'TIPO[\s:]*[A-Z][A-Za-z\s]+',
                # Categorías típicas de ferretería
                r'\b(HERRAMIENTAS?|TORNILLOS?|TUERCAS?|CLAVOS?|PINTURA|ELECTRICIDAD|PLOMERIA|CONSTRUCCION)\b'
            ]
        }
        
        self.proveedores_conocidos = [
            'STANLEY', 'HERRAMETALSA', 'YAYI', 'PUMA', 'FERRIPLAST', 
            'CRIMARAL', 'ANCAIG', 'BABUSI', 'FERRETERIA', 'DAFYS'
        ]
        
    def analizar_datos_estructurados(self, ruta_json):
        """Analiza el JSON de datos estructurados"""
        if not os.path.exists(ruta_json):
            return None
            
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        analisis = {
            'resumen_general': self._analizar_estructura_general(datos),
            'proveedores_identificados': self._analizar_proveedores(datos),
            'productos_analizados': self._analizar_productos(datos),
            'precios_detectados': self._analizar_precios(datos),
            'relaciones_datos': self._mapear_relaciones(datos),
            'estadisticas_inteligentes': self._generar_estadisticas(datos),
            'recomendaciones_ia': self._generar_recomendaciones(datos)
        }
        
        return analisis
    
    def _analizar_estructura_general(self, datos):
        """Analiza la estructura general de los datos"""
        return {
            'planilla': datos.get('planilla', 'Sin nombre'),
            'fecha_extraccion': datos.get('fecha_extraccion', ''),
            'total_hojas': datos.get('total_hojas', 0),
            'estrategia_proveedores': datos.get('estrategia_proveedores', 'No detectada'),
            'proveedor_principal': datos.get('proveedor_principal', 'No identificado'),
            'total_registros': self._contar_registros_totales(datos)
        }
    
    def _analizar_proveedores(self, datos):
        """Identifica y analiza proveedores"""
        proveedores = {}
        
        for hoja in datos.get('hojas', []):
            nombre_hoja = hoja.get('hoja', '')
            
            # Identificar proveedor principal de la hoja
            proveedor_detectado = None
            for proveedor in self.proveedores_conocidos:
                if proveedor.upper() in nombre_hoja.upper():
                    proveedor_detectado = proveedor
                    break
            
            if not proveedor_detectado:
                proveedor_detectado = nombre_hoja.split('_')[0] if '_' in nombre_hoja else nombre_hoja
            
            # Analizar datos del proveedor
            total_productos = sum(tabla.get('total_filas', 0) for tabla in hoja.get('tablas', []))
            
            if proveedor_detectado not in proveedores:
                proveedores[proveedor_detectado] = {
                    'nombre': proveedor_detectado,
                    'hojas': [],
                    'total_productos': 0,
                    'productos_muestra': [],
                    'precios_detectados': [],
                    'categorias_identificadas': set()
                }
            
            proveedores[proveedor_detectado]['hojas'].append(nombre_hoja)
            proveedores[proveedor_detectado]['total_productos'] += total_productos
            
            # Analizar muestra de productos
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', [])[:5]:  # Primeras 5 filas
                    producto_info = self._analizar_fila_producto(fila)
                    if producto_info:
                        proveedores[proveedor_detectado]['productos_muestra'].append(producto_info)
                        
                        if producto_info.get('precio'):
                            proveedores[proveedor_detectado]['precios_detectados'].append(producto_info['precio'])
                        
                        if producto_info.get('categoria'):
                            proveedores[proveedor_detectado]['categorias_identificadas'].add(producto_info['categoria'])
        
        # Convertir sets a listas para JSON
        for proveedor in proveedores.values():
            proveedor['categorias_identificadas'] = list(proveedor['categorias_identificadas'])
        
        return proveedores
    
    def _analizar_productos(self, datos):
        """Analiza productos identificando campos específicos"""
        productos_analizados = []
        
        for hoja in datos.get('hojas', []):
            proveedor = hoja.get('hoja', '')
            
            for tabla in hoja.get('tablas', []):
                encabezados = self._detectar_encabezados(tabla.get('filas', []))
                
                for i, fila in enumerate(tabla.get('filas', [])):
                    if i == 0 and encabezados:  # Saltar encabezados
                        continue
                    
                    producto = self._analizar_fila_producto(fila, encabezados)
                    if producto:
                        producto['proveedor'] = proveedor
                        producto['hoja_origen'] = hoja.get('hoja', '')
                        producto['tabla_indice'] = tabla.get('tabla_indice', 0)
                        productos_analizados.append(producto)
                    
                    # Limitar para performance
                    if len(productos_analizados) >= 50:
                        break
                
                if len(productos_analizados) >= 50:
                    break
        
        return productos_analizados
    
    def _analizar_fila_producto(self, fila, encabezados=None):
        """Analiza una fila individual para extraer información del producto"""
        if not fila or not any(str(celda).strip() for celda in fila):
            return None
        
        producto = {
            'datos_raw': fila[:10],  # Primeras 10 columnas
            'codigo': None,
            'descripcion': None,
            'precio': None,
            'cantidad': None,
            'marca': None,
            'categoria': None,
            'fecha': None
        }
        
        fila_texto = ' '.join(str(celda) for celda in fila if celda)
        
        # Detectar diferentes tipos de datos
        for i, celda in enumerate(fila):
            celda_str = str(celda).strip().upper()
            
            if not celda_str:
                continue
            
            # Detectar precios
            for patron in self.patrones_datos['precios']:
                if re.search(patron, celda_str, re.IGNORECASE):
                    producto['precio'] = celda_str
                    break
            
            # Detectar códigos
            for patron in self.patrones_datos['codigos_productos']:
                if re.search(patron, celda_str):
                    producto['codigo'] = celda_str
                    break
            
            # Detectar cantidades
            for patron in self.patrones_datos['cantidades']:
                if re.search(patron, celda_str, re.IGNORECASE):
                    producto['cantidad'] = celda_str
                    break
            
            # Detectar fechas
            for patron in self.patrones_datos['fechas']:
                if re.search(patron, celda_str, re.IGNORECASE):
                    producto['fecha'] = celda_str
                    break
            
            # Detectar marcas
            for patron in self.patrones_datos['marcas']:
                if re.search(patron, celda_str, re.IGNORECASE):
                    producto['marca'] = celda_str
                    break
            
            # Detectar categorías
            for patron in self.patrones_datos['categorias']:
                if re.search(patron, celda_str, re.IGNORECASE):
                    producto['categoria'] = celda_str
                    break
            
            # La celda más larga probablemente sea la descripción
            if not producto['descripcion'] and len(celda_str) > 10:
                producto['descripcion'] = celda_str
        
        return producto if any(producto[k] for k in ['codigo', 'descripcion', 'precio']) else None
    
    def _detectar_encabezados(self, filas):
        """Detecta si la primera fila contiene encabezados"""
        if not filas:
            return False
        
        primera_fila = filas[0]
        encabezados_keywords = [
            'CODIGO', 'COD', 'SKU', 'DESCRIPCION', 'DESC', 'PRODUCTO',
            'PRECIO', 'PRICE', 'COST', 'VALOR', 'CANTIDAD', 'QTY', 
            'STOCK', 'MARCA', 'BRAND', 'CATEGORIA', 'TIPO'
        ]
        
        for celda in primera_fila:
            celda_str = str(celda).strip().upper()
            for keyword in encabezados_keywords:
                if keyword in celda_str:
                    return True
        
        return False
    
    def _analizar_precios(self, datos):
        """Analiza precios detectados"""
        precios_info = {
            'monedas_detectadas': set(),
            'rangos_precios': {},
            'precios_promedio': {},
            'total_precios_encontrados': 0
        }
        
        todos_los_precios = []
        
        for hoja in datos.get('hojas', []):
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', []):
                    fila_texto = ' '.join(str(celda) for celda in fila if celda)
                    
                    for patron in self.patrones_datos['precios']:
                        matches = re.findall(patron, fila_texto, re.IGNORECASE)
                        for match in matches:
                            precios_info['total_precios_encontrados'] += 1
                            todos_los_precios.append(match)
                            
                            # Detectar moneda
                            if 'USD' in match.upper() or '$' in match:
                                precios_info['monedas_detectadas'].add('USD')
                            elif 'ARS' in match.upper() or 'PESO' in match.upper():
                                precios_info['monedas_detectadas'].add('ARS')
        
        precios_info['monedas_detectadas'] = list(precios_info['monedas_detectadas'])
        precios_info['muestra_precios'] = todos_los_precios[:10]
        
        return precios_info
    
    def _mapear_relaciones(self, datos):
        """Mapea las relaciones entre diferentes tipos de datos"""
        relaciones = {
            'proveedor_productos': {},
            'producto_precio': {},
            'marca_productos': {},
            'categoria_productos': {}
        }
        
        for hoja in datos.get('hojas', []):
            proveedor = hoja.get('hoja', '')
            productos_proveedor = []
            
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', []):
                    producto_info = self._analizar_fila_producto(fila)
                    if producto_info:
                        productos_proveedor.append(producto_info)
            
            relaciones['proveedor_productos'][proveedor] = len(productos_proveedor)
        
        return relaciones
    
    def _generar_estadisticas(self, datos):
        """Genera estadísticas inteligentes"""
        stats = {
            'distribucion_productos_por_proveedor': {},
            'tipos_datos_detectados': {},
            'calidad_datos': 0,
            'completitud_informacion': {}
        }
        
        total_productos = 0
        total_con_precios = 0
        total_con_codigos = 0
        
        for hoja in datos.get('hojas', []):
            proveedor = hoja.get('hoja', '')
            productos_hoja = sum(tabla.get('total_filas', 0) for tabla in hoja.get('tablas', []))
            total_productos += productos_hoja
            
            stats['distribucion_productos_por_proveedor'][proveedor] = productos_hoja
            
            # Analizar calidad de datos
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', [])[:10]:  # Muestra
                    producto = self._analizar_fila_producto(fila)
                    if producto:
                        if producto.get('precio'):
                            total_con_precios += 1
                        if producto.get('codigo'):
                            total_con_codigos += 1
        
        if total_productos > 0:
            stats['calidad_datos'] = (total_con_precios + total_con_codigos) / (total_productos * 2) * 100
            stats['completitud_informacion'] = {
                'productos_con_precio': (total_con_precios / total_productos * 100) if total_productos > 0 else 0,
                'productos_con_codigo': (total_con_codigos / total_productos * 100) if total_productos > 0 else 0
            }
        
        return stats
    
    def _generar_recomendaciones(self, datos):
        """Genera recomendaciones basadas en el análisis"""
        recomendaciones = []
        
        # Analizar estructura de datos
        total_hojas = len(datos.get('hojas', []))
        hojas_con_datos = len([h for h in datos.get('hojas', []) if h.get('total_tablas', 0) > 0])
        
        if total_hojas - hojas_con_datos > 0:
            recomendaciones.append(f"Se detectaron {total_hojas - hojas_con_datos} hojas vacías que podrían eliminarse")
        
        # Analizar consistencia de proveedores
        estrategia = datos.get('estrategia_proveedores', '')
        if estrategia == 'single_provider':
            recomendaciones.append("Se detectó un solo proveedor con múltiples listas. Considera consolidar para mejor gestión")
        elif estrategia == 'multiple_providers':
            recomendaciones.append("Se detectaron múltiples proveedores. Útil para análisis comparativo de precios")
        
        # Recomendaciones de calidad de datos
        recomendaciones.append("Revisar consistencia en formato de precios entre proveedores")
        recomendaciones.append("Considerar estandarizar códigos de productos para mejor trazabilidad")
        
        return recomendaciones
    
    def _contar_registros_totales(self, datos):
        """Cuenta el total de registros en todos los datos"""
        total = 0
        for hoja in datos.get('hojas', []):
            for tabla in hoja.get('tablas', []):
                total += tabla.get('total_filas', 0)
        return total
    
    def generar_resumen_para_ia(self, analisis):
        """Genera un resumen estructurado para enviar a la IA"""
        if not analisis:
            return "No se pudo realizar el análisis de datos estructurados"
        
        resumen = []
        
        # Información general
        general = analisis['resumen_general']
        resumen.append("=== ANÁLISIS INTELIGENTE DE DATOS ESTRUCTURADOS ===")
        resumen.append(f"PLANILLA: {general['planilla']}")
        resumen.append(f"ESTRATEGIA DETECTADA: {general['estrategia_proveedores']}")
        resumen.append(f"TOTAL REGISTROS: {general['total_registros']:,}")
        resumen.append("")
        
        # Proveedores identificados
        proveedores = analisis['proveedores_identificados']
        resumen.append("=== PROVEEDORES IDENTIFICADOS ===")
        for nombre, info in proveedores.items():
            resumen.append(f"{nombre}:")
            resumen.append(f"  • Productos: {info['total_productos']:,}")
            resumen.append(f"  • Hojas: {len(info['hojas'])}")
            if info['categorias_identificadas']:
                resumen.append(f"  • Categorías: {', '.join(info['categorias_identificadas'])}")
            if info['precios_detectados']:
                resumen.append(f"  • Precios detectados: {len(info['precios_detectados'])}")
        resumen.append("")
        
        # Muestra de productos analizados
        productos = analisis['productos_analizados']
        resumen.append("=== MUESTRA DE PRODUCTOS ANALIZADOS ===")
        for i, producto in enumerate(productos[:5], 1):
            resumen.append(f"Producto {i}:")
            resumen.append(f"  • Proveedor: {producto.get('proveedor', 'N/A')}")
            resumen.append(f"  • Descripción: {producto.get('descripcion', 'N/A')}")
            resumen.append(f"  • Código: {producto.get('codigo', 'N/A')}")
            resumen.append(f"  • Precio: {producto.get('precio', 'N/A')}")
            resumen.append(f"  • Marca: {producto.get('marca', 'N/A')}")
            resumen.append(f"  • Cantidad: {producto.get('cantidad', 'N/A')}")
        resumen.append("")
        
        # Análisis de precios
        precios = analisis['precios_detectados']
        resumen.append("=== ANÁLISIS DE PRECIOS ===")
        resumen.append(f"Total precios encontrados: {precios['total_precios_encontrados']}")
        resumen.append(f"Monedas detectadas: {', '.join(precios['monedas_detectadas'])}")
        if precios['muestra_precios']:
            resumen.append(f"Muestra de precios: {', '.join(precios['muestra_precios'][:5])}")
        resumen.append("")
        
        # Estadísticas y calidad
        stats = analisis['estadisticas_inteligentes']
        resumen.append("=== ESTADÍSTICAS DE CALIDAD ===")
        resumen.append(f"Calidad general de datos: {stats['calidad_datos']:.1f}%")
        if 'completitud_informacion' in stats:
            comp = stats['completitud_informacion']
            resumen.append(f"Productos con precio: {comp['productos_con_precio']:.1f}%")
            resumen.append(f"Productos con código: {comp['productos_con_codigo']:.1f}%")
        resumen.append("")
        
        # Recomendaciones
        recomendaciones = analisis['recomendaciones_ia']
        resumen.append("=== RECOMENDACIONES ===")
        for rec in recomendaciones:
            resumen.append(f"• {rec}")
        
        return "\n".join(resumen)

def main():
    """Función de prueba"""
    analizador = AnalizadorDatosInteligente()
    
    archivo_datos = "datos_estructurados.json"
    if os.path.exists(archivo_datos):
        print("🔍 Analizando datos estructurados...")
        analisis = analizador.analizar_datos_estructurados(archivo_datos)
        
        if analisis:
            # Guardar análisis completo
            with open("analisis_inteligente_datos.json", 'w', encoding='utf-8') as f:
                json.dump(analisis, f, ensure_ascii=False, indent=2, default=str)
            
            # Generar resumen para IA
            resumen_ia = analizador.generar_resumen_para_ia(analisis)
            
            with open("resumen_analisis_para_ia.txt", 'w', encoding='utf-8') as f:
                f.write(resumen_ia)
            
            print("✅ Análisis completado")
            print(f"📊 Total proveedores: {len(analisis['proveedores_identificados'])}")
            print(f"📦 Total productos analizados: {len(analisis['productos_analizados'])}")
            print(f"💰 Precios detectados: {analisis['precios_detectados']['total_precios_encontrados']}")
            
            print("\n📄 Archivos generados:")
            print("• analisis_inteligente_datos.json - Análisis completo")
            print("• resumen_analisis_para_ia.txt - Resumen para IA")
        else:
            print("❌ No se pudo realizar el análisis")
    else:
        print(f"❌ No se encontró {archivo_datos}")

if __name__ == "__main__":
    main()
