import React from 'react';
import { ChangeType } from '../types';
import { PlusCircle, MinusCircle, RefreshCw, CheckCircle2 } from 'lucide-react';

interface Props {
  type: ChangeType;
  className?: string;
}

export const DiffBadge: React.FC<Props> = ({ type, className = '' }) => {
  switch (type) {
    case 'ADDED':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 ${className}`}
        >
          <PlusCircle className="w-3.5 h-3.5" />
          ADDED
        </span>
      );
    case 'REMOVED':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300 ${className}`}
        >
          <MinusCircle className="w-3.5 h-3.5" />
          REMOVED
        </span>
      );
    case 'MODIFIED':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300 ${className}`}
        >
          <RefreshCw className="w-3.5 h-3.5" />
          MODIFIED
        </span>
      );
    case 'UNCHANGED':
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-300 ${className}`}
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          UNCHANGED
        </span>
      );
  }
};
