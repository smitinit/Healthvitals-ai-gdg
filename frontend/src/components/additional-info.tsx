import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function AdditionalInfo() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <label htmlFor="lifestyle" className="text-sm font-medium">
          Lifestyle Factors
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm">Exercise Frequency</p>
            <Select defaultValue="moderate">
              <SelectTrigger>
                <SelectValue placeholder="Select frequency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sedentary">
                  Sedentary (Rarely exercise)
                </SelectItem>
                <SelectItem value="light">Light (1-2 days/week)</SelectItem>
                <SelectItem value="moderate">
                  Moderate (3-4 days/week)
                </SelectItem>
                <SelectItem value="active">Active (5+ days/week)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <p className="text-sm">Sleep Quality</p>
            <Select defaultValue="fair">
              <SelectTrigger>
                <SelectValue placeholder="Select quality" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="poor">Poor ({"<"} 5 hours/night)</SelectItem>
                <SelectItem value="fair">Fair (5-6 hours/night)</SelectItem>
                <SelectItem value="good">Good (7-8 hours/night)</SelectItem>
                <SelectItem value="excellent">
                  Excellent (8+ hours/night)
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="stress" className="text-sm font-medium">
          Stress Level
        </label>
        <div className="space-y-1">
          <input
            type="range"
            min="1"
            max="10"
            defaultValue="5"
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Low</span>
            <span>Moderate</span>
            <span>High</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="diet" className="text-sm font-medium">
          Diet
        </label>
        <Select defaultValue="balanced">
          <SelectTrigger id="diet">
            <SelectValue placeholder="Select diet type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="balanced">Balanced</SelectItem>
            <SelectItem value="vegetarian">Vegetarian</SelectItem>
            <SelectItem value="vegan">Vegan</SelectItem>
            <SelectItem value="keto">Keto</SelectItem>
            <SelectItem value="paleo">Paleo</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label htmlFor="recent-changes" className="text-sm font-medium">
          Recent Life Changes
        </label>
        <Textarea
          id="recent-changes"
          placeholder="Describe any recent changes in your life that might be relevant (e.g., travel, new job, moved homes)..."
          className="min-h-[100px]"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="symptom-triggers" className="text-sm font-medium">
          Symptom Triggers
        </label>
        <Textarea
          id="symptom-triggers"
          placeholder="Describe anything that seems to trigger or worsen your symptoms..."
          className="min-h-[100px]"
        />
      </div>
    </div>
  );
}
