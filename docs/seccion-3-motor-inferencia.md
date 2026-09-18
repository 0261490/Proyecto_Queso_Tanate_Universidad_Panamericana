# Proyecto Tenate

## Sección 3 — Motor Bayesiano TypeScript

**Estado:** Completado

## 1. Objetivo

Implementar un motor capaz de cargar el modelo JSON congelado en la Sección 2
y ejecutar inferencia Bayesiana exacta completamente en el cliente.

El alcance definido por el plan maestro comprende:

- carga del modelo;
- inferencia exacta;
- validación y aplicación de evidencia;
- consultas probabilísticas;
- validación de equivalencia contra Python;
- pruebas unitarias;
- documentación de la API interna.

## 2. Decisión de implementación

La primera implementación utiliza enumeración exacta sobre el orden topológico
del DAG. Este enfoque es sencillo de auditar y reproduce directamente la
factorización de la Red Bayesiana:

```text
P(X1, ..., Xn) = producto de P(Xi | padres(Xi))
```

Para cada consulta, el motor fija la evidencia, enumera los estados de las
variables ocultas y normaliza la distribución resultante. No usa muestreo,
aproximaciones, servicios externos ni reentrenamiento.

El modelo actual tiene 11 nodos y un espacio conjunto suficientemente pequeño
para utilizar esta implementación como referencia exacta. Una optimización
posterior podrá sustituir el algoritmo siempre que mantenga equivalencia
numérica con esta referencia.

## 3. Trabajo iniciado

Se creó la estructura inicial en `inference-engine/`:

```text
package.json
src/types.ts
src/model-loader.ts
src/inference-engine.ts
src/index.ts
tests/model-loader.test.ts
tests/inference-engine.test.ts
tests/python-equivalence.test.ts
tests/fixtures/python-reference.json
tools/generate_python_reference.py
README.md
```

## 4. Cargador del modelo

`model-loader.ts` convierte el JSON sin confianza en un modelo interno validado.
Comprueba formato, versión, nodos, estados, aristas, aciclicidad, cobertura de
CPT, padres, dimensiones, rango numérico y normalización.

El código de inferencia solo recibe un `BayesianModel` después de superar estas
validaciones.

## 5. API de inferencia inicial

`ExactInferenceEngine` expone:

```text
query(variable, evidence)
probability(variable, state, evidence)
probabilityOfEvidence(evidence)
```

La evidencia es un mapa entre identificadores de nodo y estados válidos. El
motor rechaza variables o estados desconocidos antes de iniciar el cálculo.

## 6. Validación inicial

La suite final en Node.js 24 completó 18 pruebas:

```text
tests: 18
pass: 18
fail: 0
```

Se verificaron carga del modelo congelado, inferencia marginal de Q2, evidencia
aislada Q8, variable consultada ya observada, probabilidad de evidencia,
rechazo de modelos o consultas inválidos y siete comparaciones automáticas
contra Python.

## 7. Equivalencia Python versus TypeScript

Se creó un generador Python que reconstruye el modelo desde `model.json` y
calcula referencias con `pgmpy VariableElimination`. Los casos actuales cubren:

```text
P(Age)
P(Q2)
P(Q2 | Q8=Yes)
P(Q1 | Q5=Yes)
P(Q4 | Q3=Yes)
P(Q4 | Q1=Yes, Q3=Yes)
P(Q6 | Q3=No)
```

El fixture queda ligado al SHA-256 del modelo:

```text
8ecb6ae7cd8236aa3e7930287bb8ae51f4828cbe97baf138d63bb75388800f3b
```

## 8. Revisión final

La revisión de cierre confirmó:

- todas las probabilidades del modelo congelado son finitas y normalizadas;
- la inferencia conserva el orden de estados del modelo;
- las distribuciones consultadas se normalizan explícitamente;
- la evidencia de probabilidad cero produce `InferenceError`;
- el fixture Python verifica el SHA-256 del `model.json` realmente cargado;
- consultas binarias, no binarias, con evidencia única y múltiple coinciden
  con `pgmpy` dentro de una tolerancia absoluta de `1e-12`;
- las 30 pruebas Python de las secciones anteriores continúan pasando.

## 9. Estado final

```text
Carga del modelo                              COMPLETADA
Inferencia exacta                             COMPLETADA
Evidencia                                     COMPLETADA
Consultas                                     COMPLETADAS
Pruebas unitarias TypeScript                  18/18 OK
Comparaciones Python versus TypeScript        7/7 OK
Suite Python                                  30/30 OK
Documentación de API interna                  COMPLETADA

SECCIÓN 3 — COMPLETADA AL 100 %
```
