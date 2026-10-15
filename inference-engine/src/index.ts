export { ExactInferenceEngine, InferenceError } from "./inference-engine.ts";
export { QUESTION_CATALOG } from "./evidence-mapper.ts";
export {
  loadModel,
  loadModelFromJson,
  ModelValidationError,
} from "./model-loader.ts";
export type {
  BayesianModel,
  Evidence,
  ModelCpt,
  ModelEdge,
  ModelNode,
  QueryResult,
} from "./types.ts";
export type {
  Question,
  QuestionId,
  UserAnswers,
} from "./evidence-mapper.ts";
