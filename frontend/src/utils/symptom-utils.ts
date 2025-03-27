import type { AnalysisResult, Symptom } from "@/types/symptom-types";

const API_BASE_URL = 'http://localhost:5000/api';

export const generateAnalysisResult = async (
  selectedSymptoms: Symptom[],
  age: string,
  gender: string,
  medicalHistory: string[],
  dietPreference: string = "balanced",
  currentMedications: string = "",
  allergies: string = "",
  recentLifeChanges: string = "",
  symptomTriggers: string = "",
  exerciseFrequency: string = "moderate",
  sleepQuality: string = "fair",
  stressLevel: string = "moderate"
): Promise<AnalysisResult> => {
  try {
    console.log("Sending API request with:", {
      symptoms: selectedSymptoms,
      age,
      gender,
      medicalHistory,
      dietPreference,
      currentMedications,
      allergies,
      recentLifeChanges,
      symptomTriggers,
      exerciseFrequency,
      sleepQuality,
      stressLevel
    });

    const response = await fetch(`${API_BASE_URL}/analyze-symptoms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symptoms: selectedSymptoms,
        age,
        gender,
        medicalHistory,
        dietPreference,
        currentMedications,
        allergies,
        recentLifeChanges,
        symptomTriggers,
        exerciseFrequency,
        sleepQuality,
        stressLevel
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API response not OK:', response.status, errorText);
      throw new Error(`Failed to analyze symptoms: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const result = await response.json();
    console.log("API response received:", result);
    
    // Ensure all required fields are present in the result
    const defaultResult: AnalysisResult = {
      possibleConditions: [
        {
          name: "Analysis Result",
          probability: 100,
          description: "Based on the provided symptoms.",
          category: "general"
        }
      ],
      recommendation: "Please consult a healthcare professional for a proper diagnosis.",
      urgency: "medium",
      followUpActions: ["Consult a healthcare professional"],
      riskFactors: ["Self-diagnosis without professional consultation"],
      mealRecommendations: {
        breakfast: ["Consult a nutritionist for personalized recommendations"],
        lunch: ["Consult a nutritionist for personalized recommendations"],
        dinner: ["Consult a nutritionist for personalized recommendations"]
      },
      exercisePlan: ["Consult a healthcare professional before starting any exercise regimen"],
      diseases: ["Analysis could not determine specific diseases"],
      preventiveMeasures: ["Consult a healthcare professional"],
      medicineRecommendations: ["Do not self-medicate, consult a healthcare professional"],
      dos: ["Consult a healthcare professional"],
      donts: ["Do not self-diagnose or self-medicate"]
    };
    
    // Merge the API result with the default result to ensure all fields exist
    const completeResult: AnalysisResult = {
      ...defaultResult,
      ...result,
      mealRecommendations: {
        ...defaultResult.mealRecommendations,
        ...(result.mealRecommendations || {})
      }
    };
    
    return completeResult;
  } catch (error) {
    console.error('Error analyzing symptoms:', error);
    throw error;
  }
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
