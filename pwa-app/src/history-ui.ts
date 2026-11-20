import { QUESTION_CATALOG } from "../../inference-engine/src/index.ts";
import { formatProbability } from "./presentation.ts";
import { HistoryStore, type AssessmentRecord } from "./storage/history.ts";

export function createHistoryUI(store: HistoryStore, currentModelHash: string) {
  const list = document.getElementById("history-list")!;
  const status = document.getElementById("history-status")!;
  const clear = document.getElementById("clear-history") as HTMLButtonElement;
  const refresh = document.getElementById("refresh-history") as HTMLButtonElement;
  let generation = 0;

  async function reload(): Promise<void> {
    const current = ++generation;
    try {
      const records = await store.list();
      if (current !== generation) return;
      list.replaceChildren(...records.map(renderRecord));
      clear.disabled = records.length === 0;
      status.textContent = records.length === 0
        ? "Todavía no hay evaluaciones guardadas."
        : records.length === 1
          ? "1 evaluación guardada en este navegador."
          : `${records.length} evaluaciones guardadas en este navegador.`;
    } catch {
      if (current !== generation) return;
      list.replaceChildren();
      clear.disabled = true;
      status.textContent = "No se pudo leer el historial. Puede seguir evaluando y volver a intentar con Actualizar historial.";
    }
  }

  function renderRecord(record: AssessmentRecord): HTMLElement {
    const item = document.createElement("li");
    item.className = "history-card";
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    const date = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(record.createdAt));
    summary.textContent = `${date} · ${formatProbability(record.result.probability)}`;
    details.append(summary);
    if (record.model.sha256 !== currentModelHash) {
      const note = document.createElement("p");
      note.textContent = "Este resultado se calculó con una versión anterior del modelo y se conserva sin recalcular.";
      details.append(note);
    }
    const answers = document.createElement("dl");
    for (const question of QUESTION_CATALOG.filter(q => q.id !== "purchaseIntention")) {
      const label = document.createElement("dt");
      label.textContent = question.prompt;
      const value = document.createElement("dd");
      value.textContent = record.answers[question.id] ? "Sí" : "No";
      answers.append(label, value);
    }
    details.append(answers);
    const remove = document.createElement("button");
    remove.className = "button button-secondary";
    remove.type = "button";
    remove.textContent = "Eliminar evaluación";
    remove.setAttribute("aria-label", `Eliminar evaluación del ${date}`);
    remove.addEventListener("click", async () => {
      if (!window.confirm("¿Eliminar esta evaluación del historial? Esta acción no se puede deshacer.")) return;
      remove.disabled = true;
      try {
        await store.delete(record.id);
        await reload();
        refresh.focus();
      } catch {
        remove.disabled = false;
        status.textContent = "No se pudo eliminar la evaluación. Intente de nuevo.";
      }
    });
    item.append(details, remove);
    return item;
  }

  clear.addEventListener("click", async () => {
    if (!window.confirm("¿Eliminar todo el historial de este navegador? Esta acción no se puede deshacer.")) return;
    clear.disabled = true;
    try {
      await store.clear();
      await reload();
      refresh.focus();
    } catch {
      clear.disabled = false;
      status.textContent = "No se pudo eliminar el historial. Intente de nuevo.";
    }
  });
  refresh.addEventListener("click", () => { void reload(); });
  void reload();
  return { reload };
}
