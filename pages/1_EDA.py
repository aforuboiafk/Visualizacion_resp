import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="EDA - Exploración de Datos",
    layout="wide"
)

# -----------------------------
# Carga y preparación inicial
# -----------------------------
st.title("Análisis Exploratorio de Datos (EDA)")

st.write(
    "Esta sección explora las propiedades estadísticas y estructurales del dataset "
    "mediante las 6 preguntas analíticas de visualización: distribuciones, comparaciones "
    "entre grupos, relaciones numéricas, temporalidad, espacialidad y múltiples dimensiones."
)

df = pd.read_csv("data/processed/datos_limpios.csv")

# Tipificación de variables numéricas
for col in ["PASAJEROS", "Distancia", "PAX_LIB", "CAR_LIB", "CARGA (Ton)", "CORREO"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["periodo"] = pd.to_datetime(dict(year=df["Ano"], month=df["Mes"], day=1))
df["ruta"] = df["ORIG_1_N"].astype(str) + " → " + df["DEST_1_N"].astype(str)

# -----------------------------
# Filtros interactivos
# -----------------------------
st.sidebar.header("Filtros del EDA")

operadores = sorted(df["Operador"].dropna().unique())
operadores_seleccionados = st.sidebar.multiselect(
    "Seleccionar operadores",
    options=operadores,
    default=operadores
)

tipos_trafico = sorted(df["NAC"].dropna().unique())
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de tráfico",
    options=tipos_trafico,
    default=tipos_trafico
)

destinos = sorted(df["DEST_1_N"].dropna().unique())
destinos_seleccionados = st.sidebar.multiselect(
    "Filtrar por destinos específicos (opcional)",
    options=destinos
)

fecha_inicial = df["periodo"].min().date()
fecha_final = df["periodo"].max().date()

rango_fechas = st.sidebar.slider(
    "Rango temporal",
    min_value=fecha_inicial,
    max_value=fecha_final,
    value=(fecha_inicial, fecha_final)
)

df_filtrado = df[
    df["Operador"].isin(operadores_seleccionados)
    & df["NAC"].isin(tipos_seleccionados)
    & df["periodo"].between(
        pd.Timestamp(rango_fechas[0]),
        pd.Timestamp(rango_fechas[1])
    )
].copy()

if destinos_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["DEST_1_N"].isin(destinos_seleccionados)]

if df_filtrado.empty:
    st.warning("No existen observaciones para los filtros seleccionados.")
    st.stop()

# -----------------------------
# Resumen estadístico numérico
# -----------------------------
st.header("Estadísticas descriptivas de variables numéricas")

estadisticas = (
    df_filtrado[
        ["PASAJEROS", "Distancia", "PAX_LIB", "CAR_LIB", "CARGA (Ton)", "CORREO"]
    ]
    .describe()
    .T
    .round(2)
)

st.dataframe(estadisticas, use_container_width=True)
st.caption(
    "Resumen de tendencia central, dispersión y percentiles para las variables operativas y de demanda."
)

st.divider()

# -----------------------------
# 1. Distribución de una variable
# -----------------------------
st.header("1. Distribución del flujo de pasajeros")

fig_dist = px.box(
    df_filtrado,
    x="PASAJEROS",
    y="NAC",
    color="NAC",
    title="Distribución del flujo de pasajeros por tipo de tráfico",
    labels={
        "PASAJEROS": "Pasajeros por registro mensual",
        "NAC": "Tipo de tráfico"
    },
    color_discrete_map={
        "Nacional": "#2563eb",
        "Internacional": "#f97316"
    }
)
st.plotly_chart(fig_dist, use_container_width=True)
fig_dist.update_layout(
    hovermode="closest",
    showlegend=False
)
fig_dist.update_traces(
    hoverinfo="x+y"
)

st.write(
    "La mayoría de los registros no supera los 5.000 pasajeros, mientras que unas pocas rutas masivas superan los 30.000. "
    "Esta asimetría indica que la red está concentrada en pocas conexiones troncales, por lo que evaluar estabilidad con promedios simples distorsionaría el análisis."
)

st.divider()

# -----------------------------
# 2. Comparación entre grupos
# -----------------------------
st.header("2. Concentración de mercado por operador")

resumen_operadores = (
    df_filtrado.groupby(["Operador", "NAC"], as_index=False)
    .agg(pasajeros=("PASAJEROS", "sum"))
    .sort_values("pasajeros", ascending=True)
)

fig_operadores = px.bar(
    resumen_operadores,
    x="pasajeros",
    y="Operador",
    color="NAC",
    orientation="h",
    title="¿Qué operadores concentran el mayor flujo de pasajeros?",
    labels={
        "pasajeros": "Pasajeros acumulados",
        "Operador": "Aerolínea / Operador",
        "NAC": "Tipo de tráfico"
    },
    color_discrete_map={
        "Nacional": "#2563eb",
        "Internacional": "#f97316"
    }
)
fig_operadores.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_operadores, use_container_width=True)

st.write(
    "Tres aerolíneas concentran casi la totalidad del tráfico nacional, frente a una oferta internacional más fragmentada. "
    "Esta dependencia de pocos operadores muestra que la conectividad interna es vulnerable ante contingencias operativas o huelgas de una sola empresa."
)
st.divider()

# -----------------------------
# 3. Relación entre dos variables numéricas
# -----------------------------
st.header("3. Relación física: Distancia de ruta vs. Flujo de pasajeros")

fig_scatter = px.scatter(
    df_filtrado,
    x="Distancia",
    y="PASAJEROS",
    color="NAC",
    hover_name="ruta",
    hover_data={"Operador": True, "Distancia": ":,.0f", "PASAJEROS": ":,.0f"},
    title="¿Existe relación entre la distancia de vuelo y el volumen de pasajeros?",
    labels={
        "Distancia": "Distancia ortodrómica (km)",
        "PASAJEROS": "Pasajeros por registro",
        "NAC": "Tipo de tráfico"
    },
    opacity=0.65,
    color_discrete_map={
        "Nacional": "#2563eb",
        "Internacional": "#f97316"
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.write(
    "El mayor volumen de pasajeros se concentra en rutas de 1.000 a 1.500 km, vinculadas al eje entre Santiago y el norte del país. "
    "Este patrón delimita geográficamente los corredores de mayor demanda regular que sostienen la red aérea nacional."
)

st.divider()

# -----------------------------
# 4. Evolución temporal y estacionalidad (T)
# -----------------------------
st.header("4. Comportamiento estacional agregado")

df_filtrado["Mes_Nombre"] = df_filtrado["periodo"].dt.strftime("%m - %B")
estacionalidad = (
    df_filtrado.groupby(["Mes", "Mes_Nombre", "NAC"], as_index=False)
    .agg(pasajeros=("PASAJEROS", "sum"))
    .sort_values("Mes")
)

fig_estacional = px.line(
    estacionalidad,
    x="Mes_Nombre",
    y="pasajeros",
    color="NAC",
    markers=True,
    title="¿Cómo varía el volumen de pasajeros a lo largo de los meses del año?",
    labels={
        "Mes_Nombre": "Mes del año",
        "pasajeros": "Pasajeros acumulados",
        "NAC": "Tipo de tráfico"
    },
    color_discrete_map={
        "Nacional": "#2563eb",
        "Internacional": "#f97316"
    }
)
st.plotly_chart(fig_estacional, use_container_width=True)

st.write(
    "El tráfico alcanza sus máximos en enero-febrero y julio, cayendo de forma pronunciada en otoño y primavera. "
    "Esta estacionalidad cíclica debe aislarse para no confundir la baja demanda de ciertos meses con inestabilidad estructural de una ruta."
)

st.divider()

# -----------------------------
# 5. Distribución espacial del fenómeno
# -----------------------------
st.header("5. Concentración por nodos de destino geográfico")

top_destinos = (
    df_filtrado.groupby(["DEST_1_N", "NAC"], as_index=False)
    .agg(
        pasajeros=("PASAJEROS", "sum"),
        meses_activos=("periodo", "nunique")
    )
    .sort_values("pasajeros", ascending=False)
    .head(15)
)

fig_destinos = px.bar(
    top_destinos,
    x="pasajeros",
    y="DEST_1_N",
    color="NAC",
    orientation="h",
    hover_data=["meses_activos"],
    title="Top 15 aeropuertos de destino según volumen de pasajeros",
    labels={
        "pasajeros": "Pasajeros acumulados",
        "DEST_1_N": "Aeropuerto de destino",
        "NAC": "Tipo de tráfico"
    },
    color_discrete_map={
        "Nacional": "#2563eb",
        "Internacional": "#f97316"
    }
)
fig_destinos.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_destinos, use_container_width=True)

st.write(
    "Los destinos con mayor flujo corresponden a centros mineros del norte como Antofagasta y Calama, y a hubs regionales como Lima. "
    "Esto confirma una red polarizada hacia polos productivos estratégicos, donde la continuidad del servicio resulta prioritaria."
)

st.divider()

# -----------------------------
# 6. Relación entre múltiples variables
# -----------------------------
st.header("6. Matriz de correlación entre variables numéricas")

variables_matriz = [
    "PASAJEROS",
    "Distancia",
    "PAX_LIB",
    "CAR_LIB",
    "CARGA (Ton)",
    "CORREO"
]

matriz_corr = df_filtrado[variables_matriz].corr()

fig_corr = px.imshow(
    matriz_corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Asociación multivariada entre métricas operativas y de demanda"
)
st.plotly_chart(fig_corr, use_container_width=True)

st.write(
    "El flujo de pasajeros no correlaciona con la distancia de vuelo ni con el volumen de carga pura. "
    "Esto demuestra que la movilidad de personas sigue dinámicas independientes de la carga, validando su análisis como fenómeno aislado."
)