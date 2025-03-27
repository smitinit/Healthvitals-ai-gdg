export type Symptom = {
  id: string;
  name: string;
  severity: number;
  duration: string;
};

export type BodyArea = {
  id: string;
  name: string;
  symptoms: string[];
};

export interface AnalysisResult {
  possibleConditions: {
    name: string;
    probability: number;
    description: string;
    category: "respiratory" | "digestive" | "neurological" | "general";
  }[];
  recommendation: string;
  urgency: "low" | "medium" | "high";
  followUpActions: string[];
  riskFactors: string[];
  mealRecommendations: {
    breakfast: string[];
    lunch: string[];
    dinner: string[];
    note?: string;
  };
  exercisePlan: string[];
  diseases: string[];
  preventiveMeasures: string[];
  medicineRecommendations: string[];
  ayurvedicMedication?: {
    recommendations: Array<{
      name: string;
      description: string;
      importance: string;
      benefits: string;
    }>;
  };
  dos: string[];
  donts: string[];
  conditionSpecificData?: {
    [conditionName: string]: {
      recommendedActions?: string[];
      preventiveMeasures?: string[];
    }
  };
  reportsRequired?: {
    name: string;
    purpose?: string;
    benefits?: string;
    analysisDetails?: string;
    preparationRequired?: string;
    recommendationReason: string;
  }[];
  healthScore?: number;
  
  // User information fields
  age?: string;
  gender?: string;
  height?: string;
  weight?: string;
  medicalHistory?: string[];
  medicalHistoryText?: string;
  exerciseFrequency?: string;
  sleepQuality?: string;
  stressLevel?: string;
  dietPreference?: string;
  allergies?: string;
  currentMedications?: string;
  recentLifeChanges?: string;
}

export type MedicalCondition = {
  name: string;
  description: string;
  symptoms: string[];
  urgency: "low" | "medium" | "high";
  treatmentOptions: string[];
  recoveryTime: string;
  preventionTips: string[];
};

export type Doctor = {
  id: number;
  name: string;
  specialty: string;
  distance: string;
  availability: string;
  rating: number;
  image: string;
  address: string;
  phone: string;
};

export type MedicalArticle = {
  id: number;
  title: string;
  excerpt: string;
  source: string;
  date: string;
  url: string;
};

export type DummyConditions = {
  respiratory: MedicalCondition[];
  digestive: MedicalCondition[];
  neurological: MedicalCondition[];
};
