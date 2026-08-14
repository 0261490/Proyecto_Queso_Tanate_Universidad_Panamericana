# Proyecto Tenate

## Ecosistema Edge-AI de Inferencia Bayesiana

### Aplicación de Resiliencia Comercial para Productores Artesanales de Queso Tenate

---

# Estado del Proyecto

**Fecha de inicio:** Agosto 2026

El objetivo del proyecto es desarrollar una aplicación **Edge-AI** capaz de ejecutar inferencia bayesiana completamente en el cliente (offline), utilizando un modelo previamente entrenado en Python (`pgmpy`) y exportado a un formato portable (`JSON`) que será interpretado por un motor de inferencia escrito en TypeScript.

La aplicación será una **Progressive Web App (PWA)**, instalable y funcional sin conexión a Internet.

---

# Repositorio Oficial

Todo el desarrollo del proyecto deberá mantenerse actualizado en el siguiente repositorio:

**GitHub:**

https://github.com/0261490/Proyecto_Queso_Tanate_Universidad_Panamericana

El repositorio funcionará como fuente oficial del código, documentación, pruebas y versiones del proyecto.

---

# Política de Actualización en GitHub

Al finalizar cada sprint se deberá realizar una actualización formal del repositorio.

Cada cierre de sprint deberá incluir, como mínimo:

1. código fuente desarrollado o modificado;
2. pruebas asociadas;
3. documentación correspondiente;
4. actualización del `README.md` cuando sea necesario;
5. actualización del estado del sprint en la documentación del proyecto;
6. commit descriptivo;
7. push al repositorio remoto;
8. etiqueta de versión (`tag`) cuando el sprint represente un hito estable.

## Convención recomendada de commits

```text
Sprint N: descripción breve del avance
```

Ejemplos:

```text
Sprint 2: implementar exportador del modelo bayesiano
Sprint 3: implementar motor de inferencia TypeScript
Sprint 4: agregar traductor de evidencia
```

## Convención recomendada de etiquetas

```text
sprint-0
sprint-1
sprint-2
sprint-3
...
sprint-8
```

Cuando exista una versión funcional completa de la aplicación podrán utilizarse versiones semánticas adicionales:

```text
v0.1.0
v0.2.0
v1.0.0
```

---

# Objetivo General

Construir un ecosistema reproducible y portable que permita:

- entrenar una Red Bayesiana en Python;
- exportar automáticamente el modelo;
- ejecutar inferencia exacta en TypeScript;
- funcionar completamente offline;
- almacenar historial de inferencias localmente;
- proporcionar una interfaz intuitiva que traduzca el conocimiento técnico del modelo bayesiano en preguntas comprensibles para productores artesanales;
- mantener todo el desarrollo versionado y respaldado en GitHub.

---

# Principio Arquitectónico

La aplicación estará dividida en dos capas completamente independientes.

## Capa Científica

Contiene el modelo matemático original.

Componentes:

- DAG;
- CPT;
- variables Q1–Q8;
- Motor Bayesiano.

Esta capa **nunca será modificada por la interfaz**.

---

## Capa de Interacción

Contiene únicamente elementos relacionados con la experiencia del usuario.

Componentes:

- preguntas amigables;
- iconografía;
- controles gráficos;
- validación de formularios;
- traducción de respuestas.

Esta capa convierte las respuestas del usuario en evidencia para el motor bayesiano.

---

# Arquitectura General

```text
                     Usuario
                        │
                        ▼
             Interfaz amigable (PWA)
                        │
                        ▼
             Traductor de Evidencia
                        │
                        ▼
         Evidencia Bayesiana (Q1-Q8)
                        │
                        ▼
      Motor Bayesiano TypeScript
                        │
                        ▼
              Probabilidades
                        │
                        ▼
             Resultados al usuario
```

---

# Objetivos Científicos

La Red Bayesiana conservará exactamente la estructura obtenida durante el entrenamiento en Python.

No se modificarán:

- nodos;
- dependencias;
- CPT;
- probabilidades.

La aplicación únicamente traducirá entradas del usuario hacia evidencia del modelo.

Ejemplo:

```text
Usuario responde

✔ Aroma tradicional

✔ Maduración en tenate

✔ Elaboración artesanal

↓

Motor recibe

Q5 = Yes

Q8 = Yes
```

De esta forma se mantiene la equivalencia científica con el modelo original.

---

# Objetivos de Ingeniería

## Reproducibilidad

El proyecto debe ejecutarse exactamente igual en:

- Windows;
- Linux;
- macOS.

Utilizando Docker.

---

## Portabilidad

El proyecto no dependerá de:

- rutas absolutas;
- Python instalado;
- Node instalado;
- sistema operativo.

Todo deberá ejecutarse mediante Docker.

---

## Edge AI

Toda la inferencia ocurrirá dentro del navegador.

```text
model.json

↓

Inference Engine

↓

Resultados
```

No existirá un servidor para ejecutar la inferencia.

---

## Arquitectura en Capas

Separar completamente los siguientes componentes.

### Motor Bayesiano

Responsable únicamente de:

- cargar `model.json`;
- realizar inferencia;
- calcular probabilidades.

Nunca conocerá la interfaz.

---

### Traductor de Evidencia

Nueva capa responsable de:

- convertir respuestas humanas en estados bayesianos;
- validar entradas;
- mantener independencia entre la interfaz y el modelo.

Ejemplo:

```text
¿Maduró en tenate?

↓

Q8 = Yes
```

---

### Interfaz

Responsable únicamente de:

- mostrar preguntas;
- mostrar resultados;
- accesibilidad;
- iconografía;
- experiencia de usuario.

No contendrá lógica probabilística.

---

# Organización del Proyecto

```text
proyecto-tenate/

├── docker/
│
├── docs/
│
├── inference-engine/
│
├── model-export/
│
├── model-source/
│
├── pwa-app/
│   ├── ui/
│   ├── translator/
│   ├── components/
│   ├── services/
│   └── storage/
│
├── tests/
│
└── README.md
```

---

# Nuevo Componente

## Traductor de Evidencia

Nuevo módulo.

```text
translator/

evidence-mapper.ts
```

### Responsabilidades

- recibir respuestas del usuario;
- generar evidencia bayesiana;
- enviar evidencia al motor.

### Ejemplo

#### Entrada

```text
{
  aroma: true,
  tenate: true,
  artesanal: true
}
```

↓

#### Salida

```text
{
  Q5: "Yes",
  Q8: "Yes"
}
```

---

# Trabajo Realizado

## Sprint 0

**Estado:** Completado.

### Actualización GitHub

Si todavía no se encuentra registrado formalmente, realizar una actualización retrospectiva del repositorio con:

- estructura inicial del proyecto;
- documentación base;
- definición de arquitectura;
- `README.md` inicial.

Commit recomendado:

```text
Sprint 0: inicializar estructura y documentación del proyecto
```

Tag recomendado:

```text
sprint-0
```

---

## Sprint 1

### Infraestructura Docker

**Estado:** Completado.

### Actualización GitHub

Subir:

- archivos Docker;
- configuración de contenedores;
- documentación para ejecución;
- pruebas básicas de reproducibilidad.

Commit recomendado:

```text
Sprint 1: configurar infraestructura Docker reproducible
```

Tag recomendado:

```text
sprint-1
```

---

# Sprint 2

## Exportador del Modelo

### Objetivo

Construir:

```text
export_model.py
```

Exportará:

- nodos;
- estados;
- DAG;
- CPT;
- metadata.

Hacia:

```text
model.json
```

### Actualización GitHub del Sprint 2

Subir al repositorio:

- `export_model.py`;
- estructura de `model-export/`;
- archivo `model.json` de prueba o versión validada;
- pruebas del exportador;
- documentación del formato JSON;
- instrucciones para regenerar el modelo.

Commit recomendado:

```text
Sprint 2: implementar exportador del modelo bayesiano
```

Tag recomendado:

```text
sprint-2
```

---

# Sprint 3

## Motor Bayesiano

Implementar:

- carga del modelo;
- inferencia exacta;
- evidencia;
- consultas.

Validar contra Python.

### Actualización GitHub del Sprint 3

Subir:

- código del motor TypeScript;
- cargador de `model.json`;
- implementación de inferencia;
- pruebas unitarias;
- casos de comparación Python vs TypeScript;
- documentación de la API interna del motor.

Commit recomendado:

```text
Sprint 3: implementar motor bayesiano de inferencia exacta
```

Tag recomendado:

```text
sprint-3
```

---

# Sprint 4

## Traductor de Evidencia

Construir:

```text
evidence-mapper.ts
```

### Funciones

- convertir preguntas del usuario;
- validar respuestas;
- generar evidencia;
- desacoplar interfaz y modelo.

### Actualización GitHub del Sprint 4

Subir:

- `evidence-mapper.ts`;
- catálogo de correspondencias entre preguntas y variables;
- validaciones de entrada;
- pruebas unitarias;
- documentación del contrato entre interfaz y motor.

Commit recomendado:

```text
Sprint 4: agregar traductor de evidencia desacoplado
```

Tag recomendado:

```text
sprint-4
```

---

# Sprint 5

## Desarrollo de la PWA

Construir:

- formularios;
- componentes;
- iconografía;
- resultados;
- accesibilidad.

La interfaz nunca mostrará variables **Q1–Q8**.

Mostrará únicamente preguntas naturales.

### Ejemplo

```text
¿Su queso presenta aroma característico?

Sí

No
```

### Actualización GitHub del Sprint 5

Subir:

- interfaz PWA;
- componentes visuales;
- formularios;
- manifiesto PWA;
- service worker;
- recursos gráficos;
- pruebas de interfaz;
- documentación de accesibilidad;
- instrucciones de instalación.

Commit recomendado:

```text
Sprint 5: desarrollar interfaz PWA accesible y offline
```

Tag recomendado:

```text
sprint-5
```

---

# Sprint 6

## Persistencia

Implementar:

```text
IndexedDB
```

Guardar:

- respuestas del usuario;
- evidencia generada;
- resultados;
- historial.

### Actualización GitHub del Sprint 6

Subir:

- capa de persistencia;
- esquema de almacenamiento;
- servicios para IndexedDB;
- pruebas de lectura y escritura;
- pruebas de funcionamiento offline;
- documentación del formato del historial local.

Commit recomendado:

```text
Sprint 6: implementar persistencia local con IndexedDB
```

Tag recomendado:

```text
sprint-6
```

---

# Sprint 7

## Pruebas

Validar:

```text
Python

↓

TypeScript

↓

Traductor

↓

Interfaz
```

Realizar:

- Golden Tests;
- pruebas unitarias;
- pruebas de integración;
- pruebas de inferencia;
- pruebas de UX.

La prueba científica de referencia deberá incluir, como mínimo:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
```

### Actualización GitHub del Sprint 7

Subir:

- conjunto completo de pruebas;
- Golden Tests;
- resultados de equivalencia Python vs TypeScript;
- pruebas de integración;
- reporte de validación;
- documentación de cobertura de pruebas.

Commit recomendado:

```text
Sprint 7: completar validación científica e integración
```

Tag recomendado:

```text
sprint-7
```

---

# Sprint 8

## Optimización

### Objetivo

Optimizar el ecosistema para mejorar su desempeño, mantenibilidad y facilidad de despliegue, preservando la independencia entre sus componentes y garantizando que la inferencia bayesiana continúe ejecutándose completamente en el cliente.

### Optimizar

- tiempo de inferencia;
- consumo de memoria;
- desacoplamiento entre módulos;
- accesibilidad;
- documentación técnica;
- integración y despliegue continuo (CI/CD).

### Validar

Verificar que las optimizaciones:

- no modifiquen la estructura de la Red Bayesiana;
- no alteren las Tablas de Probabilidad Condicional (CPT);
- mantengan resultados equivalentes al modelo entrenado en Python;
- preserven la ejecución completamente offline de la aplicación.

### Resultado Esperado

El sistema deberá:

- ejecutar la inferencia con el menor consumo posible de recursos;
- mantener una arquitectura modular y desacoplada;
- conservar la equivalencia científica entre el modelo de Python y el motor de inferencia en TypeScript;
- facilitar el mantenimiento y la evolución del proyecto mediante documentación actualizada y procesos automatizados de integración y despliegue continuo.

### Actualización GitHub del Sprint 8

Subir:

- optimizaciones realizadas;
- pruebas de regresión;
- mediciones de rendimiento;
- configuración CI/CD;
- documentación final;
- actualización completa del `README.md`;
- guía de instalación;
- guía de desarrollo;
- guía de validación científica.

Commit recomendado:

```text
Sprint 8: optimizar rendimiento y configurar CI/CD
```

Tag recomendado:

```text
sprint-8
```

Cuando el sistema completo sea considerado estable, crear además:

```text
v1.0.0
```

---

# Flujo de Cierre Obligatorio de Cada Sprint

Al terminar cada sprint se seguirá este procedimiento:

```text
Desarrollo del Sprint
        │
        ▼
Pruebas locales
        │
        ▼
Validación científica/técnica
        │
        ▼
Actualización de documentación
        │
        ▼
git status
        │
        ▼
git add .
        │
        ▼
git commit
        │
        ▼
git push
        │
        ▼
Crear tag del sprint
        │
        ▼
git push --tags
        │
        ▼
Sprint cerrado
```

Comandos generales:

```bash
git status

git add .

git commit -m "Sprint N: descripción del avance"

git push origin main

git tag sprint-N

git push origin sprint-N
```

Antes de ejecutar `git push`, deberán pasar las pruebas correspondientes al sprint.

---

# Regla de Protección del Modelo Científico

Ninguna actualización del repositorio podrá considerarse válida si modifica accidentalmente:

- estructura del DAG;
- dependencias de la Red Bayesiana;
- estados originales;
- CPT;
- probabilidades validadas.

Cualquier cambio en esos componentes deberá considerarse una modificación científica del modelo y no una modificación de interfaz o ingeniería.

---

# Criterio de Finalización del Proyecto

El proyecto podrá considerarse terminado cuando:

1. el modelo de Python pueda exportarse automáticamente;
2. TypeScript reproduzca la inferencia del modelo original;
3. la interfaz traduzca correctamente respuestas humanas a evidencia bayesiana;
4. la PWA funcione completamente offline;
5. IndexedDB almacene correctamente el historial;
6. las pruebas científicas y de ingeniería sean satisfactorias;
7. Docker permita reproducir el entorno en Windows, Linux y macOS;
8. CI/CD ejecute automáticamente las validaciones principales;
9. cada sprint se encuentre respaldado y versionado en el repositorio oficial;
10. exista una versión estable etiquetada como `v1.0.0`.
