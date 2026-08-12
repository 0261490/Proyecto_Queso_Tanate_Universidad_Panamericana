# Configuración del Entorno Docker

## Proyecto Tenate

Este documento describe cómo construir, ejecutar y verificar el entorno Docker de **Proyecto Tenate**.

El objetivo del entorno es proporcionar una base reproducible para el desarrollo del ecosistema Edge-AI, evitando depender de instalaciones locales de Python o Node.js y facilitando la ejecución del proyecto en Windows, Linux y macOS.

---

## 1. Requisitos

Antes de comenzar, el equipo debe contar con:

- Git;
- Docker Desktop o Docker Engine;
- Docker Compose;
- acceso al repositorio del proyecto.

Repositorio oficial:

```text
https://github.com/0261490/Proyecto_Queso_Tanate_Universidad_Panamericana
```

No es necesario instalar Python, Node.js ni npm directamente en el sistema operativo anfitrión para utilizar los contenedores del proyecto.

---

## 2. Estructura Docker del Proyecto

Los archivos principales relacionados con Docker son:

```text
proyecto-tenate/
├── docker/
│   ├── node.Dockerfile
│   └── python.Dockerfile
├── model-export/
│   └── requirements.txt
├── .dockerignore
└── docker-compose.yml
```

El archivo `docker-compose.yml` define dos servicios:

- `python`;
- `node`.

Ambos montan el repositorio local dentro del contenedor en:

```text
/workspace
```

---

## 3. Servicio Python

El servicio `python` utiliza el archivo:

```text
docker/python.Dockerfile
```

Su propósito es proporcionar el entorno necesario para:

- trabajar con la Red Bayesiana;
- ejecutar herramientas de exportación;
- validar dependencias científicas;
- ejecutar pruebas de referencia.

Las dependencias Python se instalan desde:

```text
model-export/requirements.txt
```

Esto evita mantener una segunda lista manual de dependencias dentro del Dockerfile.

---

## 4. Servicio Node

El servicio `node` utiliza:

```text
docker/node.Dockerfile
```

Su propósito es proporcionar el entorno para:

- desarrollar el motor de inferencia en TypeScript;
- desarrollar la PWA;
- utilizar herramientas del ecosistema Node.js y npm.

---

## 5. Construcción del Entorno

Desde la raíz del repositorio:

```bash
docker compose build
```

Este comando construye las imágenes de los servicios definidos en `docker-compose.yml`.

Para forzar una reconstrucción completa y evitar el uso de caché:

```bash
docker compose build --no-cache
```

---

## 6. Verificación de Docker y Docker Compose

Comprobar Docker:

```bash
docker --version
```

Comprobar Docker Compose:

```bash
docker compose version
```

Comprobar que Compose reconoce los servicios del proyecto:

```bash
docker compose config --services
```

El resultado esperado es:

```text
node
python
```

El orden puede variar sin afectar el funcionamiento.

---

## 7. Verificación del Entorno Python

Comprobar la versión de Python dentro del contenedor:

```bash
docker compose run --rm python python --version
```

Comprobar que `pgmpy` puede importarse:

```bash
docker compose run --rm python python -c "import pgmpy; print(pgmpy.__version__)"
```

También puede comprobarse que las principales dependencias están disponibles:

```bash
docker compose run --rm python python -c "import pgmpy, pandas, numpy, scipy, networkx, joblib, pydantic; print('Dependencias Python OK')"
```

---

## 8. Verificación del Entorno Node

Comprobar Node.js:

```bash
docker compose run --rm node node --version
```

Comprobar npm:

```bash
docker compose run --rm node npm --version
```

---

## 9. Verificación del Montaje del Repositorio

Para verificar que el repositorio local se encuentra correctamente montado en `/workspace`:

```bash
docker compose run --rm python ls -la /workspace
```

El resultado debe mostrar los archivos y directorios del proyecto, incluyendo elementos como:

```text
docker/
docs/
inference-engine/
model-export/
model-source/
pwa-app/
tests/
README.md
docker-compose.yml
```

---

## 10. Estado de los Contenedores

Para consultar el estado de los servicios:

```bash
docker compose ps -a
```

Si Docker Desktop o el daemon de Docker no está ejecutándose, este comando puede devolver un error de conexión con la API de Docker.

En Windows con Docker Desktop, un mensaje relacionado con:

```text
dockerDesktopLinuxEngine
```

normalmente indica que Docker Desktop no está iniciado o que el motor Linux todavía no está disponible.

En ese caso:

1. iniciar Docker Desktop;
2. esperar a que indique que el motor está listo;
3. repetir el comando.

---

## 11. Limpieza de Contenedores

Para detener y eliminar los contenedores creados por Compose:

```bash
docker compose down
```

Para eliminar también volúmenes asociados al entorno:

```bash
docker compose down -v
```

Este segundo comando debe utilizarse con precaución si en el futuro se agregan volúmenes persistentes.

---

## 12. Reconstrucción Después de Cambios

Debe reconstruirse la imagen correspondiente cuando se modifique alguno de estos elementos:

- un Dockerfile;
- `model-export/requirements.txt`;
- configuración que afecte el proceso de construcción.

Reconstrucción normal:

```bash
docker compose build
```

Reconstrucción completamente limpia:

```bash
docker compose build --no-cache
```

---

## 13. `.dockerignore`

El archivo `.dockerignore` evita enviar al contexto de construcción archivos que no son necesarios, por ejemplo:

- `.venv/`;
- `.git/`;
- `__pycache__/`;
- `node_modules/`;
- archivos temporales de editores;
- directorios de cobertura, compilación o distribución.

Esto reduce el contexto enviado a Docker y ayuda a evitar construcciones innecesariamente pesadas.

---

## 14. Reproducibilidad

La arquitectura Docker busca que el proyecto pueda ejecutarse de forma equivalente en:

- Windows;
- Linux;
- macOS.

El código del proyecto se monta en `/workspace`, por lo que no debe depender de rutas absolutas específicas de un sistema operativo.

Las dependencias de Python se gestionan mediante `model-export/requirements.txt`.

La estrategia definitiva de fijación de versiones científicas se validará por separado antes de cerrar la **Sección 1**, para garantizar que el entorno de desarrollo sea compatible con el modelo científico original.

---

## 15. Checklist de Verificación

Antes de considerar válido el entorno Docker, comprobar:

```text
[ ] Docker responde correctamente.
[ ] Docker Compose responde correctamente.
[ ] Los servicios node y python son reconocidos.
[ ] La imagen Python se construye correctamente.
[ ] La imagen Node se construye correctamente.
[ ] Python se ejecuta dentro del contenedor.
[ ] pgmpy puede importarse dentro del contenedor.
[ ] Node.js se ejecuta dentro del contenedor.
[ ] npm se ejecuta dentro del contenedor.
[ ] /workspace contiene el repositorio.
[ ] No existen errores durante docker compose build.
```

---

## 16. Regla de Validación

La configuración Docker no debe considerarse finalizada únicamente porque las imágenes se construyan.

Antes de cerrar la **Sección 1 — Infraestructura Docker**, deberán completarse:

1. documentación;
2. validación de versiones;
3. construcción limpia;
4. pruebas de ejecución;
5. verificación del repositorio;
6. commit;
7. push;
8. etiqueta de cierre de la sección cuando corresponda.

No se avanzará a la siguiente sección hasta completar la sección actual al 100%.
