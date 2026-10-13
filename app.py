import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Contexto y Datos - Conectividad Aérea",
    layout="wide"
)

# -----------------------------
# Carga y preparación inicial
# -----------------------------
df = pd.read_csv("data/processed/datos_limpios.csv")

df["PASAJEROS"] = pd.to_numeric(df["PASAJEROS"], errors="coerce").fillna(0)
df["Distancia"] = pd.to_numeric(df["Distancia"], errors="coerce").fillna(0)
df["periodo"] = pd.to_datetime(dict(year=df["Ano"], month=df["Mes"], day=1))

# -----------------------------
# 1. TÍTULO Y CONTEXTO INICIAL
# -----------------------------
st.title("Evolución y Resiliencia de la Conectividad Aérea")
st.caption("Contexto institucional, formulación del problema y auditoría de datos.")

st.subheader("1. Problemática")
st.write(
    "Tras la crisis sanitaria y contingencias operativas recientes en Chile (como huelgas en terminales "
    "y fluctuaciones de demanda), la red de transporte aéreo experimentó una reconfiguración drástica. "
    "Frente a este escenario, resulta crítico identificar qué rutas demuestran resiliencia sostenida para "
    "anticipar requerimientos de inversión y planificación en infraestructura aeroportuaria."
)

st.subheader("2. Pregunta de investigación")
st.success(
    "¿Cómo ha evolucionado el flujo de pasajeros y cuáles rutas son los nodos más estables actualmente (2022–2026)?"
)

st.subheader("3. Alcance del proyecto")
st.markdown(
    """
    * **Foco:** Movilidad humana regular de pasajeros.
    * **Cobertura espacial:** Vuelos comerciales con origen o destino en Chile (rutas nacionales e internacionales).
    * **Contexto temporal:** Periodo 2022 a 2026.
    * **Exclusiones:** Transporte de carga comercial pura y operaciones militares.
    """
)

st.divider()

# -----------------------------
# 2. MARCO METODOLÓGICO: Y, X y T
# -----------------------------
st.header("Marco Metodológico de Variables")

col_y, col_x, col_t = st.columns(3)

with col_y:
    st.markdown("### $Y$: Variable Objetivo")
    st.markdown("**`PASAJEROS`**")
    st.write("Flujo mensual agregado de pasajeros transportados por aerolínea en una ruta específica.")

with col_x:
    st.markdown("### $X$: Variables Explicativas")
    st.markdown("**`Operador`, `ORIG_1_N`, `DEST_1_N`, `Distancia`, `NAC`**")
    st.write("Variables espaciales y de mercado que caracterizan la competencia, los pares de conexión y el tipo de tráfico.")

with col_t:
    st.markdown("### $T$: Dimensión Temporal")
    st.markdown("**`Ano`, `Mes`, `periodo`**")
    st.write("Ciclos mensuales multianuales (2022–2026) para evaluar la recuperación post-crisis y la estacionalidad.")

st.divider()

# -----------------------------
# 3. DIMENSIÓN DEL DATASET
# -----------------------------
st.header("Resumen General de los Datos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Registros Observados", f"{len(df):,}")

with col2:
    st.metric("Pasajeros Totales", f"{df['PASAJEROS'].sum():,.0f}")

with col3:
    st.metric("Operadores Activos", df["Operador"].nunique())

with col4:
    total_rutas = df[["ORIG_1", "DEST_1"]].drop_duplicates().shape[0]
    st.metric("Rutas Únicas", total_rutas)

st.caption(
    f"Fuente: Junta de Aeronáutica Civil (JAC). Cobertura mensual desde "
    f"{df['periodo'].min().strftime('%m/%Y')} hasta {df['periodo'].max().strftime('%m/%Y')}."
)

st.divider()

# -----------------------------
# 4. CALIDAD Y AUDITORÍA DE DATOS
# -----------------------------
st.header("Calidad y Estructura de los Datos")

nulos_total = int(df.isna().sum().sum())
porcentaje_nulos = (nulos_total / df.size) * 100

calidad = pd.DataFrame({
    "Dimensión de Auditoría": [
        "Total de observaciones",
        "Variables en el dataset",
        "Filas duplicadas",
        "Celdas con valores nulos",
        "Tasa de datos nulos",
        "Periodos mensuales registrados"
    ],
    "Resultado": [
        f"{len(df):,}",
        len(df.columns),
        int(df.duplicated().sum()),
        f"{nulos_total:,}",
        f"{porcentaje_nulos:.2f}%",
        df["periodo"].nunique()
    ]
})

st.dataframe(calidad, hide_index=True, use_container_width=True)

with st.expander("Ver decisiones de preparación y limpieza aplicadas"):
    st.markdown(
        """
        * **Filtrado de actividad:** Se conservaron únicamente registros comerciales con flujo de pasajeros mayor a cero.
        * **Consistencia temporal:** Se sintetizó la variable `periodo` a partir de `Ano` y `Mes` para facilitar análisis de series de tiempo.
        * **Tipificación:** Se aseguraron tipos numéricos en variables de demanda, distancia y capacidad liberada (`PASAJEROS`, `Distancia`, etc.).
        * **Desacople de métricas:** Los indicadores agregados de flota (ASK, RPK) se procesaron de forma modular para evitar duplicidad a nivel de ruta.
        """
    )

with st.expander("Ver muestra de registros procesados"):
    st.dataframe(df.head(15), use_container_width=True)