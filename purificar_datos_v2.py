#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para purificar datos JSON de ferretería
Elimina información irrelevante y estructura mejor los datos
"""

import json
import re
from datetime import datetime


class PurificadorMejorado:
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
            r'ESCRIBA AQUI MISMO UN CODIGO',
            r'DIAMETRO DEL CAO',
            r'^DESCRIPCION$',
            r'^YAYI$',
            r'^Gs\s*-$',
            r'^\.$',
            r'^-$',
            r'^\+$',
            r'^$',
            r'OFERTAS',
            r'FECHA',
            r'% GANANCIA',
            r'PUBLICO',
            r'CODIGO DE FABRICA',
            r'SIN IVA.*',
            r'COSTO FINAL',
            r'BASE',
            r'CON OFERTAS'
        ]
        
        self.patron_codigo = re.compile(r'^[0-9]{6,8}$')
        self.patron_precio = re.compile(r'^[\$\s]*[\d\.,]+$')
        self.patron_medida = re.compile(r'^\d+/\d+$|^\d+x\d+$|^\d+mm$|^\d+cm$|^\d+"$')
        self.patron_iva = re.compile(r'^\d{1,2}$')
        
    def es_texto_irrelevante(self, texto):
        """Determina si un texto es irrelevante y debe ser eliminado"""
        if not texto or texto.strip() == '':
            return True
            
        texto = str(texto).strip()
        
        # Verificar patrones irrelevantes
        for patron in self.patrones_irrelevantes:
            if re.search(patron, texto, re.IGNORECASE):
                return True
                
        # Si tiene más de 100 caracteres y contiene instrucciones
        if len(texto) > 100 and any(palabra in texto.lower() for palabra in 
                                   ['ingresar', 'completar', 'funcionamiento', 'recuerde', 'defecto']):
            return True
        
        # Si es muy corto y no parece útil
        if len(texto) <= 2 and texto not in ['MM', 'CM', 'M', 'L', 'XL']:
            return True
            
        return False
    
    def normalizar_precio(self, precio_str):
        """Normaliza un precio eliminando caracteres innecesarios"""
        precio_limpio = re.sub(r'[^\d,.]', '', str(precio_str))
        if precio_limpio and precio_limpio not in ['0', '0,00', '0.00']:
            return precio_limpio
        return None
    
    def clasificar_campo(self, valor):
        """Clasifica un campo según su contenido"""
        valor_str = str(valor).strip()
        
        if not valor_str or valor_str == '':
            return None
            
        # Código de producto (6-8 dígitos)
        if self.patron_codigo.match(valor_str):
            return {'tipo': 'codigo', 'valor': valor_str}
            
        # IVA (1-2 dígitos)
        if self.patron_iva.match(valor_str) and int(valor_str) <= 50:
            return {'tipo': 'iva', 'valor': valor_str}
            
        # Precio (contiene números y separadores)
        precio_normalizado = self.normalizar_precio(valor_str)
        if precio_normalizado:
            return {'tipo': 'precio', 'valor': precio_normalizado}
            
        # Medida específica
        if self.patron_medida.match(valor_str):
            return {'tipo': 'medida', 'valor': valor_str}
            
        # Descripción (texto útil)
        if not self.es_texto_irrelevante(valor_str) and 3 <= len(valor_str) <= 80:
            # Limpiar descripción
            descripcion_limpia = re.sub(r'\s+', ' ', valor_str).strip()
            if descripcion_limpia and len(descripcion_limpia) >= 3:
                return {'tipo': 'descripcion', 'valor': descripcion_limpia}
            
        return None
    
    def procesar_fila(self, fila):
        """Procesa una fila de datos y extrae información relevante"""
        campos_clasificados = []
        
        for valor in fila:
            clasificacion = self.clasificar_campo(valor)
            if clasificacion:
                campos_clasificados.append(clasificacion)
        
        # Si no hay campos relevantes, descartar
        if not campos_clasificados:
            return None
            
        # Organizar producto
        producto = {}
        precios_encontrados = []
        
        for campo in campos_clasificados:
            tipo = campo['tipo']
            valor = campo['valor']
            
            if tipo == 'codigo':
                producto['codigo'] = valor
            elif tipo == 'precio':
                precios_encontrados.append(valor)
            elif tipo == 'descripcion':
                # Solo usar la descripción más larga y específica
                if 'descripcion' not in producto or len(valor) > len(producto['descripcion']):
                    producto['descripcion'] = valor
            elif tipo == 'medida':
                producto['medida'] = valor
            elif tipo == 'iva':
                producto['iva'] = int(valor)
        
        # Agregar precios si hay
        if precios_encontrados:
            # Filtrar precios duplicados y ordenar
            precios_unicos = []
            for precio in precios_encontrados:
                if precio not in precios_unicos:
                    precios_unicos.append(precio)
            
            if len(precios_unicos) == 1:
                producto['precio'] = precios_unicos[0]
            else:
                producto['precios'] = precios_unicos
        
        # Solo devolver productos que tengan código Y descripción, O descripción muy específica
        tiene_codigo = 'codigo' in producto
        tiene_descripcion = 'descripcion' in producto
        descripcion_especifica = tiene_descripcion and len(producto['descripcion']) > 10
        
        if (tiene_codigo and tiene_descripcion) or descripcion_especifica:
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
        productos_por_hoja = {}
        
        # Procesar cada hoja
        for hoja in datos.get('hojas', []):
            nombre_hoja = hoja.get('hoja', 'Sin nombre')
            print(f"  📄 Procesando hoja: {nombre_hoja}")
            productos_hoja = 0
            
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', []):
                    total_filas_procesadas += 1
                    producto = self.procesar_fila(fila)
                    
                    if producto:
                        producto['hoja'] = nombre_hoja
                        producto['proveedor'] = datos.get('proveedor_principal', 'YAYI')
                        productos_purificados.append(producto)
                        productos_hoja += 1
            
            productos_por_hoja[nombre_hoja] = productos_hoja
        
        # Crear estructura mejorada
        datos_purificados = {
            'metadata': {
                'planilla_original': datos.get('planilla', ''),
                'proveedor': datos.get('proveedor_principal', 'YAYI'),
                'fecha_purificacion': datetime.now().isoformat(),
                'total_productos': len(productos_purificados),
                'total_filas_procesadas': total_filas_procesadas,
                'eficiencia_purificacion': f"{(len(productos_purificados)/total_filas_procesadas*100):.1f}%" if total_filas_procesadas > 0 else "0%",
                'productos_por_hoja': productos_por_hoja
            },
            'estadisticas': {
                'productos_con_codigo': sum(1 for p in productos_purificados if 'codigo' in p),
                'productos_con_precio': sum(1 for p in productos_purificados if 'precio' in p or 'precios' in p),
                'productos_con_medida': sum(1 for p in productos_purificados if 'medida' in p),
                'productos_con_iva': sum(1 for p in productos_purificados if 'iva' in p)
            },
            'productos': productos_purificados
        }
        
        # Guardar archivo purificado
        if archivo_salida is None:
            archivo_salida = archivo_entrada.replace('.json', '_purificado_v2.json')
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(datos_purificados, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Datos purificados guardados en: {archivo_salida}")
            print(f"📊 Estadísticas finales:")
            print(f"   • Filas procesadas: {total_filas_procesadas:,}")
            print(f"   • Productos válidos extraídos: {len(productos_purificados):,}")
            print(f"   • Eficiencia: {datos_purificados['metadata']['eficiencia_purificacion']}")
            print(f"   • Con código: {datos_purificados['estadisticas']['productos_con_codigo']:,}")
            print(f"   • Con precio: {datos_purificados['estadisticas']['productos_con_precio']:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")
            return False


def main():
    purificador = PurificadorMejorado()
    
    archivo_entrada = "datos_extraidos_app.json"
    archivo_salida = "datos_purificados_v2.json"
    
    print("🧽 PURIFICADOR MEJORADO DE DATOS DE FERRETERÍA")
    print("=" * 60)
    
    if purificador.purificar_json(archivo_entrada, archivo_salida):
        print(f"\n🎯 ¡Proceso completado! Archivo purificado: {archivo_salida}")
    else:
        print("❌ Error en el proceso de purificación")


if __name__ == "__main__":
    main()
