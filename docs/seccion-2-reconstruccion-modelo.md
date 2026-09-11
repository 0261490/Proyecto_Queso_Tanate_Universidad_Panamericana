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

---

# 20. Subapartado 2.3 — Aprendizaje estructural con Hill-Climbing + BIC

El Subapartado 2.3 tiene como objetivo reconstruir de forma reproducible únicamente la estructura del DAG, sin estimar todavía CPT ni realizar inferencia probabilística.

La entrada utilizada es exclusivamente la vista reproducible definida en el Subapartado 2.2:

```text
169 observaciones
11 variables
SHA-256 del dataset de entrenamiento:
c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5
```

No se utiliza `Judge_ID` como variable del modelo.

La metodología reportada por la publicación se conserva en lo que sí puede verificarse:

```text
Hill-Climbing
+
BIC
```

La reconstrucción actual utiliza el entorno congelado del proyecto:

```text
Python 3.12.13
pgmpy 1.1.2
```

La publicación utilizó `pgmpy 0.1.23`. Por ello, las diferencias de API y comportamiento se documentan explícitamente y no se presenta la reconstrucción como recuperación exacta del modelo original.

---

# 21. Auditoría de la API y configuración de Hill-Climbing

En `pgmpy 1.1.2` se verificó que:

```text
HillClimbSearch: disponible
BIC: disponible
BicScore: no disponible con ese nombre
ExpertKnowledge: disponible
```

Para datos discretos, el criterio utilizado es:

```text
scoring_method="bic-d"
```

La configuración estructural se fijó de forma explícita:

```text
scoring_method   = "bic-d"
use_cache        = True
start_dag        = None
tabu_length      = 100
max_indegree     = None
expert_knowledge = None
epsilon          = 0.0001
max_iter         = 1000000
show_progress    = False
```

`start_dag=None` implica comenzar desde un DAG completamente desconectado.

`show_progress=False` solamente desactiva la barra visual y no altera el criterio de búsqueda.

No se aplicaron aristas requeridas, aristas prohibidas, orden temporal ni otras restricciones estructurales.

La API actual devuelve:

```text
pgmpy.base.DAG
```

y realiza únicamente aprendizaje de estructura.

Durante la ejecución aparecen advertencias de deprecación indicando que ciertas clases serán reubicadas o eliminadas en versiones futuras de `pgmpy`. Estas advertencias no constituyen errores en el entorno congelado `pgmpy 1.1.2`.

---

# 22. Hallazgo de no determinismo en el comportamiento nativo de pgmpy

Se creó:

```text
model-source/audit_hillclimb.py
```

para auditar el aprendizaje estructural, calcular el BIC final y generar una representación canónica del DAG con SHA-256.

Tres ejecuciones consecutivas dentro del mismo proceso produjeron inicialmente el mismo DAG.

Sin embargo, al ejecutar procesos independientes con diferentes valores de `PYTHONHASHSEED`, se observó que el comportamiento nativo de `HillClimbSearch` podía terminar en estructuras diferentes.

Resultados relevantes:

```text
PYTHONHASHSEED=0
Aristas: 7
BIC: -1120.7456402514
SHA-256 DAG:
11fb5b49d2d51e4508563e4ba4b1d07eba1e36cf0e6da36703312c9c08136cdb
```

```text
PYTHONHASHSEED=1
Aristas: 7
BIC: -1120.3418009039
SHA-256 DAG:
d0fd1389d23740f4684c3d4f84db0fc91c43c34b91b061b4fb4fde366d5563ef
```

Los procesos con:

```text
PYTHONHASHSEED=42
PYTHONHASHSEED=12345
```

produjeron el mismo resultado observado con `PYTHONHASHSEED=0`.

La inspección del código de `pgmpy 1.1.2` mostró que las posibles aristas nuevas se generan a partir de una colección basada en `set(...)` y que `estimate()` selecciona la mejor operación mediante `max(..., key=score_delta)`.

Esto es relevante porque el orden de iteración de un `set` puede cambiar entre procesos.

---

# 23. Empate exacto identificado

La auditoría con trazado de empates identificó un único empate en la mejor operación durante la búsqueda:

```text
iteración = 2
score_delta = 20.959907995794595
candidatos = 2
```

Las dos operaciones empatadas fueron:

```text
Q1_Traditional_Mexican -> Q4_Gastronomic_Heritage

Q4_Gastronomic_Heritage -> Q1_Traditional_Mexican
```

Ambas operaciones tenían exactamente el mismo incremento de score en ese punto de la búsqueda.

Con el comportamiento nativo, el orden interno de las operaciones podía determinar cuál era encontrada primero por `max()`.

La elección inicial modificaba posteriormente el espacio local explorado por Hill-Climbing y podía conducir a máximos locales finales distintos.

Por tanto, el BIC final diferente no contradice el empate inicial.

---

# 24. Política canónica de desempate

Para eliminar la dependencia accidental del orden interno de Python se definió una política explícita de desempate.

Las operaciones legales se ordenan canónicamente por:

```text
1. tipo de operación;
2. nodo origen;
3. nodo destino.
```

Orden de tipos:

```text
+ < - < flip
```

Los nombres de nodos se ordenan lexicográficamente.

La política no modifica:

```text
BIC
epsilon
tabu_length
max_iter
max_indegree
restricciones estructurales
dataset
```

La regla únicamente determina qué operación se selecciona cuando dos o más operaciones tienen exactamente el mismo `score_delta`.

Esta política es una decisión de ingeniería para la reconstrucción reproducible de Proyecto Tenate.

No se atribuye esta regla al modelo científico original ni a la publicación.

Tampoco se eligió una estructura únicamente por aproximarse a la inferencia publicada de 62.6 %.

---

# 25. Validación entre procesos independientes

El modo canónico se ejecutó en cuatro procesos independientes:

```text
PYTHONHASHSEED=0
PYTHONHASHSEED=1
PYTHONHASHSEED=42
PYTHONHASHSEED=12345
```

Los cuatro produjeron exactamente:

```text
Nodos: 11
Aristas: 7
BIC: -1120.7456402514
SHA-256 canónico del DAG:
11fb5b49d2d51e4508563e4ba4b1d07eba1e36cf0e6da36703312c9c08136cdb
Iteraciones con empate: 1
```

Las siete aristas reproducibles fueron:

```text
Q1_Traditional_Mexican -> Q4_Gastronomic_Heritage
Q2_Purchase_Intention -> Q3_Recommendation
Q3_Recommendation -> Q4_Gastronomic_Heritage
Q3_Recommendation -> Q5_Authenticity_Elaboration
Q3_Recommendation -> Q6_Commercial_Potential
Q5_Authenticity_Elaboration -> Q1_Traditional_Mexican
Q5_Authenticity_Elaboration -> Q7_Culture_Preservation
```

En esta reconstrucción quedaron sin aristas:

```text
Gender
Age
Standardized_City
Q8_Sensory_Uniqueness
```

Esto se conserva como resultado observado de la metodología reconstruida.

No se añadirán aristas manualmente para forzar coincidencia con la publicación.

---

# 26. Pruebas automáticas del Subapartado 2.3

Se creó:

```text
tests/test_audit_hillclimb.py
```

Las pruebas utilizan exclusivamente datos sintéticos categóricos y no requieren el CSV científico original.

Se validan cinco comportamientos:

```text
1. el orden canónico de operaciones empatadas es estable;
2. un empate de score se resuelve siempre mediante la regla canónica;
3. la regla canónica no sustituye una operación que tenga un score superior;
4. el SHA-256 canónico de un DAG no depende del orden de inserción de sus aristas;
5. el modo canónico resuelve de forma reproducible un empate de orientación con datos sintéticos discretos.
```

Resultado dentro de Docker:

```text
Ran 5 tests in 0.082s

OK
```

También se verificó la compilación de:

```text
model-source/audit_hillclimb.py
tests/test_audit_hillclimb.py
```

mediante:

```text
python -m py_compile
```

sin errores.

`git diff --check` tampoco reportó errores de formato.

---

# 27. Limitaciones científicas del resultado estructural

El DAG obtenido en este subapartado es una reconstrucción reproducible basada en:

```text
CSV científico recibido
+
Hill-Climbing
+
BIC discreto
+
pgmpy 1.1.2
+
parámetros explícitos
+
política canónica de desempate
```

No se puede afirmar que sea idéntico al DAG original utilizado por los autores porque no están disponibles:

```text
modelo serializado original;
archivo GeNIe original;
código de entrenamiento original;
configuración completa de Hill-Climbing;
restricciones estructurales originales;
regla original de desempate;
CPT originales.
```

La dirección de una arista aprendida por este procedimiento tampoco debe interpretarse automáticamente como evidencia causal.

Las diferencias con la figura o resultados de la publicación se registrarán como diferencias observadas, no se corregirán manualmente.

La estimación de CPT pertenece al Subapartado 2.4 y todavía no se realiza aquí.

---

# 28. Criterios de cierre del Subapartado 2.3

- [x] verificar la API de Hill-Climbing en `pgmpy 1.1.2`;
- [x] verificar el criterio BIC discreto disponible;
- [x] documentar diferencias relevantes de API frente a `pgmpy 0.1.23`;
- [x] fijar explícitamente los parámetros de Hill-Climbing;
- [x] comenzar desde un DAG vacío;
- [x] mantener `max_indegree=None`;
- [x] evitar restricciones estructurales no justificadas;
- [x] verificar los criterios de parada;
- [x] estudiar el comportamiento ante empates;
- [x] identificar un empate exacto durante el aprendizaje real;
- [x] demostrar sensibilidad del comportamiento nativo a `PYTHONHASHSEED`;
- [x] definir una política explícita de desempate;
- [x] demostrar reproducibilidad entre cuatro procesos independientes;
- [x] registrar el BIC del DAG;
- [x] registrar las aristas del DAG;
- [x] registrar un SHA-256 canónico de la estructura;
- [x] crear pruebas automáticas con datos sintéticos;
- [x] obtener 5/5 pruebas satisfactorias;
- [x] verificar experimentalmente el efecto del orden de las columnas de entrada;
- [x] ejecutar la suite completa de pruebas del repositorio para comprobar ausencia de regresiones.

Estado:

```text
SUBAPARTADO 2.3 — APRENDIZAJE ESTRUCTURAL CON HILL-CLIMBING + BIC
COMPLETADO AL 100 %
```

---

# 29. Estado del Apartado 2

```text
Apartado 2 — Reconstrucción reproducible del modelo Bayesiano

2.1 Especificación científica de reconstrucción
COMPLETADO AL 100 %

2.2 Preparación reproducible del dataset
COMPLETADO AL 100 %

2.3 Aprendizaje estructural con Hill-Climbing + BIC
COMPLETADO AL 100 %

2.4 Estimación reproducible de CPT
PENDIENTE

2.5 Validación estructural y probabilística
PENDIENTE

2.6 Congelación y versionado del modelo derivado
PENDIENTE
```

---

# 30. Cierre del Subapartado 2.3

Las dos comprobaciones finales requeridas para cerrar el Subapartado 2.3 fueron ejecutadas satisfactoriamente:

```text
1. se verificó experimentalmente que el orden de las columnas de entrada no altera el resultado del modo canónico;
2. se ejecutó satisfactoriamente la suite completa de pruebas del repositorio: 16/16 pruebas OK.
```

Ambas comprobaciones fueron satisfactorias. Por lo tanto, el Subapartado 2.3 queda cerrado técnica y documentalmente al 100 %.

El siguiente subapartado habilitado es:

```text
2.4 — Estimación reproducible de CPT
```

No se iniciará 2.4 hasta que los cambios correspondientes a 2.3 sean revisados, versionados y sincronizados con GitHub.
