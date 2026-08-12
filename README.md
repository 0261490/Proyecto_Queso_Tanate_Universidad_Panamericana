# Proyecto Tenate

## Ecosistema Edge-AI de Inferencia Bayesiana

### Aplicación de Resiliencia Comercial para Productores Artesanales de Queso Tenate

---

## Descripción

Proyecto Tenate es un ecosistema de inferencia bayesiana diseñado para apoyar la resiliencia comercial de productores artesanales de Queso Tenate.

El sistema permitirá ejecutar inferencia bayesiana completamente en el cliente mediante una aplicación web progresiva (PWA), sin depender de una conexión constante a Internet.

El modelo científico será desarrollado y validado en Python utilizando `pgmpy`, exportado a un formato portable `JSON` y posteriormente interpretado por un motor de inferencia escrito en TypeScript.

---

## Objetivo General

Construir un ecosistema reproducible y portable que permita:

- entrenar y validar una Red Bayesiana en Python;
- exportar automáticamente el modelo;
- ejecutar inferencia exacta en TypeScript;
- funcionar completamente offline;
- almacenar historial de inferencias localmente;
- proporcionar una interfaz intuitiva para productores artesanales;
- mantener el desarrollo respaldado y versionado en GitHub.

---

## Arquitectura General

```text
                     Usuario
                        |
                        v
             Interfaz amigable (PWA)
                        |
                        v
             Traductor de Evidencia
                        |
                        v
         Evidencia Bayesiana (Q1-Q8)
                        |
                        v
      Motor Bayesiano TypeScript
                        |
                        v
              Probabilidades
                        |
                        v
             Resultados al usuario
```

La arquitectura separa completamente la capa científica de la capa de interacción.

### Capa Científica

Incluye:

- estructura de la Red Bayesiana;
- DAG;
- estados;
- Tablas de Probabilidad Condicional (CPT);
- variables Q1-Q8;
- inferencia probabilística.

La interfaz no debe modificar esta capa.

### Capa de Interacción

Incluye:

- preguntas amigables;
- controles de usuario;
- validación de respuestas;
- iconografía;
- traducción de respuestas a evidencia bayesiana.

---

## Estructura del Repositorio

```text
proyecto-tenate/

├── docker/
│   ├── node.Dockerfile
│   └── python.Dockerfile
│
├── docs/
│
├── inference-engine/
│
├── model-export/
│   └── requirements.txt
│
├── model-source/
│
├── pwa-app/
│
├── tests/
│
├── .dockerignore
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Requisitos

Para trabajar con el proyecto se recomienda utilizar:

- Git;
- Docker Desktop;
- Docker Compose;
- Visual Studio Code.

El entorno de desarrollo está diseñado para utilizar contenedores Docker y reducir las dependencias directas del sistema operativo anfitrión.

---

## Entorno Docker

El proyecto cuenta actualmente con dos servicios principales.

### Python

Utilizado para:

- modelo bayesiano;
- exportación del modelo;
- validación científica;
- pruebas de referencia.

### Node

Utilizado para:

- motor de inferencia TypeScript;
- desarrollo de la PWA;
- herramientas del ecosistema JavaScript.

---

## Construcción del Entorno

Desde la raíz del proyecto:

```bash
docker compose build
```

Para reconstruir completamente las imágenes sin utilizar caché:

```bash
docker compose build --no-cache
```

---

## Verificación del Entorno Python

Comprobar la versión de Python:

```bash
docker compose run --rm python python --version
```

Comprobar que `pgmpy` está disponible:

```bash
docker compose run --rm python python -c "import pgmpy; print(pgmpy.__version__)"
```

---

## Verificación del Entorno Node

Comprobar Node.js:

```bash
docker compose run --rm node node --version
```

Comprobar npm:

```bash
docker compose run --rm node npm --version
```

---

## Verificación del Montaje del Proyecto

El repositorio local se monta dentro de los contenedores en:

```text
/workspace
```

Puede comprobarse con:

```bash
docker compose run --rm python ls -la /workspace
```

---

## Estado Actual

### Sección 0

Arquitectura inicial y planificación del proyecto.

**Estado:** Completada.

### Sección 1

Infraestructura Docker reproducible.

Hasta el momento se ha validado:

- Docker Desktop;
- Docker Engine;
- Docker Compose;
- construcción de la imagen Python;
- construcción de la imagen Node;
- ejecución de Python dentro del contenedor;
- ejecución de Node.js dentro del contenedor;
- ejecución de npm;
- importación de dependencias Python;
- montaje del repositorio en `/workspace`;
- integración de `requirements.txt` con el Dockerfile Python;
- configuración de `.dockerignore`;
- sincronización del repositorio local con GitHub.

**Estado:** En proceso de cierre y documentación.

### Sección 2

Exportador del modelo bayesiano.

**Estado:** Pendiente.

---

## Modelo Científico

El proyecto se basa en una Red Bayesiana desarrollada para analizar factores relacionados con la intención de compra del Queso Tenate.

Una de las referencias científicas que posteriormente deberá utilizarse para validar la equivalencia de las implementaciones es:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
```

La estructura científica, los estados, las dependencias y las Tablas de Probabilidad Condicional no deberán modificarse desde la capa de interfaz.

---

## Repositorio Oficial

GitHub:

```text
https://github.com/0261490/Proyecto_Queso_Tanate_Universidad_Panamericana
```

---

## Política de Desarrollo

El proyecto se desarrolla por secciones.

Cada sección deberá terminar con:

1. desarrollo completo;
2. pruebas;
3. validación;
4. documentación;
5. commit descriptivo;
6. push a GitHub;
7. tag de versión cuando corresponda.

No se deberá avanzar a la siguiente sección hasta completar la sección actual al 100%.

---

## Licencia

La licencia del proyecto todavía está pendiente de definición.
