export const QUESTION_CATALOG = [
  {
    id: "traditionalMexican",
    prompt: "¿Considera que el Queso Tenate es un producto tradicional mexicano?",
    variable: "Q1_Traditional_Mexican",
  },
  {
    id: "purchaseIntention",
    prompt: "¿Compraría Queso Tenate?",
    variable: "Q2_Purchase_Intention",
  },
  {
    id: "recommendation",
    prompt: "¿Recomendaría el Queso Tenate?",
    variable: "Q3_Recommendation",
  },
  {
    id: "gastronomicHeritage",
    prompt: "¿Considera que el Queso Tenate forma parte del patrimonio gastronómico?",
    variable: "Q4_Gastronomic_Heritage",
  },
  {
    id: "authenticElaboration",
    prompt: "¿Considera auténtico el proceso de elaboración del Queso Tenate?",
    variable: "Q5_Authenticity_Elaboration",
  },
  {
    id: "commercialPotential",
    prompt: "¿Considera que el Queso Tenate tiene potencial comercial?",
    variable: "Q6_Commercial_Potential",
  },
  {
    id: "culturePreservation",
    prompt: "¿Considera que el Queso Tenate contribuye a preservar la cultura y la tradición?",
    variable: "Q7_Culture_Preservation",
  },
  {
    id: "sensoryUniqueness",
    prompt: "¿Considera que el Queso Tenate posee características sensoriales únicas?",
    variable: "Q8_Sensory_Uniqueness",
  },
] as const;

export type Question = (typeof QUESTION_CATALOG)[number];
export type QuestionId = Question["id"];
export type UserAnswers = Readonly<Partial<Record<QuestionId, boolean>>>;
