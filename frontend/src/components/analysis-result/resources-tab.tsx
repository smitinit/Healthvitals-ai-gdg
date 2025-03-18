import { Button } from "@/components/ui/button";
import { medicalArticles } from "@/data/symptom-data";
import { Activity, ChevronRight, FileText, Heart } from "lucide-react";

export default function ResourcesTab() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">
          Relevant Medical Articles
        </h3>
        <div className="space-y-4">
          {medicalArticles.map((article) => (
            <div key={article.id} className="p-4 border rounded-lg">
              <h4 className="font-medium">{article.title}</h4>
              <p className="text-sm text-muted-foreground mt-1">
                {article.excerpt}
              </p>
              <div className="flex items-center justify-between mt-3">
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <FileText className="h-3 w-3" />
                  <span>{article.source}</span>
                  <span>•</span>
                  <span>{article.date}</span>
                </div>
                <Button variant="link" size="sm" className="h-auto p-0">
                  Read More
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 border rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <Heart className="h-5 w-5 text-primary" />
            <h3 className="font-medium">Self-Care Tips</h3>
          </div>
          <ul className="space-y-2">
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>
                Stay hydrated by drinking plenty of water throughout the day
              </span>
            </li>
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Get adequate rest to allow your body to recover</span>
            </li>
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>
                Maintain a balanced diet rich in fruits and vegetables
              </span>
            </li>
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>
                Practice stress-reduction techniques like deep breathing or
                meditation
              </span>
            </li>
          </ul>
        </div>

        <div className="p-4 border rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="h-5 w-5 text-primary" />
            <h3 className="font-medium">Symptom Tracking</h3>
          </div>
          <p className="text-sm mb-3">
            Keep track of your symptoms to share with healthcare providers:
          </p>
          <ul className="space-y-2">
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Note when symptoms started and how they've changed</span>
            </li>
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>
                Record any factors that seem to trigger or worsen symptoms
              </span>
            </li>
            <li className="flex items-start gap-2 text-sm">
              <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Track effectiveness of any treatments or medications</span>
            </li>
          </ul>
          <Button className="w-full mt-3">Download Symptom Tracker</Button>
        </div>
      </div>
    </div>
  );
}
