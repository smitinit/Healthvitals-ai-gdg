"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Symptom, BodyArea } from "@/types/symptom-types";
import { Plus, X } from "@/components/icons";
import { isSymptomAlreadySelected } from "@/utils/symptom-utils";
import { durationOptions } from "@/data/symptom-data";
import { toast } from "sonner";
// import { toast } from "@/";

interface SymptomSelectorProps {
  bodyAreas: BodyArea[];
  selectedSymptoms: Symptom[];
  setSelectedSymptoms: (symptoms: Symptom[]) => void;
}

export default function SymptomSelector({
  bodyAreas,
  selectedSymptoms,
  setSelectedSymptoms,
}: SymptomSelectorProps) {
  const [selectedBodyArea, setSelectedBodyArea] = useState<string | null>(null);
  const [textSymptoms, setTextSymptoms] = useState("");
  const [recentlyAdded, setRecentlyAdded] = useState<string | null>(null);

  const handleAddSymptom = (symptomName: string) => {
    // Check if symptom already exists
    if (isSymptomAlreadySelected(selectedSymptoms, symptomName)) {
      toast("Symptom already selected");
      return;
    }

    const newSymptom: Symptom = {
      id: `symptom-${Date.now()}`,
      name: symptomName,
      severity: 5, // Default to medium severity
      duration: "1-3 days", // Default duration
    };

    setSelectedSymptoms([...selectedSymptoms, newSymptom]);
    setRecentlyAdded(newSymptom.id);

    // Clear the highlight after animation
    setTimeout(() => {
      setRecentlyAdded(null);
    }, 2000);
  };

  const handleRemoveSymptom = (id: string) => {
    setSelectedSymptoms(selectedSymptoms.filter((s) => s.id !== id));
  };

  const handleUpdateSymptomSeverity = (id: string, severity: number) => {
    setSelectedSymptoms(
      selectedSymptoms.map((s) => (s.id === id ? { ...s, severity } : s))
    );
  };

  const handleUpdateSymptomDuration = (id: string, duration: string) => {
    setSelectedSymptoms(
      selectedSymptoms.map((s) => (s.id === id ? { ...s, duration } : s))
    );
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 space-y-4">
          <h3 className="text-lg font-medium">Body Areas</h3>
          <div className="space-y-2">
            {bodyAreas.map((area) => (
              <Button
                key={area.id}
                variant={selectedBodyArea === area.id ? "default" : "outline"}
                className="w-full justify-start"
                onClick={() => setSelectedBodyArea(area.id)}
              >
                {area.name}
              </Button>
            ))}
          </div>
        </div>
        <div className="md:col-span-2 space-y-4">
          <h3 className="text-lg font-medium">
            {selectedBodyArea
              ? `${
                  bodyAreas.find((a) => a.id === selectedBodyArea)?.name
                } Symptoms`
              : "Select a body area"}
          </h3>
          {selectedBodyArea ? (
            <div className="grid grid-cols-2 gap-2">
              {bodyAreas
                .find((a) => a.id === selectedBodyArea)
                ?.symptoms.map((symptom) => {
                  const isSelected = isSymptomAlreadySelected(
                    selectedSymptoms,
                    symptom
                  );
                  return (
                    <Button
                      key={symptom}
                      variant={isSelected ? "secondary" : "outline"}
                      className="justify-start"
                      onClick={() => !isSelected && handleAddSymptom(symptom)}
                      disabled={isSelected}
                    >
                      {isSelected ? (
                        <span className="mr-2 text-green-500">✓</span>
                      ) : (
                        <Plus className="mr-2 h-4 w-4" />
                      )}
                      {symptom}
                    </Button>
                  );
                })}
            </div>
          ) : (
            <div className="flex items-center justify-center h-40 border rounded-md bg-muted/20">
              <p className="text-muted-foreground">
                Please select a body area to see related symptoms
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">Selected Symptoms</h3>
          {selectedSymptoms.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedSymptoms([])}
            >
              Clear All
            </Button>
          )}
        </div>

        {selectedSymptoms.length > 0 ? (
          <div className="space-y-4">
            {selectedSymptoms.map((symptom) => (
              <div
                key={symptom.id}
                className={`flex flex-col space-y-3 p-4 border rounded-lg transition-all duration-300 ${
                  recentlyAdded === symptom.id
                    ? "bg-primary/5 border-primary"
                    : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{symptom.name}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemoveSymptom(symptom.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Severity</span>
                    <span className="text-sm font-medium">
                      {symptom.severity}/10
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={symptom.severity}
                    onChange={(e) =>
                      handleUpdateSymptomSeverity(
                        symptom.id,
                        Number.parseInt(e.target.value)
                      )
                    }
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Mild</span>
                    <span>Moderate</span>
                    <span>Severe</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-sm">Duration</label>
                  <Select
                    value={symptom.duration}
                    onValueChange={(value) =>
                      handleUpdateSymptomDuration(symptom.id, value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select duration" />
                    </SelectTrigger>
                    <SelectContent>
                      {durationOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-32 border rounded-md bg-muted/20">
            <p className="text-muted-foreground">
              No symptoms selected. Select from the list above or add custom
              symptoms.
            </p>
          </div>
        )}

        <div className="pt-4">
          <div className="flex items-center gap-2">
            <Input
              placeholder="Add a custom symptom..."
              value={textSymptoms}
              onChange={(e) => setTextSymptoms(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && textSymptoms.trim()) {
                  handleAddSymptom(textSymptoms.trim());
                  setTextSymptoms("");
                }
              }}
            />
            <Button
              onClick={() => {
                if (textSymptoms.trim()) {
                  handleAddSymptom(textSymptoms.trim());
                  setTextSymptoms("");
                }
              }}
              disabled={!textSymptoms.trim()}
            >
              Add
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
