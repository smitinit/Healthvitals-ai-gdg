import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FileUp, Upload, Trash2, FileText, Image, FilePlus, Loader2, Search, 
  HeartPulse, Utensils, Dumbbell, Shield, AlertTriangle, Check, X, Pill, 
  Activity, Leaf, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import type { AnalysisResult, Symptom } from "@/types/symptom-types";
import { Separator } from "@/components/ui/separator";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import CircleProgress from "@/components/circle-progress";

interface ReportAnalysisTabProps {
  result: AnalysisResult;
  selectedSymptoms: Symptom[];
}

export default function ReportAnalysisTab({ result, selectedSymptoms }: ReportAnalysisTabProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [reportInsights, setReportInsights] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyzeReports = async () => {
    if (files.length === 0) {
      setErrorMessage("Please upload at least one report to analyze");
      return;
    }

    // Check file sizes
    const maxFileSize = 10 * 1024 * 1024; // 10MB
    const oversizedFiles = files.filter(file => file.size > maxFileSize);
    if (oversizedFiles.length > 0) {
      setErrorMessage(`Some files exceed the 10MB limit: ${oversizedFiles.map(f => f.name).join(", ")}`);
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      // Create a FormData object to send files
      const formData = new FormData();
      
      // Add all the files
      files.forEach((file, index) => {
        formData.append(`reports`, file);
      });
      
      // Add analysis result and symptoms for context
      formData.append('analysisResult', JSON.stringify(result));
      formData.append('selectedSymptoms', JSON.stringify(selectedSymptoms));

      // Send the files to the server for analysis
      const response = await fetch('/api/analyze-reports', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        if (errorData && errorData.error) {
          throw new Error(errorData.error);
        } else {
          throw new Error(`Server error (${response.status}): Failed to analyze reports`);
        }
      }

      const data = await response.json();
      console.log("Report analysis response:", data);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setReportInsights(data);
      setAnalysisComplete(true);
    } catch (error) {
      console.error('Error analyzing reports:', error);
      setErrorMessage(error.message || 'Failed to analyze reports. Please try again later.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getFileIcon = (file: File) => {
    const fileType = file.type.split('/')[0];
    if (fileType === 'image') return <Image className="h-5 w-5 text-blue-500" />;
    if (file.type === 'application/pdf') return <FileText className="h-5 w-5 text-red-500" />;
    return <FilePlus className="h-5 w-5 text-green-500" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Report Analysis</h3>
        <Badge className="bg-blue-100 text-blue-800">Enhanced Analysis</Badge>
      </div>

      {/* User Information Summary */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-md">Your Information Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Patient Profile */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Patient Profile</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Age:</span>
                  <span>{result.age || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Gender:</span>
                  <span>{result.gender || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Height:</span>
                  <span>{result.height || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Weight:</span>
                  <span>{result.weight || 'Not provided'}</span>
                </div>
              </div>
            </div>

            {/* Lifestyle Factors */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Lifestyle Factors</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Exercise:</span>
                  <span>{result.exerciseFrequency || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sleep Quality:</span>
                  <span>{result.sleepQuality || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Stress Level:</span>
                  <span>{result.stressLevel || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Diet Preference:</span>
                  <span>{result.dietPreference || 'Not provided'}</span>
                </div>
              </div>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Reported Symptoms */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Reported Symptoms</h4>
            <div className="space-y-2">
              {selectedSymptoms.map((symptom, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm">{symptom.name}</span>
                  <Badge variant="outline">
                    Severity: {symptom.severity}/10 • Duration: {symptom.duration}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          <Separator className="my-4" />

          {/* Medical History */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Medical History</h4>
            {result.medicalHistory && result.medicalHistory.length > 0 ? (
              <ul className="space-y-1">
                {result.medicalHistory.map((condition, index) => (
                  <li key={index} className="text-sm flex items-start gap-2">
                    <span className="text-primary">•</span>
                    <span className="text-muted-foreground">{condition}</span>
                  </li>
                ))}
              </ul>
            ) : result.medicalHistoryText ? (
              <p className="text-sm text-muted-foreground">{result.medicalHistoryText}</p>
            ) : (
              <p className="text-sm text-muted-foreground">No medical history reported</p>
            )}
          </div>
          
          {result.recentLifeChanges && (
            <>
              <Separator className="my-4" />
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Recent Life Changes</h4>
                <p className="text-sm text-muted-foreground">{result.recentLifeChanges}</p>
              </div>
            </>
          )}
          
          {result.allergies && (
            <>
              <Separator className="my-4" />
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Allergies</h4>
                <p className="text-sm text-muted-foreground">{result.allergies}</p>
              </div>
            </>
          )}
          
          {result.currentMedications && (
            <>
              <Separator className="my-4" />
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Current Medications</h4>
                <p className="text-sm text-muted-foreground">{result.currentMedications}</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Report Upload Section */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-md">Upload Medical Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Upload your medical reports, X-rays, or doctor prescriptions for a more personalized analysis. Supported file types: PDF, JPG, PNG.
            </p>
            
            <div className="border-2 border-dashed rounded-lg p-6 text-center">
              <FileUp className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm font-medium mb-2">
                Drag and drop your files here, or click to browse
              </p>
              <p className="text-xs text-muted-foreground mb-4">
                Max 10MB per file • Up to 10 files • PDF, JPG, PNG formats recommended
              </p>
              <Button
                variant="outline"
                size="sm"
                className="relative overflow-hidden"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                <Upload className="h-4 w-4 mr-2" />
                Browse Files
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png,.bmp,.gif,.tiff,.webp,.doc,.docx,.txt,.rtf"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  onChange={handleFileChange}
                  aria-label="Upload medical reports"
                />
              </Button>
            </div>

            {/* Display selected files */}
            {files.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Selected Files ({files.length})</h4>
                <div className="max-h-60 overflow-y-auto">
                  {files.map((file, index) => (
                    <div 
                      key={index} 
                      className="flex items-center justify-between p-2 border rounded-md mb-2"
                    >
                      <div className="flex items-center">
                        {getFileIcon(file)}
                        <span className="ml-2 text-sm truncate max-w-[200px]">
                          {file.name}
                        </span>
                        <span className="ml-2 text-xs text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => removeFile(index)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {errorMessage && (
              <Alert variant="destructive">
                <AlertTitle className="flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Error
                </AlertTitle>
                <AlertDescription className="mt-2">{errorMessage}</AlertDescription>
                <div className="mt-2 text-xs">
                  {errorMessage.includes('Failed to analyze') && (
                    <span>Try uploading a different file format (PDF recommended) or check your internet connection.</span>
                  )}
                </div>
              </Alert>
            )}

            <Button 
              className="w-full" 
              disabled={files.length === 0 || isAnalyzing}
              onClick={handleAnalyzeReports}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing Reports...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Analyze Reports
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Comprehensive Analysis Results Section - Shown after analysis is complete */}
      {analysisComplete && reportInsights && (
        <div className="space-y-6">
          {/* Primary Recommendation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-primary" />
                Primary Recommendation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-line">{reportInsights.recommendation}</p>
            </CardContent>
          </Card>

          {/* Health Score - Now shown only after report analysis */}
          {reportInsights.healthScore !== undefined && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HeartPulse className="h-5 w-5 text-primary" />
                  Health Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div className="relative h-16 w-16 flex items-center justify-center">
                    <CircleProgress 
                      value={reportInsights.healthScore} 
                      max={10}
                      className="h-16 w-16 absolute text-primary" 
                      strokeWidth={4}
                    />
                    <span className="text-2xl font-bold relative z-10">
                      {reportInsights.healthScore}
                    </span>
                  </div>
                  <div className="flex-1">
                    <span className="text-sm">
                      {reportInsights.healthScore >= 8 
                        ? "Your health score is very good!" 
                        : reportInsights.healthScore >= 6 
                        ? "Your health score is good, with some areas for improvement." 
                        : reportInsights.healthScore >= 4 
                        ? "Your health score indicates medical attention may be needed." 
                        : "Your health score suggests urgent medical attention is recommended."}
                    </span>
                    <div className="w-full bg-muted mt-2 h-2 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${
                          reportInsights.healthScore >= 8 
                            ? "bg-green-500" 
                            : reportInsights.healthScore >= 6 
                            ? "bg-yellow-500" 
                            : reportInsights.healthScore >= 4 
                            ? "bg-orange-500" 
                            : "bg-red-500"
                        }`}
                        style={{ width: `${(reportInsights.healthScore / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Key Findings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Key Findings from Reports
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {reportInsights.keyFindings.map((finding: string, index: number) => (
                <div key={index} className="p-3 border rounded-md bg-muted/10">
                  <p className="text-sm">{finding}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Possible Conditions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Possible Conditions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reportInsights.possibleConditions.map((condition: any, index: number) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{condition.name}</h4>
                      <Badge variant="outline">{condition.probability}% Match</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{condition.description}</p>
                    <div className="mt-2">
                      <div className="w-full bg-muted h-2 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary rounded-full"
                          style={{ width: `${condition.probability}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Follow-up Actions & Risk Factors */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Follow-up Actions */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-md flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-primary" />
                  Follow-up Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {reportInsights.followUpActions.map((action: string, index: number) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Risk Factors */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-md flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-primary" />
                  Risk Factors
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {reportInsights.riskFactors.map((risk: string, index: number) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{risk}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Meal Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-5 w-5 text-primary" />
                Meal Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Breakfast */}
                <div>
                  <h4 className="font-medium mb-2 text-sm">Breakfast</h4>
                  <ul className="space-y-1">
                    {reportInsights.mealRecommendations.breakfast.map((item: string, i: number) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-primary">•</span>
                        <span className="text-muted-foreground">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Lunch */}
                <div>
                  <h4 className="font-medium mb-2 text-sm">Lunch</h4>
                  <ul className="space-y-1">
                    {reportInsights.mealRecommendations.lunch.map((item: string, i: number) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-primary">•</span>
                        <span className="text-muted-foreground">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Dinner */}
                <div>
                  <h4 className="font-medium mb-2 text-sm">Dinner</h4>
                  <ul className="space-y-1">
                    {reportInsights.mealRecommendations.dinner.map((item: string, i: number) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-primary">•</span>
                        <span className="text-muted-foreground">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Note */}
                {reportInsights.mealRecommendations.note && (
                  <p className="text-sm italic text-muted-foreground">
                    Note: {reportInsights.mealRecommendations.note}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Exercise Plan & Preventive Measures */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Exercise Plan */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-md flex items-center gap-2">
                  <Dumbbell className="h-4 w-4 text-primary" />
                  Exercise Plan
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {reportInsights.exercisePlan.map((exercise: string, index: number) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{exercise}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Preventive Measures */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-md flex items-center gap-2">
                  <Shield className="h-4 w-4 text-primary" />
                  Preventive Measures
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {reportInsights.preventiveMeasures.map((measure: string, index: number) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{measure}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Do's and Don'ts */}
          <Card>
            <CardHeader>
              <CardTitle>Do's and Don'ts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Do's */}
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center">
                    <Check className="mr-2 h-4 w-4 text-green-500" />
                    Do's
                  </h4>
                  <ul className="space-y-2">
                    {reportInsights.dos.map((item: string, index: number) => (
                      <li key={index} className="text-sm flex items-start gap-2">
                        <span className="text-green-500">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Don'ts */}
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center">
                    <X className="mr-2 h-4 w-4 text-red-500" />
                    Don'ts
                  </h4>
                  <ul className="space-y-2">
                    {reportInsights.donts.map((item: string, index: number) => (
                      <li key={index} className="text-sm flex items-start gap-2">
                        <span className="text-red-500">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Ayurvedic Medication */}
          {reportInsights.ayurvedicMedication.recommendations && 
           reportInsights.ayurvedicMedication.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Leaf className="h-5 w-5 text-primary" />
                  Ayurvedic Medication
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Accordion type="single" collapsible className="space-y-2">
                  {reportInsights.ayurvedicMedication.recommendations.map((rec: any, index: number) => (
                    <AccordionItem 
                      key={index} 
                      value={`ayur-${index}`}
                      className="border rounded-md p-0 overflow-hidden"
                    >
                      <AccordionTrigger className="px-4 py-3 hover:no-underline">
                        <div className="flex items-center gap-2">
                          <span>{rec.name}</span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-4 pb-4">
                        <div className="space-y-3">
                          <div>
                            <h5 className="text-sm font-medium">Description</h5>
                            <p className="text-sm text-muted-foreground">{rec.description}</p>
                          </div>
                          <div>
                            <h5 className="text-sm font-medium">Why It's Important</h5>
                            <p className="text-sm text-muted-foreground">{rec.importance}</p>
                          </div>
                          <div>
                            <h5 className="text-sm font-medium">Benefits</h5>
                            <p className="text-sm text-muted-foreground">{rec.benefits}</p>
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </CardContent>
            </Card>
          )}

          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground whitespace-pre-line">
                {reportInsights.summary}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="text-sm text-muted-foreground bg-muted/20 p-4 rounded-lg">
        <p className="text-xs">
          <strong>Privacy Note:</strong> Your medical reports are processed securely and are not stored permanently on our servers. All data is encrypted in transit and at rest.
        </p>
      </div>
    </div>
  );
} 