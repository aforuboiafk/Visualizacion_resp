import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="EDA",
    layout="wide"
)

# -----------------------------
# Carga y preparación
# -----------------------------

st.title("Análisis Exploratorio de Datos")

st.write(
    "Esta página explora cómo se comportan los datos de tráfico aéreo "
    "mediante distribuciones, comparaciones, relaciones y evolución temporal."
)

df = pd.read_csv(
    "data/processed/datos_limpios.csv"
)

df["PASAJEROS"] = pd.to_numeric(
    df["PASAJEROS"],
    errors="coerce"
).fillna(0)

df["Distancia"] = pd.to_numeric(
    df["Distancia"],
    errors="coerce"
).fillna(0)

df["PAX_LIB"] = pd.to_numeric(
    df["PAX_LIB"],
    errors="coerce"
).fillna(0)

df["CAR_LIB"] = pd.to_numeric(
    df["CAR_LIB"],
    errors="coerce"
).fillna(0)

df["CARGA (Ton)"] = pd.to_numeric(
    df["CARGA (Ton)"],
    errors="coerce"
).fillna(0)

df["CORREO"] = pd.to_numeric(
    df["CORREO"],
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
    + " -> "
    + df["DEST_1_N"].astype(str)
)

# -----------------------------
# Filtros interactivos
# -----------------------------

st.sidebar.header("Filtros interactivos")

operadores = sorted(
    df["Operador"].dropna().unique()
)

operadores_seleccionados = st.sidebar.multiselect(
    "Seleccionar operadores",
    options=operadores,
    default=operadores
)

tipos_trafico = sorted(
    df["NAC"].dropna().unique()
)

tipos_seleccionados = st.sidebar.multiselect(
    "Seleccionar tipo de tráfico",
    options=tipos_trafico,
    default=tipos_trafico
)

destinos = sorted(
    df["DEST_1_N"].dropna().unique()
)

destinos_seleccionados = st.sidebar.multiselect(
    "Seleccionar destinos",
    options=destinos
)

fecha_inicial = df["periodo"].min().date()
fecha_final = df["periodo"].max().date()

rango_fechas = st.sidebar.slider(
    "Seleccionar periodo",
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
    df_filtrado = df_filtrado[
        df_filtrado["DEST_1_N"].isin(destinos_seleccionados)
    ]

if df_filtrado.empty:
    st.warning(
        "No existen datos para los filtros seleccionados."
    )
    st.stop()

# -----------------------------
# Resumen
# -----------------------------

st.header("Resumen del subconjunto seleccionado")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Registros",
        f"{len(df_filtrado):,}"
    )

with col2:
    st.metric(
        "Pasajeros",
        f"{df_filtrado['PASAJEROS'].sum():,.0f}"
    )

with col3:
    st.metric(
        "Operadores",
        df_filtrado["Operador"].nunique()
    )

with col4:
    st.metric(
        "Rutas",
        df_filtrado[
            ["ORIG_1", "DEST_1"]
        ].drop_duplicates().shape[0]
    )

st.divider()

# -----------------------------
# Estadísticas descriptivas
# -----------------------------

st.header("Estadísticas descriptivas")

estadisticas = (
    df_filtrado[
        [
            "PASAJEROS",
            "Distancia",
            "PAX_LIB",
            "CAR_LIB",
            "CARGA (Ton)",
            "CORREO"
        ]
    ]
    .describe()
    .T
    .round(2)
)

st.dataframe(
    estadisticas,
    use_container_width=True
)

st.caption(
    "La tabla resume tendencia central, dispersión y valores extremos "
    "de las variables numéricas seleccionadas."
)

st.divider()

# -----------------------------
# Visualización 1:
# Distribución de Y
# -----------------------------

st.header("1. Distribución de la variable objetivo")

fig_histograma = px.histogram(
    df_filtrado,
    x="PASAJEROS",
    nbins=40,
    color="NAC",
    marginal="box",
    opacity=0.75,
    title="¿Cómo se distribuye el flujo de pasajeros?",
    labels={
        "PASAJEROS": "Pasajeros por registro",
        "count": "Cantidad de registros",
        "NAC": "Tipo de tráfico"
    },
    color_discrete_sequence=[
        "#2563eb",
        "#f97316"
    ]
)

fig_histograma.update_layout(
    legend_title_text="Tipo de tráfico"
)

st.plotly_chart(
    fig_histograma,
    use_container_width=True
)

st.caption(
    "El histograma muestra la frecuencia de los registros según su "
    "cantidad de pasajeros. El boxplot marginal permite observar "
    "la dispersión y los valores extremos."
)

st.divider()

# -----------------------------
# Visualización 2:
# Comparación de grupos
# -----------------------------

st.header("2. Comparación entre operadores")

resumen_operadores = (
    df_filtrado
    .groupby("Operador", as_index=False)
    .agg(
        pasajeros=("PASAJEROS", "sum"),
        registros=("PASAJEROS", "count")
    )
    .sort_values(
        "pasajeros",
        ascending=False
    )
)

fig_operadores = px.bar(
    resumen_operadores,
    x="pasajeros",
    y="Operador",
    orientation="h",
    color="pasajeros",
    title="¿Qué operadores concentran mayor flujo de pasajeros?",
    labels={
        "pasajeros": "Pasajeros acumulados",
        "Operador": "Operador"
    },
    color_continuous_scale="Blues"
)

fig_operadores.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    }
)

st.plotly_chart(
    fig_operadores,
    use_container_width=True
)

st.caption(
    "Las barras permiten comparar directamente el volumen acumulado "
    "de pasajeros entre los operadores seleccionados."
)

st.divider()

# -----------------------------
# Visualización 3:
# Valores atípicos
# -----------------------------

st.header("3. Distribución y valores atípicos")

fig_boxplot = px.box(
    df_filtrado,
    x="Operador",
    y="PASAJEROS",
    color="NAC",
    points="outliers",
    title="¿Qué operadores presentan mayor dispersión?",
    labels={
        "Operador": "Operador",
        "PASAJEROS": "Pasajeros",
        "NAC": "Tipo de tráfico"
    }
)

st.plotly_chart(
    fig_boxplot,
    use_container_width=True
)

st.caption(
    "El boxplot compara medianas, dispersión y valores atípicos "
    "entre operadores y tipos de tráfico."
)

st.divider()

# -----------------------------
# Visualización 4:
# Evolución temporal
# -----------------------------

st.header("4. Evolución temporal")

resumen_temporal = (
    df_filtrado
    .groupby(
        ["periodo", "Operador"],
        as_index=False
    )
    .agg(
        pasajeros=("PASAJEROS", "sum")
    )
)

fig_temporal = px.line(
    resumen_temporal,
    x="periodo",
    y="pasajeros",
    color="Operador",
    markers=True,
    title="¿Cómo cambia el flujo de pasajeros en el tiempo?",
    labels={
        "periodo": "Periodo mensual",
        "pasajeros": "Pasajeros",
        "Operador": "Operador"
    }
)

st.plotly_chart(
    fig_temporal,
    use_container_width=True
)

st.caption(
    "La línea temporal permite observar tendencias, cambios mensuales "
    "y diferencias en el comportamiento de los operadores."
)

st.divider()

# -----------------------------
# Visualización 5:
# Relación X-Y
# -----------------------------

st.header("5. Relación entre distancia y pasajeros")

fig_scatter = px.scatter(
    df_filtrado,
    x="Distancia",
    y="PASAJEROS",
    color="Operador",
    size="PASAJEROS",
    hover_data=[
        "ruta",
        "NAC"
    ],
    title="¿Existe relación entre distancia y flujo de pasajeros?",
    labels={
        "Distancia": "Distancia de la ruta",
        "PASAJEROS": "Pasajeros",
        "Operador": "Operador"
    }
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

st.caption(
    "El gráfico explora la relación entre una variable explicativa X, "
    "la distancia, y la variable objetivo Y, los pasajeros."
)

st.divider()

# -----------------------------
# Visualización 6:
# Rutas y contexto espacial
# -----------------------------

st.header("6. Comparación de rutas")

resumen_rutas = (
    df_filtrado
    .groupby("ruta", as_index=False)
    .agg(
        pasajeros=("PASAJEROS", "sum"),
        meses_activos=("periodo", "nunique")
    )
    .sort_values(
        "pasajeros",
        ascending=False
    )
    .head(15)
    .sort_values(
        "pasajeros",
        ascending=True
    )
)

fig_rutas = px.bar(
    resumen_rutas,
    x="pasajeros",
    y="ruta",
    orientation="h",
    color="meses_activos",
    title="¿Qué rutas concentran mayor flujo de pasajeros?",
    labels={
        "pasajeros": "Pasajeros acumulados",
        "ruta": "Ruta",
        "meses_activos": "Meses activos"
    },
    color_continuous_scale="Viridis"
)

st.plotly_chart(
    fig_rutas,
    use_container_width=True
)

st.caption(
    "Las rutas se comparan por pasajeros acumulados y meses activos, "
    "aportando una primera aproximación a su importancia y continuidad."
)

st.divider()

# -----------------------------
# Relación entre múltiples variables
# -----------------------------

st.header("Relación entre variables numéricas")

variables_numericas = [
    "PASAJEROS",
    "Distancia",
    "PAX_LIB",
    "CAR_LIB",
    "CARGA (Ton)",
    "CORREO"
]

correlacion = df_filtrado[
    variables_numericas
].corr()

fig_correlacion = px.imshow(
    correlacion,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="¿Cómo se relacionan las variables numéricas?"
)

st.plotly_chart(
    fig_correlacion,
    use_container_width=True
)

st.caption(
    "La matriz permite explorar asociaciones entre pasajeros, distancia "
    "y variables de carga u operación."
)

st.divider()

# Descarga
st.download_button(
    label="Descargar datos filtrados",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="datos_eda_filtrados.csv",
    mime="text/csv"
)