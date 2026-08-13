# Documentación de la Sección 1 — Infraestructura Docker

## Proyecto Tenate

### Ecosistema Edge-AI de Inferencia Bayesiana

**Estado de la Sección 1:** Completada  
**Etiqueta de cierre:** `seccion-1`  
**Commit de cierre:** `3eed65f`  
**Repositorio oficial:** https://github.com/0261490/Proyecto_Queso_Tanate_Universidad_Panamericana

---

## 1. Objetivo de la Sección 1

La Sección 1 tuvo como objetivo construir y validar una infraestructura Docker reproducible para Proyecto Tenate.

El entorno debía permitir trabajar con los componentes Python y Node.js del proyecto sin depender de instalaciones locales específicas de cada sistema operativo y debía servir como base para las siguientes secciones del desarrollo.

Los objetivos principales fueron:

- definir un entorno Python reproducible;
- definir un entorno Node.js reproducible;
- centralizar las dependencias Python;
- fijar las versiones utilizadas;
- validar la construcción desde cero;
- comprobar el montaje del repositorio dentro de los contenedores;
- documentar la configuración y las pruebas;
- mantener todos los cambios sincronizados con GitHub.

---

## 2. Arquitectura Docker

El proyecto utiliza dos servicios principales definidos mediante Docker Compose:

```text
Proyecto Tenate
│
├── Servicio Python
│   ├── Python
│   ├── pgmpy
│   ├── numpy
│   ├── pandas
│   ├── scipy
│   ├── networkx
│   ├── joblib
│   └── pydantic
│
└── Servicio Node
    ├── Node.js
    └── npm
```

Los dos servicios trabajan sobre el repositorio montado en:

```text
/workspace
```

---

## 3. Archivos Principales

La infraestructura desarrollada y documentada en esta sección utiliza principalmente:

```text
proyecto-tenate/
├── docker/
│   ├── python.Dockerfile
│   └── node.Dockerfile
│
├── docs/
│   ├── docker-setup.md
│   └── seccion-1-validacion.md
│
├── model-export/
│   ├── requirements.txt
│   └── requirements.lock.txt
│
├── .dockerignore
├── docker-compose.yml
└── README.md
```

---

## 4. Entorno Python

La imagen base quedó fijada en:

```text
python:3.12.13-slim
```

Versiones principales validadas:

```text
Python      3.12.13
pip         26.2.1
pgmpy       1.1.2
numpy       2.5.2
pandas      3.0.5
scipy       1.18.0
networkx    3.6.1
joblib      1.5.3
pydantic    2.13.4
```

El archivo:

```text
model-export/requirements.txt
```

contiene las dependencias directas con versiones exactas.

El archivo:

```text
model-export/requirements.lock.txt
```

contiene el conjunto completo de 35 paquetes instalados y bloqueados.

---

## 5. Entorno Node.js

La imagen base quedó fijada en:

```text
node:24.19.0-bookworm
```

Versiones validadas:

```text
Node.js     24.19.0
npm         11.17.0
```

---

## 6. Construcción Reproducible

La construcción limpia se validó utilizando:

```bash
docker compose build --no-cache
```

Resultado:

```text
Image proyecto-tenate-python Built
Image proyecto-tenate-node   Built
```

Esto permitió comprobar que las imágenes podían reconstruirse desde cero utilizando únicamente los archivos versionados del proyecto.

---

## 7. Validaciones Ejecutadas

### 7.1 Docker Compose

Se validó la configuración mediante:

```bash
docker compose config --quiet
```

No se reportaron errores.

Los servicios reconocidos fueron:

```text
node
python
```

### 7.2 Stack Python

Se verificó la importación conjunta de las dependencias principales.

Resultado:

```text
PYTHON_STACK_OK
```

### 7.3 Node.js

Se verificó la ejecución del contenedor Node.

Resultado:

```text
v24.19.0
NODE_OK
```

### 7.4 npm

Resultado:

```text
11.17.0
```

### 7.5 Montaje del Repositorio

Se comprobó que los contenedores podían acceder correctamente al repositorio dentro de:

```text
/workspace
```

Resultado:

```text
WORKSPACE_OK
```

### 7.6 Equivalencia del Lock

Se comparó el entorno Python instalado con el archivo lock mediante:

```powershell
docker compose run --rm python python -m pip freeze | Compare-Object (Get-Content model-export\requirements.lock.txt)
```

El comando no produjo diferencias.

Esto confirmó que:

```text
pip freeze == requirements.lock.txt
```

para el entorno validado.

### 7.7 Estado de Git

Después de las pruebas finales:

```bash
git status
```

reportó:

```text
nothing to commit, working tree clean
```

---

## 8. Documentación Generada

Durante la Sección 1 se generaron los siguientes documentos principales:

### `README.md`

Describe:

- objetivo general del proyecto;
- arquitectura;
- estructura del repositorio;
- entorno Docker;
- comandos de verificación;
- estado de las secciones;
- referencia científica principal.

### `docs/docker-setup.md`

Documenta:

- requisitos;
- construcción de imágenes;
- servicios Docker;
- pruebas Python;
- pruebas Node.js;
- montaje `/workspace`;
- limpieza de contenedores;
- reconstrucción;
- reproducibilidad.

### `docs/seccion-1-validacion.md`

Registra:

- construcción limpia;
- versiones finales;
- validación de dependencias;
- validación Node;
- validación del montaje;
- comparación contra el lock;
- alcance científico de la validación;
- resultado final de la Sección 1.

---

## 9. Historial de Commits de la Sección 1

Los principales commits realizados durante el cierre fueron:

```text
e3fee7b  Sección 1: completar README del proyecto
5dbae19  Sección 1: documentar configuración Docker
61ab6b2  Sección 1: fijar entorno Docker reproducible
3eed65f  Sección 1: cerrar infraestructura Docker
```

El commit de cierre fue:

```text
3eed65f
```

---

## 10. Etiqueta de Cierre

La Sección 1 fue etiquetada mediante:

```text
seccion-1
```

El tag anotado contiene el mensaje:

```text
Sección 1: infraestructura Docker reproducible completada
```

El tag se encuentra publicado en el repositorio remoto.

---

## 11. Alcance Científico

La reproducibilidad demostrada durante esta sección corresponde al **entorno de ingeniería actual**.

El artículo científico que origina el proyecto documenta el uso de:

```text
pgmpy 0.1.23
GeNIe Modeler 4.1
```

El entorno actual de ingeniería utiliza:

```text
pgmpy 1.1.2
```

Por lo tanto, la Sección 1 no afirma todavía equivalencia científica entre ambos entornos.

La equivalencia deberá comprobarse posteriormente cuando el modelo científico original se encuentre disponible en `model-source/`.

La validación futura deberá comprobar como mínimo:

- nodos;
- estados;
- estructura del DAG;
- dependencias;
- Tablas de Probabilidad Condicional (CPT);
- inferencias de referencia;
- resultados probabilísticos.

Una referencia científica que deberá preservarse es:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
```

---

## 12. Criterios de Finalización Cumplidos

```text
[OK] Docker Desktop validado
[OK] Docker Engine validado
[OK] Docker Compose validado
[OK] Servicio Python reproducible
[OK] Servicio Node reproducible
[OK] Python fijado
[OK] pip fijado
[OK] Node.js fijado
[OK] npm validado
[OK] Dependencias directas fijadas
[OK] Dependencias transitivas bloqueadas
[OK] Build limpio con --no-cache
[OK] Stack Python funcional
[OK] Node funcional
[OK] Montaje /workspace funcional
[OK] requirements.lock.txt reproducido sin diferencias
[OK] README actualizado
[OK] Documentación Docker creada
[OK] Documento de validación creado
[OK] Commits realizados
[OK] Cambios enviados a GitHub
[OK] Tag seccion-1 creado
[OK] Tag seccion-1 publicado en GitHub
```

---

## 13. Resultado Final

La **Sección 1 — Infraestructura Docker** de Proyecto Tenate quedó completada y validada.

El proyecto cuenta ahora con una base reproducible para continuar con las siguientes secciones de desarrollo.

El siguiente bloque de trabajo corresponde a:

```text
Sección 2 — Exportador del Modelo Bayesiano
```

Antes de implementar el exportador deberá recuperarse y auditarse el modelo científico original que alimentará el proceso de exportación.
