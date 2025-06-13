"""
Clase PurificadorDatos - Módulo separado para purificación de datos
================================================================
"""

import json
import re
from typing import Dict, List, Any, Tuple

class PurificadorDatos:
    """Clase para purificar y estructurar datos de ferretería"""
    
    def __init__(self):
        self.stats = {
            'productos_procesados': 0,
            'productos_eliminados': 0,
            'duplicados_removidos': 0,
            'categorias_detectadas': 0
        }
    
    def purificar_datos_completos(self, datos_originales: Dict) -> Dict:
        """Purifica los datos completos de la aplicación"""
        if not datos_originales or 'hojas' not in datos_originales:
            return datos_originales
        
        datos_purificados = {
            'hojas': [],
            'resumen': datos_originales.get('resumen', {}),
            'fecha_procesamiento': datos_originales.get('fecha_procesamiento', ''),
            'estrategia_proveedores': datos_originales.get('estrategia_proveedores', 'unknown'),
            'proveedor_principal': datos_originales.get('proveedor_principal', 'No detectado')
        }
        
        productos_vistos = set()
        
        for hoja in datos_originales['hojas']:
            if 'productos' not in hoja:
                continue
            
            productos_purificados = []
            
            for producto in hoja['productos']:
                # Purificar producto individual
                producto_limpio = self._purificar_producto(producto)
                
                if producto_limpio and self._es_producto_valido(producto_limpio):
                    # Verificar duplicados
                    codigo = producto_limpio.get('codigo', '')
                    if codigo and codigo not in productos_vistos:
                        productos_purificados.append(producto_limpio)
                        productos_vistos.add(codigo)
                        self.stats['productos_procesados'] += 1
                    else:
                        self.stats['duplicados_removidos'] += 1
                else:
                    self.stats['productos_eliminados'] += 1
            
            if productos_purificados:
                hoja_purificada = {
                    'nombre': hoja.get('nombre', 'Sin nombre'),
                    'archivo': hoja.get('archivo', ''),
                    'productos': productos_purificados,
                    'total_productos': len(productos_purificados)
                }
                datos_purificados['hojas'].append(hoja_purificada)
        
        # Actualizar resumen
        total_productos = sum(len(hoja['productos']) for hoja in datos_purificados['hojas'])
        datos_purificados['resumen']['total_productos'] = total_productos
        datos_purificados['resumen']['total_hojas'] = len(datos_purificados['hojas'])
        
        self.stats['categorias_detectadas'] = len(datos_purificados['hojas'])
        
        return datos_purificados
    
    def _purificar_producto(self, producto: Dict) -> Dict:
        """Purifica un producto individual"""
        if not isinstance(producto, dict):
            return None
        
        # Extraer campos básicos
        descripcion = str(producto.get('descripcion', '')).strip()
        codigo = str(producto.get('codigo', '')).strip()
        precio = producto.get('precio', '')
        
        # Limpiar descripción
        descripcion = self._limpiar_descripcion(descripcion)
        
        # Limpiar código
        codigo = self._limpiar_codigo(codigo)
        
        # Limpiar precio
        precio = self._limpiar_precio(precio)
        
        if not descripcion or len(descripcion) < 3:
            return None
        
        producto_limpio = {
            'codigo': codigo,
            'descripcion': descripcion,
            'precio': precio,
            'categoria': producto.get('categoria', 'General'),
            'unidad': producto.get('unidad', ''),
            'stock': producto.get('stock', ''),
            'proveedor': producto.get('proveedor', '')
        }
        
        return producto_limpio
    
    def _limpiar_descripcion(self, descripcion: str) -> str:
        """Limpia y mejora la descripción del producto"""
        if not descripcion:
            return ''
        
        # Eliminar textos muy largos (probablemente instrucciones)
        if len(descripcion) > 200:
            return ''
        
        # Eliminar patrones de instrucciones comunes
        patrones_eliminar = [
            r'selecciona.*archivo.*html',
            r'exportar.*excel',
            r'click.*botón',
            r'presiona.*tecla',
            r'instrucciones.*uso',
            r'guía.*usuario',
            r'paso.*paso',
            r'tutorial.*completo'
        ]
        
        for patron in patrones_eliminar:
            if re.search(patron, descripcion.lower()):
                return ''
        
        # Limpiar caracteres especiales y espacios extra
        descripcion = re.sub(r'[^\w\s\-\.\,\(\)]', ' ', descripcion)
        descripcion = re.sub(r'\s+', ' ', descripcion)
        descripcion = descripcion.strip()
        
        return descripcion
    
    def _limpiar_codigo(self, codigo: str) -> str:
        """Limpia y valida el código del producto"""
        if not codigo:
            return ''
        
        # Limpiar caracteres especiales
        codigo = re.sub(r'[^\w\-]', '', str(codigo))
        codigo = codigo.strip()
        
        # Validar longitud mínima
        if len(codigo) < 2:
            return ''
        
        return codigo.upper()
    
    def _limpiar_precio(self, precio) -> str:
        """Limpia y formatea el precio"""
        if not precio:
            return ''
        
        precio_str = str(precio).strip()
        
        # Extraer números y puntos/comas
        precio_limpio = re.sub(r'[^\d\.\,]', '', precio_str)
        
        if not precio_limpio:
            return ''
        
        # Formatear precio
        try:
            # Convertir a float y volver a string con formato
            precio_num = float(precio_limpio.replace(',', '.'))
            return f"{precio_num:.2f}"
        except:
            return precio_limpio
    
    def _es_producto_valido(self, producto: Dict) -> bool:
        """Verifica si un producto es válido"""
        if not producto:
            return False
        
        descripcion = producto.get('descripcion', '')
        codigo = producto.get('codigo', '')
        
        # Debe tener al menos descripción o código
        if not descripcion and not codigo:
            return False
        
        # Filtrar descripciones muy cortas
        if descripcion and len(descripcion) < 3:
            return False
        
        # Filtrar descripciones que parecen instrucciones
        if descripcion:
            desc_lower = descripcion.lower()
            palabras_prohibidas = [
                'click', 'selecciona', 'exportar', 'botón', 'archivo',
                'instrucciones', 'paso', 'tutorial', 'guía', 'manual'
            ]
            
            if any(palabra in desc_lower for palabra in palabras_prohibidas):
                return False
        
        return True
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene las estadísticas de purificación"""
        return self.stats.copy()
    
    def reiniciar_estadisticas(self):
        """Reinicia las estadísticas"""
        self.stats = {
            'productos_procesados': 0,
            'productos_eliminados': 0,
            'duplicados_removidos': 0,
            'categorias_detectadas': 0
        }
