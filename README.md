# Establecimientos de Salud en Chile

Aplicación web interactiva desarrollada en Python + Streamlit que consume la API REST pública del portal de datos del gobierno de Chile ([datos.gob.cl](https://datos.gob.cl)) para visualizar y analizar los **5.644 establecimientos de salud** registrados en el Ministerio de Salud.

## Información académica

- **Asignatura:** Taller de Programación II
- **Evaluación:** Solemne II
- **Universidad:** Universidad San Sebastián
- **Integrantes:**
  - Claudia Martinez
  - Céssar Leiva

## Funcionalidades

- Descarga en vivo de datos desde la API REST de datos.gob.cl (CKAN 2.10).
- **Filtros interactivos** por región, tipo de establecimiento, dependencia administrativa y servicio de urgencia.
- **Métricas dinámicas** que se recalculan al cambiar los filtros.
- **Tres vistas** organizadas en pestañas:
  - Tabla de datos filtrados
  - Gráficos analíticos (distribución por región, tipo y dependencia)
  - Mapa interactivo con la ubicación geográfica de cada establecimiento

## Tecnologías utilizadas

- **Python 3.11+**
- **requests** — consumo de la API REST
- **pandas** — análisis y procesamiento de datos
- **matplotlib** — visualización gráfica
- **streamlit** — interfaz web interactiva

## Estructura del proyecto

```
Solemne2-API-Chile/
├── api.py              # Cliente POO para la API de datos.gob.cl
├── app.py              # Aplicación Streamlit (interfaz principal)
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```

## Cómo ejecutar la aplicación

1. Clonar el repositorio:
```
   git clone https://github.com/cmartineznut-alt/Solemne2-API-Chile.git
   cd Solemne2-API-Chile
```

2. Instalar las dependencias:
```
   pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```
   streamlit run app.py
```

4. La aplicación se abrirá automáticamente en el navegador en `http://localhost:8501`.