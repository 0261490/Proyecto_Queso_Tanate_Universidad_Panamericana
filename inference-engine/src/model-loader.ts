import type {
  BayesianModel,
  ModelCpt,
  ModelEdge,
  ModelNode,
} from "./types.ts";

const FORMAT = "proyecto-tenate-bayesian-model";
const NORMALIZATION_TOLERANCE = 1e-12;

export class ModelValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ModelValidationError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireRecord(value: unknown, label: string): Record<string, unknown> {
  if (!isRecord(value)) {
    throw new ModelValidationError(`${label} must be an object.`);
  }
  return value;
}

function requireString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new ModelValidationError(`${label} must be a non-empty string.`);
  }
  return value;
}

function requireStringArray(value: unknown, label: string): string[] {
  if (!Array.isArray(value) || value.length === 0) {
    throw new ModelValidationError(`${label} must be a non-empty array.`);
  }
  const result = value.map((item, index) =>
    requireString(item, `${label}[${index}]`),
  );
  if (new Set(result).size !== result.length) {
    throw new ModelValidationError(`${label} contains duplicate values.`);
  }
  return result;
}

function arraysEqual(left: readonly string[], right: readonly string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function topologicalSort(nodes: readonly string[], edges: readonly ModelEdge[]): string[] {
  const children = new Map(nodes.map((node) => [node, [] as string[]]));
  const indegree = new Map(nodes.map((node) => [node, 0]));

  for (const edge of edges) {
    children.get(edge.source)?.push(edge.target);
    indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1);
  }

  const ready = nodes.filter((node) => indegree.get(node) === 0).sort();
  const ordered: string[] = [];
  while (ready.length > 0) {
    const node = ready.shift()!;
    ordered.push(node);
    for (const child of (children.get(node) ?? []).sort()) {
      const next = (indegree.get(child) ?? 0) - 1;
      indegree.set(child, next);
      if (next === 0) {
        ready.push(child);
        ready.sort();
      }
    }
  }

  if (ordered.length !== nodes.length) {
    throw new ModelValidationError("Model edges do not form a directed acyclic graph.");
  }
  return ordered;
}

export function loadModel(raw: unknown): BayesianModel {
  const root = requireRecord(raw, "model");
  if (root.format !== FORMAT) {
    throw new ModelValidationError(`Unsupported model format: ${String(root.format)}.`);
  }
  if (root.schema_version !== 1) {
    throw new ModelValidationError(`Unsupported schema version: ${String(root.schema_version)}.`);
  }

  const modelVersion = requireString(root.model_version, "model_version");
  const metadata = requireRecord(root.metadata, "metadata");

  if (!Array.isArray(root.nodes) || root.nodes.length === 0) {
    throw new ModelValidationError("nodes must be a non-empty array.");
  }
  const nodes: ModelNode[] = root.nodes.map((value, index) => {
    const item = requireRecord(value, `nodes[${index}]`);
    return {
      id: requireString(item.id, `nodes[${index}].id`),
      states: requireStringArray(item.states, `nodes[${index}].states`),
    };
  });
  const nodeIds = nodes.map((node) => node.id);
  if (new Set(nodeIds).size !== nodeIds.length) {
    throw new ModelValidationError("Node identifiers must be unique.");
  }
  const statesByNode = new Map(nodes.map((node) => [node.id, node.states]));

  if (!Array.isArray(root.edges)) {
    throw new ModelValidationError("edges must be an array.");
  }
  const edgeKeys = new Set<string>();
  const edges: ModelEdge[] = root.edges.map((value, index) => {
    const item = requireRecord(value, `edges[${index}]`);
    const source = requireString(item.source, `edges[${index}].source`);
    const target = requireString(item.target, `edges[${index}].target`);
    if (!statesByNode.has(source) || !statesByNode.has(target)) {
      throw new ModelValidationError(`edges[${index}] references an unknown node.`);
    }
    const key = `${source}\u0000${target}`;
    if (edgeKeys.has(key)) {
      throw new ModelValidationError(`Duplicate edge: ${source} -> ${target}.`);
    }
    edgeKeys.add(key);
    return { source, target };
  });
  const topologicalOrder = topologicalSort(nodeIds, edges);

  if (!Array.isArray(root.cpts) || root.cpts.length !== nodes.length) {
    throw new ModelValidationError("There must be exactly one CPT per node.");
  }
  const cptNodes = new Set<string>();
  const cpts: ModelCpt[] = root.cpts.map((value, index) => {
    const item = requireRecord(value, `cpts[${index}]`);
    const node = requireString(item.node, `cpts[${index}].node`);
    if (!statesByNode.has(node) || cptNodes.has(node)) {
      throw new ModelValidationError(`Invalid or duplicate CPT node: ${node}.`);
    }
    cptNodes.add(node);

    const parents = Array.isArray(item.parents)
      ? item.parents.map((parent, parentIndex) =>
          requireString(parent, `cpts[${index}].parents[${parentIndex}]`),
        )
      : (() => {
          throw new ModelValidationError(`cpts[${index}].parents must be an array.`);
        })();
    if (new Set(parents).size !== parents.length) {
      throw new ModelValidationError(`CPT ${node} contains duplicate parents.`);
    }
    const expectedParents = edges
      .filter((edge) => edge.target === node)
      .map((edge) => edge.source)
      .sort();
    if (!arraysEqual(parents, expectedParents)) {
      throw new ModelValidationError(`CPT ${node} parents do not match the DAG.`);
    }

    const rawStateNames = requireRecord(item.state_names, `CPT ${node} state_names`);
    const stateNames: Record<string, readonly string[]> = {};
    for (const variable of [node, ...parents]) {
      const states = requireStringArray(rawStateNames[variable], `CPT ${node} states for ${variable}`);
      if (!arraysEqual(states, statesByNode.get(variable)!)) {
        throw new ModelValidationError(`CPT ${node} states for ${variable} do not match the node.`);
      }
      stateNames[variable] = states;
    }

    const nodeStates = statesByNode.get(node)!;
    const columns = parents.reduce(
      (count, parent) => count * statesByNode.get(parent)!.length,
      1,
    );
    if (!Array.isArray(item.values) || item.values.length !== nodeStates.length) {
      throw new ModelValidationError(`CPT ${node} has an invalid row count.`);
    }
    const values = item.values.map((row, rowIndex) => {
      if (!Array.isArray(row) || row.length !== columns) {
        throw new ModelValidationError(`CPT ${node} row ${rowIndex} has an invalid column count.`);
      }
      return row.map((probability, columnIndex) => {
        if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) {
          throw new ModelValidationError(
            `CPT ${node}[${rowIndex}][${columnIndex}] is not a probability.`,
          );
        }
        return probability;
      });
    });
    for (let column = 0; column < columns; column += 1) {
      const total = values.reduce((sum, row) => sum + row[column], 0);
      if (Math.abs(total - 1) > NORMALIZATION_TOLERANCE) {
        throw new ModelValidationError(`CPT ${node} column ${column} is not normalized.`);
      }
    }

    return { node, parents, stateNames, values };
  });

  return {
    format: FORMAT,
    schemaVersion: 1,
    modelVersion,
    metadata,
    nodes,
    edges,
    cpts,
    topologicalOrder,
  };
}

export function loadModelFromJson(json: string): BayesianModel {
  try {
    return loadModel(JSON.parse(json));
  } catch (error) {
    if (error instanceof ModelValidationError) {
      throw error;
    }
    throw new ModelValidationError(
      `Invalid model JSON: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}
