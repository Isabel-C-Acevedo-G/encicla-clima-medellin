# Informe técnico: diagnóstico de calidad de datos · EnCicla Medellín

**Aprendiz:** Isabel Cristina Acevedo Guirales · **Ficha:** 3169901
**Instructor:** Carlos Enrique Navia Torres
**Actividad:** GA1-220501094-01-AA1-EV06
**Fecha:** 4 de noviembre de 2026

> **Nota importante:** los datasets de este proyecto son **simulados**. No existen datos públicos de EnCicla viaje por viaje, así que se generaron con el script `scripts/generar_datos_simulados.py`. Ese script introduce **a propósito** varios problemas de calidad (duplicados, nulos, valores imposibles) para poder practicar el diagnóstico. Los resultados sirven para aprender la técnica, no para sacar conclusiones sobre el sistema real.

## 1. Nombre del proyecto y pregunta analítica

**Proyecto:** análisis del uso de las bicicletas públicas EnCicla en Medellín según las condiciones climáticas y las horas pico.

**Pregunta analítica:** ¿Cómo nos afectan las condiciones climáticas los días de la semana durante las horas pico en la ciudad de Medellín?

**Tipo de análisis:** descriptivo y diagnóstico.

## 2. Descripción de los datasets utilizados

| Dataset | Fuente | Qué contiene | Relación con la pregunta |
| --- | --- | --- | --- |
| viajes (`viajes_encicla_simulado.csv`) | Simulado con `scripts/generar_datos_simulados.py` | 21.806 viajes del 1 de agosto al 31 de octubre de 2026: ID, estación de origen y destino, hora de inicio y duración | Permite sacar la hora y el día de cada viaje para identificar horas pico y demanda por día |
| clima (`clima_medellin_simulado.csv`) | Simulado con `scripts/generar_datos_simulados.py` | 2.160 registros por hora: tipo de clima y temperatura | Aporta las condiciones climáticas para cruzarlas con los viajes por fecha y hora |

## 3. Resultados de la inspección estructural

Se aplicaron `head()`, `tail()`, `shape`, `columns`, `dtypes`, `info()` y `describe()` (ver `notebooks/diagnostico_calidad.ipynb`).

| Dataset | Filas | Columnas | Tipos de datos | Observaciones |
| --- | --- | --- | --- | --- |
| viajes | 21.806 | 5 | texto: 4, entero: 1 | 60 valores nulos; 40 filas duplicadas |
| clima | 2.160 | 3 | texto: 2, decimal: 1 | 211 valores nulos; 0 filas duplicadas |

- **viajes:** `ID_Viaje`, `Estacion_Origen`, `Estacion_Destino` y `Hora_Inicio` son texto; solo `Duracion_Viaje_Minutos` es numérica (promedio de 14,5 min). Hay 6 estaciones y los viajes cubren los 7 días de la semana y las 24 horas del día; el 53,7 % (11.709) ocurre en las horas pico definidas (6, 7, 8, 17, 18 y 19).
- **clima:** `Fecha_Hora` y `Tipo_Clima` son texto; `Temperatura_C` es decimal (promedio de 20,9 °C).
- Los dos archivos **no comparten columnas**, así que para unirlos hay que construir una llave con la fecha y la hora.

## 4. Valores faltantes, tipos de datos y posibles inconsistencias

- **Valores faltantes:** en viajes, `Estacion_Origen` tiene 60 vacíos (0,28 %) y `Hora_Inicio` tiene 15 valores "sin dato" que Pandas no cuenta como nulos. En clima, `Temperatura_C` tiene 149 vacíos (6,9 %) y `Tipo_Clima` tiene 62 (2,87 %).
- **Tipos de datos:** `Hora_Inicio` y `Fecha_Hora` están guardadas como texto y deberían ser fechas.
- **Posibles inconsistencias:** 40 filas duplicadas (con `ID_Viaje` repetido); 45 duraciones fuera de 1–180 minutos (mínimo -3 y máximo 1.439); 20 temperaturas de 99,9 °C, fuera de 5–40 °C; `Tipo_Clima` escrito de 7 formas para solo 3 climas (por ejemplo `Lluvioso`, `LLUVIOSO` y `lluvioso `); 48 horas sin registro de clima (del 11 de septiembre a las 16:00 al 13 de septiembre a las 15:00); y 4.033 viajes con la misma estación de origen y destino, que puede ser normal pero conviene revisar.

## 5. Principales hallazgos de calidad por dataset

| Dataset | Problema identificado | Evidencia encontrada | Posible impacto | Acción propuesta |
| --- | --- | --- | --- | --- |
| viajes | Valores faltantes en `Estacion_Origen` | 60 vacíos (0,28 %) | Reduce los registros utilizables | Decidir si se eliminan o se dejan según su importancia |
| viajes | Nulos escondidos en `Hora_Inicio` | 15 valores "sin dato" | Pandas no los cuenta como nulos | Convertirlos a vacío con `replace()` |
| viajes | `Hora_Inicio` no es de tipo fecha | Tipo `str` | No se pueden extraer hora ni día de la semana | Convertir con `pd.to_datetime` y crear columnas de hora y día |
| viajes | Filas duplicadas | 40 de 21.806 | Infla el conteo de viajes | Eliminar con `drop_duplicates()` |
| viajes | `ID_Viaje` repetido | 40 filas con id ya visto | Un viaje contado más de una vez | Conservar un solo registro |
| viajes | Duraciones fuera de rango | 45 viajes fuera de 1–180 min | Sesgan el promedio | Definir y documentar un criterio de exclusión |
| clima | Valores faltantes | `Temperatura_C` 149 (6,9 %); `Tipo_Clima` 62 (2,87 %) | Menos datos para comparar por clima | Decidir si se eliminan, se imputan o se dejan |
| clima | Temperaturas fuera de rango | 20 valores de 99,9 °C | Alteran el análisis por clima | Tratarlos como vacíos |
| clima | Categorías de `Tipo_Clima` inconsistentes | 7 valores distintos pero 3 reales | Separa grupos que son iguales | Normalizar con `str.strip().str.lower()` |
| clima | Horas sin registro | 48 horas faltantes | No se puede asignar clima a esos viajes | Buscar otra fuente o excluir esos viajes |
| clima | `Fecha_Hora` guardada como texto | Tipo `str` | No se puede cruzar con los viajes | Convertir con `pd.to_datetime` |

## 6. Acciones de limpieza y preparación propuestas

1. Convertir `Hora_Inicio` y `Fecha_Hora` a tipo fecha y crear columnas de hora y día de la semana.
2. Eliminar las 40 filas duplicadas.
3. Normalizar `Tipo_Clima` (minúsculas y sin espacios) para dejar tres categorías.
4. Reemplazar los 99,9 °C y los "sin dato" por valores vacíos, y decidir cómo tratar los vacíos.
5. Revisar las duraciones fuera de 1–180 minutos y definir un criterio de exclusión.
6. Redondear la hora de cada viaje a la hora completa y unirlo con el clima.
7. Buscar otra fuente para las 48 horas sin clima o excluir esos viajes.

## 7. Conclusiones sobre las condiciones actuales de los datos

Los datos permiten continuar con el proyecto, pero solo después de una limpieza previa. Cubren los 7 días de la semana y las 24 horas, con más de la mitad de los viajes en horas pico, que es lo que necesita la pregunta analítica. Las limitaciones principales son que viajes y clima están en archivos separados sin columnas comunes, que las fechas están como texto y que al clima le faltan 48 horas. Además, como los datos son simulados y los problemas se introdujeron a propósito, los hallazgos sirven para practicar el diagnóstico y no describen el comportamiento real de EnCicla.
