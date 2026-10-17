
import streamlit as st
import pandas as pd
import plotly.express as px
import base64

from html import escape
from scripts.eventos import cargar_eventos


# =====================================================
# 1. CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Análisis de eventos | Laboral.AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

FONDO = "#F6F8FC"
AZUL = "#102B49"
FONDO_HALLAZGOS = "#7288AA"

# Colores aprobados para los gráficos
COLOR_INSCRIPCIONES = "#173F6D"
COLOR_EVOLUCION = "#8CC04B"
COLOR_ESTADOS = "#624C8E"
COLOR_MODALIDAD = "#6DB3BB"
COLOR_CATEGORIAS = "#F1921A"
COLOR_TIPOS = "#173F6D"
COLOR_EMPRESAS = "#6DB3BB"

# Análisis de participantes
COLOR_CREACION_CUENTAS = "#F8C64B"
COLOR_RELACION_USUARIOS = "#CF4786"

# Análisis de certificados
COLOR_CERTIFICADOS = "#12365B"

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre",
    "Diciembre",
]


# =====================================================
# 2. FUNCIONES DE COLORES
# =====================================================

def tonos_grafico(color, cantidad):
    """
    Genera tonalidades de un mismo color,
    desde el original hasta tonos más claros.
    """

    if cantidad <= 0:
        return []

    color = color.lstrip("#")

    rojo = int(color[0:2], 16)
    verde = int(color[2:4], 16)
    azul = int(color[4:6], 16)

    resultado = []

    for indice in range(cantidad):
        factor = (
            0.0
            if cantidad == 1
            else 0.60 * indice / (cantidad - 1)
        )

        r = round(rojo + (255 - rojo) * factor)
        g = round(verde + (255 - verde) * factor)
        b = round(azul + (255 - azul) * factor)

        resultado.append(f"rgb({r},{g},{b})")

    return resultado


def color_transparente(color, opacidad=0.18):
    """Convierte un color hexadecimal a RGBA."""

    color = color.lstrip("#")

    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)

    return f"rgba({r},{g},{b},{opacidad})"



# =====================================================
# 3. ESTILOS GENERALES
# =====================================================

st.html("""
<style>

/* =============================================
   FONDO GENERAL
   ============================================= */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #F6F8FC !important;
}

[data-testid="stMainBlockContainer"],
.block-container {
    max-width: 1500px !important;
    padding: 4rem 2rem 3rem !important;
}


/* =============================================
   BARRA LATERAL
   ============================================= */

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background-color: #102B49 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* Espacio superior compacto */

[data-testid="stSidebarUserContent"] {
    padding-top: 0.6rem !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 0.8rem !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.45rem !important;
}

/* Encabezados */

[data-testid="stSidebar"] h2 {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] h3 {
    margin-top: 0.15rem !important;
    margin-bottom: 0.15rem !important;
}

/* Descripción bajo Laboral.AI */

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #A4B1C4 !important;
}

/* Separadores */

[data-testid="stSidebar"] hr {
    margin: 0.25rem 0 !important;
}

/* Etiquetas */

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    margin-bottom: 0.1rem !important;
}


/* =============================================
   FILTROS BLANCOS EN LIGHT Y DARK
   ============================================= */

/* Selectores */

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
    background-color: #FFFFFF !important;
    color: #303441 !important;
    border-color: #FFFFFF !important;
    border-radius: 9px !important;
    min-height: 38px !important;
    box-shadow: none !important;
}

/* Textos seleccionados */

[data-testid="stSidebar"]
[data-baseweb="select"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"]
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"]
[data-baseweb="select"] [role="combobox"],
[data-testid="stSidebar"]
[data-baseweb="select"] input,
[data-testid="stSidebar"]
[data-baseweb="select"] span {
    color: #303441 !important;
    -webkit-text-fill-color: #303441 !important;
}

/* Flechas */

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    color: #303441 !important;
    fill: #303441 !important;
}

/* Selector de fechas */

[data-testid="stSidebar"]
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stSidebar"]
[data-testid="stDateInput"] [data-baseweb="input"] > div,
[data-testid="stSidebar"]
[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    border-color: #FFFFFF !important;
    border-radius: 9px !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"]
[data-testid="stDateInput"] input {
    color: #303441 !important;
    -webkit-text-fill-color: #303441 !important;
    min-height: 38px !important;
}

/* Icono de calendario */

[data-testid="stSidebar"]
[data-testid="stDateInput"] svg {
    color: #838792 !important;
}

/* Selectores deshabilitados */

[data-testid="stSidebar"]
[data-baseweb="select"] [aria-disabled="true"],
[data-testid="stSidebar"]
[data-baseweb="select"] [aria-disabled="true"] *,
[data-testid="stSidebar"]
[data-baseweb="select"] [data-disabled="true"],
[data-testid="stSidebar"]
[data-baseweb="select"] [data-disabled="true"] * {
    color: #A9ABB2 !important;
    -webkit-text-fill-color: #A9ABB2 !important;
}


/* =============================================
   BOTONES DE LA BARRA LATERAL
   ============================================= */

[data-testid="stSidebar"] .st-key-btn_limpiar button,
[data-testid="stSidebar"] .st-key-btn_actualizar button {
    background-color: #294463 !important;
    color: #FFFFFF !important;
    border: 1px solid #294463 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    width: 100% !important;
    min-height: 40px !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .st-key-btn_limpiar button p,
[data-testid="stSidebar"] .st-key-btn_actualizar button p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .st-key-btn_limpiar button:hover,
[data-testid="stSidebar"] .st-key-btn_actualizar button:hover {
    background-color: #365577 !important;
    border-color: #365577 !important;
}

[data-testid="stSidebar"] .st-key-btn_limpiar button:hover p,
[data-testid="stSidebar"] .st-key-btn_actualizar button:hover p,
[data-testid="stSidebar"] .st-key-btn_limpiar button:focus p,
[data-testid="stSidebar"] .st-key-btn_actualizar button:focus p,
[data-testid="stSidebar"] .st-key-btn_limpiar button:active p,
[data-testid="stSidebar"] .st-key-btn_actualizar button:active p {
    color: #FFFFFF !important;
}


/* =============================================
   CONTENIDO PRINCIPAL
   ============================================= */

[data-testid="stMain"] h1 {
    color: #102B49 !important;
    font-size: 44px !important;
    font-weight: 800 !important;
    line-height: 1.3 !important;
    margin-top: 0 !important;
    padding-top: 12px !important;
}

/* Títulos de las secciones */

.section-heading {
    font-size: 23px !important;
    font-weight: 800 !important;
    line-height: 1.35 !important;
    color: #102B49 !important;
    margin-top: 22px;
    margin-bottom: 12px;
}

/* Títulos de los gráficos */

[data-testid="stMain"] h3 {
    font-size: 20px !important;
    font-weight: 400 !important;
    line-height: 1.35 !important;
    color: #102B49 !important;
    margin-bottom: 12px !important;
}


/* =============================================
   CUADROS DE GRÁFICOS CON FONDO BLANCO
   INCLUYE TÍTULO Y GRÁFICO
   ============================================= */

/* Solo los contenedores identificados como gráficos */

[data-testid="stMain"] [class*="st-key-cuadro_grafico_"] {
    background-color: #FFFFFF !important;
    border-radius: 15px !important;
}

/* Área interior de Plotly */

[data-testid="stMain"]
[class*="st-key-cuadro_grafico_"]
[data-testid="stPlotlyChart"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
}

/* Fondo del elemento gráfico */

[data-testid="stMain"]
[class*="st-key-cuadro_grafico_"]
[data-testid="stPlotlyChart"] > div {
    background-color: #FFFFFF !important;
}


/* =============================================
   PANTALLAS PEQUEÑAS
   ============================================= */

@media (max-width: 600px) {

    [data-testid="stMainBlockContainer"],
    .block-container {
        padding: 3rem 1rem 2rem !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 0.4rem !important;
    }

    [data-testid="stMain"] h1 {
        font-size: 32px !important;
    }
}
/* Fondo blanco exclusivo para la tabla de eventos */

[data-testid="stMain"] .st-key-cuadro_tabla_eventos {
    background-color: #FFFFFF !important;
    border-radius: 15px !important;
}
</style>
""")


# =====================================================
# 4. FUNCIONES VISUALES
# =====================================================

def numero(valor):
    return f"{int(valor):,}".replace(",", ".")


def titulo_seccion(texto):
    st.html(
        '<div class="section-heading">'
        + escape(texto)
        + '</div>'
    )


def sin_datos(mensaje):
    st.info(mensaje)


def grafico(fig, altura=340):
    fig.update_layout(
        template="plotly_white",
        height=altura,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#263B54", size=12),
        margin=dict(l=15, r=25, t=20, b=35),
        legend_title_text=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


def texto_tabla(valor):
    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass

    return escape(str(valor))


# =====================================================
# 5. TARJETAS KPI PRINCIPALES
# =====================================================

def mostrar_kpis(indicadores):

    tarjetas = []

    for titulo, valor in indicadores:
        tarjetas.append(
            '<div class="kpi-card">'
            f'<div class="kpi-label">{escape(titulo)}</div>'
            f'<div class="kpi-value">{numero(valor)}</div>'
            '</div>'
        )

    html = """
    <style>

    .kpi-scroll {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 8px;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(175px, 1fr));
        gap: 12px;
        width: 100%;
        min-width: 900px;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E1E7F0;
        border-radius: 15px;
        padding: 19px 12px;
        min-height: 125px;
        box-sizing: border-box;
        box-shadow: 0 3px 12px rgba(16,43,73,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .kpi-label {
        color: #677890;
        font-size: 12px;
        line-height: 1.45;
        font-weight: 650;
        margin-bottom: 12px;
        min-height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .kpi-value {
        color: #102B49;
        font-size: 31px;
        line-height: 1.2;
        font-weight: 800;
        text-align: center;
    }

    </style>
    """

    html += (
        '<div class="kpi-scroll">'
        '<div class="kpi-grid">'
        + "".join(tarjetas)
        + '</div></div>'
    )

    st.html(html)


# =====================================================
# 6. HALLAZGOS CLAVE
# =====================================================

def obtener_mes_mayor_actividad(df):

    fechas = df[
        ["eventguest_id", "registrationDate"]
    ].copy()

    fechas["registrationDate"] = pd.to_datetime(
        fechas["registrationDate"],
        errors="coerce",
        utc=True
    )

    fechas = fechas.dropna(
        subset=["registrationDate"]
    )

    if fechas.empty:
        return "Sin información", 0

    fechas["mes"] = (
        fechas["registrationDate"]
        .dt.strftime("%Y-%m")
    )

    conteos = (
        fechas.groupby("mes")["eventguest_id"]
        .nunique()
        .sort_values(ascending=False)
    )

    mes_top = conteos.index[0]
    cantidad = int(conteos.iloc[0])

    anio, mes_num = map(int, mes_top.split("-"))

    return f"{MESES_ES[mes_num - 1]} {anio}", cantidad


def svg_a_imagen(svg):

    contenido = base64.b64encode(
        svg.encode("utf-8")
    ).decode("utf-8")

    return (
        '<img '
        f'src="data:image/svg+xml;base64,{contenido}" '
        'width="43" height="43" '
        'style="display:block;width:43px;height:43px;" '
        'alt="Icono">'
    )


def mostrar_hallazgos(
    nombre_evento,
    inscripciones_evento,
    nombre_mes,
    inscripciones_mes,
    certificados_pagados
):

    icono_trofeo = svg_a_imagen(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="43" height="43" viewBox="0 0 24 24" '
        'fill="none" stroke="#17245D" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M8 21h8M12 17v4"/>'
        '<path d="M7 4h10v6a5 5 0 0 1-10 0V4Z"/>'
        '<path d="M7 6H4v3a4 4 0 0 0 4 4"/>'
        '<path d="M17 6h3v3a4 4 0 0 1-4 4"/>'
        '</svg>'
    )

    icono_calendario = svg_a_imagen(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="43" height="43" viewBox="0 0 24 24" '
        'fill="none" stroke="#17245D" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="5" width="18" height="16" rx="2"/>'
        '<path d="M16 3v4M8 3v4M3 10h18"/>'
        '</svg>'
    )

    icono_certificado = svg_a_imagen(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="43" height="43" viewBox="0 0 24 24" '
        'fill="none" stroke="#17245D" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="8" r="5"/>'
        '<path d="m8.5 12-1 9 4.5-2 4.5 2-1-9"/>'
        '<path d="m10 8 1.3 1.3L14 6.8"/>'
        '</svg>'
    )

    def tarjeta_hallazgo(icono, titulo, valor, detalle):
        return (
            '<div class="hallazgo-item">'
            '<div class="hallazgo-icono">'
            + icono
            + '</div>'
            '<div class="hallazgo-texto">'
            f'<div class="hallazgo-etiqueta">{escape(titulo)}</div>'
            f'<div class="hallazgo-valor">{escape(str(valor))}</div>'
            f'<div class="hallazgo-detalle">{escape(detalle)}</div>'
            '</div></div>'
        )

    tarjetas = [
        tarjeta_hallazgo(
            icono_trofeo,
            "Evento con más inscripciones",
            nombre_evento,
            f"{numero(inscripciones_evento)} inscripciones"
        ),
        tarjeta_hallazgo(
            icono_calendario,
            "Mes de mayor actividad",
            nombre_mes,
            f"{numero(inscripciones_mes)} inscripciones"
        ),
        tarjeta_hallazgo(
            icono_certificado,
            "Total de certificados pagados",
            numero(certificados_pagados),
            "Certificados marcados como pagados"
        )
    ]

    html = """
    <style>

    .hallazgos-contenedor {
        background: #7288AA;
        border-radius: 18px;
        padding: 23px 25px;
        margin: 15px 0 22px;
        width: 100%;
        box-sizing: border-box;
    }

    .hallazgos-titulo {
        font-size: 23px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 18px;
        line-height: 1.3;
    }

    .hallazgos-scroll {
        width: 100%;
        overflow-x: auto;
    }

    .hallazgos-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(270px, 1fr));
        min-width: 810px;
        border-radius: 13px;
        background: rgba(255,255,255,0.88);
        padding: 14px 5px;
    }

    .hallazgo-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        min-width: 0;
        box-sizing: border-box;
    }

    .hallazgo-item + .hallazgo-item {
        border-left: 1px solid #C7CCE8;
    }

    .hallazgo-icono {
        flex: 0 0 49px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hallazgo-texto {
        flex: 1;
        min-width: 0;
        text-align: center;
    }

    .hallazgo-etiqueta {
        font-size: 13px;
        font-weight: 500;
        color: #465573;
        line-height: 1.35;
        margin-bottom: 5px;
    }

    .hallazgo-valor {
        font-size: 16px;
        font-weight: 800;
        color: #17245D;
        line-height: 1.35;
        overflow-wrap: anywhere;
    }

    .hallazgo-detalle {
        font-size: 13px;
        font-weight: 500;
        color: #344D78;
        line-height: 1.4;
        margin-top: 5px;
    }

    </style>
    """

    html += (
        '<div class="hallazgos-contenedor">'
        '<div class="hallazgos-titulo">Hallazgos clave</div>'
        '<div class="hallazgos-scroll">'
        '<div class="hallazgos-grid">'
        + "".join(tarjetas)
        + '</div></div></div>'
    )

    st.html(html)


# =====================================================
# 7. TARJETAS DE CERTIFICADOS
# =====================================================

def mostrar_tarjetas_certificados(indicadores):

    tarjetas = []

    for titulo, valor in indicadores:
        tarjetas.append(
            '<div class="cert-card">'
            f'<div class="cert-label">{escape(titulo)}</div>'
            f'<div class="cert-value">{escape(str(valor))}</div>'
            '</div>'
        )

    html = """
    <style>

    .cert-scroll {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 8px;
    }

    .cert-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(220px, 1fr));
        gap: 15px;
        min-width: 690px;
    }

    .cert-card {
        background: #FFFFFF;
        border: 1px solid #E1E7F0;
        border-radius: 15px;
        padding: 22px 18px;
        min-height: 130px;
        box-sizing: border-box;
        box-shadow: 0 3px 12px rgba(16,43,73,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .cert-label {
        color: #677890;
        font-size: 13px;
        font-weight: 650;
        line-height: 1.4;
        min-height: 38px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .cert-value {
        color: #102B49;
        font-size: 31px;
        font-weight: 800;
        line-height: 1.2;
    }

    </style>
    """

    html += (
        '<div class="cert-scroll">'
        '<div class="cert-grid">'
        + "".join(tarjetas)
        + '</div></div>'
    )

    st.html(html)


# =====================================================
# 8. TABLA DE EVENTOS COMPACTA
# =====================================================

def mostrar_tabla_eventos(df):

    css = """
    <style>

    .tabla-eventos-scroll {
        width: 100%;
        max-height: 380px;
        overflow-x: auto;
        overflow-y: auto;
        border: 1px solid #DAE1EB;
        border-radius: 10px;
        background: #FFFFFF;
    }

    .tabla-eventos {
        width: max-content;
        min-width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        font-family: inherit;
        table-layout: auto;
    }

    .tabla-eventos thead th {
        background-color: #6CBBC3 !important;
        color: #000000 !important;
        font-size: 11px;
        font-weight: 600;
        text-align: center !important;
        vertical-align: middle;
        padding: 7px 10px;
        white-space: nowrap !important;
        line-height: 1.2;
        border-right: 1px solid rgba(255,255,255,0.22);
        position: sticky;
        top: 0;
        z-index: 1;
    }

    .tabla-eventos tbody tr:nth-child(odd) {
        background-color: #FFFFFF;
    }

    /* Filas pares: celeste muy claro */
    .tabla-eventos tbody tr:nth-child(even) {
    background-color: #EEF7FA;
    }

    .tabla-eventos tbody tr:hover {
        background-color: #DDEFF7 !important;
    }

    .tabla-eventos tbody td {
        padding: 6px 10px;
        font-size: 11px;
        line-height: 1.2;
        white-space: nowrap !important;
        color: #263B54 !important;
        border-bottom: 1px solid #E1E7F0;
        border-right: 1px solid #E7EBF2;
        vertical-align: middle;
        text-align: center;
    }

    .tabla-eventos tbody td:first-child {
        text-align: left;
        font-weight: 400;
    }

    </style>
    """

    encabezados = "".join(
        f"<th>{escape(str(columna))}</th>"
        for columna in df.columns
    )

    filas = []

    for _, fila in df.iterrows():
        celdas = "".join(
            f"<td>{texto_tabla(valor)}</td>"
            for valor in fila.tolist()
        )
        filas.append(f"<tr>{celdas}</tr>")

    html = (
        css
        + '<div class="tabla-eventos-scroll">'
        + '<table class="tabla-eventos">'
        + f'<thead><tr>{encabezados}</tr></thead>'
        + '<tbody>'
        + "".join(filas)
        + '</tbody></table></div>'
    )

    st.html(html)


# =====================================================
# 9. CARGAR DATOS DE MONGODB
# =====================================================

@st.cache_data(ttl=300, show_spinner=False)
def obtener_datos():
    return cargar_eventos()


try:
    with st.spinner("Cargando datos desde MongoDB..."):
        events, inscripciones = obtener_datos()

except Exception as error:
    st.error("No se pudieron cargar los datos desde MongoDB.")
    st.exception(error)
    st.stop()


events = events.copy()
inscripciones = inscripciones.copy()

if events.empty:
    st.warning("No hay eventos registrados.")
    st.stop()


# =====================================================
# 10. PREPARAR ETIQUETAS DE EVENTOS
# =====================================================

catalogo = events[
    ["event_id", "title", "date"]
].copy()

catalogo["_id_texto"] = (
    catalogo["event_id"].astype(str)
)

catalogo["titulo_limpio"] = (
    catalogo["title"]
    .fillna("Sin título")
    .astype(str)
    .str.strip()
)

catalogo["fecha_orden"] = pd.to_datetime(
    catalogo["date"],
    errors="coerce",
    utc=True
)

catalogo = (
    catalogo.sort_values(
        ["titulo_limpio", "fecha_orden", "_id_texto"],
        kind="stable",
        na_position="last"
    )
    .drop_duplicates("_id_texto")
    .copy()
)

catalogo["repeticiones"] = (
    catalogo.groupby("titulo_limpio")[
        "_id_texto"
    ].transform("size")
)

catalogo["numero_repetido"] = (
    catalogo.groupby("titulo_limpio")
    .cumcount() + 1
)

catalogo["etiqueta"] = catalogo["titulo_limpio"]

repetidos = catalogo["repeticiones"] > 1

catalogo.loc[repetidos, "etiqueta"] = (
    catalogo.loc[repetidos, "titulo_limpio"]
    + " ("
    + catalogo.loc[
        repetidos, "numero_repetido"
    ].astype(str)
    + ")"
)

etiquetas_eventos = dict(
    zip(
        catalogo["_id_texto"],
        catalogo["etiqueta"]
    )
)

opciones_eventos = catalogo["_id_texto"].tolist()

modalidades = sorted(
    events["modality"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

fechas_validas = pd.to_datetime(
    events["date"],
    errors="coerce",
    utc=True
).dropna()

rango_default = None

if not fechas_validas.empty:
    rango_default = (
        fechas_validas.min().date(),
        fechas_validas.max().date()
    )

empresas_disponibles = events[
    ["companyName", "companyId"]
].copy()

empresas_disponibles["Empresa"] = (
    empresas_disponibles["companyName"]
    .fillna(empresas_disponibles["companyId"])
    .astype("string")
    .str.strip()
    .replace("", pd.NA)
)

opciones_empresas = sorted(
    empresas_disponibles["Empresa"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

opciones_categorias = sorted(
    events["category"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[lambda s: s.ne("")]
    .unique()
    .tolist()
)


def limpiar_filtros():
    # Restablecer todos los filtros a sus valores iniciales

    if rango_default is not None:
        st.session_state["f_fechas"] = rango_default

    st.session_state["f_evento"] = "Todos"
    st.session_state["f_modalidad"] = "Todas"

    st.session_state["f_empresa"] = (
        "Todas"
        if opciones_empresas
        else "Aún no hay datos"
    )

    st.session_state["f_categoria"] = (
        "Todas"
        if opciones_categorias
        else "Aún no hay datos"
    )

# =====================================================
# 11. BARRA LATERAL COMPACTA
# =====================================================

with st.sidebar:

    st.markdown("## Laboral.AI")
    st.caption("Análisis de eventos")

    st.divider()

    st.markdown("### Filtros")

    rango = None

    if rango_default is not None:
        rango = st.date_input(
            "Periodo de realización de los eventos",
            value=rango_default,
            min_value=rango_default[0],
            max_value=rango_default[1],
            key="f_fechas"
        )

    evento = st.selectbox(
        "Evento seleccionado",
        options=["Todos"] + opciones_eventos,
        format_func=lambda valor: (
            "Todos"
            if valor == "Todos"
            else etiquetas_eventos.get(
                valor,
                "Sin título"
            )
        ),
        key="f_evento"
    )

    modalidad = st.selectbox(
        "Modalidad del evento",
        ["Todas"] + modalidades,
        key="f_modalidad"
    )

    empresa = st.selectbox(
        "Empresa organizadora",
        (
            ["Todas"] + opciones_empresas
            if opciones_empresas
            else ["Aún no hay datos"]
        ),
        key="f_empresa",
        disabled=not bool(opciones_empresas)
    )

    categoria = st.selectbox(
        "Categoría del evento",
        (
            ["Todas"] + opciones_categorias
            if opciones_categorias
            else ["Aún no hay datos"]
        ),
        key="f_categoria",
        disabled=not bool(opciones_categorias)
    )

    st.divider()

    st.button(
        "Limpiar filtros",
        key="btn_limpiar",
        on_click=limpiar_filtros,
        use_container_width=True
    )

    if st.button(
        "Actualizar datos",
        key="btn_actualizar",
        use_container_width=True
    ):
        obtener_datos.clear()
        st.rerun()


# =====================================================
# 12. APLICAR FILTROS
# =====================================================

eventos_filtrados = events.copy()

if (
    isinstance(rango, (tuple, list))
    and len(rango) == 2
):
    fecha_inicio, fecha_fin = rango

    fechas = pd.to_datetime(
        eventos_filtrados["date"],
        errors="coerce",
        utc=True
    ).dt.date

    eventos_filtrados = eventos_filtrados[
        fechas.between(fecha_inicio, fecha_fin)
    ]

if evento != "Todos":
    eventos_filtrados = eventos_filtrados[
        eventos_filtrados["event_id"].astype(str) == evento
    ]

if modalidad != "Todas":
    eventos_filtrados = eventos_filtrados[
        eventos_filtrados["modality"].astype(str) == modalidad
    ]

if opciones_empresas and empresa != "Todas":

    nombres_empresa = (
        eventos_filtrados["companyName"]
        .fillna(eventos_filtrados["companyId"])
        .astype("string")
        .str.strip()
    )

    eventos_filtrados = eventos_filtrados[
        nombres_empresa.eq(empresa).fillna(False)
    ]

if opciones_categorias and categoria != "Todas":

    categorias_eventos = (
        eventos_filtrados["category"]
        .astype("string")
        .str.strip()
    )

    eventos_filtrados = eventos_filtrados[
        categorias_eventos.eq(categoria).fillna(False)
    ]

datos = inscripciones[
    inscripciones["event_id"].isin(
        eventos_filtrados["event_id"]
    )
].copy()


def nombre_evento_desde_id(event_id):
    return etiquetas_eventos.get(
        str(event_id),
        "Sin título"
    )


# =====================================================
# 13. ENCABEZADO
# =====================================================

st.title("Exploración por eventos")

st.caption(
    "Laboral.AI | Desempeño de eventos, "
    "inscripciones, participantes y certificados"
)


# =====================================================
# 14. KPI PRINCIPALES
# =====================================================

total_eventos = (
    eventos_filtrados["event_id"].nunique()
)

total_inscripciones = (
    datos["eventguest_id"].nunique()
)

participantes_unicos = (
    datos["email_key"].nunique()
)

asistencias = int(
    datos["status"].eq("ATTENDED").sum()
)

eventos_con_inscripciones = (
    datos["event_id"].nunique()
)

certificados_pagados = int(
    datos["certificado_pagado"].sum()
)

indicadores = [
    ("Total de eventos registrados", total_eventos),
    ("Total de inscripciones", total_inscripciones),
    ("Total de participantes distintos", participantes_unicos),
    ("Total de asistencias registradas", asistencias),
    ("Total de eventos con inscripciones", eventos_con_inscripciones)
]

mostrar_kpis(indicadores)


# =====================================================
# 15. HALLAZGOS CLAVE
# =====================================================

nombre_mejor = "Sin información"
mayor_registro = 0

ranking_hallazgos = (
    datos.groupby("event_id")["eventguest_id"]
    .nunique()
    .sort_values(ascending=False)
)

if not ranking_hallazgos.empty:

    mejor_id = ranking_hallazgos.index[0]
    mayor_registro = int(ranking_hallazgos.iloc[0])

    nombre_mejor = nombre_evento_desde_id(mejor_id)

nombre_mes, mayor_mes = obtener_mes_mayor_actividad(datos)

mostrar_hallazgos(
    nombre_evento=nombre_mejor,
    inscripciones_evento=mayor_registro,
    nombre_mes=nombre_mes,
    inscripciones_mes=mayor_mes,
    certificados_pagados=certificados_pagados
)


# =====================================================
# 16. DESEMPEÑO DE EVENTOS
# =====================================================

titulo_seccion("Desempeño de eventos")

col1, col2 = st.columns(2, gap="medium")


# -----------------------------------------------------
# TOTAL DE INSCRIPCIONES POR EVENTO
# AZUL MARINO
# -----------------------------------------------------

with col1:

    with st.container(
        border=True,
        key="cuadro_grafico_inscripciones1"
    ):

        st.subheader("Total de inscripciones por evento")

        ranking = (
            datos.groupby("event_id")["eventguest_id"]
            .nunique()
            .reset_index(name="Inscripciones")
        )

        if ranking.empty:
            sin_datos("Aún no hay inscripciones.")

        else:
            ranking = ranking.sort_values(
                "Inscripciones",
                ascending=False
            ).copy()

            ranking["_evento_id"] = (
                ranking["event_id"].astype(str)
            )

            ranking["Evento"] = (
                ranking["event_id"].map(
                    nombre_evento_desde_id
                )
            )

            fig = px.bar(
                ranking,
                x="Inscripciones",
                y="_evento_id",
                orientation="h",
                text="Inscripciones",
                custom_data=["Evento"],
                color_discrete_sequence=[COLOR_INSCRIPCIONES]
            )

            fig.update_traces(
                marker_color=tonos_grafico(
                    COLOR_INSCRIPCIONES,
                    len(ranking)
                ),
                hovertemplate=(
                    "%{customdata[0]}"
                    "<br>Inscripciones: %{x}"
                    "<extra></extra>"
                )
            )

            fig.update_yaxes(
                title=None,
                tickmode="array",
                tickvals=ranking["_evento_id"].tolist(),
                ticktext=ranking["Evento"].tolist(),
                categoryorder="total ascending"
            )

            grafico(fig, 370)


# -----------------------------------------------------
# EVOLUCIÓN DEL TOTAL DE INSCRIPCIONES
# VERDE CON SOMBREADO
# -----------------------------------------------------

with col2:

    with st.container (
        border=True,
        key="cuadro_grafico_inscripciones2"
    ):

        st.subheader("Evolución del total de inscripciones")

        temporal = datos.copy()

        temporal["registrationDate"] = pd.to_datetime(
            temporal["registrationDate"],
            errors="coerce",
            utc=True
        )

        temporal = temporal.dropna(
            subset=["registrationDate"]
        )

        if temporal.empty:
            sin_datos(
                "Aún no hay fechas válidas de inscripción."
            )

        else:

            temporal["Mes"] = (
                temporal["registrationDate"]
                .dt.strftime("%Y-%m")
            )

            mensual = (
                temporal.groupby("Mes")["eventguest_id"]
                .nunique()
                .reset_index(name="Inscripciones")
                .sort_values("Mes")
            )

            fig = px.line(
                mensual,
                x="Mes",
                y="Inscripciones",
                markers=True
            )

            fig.update_traces(
                line=dict(
                    color=COLOR_EVOLUCION,
                    width=3
                ),
                marker=dict(
                    color=COLOR_EVOLUCION,
                    size=7
                ),
                fill="tozeroy",
                fillcolor=color_transparente(
                    COLOR_EVOLUCION,
                    0.18
                )
            )

            fig.update_layout(showlegend=False)

            grafico(fig, 370)


# =====================================================
# 17. ESTADOS Y MODALIDAD
# =====================================================

if modalidad == "Todas":
    col3, col4 = st.columns(2, gap="medium")
else:
    col3 = st.container()
    col4 = None


# -----------------------------------------------------
# ESTADOS DE INSCRIPCIÓN
# LILA
# -----------------------------------------------------

with col3:

    with st.container(
        border=True,
        key="cuadro_grafico_inscripciones3"
    ):

        st.subheader("Estados de inscripción")

        estados = (
            datos["status"]
            .fillna("SIN INFORMACIÓN")
            .value_counts()
            .rename_axis("Estado")
            .reset_index(name="Cantidad")
        )

        if estados.empty:
            sin_datos("Aún no hay estados para mostrar.")

        else:
            fig = px.bar(
                estados,
                x="Estado",
                y="Cantidad",
                text="Cantidad",
                color_discrete_sequence=[COLOR_ESTADOS]
            )

            fig.update_traces(
                marker_color=tonos_grafico(
                    COLOR_ESTADOS,
                    len(estados)
                )
            )

            fig.update_layout(showlegend=False)

            grafico(fig)


# -----------------------------------------------------
# EVENTOS POR MODALIDAD
# TURQUESA
# -----------------------------------------------------

if modalidad == "Todas":

    with col4:

        with st.container(
            border=True,
            key="cuadro_grafico_eventos_modalidad4"
        ):

            st.subheader("Eventos por modalidad")

            tabla_modalidad = (
                eventos_filtrados["modality"]
                .fillna("No informado")
                .value_counts()
                .rename_axis("Modalidad")
                .reset_index(name="Eventos")
            )

            if tabla_modalidad.empty:
                sin_datos("No hay eventos disponibles.")

            else:
                colores_modalidad = tonos_grafico(
                    COLOR_MODALIDAD,
                    len(tabla_modalidad)
                )

                fig = px.pie(
                    tabla_modalidad,
                    names="Modalidad",
                    values="Eventos",
                    hole=0.58,
                    color_discrete_sequence=colores_modalidad
                )

                fig.update_traces(
                    marker=dict(colors=colores_modalidad)
                )

                grafico(fig)


# =====================================================
# 18. CATEGORÍAS Y TIPOS DE EVENTOS
# =====================================================

titulo_seccion("Categorías y tipos de eventos")

# Si se selecciona una categoría específica,
# ocultamos su gráfico y ampliamos Eventos por tipo.

if categoria in ["Todas", "Aún no hay datos"]:
    col5, col6 = st.columns(2, gap="medium")
else:
    col5 = None
    col6 = st.container()

# -----------------------------------------------------
# INSCRIPCIONES POR CATEGORÍA
# NARANJA
# -----------------------------------------------------

if categoria in ["Todas", "Aún no hay datos"]:

    with col5:

        with st.container(
            border=True,
            key="cuadro_grafico_inscripciones_categoria5"
        ):

            st.subheader("Inscripciones por categoría")

            categorias_validas = datos[
                datos["category"].notna()
            ].copy()

            if categorias_validas.empty:
                sin_datos(
                    "Aún no hay categorías registradas "
                    "en los eventos."
                )

            else:
                tabla_categorias = (
                    categorias_validas.groupby(
                        "category"
                    )["eventguest_id"]
                    .nunique()
                    .reset_index(name="Inscripciones")
                    .sort_values(
                        "Inscripciones",
                        ascending=False
                    )
                )

                fig = px.bar(
                    tabla_categorias,
                    x="Inscripciones",
                    y="category",
                    orientation="h",
                    color_discrete_sequence=[COLOR_CATEGORIAS]
                )

                fig.update_traces(
                    marker_color=tonos_grafico(
                        COLOR_CATEGORIAS,
                        len(tabla_categorias)
                    )
                )

                fig.update_yaxes(
                    title=None,
                    categoryorder="total ascending"
                )

                grafico(fig)


# -----------------------------------------------------
# EVENTOS POR TIPO
# AZUL MARINO
# -----------------------------------------------------

with col6:

    with st.container(
        border=True,
        key="cuadro_grafico_evetnos_tipo6"
    ):

        st.subheader("Eventos por tipo")

        tipos_validos = eventos_filtrados[
            eventos_filtrados["type"].notna()
        ]

        if tipos_validos.empty:
            sin_datos(
                "Aún no hay tipos de evento registrados."
            )

        else:
            tabla_tipos = (
                tipos_validos["type"]
                .value_counts()
                .rename_axis("Tipo")
                .reset_index(name="Eventos")
            )

            fig = px.bar(
                tabla_tipos,
                x="Tipo",
                y="Eventos",
                color_discrete_sequence=[COLOR_TIPOS]
            )

            fig.update_traces(
                marker_color=tonos_grafico(
                    COLOR_TIPOS,
                    len(tabla_tipos)
                )
            )

            grafico(fig)

# =====================================================
# 19. EMPRESAS ORGANIZADORAS
# =====================================================

# El gráfico solo se muestra cuando no se ha
# seleccionado una empresa específica.

if empresa in ["Todas", "Aún no hay datos"]:

    titulo_seccion("Empresas organizadoras")

    with st.container(
        border=True,
        key="cuadro_grafico_empresa"
    ):

        st.subheader("Inscripciones por empresa")

        empresas_validas = datos[
            datos["companyId"].notna()
            | datos["companyName"].notna()
        ].copy()

        if empresas_validas.empty:
            sin_datos(
                "Aún no hay información de empresas "
                "asociadas a los eventos."
            )

        else:
            empresas_validas["Empresa"] = (
                empresas_validas["companyName"]
                .fillna(empresas_validas["companyId"])
                .fillna("No informado")
            )

            tabla_empresas = (
                empresas_validas.groupby(
                    "Empresa"
                )["eventguest_id"]
                .nunique()
                .reset_index(name="Inscripciones")
                .sort_values(
                    "Inscripciones",
                    ascending=False
                )
            )

            fig = px.bar(
                tabla_empresas,
                x="Inscripciones",
                y="Empresa",
                orientation="h",
                color_discrete_sequence=[COLOR_EMPRESAS]
            )

            fig.update_traces(
                marker_color=tonos_grafico(
                    COLOR_EMPRESAS,
                    len(tabla_empresas)
                )
            )

            fig.update_yaxes(
                categoryorder="total ascending"
            )

            grafico(fig)


# =====================================================
# 20. ANÁLISIS DE PARTICIPANTES
# =====================================================

titulo_seccion("Análisis de participantes")

col7, col8 = st.columns(2, gap="medium")


# -----------------------------------------------------
# NUEVO GRÁFICO:
# CREACIÓN DE CUENTAS RESPECTO AL EVENTO
# AMARILLO DORADO #F8C64B
# -----------------------------------------------------

# Trabajamos solamente con los registros filtrados.
# Cada persona se contará una sola vez.

participantes_base = datos[
    datos["email_key"].notna()
].copy()

if not participantes_base.empty:

    # Relacionamos cada inscripción con la fecha
    # de realización de su evento.

    fechas_eventos = eventos_filtrados[
        ["event_id", "date"]
    ].drop_duplicates("event_id").rename(
        columns={"date": "fecha_evento"}
    )

    participantes_base = participantes_base.merge(
        fechas_eventos,
        on="event_id",
        how="left",
        validate="many_to_one"
    )

    participantes_base["registrationDate"] = pd.to_datetime(
        participantes_base["registrationDate"],
        errors="coerce",
        utc=True
    )

    participantes_base["fecha_evento"] = pd.to_datetime(
        participantes_base["fecha_evento"],
        errors="coerce",
        utc=True
    )

    participantes_base["fecha_cuenta"] = pd.to_datetime(
        participantes_base["fecha_creacion_usuario"],
        errors="coerce",
        utc=True
    )

    # Seleccionar la primera inscripción conocida
    # de cada participante. Es la misma regla de
    # la prueba realizada en la terminal.

    participantes_base = (
        participantes_base.sort_values(
            ["registrationDate", "fecha_evento"],
            kind="stable",
            na_position="last"
        )
        .drop_duplicates(
            subset="email_key",
            keep="first"
        )
        .copy()
    )

    # Comparamos fechas por día calendario,
    # manteniendo el mismo criterio UTC de la prueba.

    participantes_base["dia_evento"] = (
        participantes_base["fecha_evento"]
        .dt.normalize()
    )

    participantes_base["dia_cuenta"] = (
        participantes_base["fecha_cuenta"]
        .dt.normalize()
    )

    def clasificar_creacion_cuenta(fila):

        if not bool(fila["cuenta_identificada"]):
            return "Sin cuenta identificada"

        if (
            pd.isna(fila["dia_evento"])
            or pd.isna(fila["dia_cuenta"])
        ):
            return "Sin fecha suficiente"

        if fila["dia_cuenta"] < fila["dia_evento"]:
            return "Antes del evento"

        if fila["dia_cuenta"] == fila["dia_evento"]:
            return "El mismo día del evento"

        return "Después del evento"

    participantes_base["momento_cuenta"] = (
        participantes_base.apply(
            clasificar_creacion_cuenta,
            axis=1
        )
    )


with col7:

    with st.container(
        border=True,
        key="cuadro_grafico_cuentas7"
    ):

        st.subheader(
            "Creación de cuentas respecto al evento"
        )

        if participantes_base.empty:

            sin_datos(
                "Aún no hay participantes con correo "
                "para analizar."
            )

        else:

            orden_momentos = [
                "Antes del evento",
                "El mismo día del evento",
                "Después del evento",
                "Sin cuenta identificada",
                "Sin fecha suficiente"
            ]

            conteo_momentos = (
                participantes_base["momento_cuenta"]
                .value_counts()
                .reindex(
                    orden_momentos,
                    fill_value=0
                )
            )

            # Las tres categorías principales siempre
            # se muestran, incluso cuando alguna vale 0.
            # Las categorías de información faltante
            # aparecen solamente cuando existen.

            categorias_visibles = [
                "Antes del evento",
                "El mismo día del evento",
                "Después del evento"
            ]

            categorias_visibles += [
                categoria
                for categoria in orden_momentos[3:]
                if conteo_momentos[categoria] > 0
            ]

            tabla_creacion = (
                conteo_momentos
                .reindex(categorias_visibles)
                .rename_axis("Momento")
                .reset_index(name="Participantes")
            )

            colores_creacion = tonos_grafico(
                COLOR_CREACION_CUENTAS,
                len(tabla_creacion)
            )

            fig = px.bar(
                tabla_creacion,
                x="Participantes",
                y="Momento",
                orientation="h",
                text="Participantes",
                color_discrete_sequence=[
                    COLOR_CREACION_CUENTAS
                ]
            )

            # La primera barra lleva el amarillo
            # original y las restantes tonos claros.

            fig.update_traces(
                marker_color=colores_creacion,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "%{y}"
                    "<br>Participantes: %{x}"
                    "<extra></extra>"
                )
            )

            fig.update_yaxes(
                title=None,
                categoryorder="array",
                categoryarray=list(
                    reversed(categorias_visibles)
                )
            )

            fig.update_xaxes(
                title="Participantes distintos",
                rangemode="tozero"
            )

            fig.update_layout(
                showlegend=False,
                margin=dict(
                    l=15,
                    r=35,
                    t=20,
                    b=35
                ),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
            )

            grafico(fig, 350)




# -----------------------------------------------------
# RELACIÓN DE PARTICIPANTES CON LABORAL.AI
# ROSA FRAMBUESA #CF4786
# -----------------------------------------------------

with col8:

    with st.container(
        border=True,
        key="cuadro_grafico_participantes8"
    ):

        st.subheader(
            "Relación de los participantes con Laboral.AI"
        )

        if participantes_base.empty:

            sin_datos(
                "Aún no hay participantes con correo "
                "identificado."
            )

        else:

            # Para este gráfico buscamos identificar
            # si cada persona tiene cuenta en Laboral.AI.
            # No contamos varias veces la misma persona.

            participantes_relacion = datos[
                datos["email_key"].notna()
            ].copy()

            participantes_relacion["registrationDate"] = (
                pd.to_datetime(
                    participantes_relacion["registrationDate"],
                    errors="coerce",
                    utc=True
                )
            )

            participantes_relacion = (
                participantes_relacion.sort_values(
                    "registrationDate",
                    na_position="first",
                    kind="stable"
                )
                .drop_duplicates(
                    subset="email_key",
                    keep="last"
                )
                .copy()
            )

            tabla_usuarios = (
                participantes_relacion["tipo_usuario"]
                .fillna("No determinado")
                .replace({
                    "Sin cuenta identificada":
                        "Sin cuenta registrada identificada"
                })
                .value_counts()
                .rename_axis("Tipo")
                .reset_index(name="Participantes")
            )

            colores_usuarios = tonos_grafico(
                COLOR_RELACION_USUARIOS,
                len(tabla_usuarios)
            )

            fig = px.pie(
                tabla_usuarios,
                names="Tipo",
                values="Participantes",
                hole=0.58,
                color_discrete_sequence=colores_usuarios
            )

            fig.update_traces(
                marker=dict(
                    colors=colores_usuarios
                )
            )

            grafico(fig, 350)



# =====================================================
# 21. ANÁLISIS DE CERTIFICADOS
# =====================================================

titulo_seccion("Análisis de certificados")

eventos_con_certificado = int(
    eventos_filtrados["hasCertificate"]
    .eq(True)
    .sum()
)

pagados = datos[
    datos["certificado_pagado"].fillna(False)
].copy()

sin_precio_valido = int(
    pagados["importe_certificado_estimado"]
    .isna()
    .sum()
)

importe_total = pagados[
    "importe_certificado_estimado"
].sum(min_count=1)

if pd.isna(importe_total):
    importe_mostrado = (
        "0,00"
        if pagados.empty
        else "No disponible"
    )
else:
    importe_mostrado = (
        f"{importe_total:,.2f}"
        .replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
    )

mostrar_tarjetas_certificados([
    (
        "Eventos que ofrecen certificado",
        numero(eventos_con_certificado)
    ),
    (
        "Certificados marcados como pagados",
        numero(certificados_pagados)
    ),
    (
        "Importe asociado a certificados pagados",
        importe_mostrado
    )
])

st.caption(
    "Importe estimado a partir del precio "
    "y el estado de pago registrados para "
    "los certificados."
)

if sin_precio_valido > 0:
    st.warning(
        f"Hay {sin_precio_valido} certificados "
        "marcados como pagados sin importe calculable."
    )


# -----------------------------------------------------
# CERTIFICADOS PAGADOS POR EVENTO
# AZUL MARINO #12365B
# -----------------------------------------------------

with st.container(
    border=True,
    key="cuadro_grafico_certificados"
):

    st.subheader("Certificados pagados por evento")

    certificados_evento = (
        pagados.groupby("event_id")["eventguest_id"]
        .nunique()
        .reset_index(name="Certificados pagados")
    )

    if certificados_evento.empty:

        sin_datos(
            "Todavía no hay certificados "
            "marcados como pagados."
        )

    else:

        certificados_evento = (
            certificados_evento.sort_values(
                "Certificados pagados",
                ascending=False
            ).copy()
        )

        certificados_evento["_evento_id"] = (
            certificados_evento["event_id"].astype(str)
        )

        certificados_evento["Evento"] = (
            certificados_evento["event_id"]
            .map(nombre_evento_desde_id)
        )

        fig = px.bar(
            certificados_evento,
            x="Certificados pagados",
            y="_evento_id",
            orientation="h",
            text="Certificados pagados",
            custom_data=["Evento"],
            color_discrete_sequence=[COLOR_CERTIFICADOS]
        )

        # Degradado dinámico:
        # funciona para 1, 3, 6, 10 o más eventos.

        fig.update_traces(
            marker_color=tonos_grafico(
                COLOR_CERTIFICADOS,
                len(certificados_evento)
            ),
            hovertemplate=(
                "%{customdata[0]}"
                "<br>Certificados pagados: %{x}"
                "<extra></extra>"
            )
        )

        fig.update_yaxes(
            title=None,
            tickmode="array",
            tickvals=certificados_evento[
                "_evento_id"
            ].tolist(),
            ticktext=certificados_evento[
                "Evento"
            ].tolist(),
            categoryorder="total ascending"
        )

        grafico(fig)


# =====================================================
# 22. DETALLE DE EVENTOS
# =====================================================

titulo_seccion("Detalle de eventos")

with st.container(
    border=True,
    key="cuadro_tabla_eventos"
):

    conteos = (
        datos.groupby("event_id")
        .agg(
            inscripciones=(
                "eventguest_id",
                "nunique"
            ),
            participantes=(
                "email_key",
                "nunique"
            ),
            asistencias=(
                "status",
                lambda s: int(
                    s.eq("ATTENDED").sum()
                )
            ),
            certificados=(
                "certificado_pagado",
                "sum"
            )
        )
        .reset_index()
    )

    tabla = eventos_filtrados[
        [
            "event_id",
            "title",
            "date",
            "modality",
            "category",
            "type",
            "companyName",
            "registrationType",
            "hasCertificate",
            "certificatePrice"
        ]
    ].merge(
        conteos,
        on="event_id",
        how="left",
        validate="one_to_one"
    )

    for columna in [
        "inscripciones",
        "participantes",
        "asistencias",
        "certificados"
    ]:
        tabla[columna] = (
            tabla[columna]
            .fillna(0)
            .astype(int)
        )

    tabla["Fecha"] = pd.to_datetime(
        tabla["date"],
        errors="coerce",
        utc=True
    ).dt.strftime("%Y-%m-%d")

    tabla["Evento"] = (
        tabla["event_id"]
        .map(nombre_evento_desde_id)
    )

    tabla["Modalidad"] = (
        tabla["modality"].fillna("No informado")
    )

    tabla["Categoría"] = (
        tabla["category"].fillna("No informado")
    )

    tabla["Tipo"] = (
        tabla["type"].fillna("No informado")
    )

    tabla["Empresa"] = (
        tabla["companyName"].fillna("No informado")
    )

    tabla["Registro"] = (
        tabla["registrationType"].fillna("No informado")
    )

    tabla["Ofrece certificado"] = (
        tabla["hasCertificate"]
        .map({
            True: "Sí",
            False: "No"
        })
        .fillna("No informado")
    )

    tabla["Precio certificado"] = (
        tabla["certificatePrice"]
    )

    tabla_visible = tabla[
        [
            "Evento",
            "Fecha",
            "Modalidad",
            "Categoría",
            "Tipo",
            "Empresa",
            "Registro",
            "inscripciones",
            "participantes",
            "asistencias",
            "Ofrece certificado",
            "Precio certificado",
            "certificados"
        ]
    ].rename(
        columns={
            "inscripciones": "Inscripciones",
            "participantes": "Participantes únicos",
            "asistencias": "Asistencias registradas",
            "certificados": "Certificados pagados"
        }
    )
    # La tabla se mantiene visible
    mostrar_tabla_eventos(tabla_visible)


# =====================================================
# 23. PIE DE PÁGINA
# =====================================================

st.caption(
    "Fuente: MongoDB | Colecciones events, "
    "eventguests y users. "
    "Todos los indicadores responden a los filtros."
)
