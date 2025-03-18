import { Badge } from "@/components/ui/badge"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import type { AnalysisResult, Symptom } from "@/types/symptom-types"
import { dummyConditions } from "@/data/symptom-data"
import { Pill, Stethoscope, Thermometer } from "lucide-react"

interface DetailsTabProps {
  result: AnalysisResult
  selectedSymptoms: Symptom[]
}

export default function DetailsTab({ result, selectedSymptoms }: DetailsTabProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {result.possibleConditions.map((condition, index) => {
          const conditionDetails = dummyConditions[condition.category].find((c) => c.name === condition.name)

          if (!conditionDetails) return null

          return (
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
                      <p className="text-sm text-muted-foreground mt-1">{conditionDetails.description}</p>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium">Common Symptoms</h4>
                      <ul className="mt-1 grid grid-cols-2 gap-1">
                        {conditionDetails.symptoms.map((symptom, i) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-center gap-1">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                            {symptom}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium">Treatment Options</h4>
                      <ul className="mt-1 space-y-1">
                        {conditionDetails.treatmentOptions.map((treatment, i) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-center gap-1">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                            {treatment}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium">Recovery Time</h4>
                        <p className="text-sm text-muted-foreground mt-1">{conditionDetails.recoveryTime}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium">Prevention</h4>
                        <ul className="mt-1 space-y-1">
                          {conditionDetails.preventionTips.map((tip, i) => (
                            <li key={i} className="text-sm text-muted-foreground flex items-center gap-1">
                              <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                              {tip}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          )
        })}
      </div>

      <div className="p-4 border rounded-lg">
        <h3 className="font-medium mb-3">Your Symptom Details</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
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
    </div>
  )
}

