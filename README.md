# Pipeline de monitorización automática del avance de obra en plantas fotovoltaicas

Trabajo Fin de Máster · Máster en Big Data & Data Engineering (UCM)
Autor: Gonzalo Zubía López · Tutores: Jorge Centeno y Alberto González

## Descripción

Pipeline de datos en Microsoft Fabric que estima el avance de la obra de una planta
fotovoltaica a partir de imágenes aéreas. Para cada zona de la planta detecta en qué fase está la obra (terreno sin tocar, movimiento de tierras, estructuras sin paneles o paneles instalados) y calcula el % de avance, los paneles instalados y la potencia montada.

**Caso de estudio:** planta Núñez de Balboa (Badajoz, 500 MWp, ~1.000 ha). Se usan las
ortofotos del PNOA histórico del IGN de 2016 (antes de la obra), 2019 (en construcción) y 2022 (terminada), que hacen el papel de los vuelos de dron que tendría en caso de usarse en una obra en construccion real.

**Resultado:** 1 % de avance en 2016, 20 % en 2019 (unos 286.000 paneles y 100 MWp)
y 100 % en 2022.

## Contenido del repositorio

- `notebooks/` – notebooks de Microsoft Fabric del pipeline (Bronze, Silver, Gold) y de las pruebas.
- `pipelines/` – exportación del Data Pipeline `Pl_obra_semanal` que los ejecuta cada semana.
- `powerbi/` – modelo semántico (TMDL) e informe en PDF.
- `src/avance_obra/` – paquete de Python con la lógica principal, extraída de los notebooks.
- `tests/` – tests unitarios del paquete (pytest), ejecutados con GitHub Actions en cada cambio.

El pipeline se desarrolló en Fabric. Como la integración de Fabric con GitHub está
deshabilitada en la cuenta de la universidad, la lógica principal se extrajo después
al paquete `avance_obra` para poder versionarla y cubrirla con tests.
