import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==========================================
st.set_page_config(page_title="Portal de Datos Públicos Chile", layout="wide", page_icon="🇨🇱")

st.title("🇨🇱 Analizador de Datasets Públicos de Salud - Chile")
st.markdown("""
Este panel interactivo consume datos en tiempo real desde la **API oficial de datos.gob.cl**.
Cumple con los requisitos de utilizar **Requests** para la conexión, **Pandas** para el análisis y **Matplotlib** junto con **Streamlit** para la visualización.
""")

# ==========================================
# 2. INTERACCIÓN CON API (Requests + JSON)
# ==========================================
# Buscamos datasets relacionados con "salud"
URL_API = "https://datos.gob.cl/api/3/action/package_search?q=salud&rows=100"

@st.cache_data
def traer_datos_gobierno():
    try:
        respuesta = requests.get(URL_API)
        respuesta.raise_for_status() # Verifica que no haya errores HTTP (ej: 404)
        
        datos_json = respuesta.json()
        lista_datasets = datos_json['result']['results']
        return lista_datasets
    except Exception as e:
        st.error(f"Error de conexión con la API: {e}")
        return None

datos_raw = traer_datos_gobierno()

# ==========================================
# 3. ANÁLISIS DE DATOS (Pandas)
# ==========================================
if datos_raw:
    df_completo = pd.DataFrame(datos_raw)
    
    # Extraer el nombre de la institución del diccionario anidado 'organization'
    def extraer_institucion(item):
        if isinstance(item, dict) and 'title' in item:
            return item['title']
        return "Institución no especificada"
        
    df_completo['Institución Pública'] = df_completo['organization'].apply(extraer_institucion)
    
    # Extraer el año de la fecha de modificación para los gráficos
    # Se convierte la fecha a datetime y se extrae solo el año
    df_completo['Año'] = pd.to_datetime(df_completo['metadata_modified'], errors='coerce').dt.year
    df_completo['Año'] = df_completo['Año'].fillna(0).astype(int)
    
    # Limpiamos el dataframe dejando solo las columnas útiles
    df_limpio = df_completo[['title', 'Institución Pública', 'notes', 'Año']].copy()
    df_limpio.columns = ['Título del Dataset', 'Institución Pública', 'Descripción', 'Año']

    # ==========================================
    # 4. PRESENTACIÓN Y VISUALIZACIÓN INTERACTIVA (Streamlit + Matplotlib)
    # ==========================================
    
    # --- FILTROS LATERALES ---
    st.sidebar.header("🎯 Filtros Disponibles")
    instituciones = sorted(df_limpio['Institución Pública'].unique())
    opciones_filtro = ["Todas las Instituciones"] + instituciones
    seleccion = st.sidebar.selectbox("Selecciona una Institución:", opciones_filtro)
    
    # Aplicar el filtro de Pandas
    if seleccion == "Todas las Instituciones":
        df_filtrado = df_limpio
    else:
        df_filtrado = df_limpio[df_limpio['Institución Pública'] == seleccion]

    # --- DISEÑO EN PESTAÑAS (TABS) ---
    tab1, tab2 = st.tabs(["📋 Tabla de Datos", "📊 Visualización Gráfica"])
    
    # PESTAÑA 1: TABLA
    with tab1:
        st.subheader("Catálogo de Datasets")
        # Ocultamos la columna Año en la tabla para que se vea más limpia
        st.dataframe(df_filtrado.drop(columns=['Año']), use_container_width=True, hide_index=True)
        st.caption(f"Mostrando {len(df_filtrado)} registros. Origen: API datos.gob.cl")
        
    # PESTAÑA 2: GRÁFICOS (Matplotlib)
    with tab2:
        if df_filtrado.empty:
            st.warning("No hay datos para graficar con los filtros actuales.")
        else:
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("🏆 Top Instituciones")
                conteo_inst = df_filtrado['Institución Pública'].value_counts().head(5)
                
                # Gráfico de Barras Horizontales Mejorado
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                barras = ax1.barh(conteo_inst.index, conteo_inst.values, color='#005088')
                ax1.invert_yaxis() # Para que el valor mayor quede arriba
                
                # Limpieza visual del gráfico
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.spines['bottom'].set_visible(False)
                ax1.xaxis.set_visible(False) # Ocultar eje x
                
                # Agregar etiquetas de datos en las barras
                ax1.bar_label(barras, padding=5, fontweight='bold', color='#005088')
                
                st.pyplot(fig1)
                
            with col_graf2:
                st.subheader("📅 Publicaciones por Año")
                # Filtramos años mayores a 2000 para evitar errores de tipeo en la API
                conteo_anios = df_filtrado[df_filtrado['Año'] > 2000]['Año'].value_counts().sort_index()
                
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                if len(conteo_anios) > 0:
                    ax2.plot(conteo_anios.index, conteo_anios.values, marker='o', color='#E63946', linewidth=2)
                    
                    # Limpieza visual
                    ax2.spines['top'].set_visible(False)
                    ax2.spines['right'].set_visible(False)
                    ax2.set_xticks(conteo_anios.index) # Mostrar solo años enteros
                    ax2.set_ylabel("Cantidad de Datasets")
                    st.pyplot(fig2)
                else:
                    st.info("No hay datos de fecha válidos para graficar.")
                    
else:
    st.warning("No se pudieron extraer datos en este momento. Inténtalo nuevamente.")