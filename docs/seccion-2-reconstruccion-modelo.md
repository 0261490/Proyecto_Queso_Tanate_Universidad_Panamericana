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

# 17. Subapartado 2.2 — Preparación reproducible del dataset

El Subapartado 2.2 tuvo como objetivo construir una vista de entrenamiento reproducible a partir del CSV científico auditado, sin modificar la fuente original.

Se implementó:

```text
model-source/prepare_dataset.py
```

La herramienta valida primero la identidad criptográfica del CSV científico original.

Fuente esperada:

```text
Filas: 169
Columnas: 12

SHA-256:
2a74e34d0cb9dad5f98bdd8d0cf4691c5ffc929ead195ea39de603974ca716be
```

Si el SHA-256 no coincide, el proceso se detiene y el archivo es rechazado.

## 17.1 Transformación aplicada

La única variable eliminada de la vista de entrenamiento es:

```text
Judge_ID
```

La transformación aplicada es:

```text
CSV científico original
169 filas × 12 columnas
        │
        ├── validar SHA-256
        ├── validar esquema
        ├── validar integridad
        ├── conservar orden de filas
        ├── conservar categorías demográficas
        ├── conservar Q1-Q8 como Yes/No
        ├── no realizar imputación
        ├── no recodificar contenido científico
        └── excluir Judge_ID
                │
                ▼
Dataset de entrenamiento
169 filas × 11 columnas
```

No se alteran las 169 observaciones originales.

## 17.2 Columnas de entrenamiento

La vista reproducible contiene exactamente:

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

Total:

```text
11 variables
169 observaciones
```

`Judge_ID` permanece exclusivamente en el CSV fuente para trazabilidad y no participa como nodo científico de la Red Bayesiana.

## 17.3 Serialización canónica

Cuando se solicita escribir la vista derivada mediante `--output`, el archivo se genera de forma determinista con:

```text
UTF-8
sin BOM
sin índice
orden de filas conservado
orden científico fijo de columnas
saltos de línea LF
```

El dataset derivado producido a partir del CSV científico auditado tiene:

```text
SHA-256:
c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5
```

El hash calculado por `prepare_dataset.py` coincidió exactamente con el calculado posteriormente desde Windows.

Por lo tanto, la transformación:

```text
CSV original
→ dataset de entrenamiento
```

es reproducible a nivel de bytes bajo la serialización definida.

## 17.4 Modo de verificación

`prepare_dataset.py` puede ejecutarse sin `--output`.

En ese modo:

```text
Archivo derivado: NO ESCRITO
```

La herramienta valida y prepara la vista de entrenamiento en memoria, calcula su SHA-256 y no genera un nuevo archivo.

Esta modalidad permite comprobar la preparación sin crear artefactos innecesarios.

## 17.5 Prueba real con la fuente científica

La herramienta fue ejecutada dentro del entorno Docker utilizando el CSV original montado como solo lectura:

```text
:ro
```

Resultado:

```text
SHA-256 fuente:
2a74e34d0cb9dad5f98bdd8d0cf4691c5ffc929ead195ea39de603974ca716be

Filas fuente:
169

Columnas fuente:
12

Filas entrenamiento:
169

Columnas entrenamiento:
11

SHA-256 entrenamiento:
c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5

RESULTADO:
DATASET DE ENTRENAMIENTO PREPARADO CORRECTAMENTE
```

## 17.6 Prueba del modo `--output`

También se generó temporalmente:

```text
model-source/training_dataset_temp.csv
```

El archivo produjo:

```text
169 filas
11 columnas

SHA-256:
c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5
```

El hash coincidió con el calculado previamente en memoria por `prepare_dataset.py`.

Después de comprobar la reproducibilidad, el archivo temporal fue eliminado.

Resultado:

```text
Test-Path model-source/training_dataset_temp.csv
False
```

El dataset derivado temporal no se conservará ni se versionará en GitHub.

Puede regenerarse de forma determinista a partir del CSV científico original cuando sea necesario.

---

# 18. Pruebas automáticas del Subapartado 2.2

Se creó:

```text
tests/test_prepare_dataset.py
```

Las pruebas utilizan datos sintéticos y no requieren acceso al CSV científico original.

Se validan los siguientes comportamientos:

```text
1. vista de entrenamiento = 169 × 11;
2. Judge_ID no entra al modelo;
3. valores científicos conservados;
4. preparación determinista;
5. SHA-256 de fuente incorrecto rechazado;
6. estados diferentes de Yes/No rechazados;
7. Judge_ID duplicado rechazado;
8. archivo derivado idéntico a la serialización canónica.
```

La suite implementa siete pruebas automáticas, ya que algunas de las validaciones anteriores se comprueban conjuntamente dentro de un mismo caso de prueba.

Resultado dentro de Docker:

```text
Ran 7 tests

OK
```

También se verificó la compilación mediante:

```text
python -m py_compile
```

sin errores.

---

# 19. Criterios de cierre del Subapartado 2.2

- [x] validar el SHA-256 del CSV científico original;
- [x] conservar intacto el archivo fuente;
- [x] mantener las 169 observaciones;
- [x] excluir `Judge_ID` de la vista de entrenamiento;
- [x] producir exactamente 11 variables científicas;
- [x] conservar el orden definido de las variables;
- [x] conservar las categorías demográficas;
- [x] conservar Q1-Q8 como `Yes/No`;
- [x] evitar imputaciones;
- [x] evitar recodificaciones científicas;
- [x] definir una serialización canónica reproducible;
- [x] calcular el SHA-256 del dataset derivado;
- [x] demostrar que dos preparaciones producen el mismo resultado;
- [x] validar el modo sin escritura;
- [x] validar el modo `--output`;
- [x] ejecutar pruebas automáticas dentro de Docker;
- [x] obtener 7/7 pruebas satisfactorias;
- [x] eliminar el dataset temporal generado durante la validación;
- [x] mantener el dataset científico y su derivado fuera de GitHub.

Estado:

```text
SUBAPARTADO 2.2 — PREPARACIÓN REPRODUCIBLE DEL DATASET
COMPLETADO AL 100 %
```

---

# 20. Estado del Apartado 2

```text
Apartado 2 — Reconstrucción reproducible del modelo Bayesiano

2.1 Especificación científica de reconstrucción
COMPLETADO AL 100 %

2.2 Preparación reproducible del dataset
COMPLETADO AL 100 %

2.3 Aprendizaje estructural con Hill-Climbing + BIC
SIGUIENTE

2.4 Estimación reproducible de CPT
PENDIENTE

2.5 Validación estructural y probabilística
PENDIENTE

2.6 Congelación y versionado del modelo derivado
PENDIENTE
```

---

# 21. Próximo paso

El siguiente subapartado será:

```text
2.3 — Aprendizaje estructural con Hill-Climbing + BIC
```

En esta etapa se utilizará exclusivamente la vista reproducible de 169 observaciones y 11 variables definida en el Subapartado 2.2.

Antes de entrenar el modelo definitivo deberán verificarse:

1. la API exacta de Hill-Climbing en `pgmpy 1.1.2`;
2. la implementación actual del criterio BIC;
3. diferencias relevantes frente a `pgmpy 0.1.23`;
4. parámetros por defecto de Hill-Climbing;
5. criterios de parada;
6. comportamiento ante empates;
7. determinismo del aprendizaje;
8. restricciones estructurales disponibles;
9. efecto del orden de variables;
10. método reproducible para registrar el DAG resultante.

No se modificarán parámetros únicamente para intentar obtener la inferencia publicada de 62.6 %.

La comparación con la publicación se realizará después de producir el modelo mediante una metodología documentada.