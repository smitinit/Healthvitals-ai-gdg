import { Loader2 } from "lucide-react";

export default function LoadingAnalysis() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
      <h3 className="text-lg font-medium mb-2">Analyzing Your Symptoms</h3>
      <p className="text-sm text-muted-foreground text-center max-w-md">
        Our AI is processing your symptoms and comparing them with thousands of
        medical conditions to provide you with accurate insights.
      </p>
    </div>
  );
}
