# Sección 4: Traductor de evidencia

## Estado

En desarrollo. Parte 1 de 3 completada: catálogo y contrato entre interfaz y
modelo.

## División de la sección

1. catálogo y contrato entre la interfaz y el modelo;
2. validación y traducción de respuestas;
3. pruebas de integración y cierre documental.

## Objetivo de la primera parte

La capa de interfaz trabaja con preguntas naturales e identificadores
semánticos. La capa bayesiana trabaja con nombres científicos como
`Q5_Authenticity_Elaboration`. El catálogo mantiene la correspondencia en un
único módulo para evitar que formularios y componentes repitan o inventen esos
nombres.

El texto español se deriva del significado conservado en los nombres de las
variables del conjunto científico. El material fuente disponible no contiene un
cuestionario español autoritativo; estos textos son el contrato de interfaz del
proyecto y no se presentan como citas literales del instrumento original.

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

La futura PWA podrá renderizar `prompt` y usar `id` en sus controles sin mostrar
la propiedad técnica `variable` al usuario.

## Contrato TypeScript

El catálogo es una constante inmutable. Sus tipos se derivan de la misma fuente:

```ts
type Question = (typeof QUESTION_CATALOG)[number];
type QuestionId = Question["id"];
type UserAnswers = Readonly<Partial<Record<QuestionId, boolean>>>;
```

- `Question` representa cualquiera de las ocho entradas;
- `QuestionId` acepta únicamente los identificadores publicados;
- `UserAnswers` representa respuestas booleanas, parciales y de solo lectura.

Esta parte todavía no convierte respuestas a evidencia. Esa responsabilidad se
incorporará en la parte 2 para mantener cada actualización verificable.

## Pruebas de esta parte

La suite comprueba que:

- existen exactamente ocho correspondencias;
- no se repiten identificadores ni variables;
- el orden cubre Q1–Q8;
- todas las variables existen en el modelo congelado;
- todas las preguntas conservan formato interrogativo en español.

Comando reproducible:

```text
docker compose run --rm node npm --prefix inference-engine test
```
