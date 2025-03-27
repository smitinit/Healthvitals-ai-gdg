import { Badge } from "@/components/ui/badge"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import type { AnalysisResult, Symptom } from "@/types/symptom-types"
import { Pill, Stethoscope, Thermometer, ActivitySquare, Utensils, Dumbbell, Heart, Shield, Check, X, FileSpreadsheet, ClipboardList, Leaf } from "lucide-react"

interface DetailsTabProps {
  result: AnalysisResult
  selectedSymptoms: Symptom[]
}

export default function DetailsTab({ result, selectedSymptoms }: DetailsTabProps) {
  // Function to get recommended actions specific to a condition
  const getConditionActions = (conditionName: string) => {
    // Check if there are condition-specific actions in the result
    if (result.conditionSpecificData && 
        result.conditionSpecificData[conditionName] && 
        result.conditionSpecificData[conditionName].recommendedActions) {
      return result.conditionSpecificData[conditionName].recommendedActions;
    }
    
    // Fall back to general actions if no condition-specific actions found
    return result.followUpActions.slice(0, 3);
  };
  
  // Function to get preventive measures specific to a condition
  const getConditionPreventiveMeasures = (conditionName: string) => {
    // Check if there are condition-specific preventive measures in the result
    if (result.conditionSpecificData && 
        result.conditionSpecificData[conditionName] && 
        result.conditionSpecificData[conditionName].preventiveMeasures) {
      return result.conditionSpecificData[conditionName].preventiveMeasures;
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
            {result.mealRecommendations.breakfast.map((meal, index) => (
              <li key={index} className="text-gray-700">{meal}</li>
            ))}
          </ul>
        </div>
        
        <div>
          <h4 className="font-medium text-lg mb-2">Lunch</h4>
          <ul className="list-disc pl-5 space-y-1">
            {result.mealRecommendations.lunch.map((meal, index) => (
              <li key={index} className="text-gray-700">{meal}</li>
            ))}
          </ul>
        </div>
        
        <div>
          <h4 className="font-medium text-lg mb-2">Dinner</h4>
          <ul className="list-disc pl-5 space-y-1">
            {result.mealRecommendations.dinner.map((meal, index) => (
              <li key={index} className="text-gray-700">{meal}</li>
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

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {result.possibleConditions.map((condition, index) => (
          <Accordion key={index} type="single" collapsible className="border rounded-lg">
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
                    <p className="text-sm text-muted-foreground mt-1">{condition.description}</p>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium">Related Information</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                      <div className="p-3 border rounded-md">
                        <h5 className="text-xs font-semibold text-primary mb-2 flex items-center">
                          <ActivitySquare className="h-3 w-3 mr-1" /> Recommended Actions
                        </h5>
                        <ul className="space-y-1">
                          {getConditionActions(condition.name).map((action, i) => (
                            <li key={i} className="text-xs text-muted-foreground flex items-start gap-1">
                              <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                              <span>{action}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="p-3 border rounded-md">
                        <h5 className="text-xs font-semibold text-primary mb-2 flex items-center">
                          <Shield className="h-3 w-3 mr-1" /> Preventive Measures
                        </h5>
                        <ul className="space-y-1">
                          {getConditionPreventiveMeasures(condition.name).map((measure, i) => (
                            <li key={i} className="text-xs text-muted-foreground flex items-start gap-1">
                              <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                              <span>{measure}</span>
                            </li>
                          ))}
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

      <div className="p-4 border rounded-lg mb-4">
        <h3 className="font-medium mb-3">Your Symptom Details</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {selectedSymptoms.map((symptom) => (
              <div key={symptom.id} className="p-3 border rounded-md bg-muted/10">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm">{symptom.name}</span>
                  <Badge
                    variant="outline"
                    className={`${
                      symptom.severity >= 8
                        ? "text-red-600"
                        : symptom.severity >= 5
                          ? "text-yellow-600"
                          : "text-green-600"
                    }`}
                  >
                    {symptom.severity}/10
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">Duration: {symptom.duration}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="p-4 border rounded-lg">
          <h3 className="font-medium mb-3 flex items-center">
            <Heart className="h-4 w-4 text-primary mr-2" />
            Possible Diseases
          </h3>
          <ul className="space-y-2">
            {result.diseases.map((disease, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                <span>{disease}</span>
              </li>
            ))}
          </ul>
        </div>

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
            {result.exercisePlan.map((exercise, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
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
              {result.ayurvedicMedication.recommendations.map((recommendation, index) => (
                <Accordion key={index} type="single" collapsible className="border rounded-lg">
                  <AccordionItem value={`ayurvedic-${index}`} className="border-none">
                    <AccordionTrigger className="px-4 py-3 hover:no-underline">
                      <div className="flex items-center gap-2">
                        <Leaf className="h-4 w-4 text-primary" />
                        <span>{recommendation.name}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-sm font-medium text-primary">Description</h4>
                          <p className="text-sm text-muted-foreground mt-1">{recommendation.description}</p>
                        </div>

                        <div>
                          <h4 className="text-sm font-medium text-primary">Why It's Important</h4>
                          <p className="text-sm text-muted-foreground mt-1">{recommendation.importance}</p>
                        </div>

                        <div>
                          <h4 className="text-sm font-medium text-primary">Benefits</h4>
                          <p className="text-sm text-muted-foreground mt-1">{recommendation.benefits}</p>
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
              {result.reportsRequired.map((report, i) => (
                <Accordion key={i} type="single" collapsible className="border rounded-lg">
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
                            <h4 className="text-sm font-medium text-primary">Purpose</h4>
                            <p className="text-sm text-muted-foreground">{report.purpose}</p>
                          </div>
                        )}
                        
                        {report.benefits && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">Benefits</h4>
                            <p className="text-sm text-muted-foreground">{report.benefits}</p>
                          </div>
                        )}
                        
                        {report.analysisDetails && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">Analysis Details</h4>
                            <p className="text-sm text-muted-foreground">{report.analysisDetails}</p>
                          </div>
                        )}
                        
                        {report.preparationRequired && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium text-primary">Preparation Required</h4>
                            <p className="text-sm text-muted-foreground">{report.preparationRequired}</p>
                          </div>
                        )}
                        
                        <div className="space-y-1">
                          <h4 className="text-sm font-medium text-primary">Recommendation Reason</h4>
                          <p className="text-sm text-muted-foreground">{report.recommendationReason}</p>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium mb-3 flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              Do's
            </h3>
            <ul className="space-y-2">
              {result.dos.map((doItem, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{doItem}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 border rounded-lg">
            <h3 className="font-medium mb-3 flex items-center">
              <X className="h-4 w-4 text-red-500 mr-2" />
              Don'ts
            </h3>
            <ul className="space-y-2">
              {result.donts.map((dontItem, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <X className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>{dontItem}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

