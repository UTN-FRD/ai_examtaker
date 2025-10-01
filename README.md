# Examtaker AI

**Generador y evaluador de exámenes con inteligencia artificial usando Google Gemini**

## Descripción General

Examtaker AI es un sistema inteligente que genera exámenes personalizados basados en temas específicos y evalúa automáticamente las respuestas de los estudiantes utilizando tecnología de inteligencia artificial avanzada. El sistema proporciona retroalimentación detallada y puntuación basada en rúbricas predefinidas.

## Requisitos Previos

- Python 3.8 o superior
- Poetry (herramienta de gestión de dependencias de Python)

## Instalación

### 1. Instalar Poetry

Si no tienes Poetry instalado, instálalo usando pip:

```bash
pip install poetry
```

### 2. Instalar Dependencias

Instala todos los paquetes requeridos usando Poetry:

```bash
poetry install
```

### 3. Configuración de la Clave API

Para usar el servicio de Google Gemini AI, necesitas obtener una clave API:

1. Visita la [página de claves API de Google AI Studio](https://aistudio.google.com/api-keys)
2. Genera una nueva clave API
3. Crea un archivo `.env` en el directorio raíz del proyecto
4. Agrega tu clave API al archivo `.env`:

```
GOOGLE_API_KEY=tu_clave_api_aqui
```

## Uso

### Ejecutar la Aplicación

Ejecuta la aplicación principal usando Poetry:

```bash
poetry run python main.py
```

### Flujo de Trabajo

1. **Entrada del Tema**: El sistema te pedirá que ingreses un tema para la generación del examen
2. **Generación del Examen**: La IA creará un examen personalizado basado en el tema especificado
3. **Sesión de Examen**: Completa las preguntas del examen generado
4. **Evaluación Automática**: El sistema evalúa tus respuestas usando las rúbricas definidas en `exam_rubrics.json`

### Archivos de Salida

La aplicación genera los siguientes archivos:

- **Sesión de Examen**: `exam_session_{timestamp}.json` - Contiene el examen generado y tus respuestas
- **Resultados de Evaluación**: `exam_correction_{timestamp}.json` - Contiene retroalimentación detallada, correcciones y puntuaciones para cada pregunta

La puntuación final también se mostrará en la terminal al completar el proceso de evaluación.

## Estructura del Proyecto

```
Examtaker/
├── core/               # Funcionalidad del adaptador de IA principal
├── labs/               # Lógica de generación de exámenes
├── models/             # Modelos y estructuras de datos
├── settings/           # Gestión de configuración
├── exam_rubrics.json   # Rúbricas de evaluación
└── main.py            # Punto de entrada de la aplicación
```