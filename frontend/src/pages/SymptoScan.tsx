"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  ArrowRight,
  ArrowLeft,
  Loader2,
  Stethoscope,
  Activity,
} from "lucide-react";
import { useNavigate } from "react-router";
import { useAuth } from "@clerk/clerk-react";
import type { Symptom, AnalysisResult } from "@/types/symptom-types";
import { bodyAreas } from "@/data/symptom-data";

import SymptomSelector from "@/components/symptom-selector";
import PersonalInfo from "@/components/personal-info";
import AdditionalInfo from "@/components/additional-info";
import AnalysisResultComponent from "@/components/analysis-result/analysis-result";
import LoadingAnalysis from "@/components/loading-analysis";
import ConfettiEffect from "@/components/confetti-effect";
import API_BASE_URL from "@/config";

export default function SymptomScanEnhanced({
  isPro = false,
}: {
  isPro?: boolean;
}) {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [selectedSymptoms, setSelectedSymptoms] = useState<Symptom[]>([]);
  const [age, setAge] = useState<string>("");
  const [gender, setGender] = useState<string>("");
  const [medicalHistory, setMedicalHistory] = useState<string[]>([]);
  const [medicalHistoryText, setMedicalHistoryText] = useState<string>("");
  const [height, setHeight] = useState<string>("");
  const [weight, setWeight] = useState<string>("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [hasUsedQuickAnalysis, setHasUsedQuickAnalysis] = useState(false);
  const navigate = useNavigate();

  const { isSignedIn, getToken } = useAuth();

  // Additional information states
  const [exerciseFrequency, setExerciseFrequency] =
    useState<string>("moderate");
  const [sleepQuality, setSleepQuality] = useState<string>("fair");
  const [stressLevel, setStressLevel] = useState<string>("moderate");
  const [dietPreference, setDietPreference] = useState<string>("balanced");
  const [recentLifeChanges, setRecentLifeChanges] = useState<string>("");
  const [allergies, setAllergies] = useState<string>("");
  const [currentMedications, setCurrentMedications] = useState<string>("");

  // Use localStorage to track if anonymous user has used the quick analysis
  useEffect(() => {
    // Only check if this is the regular symptoscan and user is not signed in
    if (!isPro && !isSignedIn) {
      const hasUsedBefore =
        localStorage.getItem("hasUsedSymptomScan") === "true";
      setHasUsedQuickAnalysis(hasUsedBefore);
    }
  }, [isPro, isSignedIn]);

  // Check if user needs to be redirected to sign in
  useEffect(() => {
    if (!isPro && !isSignedIn && hasUsedQuickAnalysis) {
      // If anonymous user has already used quick analysis, redirect to sign in
      navigate("/symptoscan-pro");
    }
  }, [isPro, isSignedIn, hasUsedQuickAnalysis, navigate]);

  // Update progress based on current step
  useEffect(() => {
    const progressMap: { [key: number]: number } = {
      1: 25,
      2: 50,
      3: 75,
      4: 100,
    };
    setProgress(progressMap[step] || 0);
  }, [step]);

  // Check if this is quick-analyze path or symptoscan-pro path
  // const isQuickAnalyze = !isPro;

  // Submit handler for the form
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setResult(null);

    // console.log("Form submitted with symptoms:", selectedSymptoms);
    if (selectedSymptoms.length === 0) {
      alert("Please select at least one symptom");
      setIsLoading(false);
      return;
    }

    if (!age) {
      alert("Please enter your age");
      setIsLoading(false);
      return;
    }

    try {
      // Determine if this is a quick analysis or full analysis
      const isQuickAnalysis = !isPro || step !== 3;

      // console.log("Starting symptom analysis...");
      // console.log("Using Pro Mode:", isPro);
      // console.log("Current step:", step);
      // console.log("isQuickAnalysis determined to be:", isQuickAnalysis);

      // Log which endpoint we're using
      // console.log(
      //   "Using endpoint:",
      //   isQuickAnalysis ? "/api/quick-analyze" : "/api/analyze-symptoms"
      // );

      // Prepare request body
      let requestBody: any = {};

      if (isQuickAnalysis) {
        // Quick analysis just needs symptoms and age
        const symptomString = selectedSymptoms.map((s) => s.name).join(", ");
        // console.log("Quick analysis request:", {
        //   symptoms: symptomString,
        //   age,
        // });
        // console.log("Selected symptoms:", selectedSymptoms);
        requestBody = { symptoms: symptomString, age };
      } else {
        // Full analysis needs all the details
        // console.log("Full analysis request - using full symptom objects");
        // console.log("Selected symptoms:", selectedSymptoms);

        requestBody = {
          symptoms: selectedSymptoms, // Send the full symptom objects with severity and duration
          age,
          gender,
          height,
          weight,
          medicalHistory,
          medicalHistoryText, // Add the free-text medical history
          exerciseFrequency,
          sleepQuality,
          stressLevel,
          dietPreference,
          recentLifeChanges,
          allergies,
          currentMedications,
        };
      }

      // Make API request
      const endpoint = isQuickAnalysis
        ? `${API_BASE_URL}/api/quick-analyze`
        : `${API_BASE_URL}/api/analyze-symptoms`;
      // console.log("Sending request to:", API_BASE_URL);

      // Get the token if user is signed in
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (isSignedIn) {
        try {
          const token = await getToken();
          if (token) {
            headers["Authorization"] = `Bearer ${token}`;
            // Store token in sessionStorage for PDF download functionality
            window.sessionStorage.setItem("clerk-auth-token", token);
            // console.log("Added authorization token to request");
          } else {
            console.error("No token available despite user being signed in");
            throw new Error("Authentication token not available");
          }
        } catch (error) {
          // console.error("Error getting token:", error);
          throw new Error("Failed to get authentication token");
        }
      } else {
        console.error("User must be signed in to use this feature");
        throw new Error("Authentication required");
      }

      // console.log("Request payload:", JSON.stringify(requestBody, null, 2));

      const response = await fetch(endpoint, {
        method: "POST",
        headers,
        body: JSON.stringify(requestBody),
      });

      // console.log("Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API error response:", errorText);
        throw new Error(
          `Error ${response.status}: ${errorText || response.statusText}`
        );
      }

      const data = await response.json();
      // console.log("Analysis response:", data);

      // If this is a quick analysis and user is not signed in, mark as used
      if (isQuickAnalysis && !isSignedIn) {
        localStorage.setItem("hasUsedSymptomScan", "true");
        setHasUsedQuickAnalysis(true);
      }

      // Add user information to the result
      const enrichedResult = {
        ...data,
        age,
        gender,
        height,
        weight,
        medicalHistory,
        medicalHistoryText,
        exerciseFrequency,
        sleepQuality,
        stressLevel,
        dietPreference,
        recentLifeChanges,
        allergies,
        currentMedications,
      };

      setResult(enrichedResult);

      // Move to the results step
      setStep(4);
    } catch (error) {
      // console.error("Analysis failed:", error);
      if (error instanceof Error) {
        alert(`Failed to analyze symptoms. Please try again. ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const resetDemo = () => {
    setStep(1);
    setSelectedSymptoms([]);
    setAge("");
    setGender("");
    setMedicalHistory([]);
    setMedicalHistoryText("");
    setHeight("");
    setWeight("");
    setExerciseFrequency("moderate");
    setSleepQuality("fair");
    setStressLevel("moderate");
    setDietPreference("balanced");
    setRecentLifeChanges("");
    setAllergies("");
    setCurrentMedications("");
    setResult(null);
    setShowConfetti(false);
  };

  const handleNextStep = () => {
    // Log the current step for debugging
    console.log("Moving from step", step, "to", step + 1);
    if (step < 4) {
      setStep(step + 1);
    }
  };

  const handlePrevStep = () => {
    // Log the current step for debugging
    console.log("Moving from step", step, "to", step - 1);
    if (step > 1) {
      setStep(step - 1);
    }
  };

  // This ensures the result and loading state synchronize with step 4
  useEffect(() => {
    if (step === 4 && !isLoading && !result) {
      // If we're on step 4 but have no result and aren't loading, go back to step 3
      setStep(3);
    }
  }, [step, isLoading, result]);

  return (
    <Card className="w-full shadow-lg border-primary/10 mt-0 pt-0">
      <CardHeader className="bg-primary/5 border-b rounded-t-2xl">
        <div className="flex items-center justify-between pt-6 ">
          <div>
            <CardTitle className="text-primary flex items-center gap-2 text-2xl ">
              {isPro ? (
                <>
                  <Stethoscope className="h-6 w-6 text-primary" />
                  SymptomScan Pro
                </>
              ) : (
                <>
                  <Activity className="h-6 w-6 text-primary" />
                  SymptomScan
                </>
              )}
            </CardTitle>
            <CardDescription>
              {isPro
                ? "Our comprehensive AI-powered health analysis tool. Get detailed insights and personalized recommendations."
                : "Quick AI-powered symptom checker. Get a basic assessment of your symptoms in seconds."}
            </CardDescription>
          </div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={resetDemo}>
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Start Over</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <div className="p-4 border-b bg-muted/10">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Progress</span>
            <span className="text-xs text-muted-foreground">
              Step {step} of 4
            </span>
          </div>
          <span className="text-sm font-medium">{progress}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>
      <AnimatePresence mode="wait">
        <motion.div
          key={`step-${step}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
        >
          <CardContent className="p-6">
            {step === 1 && (
              <>
                <h2 className="text-xl font-semibold mb-4">
                  Select Your Symptoms
                </h2>
                <SymptomSelector
                  bodyAreas={bodyAreas}
                  selectedSymptoms={selectedSymptoms}
                  setSelectedSymptoms={setSelectedSymptoms}
                />
              </>
            )}

            {step === 2 && (
              <>
                <h2 className="text-xl font-semibold mb-4">
                  Personal Information
                </h2>
                <PersonalInfo
                  age={age}
                  setAge={setAge}
                  gender={gender}
                  setGender={setGender}
                  medicalHistory={medicalHistory}
                  setMedicalHistory={setMedicalHistory}
                  medicalHistoryText={medicalHistoryText}
                  setMedicalHistoryText={setMedicalHistoryText}
                  height={height}
                  setHeight={setHeight}
                  weight={weight}
                  setWeight={setWeight}
                />
              </>
            )}

            {step === 3 && (
              <>
                <h2 className="text-xl font-semibold mb-4">
                  Additional Information
                </h2>
                <AdditionalInfo
                  exerciseFrequency={exerciseFrequency}
                  setExerciseFrequency={setExerciseFrequency}
                  sleepQuality={sleepQuality}
                  setSleepQuality={setSleepQuality}
                  stressLevel={stressLevel}
                  setStressLevel={setStressLevel}
                  dietPreference={dietPreference}
                  setDietPreference={setDietPreference}
                  recentLifeChanges={recentLifeChanges}
                  setRecentLifeChanges={setRecentLifeChanges}
                  allergies={allergies}
                  setAllergies={setAllergies}
                  currentMedications={currentMedications}
                  setCurrentMedications={setCurrentMedications}
                />
              </>
            )}

            {step === 4 && (
              <>
                <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
                {isLoading ? (
                  <LoadingAnalysis />
                ) : (
                  result && (
                    <AnalysisResultComponent
                      result={result}
                      selectedSymptoms={selectedSymptoms}
                    />
                  )
                )}
              </>
            )}
          </CardContent>
        </motion.div>
      </AnimatePresence>
      <CardFooter className="border-t bg-muted/20 flex justify-between p-4">
        {step < 4 ? (
          <>
            <Button
              variant="outline"
              onClick={handlePrevStep}
              disabled={step === 1}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
            {step < 3 ? (
              <Button
                onClick={handleNextStep}
                disabled={
                  (step === 1 && selectedSymptoms.length === 0) ||
                  (step === 2 && (!age || !gender))
                }
                className="gap-2"
              >
                Next
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={(e) => {
                  // console.log("Analyze Symptoms button clicked");
                  handleSubmit(e);
                }}
                disabled={isLoading}
                className="gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Analyze Symptoms
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            )}
          </>
        ) : (
          <>
            <Button variant="outline" onClick={resetDemo}>
              Start New Analysis
            </Button>
            {/* <Button>
              <FileText className="mr-2 h-4 w-4" />
              Download Report
            </Button> */}
          </>
        )}
      </CardFooter>
      <ConfettiEffect trigger={showConfetti} />
    </Card>
  );
}
