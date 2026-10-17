# Laboral.AI — Dashboard de Eventos

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un dashboard interactivo para el módulo de **Eventos de Laboral.AI**, diseñado para analizar la información de eventos, inscripciones, participantes y certificados.

El dashboard utiliza datos de MongoDB y presenta indicadores, gráficos y filtros interactivos que facilitan el seguimiento de la actividad de los eventos.

## Objetivo general

Diseñar e implementar un dashboard que permita analizar el desempeño de los eventos registrados en Laboral.AI y facilitar la interpretación de sus principales indicadores.

## Funcionalidades

- Indicadores de eventos, inscripciones, participantes y asistencias registradas.
- Identificación del evento con mayor cantidad de inscripciones.
- Evolución mensual de las inscripciones.
- Análisis de estados de inscripción y modalidades.
- Análisis de categorías, tipos y empresas organizadoras, cuando exista información disponible.
- Análisis de participantes y fechas de creación de cuentas.
- Indicadores de certificados y certificados pagados por evento.
- Tabla de detalle de eventos.
- Filtros interactivos por fecha, evento, modalidad, empresa y categoría.

## Tecnologías utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- MongoDB
- PyMongo
- Python-dotenv

## Fuentes de datos

El dashboard utiliza las colecciones `events`, `eventguests` y `users` de MongoDB.

## Consideraciones

- Los datos se obtienen de MongoDB.
- Los indicadores responden a los filtros seleccionados.
- Las inscripciones sin un evento asociado no se incluyen en los indicadores del dashboard.
- Los gráficos que aún no disponen de datos muestran mensajes informativos.
- Las credenciales de acceso a MongoDB no deben publicarse en GitHub.