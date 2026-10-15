# Motor Bayesiano TypeScript

## Estado

Sección 3 completada. El motor carga el `model.json`
congelado en la Sección 2, valida su estructura y ejecuta inferencia exacta por
enumeración sin servidor ni dependencias de ejecución externas.

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

La primera parte del traductor publica un catálogo único para que la interfaz
muestre preguntas naturales y utilice identificadores semánticos estables. Los
componentes visuales pueden consumir `QUESTION_CATALOG` sin codificar de nuevo
los textos ni sus correspondencias:

```ts
import { QUESTION_CATALOG } from "./src/index.ts";

for (const question of QUESTION_CATALOG) {
  renderQuestion(question.id, question.prompt);
}
```

Cada entrada relaciona `id` (interfaz), `prompt` (pregunta natural) y `variable`
(modelo). Los tipos `UserAnswers`, `QuestionId` y `Question` se derivan del
catálogo y forman el contrato TypeScript con la futura PWA. La validación de
entrada y la conversión a estados `Yes`/`No` corresponden a la segunda parte.

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
