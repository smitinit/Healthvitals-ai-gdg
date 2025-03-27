import React from 'react';
import { cn } from '@/lib/utils';

interface CircleProgressProps extends React.SVGAttributes<SVGElement> {
  value: number;
  max: number;
  strokeWidth?: number;
}

const CircleProgress = ({ 
  value, 
  max, 
  className, 
  strokeWidth = 2,
  ...props 
}: CircleProgressProps) => {
  // Calculate the percentage
  const percentage = (value / max) * 100;
  
  // Calculate the radius and circumference
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  
  // Calculate the dash offset based on the percentage
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg 
      className={cn('transform -rotate-90', className)} 
      height="100" 
      width="100" 
      viewBox="0 0 100 100"
      {...props}
    >
      <circle
        className="text-current"
        strokeWidth={strokeWidth}
        stroke="currentColor"
        fill="transparent"
        r={radius}
        cx="50"
        cy="50"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
      />
    </svg>
  );
};

export default CircleProgress; 