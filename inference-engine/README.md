# Motor Bayesiano TypeScript

## Estado

Secciones 3 y 4 completadas. El motor carga el `model.json`
congelado en la Sección 2, valida su estructura y ejecuta inferencia exacta por
enumeración sin servidor ni dependencias de ejecución externas. El traductor de
evidencia valida y desacopla las respuestas de interfaz del modelo.

## API interna

### Carga del modelo

```ts
import { loadModel, loadModelFromJson } from "./src/index.ts";

const model = loadModel(rawObject);
const sameModel = loadModelFromJson(jsonText);
```

El cargador rechaza:

- formatos o versiones de esquema no compatibles;
- nodos, estados o aristas duplicados;
- aristas con nodos desconocidos;
- ciclos;
- padres de CPT que no coincidan con el DAG;
- estados inconsistentes;
- dimensiones de CPT inválidas;
- probabilidades fuera de rango o columnas sin normalizar.

### Motor de inferencia

```ts
import { ExactInferenceEngine } from "./src/index.ts";

const engine = new ExactInferenceEngine(model);
```

#### Consultar una distribución

```ts
const result = engine.query("Q2_Purchase_Intention", {
  Q8_Sensory_Uniqueness: "Yes",
});
```

Devuelve el identificador de la variable, estados en el orden del modelo,
probabilidades normalizadas y una copia de la evidencia utilizada.

#### Consultar una probabilidad concreta

```ts
const probability = engine.probability(
  "Q2_Purchase_Intention",
  "Yes",
  { Q8_Sensory_Uniqueness: "Yes" },
);
```

#### Probabilidad de evidencia

```ts
const probability = engine.probabilityOfEvidence({
  Q3_Recommendation: "Yes",
});
```

Las variables o estados desconocidos generan `InferenceError`. La inferencia es
exacta: enumera las variables ocultas en orden topológico y utiliza directamente
las CPT exportadas, sin aproximaciones ni reentrenamiento.

## Traductor de evidencia

La interfaz no necesita conocer los identificadores `Q1`–`Q8` ni los estados
internos del modelo. Puede construir sus formularios con `QUESTION_CATALOG` y
enviar las respuestas usando los identificadores semánticos estables:

```ts
import {
  ExactInferenceEngine,
  mapAnswersToEvidence,
  QUESTION_CATALOG,
} from "./src/index.ts";

const answers = {
  traditionalMexican: true,
  authenticElaboration: false,
  sensoryUniqueness: true,
};

const evidence = mapAnswersToEvidence(answers);
const result = engine.query("Q2_Purchase_Intention", evidence);
```

La traducción produce:

```ts
{
  Q1_Traditional_Mexican: "Yes",
  Q5_Authenticity_Elaboration: "No",
  Q8_Sensory_Uniqueness: "Yes",
}
```

`mapAnswersToEvidence` acepta conjuntos parciales —una pregunta omitida no
genera evidencia— y valida el límite de ejecución. La entrada debe ser un
objeto, cada clave debe pertenecer al catálogo y cada respuesta debe ser un
booleano o texto español `sí`, `si` o `no` (ignorando mayúsculas y espacios en
los extremos). `normalizeUserAnswers` convierte esas cadenas a booleanos en un
objeto nuevo antes de la traducción. Otras cadenas y los números se rechazan
con `EvidenceMapperError`.

`validateUserAnswers` está disponible por separado cuando la interfaz necesita
validar objetos estrictamente booleanos; no convierte texto. `UserAnswers`,
`QuestionId` y `Question` forman el contrato TypeScript compartido con la futura
PWA.

## Pruebas

```text
docker compose run --rm node npm --prefix inference-engine test
```

Los casos de equivalencia se generan con `pgmpy VariableElimination`:

```text
docker compose run --rm python python \
  inference-engine/tools/generate_python_reference.py \
  model-export/model.json \
  inference-engine/tests/fixtures/python-reference.json
```

El fixture registra el SHA-256 del modelo para impedir comparaciones contra una
versión distinta.

## Alcance

La implementación cubre carga, validación semántica, evidencia, consultas de
una variable, probabilidad de evidencia e inferencia exacta. Los casos de
equivalencia comprueban consultas binarias, no binarias, con evidencia única y
con evidencia múltiple. La evidencia de probabilidad cero se rechaza antes de
devolver una distribución condicionada.
