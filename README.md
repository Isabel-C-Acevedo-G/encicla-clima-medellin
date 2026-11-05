# Diagnóstico de calidad de datos · EnCicla Medellín

**Aprendiz: Isabel Cristina Acevedo Guirales · Ficha: 3169901
**Programa: Tecnólogo en Análisis y Desarrollo de Software · SENA
Instructor: Carlos Enrique Navia Torres
Actividad: EV06 – Diagnosticar la calidad de datos: preparación, exploración y documentación

## Descripción

Proyecto de ciencia de datos sobre el uso de las bicicletas públicas EnCicla en Medellín y su relación con las condiciones climáticas y las horas pico. Este repositorio contiene el diagnóstico inicial de calidad de los datasets del proyecto, hecho con Python y Pandas, antes de cualquier limpieza o análisis.

Los datos son simulados. No se encontraron datos públicos de EnCicla viaje por viaje, así que se generan con un script que además introduce problemas de calidad a propósito para practicar el diagnóstico. Los resultados no describen el comportamiento real del sistema.

## Propósito

Identificar en qué momentos y bajo qué condiciones el sistema se satura o se queda sin bicicletas disponibles, para que la unidad de movilidad pueda planificar mejor la distribución de las bicicletas antes de las horas pico. Esta etapa verifica si los datos están en condiciones de responder esa pregunta.

## Pregunta analítica

¿Cómo nos afectan las condiciones climáticas los días de la semana durante las horas pico en la ciudad de Medellín?

Tipo de análisis: descriptivo y diagnóstico.

 Datasets utilizados

| Dataset | Archivo en `data/raw/` | Fuente | Descripción |
| --- | --- | --- | --- |
| viajes | `viajes_encicla_simulado.csv` | Simulado con `scripts/generar_datos_simulados.py` | 21.806 viajes del 1 de agosto al 31 de octubre de 2026: ID, estación de origen y destino, hora de inicio y duración |
| clima | `clima_medellin_simulado.csv` | Simulado con `scripts/generar_datos_simulados.py` | 2.160 registros por hora: tipo de clima y temperatura |

Cómo obtener los datos

Los archivos de datos no se publican en este repositorio (se generan con un script). Para crearlos, con el entorno ya instalado (ver abajo):

bash
python scripts/generar_datos_simulados.py
```

El script usa una semilla fija, así que siempre genera los mismos archivos en `data/raw/`.

 Estructura 

encicla-clima-medellin/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   └── raw/                      
├── scripts/
│   └── generar_datos_simulados.py
├── notebooks/
│   └── diagnostico_calidad.ipynb
└── reports/
    ├── informe_diagnostico.md
    └── hallazgos_calidad.csv


Cómo reproducir el diagnóstico

Requiere Python 3.11 o superior y Git. Los comandos son para Git Bash (en macOS o Linux, la terminal normal).

bash
git clone https://github.com/Isabel-C-Acevedo-G/encicla-clima-medellin.git
cd encicla-clima-medellin

python -m venv .venv
source .venv/Scripts/activate    
python -m pip install -r requirements.txt

python scripts/generar_datos_simulados.py
```

1. Abre `notebooks/diagnostico_calidad.ipynb` en VS Code y elige el kernel .venv.
2. Revisa las celdas de configuración (`DATASETS` y `COLUMNAS`) y ejecuta Run All.
3. El notebook genera `reports/hallazgos_calidad.csv`; el informe completo está en `reports/informe_diagnostico.md`.

Resultados

El diagnóstico encontró 11 problemas de calidad: valores faltantes (incluidos "sin dato"), fechas guardadas como texto, 40 viajes duplicados, 45 duraciones fuera de rango, 20 temperaturas imposibles, el clima escrito de 7 formas para 3 categorías y 48 horas sin registro de clima. Los datos cubren los 7 días de la semana y las 24 horas, por lo que permiten continuar con el proyecto después de una limpieza. El detalle está en [`reports/informe_diagnostico.md`](reports/informe_diagnostico.md).
