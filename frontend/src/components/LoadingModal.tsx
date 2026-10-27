import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';

interface Props {
  isOpen: boolean;
}

const STAGES = [
  'Validating document format and reading structure...',
  'Segmenting policy clauses, numbered rules, and section headings...',
  'Executing dual semantic embedding & bipartite alignment...',
  'Analyzing changes in dates, thresholds, negation, and obligations...',
  'Generating plain-English explanations and compiling report...',
];

export const LoadingModal: React.FC<Props> = ({ isOpen }) => {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    if (!isOpen) {
      setCurrentStage(0);
      return;
    }
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 1800);
    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Comparing Policy Documents</h3>
            <p className="text-xs text-slate-500">Executing Deep NLP Difference Engine</p>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          {STAGES.map((stageText, idx) => {
            const isDone = idx < currentStage;
            const isCurrent = idx === currentStage;

            return (
              <div
                key={idx}
                className={`flex items-start gap-3 text-xs p-2.5 rounded-lg transition-all ${
                  isCurrent
                    ? 'bg-blue-50 text-blue-900 font-medium border border-blue-200'
                    : isDone
                    ? 'text-slate-600 bg-slate-50'
                    : 'text-slate-400'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-blue-600 animate-spin shrink-0 mt-0.5" />
                ) : (
                  <span className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[10px] text-slate-400 shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                )}
                <span>{stageText}</span>
              </div>
            );
          })}
        </div>

        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${((currentStage + 1) / STAGES.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};
