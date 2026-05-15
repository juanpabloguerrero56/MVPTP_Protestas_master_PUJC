# Multiple Vehicle Profitable Tour Problem (MVPTP)

Repositorio que contiene las instancias, resultados computacionales, scripts y archivos auxiliares utilizados en la investigación sobre el **Multiple Vehicle Profitable Tour Problem (MVPTP)** aplicado al contexto de protestas urbanas.

El repositorio incluye las instancias experimentales utilizadas en los experimentos computacionales, así como los resultados obtenidos mediante diferentes enfoques de solución y validación del modelo.

---

# Estructura del repositorio

```text
MVPTP PROTESTAS PUJ
│
├── Figuras/
│   └── Figuras utilizadas en el documento de tesis
│
├── Instancias/
│   └── Archivos .dat de las instancias experimentales
│
├── Logs/
│   ├── Logs greedy V2/
│   ├── Logs Modelo/
│   └── Logs_SIN_PI/
│
├── Resultados/
│   ├── Resultados Greedy V2/
│   ├── Resultados_Modelo/
│   └── Resultados_SIN_PI/
│
└── Scripts/
    └── Generador/

```

Descripción de carpetas
Figuras/
Contiene las figuras e imágenes utilizadas en el documento de tesis.

Instancias/
Contiene las instancias experimentales del problema en formato .dat.

La nomenclatura de las instancias sigue el formato:
MVPTP_CALI_n_i.dat
Donde:

n representa el tamaño o configuración de la instancia.
i identifica la réplica correspondiente.

Ejemplo: MVPTP_CALI_8_1.dat


Logs/
Contiene los archivos de salida (.txt) generados durante la ejecución de los experimentos computacionales.

Logs greedy V2/
Registros de ejecución del algoritmo heurístico Greedy V2.

Logs Modelo/
Registros de ejecución del modelo matemático principal.

Logs_SIN_PI/
Registros asociados a la versión ajustada del modelo utilizada en el capítulo de validación.
En esta variante, la función objetivo no considera cobertura ponderada, sino cobertura basada únicamente en el número de nodos cubiertos.

Resultados/
Contiene los resultados consolidados de los experimentos computacionales en formato .csv.

Resultados Greedy V2/
Resultados obtenidos mediante el algoritmo Greedy V2.

Resultados_Modelo/
Resultados obtenidos mediante el modelo matemático principal.

Resultados_SIN_PI/
Resultados obtenidos con la variante del modelo utilizada para validación, basada en cobertura de nodos no ponderada.

Scripts/
Contiene scripts auxiliares utilizados en la investigación.

Generador/
Script en Python utilizado para la generación de instancias experimentales.


Objetivo del repositorio

El objetivo de este repositorio es facilitar la reproducibilidad de los experimentos computacionales desarrollados en la investigación, así como servir como material de apoyo para futuros trabajos relacionados con el Multiple Vehicle Profitable Tour Problem (MVPTP).

Autor

Juan Pablo
Pontificia Universidad Javeriana
2026