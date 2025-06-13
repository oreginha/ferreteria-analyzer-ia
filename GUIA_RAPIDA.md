# 🚀 GUÍA RÁPIDA - Analizador de Planillas de Ferretería

## ⚡ Inicio Rápido

### 1. **Obtener API Key de Gemini**

- Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
- Inicia sesión con tu cuenta Google
- Crea una nueva API Key
- Copia la clave generada

### 2. **Ejecutar la Aplicación**

```bash
# Opción 1: Doble clic
ejecutar_app.bat

# Opción 2: Terminal
python ferreteria_analyzer_app.py
```

### 3. **Configuración Inicial**

1. Pega tu API Key de Gemini en el campo correspondiente
2. Haz clic en "Configurar"
3. Selecciona el directorio con tus archivos HTML (sheet001.htm, sheet002.htm, etc.)

## 🔧 Funciones Principales

### 📊 **Extracción de Datos**

- Haz clic en **"🔍 Extraer Datos"**
- La aplicación procesará automáticamente todos los archivos HTML
- Verás el progreso en tiempo real

### 🤖 **Análisis con IA**

- Haz clic en **"🤖 Analizar con IA"**
- Gemini analizará tus datos y proporcionará insights
- Ve a la pestaña "Análisis IA" para ver los resultados

### 📈 **Consultas Personalizadas**

En la pestaña "Análisis IA":

- Escribe tu pregunta en el campo "Consulta"
- Ejemplos:
  - "¿Cuáles son los productos más caros?"
  - "Compara precios entre proveedores"
  - "¿Qué productos tienen mejor margen?"

### 💾 **Exportación**

- **📊 Generar Reporte**: Crea un reporte en Markdown
- **💾 Exportar Excel**: Exporta a formato Excel
- **📈 Ver Estadísticas**: Muestra estadísticas detalladas

## 📋 **Datos que Procesa**

La aplicación puede analizar planillas que contengan:

- Listas de precios con códigos
- Inventarios con stock
- Catálogos de productos
- Datos en múltiples monedas (USD, ARS)

### Proveedores Detectados:

- **CRIMARAL** - Sistemas de riego
- **ANCAIG** - Productos químicos
- **HERRAMETAL** - Herrajes y metalurgia
- **YAYI** - Materiales de construcción
- **FERRIPLAST** - Productos plásticos
- **BABUSI** - Aceites y lubricantes
- **FERRETERIA** - Inventario general

## ⚙️ **Configuración Avanzada**

### Archivo config.ini

```ini
[gemini]
api_key = tu_api_key_aquí

[ui]
window_width = 1200
window_height = 800

[export]
default_format = xlsx
```

### Variables de Entorno

```bash
set GEMINI_API_KEY=tu_api_key_aquí
```

## 🔍 **Ejemplos de Análisis IA**

### Consultas Básicas:

- "Resume los datos por proveedor"
- "¿Cuántos productos tiene cada categoría?"
- "Muestra las tendencias de precios"

### Consultas Avanzadas:

- "Identifica productos con precios inconsistentes"
- "¿Qué proveedor tiene mejor variedad de productos?"
- "Calcula el precio promedio por categoría"
- "Encuentra productos duplicados entre proveedores"

### Consultas de Negocio:

- "¿Qué productos deberían tener mayor margen?"
- "Identifica oportunidades de negocio"
- "¿Qué productos están obsoletos?"
- "Recomienda estrategias de precios"

## 📁 **Estructura de Archivos**

```
📂 Tu Proyecto/
├── ferreteria_analyzer_app.py  # Aplicación principal
├── data_analyzer.py           # Análisis avanzado
├── requirements.txt           # Dependencias
├── config.ini               # Configuración
├── README.md                # Documentación completa
├── ejecutar_app.bat         # Ejecutar aplicación
└── 📂 datos/
    ├── sheet001.htm         # CRIMARAL
    ├── sheet002.htm         # ANCAIG
    ├── sheet003.htm         # DAFYS
    └── ...
```

## 🛠️ **Solución de Problemas**

### "API Key no válida"

- Verifica que la clave esté correctamente copiada
- Asegúrate de tener créditos en Google AI Studio
- Revisa que no haya espacios extra

### "Archivos no encontrados"

- Verifica que los archivos se llamen sheet001.htm, sheet002.htm, etc.
- Asegúrate de seleccionar el directorio correcto
- Comprueba permisos de lectura

### "Error de dependencias"

```bash
pip install --upgrade -r requirements.txt
```

## 📞 **Soporte y Consejos**

### Tips de Uso:

1. **Usa nombres descriptivos** en tus consultas IA
2. **Sé específico** con lo que buscas
3. **Experimenta** con diferentes tipos de preguntas
4. **Guarda** los reportes importantes
5. **Actualiza** tus listas de precios regularmente

### Mejores Prácticas:

- Mantén tus archivos HTML organizados
- Respalda tus datos regularmente
- Usa la función de exportación para análisis externos
- Aprovecha las consultas personalizadas para insights específicos

---

**¡Disfruta analizando tus datos con IA! 🚀**

_Para más información, consulta el README.md completo_
