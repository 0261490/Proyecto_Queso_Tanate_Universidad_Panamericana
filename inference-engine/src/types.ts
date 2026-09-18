export type Evidence = Readonly<Record<string, string>>;

export interface ModelNode {
  readonly id: string;
  readonly states: readonly string[];
}

export interface ModelEdge {
  readonly source: string;
  readonly target: string;
}

export interface ModelCpt {
  readonly node: string;
  readonly parents: readonly string[];
  readonly stateNames: Readonly<Record<string, readonly string[]>>;
  readonly values: readonly (readonly number[])[];
}

export interface BayesianModel {
  readonly format: "proyecto-tenate-bayesian-model";
  readonly schemaVersion: 1;
  readonly modelVersion: string;
  readonly metadata: Readonly<Record<string, unknown>>;
  readonly nodes: readonly ModelNode[];
  readonly edges: readonly ModelEdge[];
  readonly cpts: readonly ModelCpt[];
  readonly topologicalOrder: readonly string[];
}

export interface QueryResult {
  readonly variable: string;
  readonly states: readonly string[];
  readonly probabilities: readonly number[];
  readonly evidence: Evidence;
}
