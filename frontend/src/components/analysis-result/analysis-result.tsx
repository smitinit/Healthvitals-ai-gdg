"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Info } from "lucide-react";
import type { AnalysisResult, Symptom } from "@/types/symptom-types";
import OverviewTab from "./overview-tab";
import DetailsTab from "./details-tab";
import DoctorsTab from "./doctors-tab";
import ResourcesTab from "./resources-tab";
import { useState } from "react";

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
    </div>
  );
}
