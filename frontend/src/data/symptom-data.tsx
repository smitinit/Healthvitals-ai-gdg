import type {
  BodyArea,
  Doctor,
  DummyConditions,
  MedicalArticle,
} from "@/types/symptom-types";

// Body areas and associated symptoms
export const bodyAreas: BodyArea[] = [
  {
    id: "head",
    name: "Head & Face",
    symptoms: [
      "Headache",
      "Facial pain",
      "Dizziness",
      "Sinus pressure",
      "Eye pain",
    ],
  },
  {
    id: "respiratory",
    name: "Respiratory System",
    symptoms: [
      "Cough",
      "Shortness of breath",
      "Sore throat",
      "Runny nose",
      "Congestion",
      "Sneezing",
    ],
  },
  {
    id: "digestive",
    name: "Digestive System",
    symptoms: [
      "Nausea",
      "Vomiting",
      "Diarrhea",
      "Constipation",
      "Abdominal pain",
      "Heartburn",
    ],
  },
  {
    id: "musculoskeletal",
    name: "Muscles & Joints",
    symptoms: [
      "Joint pain",
      "Muscle aches",
      "Stiffness",
      "Back pain",
      "Weakness",
    ],
  },
  {
    id: "skin",
    name: "Skin",
    symptoms: ["Rash", "Itching", "Hives", "Discoloration", "Dryness"],
  },
  {
    id: "general",
    name: "General",
    symptoms: ["Fever", "Fatigue", "Chills", "Night sweats", "Weight changes"],
  },
];

// Dummy data for the enhanced demo
export const dummyConditions: DummyConditions = {
  respiratory: [
    {
      name: "Common Cold",
      description: "A viral infection of the upper respiratory tract.",
      symptoms: ["Runny nose", "Sore throat", "Cough", "Mild fever"],
      urgency: "low",
      treatmentOptions: [
        "Rest and hydration",
        "Over-the-counter cold medications",
        "Saline nasal spray",
      ],
      recoveryTime: "7-10 days",
      preventionTips: [
        "Frequent handwashing",
        "Avoid close contact with sick individuals",
        "Maintain good immune health",
      ],
    },
    {
      name: "Seasonal Allergies",
      description: "An immune response to environmental triggers like pollen.",
      symptoms: ["Sneezing", "Itchy eyes", "Runny nose", "Congestion"],
      urgency: "low",
      treatmentOptions: [
        "Antihistamines",
        "Nasal corticosteroids",
        "Avoiding allergens",
      ],
      recoveryTime: "Varies with exposure",
      preventionTips: [
        "Track pollen counts",
        "Keep windows closed during high pollen seasons",
        "Use air purifiers",
      ],
    },
    {
      name: "Sinus Infection",
      description: "Inflammation of the sinuses, often following a cold.",
      symptoms: [
        "Facial pressure",
        "Thick nasal discharge",
        "Headache",
        "Congestion",
      ],
      urgency: "medium",
      treatmentOptions: [
        "Antibiotics (if bacterial)",
        "Nasal decongestants",
        "Saline irrigation",
      ],
      recoveryTime: "10-14 days",
      preventionTips: [
        "Treat colds promptly",
        "Use a humidifier",
        "Practice good hand hygiene",
      ],
    },
    {
      name: "Bronchitis",
      description: "Inflammation of the bronchial tubes in the lungs.",
      symptoms: [
        "Persistent cough",
        "Chest discomfort",
        "Fatigue",
        "Mild fever",
      ],
      urgency: "medium",
      treatmentOptions: [
        "Rest and hydration",
        "Cough suppressants",
        "Bronchodilators (if needed)",
      ],
      recoveryTime: "2-3 weeks",
      preventionTips: [
        "Avoid smoking",
        "Reduce exposure to air pollutants",
        "Get vaccinated against respiratory infections",
      ],
    },
  ],
  digestive: [
    {
      name: "Gastroenteritis",
      description: "Inflammation of the stomach and intestines.",
      symptoms: ["Nausea", "Vomiting", "Diarrhea", "Abdominal cramps"],
      urgency: "medium",
      treatmentOptions: [
        "Hydration",
        "BRAT diet (Bananas, Rice, Applesauce, Toast)",
        "Rest",
      ],
      recoveryTime: "1-3 days",
      preventionTips: [
        "Proper food handling",
        "Frequent handwashing",
        "Avoid contaminated food and water",
      ],
    },
    {
      name: "Acid Reflux",
      description: "Backward flow of stomach acid into the esophagus.",
      symptoms: [
        "Heartburn",
        "Regurgitation",
        "Chest pain",
        "Difficulty swallowing",
      ],
      urgency: "low",
      treatmentOptions: [
        "Antacids",
        "H2 blockers",
        "Proton pump inhibitors",
        "Dietary changes",
      ],
      recoveryTime: "Manageable with treatment",
      preventionTips: [
        "Avoid trigger foods",
        "Eat smaller meals",
        "Don't lie down after eating",
        "Maintain healthy weight",
      ],
    },
  ],
  neurological: [
    {
      name: "Tension Headache",
      description: "Common headache with mild to moderate pain.",
      symptoms: [
        "Dull, aching head pain",
        "Tightness around forehead",
        "Tenderness in scalp",
      ],
      urgency: "low",
      treatmentOptions: [
        "Over-the-counter pain relievers",
        "Stress management",
        "Rest",
      ],
      recoveryTime: "30 minutes to several hours",
      preventionTips: [
        "Regular exercise",
        "Adequate sleep",
        "Stress reduction techniques",
      ],
    },
    {
      name: "Migraine",
      description: "Recurring headache with moderate to severe pain.",
      symptoms: [
        "Throbbing pain",
        "Sensitivity to light and sound",
        "Nausea",
        "Visual disturbances",
      ],
      urgency: "medium",
      treatmentOptions: [
        "Pain relievers",
        "Triptans",
        "Anti-nausea medications",
        "Rest in dark, quiet room",
      ],
      recoveryTime: "4-72 hours",
      preventionTips: [
        "Identify and avoid triggers",
        "Maintain regular sleep schedule",
        "Stay hydrated",
      ],
    },
  ],
};

export const nearbyDoctors: Doctor[] = [
  {
    id: 1,
    name: "Dr. Sarah Johnson",
    specialty: "General Practitioner",
    distance: "0.8 miles",
    availability: "Today",
    rating: 4.8,
    image: "/placeholder.svg?height=80&width=80",
    address: "123 Medical Center Dr, Suite 101",
    phone: "(555) 123-4567",
  },
  {
    id: 2,
    name: "Dr. Michael Chen",
    specialty: "Pulmonologist",
    distance: "1.2 miles",
    availability: "Tomorrow",
    rating: 4.9,
    image: "/placeholder.svg?height=80&width=80",
    address: "456 Health Parkway, Building B",
    phone: "(555) 987-6543",
  },
  {
    id: 3,
    name: "Dr. Emily Rodriguez",
    specialty: "Family Medicine",
    distance: "1.5 miles",
    availability: "Today",
    rating: 4.7,
    image: "/placeholder.svg?height=80&width=80",
    address: "789 Wellness Blvd",
    phone: "(555) 456-7890",
  },
];

export const medicalArticles: MedicalArticle[] = [
  {
    id: 1,
    title: "Understanding Upper Respiratory Infections",
    excerpt:
      "Learn about the common causes, symptoms, and treatments for URIs.",
    source: "Medical Journal International",
    date: "May 15, 2023",
    url: "#",
  },
  {
    id: 2,
    title: "When to See a Doctor for Respiratory Symptoms",
    excerpt:
      "Guidelines for determining when your symptoms require professional medical attention.",
    source: "Health Advisory Board",
    date: "June 3, 2023",
    url: "#",
  },
  {
    id: 3,
    title: "Seasonal Allergies vs. Common Cold: How to Tell the Difference",
    excerpt: "Key differences between allergic reactions and viral infections.",
    source: "Allergy & Immunology Today",
    date: "April 22, 2023",
    url: "#",
  },
];

export const medicalHistoryOptions = [
  "Asthma",
  "Diabetes",
  "Hypertension",
  "Heart Disease",
  "Allergies",
  "Thyroid Disorder",
  "Cancer",
  "Autoimmune Disease",
  "Depression/Anxiety",
];

export const durationOptions = [
  { value: "Less than 24 hours", label: "Less than 24 hours" },
  { value: "1-3 days", label: "1-3 days" },
  { value: "4-7 days", label: "4-7 days" },
  { value: "1-2 weeks", label: "1-2 weeks" },
  { value: "More than 2 weeks", label: "More than 2 weeks" },
];
