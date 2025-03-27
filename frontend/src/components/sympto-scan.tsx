import type React from "react";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ArrowRight, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";

const API_BASE_URL = 'http://localhost:5000/api';

export default function SymptomScanDemo() {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [symptoms, setSymptoms] = useState("");
  const [age, setAge] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<null | {
    possibleConditions: string[];
    recommendation: string;
    urgency: "low" | "medium" | "high";
  }>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      console.log("Sending API request with:", {
        symptoms,
        age
      });

      const response = await fetch(`${API_BASE_URL}/quick-analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symptoms,
          age
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API response not OK:', response.status, errorText);
        throw new Error(`Failed to analyze symptoms: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log("API response received:", data);
      
      setResult({
        possibleConditions: data.possibleConditions || [],
        recommendation: data.recommendation || "No specific recommendation available. Please consult a healthcare professional.",
        urgency: data.urgency || "medium",
      });
      
      setStep(2);
    } catch (error) {
      console.error('Error analyzing symptoms:', error);
      setError("There was an error analyzing your symptoms. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetDemo = () => {
    setStep(1);
    setSymptoms("");
    setAge("");
    setError("");
    setResult(null);
  };

  return (
    <Card className="w-full shadow-lg border-primary/10 mt-0 pt-0">
      <CardHeader className="bg-primary/5 border-b rounded-t-2xl pt-6">
        <CardTitle className="text-primary">SymptomScan</CardTitle>
        <CardDescription>
          Enter your symptoms to get an instant analysis
        </CardDescription>
      </CardHeader>

      <AnimatePresence mode="wait">
        {step === 1 ? (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <CardContent className="pt-2 pb-6">
              <form onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="symptoms"
                      className="block text-sm font-medium mb-1"
                    >
                      Describe your symptoms
                    </label>
                    <Textarea
                      id="symptoms"
                      placeholder="E.g., I've had a runny nose, sore throat, and mild fever for the past 2 days..."
                      value={symptoms}
                      onChange={(e) => setSymptoms(e.target.value)}
                      className="min-h-[120px]"
                      required
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="age"
                      className="block text-sm font-medium mb-1"
                    >
                      Age
                    </label>
                    <Input
                      id="age"
                      type="number"
                      placeholder="Enter your age"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      required
                    />
                  </div>

                  {error && (
                    <div className="text-sm text-red-500 mt-2">
                      {error}
                    </div>
                  )}
                </div>
              </form>
            </CardContent>

            <CardFooter className="border-t bg-muted/20 flex justify-end">
              <Button
                onClick={handleSubmit}
                disabled={!symptoms.trim() || !age.trim() || isLoading}
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
            </CardFooter>
          </motion.div>
        ) : (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <CardContent className="pt-2 pb-6">
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Based on your symptoms
                  </h4>
                  <h3 className="text-lg font-semibold mt-1">
                    Possible Conditions
                  </h3>
                  <ul className="mt-2 space-y-2">
                    {result?.possibleConditions.map((condition, index) => (
                      <motion.li
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        className="flex items-center gap-2 text-sm"
                      >
                        <div className="h-2 w-2 rounded-full bg-primary" />
                        {condition}
                      </motion.li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold">Recommendation</h3>
                  <p className="mt-2 text-sm">{result?.recommendation}</p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold">Urgency Level</h3>
                  <div className="mt-2 flex items-center gap-2">
                    <div
                      className={`h-3 w-3 rounded-full ${
                        result?.urgency === "low"
                          ? "bg-green-500"
                          : result?.urgency === "medium"
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                    />
                    <span className="text-sm capitalize">
                      {result?.urgency}
                    </span>
                  </div>
                </div>

                <div className="pt-2 text-sm text-muted-foreground">
                  <p>
                    <strong>Note:</strong> This is a preliminary analysis. 
                    For a comprehensive assessment, please use the full 
                    SymptomScan feature. Always consult with a healthcare 
                    professional for medical advice.
                  </p>
                </div>
              </div>
            </CardContent>

            <CardFooter className="border-t bg-muted/20 flex justify-between">
              <Button variant="outline" onClick={resetDemo}>
                Try Again
              </Button>
              <Link to="/symptom-scanner">
                <Button>Get Detailed Report</Button>
              </Link>
            </CardFooter>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}
