import type { AnalysisResult, Symptom } from "@/types/symptom-types";

export const generateAnalysisResult = (
  selectedSymptoms: Symptom[]
): AnalysisResult => {
  // Generate analysis result based on symptoms
  const hasRespiratorySymptoms = selectedSymptoms.some((s) =>
    ["Cough", "Sore throat", "Runny nose", "Congestion", "Sneezing"].includes(
      s.name
    )
  );

  const hasHeadacheSymptoms = selectedSymptoms.some((s) =>
    ["Headache", "Facial pain", "Sinus pressure"].includes(s.name)
  );

  const hasDigestiveSymptoms = selectedSymptoms.some((s) =>
    ["Nausea", "Vomiting", "Diarrhea", "Abdominal pain", "Heartburn"].includes(
      s.name
    )
  );

  // Create a tailored result based on the symptoms
  const analysisResult: AnalysisResult = {
    possibleConditions: [],
    recommendation: "",
    urgency: "low",
    followUpActions: [],
    riskFactors: [],
  };

  if (hasRespiratorySymptoms) {
    analysisResult.possibleConditions.push(
      {
        name: "Common Cold",
        probability: 75,
        description: "A viral infection of the upper respiratory tract.",
        category: "respiratory",
      },
      {
        name: "Seasonal Allergies",
        probability: 65,
        description:
          "An immune response to environmental triggers like pollen.",
        category: "respiratory",
      }
    );

    if (hasHeadacheSymptoms) {
      analysisResult.possibleConditions.push({
        name: "Sinus Infection",
        probability: 60,
        description: "Inflammation of the sinuses, often following a cold.",
        category: "respiratory",
      });
    }

    analysisResult.recommendation =
      "Stay hydrated, rest, and consider over-the-counter cold medications. If symptoms persist for more than 7 days or worsen, consult a healthcare professional.";
    analysisResult.followUpActions = [
      "Monitor symptoms for 3-5 days",
      "Take over-the-counter decongestants if needed",
      "Use saline nasal spray for congestion",
    ];
    analysisResult.riskFactors = [
      "Exposure to others with similar symptoms",
      "Recent weather changes",
      "Seasonal allergens",
    ];
  } else if (hasDigestiveSymptoms) {
    analysisResult.possibleConditions.push(
      {
        name: "Gastroenteritis",
        probability: 70,
        description: "Inflammation of the stomach and intestines.",
        category: "digestive",
      },
      {
        name: "Acid Reflux",
        probability: 55,
        description: "Backward flow of stomach acid into the esophagus.",
        category: "digestive",
      }
    );

    analysisResult.recommendation =
      "Stay hydrated with clear fluids, follow the BRAT diet (bananas, rice, applesauce, toast), and rest. If symptoms persist for more than 48 hours or include severe pain, consult a healthcare professional.";
    analysisResult.urgency = "medium";
    analysisResult.followUpActions = [
      "Monitor hydration levels",
      "Gradually return to normal diet as symptoms improve",
      "Consider probiotics to restore gut flora",
    ];
    analysisResult.riskFactors = [
      "Recent consumption of undercooked food",
      "Exposure to others with similar symptoms",
      "Recent travel",
    ];
  } else if (hasHeadacheSymptoms) {
    analysisResult.possibleConditions.push(
      {
        name: "Tension Headache",
        probability: 80,
        description: "Common headache with mild to moderate pain.",
        category: "neurological",
      },
      {
        name: "Migraine",
        probability: 45,
        description: "Recurring headache with moderate to severe pain.",
        category: "neurological",
      }
    );

    analysisResult.recommendation =
      "Rest in a quiet, dark room. Try over-the-counter pain relievers and apply a cold or warm compress to your head. If headaches are severe or recurring, consult a healthcare professional.";
    analysisResult.followUpActions = [
      "Track headache patterns and triggers",
      "Consider stress reduction techniques",
      "Ensure adequate hydration and regular meals",
    ];
    analysisResult.riskFactors = [
      "Stress and anxiety",
      "Poor sleep patterns",
      "Screen time and eye strain",
    ];
  } else {
    // Default if no specific pattern is detected
    analysisResult.possibleConditions.push({
      name: "General Fatigue",
      probability: 65,
      description: "Temporary tiredness that can be caused by various factors.",
      category: "neurological",
    });

    analysisResult.recommendation =
      "Rest and monitor your symptoms. Ensure adequate hydration and nutrition. If symptoms persist or worsen, consult a healthcare professional.";
    analysisResult.followUpActions = [
      "Get adequate rest",
      "Stay hydrated",
      "Monitor for any new or worsening symptoms",
    ];
    analysisResult.riskFactors = [
      "Recent stress or lifestyle changes",
      "Inadequate sleep",
      "Poor nutrition",
    ];
  }

  // Determine urgency based on symptom severity
  const highSeveritySymptoms = selectedSymptoms.filter(
    (s) => s.severity >= 8
  ).length;
  if (highSeveritySymptoms >= 2) {
    analysisResult.urgency = "high";
  } else if (
    highSeveritySymptoms === 1 ||
    selectedSymptoms.filter((s) => s.severity >= 6).length >= 3
  ) {
    analysisResult.urgency = "medium";
  }

  return analysisResult;
};

// Helper function to check if a symptom already exists in the array
export const isSymptomAlreadySelected = (
  selectedSymptoms: Symptom[],
  symptomName: string
): boolean => {
  return selectedSymptoms.some(
    (s) => s.name.toLowerCase() === symptomName.toLowerCase()
  );
};

// Helper function to get a random integer between min and max (inclusive)
export const getRandomInt = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

// Helper function to get a random element from an array
export const getRandomElement = <T>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};
