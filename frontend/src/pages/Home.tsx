import { motion } from "framer-motion";
import {
  ArrowDown,
  ArrowRight,
  Brain,
  CheckCircle,
  Stethoscope,
} from "lucide-react";
import { Button } from "@/components/ui/button";
// import SymptomScanDemo from "@/components/sympto-scan";
import { Link } from "react-router";
import Landing_page_image from "../assets/Landing_page_image.jpg";

import { useRef } from "react";
// import { useAuth } from "@clerk/clerk-react";

export default function Home() {
  const symptomScanRef = useRef<HTMLDivElement>(null);
  // const { isSignedIn } = useAuth();

  // Function to scroll to SymptomScan section
  const scrollToSymptomScan = () => {
    symptomScanRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Function to handle Try SymptomScan Now button click
  // const handleTrySymptomScanNow = () => {
  //   if (!isSignedIn) {
  //     // If not signed in, redirect will happen via the Link component
  //     // to the symptoscan-pro route, which will then redirect to sign-in
  //     return;
  //   }
  //   // If signed in, just navigate to symptoscan-pro via the Link component
  // };

  return (
    <>
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="py-20 px-4 md:px-6 lg:px-8">
          <div className="container mx-auto max-w-6xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-primary">
                  HealthVitals AI
                </h1>
                <p className="mt-4 text-xl text-muted-foreground">
                  Advanced AI-powered health analysis at your fingertips
                </p>
                <p className="mt-6 text-lg text-muted-foreground">
                  Get instant insights about your symptoms and potential health
                  concerns with our cutting-edge AI technology.
                </p>
                <div className="mt-8 flex flex-col sm:flex-row gap-4">
                  <Button
                    size="lg"
                    className="gap-2"
                    onClick={scrollToSymptomScan}
                  >
                    About SymptomScan <ArrowDown className="h-4 w-4" />
                  </Button>
                  {/* <Link to="/symptoscan-pro">
                    <Button size="lg" variant="outline" className="gap-2">
                      Try SymptomScan Pro <Stethoscope className="h-4 w-4" />
                    </Button>
                  </Link> */}
                </div>
              </motion.div>

              {/* <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="relative h-[400px] rounded-lg overflow-hidden bg-gradient-to-br from-blue-50 to-teal-50 "
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <img
                    src={Landing_page_image}
                    alt="HealthVitals AI Dashboard"
                    className="object-cover"
                  />
                </div>
              </motion.div> */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9, rotate: 0 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  rotate: window.innerWidth >= 768 ? 5 : 0, // Rotate only on devices wider than 768px
                }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="relative h-[400px] rounded-lg overflow-hidden  "
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <img
                    src={Landing_page_image}
                    alt="HealthVitals AI Dashboard"
                    className="object-cover"
                  />
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Feature Section - SymptomScan */}
        <section
          ref={symptomScanRef}
          className="py-20 px-4 md:px-6 lg:px-8 bg-slate-50"
        >
          <div className="container mx-auto max-w-6xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-primary">
                Introducing SymptomScan
              </h2>
              <p className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto">
                Our core technology that analyzes your symptoms and provides
                accurate health insights.
              </p>
            </motion.div>

            <div className="flex flex-col md:flex-row gap-12 items-center justify-center">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                viewport={{ once: true }}
                // className="justify-self-center text-center mx-auto"
              >
                <h3 className="text-2xl font-bold text-primary">
                  How SymptomScan Works
                </h3>

                <ul className="mt-6 space-y-4">
                  {[
                    {
                      icon: <Brain className="h-5 w-5 text-primary" />,
                      title: "AI-Powered Analysis",
                      description:
                        "Our advanced AI analyzes your symptoms using the latest medical knowledge",
                    },
                    {
                      icon: <CheckCircle className="h-5 w-5 text-primary" />,
                      title: "Accurate Results",
                      description:
                        "Get reliable insights based on medical databases and AI learning",
                    },
                    {
                      icon: <Stethoscope className="h-5 w-5 text-primary" />,
                      title: "Healthcare Guidance",
                      description:
                        "Receive recommendations on next steps and potential treatments",
                    },
                  ].map((feature, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      viewport={{ once: true }}
                      className="flex gap-4"
                    >
                      <div className="mt-1 bg-primary/10 p-2 rounded-full">
                        {feature.icon}
                      </div>
                      <div>
                        <h4 className="font-medium text-primary">
                          {feature.title}
                        </h4>
                        <p className="mt-1 text-muted-foreground">
                          {feature.description}
                        </p>
                      </div>
                    </motion.li>
                  ))}
                </ul>

                <div className="mt-8 justify-self-end">
                  <Link to="/symptoscan-pro">
                    <Button size="lg" variant="outline" className="gap-2">
                      <ArrowRight className="h-4 w-4" />
                      Try SymptomScan Pro <Stethoscope className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-20 px-4 md:px-6 lg:px-8">
          <div className="container mx-auto max-w-6xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-primary">
                Trusted by Thousands
              </h2>
              <p className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto">
                See what our users have to say about HealthVitals AI
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  name: "Sarah Johnson",
                  role: "Healthcare Professional",
                  quote:
                    "HealthVitals AI has transformed how I provide initial assessments for my patients. The accuracy is impressive.",
                },
                {
                  name: "Michael Chen",
                  role: "Regular User",
                  quote:
                    "I was skeptical at first, but SymptomScan helped me identify a condition I needed to see a doctor about. It's been a lifesaver.",
                },
                {
                  name: "Emily Rodriguez",
                  role: "Medical Student",
                  quote:
                    "As a medical student, I find HealthVitals AI to be an excellent learning tool. The symptom analysis is thorough and educational.",
                },
              ].map((testimonial, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="bg-white p-6 rounded-lg shadow-md"
                >
                  <p className="italic text-muted-foreground">
                    "{testimonial.quote}"
                  </p>
                  <div className="mt-4 flex items-center">
                    <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-medium">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div className="ml-3">
                      <p className="font-medium text-primary">
                        {testimonial.name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4 md:px-6 lg:px-8 bg-primary text-primary-foreground">
          <div className="container mx-auto max-w-6xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <h2 className="text-3xl md:text-4xl font-bold">
                Ready to take control of your health?
              </h2>
              <p className="mt-4 text-xl max-w-2xl mx-auto opacity-90">
                Join thousands of users who trust HealthVitals AI for their
                health insights
              </p>
              <div className="mt-8">
                <Button
                  size="lg"
                  variant="secondary"
                  className="gap-2"
                  onClick={scrollToSymptomScan}
                >
                  Get Started Today <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
    </>
  );
}
