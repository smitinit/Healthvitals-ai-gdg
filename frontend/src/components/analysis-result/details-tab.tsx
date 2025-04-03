import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import type { AnalysisResult, Symptom } from "@/types/symptom-types";
import {
  Pill,
  Stethoscope,
  Thermometer,
  ActivitySquare,
  Utensils,
  Dumbbell,
  Shield,
  FileSpreadsheet,
  ClipboardList,
  Leaf,
  FileDown,
} from "lucide-react";
import API_BASE_URL from "@/config";

interface DetailsTabProps {
  result: AnalysisResult;
  selectedSymptoms: Symptom[];
}

export default function DetailsTab({
  result,
}: // selectedSymptoms,
DetailsTabProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  // Function to get recommended actions specific to a condition
  const getConditionActions = (conditionName: string) => {
    // Check if there are condition-specific actions in the result
    if (
      result.conditionSpecificData &&
      result.conditionSpecificData[conditionName] &&
      result.conditionSpecificData[conditionName].recommendedActions
    ) {
      return result.conditionSpecificData[
        conditionName
      ].recommendedActions.slice(0, 3);
    }

    // Fall back to general actions if no condition-specific actions found
    return result.followUpActions.slice(0, 3);
  };

  // Function to get preventive measures specific to a condition
  const getConditionPreventiveMeasures = (conditionName: string) => {
    // Check if there are condition-specific preventive measures in the result
    if (
      result.conditionSpecificData &&
      result.conditionSpecificData[conditionName] &&
      result.conditionSpecificData[conditionName].preventiveMeasures
    ) {
      return result.conditionSpecificData[
        conditionName
      ].preventiveMeasures.slice(0, 3);
    }

    // Fall back to general preventive measures if no condition-specific measures found
    return result.preventiveMeasures.slice(0, 3);
  };

  // Display meal recommendations with diet note
  const displayMealRecommendations = () => {
    return (
      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-lg mb-2">Breakfast</h4>
          <ul className="list-disc pl-5 space-y-1">
            {result.mealRecommendations.breakfast
              .slice(0, 3)
              .map((meal, index) => (
                <li key={index} className="text-gray-700">
                  {meal}
                </li>
              ))}
          </ul>
        </div>

        <div>
          <h4 className="font-medium text-lg mb-2">Lunch</h4>
          <ul className="list-disc pl-5 space-y-1">
            {result.mealRecommendations.lunch.slice(0, 3).map((meal, index) => (
              <li key={index} className="text-gray-700">
                {meal}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="font-medium text-lg mb-2">Dinner</h4>
          <ul className="list-disc pl-5 space-y-1">
            {result.mealRecommendations.dinner
              .slice(0, 3)
              .map((meal, index) => (
                <li key={index} className="text-gray-700">
                  {meal}
                </li>
              ))}
          </ul>
        </div>

        {result.mealRecommendations.note && (
          <div className="mt-4 italic text-gray-600">
            {result.mealRecommendations.note}
          </div>
        )}
      </div>
    );
  };

  const handleDownloadPDF = async () => {
    try {
      setIsDownloading(true);

      // Make API request to generate PDF
      const response = await fetch(
        `${API_BASE_URL}/api/public/generate-details-pdf`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(result),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }

      // Download the PDF file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "healthvitals-detailed-report.pdf";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Error downloading PDF:", error);
      alert("Failed to download PDF report. Please try again later.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {result.possibleConditions.slice(0, 3).map((condition, index) => (
          <Accordion
            key={index}
            type="single"
            collapsible
            className="border rounded-lg"
          >
            <AccordionItem value={`condition-${index}`} className="border-none">
              <AccordionTrigger className="px-4 py-3 hover:no-underline">
                <div className="flex items-center gap-2">
                  {condition.category === "respiratory" ? (
                    <Stethoscope className="h-4 w-4 text-primary" />
                  ) : condition.category === "digestive" ? (
                    <Pill className="h-4 w-4 text-primary" />
                  ) : (
                    <Thermometer className="h-4 w-4 text-primary" />
                  )}
                  <span>{condition.name}</span>
                  <Badge variant="outline" className="ml-2 text-xs">
                    {condition.probability}% Match
                  </Badge>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium">Description</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {condition.description}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium">Related Information</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                      <div className="p-3 border rounded-md">
                        <h5 className="text-xs font-semibold text-primary mb-2 flex items-center">
                          <ActivitySquare className="h-3 w-3 mr-1" />{" "}
                          Recommended Actions
                        </h5>
                        <ul className="space-y-1">
                          {getConditionActions(condition.name).map(
                            (action, i) => (
                              <li
                                key={i}
                                className="text-xs text-muted-foreground flex items-start gap-1"
                              >
                                <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                                <span>{action}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>

                      <div className="p-3 border rounded-md">
                        <h5 className="text-xs font-semibold text-primary mb-2 flex items-center">
                          <Shield className="h-3 w-3 mr-1" /> Preventive
                          Measures
                        </h5>
                        <ul className="space-y-1">
                          {getConditionPreventiveMeasures(condition.name).map(
                            (measure, i) => (
                              <li
                                key={i}
                                className="text-xs text-muted-foreground flex items-start gap-1"
                              >
                                <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                                <span>{measure}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        ))}
      </div>

      <div className="space-y-4">
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-3 flex items-center">
            <Utensils className="h-4 w-4 text-primary mr-2" />
            Diet Recommendations
          </h3>
          {displayMealRecommendations()}
        </div>

        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-3 flex items-center">
            <Dumbbell className="h-4 w-4 text-primary mr-2" />
            Exercise Plan
          </h3>
          <ul className="space-y-2">
            {result.exercisePlan.slice(0, 3).map((exercise, i) => (
              <li
                key={i}
                className="text-sm text-muted-foreground flex items-start gap-2"
              >
                <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                <span>{exercise}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Ayurvedic Medication Section */}
        {result.ayurvedicMedication && (
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium mb-3 flex items-center">
              <Leaf className="h-4 w-4 text-primary mr-2" />
              Ayurvedic Medication
            </h3>
            <div className="space-y-6">
              {result.ayurvedicMedication.recommendations
                .slice(0, 3)
                .map((recommendation, index) => (
                  <Accordion
                    key={index}
                    type="single"
                    collapsible
                    className="border rounded-lg"
                  >
                    <AccordionItem
                      value={`ayurvedic-${index}`}
                      className="border-none"
                    >
                      <AccordionTrigger className="px-4 py-3 hover:no-underline">
                        <div className="flex items-center gap-2">
                          <Leaf className="h-4 w-4 text-primary" />
                          <span>{recommendation.name}</span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-4 pb-4">
                        <div className="space-y-4">
                          <div>
                            <h4 className="text-sm font-medium text-primary">
                              Description
                            </h4>
                            <p className="text-sm text-muted-foreground mt-1">
                              {recommendation.description}
                            </p>
                          </div>

                          <div>
                            <h4 className="text-sm font-medium text-primary">
                              Why It's Important
                            </h4>
                            <p className="text-sm text-muted-foreground mt-1">
                              {recommendation.importance}
                            </p>
                          </div>

                          <div>
                            <h4 className="text-sm font-medium text-primary">
                              Benefits
                            </h4>
                            <p className="text-sm text-muted-foreground mt-1">
                              {recommendation.benefits}
                            </p>
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                ))}
            </div>
          </div>
        )}

        {/* Reports Required Section */}
        {result.reportsRequired && result.reportsRequired.length > 0 && (
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium mb-3 flex items-center">
              <FileSpreadsheet className="h-4 w-4 text-primary mr-2" />
              Reports Required
            </h3>
            <div className="space-y-4">
              {result.reportsRequired.slice(0, 3).map((report, i) => (
                <Accordion
                  key={i}
                  type="single"
                  collapsible
                  className="border rounded-lg"
                >
                  <AccordionItem value={`report-${i}`} className="border-none">
                    <AccordionTrigger className="px-4 py-3 hover:no-underline">
                      <div className="flex items-center gap-2">
                        <ClipboardList className="h-4 w-4 text-primary" />
                        <span>{report.name}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="space-y-3">
                        {report.purpose && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">
                              Purpose
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {report.purpose}
                            </p>
                          </div>
                        )}

                        {report.benefits && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">
                              Benefits
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {report.benefits}
                            </p>
                          </div>
                        )}

                        {report.analysisDetails && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">
                              Analysis Details
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {report.analysisDetails}
                            </p>
                          </div>
                        )}

                        {report.preparationRequired && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">
                              Preparation Required
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {report.preparationRequired}
                            </p>
                          </div>
                        )}

                        <div className="space-y-1">
                          <h4 className="text-sm font-medium text-primary">
                            Recommendation Reason
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {report.recommendationReason}
                          </p>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Download Report Button */}
      <div className="flex justify-center mt-8">
        <Button
          onClick={handleDownloadPDF}
          disabled={isDownloading}
          className="w-full max-w-md"
        >
          <FileDown className="mr-2 h-4 w-4" />
          {isDownloading ? "Generating PDF..." : "Download Detailed Report"}
        </Button>
      </div>
    </div>
  );
}
