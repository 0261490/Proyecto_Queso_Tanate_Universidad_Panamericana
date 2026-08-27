# Proyecto Tenate

## Sección 2 — Exportador del Modelo Bayesiano

### Apartado 2 — Reconstrucción reproducible del modelo Bayesiano

**Estado:** En proceso
**Fuente científica disponible:** CSV auditado de 169 registros
**Modelo Bayesiano serializado original:** No disponible

---

# 1. Objetivo

Construir de manera reproducible una Red Bayesiana derivada del CSV científico recibido, documentando con precisión qué decisiones están respaldadas por el artículo y cuáles corresponden a decisiones de reconstrucción del proyecto.

El modelo resultante no se presentará como una recuperación exacta del archivo Bayesiano original publicado.

La reconstrucción deberá producir un modelo científicamente trazable que posteriormente pueda exportarse a `model.json` sin alterar su contenido probabilístico.

---

# 2. Fuente científica disponible

La única fuente científica digital disponible es el CSV auditado durante el Apartado 1.

Características registradas:

```text
Registros: 169
Columnas: 12
Valores faltantes: 0
Filas duplicadas: 0
```

SHA-256 del archivo original:

```text
2a74e34d0cb9dad5f98bdd8d0cf4691c5ffc929ead195ea39de603974ca716be
```

El archivo original deberá mantenerse sin modificaciones.

---

# 3. Variables disponibles en el CSV

El CSV contiene:

```text
Judge_ID
Gender
Age
Standardized_City
Q1_Traditional_Mexican
Q2_Purchase_Intention
Q3_Recommendation
Q4_Gastronomic_Heritage
Q5_Authenticity_Elaboration
Q6_Commercial_Potential
Q7_Culture_Preservation
Q8_Sensory_Uniqueness
```

---

# 4. Variables que participarán en la Red Bayesiana

## 4.1 Variables incluidas

Con base en el artículo, la Red Bayesiana utilizará las variables demográficas discretizadas y las variables perceptuales Q1-Q8:

```text
Gender
Age
Standardized_City
Q1_Traditional_Mexican
Q2_Purchase_Intention
Q3_Recommendation
Q4_Gastronomic_Heritage
Q5_Authenticity_Elaboration
Q6_Commercial_Potential
Q7_Culture_Preservation
Q8_Sensory_Uniqueness
```

Total previsto:

```text
11 nodos
```

## 4.2 Judge_ID

`Judge_ID` se considera un identificador de registro y no una variable científica del modelo.

Por lo tanto:

```text
Judge_ID
→ conservar en el CSV original
→ usar para trazabilidad de filas
→ NO incluir como nodo de la Red Bayesiana
```

Esta exclusión evita introducir una variable identificadora sin significado probabilístico en el aprendizaje estructural.

---

# 5. Estados de las variables

## 5.1 Q1-Q8

El artículo describe Q1-Q8 como variables dicotómicas y reporta una binarización:

```text
Yes
No
```

El CSV recibido ya contiene esos estados.

Durante la reconstrucción no se cambiarán los valores originales del CSV.

Cuando una representación numérica sea necesaria internamente, deberá conservarse una correspondencia explícita y reversible:

```text
Yes ↔ 1
No  ↔ 0
```

La representación numérica interna no autoriza a cambiar los nombres científicos de los estados exportados.

## 5.2 Variables demográficas

Las variables:

```text
Gender
Age
Standardized_City
```

son categóricas/discretizadas.

Se conservarán las categorías observadas en el CSV recibido, salvo que exista evidencia científica explícita que justifique otra transformación.

---

# 6. Tratamiento de datos faltantes

La auditoría del CSV determinó:

```text
Valores faltantes = 0
```

Por lo tanto, no se realizará imputación.

No se agregarán valores artificiales para completar observaciones.

---

# 7. Aprendizaje estructural respaldado por el artículo

El artículo reporta:

```text
Algoritmo de búsqueda: Hill-Climbing
Tipo de búsqueda: Greedy / local
Criterio de selección: BIC
```

La reconstrucción deberá utilizar estos elementos como especificación científica mínima.

No se sustituirá Hill-Climbing por otro algoritmo únicamente para aproximar los resultados publicados.

No se sustituirá BIC por otra función de puntuación únicamente para aproximar el valor de referencia de 62.6 %.

---

# 8. Restricciones estructurales conocidas

El artículo describe como variables raíz:

```text
Age
Gender
Standardized_City
```

y señala que influyen inicialmente sobre:

```text
Q1_Traditional_Mexican
```

Estas observaciones se usarán como referencia para comparar el DAG reconstruido con la publicación.

Sin embargo, antes de introducir restricciones manuales en Hill-Climbing deberá distinguirse entre:

1. estructura obtenida automáticamente por el algoritmo;
2. estructura descrita posteriormente en el artículo;
3. restricciones explícitamente impuestas durante el entrenamiento original.

El artículo disponible no permite demostrar por sí solo que todas las relaciones visibles en la figura hayan sido impuestas como restricciones previas.

Por lo tanto, no se introducirán restricciones estructurales adicionales sin documentarlas como decisiones de reconstrucción.

---

# 9. Parametrización de CPT

El artículo indica que las dependencias fueron cuantificadas mediante probabilidades condicionales obtenidas a partir de frecuencias observadas.

Sin embargo, los archivos disponibles no especifican de forma inequívoca qué clase o estimador concreto de `pgmpy` fue utilizado para parametrizar las CPT.

Por lo tanto:

```text
Método exacto original de estimación de CPT
→ NO VERIFICABLE con los archivos disponibles
```

`MaximumLikelihoodEstimator` podrá evaluarse como candidato técnico porque estima probabilidades a partir de frecuencias observadas, pero no se declarará como el método original hasta justificar y documentar esa decisión.

No se utilizarán priors, suavizado o estimación Bayesiana sin una justificación explícita.

---

# 10. Versiones de software

El artículo reporta:

```text
pgmpy: 0.1.23
GeNIe Modeler: 4.1
```

El entorno reproducible actual del proyecto utiliza:

```text
pgmpy: 1.1.2
Python: 3.12.13
```

Antes de implementar el entrenamiento definitivo deberá verificarse la equivalencia de las APIs y del comportamiento relevante entre la versión científica reportada y la versión de ingeniería actual.

Cualquier diferencia deberá documentarse.

---

# 11. Determinismo

El artículo disponible no especifica una semilla aleatoria concreta para el aprendizaje estructural.

Antes de declarar reproducible el entrenamiento se deberá determinar:

- si el procedimiento utilizado por `pgmpy` requiere semilla;
- si Hill-Climbing es determinista bajo la configuración seleccionada;
- cómo se resuelven empates entre estructuras con igual puntuación;
- si el orden de las columnas o estados afecta el resultado;
- qué parámetros por defecto de la versión utilizada pueden influir en el DAG.

La configuración final deberá quedar explícita en código y documentación.

---

# 12. Referencias de validación científica

## 12.1 Inferencia principal

El artículo reporta:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
P(Q2 = No  | Q8 = Yes) = 37.4%
```

El modelo reconstruido deberá ejecutar la misma consulta y registrar su resultado.

La referencia de 62.6 % se utilizará para comparación, no como un valor que deba forzarse.

## 12.2 Métricas predictivas publicadas

El artículo reporta para Q2 mediante validación cruzada K-fold con K=10:

```text
Accuracy = 84.2%
Log-loss = 0.32
AUC-ROC = 0.89
```

Estas métricas se conservarán como referencias científicas.

Su reproducción exacta solo se exigirá si los archivos disponibles permiten reconstruir de manera inequívoca el mismo procedimiento de validación.

## 12.3 Distribuciones marginales

Las distribuciones marginales mostradas en la Figura 1 se utilizarán como evidencia comparativa adicional.

Las diferencias ya observadas entre algunas marginales de la figura y el CSV recibido deberán documentarse y no corregirse artificialmente.

---

# 13. Separación entre evidencia y decisión de reconstrucción

Cada decisión deberá clasificarse en una de estas categorías:

```text
A — RESPALDADA POR EL ARTÍCULO
B — OBSERVADA EN EL CSV
C — DECISIÓN DE RECONSTRUCCIÓN
D — NO VERIFICABLE
```

Ejemplos iniciales:

| Elemento | Clasificación |
|---|---|
| N = 169 | A + B |
| Q1-Q8 dicotómicas | A + B |
| Gender, Age y Standardized_City | A + B |
| Hill-Climbing | A |
| BIC | A |
| pgmpy 0.1.23 | A |
| GeNIe 4.1 | A |
| Q2 como objetivo de validación | A |
| K-fold, K=10 | A |
| `Judge_ID` fuera del modelo | C, respaldada por su función de identificador |
| Estimador exacto de CPT | D |
| Semilla original | D |
| Parámetros exactos de Hill-Climbing | D |

---

# 14. Prohibiciones metodológicas

Durante la reconstrucción no se permitirá:

- modificar el CSV original para aproximar resultados publicados;
- cambiar respuestas `Yes/No` para obtener 62.6 %;
- eliminar observaciones sin justificación documentada;
- agregar observaciones artificiales;
- modificar el DAG manualmente y presentarlo como salida automática;
- ajustar CPT manualmente para obtener una probabilidad objetivo;
- seleccionar parámetros únicamente porque producen una coincidencia numérica;
- presentar el modelo derivado como el archivo original del artículo.

---

# 15. Subapartados de reconstrucción

El Apartado 2 se dividirá en:

```text
2.1 Especificación científica de reconstrucción
2.2 Preparación reproducible del dataset
2.3 Aprendizaje estructural con Hill-Climbing + BIC
2.4 Estimación reproducible de CPT
2.5 Validación estructural y probabilística
2.6 Congelación y versionado del modelo derivado
```

No se avanzará al siguiente subapartado hasta terminar el actual al 100 %.

---

# 16. Criterios para completar el Subapartado 2.1 al 100 %

- [x] identificar la única fuente científica disponible;
- [x] registrar el SHA-256 de la fuente;
- [x] identificar las variables disponibles;
- [x] definir la exclusión de `Judge_ID` del modelo;
- [x] identificar las 11 variables previstas para la Red Bayesiana;
- [x] documentar los estados de Q1-Q8;
- [x] documentar el tratamiento de variables demográficas;
- [x] documentar que no se requiere imputación;
- [x] registrar Hill-Climbing como algoritmo respaldado;
- [x] registrar BIC como criterio respaldado;
- [x] registrar las versiones científicas reportadas;
- [x] registrar la inferencia de referencia 62.6 % / 37.4 %;
- [x] registrar las métricas predictivas publicadas;
- [x] identificar como no verificable el estimador original exacto de CPT;
- [x] identificar como no verificable la semilla/configuración exacta original;
- [x] establecer las reglas para distinguir evidencia científica de decisiones de reconstrucción;
- [x] establecer las prohibiciones contra ajustes destinados únicamente a forzar coincidencias.

Estado documental previsto una vez validado este archivo:

```text
SUBAPARTADO 2.1 — ESPECIFICACIÓN CIENTÍFICA
LISTO PARA VALIDACIÓN
```

---

# 17. Próximo paso después de validar este documento

Una vez revisada y versionada esta especificación, el siguiente trabajo será:

```text
Subapartado 2.2 — Preparación reproducible del dataset
```

Ese subapartado deberá construir una vista de entrenamiento reproducible a partir del CSV original sin modificar la fuente.

Todavía no se entrenará la Red Bayesiana hasta que la preparación de datos quede validada al 100 %.
