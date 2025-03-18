"use client";

import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { medicalHistoryOptions } from "@/data/symptom-data";

interface PersonalInfoProps {
  age: string;
  setAge: (age: string) => void;
  gender: string;
  setGender: (gender: string) => void;
  medicalHistory: string[];
  setMedicalHistory: (history: string[]) => void;
}

export default function PersonalInfo({
  age,
  setAge,
  gender,
  setGender,
  medicalHistory,
  setMedicalHistory,
}: PersonalInfoProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label htmlFor="age" className="text-sm font-medium">
            Age
          </label>
          <Input
            id="age"
            type="number"
            placeholder="Enter your age"
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="gender" className="text-sm font-medium">
            Gender
          </label>
          <Select value={gender} onValueChange={setGender}>
            <SelectTrigger id="gender">
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="non-binary">Non-binary</SelectItem>
              <SelectItem value="prefer-not-to-say">
                Prefer not to say
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Medical History</label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {medicalHistoryOptions.map((condition) => (
            <div
              key={condition}
              className="flex items-center space-x-2 border rounded-md p-2"
            >
              <input
                type="checkbox"
                id={`condition-${condition}`}
                checked={medicalHistory.includes(condition)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setMedicalHistory([...medicalHistory, condition]);
                  } else {
                    setMedicalHistory(
                      medicalHistory.filter((c) => c !== condition)
                    );
                  }
                }}
                className="h-4 w-4 rounded border-gray-300"
              />
              <label
                htmlFor={`condition-${condition}`}
                className="text-sm cursor-pointer"
              >
                {condition}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="medications" className="text-sm font-medium">
          Current Medications
        </label>
        <Textarea
          id="medications"
          placeholder="List any medications you are currently taking..."
          className="min-h-[100px]"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="allergies" className="text-sm font-medium">
          Allergies
        </label>
        <Textarea
          id="allergies"
          placeholder="List any allergies you have..."
          className="min-h-[100px]"
        />
      </div>
    </div>
  );
}
