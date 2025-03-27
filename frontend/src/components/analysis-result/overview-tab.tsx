"use client";

import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { AnalysisResult } from "@/types/symptom-types";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Info,
  Utensils,
  Dumbbell,
  Pill,
  Heart,
  Shield,
  Check,
  X,
} from "lucide-react";

interface OverviewTabProps {
  result: AnalysisResult;
}

export default function OverviewTab({ result }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Symptom Analysis</h3>
        <Badge
          className={`${
            result.urgency === "low"
              ? "bg-green-100 text-green-800"
              : result.urgency === "medium"
              ? "bg-yellow-100 text-yellow-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {result.urgency === "low" ? (
            <CheckCircle2 className="mr-1 h-3 w-3" />
          ) : result.urgency === "medium" ? (
            <Info className="mr-1 h-3 w-3" />
          ) : (
            <AlertTriangle className="mr-1 h-3 w-3" />
          )}
          {result.urgency.charAt(0).toUpperCase() + result.urgency.slice(1)}{" "}
          Urgency
        </Badge>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-2">
            Based on your symptoms
          </h4>
          <div className="space-y-3">
            {result.possibleConditions.map((condition, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="p-4 border rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-medium">{condition.name}</h5>
                  <Badge variant="outline">
                    {condition.probability}% Match
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {condition.description}
                </p>
                <div className="mt-2">
                  <Progress value={condition.probability} className="h-2" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="p-4 border rounded-lg bg-muted/10">
          <h4 className="font-medium mb-2">Recommendation</h4>
          <p className="text-sm">{result.recommendation}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2 flex items-center">
              <Activity className="mr-2 h-4 w-4 text-primary" />
              Follow-up Actions
            </h4>
            <ul className="space-y-2">
              {result.followUpActions.map((action, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.1 }}
                  className="flex items-start gap-2 text-sm"
                >
                  <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>{action}</span>
                </motion.li>
              ))}
            </ul>
          </div>

          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2 flex items-center">
              <AlertTriangle className="mr-2 h-4 w-4 text-primary" />
              Risk Factors
            </h4>
            <ul className="space-y-2">
              {result.riskFactors.map((factor, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.1 }}
                  className="flex items-start gap-2 text-sm"
                >
                  <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>{factor}</span>
                </motion.li>
              ))}
            </ul>
          </div>
        </div>

        {/* Meal Recommendations */}
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2 flex items-center">
            <Utensils className="mr-2 h-4 w-4 text-primary" />
            Meal Recommendations
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h5 className="text-sm font-medium mb-1">Breakfast</h5>
              <ul className="space-y-1">
                {result.mealRecommendations.breakfast.map((meal, index) => (
                  <li key={index} className="text-sm text-muted-foreground">
                    • {meal}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="text-sm font-medium mb-1">Lunch</h5>
              <ul className="space-y-1">
                {result.mealRecommendations.lunch.map((meal, index) => (
                  <li key={index} className="text-sm text-muted-foreground">
                    • {meal}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="text-sm font-medium mb-1">Dinner</h5>
              <ul className="space-y-1">
                {result.mealRecommendations.dinner.map((meal, index) => (
                  <li key={index} className="text-sm text-muted-foreground">
                    • {meal}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Exercise Plan */}
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2 flex items-center">
            <Dumbbell className="mr-2 h-4 w-4 text-primary" />
            Exercise Plan
          </h4>
          <ul className="space-y-2">
            {result.exercisePlan.map((exercise, index) => (
              <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span>{exercise}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Diseases and Preventive Measures */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2 flex items-center">
              <Heart className="mr-2 h-4 w-4 text-primary" />
              Possible Diseases
            </h4>
            <ul className="space-y-2">
              {result.diseases.map((disease, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>{disease}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2 flex items-center">
              <Shield className="mr-2 h-4 w-4 text-primary" />
              Preventive Measures
            </h4>
            <ul className="space-y-2">
              {result.preventiveMeasures.map((measure, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>{measure}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Medicine Recommendations */}
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2 flex items-center">
            <Pill className="mr-2 h-4 w-4 text-primary" />
            Medicine Recommendations
          </h4>
          <ul className="space-y-2">
            {result.medicineRecommendations.map((medicine, index) => (
              <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span>{medicine}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Do's and Don'ts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2 flex items-center">
              <Check className="mr-2 h-4 w-4 text-primary" />
              Do's
            </h4>
            <ul className="space-y-2">
              {result.dos.map((do_item, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{do_item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2 flex items-center">
              <X className="mr-2 h-4 w-4 text-primary" />
              Don'ts
            </h4>
            <ul className="space-y-2">
              {result.donts.map((dont, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <X className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>{dont}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
