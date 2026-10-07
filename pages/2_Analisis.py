import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Análisis de la Pregunta",
    layout="wide"
)

st.title("Análisis de la Pregunta de Investigación")

st.write(
    "Esta página conecta el EDA con la pregunta: "
    "¿Cómo ha evolucionado el flujo de pasajeros y cuáles rutas "
    "son los nodos más estables actualmente?"
)

df = pd.read_csv(
    "data/processed/datos_limpios.csv"
)

df["PASAJEROS"] = pd.to_numeric(
    df["PASAJEROS"],
    errors="coerce"
).fillna(0)

df["periodo"] = pd.to_datetime(
    dict(
        year=df["Ano"],
        month=df["Mes"],
        day=1
    )
)

df["ruta"] = (
    df["ORIG_1_N"].astype(str)
    + " → "
    + df["DEST_1_N"].astype(str)
)

operadores = sorted(
    df["Operador"].dropna().unique()
)

operadores_seleccionados = st.sidebar.multiselect(
    "Operadores",
    operadores,
    default=operadores
)

df_filtrado = df[
    df["Operador"].isin(operadores_seleccionados)
].copy()

if df_filtrado.empty:
    st.warning("No existen datos para los operadores seleccionados.")
    st.stop()

# Evolución general
st.subheader("Evolución mensual del flujo de pasajeros")

evolucion = (
    df_filtrado
    .groupby("periodo", as_index=False)
    .agg(
        pasajeros=("PASAJEROS", "sum")
    )
)

fig_evolucion = px.line(
    evolucion,
    x="periodo",
    y="pasajeros",
    markers=True,
    title="Flujo mensual total de pasajeros",
    labels={
        "periodo": "Mes",
        "pasajeros": "Pasajeros"
    }
)

st.plotly_chart(
    fig_evolucion,
    use_container_width=True
)

maximo = evolucion.loc[
    evolucion["pasajeros"].idxmax()
]

minimo = evolucion.loc[
    evolucion["pasajeros"].idxmin()
]

st.info(
    f"El mayor flujo observado ocurre en "
    f"{maximo['periodo'].strftime('%B de %Y')}, con "
    f"{maximo['pasajeros']:,.0f} pasajeros. "
    f"El menor flujo ocurre en "
    f"{minimo['periodo'].strftime('%B de %Y')}."
)

st.divider()

# Rutas principales
st.subheader("Rutas con mayor flujo acumulado")

rutas = (
    df_filtrado
    .groupby(
        ["ruta", "ORIG_1_N", "DEST_1_N"],
        as_index=False
    )
    .agg(
        pasajeros=("PASAJEROS", "sum"),
        meses_activos=("periodo", "nunique")
    )
    .sort_values(
        "pasajeros",
        ascending=False
    )
    .head(15)
)

fig_rutas = px.bar(
    rutas.sort_values(
        "pasajeros",
        ascending=True
    ),
    x="pasajeros",
    y="ruta",
    orientation="h",
    color="pasajeros",
    title="Top 15 rutas por pasajeros acumulados",
    labels={
        "ruta": "Ruta",
        "pasajeros": "Pasajeros"
    },
    color_continuous_scale="Blues"
)

st.plotly_chart(
    fig_rutas,
    use_container_width=True
)

st.divider()

# Estabilidad de rutas
st.subheader("Estabilidad de las rutas")

st.write(
    "Para esta exploración preliminar, una ruta estable se define como "
    "una ruta activa durante varios meses y con poca variación mensual "
    "en su flujo de pasajeros."
)

ruta_mes = (
    df_filtrado
    .groupby(
        ["ruta", "periodo"],
        as_index=False
    )
    .agg(
        pasajeros=("PASAJEROS", "sum")
    )
)

estabilidad = (
    ruta_mes
    .groupby("ruta", as_index=False)
    .agg(
        meses_activos=("periodo", "nunique"),
        pasajeros_totales=("pasajeros", "sum"),
        pasajeros_promedio=("pasajeros", "mean"),
        desviacion=("pasajeros", "std")
    )
)

estabilidad["coeficiente_variacion"] = (
    estabilidad["desviacion"]
    / estabilidad["pasajeros_promedio"]
)

estabilidad = estabilidad[
    (estabilidad["meses_activos"] >= 6)
    & (estabilidad["pasajeros_promedio"] > 0)
].copy()

estabilidad["coeficiente_variacion"] = (
    estabilidad["coeficiente_variacion"]
    .fillna(0)
)

rutas_estables = (
    estabilidad
    .sort_values(
        [
            "coeficiente_variacion",
            "pasajeros_promedio"
        ],
        ascending=[
            True,
            False
        ]
    )
    .head(15)
)

fig_estables = px.bar(
    rutas_estables.sort_values(
        "pasajeros_promedio",
        ascending=True
    ),
    x="pasajeros_promedio",
    y="ruta",
    orientation="h",
    color="coeficiente_variacion",
    title="Rutas con menor variabilidad relativa",
    labels={
        "ruta": "Ruta",
        "pasajeros_promedio": "Pasajeros promedio",
        "coeficiente_variacion": "Coeficiente de variación"
    },
    color_continuous_scale="RdYlGn_r"
)

st.plotly_chart(
    fig_estables,
    use_container_width=True
)

st.dataframe(
    rutas_estables.round(2),
    use_container_width=True
)

st.divider()

# Relación entre volumen y estabilidad
st.subheader("Volumen de pasajeros y estabilidad")

fig_estabilidad = px.scatter(
    estabilidad,
    x="pasajeros_promedio",
    y="coeficiente_variacion",
    size="meses_activos",
    hover_name="ruta",
    title="Relación entre pasajeros promedio y variabilidad",
    labels={
        "pasajeros_promedio": "Pasajeros promedio",
        "coeficiente_variacion": "Coeficiente de variación",
        "meses_activos": "Meses activos"
    }
)

st.plotly_chart(
    fig_estabilidad,
    use_container_width=True
)

st.info(
    "Las rutas ubicadas hacia la derecha presentan mayor volumen promedio. "
    "Las rutas ubicadas hacia abajo tienen menor variabilidad relativa. "
    "La estabilidad debe interpretarse junto con el volumen y la cantidad "
    "de meses observados."
)

st.divider()

# Comparación nacional e internacional
st.subheader("Comparación por tipo de tráfico")

tipo_trafico = (
    df_filtrado
    .groupby(
        ["periodo", "NAC"],
        as_index=False
    )
    .agg(
        pasajeros=("PASAJEROS", "sum")
    )
)

fig_tipo = px.area(
    tipo_trafico,
    x="periodo",
    y="pasajeros",
    color="NAC",
    title="Evolución de pasajeros nacionales e internacionales",
    labels={
        "periodo": "Mes",
        "pasajeros": "Pasajeros",
        "NAC": "Tipo de tráfico"
    }
)

st.plotly_chart(
    fig_tipo,
    use_container_width=True
)

st.divider()

# KPI agregado
df_kpi = pd.read_csv(
    "data/processed/datos_aerolinea_kpi.csv"
)

df_kpi["periodo"] = pd.to_datetime(
    df_kpi["month_id"].astype(str),
    format="%Y%m"
)

metricas_kpi = [
    "pasajeros",
    "ask",
    "rpk",
    "atk",
    "kkm_volados",
    "horas_vuelo"
]

metrica = st.selectbox(
    "Indicador complementario",
    metricas_kpi
)

kpi_tiempo = (
    df_kpi
    .groupby(
        ["periodo", "aerolinea_oaci"],
        as_index=False
    )
    .agg(
        valor=(metrica, "sum")
    )
)

fig_kpi = px.line(
    kpi_tiempo,
    x="periodo",
    y="valor",
    color="aerolinea_oaci",
    markers=True,
    title=f"Evolución del indicador {metrica}",
    labels={
        "periodo": "Mes",
        "valor": metrica,
        "aerolinea_oaci": "Aerolínea"
    }
)

st.plotly_chart(
    fig_kpi,
    use_container_width=True
)

st.subheader("Hallazgos preliminares")

st.markdown(
    """
    - El flujo de pasajeros presenta variaciones entre los distintos meses.
    - Las rutas con mayor volumen no necesariamente son las más estables.
    - La estabilidad debe evaluarse considerando simultáneamente volumen,
      meses activos y variabilidad.
    - Los KPI complementan el análisis de pasajeros, pero están agregados
      por aerolínea y tipo de operación.
    """
)