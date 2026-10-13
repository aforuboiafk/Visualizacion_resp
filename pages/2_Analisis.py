import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Diagnóstico y Resiliencia Aérea",
    layout="wide"
)

# -----------------------------
# 1. ENCABEZADO Y PREGUNTA CENTRAL
# -----------------------------
st.title("Diagnóstico de Conectividad y Resiliencia Aérea")


# Carga de datos base
df = pd.read_csv("data/processed/datos_limpios.csv")

df["PASAJEROS"] = pd.to_numeric(df["PASAJEROS"], errors="coerce").fillna(0)
df["periodo"] = pd.to_datetime(dict(year=df["Ano"], month=df["Mes"], day=1))
df["ruta"] = df["ORIG_1_N"].astype(str) + " → " + df["DEST_1_N"].astype(str)

# Filtros laterales
st.sidebar.header("Filtros del Análisis")
operadores = sorted(df["Operador"].dropna().unique())
operadores_seleccionados = st.sidebar.multiselect(
    "Operadores",
    operadores,
    default=operadores
)

df_filtrado = df[df["Operador"].isin(operadores_seleccionados)].copy()

if df_filtrado.empty:
    st.warning("No existen datos para los operadores seleccionados.")
    st.stop()

# -----------------------------
# 2. MÉTRICAS SINTÉTICAS (KPIs)
# -----------------------------
# Agrupación por ruta y mes para el cálculo de estabilidad
ruta_mes = (
    df_filtrado
    .groupby(["ruta", "NAC", "periodo"], as_index=False)
    .agg(pasajeros=("PASAJEROS", "sum"))
)

estabilidad = (
    ruta_mes
    .groupby(["ruta", "NAC"], as_index=False)
    .agg(
        meses_activos=("periodo", "nunique"),
        pasajeros_totales=("pasajeros", "sum"),
        pasajeros_promedio=("pasajeros", "mean"),
        desviacion=("pasajeros", "std")
    )
)
estabilidad["coeficiente_variacion"] = (
    estabilidad["desviacion"] / estabilidad["pasajeros_promedio"]
).fillna(0)

# Filtro de representatividad estadística (rutas continuas)
estabilidad_valida = estabilidad[
    (estabilidad["meses_activos"] >= 6) & (estabilidad["pasajeros_promedio"] > 0)
].copy()

total_pasajeros_sistema = df_filtrado["PASAJEROS"].sum()
top_5_vol = estabilidad.nlargest(5, "pasajeros_totales")["pasajeros_totales"].sum()
pct_concentracion = (top_5_vol / total_pasajeros_sistema) * 100 if total_pasajeros_sistema > 0 else 0

# Identificar automáticamente la ruta troncal más resiliente (alto volumen y menor CV)
candidatas_resilientes = estabilidad_valida[
    estabilidad_valida["pasajeros_promedio"] >= estabilidad_valida["pasajeros_promedio"].median()
]
nodo_top_resiliente = (
    candidatas_resilientes.sort_values("coeficiente_variacion").iloc[0]["ruta"]
    if not candidatas_resilientes.empty
    else "N/A"
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pasajeros Analizados", f"{total_pasajeros_sistema:,.0f}")
with col2:
    st.metric("Concentración en Top 5 Rutas", f"{pct_concentracion:.1f}%")
with col3:
    st.metric("Rutas Activas Analizadas", f"{len(estabilidad):,}")
with col4:
    st.metric("Nodo Más Resiliente", nodo_top_resiliente)

st.divider()

# -----------------------------
# 3. EVOLUCIÓN TEMPORAL MULTIANUAL (T)
# -----------------------------
st.subheader("1. Evolución temporal y recuperación post-crisis ($T$)")

tipo_trafico = (
    df_filtrado
    .groupby(["periodo", "NAC"], as_index=False)
    .agg(pasajeros=("PASAJEROS", "sum"))
)

fig_tipo = px.area(
    tipo_trafico,
    x="periodo",
    y="pasajeros",
    color="NAC",
    title="Flujo mensual acumulado: Tráfico Nacional vs. Internacional (2022–2026)",
    labels={
        "periodo": "Periodo mensual",
        "pasajeros": "Pasajeros transportados",
        "NAC": "Segmento"
    },
    color_discrete_map={"Nacional": "#2563eb", "Internacional": "#f97316"}
)

st.plotly_chart(fig_tipo, use_container_width=True)

st.write(
    "El tráfico creció de forma continua entre 2022 y 2024, para luego desacelerarse hacia 2025–2026. "
    "El segmento nacional aportó la base más estable del periodo, mientras que el internacional absorbió la mayor volatilidad post-reactivación."
)

st.divider()


# -----------------------------
# 4. CUADRANTES DE ESTABILIDAD Y RESILIENCIA
# -----------------------------
st.subheader("2. Matriz de Resiliencia: Volumen Promedio vs. Coeficiente de Variación")

mediana_volumen = estabilidad_valida["pasajeros_promedio"].median()
umbral_cv = 0.40  # Umbral estándar de estabilidad relativa

fig_estabilidad = px.scatter(
    estabilidad_valida,
    x="pasajeros_promedio",
    y="coeficiente_variacion",
    size="pasajeros_totales",
    color="NAC",
    hover_name="ruta",
    hover_data={
        "pasajeros_promedio": ":,.0f",
        "coeficiente_variacion": ":.2f",
        "meses_activos": True,
        "pasajeros_totales": False,
        "NAC": False
    },
    title="Clasificación de Nodos: Demanda Promedio vs. Volatilidad Relativa",
    labels={
        "pasajeros_promedio": "Flujo Promedio Mensual",
        "coeficiente_variacion": "Coeficiente de Variación (CV = σ / μ)",
        "NAC": "Tipo de tráfico"
    },
    color_discrete_map={"Nacional": "#2563eb", "Internacional": "#f97316"}
)

# Líneas de referencia para identificar el cuadrante de estabilidad
fig_estabilidad.add_vline(
    x=mediana_volumen,
    line_dash="dash",
    line_color="gray",
    annotation_text="Mediana Volumen",
    annotation_position="top right"
)
fig_estabilidad.add_hline(
    y=umbral_cv,
    line_dash="dash",
    line_color="gray",
    annotation_text="Umbral Estabilidad (CV = 0.40)",
    annotation_position="bottom right"
)

st.plotly_chart(fig_estabilidad, use_container_width=True)

st.write(
    "Las rutas del cuadrante inferior derecho combinan alto volumen continuo con baja variabilidad mensual. "
    "Este comportamiento identifica a los nodos troncales laborales como los más estables del país frente a rutas turísticas estacionales, priorizando su infraestructura."
)

st.divider()

# -----------------------------
# 5. DETALLE DE NODOS MÁS ESTABLES
# -----------------------------
st.subheader("3. Ranking de los Nodos más Estables")

rutas_top_estables = (
    estabilidad_valida
    .sort_values(["coeficiente_variacion", "pasajeros_promedio"], ascending=[True, False])
    .head(10)
    .rename(columns={
        "ruta": "Ruta",
        "NAC": "Tipo",
        "meses_activos": "Meses Activos",
        "pasajeros_promedio": "Pasajeros Promedio Mensual",
        "coeficiente_variacion": "Coeficiente de Variación (CV)"
    })
)

st.dataframe(
    rutas_top_estables[
        ["Ruta", "Tipo", "Meses Activos", "Pasajeros Promedio Mensual", "Coeficiente de Variación (CV)"]
    ].round(2),
    use_container_width=True,
    hide_index=True
)

st.divider()

# -----------------------------
# 6. INDICADOR COMPLEMENTARIO DE FLOTA (KPIs JAC)
# -----------------------------
st.subheader("4. Indicador complementario de capacidad de flota (KPIs JAC)")

try:
    df_kpi = pd.read_csv("data/processed/datos_aerolinea_kpi.csv")
    df_kpi["periodo"] = pd.to_datetime(df_kpi["month_id"].astype(str), format="%Y%m")

    metricas_kpi = ["pasajeros", "ask", "rpk", "atk", "kkm_volados", "horas_vuelo"]
    metrica_seleccionada = st.selectbox("Seleccionar métrica de flota/oferta:", metricas_kpi)

    kpi_tiempo = (
        df_kpi
        .groupby(["periodo", "aerolinea_oaci"], as_index=False)
        .agg(valor=(metrica_seleccionada, "sum"))
    )

    fig_kpi = px.line(
        kpi_tiempo,
        x="periodo",
        y="valor",
        color="aerolinea_oaci",
        markers=True,
        title=f"Evolución del indicador {metrica_seleccionada.upper()} por aerolínea",
        labels={"periodo": "Mes", "valor": metrica_seleccionada.upper(), "aerolinea_oaci": "Aerolínea"}
    )

    st.plotly_chart(fig_kpi, use_container_width=True)
except Exception:
    st.info("Archivo complementario de KPIs no disponible para visualización en este entorno.")

st.divider()

# -----------------------------
# 7. RESPUESTA Y HALLAZGOS FINALES
# -----------------------------
st.subheader("5. ¿Qué hemos aprendido sobre nuestra pregunta?")

col_h1, col_h2 = st.columns(2)

with col_h1:
    st.markdown(
        """
        **1. Polarización en Santiago (SCL)**  
        Menos del 15% de las rutas concentran casi todo el tráfico, dejando a la red vulnerable a contingencias en la capital.

        **2. Nodos laborales como base resiliente**  
        Las rutas Santiago–Norte minero (Antofagasta, Calama) tienen el menor $CV$: demanda continua e inelástica que no depende del turismo.
        """
    )

with col_h2:
    st.markdown(
        """
        **3. Techo de recuperación (2025–2026)**  
        Tras el rebote post-crisis, la red entró en una meseta de optimización donde las aerolíneas replegaron rutas secundarias.

        **4. Prioridad de infraestructura**  
        Alto volumen no equivale a estabilidad: los nodos resilientes justifican obras permanentes, mientras que las rutas estacionales solo requieren gestión de picos.
        """
    )