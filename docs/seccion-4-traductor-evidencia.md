# Sección 4: Traductor de evidencia

## Estado

En desarrollo. Parte 2 de 3 completada: validación, normalización y traducción
de respuestas a evidencia bayesiana.

## División de la sección

1. Catálogo y contrato entre la interfaz y el modelo: completado.
2. Validación y traducción de respuestas: completado, incluido texto `sí/si/no`.
3. Pruebas de integración y cierre documental: pendiente de cierre.

## Objetivo

La capa de interfaz trabaja con preguntas naturales, identificadores semánticos
y respuestas booleanas. La capa bayesiana trabaja con nombres científicos como
`Q5_Authenticity_Elaboration` y estados `Yes`/`No`. El traductor mantiene ese
límite en un único módulo para impedir que formularios, almacenamiento o
componentes dependan de la representación interna del modelo.

El texto español de las preguntas se deriva del significado conservado en los
nombres de las variables del conjunto científico. El material fuente disponible
no contiene un cuestionario español autoritativo; por ello, estos textos son el
contrato de interfaz del proyecto y no se presentan como citas literales del
instrumento original.

## Catálogo de correspondencias

| Identificador de interfaz | Pregunta natural | Variable del modelo |
|---|---|---|
| `traditionalMexican` | ¿Considera que el Queso Tenate es un producto tradicional mexicano? | `Q1_Traditional_Mexican` |
| `purchaseIntention` | ¿Compraría Queso Tenate? | `Q2_Purchase_Intention` |
| `recommendation` | ¿Recomendaría el Queso Tenate? | `Q3_Recommendation` |
| `gastronomicHeritage` | ¿Considera que el Queso Tenate forma parte del patrimonio gastronómico? | `Q4_Gastronomic_Heritage` |
| `authenticElaboration` | ¿Considera auténtico el proceso de elaboración del Queso Tenate? | `Q5_Authenticity_Elaboration` |
| `commercialPotential` | ¿Considera que el Queso Tenate tiene potencial comercial? | `Q6_Commercial_Potential` |
| `culturePreservation` | ¿Considera que el Queso Tenate contribuye a preservar la cultura y la tradición? | `Q7_Culture_Preservation` |
| `sensoryUniqueness` | ¿Considera que el Queso Tenate posee características sensoriales únicas? | `Q8_Sensory_Uniqueness` |

La PWA podrá renderizar las preguntas desde `QUESTION_CATALOG`; no necesita
mostrar la tercera columna al usuario.

## Contrato de entrada

`mapAnswersToEvidence(input)` recibe un objeto parcial con respuestas booleanas
o texto español `sí`, `si` y `no`. Primero llama a `normalizeUserAnswers(input)`,
que devuelve un objeto nuevo con respuestas booleanas:

```ts
type UserAnswers = Partial<Record<QuestionId, boolean>>;
```

- `true` significa respuesta afirmativa;
- `false` significa respuesta negativa;
- una clave ausente significa pregunta no respondida y no genera evidencia;
- un objeto vacío representa inferencia sin evidencia perceptual.

La normalización ignora mayúsculas y espacios en los extremos, y admite tildes
Unicode compuestas o descompuestas. `sí` y `si` se convierten a `true`; `no` a
`false`. Los booleanos conservan su valor. No se aceptan arreglos, valores nulos,
identificadores desconocidos, respuestas con valor `undefined`, otras cadenas
como `"Yes"`, `"true"` o `"false"`, ni números como `1`.

Toda entrada inválida genera `EvidenceMapperError`. La propiedad opcional
`questionId` identifica la respuesta problemática cuando existe una clave
concreta. `validateUserAnswers(input)` conserva la validación estricta de objetos
con respuestas booleanas; no normaliza texto. Para consumir texto se utiliza
`normalizeUserAnswers(input)` o directamente `mapAnswersToEvidence(input)`.

## Contrato de salida

La salida implementa `Evidence`, el tipo que acepta directamente
`ExactInferenceEngine`:

```ts
mapAnswersToEvidence({
  traditionalMexican: true,
  authenticElaboration: false,
  sensoryUniqueness: true,
});

// Resultado
{
  Q1_Traditional_Mexican: "Yes",
  Q5_Authenticity_Elaboration: "No",
  Q8_Sensory_Uniqueness: "Yes",
}
```

El traductor siempre crea un objeto nuevo y no modifica la entrada. Los estados
emitidos son exactamente `Yes` o `No`, tal como exige el modelo congelado.

## Separación de responsabilidades

- La interfaz decide qué preguntas mostrar y conserva respuestas booleanas.
- `evidence-mapper.ts` conoce la correspondencia entre interfaz y modelo.
- El motor valida y consume únicamente evidencia bayesiana.
- El traductor no altera CPT, estructura, estados ni probabilidades.

Cambiar un texto visible no requiere modificar el motor. Cambiar un nombre
interno del modelo exige actualizar únicamente el catálogo y sus pruebas. Los
identificadores semánticos se consideran parte estable del contrato con la PWA.

## Pruebas y validación

La suite comprueba:

- cobertura única de las ocho variables Q1–Q8;
- existencia de cada variable del catálogo en el modelo congelado;
- traducción de respuestas afirmativas y negativas;
- normalización de texto español, mayúsculas, espacios y tildes Unicode;
- conjuntos completos, parciales y vacíos;
- rechazo de entradas, claves y tipos inválidos;
- metadatos del error de validación;
- compatibilidad directa de la salida con el motor de inferencia.

Comando reproducible:

```text
docker compose run --rm node npm --prefix inference-engine test
```

Validación de la parte 2: 28 pruebas del motor aprobadas, incluidas 10 del
traductor; cero fallos. Se comprobó además manualmente la conversión de texto
y el rechazo de respuestas inválidas en PowerShell.
