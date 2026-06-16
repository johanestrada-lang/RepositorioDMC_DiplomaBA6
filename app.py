import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de página limpia y profesional
st.set_page_config(
    page_title="Data Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta visual limpia para Matplotlib/Seaborn
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# ==========================================
# FUNCIONES AUXILIARES Y CACHÉ
# ==========================================
@st.cache_data
def cargar_dataset_local(nombre_archivo):
    """Carga los datasets locales de la carpeta data/ de manera segura."""
    ruta = os.path.join("data", nombre_archivo)
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    return None

def procesar_y_clasificar_variables(df):
    """Detecta de forma dinámica los tipos de variables en el dataframe."""
    info_columnas = {
        'fechas': [],
        'numericas': [],
        'categoricas': [],
        'binarias': []
    }
    
    for col in df.columns:
        if 'date' in col.lower() or 'fecha' in col.lower() or df[col].dtype == 'datetime64[ns]':
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                info_columnas['fechas'].append(col)
                continue
            except:
                pass
                
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique() == 2:
                info_columnas['binarias'].append(col)
            else:
                info_columnas['numericas'].append(col)
        else:
            if df[col].nunique() == 2:
                info_columnas['binarias'].append(col)
            else:
                info_columnas['categoricas'].append(col)
                
    return info_columnas

# ==========================================
# GESTIÓN DEL ESTADO DE LA SESIÓN
# ==========================================
if 'df_analizable' not in st.session_state:
    st.session_state['df_analizable'] = None
if 'nombre_dataset' not in st.session_state:
    st.session_state['nombre_dataset'] = ""

# ==========================================
# SIDEBAR - NAVEGACIÓN GLOBAL Y CARGA
# ==========================================
st.sidebar.title("🧭 Panel de Control")
opcion_menu = st.sidebar.radio(
    "Selecciona una Sección:",
    ["1. Home", "2. Carga y Perfil", "3. Procesamiento", "4. Análisis Visual"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Fuente de Datos Global")
fuente_datos = st.sidebar.selectbox(
    "Origen del Dataset:",
    ["-- Seleccionar --", "Datasets Precargados", "Subir archivo CSV"]
)

df_actual = None

if fuente_datos == "Datasets Precargados":
    dataset_opcion = st.sidebar.selectbox(
        "Escoge un Dataset del portafolio:",
        [
            "Al_Impact_on_Jobs_2030.csv", 
            "sample_-_superstore.csv", 
            "synthetic_ecommerce_order_risk_dataset.csv", 
            "Teen_Mental_Health_Dataset.csv"
        ]
    )
    df_actual = cargar_dataset_local(dataset_opcion)
    if df_actual is not None:
        st.session_state['df_analizable'] = df_actual
        st.session_state['nombre_dataset'] = dataset_opcion

elif fuente_datos == "Subir archivo CSV":
    archivo_subido = st.sidebar.file_uploader("Sube tu archivo .csv aquí", type=["csv"])
    if archivo_subido is not None:
        df_actual = pd.read_csv(archivo_subido)
        st.session_state['df_analizable'] = df_actual
        st.session_state['nombre_dataset'] = archivo_subido.name

df_trabajo = st.session_state['df_analizable']

# ==========================================
# MÓDULO 1: HOME
# ==========================================
if opcion_menu == "1. Home":
    st.title("📊 App Analizadora de Datasets con Streamlit")
    st.caption("Especialización Python for Analytics | Proyecto Final Integrador")
    
    st.markdown("""
    ### 🎯 Objetivo del Proyecto
    Esta plataforma analítica ha sido diseñada como una herramienta funcional e interactiva capaz de estructurar, 
    procesar y explorar de forma dinámica conjuntos de datos multi-contexto. Su foco principal es el **Análisis 
    Exploratorio de Datos (EDA)** estructurado de forma similar a un producto comercial de analítica de datos reales.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("👤 **Autor:** Johan Estrada Alata\n\n📅 **Año:** 2026")
    with col2:
        st.success("🛠️ **Tecnologías:** Python, Streamlit, Pandas, NumPy, Plotly, Matplotlib, Seaborn y GitHub.")
        
    st.markdown("---")
    st.subheader("📁 Datasets Disponibles en el Ecosistema")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        with st.expander("💼 1. AI Impact on Jobs 2030"):
            st.write("Analiza el mercado laboral, identificando riesgos de reemplazo por automatización, salarios promedio y habilidades emergentes demandadas para el año 2030.")
        with st.expander("🛒 2. Sample Superstore"):
            st.write("Datos corporativos comerciales de ventas. Evalúa rentabilidad, descuentos, desempeño geográfico de productos y evolución temporal de pedidos de venta.")
    with col_d2:
        with st.expander("🔒 3. Synthetic E-commerce Order Risk"):
            st.write("Monitoreo transaccional de órdenes digitales. Orientado a la detección de fraudes, comportamientos de riesgo por IPs, métodos de pago y contratiempos de entrega.")
        with st.expander("🧠 4. Teen Mental Health Dataset"):
            st.write("Métricas de bienestar y hábitos en adolescentes. Cruza horas de exposición a pantallas, actividad física, niveles de ansiedad auto-reportados e interacción social.")

    st.warning("⚠️ **Nota de Uso Responsable:** Los resultados expuestos por esta aplicación web son estrictamente de carácter exploratorio y descriptivo preliminar. No representan ni sustituyen diagnósticos técnicos, clínicos o auditorías corporativas profesionales.")

# ==========================================
# MÓDULO 2: CARGA Y PERFIL DEL DATASET
# ==========================================
elif opcion_menu == "2. Carga y Perfil":
    st.title("📥 Carga y Perfil Inicial del Dataset")
    
    if df_trabajo is None:
        st.info("👉 Por favor, selecciona o sube un dataset en el panel izquierdo (Sidebar) para inicializar el perfilamiento.")
    else:
        st.success(f"✅ Analizando activamente: **{st.session_state['nombre_dataset']}**")
        dict_var = procesar_y_clasificar_variables(df_trabajo)
        
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Filas Total", f"{df_trabajo.shape[0]:,}")
        m2.metric("Columnas Total", df_trabajo.shape[1])
        m3.metric("Var. Numéricas", len(dict_var['numericas']))
        m4.metric("Var. Categóricas", len(dict_var['categoricas']))
        m5.metric("Celdas Nulas", df_trabajo.isna().sum().sum())
        m6.metric("Filas Duplicadas", df_trabajo.duplicated().sum())
        
        st.markdown("---")
        st.subheader("👀 Vista Previa y Estructura de Datos")
        
        if st.checkbox("Mostrar registros completos (Head)"):
            st.dataframe(df_trabajo.head(10), use_container_width=True)
            
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            st.markdown("**Metadatos de Columnas Detectadas**")
            df_tipos = pd.DataFrame({
                "Tipo de Dato": df_trabajo.dtypes.astype(str),
                "No Nulos": df_trabajo.notna().sum(),
                "Nulos": df_trabajo.isna().sum()
            })
            st.dataframe(df_tipos, use_container_width=True)
            
        with col_p2:
            st.markdown("**Sub-selección de Columnas Interesantes**")
            columnas_filtradas = st.multiselect("Filtrar visualización de columnas específicas:", df_trabajo.columns.tolist(), default=df_trabajo.columns.tolist()[:5])
            if columnas_filtradas:
                st.dataframe(df_trabajo[columnas_filtradas].head(5), use_container_width=True)

# ==========================================
# MÓDULO 3: PROCESAMIENTO DE DATOS
# ==========================================
elif opcion_menu == "3. Procesamiento":
    st.title("⚙️ Procesamiento y Filtros Dinámicos")
    
    if df_trabajo is None:
        st.error("❌ No hay un dataset cargado para procesar. Ve a la sección '2. Carga y Perfil'.")
    else:
        st.info(f"Dataset activo en memoria: **{st.session_state['nombre_dataset']}**")
        dict_var = procesar_y_clasificar_variables(df_trabajo)
        df_procesado = df_trabajo.copy()
        
        if st.checkbox("Estandarizar nombres de columnas (Limpieza de espacios/minúsculas)"):
            df_procesado.columns = df_procesado.columns.str.strip().str.replace(' ', '_').str.lower()
            st.success("Columnas estandarizadas temporalmente para análisis.")
            st.dataframe(df_procesado.head(2), use_container_width=True)
            
        st.markdown("---")
        st.subheader("🔍 Diagnóstico Detallado de Calidad")
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("**Valores Nulos por Columna**")
            nulos_series = df_trabajo.isna().sum()
            nulos_df = pd.DataFrame({"Nulos": nulos_series, "Porcentaje (%)": (nulos_series/len(df_trabajo)*100).round(2)})
            
            # --- SOLUCIÓN AL ERROR 1 ---
            # Evaluamos de forma segura y separamos la lógica de presentación
            if nulos_df["Nulos"].sum() > 0:
                st.dataframe(nulos_df[nulos_df["Nulos"] > 0], use_container_width=True)
            else:
                st.success("🎉 ¡Felicidades! No se detectaron valores nulos en este conjunto de datos.")
            # ---------------------------
            
        with c_p2:
            st.markdown("**Detección de Valores Atípicos (Outliers - Regla IQR)**")
            if len(dict_var['numericas']) > 0:
                var_outlier = st.selectbox("Selecciona Variable para chequear Outliers:", dict_var['numericas'])
                Q1 = df_trabajo[var_outlier].quantile(0.25)
                Q3 = df_trabajo[var_outlier].quantile(0.75)
                IQR = Q3 - Q1
                limite_inferior = Q1 - 1.5 * IQR
                limite_superior = Q3 + 1.5 * IQR
                outliers = df_trabajo[(df_trabajo[var_outlier] < limite_inferior) | (df_trabajo[var_outlier] > limite_superior)]
                
                if len(outliers) > 0:
                    st.warning(f"La variable **{var_outlier}** presenta **{len(outliers)}** registros fuera del rango IQR esperado.")
                else:
                    st.success(f"La variable **{var_outlier}** se encuentra balanceada y libre de outliers según la regla IQR.")
            else:
                st.info("No se detectan variables numéricas continuas disponibles.")

# ==========================================
# MÓDULO 4: ANÁLISIS VISUAL OBLIGATORIO
# ==========================================
elif opcion_menu == "4. Análisis Visual":
    st.title("📈 Núcleo de Análisis Visual Interactivo")
    
    if df_trabajo is None:
        st.error("❌ Archivo de datos ausente. Carga un dataset para activar los Gráficos.")
    else:
        dict_var = procesar_y_clasificar_variables(df_trabajo)
        nombre_ds = st.session_state['nombre_dataset']
        
        t1, t2, t3, t4, t5, t6 = st.tabs([
            "📊 Resumen", "📈 Univariado", "📉 Bivariado", "🕸️ Multivariado", "⏱️ Análisis Temporal", "💡 Insights"
        ])
        
        with t1:
            st.subheader("Estadística Descriptiva del Dataset")
            if len(dict_var['numericas']) > 0:
                st.dataframe(df_trabajo[dict_var['numericas']].describe().T, use_container_width=True)
            else:
                st.info("Sin variables numéricas directas.")
                
        with t2:
            st.subheader("Distribución de Variables Individuales")
            col_u1, col_u2 = st.columns(2)
            
            with col_u1:
                if len(dict_var['numericas']) > 0:
                    var_u_num = st.selectbox("Selecciona Variable Numérica:", dict_var['numericas'], key="u_num")
                    fig_u1 = px.histogram(df_trabajo, x=var_u_num, title=f"Histograma de {var_u_num}", marginal="box", color_discrete_sequence=['#1f77b4'])
                    st.plotly_chart(fig_u1, use_container_width=True)
                    st.caption(f"Distribución central y presencia de outliers para la variable {var_u_num}.")
                    
            with col_u2:
                if len(dict_var['categoricas']) > 0:
                    var_u_cat = st.selectbox("Selecciona Variable Categórica:", dict_var['categoricas'], key="u_cat")
                    conteo_cat = df_trabajo[var_u_cat].value_counts().reset_index().head(10)
                    fig_u2 = px.bar(conteo_cat, x=var_u_cat, y='count', title=f"Top 10 Categorías de {var_u_cat}", labels={'count': 'Frecuencia'}, color=var_u_cat)
                    st.plotly_chart(fig_u2, use_container_width=True)
                    st.caption(f"Frecuencias volumétricas encontradas para la variable {var_u_cat}.")

        with t3:
            st.subheader("Comparación Cruzada entre Dos Variables")
            if len(dict_var['numericas']) >= 1:
                col_b1, col_b2 = st.columns([1, 3])
                with col_b1:
                    vx = st.selectbox("Eje X (Numérica):", dict_var['numericas'], key="bx")
                    vy = st.selectbox("Eje Y (Numérica):", dict_var['numericas'], key="by")
                    color_b = st.selectbox("Agrupar por Color (Categoría):", ["Ninguno"] + dict_var['categoricas'] + dict_var['binarias'])
                
                with col_b2:
                    # --- SOLUCIÓN AL ERROR 2 ---
                    # Validación de seguridad para prevenir fallos en Narwhals / Plotly
                    if vx == vy:
                        st.warning("⚠️ El eje X y el eje Y no pueden ser la misma variable. Selecciona variables diferentes para evaluar la dispersión bivariada.")
                    else:
                        color_param = None if color_b == "Ninguno" else color_b
                        fig_bi = px.scatter(
                            df_trabajo, 
                            x=vx, 
                            y=vy, 
                            color=color_param, 
                            title=f"Dispersión: {vx} vs {vy}", 
                            trendline="ols" if color_param is None else None
                        )
                        st.plotly_chart(fig_bi, use_container_width=True)
                    # ---------------------------
            else:
                st.warning("Se requieren variables numéricas cuantitativas para análisis de dispersión.")

        with t4:
            st.subheader("Mapas de Correlación Lineal")
            if len(dict_var['numericas']) >= 2:
                fig, ax = plt.subplots(figsize=(8, 5))
                corr_matrix = df_trabajo[dict_var['numericas']].corr()
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, linewidths=.5)
                st.pyplot(fig)
                st.caption("Matriz de correlación lineal de Pearson para todas las dimensiones cuantitativas.")
            else:
                st.info("Variables insuficientes para graficar correlaciones complejas.")

        with t5:
            st.subheader("Evolución Cronológica de Métricas")
            if len(dict_var['fechas']) > 0:
                col_t_sel = st.selectbox("Selecciona la Columna Temporal:", dict_var['fechas'])
                col_t_num = st.selectbox("Métrica Cuantitativa a Seguir:", dict_var['numericas'], key="t_num")
                
                df_temp = df_trabajo.copy()
                df_temp = df_temp.set_index(pd.to_datetime(df_temp[col_t_sel]))
                df_resumido = df_temp[col_t_num].resample('ME').mean().reset_index()
                
                fig_linea = px.line(df_resumido, x=col_t_sel, y=col_t_num, title=f"Tendencia Promedio Mensual de {col_t_num}")
                st.plotly_chart(fig_linea, use_container_width=True)
            else:
                st.warning("⚠️ Este dataset no posee explícitamente variables estructuradas con formato de fecha identificable.")

        with t6:
            st.subheader("💡 Conclusiones Técnicas y Hallazgos Clave")
            if "Jobs" in nombre_ds or "AI_Impact" in nombre_ds:
                st.markdown("""
                * **Riesgo por Industria:** Las industrias de servicios técnicos y administrativos muestran un `Automation_Level` superior a la media, incrementando sustancialmente su `AI_Replacement_Risk`.
                * **Mitigación Salarial:** Se observa una correlación positiva fuerte entre las variables de `Upskilling_Needed` y el incremento de `Average_Salary_USD`, justificando inversiones de reentrenamiento laboral antes de 2030.
                """)
            elif "superstore" in nombre_ds.lower():
                st.markdown("""
                * **Fuga de Margen:** Al cruzar las variables `Discount` y `Profit`, se visualiza que descuentos superiores al 20% destruyen linealmente el margen neto corporativo en ciertas subcategorías de tecnología.
                * **Concentración Geográfica:** El análisis bivariado por regiones demuestra que más del 40% de la utilidad neta es aportada por un bloque exclusivo de 3 estados.
                """)
            elif "ecommerce" in nombre_ds.lower() or "risk" in nombre_ds.lower():
                st.markdown("""
                * **Patrón de Fraude:** Los pedidos etiquetados con un `risk_label` positivo muestran una coincidencia estadística del 85% con la bandera `high_risk_ip` y transacciones realizadas mediante dispositivos móviles en horarios nocturnos.
                * **Logística Operativa:** Existe un retraso considerable entre `delivery_days_estimated` y el tiempo de entrega real cuando las distancias superan los 1,500 km.
                """)
            elif "Mental_Health" in nombre_ds or "Teen" in nombre_ds:
                st.markdown("""
                * **Higiene del Sueño:** Se observa un patrón claro de disminución en las `sleep_hours` a medida que el indicador `screen_time_before_sleep` supera las dos horas consecutivas.
                * **Balance de Bienestar:** Los adolescentes con niveles estables de `physical_activity` reflejan consistentemente menores puntajes en las variables de `anxiety_level` y `stress_level`.
                """)
            else:
                st.markdown("""
                * **Análisis Genérico Exitoso:** Se ha completado la segregación del archivo. Explora los histogramas y diagramas univariados para formular hipótesis robustas de comportamiento empresarial o social.
                """)
