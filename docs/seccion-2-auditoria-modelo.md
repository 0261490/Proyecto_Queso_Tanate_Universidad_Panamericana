# Proyecto Tenate

## Sección 2 — Exportador del Modelo Bayesiano

### Apartado 1 — Recuperación y auditoría del modelo científico

**Fecha de documentación:** 17 de agosto de 2026
**Estado:** En proceso — pendiente de recibir el modelo científico original

---

# 1. Objetivo del Apartado 1

Recuperar, identificar y auditar la versión científica original de la Red Bayesiana utilizada en el artículo de Queso Tenate antes de desarrollar el exportador a JSON.

La finalidad es garantizar que el proceso de ingeniería preserve sin modificaciones:

- nodos;
- estados;
- estructura del DAG;
- aristas;
- Tablas de Probabilidad Condicional (CPT);
- probabilidades;
- orden de estados y padres cuando sea relevante para las CPT;
- resultados de inferencia de referencia.

Este apartado debe completarse antes de definir como definitivo el contrato `model.json` o implementar plenamente `export_model.py`.

---

# 2. Referencias científicas conocidas

El artículo del proyecto reporta que:

- la Red Bayesiana fue construida utilizando datos de `N = 169` evaluadores;
- las variables perceptuales `Q1` a `Q8` fueron binarizadas a estados `Yes/No`;
- el aprendizaje estructural utilizó Hill-Climbing;
- la selección de topología se evaluó mediante BIC;
- la parametrización y la inferencia se realizaron en Python con `pgmpy 0.1.23`;
- también se utilizó GeNIe Modeler `4.1`;
- una inferencia de referencia del modelo es:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
P(Q2 = No  | Q8 = Yes) = 37.4%
```

Esta inferencia se utilizará como una de las pruebas de identidad científica del modelo recibido.

---

# 3. Estado inicial del repositorio

Al iniciar la Sección 2 se comprobó:

```text
git status --short
```

Resultado:

```text
[sin salida]
```

Por lo tanto, el repositorio se encontraba limpio.

La carpeta:

```text
model-source/
```

contenía únicamente:

```text
.gitkeep
```

con tamaño de `0 bytes`.

Conclusión:

> El repositorio no contenía inicialmente el modelo científico original.

---

# 4. Auditoría del repositorio actual

Se revisaron archivos versionados con extensiones potencialmente relacionadas con el modelo:

```text
.py
.json
.bif
.xml
.xdsl
.pkl
.pickle
.joblib
.csv
```

La búsqueda no devolvió archivos candidatos.

También se buscaron referencias a:

```text
Q8_Sensory_Uniqueness
Q2_Purchase_Intention
DiscreteBayesianNetwork
BayesianNetwork
TabularCPD
VariableElimination
```

No se encontraron coincidencias relevantes dentro de los archivos versionados.

Conclusión:

> El repositorio actual no contiene código científico, datos de entrenamiento ni un modelo serializado.

---

# 5. Auditoría del historial de Git

Se revisó el historial de `model-source/` y `model-export/`.

Los únicos cambios históricos relevantes fueron:

```text
model-source/.gitkeep
model-export/.gitkeep
model-export/requirements.txt
model-export/requirements.lock.txt
```

También se revisaron todos los objetos alcanzables del historial Git buscando archivos con extensiones:

```text
.pkl
.pickle
.joblib
.bif
.xbif
.xdsl
.csv
.ipynb
.py
```

No se encontraron archivos científicos históricos.

Conclusión:

> No existe evidencia de que el modelo, los datos o el código de entrenamiento hayan sido versionados previamente en este repositorio.

---

# 6. Auditoría de archivos locales

Por decisión del proyecto, las carpetas de OneDrive fueron excluidas de la búsqueda.

Se revisaron ubicaciones locales relevantes:

```text
C:\Users\Valle\Downloads
C:\Users\Valle\PY
C:\Users\Valle\source
C:\Users\Valle\proyecto-tenate
```

También se realizó una búsqueda local amplia excluyendo:

```text
OneDrive
AppData
.git
.venv
.vscode
.codex
.docker
```

No se localizaron archivos científicos con formatos como:

```text
.pkl
.pickle
.joblib
.bif
.xbif
.xdsl
```

Tampoco se localizaron:

```text
CSV de entrenamiento
notebooks .ipynb
scripts Python de entrenamiento
```

---

# 7. Hallazgo: `check_model.py`

Se encontró:

```text
C:\Users\Valle\PY\check_model.py
```

El archivo contiene lógica para:

- cargar un archivo llamado `model.pkl` mediante `pickle`;
- usar `BIFReader` como alternativa;
- imprimir nodos;
- imprimir aristas;
- imprimir CPDs.

Este archivo es útil como evidencia de un flujo de verificación previsto, pero no contiene el modelo científico.

Además, no se encontró `model.pkl` dentro de `C:\Users\Valle\PY`, `C:\Users\Valle\Downloads` ni en la búsqueda local amplia realizada.

Conclusión:

> `check_model.py` no permite reconstruir por sí solo la Red Bayesiana original.

---

# 8. Auditoría del historial de PowerShell

Se identificó el archivo de historial:

```text
C:\Users\Valle\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Se buscaron referencias relacionadas con entrenamiento, serialización e inferencia del modelo.

No se localizaron comandos históricos que demostraran:

- entrenamiento del modelo;
- guardado del modelo;
- ubicación histórica de `model.pkl`;
- exportación BIF;
- creación de CPT;
- uso del CSV original.

Se encontró una referencia histórica a:

```text
C:\Users\Valle\Python BECA
```

pero esa carpeta ya no existe y el historial no mostró evidencia de que ahí hubiera estado el modelo científico.

Conclusión:

> El historial de PowerShell no permite recuperar la ubicación ni el procedimiento de creación del modelo original.

---

# 9. Diagnóstico de recuperación

Después de las búsquedas realizadas:

```text
Modelo entrenado final                 NO LOCALIZADO
CPT completas                          NO LOCALIZADAS
DAG serializado                        NO LOCALIZADO
CSV original                           NO LOCALIZADO
Script de entrenamiento                NO LOCALIZADO
Notebook de entrenamiento              NO LOCALIZADO
Versión científica original            PENDIENTE DE RECUPERAR
```

El artículo científico permite conocer parte de la estructura conceptual y resultados de referencia, pero no contiene todas las CPT necesarias para reconstruir exactamente la Red Bayesiana original.

Por lo tanto:

> No se reconstruirá el modelo manualmente ni se inventarán probabilidades a partir del artículo.

---

# 10. Responsable identificado

Se confirmó que la Red Bayesiana original fue realizada por la doctora/profesora responsable del modelo científico.

Se decidió solicitarle el archivo original correspondiente a la versión utilizada para obtener los resultados publicados.

La referencia principal para identificar la versión correcta es:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
```

---

# 11. Archivos solicitados

## Prioridad 1 — Modelo final

Solicitar el archivo final de la Red Bayesiana en el formato original en que exista.

Posibles formatos:

```text
.pkl
.pickle
.bif
.xbif
.xdsl
.xml
```

No se debe exigir una extensión concreta si la doctora utilizó otro formato.

## Prioridad 2 — Datos originales

Solicitar, si se conservan, los datos utilizados para entrenar el modelo, preferentemente en CSV.

Si contienen información identificable de participantes, deberá utilizarse una versión anonimizada antes de considerar su incorporación al proyecto.

## Prioridad 3 — Código de entrenamiento

Solicitar, si existe:

```text
.py
.ipynb
```

que permita reproducir carga de datos, preprocesamiento, aprendizaje estructural, estimación de parámetros e inferencia.

## Prioridad 4 — Archivo de GeNIe

Solicitar el archivo original utilizado en GeNIe Modeler si todavía está disponible.

## Prioridad 5 — Resultados de referencia

Solicitar capturas, tablas, salidas de Python, archivos de validación o cualquier evidencia de las inferencias realizadas con el modelo final.

---

# 12. Protocolo de recepción del modelo

Cuando se reciba el archivo científico, no se modificará inmediatamente.

Se seguirá este procedimiento:

- [ ] Registrar el nombre original del archivo.
- [ ] Registrar su extensión y tamaño.
- [ ] Registrar la fecha de recepción.
- [ ] Conservar una copia original sin modificaciones.
- [ ] Calcular un hash criptográfico del archivo.
- [ ] Identificar el software/formato con el que fue generado.
- [ ] Determinar si requiere una versión específica de `pgmpy` o GeNIe.
- [ ] Confirmar que no contiene información personal innecesaria.
- [ ] Determinar si puede almacenarse en GitHub o si requiere una política distinta.
- [ ] Crear una copia de trabajo únicamente después de preservar el original.

---

# 13. Protocolo de auditoría científica

## 13.1 Carga

- [ ] Cargar el archivo correctamente.
- [ ] Registrar cualquier warning o error de compatibilidad.
- [ ] Confirmar la clase/tipo de modelo.

## 13.2 Nodos

- [ ] Enumerar todos los nodos.
- [ ] Verificar nombres exactos.
- [ ] Confirmar que las variables esperadas están presentes.

## 13.3 Estados

- [ ] Enumerar estados de cada nodo.
- [ ] Confirmar estados `Yes/No` para `Q1–Q8`, cuando corresponda.
- [ ] Registrar el orden exacto de estados.

## 13.4 DAG

- [ ] Enumerar todas las aristas.
- [ ] Confirmar que la estructura sea acíclica.
- [ ] Comparar visualmente con la Figura 1 del artículo.
- [ ] Registrar cualquier diferencia.

## 13.5 CPT

- [ ] Extraer todas las CPT.
- [ ] Verificar cardinalidades.
- [ ] Registrar orden de padres.
- [ ] Registrar orden de estados.
- [ ] Verificar que cada distribución condicional esté normalizada.

## 13.6 Inferencia de referencia

Introducir:

```text
Q8 = Yes
```

Consultar:

```text
Q2
```

Resultado esperado:

```text
P(Q2 = Yes | Q8 = Yes) ≈ 62.6%
P(Q2 = No  | Q8 = Yes) ≈ 37.4%
```

- [ ] Registrar el resultado obtenido.
- [ ] Compararlo con la referencia del artículo.
- [ ] Investigar cualquier diferencia antes de continuar.

## 13.7 Compatibilidad

- [ ] Determinar versión original de `pgmpy`.
- [ ] Probar carga en un entorno compatible si es necesario.
- [ ] Documentar diferencias frente al entorno de ingeniería actual.
- [ ] Evitar convertir o reentrenar el modelo sin autorización científica.

## 13.8 Herramientas de auditoría preparadas

Mientras se espera la recepción del modelo científico original, se desarrolló una herramienta de inspección de solo lectura:

```text
model-export/inspect_model.py
```

La herramienta permite:

- calcular el hash SHA-256 del archivo recibido;
- cargar modelos BIF;
- cargar modelos XDSL;
- cargar modelos XMLBIF;
- cargar archivos Pickle únicamente mediante autorización explícita;
- ejecutar `check_model()` cuando esté disponible;
- enumerar nodos;
- enumerar estados;
- enumerar aristas del DAG;
- inspeccionar CPT;
- verificar la validez estructural básica de las CPT;
- ejecutar la inferencia de referencia cuando detecte Q2 y Q8.

La carga de archivos `.pkl` y `.pickle` permanece bloqueada por defecto debido a que la deserialización mediante Pickle puede ejecutar código. Solamente deberá habilitarse para archivos de procedencia confiable.

La herramienta fue validada dentro del entorno Docker reproducible mediante:

```text
python -m py_compile
CLI --help
carga de modelo BIF
lectura de nodos
lectura de estados
lectura del DAG
lectura de CPT
SHA-256
inferencia exacta
```

También se creó:

```text
tests/test_inspect_model.py
```

con cuatro pruebas automáticas:

```text
test_bif_loads_with_expected_structure
test_pickle_is_blocked_by_default
test_reference_inference_is_62_6_percent
test_sha256_is_stable
```

Resultado obtenido dentro del contenedor Docker:

```text
Ran 4 tests

OK
```

Para comprobar el flujo completo se utilizó exclusivamente una Red Bayesiana artificial de prueba con:

```text
Q8_Sensory_Uniqueness
        ↓
Q2_Purchase_Intention
```

y una CPT configurada deliberadamente para obtener:

```text
P(Q2 = Yes | Q8 = Yes) = 62.6%
P(Q2 = No  | Q8 = Yes) = 37.4%
```

El inspector recuperó:

```text
Porcentaje = 62.6000%
Diferencia absoluta = 0.0000 puntos %
Porcentaje = 37.4000%
```

Esta prueba valida el funcionamiento técnico del inspector.

> La Red Bayesiana utilizada en esta prueba es artificial y no constituye una reconstrucción ni una validación del modelo científico original del proyecto.

## 13.9 Auditoría de la base de datos recibida

Se recibió una copia de la base de datos asociada al estudio en formato CSV.

El archivo original fue conservado fuera del repositorio durante esta etapa y se auditó mediante un montaje Docker de solo lectura (`:ro`) para evitar modificaciones accidentales.

### Identificación del archivo

Tamaño:

```text
10,261 bytes
```

SHA-256:

```text
2a74e34d0cb9dad5f98bdd8d0cf4691c5ffc929ead195ea39de603974ca716be
```

El SHA-256 calculado directamente desde Windows coincidió exactamente con el calculado dentro del contenedor Docker.

Esto confirma que la auditoría fue realizada sobre el mismo archivo original sin modificaciones.

### Estructura de la base

La base contiene:

```text
169 filas
12 columnas
```

Columnas:

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

La estructura general es consistente con las variables descritas para el estudio.

### Integridad

La auditoría automática obtuvo:

```text
169 registros esperados                  OK
12 columnas esperadas                    OK
Orden de columnas                        OK
Valores faltantes                        0
Filas completamente duplicadas           0
Judge_ID duplicados                      0
Judge_ID vacíos                          0
Estados Q1-Q8 limitados a Yes/No         OK
```

Resultado:

```text
AUDITORÍA ESTRUCTURAL: OK
```

### Distribuciones observadas

```text
Q1_Traditional_Mexican
Yes = 130 / 169 = 76.92%
No  =  39 / 169 = 23.08%

Q2_Purchase_Intention
Yes = 101 / 169 = 59.76%
No  =  68 / 169 = 40.24%

Q3_Recommendation
Yes = 118 / 169 = 69.82%
No  =  51 / 169 = 30.18%

Q4_Gastronomic_Heritage
Yes = 95 / 169 = 56.21%
No  = 74 / 169 = 43.79%

Q5_Authenticity_Elaboration
Yes = 134 / 169 = 79.29%
No  =  35 / 169 = 20.71%

Q6_Commercial_Potential
Yes = 136 / 169 = 80.47%
No  =  33 / 169 = 19.53%

Q7_Culture_Preservation
Yes = 158 / 169 = 93.49%
No  =  11 / 169 = 6.51%

Q8_Sensory_Uniqueness
Yes = 126 / 169 = 74.56%
No  =  43 / 169 = 25.44%
```

### Frecuencia condicional empírica

Dentro de la base existen:

```text
126 registros con Q8_Sensory_Uniqueness = Yes
```

La frecuencia directa obtenida es:

```text
P_empírica(Q2 = Yes | Q8 = Yes)
= 75 / 126
= 0.5952380952
= 59.5238%
```

y:

```text
P_empírica(Q2 = No | Q8 = Yes)
= 51 / 126
= 0.4047619048
= 40.4762%
```

Estos valores corresponden a frecuencias observadas directamente en el CSV.

No deben confundirse con la inferencia posterior de la Red Bayesiana publicada:

```text
P_modelo(Q2 = Yes | Q8 = Yes) ≈ 62.6%
```

La diferencia entre ambos valores no constituye por sí sola un error, ya que una inferencia Bayesiana puede diferir de una frecuencia condicional directa del conjunto de datos.

### Observación de equivalencia científica

Durante la comparación preliminar se observaron diferencias entre algunas distribuciones marginales del CSV recibido y las presentadas en la Figura 1 del artículo.

Por lo tanto, actualmente se puede afirmar:

```text
Integridad estructural del CSV                 VALIDADA
Identidad criptográfica del archivo            REGISTRADA
Compatibilidad con el esquema general          VALIDADA
Equivalencia con la base científica publicada  PENDIENTE
Equivalencia con el modelo final                PENDIENTE
```

No se modificarán datos para intentar hacer coincidir artificialmente estas distribuciones.

La equivalencia científica deberá resolverse cuando se reciba el modelo original y se pueda determinar qué versión de los datos fue utilizada para entrenarlo.

### Herramienta utilizada

Se creó:

```text
model-source/audit_dataset.py
```

La herramienta:

- trabaja en modo de solo lectura;
- calcula SHA-256;
- valida filas y columnas;
- verifica valores faltantes;
- verifica duplicados;
- verifica `Judge_ID`;
- valida los estados `Yes/No`;
- reporta distribuciones de Q1-Q8;
- reporta categorías demográficas;
- calcula la frecuencia condicional empírica Q2/Q8.

El script fue validado dentro del entorno Docker antes de utilizarlo sobre la base real.

---

# 14. Protección del modelo científico

Durante toda la Sección 2 se mantendrá la siguiente regla:

> El proceso de exportación debe transformar el formato del modelo, no su contenido científico.

Por lo tanto, el exportador no podrá:

- renombrar nodos sin una capa explícita de metadatos;
- cambiar estados;
- reordenar CPT sin conservar su semántica;
- eliminar dependencias;
- agregar dependencias;
- recalcular probabilidades;
- entrenar nuevamente el modelo;
- suavizar probabilidades;
- modificar resultados para hacerlos coincidir con una referencia.

Cualquier diferencia científica deberá detener el avance y ser documentada.

---

# 15. Criterios para completar el Apartado 1 al 100 %

El Apartado 1 se considerará completado únicamente cuando:

- [x] se haya revisado `model-source/`;
- [x] se haya revisado el repositorio actual;
- [x] se haya revisado el historial de Git;
- [x] se hayan revisado ubicaciones locales relevantes;
- [x] se haya revisado el historial de PowerShell;
- [x] se haya identificado al responsable del modelo original;
- [x] se haya preparado una herramienta de inspección de solo lectura;
- [x] se hayan creado pruebas automáticas para dicha herramienta;
- [x] las pruebas automáticas hayan sido ejecutadas satisfactoriamente dentro de Docker;
- [x] se haya recibido una base de datos asociada al estudio;
- [x] se haya calculado y registrado su SHA-256;
- [x] se haya auditado la integridad estructural de la base;
- [x] se hayan validado los estados `Yes/No` de Q1-Q8;
- [x] se haya calculado la frecuencia condicional empírica Q2/Q8;
- [ ] se haya confirmado que el CSV recibido corresponde exactamente a la versión utilizada para entrenar el modelo publicado;
- [ ] se haya recibido el archivo científico;
- [ ] se haya preservado una copia original;
- [ ] se haya calculado su hash;
- [ ] se hayan identificado nodos;
- [ ] se hayan identificado estados;
- [ ] se haya identificado el DAG;
- [ ] se hayan identificado las CPT;
- [ ] se haya validado la estructura;
- [ ] se haya ejecutado la inferencia de referencia;
- [ ] se haya comprobado el resultado de aproximadamente `62.6%`;
- [ ] se haya documentado la compatibilidad de versiones;
- [ ] se haya autorizado formalmente avanzar al Apartado 2.

---

# 16. Estado actual

```text
SECCIÓN 2 — EXPORTADOR DEL MODELO BAYESIANO

Apartado 1 — Recuperación y auditoría del modelo científico

Búsqueda local                          COMPLETADA
Auditoría del repositorio               COMPLETADA
Auditoría del historial Git             COMPLETADA
Auditoría de PowerShell                 COMPLETADA
Responsable científico identificado     COMPLETADO
Documentación de auditoría              COMPLETADA
Inspector de modelo                     COMPLETADO
Pruebas automáticas del inspector       4/4 COMPLETADAS
Validación técnica en Docker            COMPLETADA
Base de datos recibida                  COMPLETADA
Hash SHA-256 de la base                 COMPLETADO
Auditoría estructural del CSV           COMPLETADA
Estados Q1-Q8                           VALIDADOS
Frecuencia empírica Q2/Q8               CALCULADA
Equivalencia CSV ↔ artículo             PENDIENTE
Solicitud del modelo                    EN ESPERA
Recepción del modelo                    PENDIENTE
Auditoría del modelo científico real    PENDIENTE
Equivalencia CSV ↔ modelo final         PENDIENTE

ESTADO GENERAL DEL APARTADO 1:
EN PROCESO
```

---

# 17. Próximo paso

La infraestructura de auditoría necesaria para recibir el modelo científico ya se encuentra preparada y validada.

El siguiente paso depende de la recepción del archivo original proporcionado por la responsable científica.

Cuando se reciba el modelo se deberá:

1. preservar el archivo original;
2. calcular su SHA-256;
3. identificar el formato;
4. cargarlo mediante `inspect_model.py`;
5. auditar nodos, estados, DAG y CPT;
6. ejecutar la inferencia de referencia;
7. comparar el resultado con:

```text
P(Q2 = Yes | Q8 = Yes) ≈ 62.6%
```

No se deberá considerar definitivo el contrato `model.json` ni iniciar la implementación completa de `export_model.py` hasta terminar esta auditoría.

---
# 18. Resultado de esta fase

La búsqueda realizada evita reconstruir o sustituir accidentalmente el modelo científico con una versión aproximada.

La dependencia pendiente está claramente identificada:

```text
RECIBIR Y VALIDAR EL MODELO CIENTÍFICO ORIGINAL
```

Hasta entonces, el Apartado 1 permanece abierto.
