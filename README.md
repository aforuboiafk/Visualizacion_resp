# Evolución y Resiliencia de la Conectividad Aérea en Chile

**Proyecto de Visualización de Datos (EIN092B)**  
Universidad Técnica Federico Santa María  
*Avance 2: Análisis Exploratorio de Datos (EDA) y Aplicación Interactiva*


## Integrantes
- Alejandra Zamora
- Yamandú Lettieri


## Problemática y Pregunta de Investigación

El mapa de conectividad aérea ha experimentado reconfiguraciones críticas tras los periodos de disrupción operativa y fluctuaciones macroeconómicas. Actualmente, el flujo de pasajeros enfrenta etapas de estabilización y contracción de oferta en rutas secundarias. 

* **Pregunta de investigación:** ¿Cómo ha evolucionado el flujo de pasajeros en Chile y cuáles rutas constituyen los nodos más estables y resilientes del sistema frente a fluctuaciones de demanda?


## Alcance y Variables del Proyecto

- **Foco analítico:** Movilidad humana comercial (pasajeros de pago). Se excluyen vuelos militares, vuelos cancelados y operaciones exclusivas de carga.
- **Cobertura geográfica:** Conexiones aéreas con origen o destino en aeropuertos de Chile (tráfico nacional e internacional).
- **Cobertura temporal ($T$):** Serie mensual continua de enero de 2022 a mediados de 2026.
- **Fenómeno objetivo ($Y$):** Flujo mensual de pasajeros por ruta (`PASAJEROS`).
- **Variables explicativas y contextuales ($X$):** Distancia ortodrómica de vuelo (`Distancia`), tipo de tráfico (`NAC`), operador/aerolínea (`Operador`), par origen-destino (`ORIG_1_N`, `DEST_1_N`) y métricas de capacidad de flota (`ASK`, `RPK`, `horas_vuelo`).


## Datos y Calidad de la Información

La información proviene de la **Junta de Aeronáutica Civil (JAC)** a través del Portal de Datos Abiertos del Estado:

1. **Tráfico Aéreo Mensual (2022–2026):** ~24.000 observaciones a nivel de ruta mensual (`Mes + Operador + Origen → Destino`).
2. **KPIs de Oferta y Demanda de Flota:** Métricas agregadas mensuales a nivel de operador (`Mes + Código OACI + Tipo de Tráfico`).

### Decisiones Principales de Preparación
* **Depuración de no comerciales:** Filtrado estricto de registros con `PASAJEROS > 0`, eliminando vuelos cancelados, técnicos o sin demanda de pago.
* **Resolución de granularidad:** Desacople del dataset en dos productos limpios para evitar duplicaciones artificiales de métricas de flota en rutas individuales.
* **Homologación de identificadores:** Creación de la llave temporal unificada `month_id` (`YYYYMM`) y mapeo de nombres comerciales de aerolíneas a códigos estándar internacionales OACI de 3 letras (`LAN`, `SKU`, `JAT`, `AAL`, etc.).



## Estructura de la Aplicación en Streamlit

La aplicación interactiva está organizada en tres páginas con propósitos complementarios:

1. **Contexto y Datos (`app.py`):** Presentación del problema, alcance, definición de variables ($X$, $Y$, $T$) y auditoría de calidad de datos.
2. **Análisis Exploratorio (`pages/1_EDA.py`):** Exploración de distribuciones (boxplot comparativo nacional vs. internacional), ranking de destinos y análisis multivariado (dispersión distancia vs. flujo y matriz de correlación).
3. **Análisis de Resiliencia (`pages/2_Analisis.py`):** Cuadrantes de resiliencia mediante el cruce de volumen promedio mensual vs. Coeficiente de Variación ($CV$), evolución temporal multianual y capacidad de flota de las aerolíneas.

---

## Estructura del Repositorio

.
├── data/
│   ├── raw/                        # Datasets originales de la JAC sin modificar
│   │   ├── TraficoAereoMensual2022-2026.csv
│   │   └── kpi_oferta_demanda.csv
│   └── processed/                  # Datos limpios y homologados generados
│       ├── datos_limpios.csv       # Base a nivel de ruta mensual (~19.900 reg.)
│       └── datos_aerolinea_kpi.csv # Base agregada de capacidad por operador
├── notebooks/
│   └── 01_exploracion.ipynb       # Pipeline de limpieza, homologación OACI y EDA
├── pages/
│   ├── 1_EDA.py                   # Página 2: Análisis Exploratorio
│   └── 2_Analisis.py              # Página 3: Matriz de Resiliencia y Flota
├── app.py                         # Página principal de Streamlit (Contexto)
├── requirements.txt               # Dependencias del entorno
├── README.md                      # Documentación del proyecto
└── .gitignore                     # Archivos excluidos de control de versiones