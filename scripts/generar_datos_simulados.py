"""Genera datos SIMULADOS de EnCicla (Medellín) y del clima para practicar el diagnóstico de calidad.

IMPORTANTE: estos datos NO son reales. Se inventan con una semilla fija (siempre salen iguales) y
se les introducen a propósito problemas de calidad para poder diagnosticarlos:

viajes_encicla_simulado.csv
    - 40 filas completamente duplicadas
    - 25 duraciones <= 0 y 20 duraciones mayores a 180 minutos
    - 60 estaciones de origen vacías
    - 15 valores "sin dato" en Hora_Inicio
clima_medellin_simulado.csv
    - ~3 % de Tipo_Clima vacío y ~4 % escrito de otras formas ("LLUVIOSO", "lluvioso ")
    - 20 temperaturas con el valor centinela 99.9
    - 150 temperaturas vacías
    - 48 horas sin registro (un vacío de dos días)

Uso, desde la raíz del proyecto y con el entorno .venv activo:
    python scripts/generar_datos_simulados.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
rng = np.random.default_rng(SEMILLA)

DESTINO = Path(__file__).resolve().parent.parent / "data" / "raw"
DESTINO.mkdir(parents=True, exist_ok=True)

# Estaciones de EnCicla (reemplázalas por tu lista si quieres otras)
ESTACIONES = [
    "Universidad", "Suramericana", "Estadio", "Floresta",
    "Universidad de Antioquia", "Hospital Infantil Concejo de Medellín",
]
PESO_ESTACION = np.array([0.25, 0.20, 0.18, 0.15, 0.14, 0.08])

# ── Clima por hora (92 días: agosto a octubre de 2026) ────────────────────────
horas = pd.date_range("2026-08-01 00:00", "2026-10-31 23:00", freq="h")
h = horas.hour.to_numpy()

p_lluvia = 0.10 + 0.25 * ((h >= 13) & (h <= 18))
p_nublado = np.full(len(h), 0.30)
u = rng.random(len(h))
clima = np.where(u < p_lluvia, "Lluvioso", np.where(u < p_lluvia + p_nublado, "Nublado", "Soleado"))

temp = 20.5 + 5.5 * np.sin((h - 9) * np.pi / 12) + rng.normal(0, 1.2, len(h))
temp = temp - np.where(clima == "Lluvioso", 2.5, 0)
temp = temp.round(1)

df_clima = pd.DataFrame({"Fecha_Hora": horas.strftime("%Y-%m-%d %H:%M:%S"),
                        "Tipo_Clima": clima, "Temperatura_C": temp})

# Viajes: demanda con horas pico, fines de semana y lluvia 
perfil = np.array([2, 1, 1, 1, 3, 10, 30, 42, 28, 16, 12, 13,
                16, 15, 14, 16, 22, 38, 44, 26, 14, 9, 5, 3], dtype=float)
factor_dia = np.where(horas.day_of_week >= 5, 0.6, 1.0)
factor_clima = np.where(clima == "Lluvioso", 0.55, np.where(clima == "Nublado", 0.9, 1.0))
lam = perfil[h] * factor_dia * factor_clima * 0.8
n_por_hora = rng.poisson(lam)

hora_base = np.repeat(horas.to_numpy(), n_por_hora)
minutos = rng.integers(0, 60, len(hora_base))
inicio = pd.to_datetime(hora_base) + pd.to_timedelta(minutos, unit="m")
n = len(inicio)

origen = rng.choice(ESTACIONES, n, p=PESO_ESTACION)
destino = rng.choice(ESTACIONES, n, p=PESO_ESTACION)
duracion = np.clip(rng.lognormal(mean=2.5, sigma=0.5, size=n), 2, 90).round(0).astype(int)

viajes = pd.DataFrame({
    "ID_Viaje": [f"V{i:06d}" for i in range(1, n + 1)],
    "Estacion_Origen": origen,
    "Estacion_Destino": destino,
    "Hora_Inicio": inicio.strftime("%Y-%m-%d %H:%M:%S"),
    "Duracion_Viaje_Minutos": duracion,
})

#  Problemas de calidad introducidos a proposito
def indices(k, total):
    return rng.choice(total, size=k, replace=False)


viajes.loc[indices(25, n), "Duracion_Viaje_Minutos"] = rng.choice([0, -3, -1], 25)
viajes.loc[indices(20, n), "Duracion_Viaje_Minutos"] = rng.integers(240, 1440, 20)
viajes.loc[indices(60, n), "Estacion_Origen"] = np.nan
viajes.loc[indices(15, n), "Hora_Inicio"] = "sin dato"
viajes = pd.concat([viajes, viajes.sample(40, random_state=SEMILLA)], ignore_index=True)

m = len(df_clima)
df_clima.loc[indices(int(m * 0.03), m), "Tipo_Clima"] = np.nan
variantes = indices(int(m * 0.04), m)
df_clima.loc[variantes, "Tipo_Clima"] = rng.choice(["LLUVIOSO", "lluvioso ", "soleado", "NUBLADO"], len(variantes))
df_clima.loc[indices(20, m), "Temperatura_C"] = 99.9
df_clima.loc[indices(150, m), "Temperatura_C"] = np.nan
df_clima = df_clima.drop(index=range(1000, 1048)).reset_index(drop=True)

viajes.to_csv(DESTINO / "viajes_encicla_simulado.csv", index=False)
df_clima.to_csv(DESTINO / "clima_medellin_simulado.csv", index=False)

print(f"viajes_encicla_simulado.csv: {viajes.shape[0]:,} filas × {viajes.shape[1]} columnas")
print(f"clima_medellin_simulado.csv: {df_clima.shape[0]:,} filas × {df_clima.shape[1]} columnas")
print(f"Guardados en {DESTINO}")