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

Búsqueda local                         COMPLETADA
Auditoría del repositorio              COMPLETADA
Auditoría del historial Git            COMPLETADA
Auditoría de PowerShell                COMPLETADA
Responsable científico identificado    COMPLETADO
Solicitud del modelo                   EN ESPERA
Recepción del modelo                   PENDIENTE
Auditoría científica                   PENDIENTE

ESTADO GENERAL DEL APARTADO 1:
EN PROCESO
```

---

# 17. Próximo paso

Mientras se espera la entrega del modelo científico, se puede preparar documentación y procedimientos de validación que no dependan de las probabilidades originales.

No se deberá considerar definitivo el contrato `model.json` ni iniciar la implementación completa de `export_model.py` hasta que el modelo recibido haya sido auditado y se haya autorizado formalmente el avance.

---

# 18. Resultado de esta fase

La búsqueda realizada evita reconstruir o sustituir accidentalmente el modelo científico con una versión aproximada.

La dependencia pendiente está claramente identificada:

```text
RECIBIR Y VALIDAR EL MODELO CIENTÍFICO ORIGINAL
```

Hasta entonces, el Apartado 1 permanece abierto.
