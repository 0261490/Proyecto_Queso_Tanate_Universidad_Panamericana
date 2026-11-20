import { mapAnswersToEvidence, QUESTION_CATALOG, type Evidence, type UserAnswers } from "../../../inference-engine/src/index.ts";

export const DATABASE_NAME = "tenate-history";
export const DATABASE_VERSION = 1;
export const STORE_NAME = "assessments";

export interface AssessmentRecord {
  schemaVersion: 1;
  id: string;
  createdAt: string;
  model: { version: string; sha256: string };
  answers: UserAnswers;
  evidence: Evidence;
  result: { variable: "Q2_Purchase_Intention"; state: "Yes"; probability: number };
}

const questionIds = QUESTION_CATALOG.filter(q => q.id !== "purchaseIntention").map(q => q.id);

export function validateRecord(value: unknown): asserts value is AssessmentRecord {
  const record = value as AssessmentRecord;
  if (!record || record.schemaVersion !== 1 || typeof record.id !== "string" || !record.id ||
      typeof record.createdAt !== "string" || !Number.isFinite(Date.parse(record.createdAt)) ||
      !record.model || typeof record.model.version !== "string" || !record.model.version ||
      !/^[a-f0-9]{64}$/.test(record.model.sha256) || !record.answers ||
      Object.keys(record.answers).length !== questionIds.length ||
      questionIds.some(id => typeof record.answers[id] !== "boolean") ||
      !record.result || record.result.variable !== "Q2_Purchase_Intention" || record.result.state !== "Yes" ||
      !Number.isFinite(record.result.probability) || record.result.probability < 0 || record.result.probability > 1) {
    throw new Error("Invalid assessment record");
  }
  const expected = mapAnswersToEvidence(record.answers);
  if (!record.evidence || Object.keys(expected).length !== Object.keys(record.evidence).length ||
      Object.entries(expected).some(([key, state]) => record.evidence[key] !== state)) {
    throw new Error("Evidence does not match answers");
  }
}

/** No network or inference dependencies: snapshots are persisted atomically. */
export class HistoryStore {
  private factory: IDBFactory | undefined;
  private name: string;

  constructor(factory: IDBFactory | undefined = globalThis.indexedDB, name = DATABASE_NAME) {
    this.factory = factory;
    this.name = name;
  }

  private open(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      if (!this.factory) return reject(new Error("IndexedDB unavailable"));
      const request = this.factory.open(this.name, DATABASE_VERSION);
      let settled = false;
      const fail = (error: unknown) => {
        settled = true;
        clearTimeout(timer);
        reject(error);
      };
      const timer = setTimeout(() => fail(new Error("Storage open timeout")), 5000);
      request.onblocked = () => fail(new Error("Storage upgrade blocked; close other tabs"));
      request.onerror = () => fail(request.error);
      request.onupgradeneeded = () => {
        if (settled) { request.transaction?.abort(); return; }
        const store = request.result.createObjectStore(STORE_NAME, { keyPath: "id" });
        store.createIndex("createdAt", "createdAt");
      };
      request.onsuccess = () => {
        clearTimeout(timer);
        const db = request.result;
        if (settled) { db.close(); return; }
        settled = true;
        db.onversionchange = () => db.close();
        resolve(db);
      };
    });
  }

  private async transact<T>(mode: IDBTransactionMode, run: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
    const db = await this.open();
    try {
      return await new Promise<T>((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, mode);
        // A successful request is not sufficient: only transaction completion confirms durability.
        tx.onabort = () => reject(tx.error ?? new Error("Storage transaction aborted"));
        tx.onerror = () => { /* onabort reports the final transaction failure */ };
        const request = run(tx.objectStore(STORE_NAME));
        tx.oncomplete = () => resolve(request.result);
      });
    } finally {
      db.close();
    }
  }

  async add(record: AssessmentRecord): Promise<void> {
    validateRecord(record);
    // Clone before awaiting open so subsequent form changes cannot mutate this evaluation.
    const snapshot = structuredClone(record);
    await this.transact("readwrite", store => store.add(snapshot));
  }

  async list(): Promise<AssessmentRecord[]> {
    const records = await this.transact("readonly", store => store.index("createdAt").getAll());
    records.forEach(validateRecord);
    return records.reverse();
  }

  async delete(id: string): Promise<void> {
    await this.transact("readwrite", store => store.delete(id));
  }

  async clear(): Promise<void> {
    await this.transact("readwrite", store => store.clear());
  }
}
