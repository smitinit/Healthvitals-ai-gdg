"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Info, HeartPulse, Circle } from "lucide-react";
import type { AnalysisResult, Symptom } from "@/types/symptom-types";
import OverviewTab from "./overview-tab";
import DetailsTab from "./details-tab";
import DoctorsTab from "./doctors-tab";
import ResourcesTab from "./resources-tab";
import { useState } from "react";
import CircleProgress from "@/components/circle-progress";

interface AnalysisResultProps {
  result: AnalysisResult;
  selectedSymptoms: Symptom[];
}

export default function AnalysisResultComponent({
  result,
  selectedSymptoms,
}: AnalysisResultProps) {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 mb-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="doctors">Find Care</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <OverviewTab result={result} />
        </TabsContent>

        <TabsContent value="details">
          <DetailsTab result={result} selectedSymptoms={selectedSymptoms} />
        </TabsContent>

        <TabsContent value="doctors">
          <DoctorsTab />
        </TabsContent>

        <TabsContent value="resources">
          <ResourcesTab />
        </TabsContent>
      </Tabs>

      <div className="text-sm text-muted-foreground bg-muted/20 p-4 rounded-lg">
        <p className="flex items-center gap-1">
          <Info className="h-4 w-4" />
          <span>
            <strong>Disclaimer:</strong> This analysis is for informational
            purposes only and does not constitute medical advice. Always consult
            with a qualified healthcare provider for diagnosis and treatment.
          </span>
        </p>
      </div>

      {/* Health Score */}
      {result.healthScore !== undefined && (
        <div className="mt-6 p-4 border rounded-lg">
          <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <HeartPulse className="h-5 w-5 text-primary" />
            Health Score
          </h2>
          <div className="flex items-center gap-4">
            <div className="relative h-16 w-16 flex items-center justify-center">
              <Circle className="h-16 w-16 absolute text-muted-foreground/20" strokeWidth={1} />
              <CircleProgress 
                value={result.healthScore} 
                max={10}
                className="h-16 w-16 absolute text-primary" 
                strokeWidth={4}
              />
              <span className="text-2xl font-bold relative z-10">
                {result.healthScore}
              </span>
            </div>
            <div className="flex-1">
              <span className="text-sm font-medium">
                {result.healthScore >= 8 
                  ? "Your health score is very good!" 
                  : result.healthScore >= 6 
                  ? "Your health score is good, with some areas for improvement." 
                  : result.healthScore >= 4 
                  ? "Your health score indicates medical attention may be needed." 
                  : "Your health score suggests urgent medical attention is recommended."}
              </span>
              <div className="w-full bg-muted mt-2 h-2 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    result.healthScore >= 8 
                      ? "bg-green-500" 
                      : result.healthScore >= 6 
                      ? "bg-yellow-500" 
                      : result.healthScore >= 4 
                      ? "bg-orange-500" 
                      : "bg-red-500"
                  }`}
                  style={{ width: `${(result.healthScore / 10) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
