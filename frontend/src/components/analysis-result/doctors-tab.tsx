import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { nearbyDoctors } from "@/data/symptom-data";
import {
  AlertTriangle,
  Calendar,
  Info,
  MapPin,
  Phone,
  Star,
  User,
} from "lucide-react";

export default function DoctorsTab() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">
          Nearby Healthcare Providers
        </h3>
        <div className="space-y-4">
          {nearbyDoctors.map((doctor) => (
            <div
              key={doctor.id}
              className="p-4 border rounded-lg flex flex-col md:flex-row gap-4"
            >
              <div className="flex-shrink-0">
                <Avatar className="h-16 w-16 md:h-20 md:w-20">
                  <AvatarImage src={doctor.image} alt={doctor.name} />
                  <AvatarFallback>
                    <User className="h-8 w-8" />
                  </AvatarFallback>
                </Avatar>
              </div>
              <div className="flex-grow space-y-3">
                <div>
                  <h4 className="font-medium">{doctor.name}</h4>
                  <p className="text-sm text-muted-foreground">
                    {doctor.specialty}
                  </p>
                </div>
                <div className="flex flex-wrap gap-y-2 gap-x-4 text-sm">
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4 text-primary" />
                    <span>{doctor.distance}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4 text-primary" />
                    <span>Available: {doctor.availability}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                    <span>{doctor.rating}/5</span>
                  </div>
                </div>
                <div className="text-sm">
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span>{doctor.address}</span>
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{doctor.phone}</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-row md:flex-col gap-2 justify-end md:justify-center">
                <Button>Book Appointment</Button>
                <Button variant="outline">View Profile</Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 border rounded-lg bg-muted/10">
        <div className="flex items-center gap-2 mb-3">
          <Info className="h-5 w-5 text-primary" />
          <h3 className="font-medium">When to Seek Immediate Care</h3>
        </div>
        <p className="text-sm mb-3">
          If you experience any of the following symptoms, please seek immediate
          medical attention:
        </p>
        <ul className="space-y-1 text-sm">
          <li className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
            <span>Difficulty breathing or shortness of breath</span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
            <span>Severe chest or abdominal pain</span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
            <span>Sudden dizziness, weakness, or changes in vision</span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
            <span>High fever with headache and stiff neck</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
