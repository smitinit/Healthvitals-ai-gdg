// const handleSubmit = async () => {
//   setLoading(true);

//   // Validate symptoms have severity and duration
//   const isValid = selectedSymptoms.every((s) => s.severity && s.duration);

//   if (!isValid) {
//     setError("Please ensure all symptoms have severity and duration");
//     setLoading(false);
//     return;
//   }

//   try {
//     const result = await generateAnalysisResult(
//       selectedSymptoms,
//       age,
//       gender,
//       medicalHistory,
//       dietPreference,
//       currentMedications,
//       allergies,
//       recentLifeChanges,
//       symptomTriggers
//     );

//     console.log("Analysis result received:", result);
//     setAnalysisResult(result);
//     router.push(`/symptom-scanner/result?step=summary`);
//   } catch (error) {
//     console.error("Error in symptom analysis:", error);
//     setError(
//       error instanceof Error
//         ? `${error.message}`
//         : "There was an error analyzing your symptoms. Please try again."
//     );
//   } finally {
//     setLoading(false);
//   }
// };
