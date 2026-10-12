import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Contexto y Datos",
    page_icon="✈️",
    layout="wide"
)

# Cargar datos procesados
df = pd.read_csv(
    "data/processed/datos_limpios.csv"
)

# Crear periodo mensual
df["periodo"] = pd.to_datetime(
    dict(
        year=df["Ano"],
        month=df["Mes"],
        day=1
    )
)

# Convertir variables numéricas
df["PASAJEROS"] = pd.to_numeric(
    df["PASAJEROS"],
    errors="coerce"
).fillna(0)

df["Distancia"] = pd.to_numeric(
    df["Distancia"],
    errors="coerce"
).fillna(0)

# Título
st.title("Evolución y Resiliencia de la Conectividad Aérea")

st.caption(
    "Contexto, estructura y calidad de los datos utilizados en el proyecto."
)

st.info(
    "Esta página responde: ¿Qué estamos estudiando y con qué datos?"
)

st.divider()

# Variables X, Y y T
# Variables X, Y y T
st.header("Variables del proyecto")

col_y, col_x, col_t = st.columns(3)

with col_y:
    st.subheader("Y: variable objetivo")
    st.write("`PASAJEROS`")
    st.caption(
        "Flujo mensual de pasajeros transportados."
    )

with col_x:
    st.subheader("X: variables explicativas")
    st.write(
        "`Operador`, `ruta`, `Distancia` y `NAC`"
    )
    st.caption(
        "Variables utilizadas para comparar y explicar "
        "el flujo de pasajeros."
    )

with col_t:
    st.subheader("T: dimensión temporal")
    st.write(
        "`Ano`, `Mes` y `periodo`"
    )
    st.caption(
        "Permite estudiar la evolución mensual del fenómeno."
    )

st.write(
    "En este proyecto, la variable objetivo **Y** corresponde al flujo "
    "de pasajeros. Las variables **X** describen el operador, la ruta, "
    "la distancia y el tipo de tráfico. La dimensión temporal **T** "
    "permite observar cómo cambia el flujo aéreo entre 2022 y 2026."
)
st.divider()

# Problema y pregunta
# Proyecto y datos
st.header("Proyecto")

st.subheader("Problema")

st.write(
    "El tráfico aéreo de pasajeros ha experimentado cambios después "
    "de la crisis sanitaria. Estos cambios pueden afectar la "
    "conectividad entre ciudades y la planificación de infraestructura "
    "aeroportuaria."
)

st.subheader("Pregunta principal")

st.success(
    "¿Cómo ha evolucionado el flujo de pasajeros y cuáles rutas son "
    "los nodos más estables actualmente?"
)

st.subheader("Alcance")

st.markdown(
    """
    - **Foco:** movilidad humana.
    - **Geografía:** vuelos con origen o destino en Chile.
    - **Periodo:** 2022 a 2026.
    - **Exclusiones:** carga comercial y vuelos militares.
    """
)

st.divider()

st.header("Datos utilizados")

st.write(
    "El dataset contiene registros de tráfico aéreo obtenidos desde "
    "la Junta de Aeronáutica Civil. Cada observación representa el "
    "flujo mensual de pasajeros de un operador en una ruta específica."
)

st.markdown(
    """
    **Unidad de observación:**

    `mes + operador + ruta + tipo de tráfico`
    """
)

st.markdown(
    """
    **Variables principales:**

    Año, mes, operador, origen, destino, países, tipo de tráfico,
    pasajeros y distancia.
    """
)

st.divider()

# Indicadores generales
st.header("Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Registros",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "Variables",
        len(df.columns)
    )

with col3:
    st.metric(
        "Operadores",
        df["Operador"].nunique()
    )

with col4:
    st.metric(
        "Rutas",
        df[
            ["ORIG_1", "DEST_1"]
        ].drop_duplicates().shape[0]
    )

st.divider()

# Periodo analizado
st.header("Periodo y cobertura")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Inicio",
        df["periodo"].min().strftime("%m/%Y")
    )

with col2:
    st.metric(
        "Término",
        df["periodo"].max().strftime("%m/%Y")
    )

with col3:
    st.metric(
        "Meses",
        df["periodo"].nunique()
    )

with col4:
    st.metric(
        "Destinos",
        df["DEST_1_N"].nunique()
    )

st.divider()

# Estadísticas descriptivas
st.header("Estadísticas descriptivas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Promedio de pasajeros",
        f"{df['PASAJEROS'].mean():,.0f}"
    )

with col2:
    st.metric(
        "Mediana de pasajeros",
        f"{df['PASAJEROS'].median():,.0f}"
    )

with col3:
    st.metric(
        "Máximo de pasajeros",
        f"{df['PASAJEROS'].max():,.0f}"
    )

with col4:
    st.metric(
        "Distancia promedio",
        f"{df['Distancia'].mean():,.0f}"
    )

st.divider()

# Calidad de datos
st.header("Calidad de los datos")

nulos_total = int(
    df.isna().sum().sum()
)

porcentaje_nulos = (
    nulos_total / df.size * 100
)

calidad = pd.DataFrame({
    "Indicador": [
        "Registros",
        "Variables",
        "Duplicados",
        "Valores nulos",
        "Porcentaje de nulos",
        "Operadores",
        "Orígenes",
        "Destinos",
        "Tipos de tráfico"
    ],
    "Resultado": [
        f"{len(df):,}",
        len(df.columns),
        int(df.duplicated().sum()),
        nulos_total,
        f"{porcentaje_nulos:.2f}%",
        df["Operador"].nunique(),
        df["ORIG_1_N"].nunique(),
        df["DEST_1_N"].nunique(),
        df["NAC"].nunique()
    ]
})

st.dataframe(
    calidad,
    hide_index=True,
    use_container_width=True
)

with st.expander("Decisiones de preparación"):
    st.markdown(
        """
        - Se eliminaron duplicados exactos.
        - Se conservaron registros con pasajeros mayores que cero.
        - Se eliminaron registros con pasajeros nulos.
        - Se normalizó la dimensión temporal a formato mensual.
        - Se estandarizaron categorías de operadores y tipos de tráfico.
        - Los KPI se mantuvieron en un archivo agregado separado para
          evitar duplicar sus valores al nivel de ruta.
        """
    )

st.divider()

# Tipos de variables
st.header("Estructura de las variables")

tipos_variables = pd.DataFrame({
    "Elemento": [
        "Y: objetivo",
        "X: operador",
        "X: ruta",
        "X: distancia",
        "X: tipo de tráfico",
        "T: tiempo"
    ],
    "Variables": [
        "PASAJEROS",
        "Operador",
        "ORIG_1_N, DEST_1_N",
        "Distancia",
        "NAC",
        "Ano, Mes, periodo"
    ],
    "Tipo": [
        "Numérica",
        "Categórica",
        "Categórica espacial",
        "Numérica",
        "Categórica",
        "Temporal"
    ],
    "Uso": [
        "Medir el flujo aéreo",
        "Comparar operadores",
        "Analizar rutas",
        "Explorar relación con pasajeros",
        "Separar tráfico nacional e internacional",
        "Analizar evolución temporal"
    ]
})

st.dataframe(
    tipos_variables,
    hide_index=True,
    use_container_width=True
)

st.divider()

# Muestra de datos
with st.expander("Ver muestra de datos procesados"):
    st.dataframe(
        df.head(20),
        use_container_width=True
    )

st.caption(
    "Las distribuciones, comparaciones y relaciones entre variables "
    "se exploran en la página EDA."
)