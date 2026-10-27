import React from 'react';
import { PriorityLevel } from '../types';
import { AlertOctagon, AlertTriangle, Info, Check } from 'lucide-react';

interface Props {
  priority: PriorityLevel;
  className?: string;
}

export const PriorityBadge: React.FC<Props> = ({ priority, className = '' }) => {
  switch (priority) {
    case 'Critical':
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-red-100 text-red-900 border border-red-300 ${className}`}
        >
          <AlertOctagon className="w-3.5 h-3.5 text-red-600" />
          Critical Priority
        </span>
      );
    case 'High':
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-orange-100 text-orange-950 border border-orange-300 ${className}`}
        >
          <AlertTriangle className="w-3.5 h-3.5 text-orange-600" />
          High Priority
        </span>
      );
    case 'Medium':
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-900 border border-blue-200 ${className}`}
        >
          <Info className="w-3.5 h-3.5 text-blue-600" />
          Medium Priority
        </span>
      );
    case 'Low':
    default:
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 ${className}`}
        >
          <Check className="w-3.5 h-3.5 text-slate-500" />
          Low Priority
        </span>
      );
  }
};
