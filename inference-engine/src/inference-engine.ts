import type {
  BayesianModel,
  Evidence,
  ModelCpt,
  ModelNode,
  QueryResult,
} from "./types.ts";

export class InferenceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InferenceError";
  }
}

export class ExactInferenceEngine {
  readonly model: BayesianModel;
  readonly #nodes: ReadonlyMap<string, ModelNode>;
  readonly #cpts: ReadonlyMap<string, ModelCpt>;

  constructor(model: BayesianModel) {
    this.model = model;
    this.#nodes = new Map(model.nodes.map((node) => [node.id, node]));
    this.#cpts = new Map(model.cpts.map((cpt) => [cpt.node, cpt]));
  }

  query(variable: string, evidence: Evidence = {}): QueryResult {
    const node = this.#requireNode(variable);
    this.#validateEvidence(evidence);

    if (Object.hasOwn(evidence, variable)) {
      const evidenceProbability = this.#enumerateAll(0, { ...evidence });
      if (!Number.isFinite(evidenceProbability) || evidenceProbability <= 0) {
        throw new InferenceError("Evidence has zero or invalid probability.");
      }
      const observed = evidence[variable];
      return {
        variable,
        states: node.states,
        probabilities: node.states.map((state) => (state === observed ? 1 : 0)),
        evidence: { ...evidence },
      };
    }

    const weights = node.states.map((state) =>
      this.#enumerateAll(0, { ...evidence, [variable]: state }),
    );
    const total = weights.reduce((sum, value) => sum + value, 0);
    if (!Number.isFinite(total) || total <= 0) {
      throw new InferenceError("Evidence has zero or invalid probability.");
    }

    return {
      variable,
      states: node.states,
      probabilities: weights.map((value) => value / total),
      evidence: { ...evidence },
    };
  }

  probabilityOfEvidence(evidence: Evidence): number {
    this.#validateEvidence(evidence);
    return this.#enumerateAll(0, { ...evidence });
  }

  probability(variable: string, state: string, evidence: Evidence = {}): number {
    const result = this.query(variable, evidence);
    const index = result.states.indexOf(state);
    if (index < 0) {
      throw new InferenceError(`Unknown state ${JSON.stringify(state)} for ${variable}.`);
    }
    return result.probabilities[index];
  }

  #enumerateAll(index: number, assignment: Record<string, string>): number {
    if (index >= this.model.topologicalOrder.length) {
      return 1;
    }

    const variable = this.model.topologicalOrder[index];
    const node = this.#nodes.get(variable)!;
    const observed = assignment[variable];
    if (observed !== undefined) {
      return (
        this.#conditionalProbability(variable, observed, assignment) *
        this.#enumerateAll(index + 1, assignment)
      );
    }

    let total = 0;
    for (const state of node.states) {
      assignment[variable] = state;
      total +=
        this.#conditionalProbability(variable, state, assignment) *
        this.#enumerateAll(index + 1, assignment);
    }
    delete assignment[variable];
    return total;
  }

  #conditionalProbability(
    variable: string,
    state: string,
    assignment: Readonly<Record<string, string>>,
  ): number {
    const cpt = this.#cpts.get(variable)!;
    const stateIndex = cpt.stateNames[variable].indexOf(state);
    if (stateIndex < 0) {
      throw new InferenceError(`Unknown state ${JSON.stringify(state)} for ${variable}.`);
    }

    let column = 0;
    for (const parent of cpt.parents) {
      const parentState = assignment[parent];
      if (parentState === undefined) {
        throw new InferenceError(`Parent ${parent} must be assigned before ${variable}.`);
      }
      const parentStates = cpt.stateNames[parent];
      const parentIndex = parentStates.indexOf(parentState);
      if (parentIndex < 0) {
        throw new InferenceError(`Unknown state ${JSON.stringify(parentState)} for ${parent}.`);
      }
      column = column * parentStates.length + parentIndex;
    }
    return cpt.values[stateIndex][column];
  }

  #requireNode(variable: string): ModelNode {
    const node = this.#nodes.get(variable);
    if (!node) {
      throw new InferenceError(`Unknown query variable: ${variable}.`);
    }
    return node;
  }

  #validateEvidence(evidence: Evidence): void {
    for (const [variable, state] of Object.entries(evidence)) {
      const node = this.#requireNode(variable);
      if (!node.states.includes(state)) {
        throw new InferenceError(`Unknown state ${JSON.stringify(state)} for ${variable}.`);
      }
    }
  }
}
