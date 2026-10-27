import React from 'react';
import { GitCompare, ShieldCheck, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 text-sm mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <GitCompare className="w-4 h-4" />
              </div>
              <span className="font-bold text-lg text-white">PolicyDiff</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-md">
              A high-precision Natural Language Processing and Document Intelligence system designed for academic
              administrators, faculty, and students. Detects nuanced changes in obligations, thresholds, dates, and
              eligibility conditions across revised policy documents.
            </p>
          </div>

          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">NLP Capabilities</h4>
            <ul className="space-y-2 text-xs">
              <li>Cross-Version Rule Alignment</li>
              <li>Dual Semantic Embeddings + RapidFuzz</li>
              <li>Entity & Numeric Threshold Detection</li>
              <li>Modal Obligation & Negation Analysis</li>
              <li>Grounded Explainability Engine</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">Compliance & Ethics</h4>
            <div className="flex items-start gap-2 text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <p>
                Local-first privacy architecture: Uploaded policy documents are processed on local compute without
                third-party cloud telemetry or external LLM data leaks.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© {new Date().getFullYear()} PolicyDiff — Academic Policy Change Detector.</p>
          <p className="flex items-center gap-1 mt-2 sm:mt-0">
            Built for Academic NLP Excellence with React, FastAPI & PyMuPDF
          </p>
        </div>
      </div>
    </footer>
  );
};
