# Validación Final — Sección 1

## Proyecto Tenate

### Infraestructura Docker Reproducible

Este documento registra la validación final de la **Sección 1 — Infraestructura Docker** de Proyecto Tenate.

El objetivo de esta validación es comprobar que el entorno de ingeniería puede reconstruirse desde cero y producir las mismas versiones de herramientas y dependencias definidas en el repositorio.

---

## 1. Resultado General

La validación de infraestructura Docker fue satisfactoria.

Se verificó:

- configuración válida de Docker Compose;
- reconocimiento de los servicios `node` y `python`;
- construcción limpia de ambas imágenes con `--no-cache`;
- ejecución correcta del entorno Python;
- ejecución correcta del entorno Node.js;
- importación de las dependencias principales;
- montaje correcto del repositorio en `/workspace`;
- coincidencia exacta entre las dependencias instaladas y `requirements.lock.txt`;
- repositorio Git limpio después de las pruebas.

---

## 2. Construcción Limpia

Comando utilizado:

```bash
docker compose build --no-cache
```

Resultado:

```text
Image proyecto-tenate-python Built
Image proyecto-tenate-node   Built
```

La construcción se realizó sin reutilizar la caché de Docker.

---

## 3. Versiones del Entorno Python

Versión de Python validada:

```text
Python 3.12.13
```

Versión de pip validada:

```text
pip 26.2.1
```

Dependencias principales validadas:

```text
pgmpy      1.1.2
numpy      2.5.2
pandas     3.0.5
scipy      1.18.0
networkx   3.6.1
joblib     1.5.3
pydantic   2.13.4
```

La imagen base utilizada es:

```text
python:3.12.13-slim
```

---

## 4. Lock de Dependencias Python

El archivo:

```text
model-export/requirements.lock.txt
```

contiene 35 dependencias con versiones exactas.

Se verificó la equivalencia entre el archivo lock y el entorno realmente instalado mediante:

```powershell
docker compose run --rm python python -m pip freeze | Compare-Object (Get-Content model-export\requirements.lock.txt)
```

Resultado:

```text
Sin diferencias.
```

Por lo tanto, el conjunto de paquetes instalado coincide con el lock almacenado en el repositorio.

---

## 5. Versiones del Entorno Node

Versión de Node.js validada:

```text
v24.19.0
```

Versión de npm validada:

```text
11.17.0
```

La imagen base utilizada es:

```text
node:24.19.0-bookworm
```

---

## 6. Validación de Docker Compose

Se verificó la configuración con:

```bash
docker compose config --quiet
```

No se reportaron errores.

Servicios reconocidos:

```text
node
python
```

---

## 7. Validación del Stack Python

Se comprobó la importación conjunta de:

```text
pgmpy
numpy
pandas
scipy
networkx
joblib
pydantic
```

Resultado:

```text
PYTHON_STACK_OK
```

---

## 8. Validación de Node

Se ejecutó Node.js dentro del contenedor.

Resultado:

```text
v24.19.0
NODE_OK
```

También se verificó npm:

```text
11.17.0
```

---

## 9. Validación del Montaje `/workspace`

Se comprobó que el contenedor Python puede acceder a archivos esenciales del repositorio montado en:

```text
/workspace
```

Se verificó la presencia de:

```text
/workspace/README.md
/workspace/docs/docker-setup.md
/workspace/model-export/requirements.lock.txt
```

Resultado:

```text
WORKSPACE_OK
```

---

## 10. Estado de Contenedores Después de las Pruebas

El comando:

```bash
docker compose ps -a
```

no mostró contenedores residuales de las pruebas ejecutadas con `--rm`.

---

## 11. Estado de Git Después de la Validación

El comando:

```bash
git status --short
```

no mostró modificaciones.

Esto confirma que las pruebas de validación no alteraron el repositorio.

---

## 12. Referencia Científica y Alcance de Esta Validación

El entorno reproducible definido en esta sección corresponde al **entorno de ingeniería actual del proyecto**.

La investigación científica original documenta el uso de:

```text
pgmpy 0.1.23
GeNIe Modeler 4.1
```

El entorno actual utiliza:

```text
pgmpy 1.1.2
```

Por lo tanto, esta sección no afirma todavía equivalencia científica entre ambas versiones.

La equivalencia científica deberá comprobarse posteriormente utilizando el modelo fuente original, incluyendo:

- estructura del DAG;
- estados;
- Tablas de Probabilidad Condicional (CPT);
- consultas de inferencia;
- resultados de referencia.

El repositorio todavía no contiene el modelo científico original dentro de `model-source/`, por lo que esa validación pertenece a una etapa posterior del proyecto.

---

## 13. Resultado de la Sección 1

La infraestructura Docker cumple con los criterios técnicos de reproducibilidad definidos para esta etapa:

```text
[OK] Docker Compose válido
[OK] Servicio Python reproducible
[OK] Servicio Node reproducible
[OK] Python fijado
[OK] pip fijado
[OK] Dependencias Python bloqueadas
[OK] Node fijado
[OK] npm verificado
[OK] Build limpio exitoso
[OK] Stack Python funcional
[OK] Node funcional
[OK] Montaje /workspace funcional
[OK] Lock reproducido sin diferencias
[OK] Git limpio después de las pruebas
```

Con estas pruebas, la infraestructura de ingeniería de la **Sección 1 — Infraestructura Docker** queda técnicamente validada.

El cierre formal de la sección requiere todavía:

1. incorporar este documento al repositorio;
2. actualizar el estado de la Sección 1 en `README.md`;
3. realizar el commit y push de cierre;
4. crear y publicar la etiqueta `seccion-1`.
