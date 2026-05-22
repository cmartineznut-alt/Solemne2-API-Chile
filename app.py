"""
App Streamlit: Explorador de Establecimientos de Salud en Chile.
Consume la API REST de datos.gob.cl mediante la clase ClienteDatosGob.

Solemne II - Taller de Programación II
Universidad San Sebastián
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from api import ClienteDatosGob


# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Establecimientos de Salud - Chile",
    page_icon="🏥",
    layout="wide",
)

RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"


# ==========================================
# CARGA DE DATOS (con caché)
# ==========================================
@st.cache_data(ttl=3600)
def cargar_datos():
    """Descarga el dataset completo desde la API y lo devuelve como DataFrame."""
    cliente = ClienteDatosGob()
    df = cliente.obtener_recurso_completo(RESOURCE_ID)
    return df


# ==========================================
# ENCABEZADO
# ==========================================
st.title("🏥 Establecimientos de Salud en Chile")
st.markdown(
    "Explorador interactivo de los establecimientos de salud registrados "
    "en el Ministerio de Salud de Chile. "
    "Fuente: [datos.gob.cl](https://datos.gob.cl) — API REST pública."
)

# Cargar datos
with st.spinner("Descargando datos desde datos.gob.cl..."):
    df = cargar_datos()


# ==========================================
# SIDEBAR CON FILTROS INTERACTIVOS
# ==========================================
st.sidebar.header("🎛️ Filtros")
st.sidebar.markdown("Ajusta los filtros para explorar el dataset.")

# --- Filtro 1: Región (multi-select) ---
regiones_disponibles = sorted(df["RegionGlosa"].dropna().unique())
regiones_seleccionadas = st.sidebar.multiselect(
    "Región",
    options=regiones_disponibles,
    default=regiones_disponibles,  # por defecto todas seleccionadas
    help="Selecciona una o más regiones del país.",
)

# --- Filtro 2: Tipo de establecimiento ---
tipos_disponibles = sorted(df["TipoEstablecimientoGlosa"].dropna().unique())
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de establecimiento",
    options=tipos_disponibles,
    default=tipos_disponibles,
)

# --- Filtro 3: Dependencia administrativa (radio) ---
opciones_dependencia = ["Todas"] + sorted(df["DependenciaAdministrativa"].dropna().unique())
dependencia_seleccionada = st.sidebar.radio(
    "Dependencia administrativa",
    options=opciones_dependencia,
    index=0,
)

# --- Filtro 4: Solo con servicio de urgencia (checkbox) ---
solo_urgencia = st.sidebar.checkbox(
    "Mostrar solo establecimientos con urgencia",
    value=False,
)


# ==========================================
# APLICAR FILTROS AL DATAFRAME
# ==========================================
df_filtrado = df.copy()

if regiones_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado["RegionGlosa"].isin(regiones_seleccionadas)]

if tipos_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["TipoEstablecimientoGlosa"].isin(tipos_seleccionados)]

if dependencia_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["DependenciaAdministrativa"] == dependencia_seleccionada]

if solo_urgencia:
    df_filtrado = df_filtrado[df_filtrado["TieneServicioUrgencia"] == "Si"]


# ==========================================
# MÉTRICAS RESUMEN (KPIs)
# ==========================================
st.markdown("### 📊 Resumen")
col1, col2, col3, col4 = st.columns(4)

total = len(df_filtrado)
porcentaje = (total / len(df) * 100) if len(df) > 0 else 0
n_regiones = df_filtrado["RegionGlosa"].nunique()
n_con_urgencia = (df_filtrado["TieneServicioUrgencia"] == "Si").sum()

col1.metric("Establecimientos", f"{total:,}")
col2.metric("% del total nacional", f"{porcentaje:.1f}%")
col3.metric("Regiones cubiertas", n_regiones)
col4.metric("Con urgencia", f"{n_con_urgencia:,}")


# ==========================================
# PESTAÑAS CON TABLA, GRÁFICOS Y MAPA
# ==========================================
tab_tabla, tab_graficos, tab_mapa = st.tabs(["📋 Tabla", "📈 Gráficos", "🗺️ Mapa"])


# --- PESTAÑA 1: TABLA ---
with tab_tabla:
    st.markdown("### Tabla de datos filtrados")

    if df_filtrado.empty:
        st.warning("⚠️ No hay establecimientos que cumplan los filtros seleccionados.")
    else:
        columnas_visibles = [
            "EstablecimientoGlosa",
            "RegionGlosa",
            "ComunaGlosa",
            "TipoEstablecimientoGlosa",
            "DependenciaAdministrativa",
            "NivelComplejidadEstabGlosa",
            "TieneServicioUrgencia",
        ]
        st.dataframe(
            df_filtrado[columnas_visibles],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Mostrando {len(df_filtrado):,} de {len(df):,} establecimientos.")


# --- PESTAÑA 2: GRÁFICOS ---
with tab_graficos:
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos para graficar con los filtros actuales.")
    else:
        # Color institucional para los gráficos
        COLOR_PRIMARIO = "#005088"
        COLOR_SECUNDARIO = "#E63946"

        # ----- Gráfico 1: Top regiones por cantidad de establecimientos -----
        st.markdown("### 🌎 Establecimientos por región")
        conteo_regiones = df_filtrado["RegionGlosa"].value_counts().head(10)

        fig1, ax1 = plt.subplots(figsize=(10, 5))
        barras1 = ax1.barh(conteo_regiones.index, conteo_regiones.values, color=COLOR_PRIMARIO)
        ax1.invert_yaxis()
        ax1.set_xlabel("Cantidad de establecimientos")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.bar_label(barras1, padding=4, fontsize=9)
        plt.tight_layout()
        st.pyplot(fig1)

        st.divider()

        # Dividir en 2 columnas los siguientes gráficos
        col_g1, col_g2 = st.columns(2)

        # ----- Gráfico 2: Tipo de establecimiento (top 8) -----
        with col_g1:
            st.markdown("### 🏥 Tipos de establecimiento")
            conteo_tipos = df_filtrado["TipoEstablecimientoGlosa"].value_counts().head(8)

            fig2, ax2 = plt.subplots(figsize=(6, 5))
            barras2 = ax2.barh(conteo_tipos.index, conteo_tipos.values, color=COLOR_SECUNDARIO)
            ax2.invert_yaxis()
            ax2.set_xlabel("Cantidad")
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            ax2.bar_label(barras2, padding=4, fontsize=9)
            plt.tight_layout()
            st.pyplot(fig2)

        # ----- Gráfico 3: Dependencia (pie chart) -----
        with col_g2:
            st.markdown("### 🏛️ Dependencia administrativa")
            conteo_dep = df_filtrado["DependenciaAdministrativa"].value_counts().head(6)

            fig3, ax3 = plt.subplots(figsize=(6, 5))
            ax3.pie(
                conteo_dep.values,
                labels=conteo_dep.index,
                autopct="%1.1f%%",
                startangle=90,
                colors=plt.cm.tab10.colors,
            )
            ax3.axis("equal")
            plt.tight_layout()
            st.pyplot(fig3)


# --- PESTAÑA 3: MAPA ---
with tab_mapa:
    st.markdown("### 🗺️ Ubicación geográfica")
    st.caption(
        "Mapa interactivo con las coordenadas reales de cada establecimiento. "
        "Usa los filtros del panel lateral para acotar la vista."
    )

    # Preparar datos para el mapa: convertir lat/lng a numérico y eliminar inválidos
    df_mapa = df_filtrado.copy()
    df_mapa["lat"] = pd.to_numeric(df_mapa["Latitud"], errors="coerce")
    df_mapa["lon"] = pd.to_numeric(df_mapa["Longitud"], errors="coerce")
    df_mapa = df_mapa.dropna(subset=["lat", "lon"])

    # Filtrar coordenadas dentro de un rango razonable para Chile
    df_mapa = df_mapa[
        (df_mapa["lat"].between(-56, -17)) & (df_mapa["lon"].between(-76, -66))
    ]

    if df_mapa.empty:
        st.warning("⚠️ No hay coordenadas válidas para mostrar en el mapa.")
    else:
        st.map(df_mapa[["lat", "lon"]], zoom=4)
        st.caption(f"Se muestran {len(df_mapa):,} establecimientos con coordenadas válidas.")


# ==========================================
# PIE DE PÁGINA
# ==========================================
st.divider()
st.caption(
    "🎓 Solemne II — Taller de Programación II | Universidad San Sebastián | "
    "Datos: Ministerio de Salud de Chile vía API datos.gob.cl"
)