# 🔧 Analizador de Planillas de Ferretería con IA

Una aplicación de escritorio para extraer, analizar y procesar datos de planillas de ferretería usando Inteligencia Artificial con Google Gemini.

## ✨ Características

- **📊 Extracción automática de datos** desde archivos HTML exportados de Excel
- **🤖 Análisis inteligente** usando Google Gemini AI
- **📈 Estadísticas detalladas** y visualización de datos
- **💾 Exportación múltiple** (Excel, JSON, Markdown)
- **🔍 Consultas personalizadas** a la IA sobre tus datos
- **📋 Interfaz gráfica intuitiva** desarrollada en Tkinter

## 🚀 Instalación Rápida

### Opción 1: Instalador Automático (Windows)

```bash
# Ejecuta el instalador
install.bat
```

### Opción 2: Instalación Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
python ferreteria_analyzer_app.py
```

## 📋 Requisitos

- **Python 3.8+**
- **API Key de Google Gemini** ([Obtener aquí](https://makersuite.google.com/app/apikey))
- **Archivos HTML** exportados desde Excel

### Dependencias principales:

- `tkinter` (incluido con Python)
- `beautifulsoup4` - Parsing HTML
- `google-generativeai` - API de Gemini
- `pandas` - Manipulación de datos
- `openpyxl` - Exportación Excel

## 🎯 Cómo usar

### 1. Configuración inicial

1. Ejecuta la aplicación: `python ferreteria_analyzer_app.py`
2. Ingresa tu API Key de Google Gemini
3. Selecciona el directorio con tus archivos HTML

### 2. Extracción de datos

1. Haz clic en **"🔍 Extraer Datos"**
2. La aplicación procesará automáticamente todos los archivos sheet\*.htm
3. Verás el progreso en tiempo real

### 3. Análisis con IA

1. Haz clic en **"🤖 Analizar con IA"**
2. Gemini analizará tus datos y proporcionará insights
3. Realiza consultas personalizadas en la pestaña "Análisis IA"

### 4. Exportación y reportes

- **📊 Generar Reporte**: Crea un reporte en Markdown
- **💾 Exportar Excel**: Exporta datos a formato Excel
- **📈 Ver Estadísticas**: Muestra estadísticas detalladas

## 📁 Estructura de archivos

```
📂 Proyecto/
├── ferreteria_analyzer_app.py  # Aplicación principal
├── requirements.txt            # Dependencias
├── config.ini                 # Configuración
├── install.bat                # Instalador Windows
├── README.md                  # Este archivo
└── 📂 datos/
    ├── sheet001.htm           # Archivos HTML de Excel
    ├── sheet002.htm
    └── ...
```

## 🔧 Configuración avanzada

### Archivo config.ini

```ini
[gemini]
api_key = tu_api_key_aquí

[ui]
theme = clam
window_width = 1200
window_height = 800

[export]
default_format = xlsx
max_rows_per_sheet = 10000
```

### Variables de entorno

```bash
# Alternativamente, puedes usar variables de entorno
set GEMINI_API_KEY=tu_api_key_aquí
```

## 📊 Tipos de datos soportados

La aplicación puede procesar planillas que contengan:

- **Listas de precios** con códigos y descripciones
- **Inventarios** con stock y costos
- **Catálogos** de productos por proveedor
- **Datos financieros** con precios en múltiples monedas

### Proveedores detectados automáticamente:

- CRIMARAL (sistemas de riego)
- ANCAIG (productos químicos)
- HERRAMETAL (herrajes y metalurgia)
- YAYI (materiales de construcción)
- FERRIPLAST (productos plásticos)
- BABUSI (aceites y lubricantes)
- Y más...

## 🤖 Capacidades de IA

La integración con Gemini permite:

- **Análisis de tendencias** de precios
- **Detección de oportunidades** de negocio
- **Comparación de proveedores**
- **Identificación de productos** más/menos rentables
- **Recomendaciones personalizadas**
- **Consultas en lenguaje natural**

### Ejemplos de consultas:

- "¿Cuáles son los productos más caros por categoría?"
- "Compara los precios entre CRIMARAL y HERRAMETAL"
- "¿Qué productos tienen mejor margen de ganancia?"
- "Identifica productos duplicados entre proveedores"

## 📈 Características técnicas

### Extracción de datos:

- **Parsing HTML** robusto con BeautifulSoup
- **Limpieza automática** de datos
- **Detección inteligente** de encabezados
- **Manejo de errores** y archivos corruptos

### Análisis:

- **Procesamiento** de más de 30,000 productos
- **Estadísticas en tiempo real**
- **Múltiples formatos** de exportación
- **Visualización** de datos estructurados

### Interfaz:

- **Multipestañas** para organización
- **Progreso en tiempo real**
- **Logs detallados** de operaciones
- **Responsive design**

## 🛠️ Solución de problemas

### Error: "API Key no válida"

1. Verifica tu API Key en [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Asegúrate de que esté correctamente copiada
3. Revisa que tengas créditos disponibles

### Error: "Archivos no encontrados"

1. Verifica que los archivos estén nombrados como sheet001.htm, sheet002.htm, etc.
2. Asegúrate de seleccionar el directorio correcto
3. Comprueba permisos de lectura en los archivos

### Error: "Dependencias faltantes"

```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 📄 Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo según tus necesidades.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras bugs o tienes ideas de mejora:

1. Reporta issues detalladamente
2. Propón nuevas características
3. Comparte tus modificaciones

## 📞 Soporte

Para soporte técnico o consultas:

- Revisa la documentación completa
- Consulta los logs de la aplicación
- Verifica la configuración de API

---

**¡Disfruta analizando tus datos de ferretería con IA! 🚀**
