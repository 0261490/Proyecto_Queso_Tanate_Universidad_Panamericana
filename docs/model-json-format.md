# Formato JSON del Modelo Bayesiano

## Objetivo

`model-export/model.json` es la representación portable y determinista de la
Red Bayesiana reconstruida por Proyecto Tenate. Está diseñada para ser leída
por el futuro motor de inferencia en TypeScript sin depender de `pgmpy`.

El archivo representa una reconstrucción reproducible derivada del CSV
auditado. No se presenta como recuperación exacta del modelo original
publicado.

## Identidad congelada

```text
Formato:       proyecto-tenate-bayesian-model
Esquema:       1
Modelo:        1.0.0
Nodos:         11
Aristas:       7
CPT:           11
Bytes JSON:    4882
SHA-256 JSON:  8ecb6ae7cd8236aa3e7930287bb8ae51f4828cbe97baf138d63bb75388800f3b
```

Los hashes científicos de entrada y componentes son:

```text
CSV original:  2a74e34d0cb9dad5f98bdd8d0cf4691c5ffc929ead195ea39de603974ca716be
Entrenamiento: c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5
DAG:           11fb5b49d2d51e4508563e4ba4b1d07eba1e36cf0e6da36703312c9c08136cdb
CPT:           a35320e2de8b2bc7c3af0093b968b1b46d28f8a8911a8ebbc19710861a88e61c
```

`model-export/model.sha256` contiene el hash del archivo JSON final.

## Estructura de nivel superior

```text
format          identificador estable del formato
schema_version  versión de la estructura JSON
model_version   versión semántica del modelo congelado
metadata        procedencia, aprendizaje, estimación y software
nodes           nodos y estados permitidos
edges           aristas dirigidas del DAG
cpts            tablas de probabilidad condicional
```

## Nodos y aristas

Cada nodo contiene un identificador y sus estados en orden canónico. Cada
arista tiene `source` y `target`. La lista completa debe formar un grafo
dirigido acíclico.

## CPT

Cada elemento de `cpts` contiene:

```text
node         nodo cuya distribución se representa
parents      padres ordenados lexicográficamente
state_names  orden de estados del nodo y de cada padre
values       matriz [estado_del_nodo][configuración_de_padres]
```

Las configuraciones de padres siguen el producto cartesiano de los padres en
el orden de `parents`; el último padre cambia más rápidamente. Para un nodo sin
padres existe una sola columna. Cada columna debe sumar exactamente 1 dentro
de la tolerancia numérica validada por el exportador.

## Validación

`model-export/export_model.py` comprueba antes de escribir:

- identidad criptográfica del CSV y del dataset de entrenamiento;
- identidad del DAG y de las CPT congeladas;
- unicidad de nodos y estados;
- existencia de una CPT por nodo;
- correspondencia entre aristas y padres de cada CPT;
- aciclicidad del grafo;
- dimensiones, finitud, rango y normalización de probabilidades;
- correspondencia de los hashes de componentes con el contenido.

El esquema estructural adicional está en
`model-export/model.schema.json`. Las validaciones semánticas que requieren
comparar varias partes del modelo pertenecen al exportador y no pueden
expresarse completamente mediante JSON Schema.

## Regeneración

El CSV científico se conserva fuera del repositorio. Para regenerar dentro del
entorno Docker, móntese como archivo de solo lectura:

```powershell
docker compose run --rm `
  -v "C:\ruta\al\datos.csv:/data/source.csv:ro" `
  python python model-export/export_model.py /data/source.csv
```

La ejecución correcta debe volver a producir:

```text
SHA-256 modelo:
8ecb6ae7cd8236aa3e7930287bb8ae51f4828cbe97baf138d63bb75388800f3b
```

Si cambia el CSV, el dataset de entrenamiento, el DAG, las CPT, una versión de
software registrada o la representación JSON, el hash final cambia. Ese cambio
debe revisarse científicamente y acompañarse de una nueva versión del modelo.
