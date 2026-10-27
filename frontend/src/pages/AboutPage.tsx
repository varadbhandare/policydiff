import React, { useEffect, useState } from 'react';
import {
  BookOpen,
  Cpu,
  Layers,
  Scale,
  ShieldCheck,
  CheckCircle2,
  FileText,
  AlertTriangle,
  RefreshCw,
  GitCompare,
  BarChart2,
  Code2,
} from 'lucide-react';
import { api } from '../services/api';
import { EvaluationMetrics } from '../types';

export const AboutPage: React.FC = () => {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  useEffect(() => {
    setLoadingMetrics(true);
    api.getEvaluationMetrics()
      .then((data) => {
        setMetrics(data);
        setLoadingMetrics(false);
      })
      .catch((err) => {
        console.error('Failed to load evaluation metrics:', err);
        setLoadingMetrics(false);
      });
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold mb-3">
          <BookOpen className="w-3.5 h-3.5" />
          <span>System Architecture & Academic Methodology</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          About PolicyDiff
        </h1>
        <p className="text-base text-slate-600 mt-2 max-w-2xl leading-relaxed">
          An explainable Natural Language Processing micro-system for detecting semantic differences,
          regulatory shifts, and numerical threshold alterations across academic policy documents.
        </p>
      </div>

      {/* Problem Statement & Objectives */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Scale className="w-5 h-5 text-blue-600" />
          Problem Statement & Objectives
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-slate-600 leading-relaxed">
          <div>
            <h3 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-2">The Challenge</h3>
            <p>
              Academic regulations, attendance rules, evaluation guidelines, and scholarship criteria undergo frequent
              annual revisions. Standard diff utilities rely on string edit distances (e.g. Git diff or Levenshtein),
              which fail to grasp subtle semantic shifts—such as transitioning from an optional recommendation to a
              compulsory obligation, or modifying numerical eligibility percentages from 75% to 80%.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-2">The Solution</h3>
            <p>
              PolicyDiff leverages a hybrid NLP architecture combining dense semantic vector embeddings (MiniLM-L6) with
              token-set lexical alignment (RapidFuzz) and deterministic entity difference extraction. Every detected change
              is categorized, assigned an explainable priority level, and accompanied by grounded natural language rationale.
            </p>
          </div>
        </div>
      </section>

      {/* Live Benchmark Evaluation Metrics */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-indigo-600" />
              Live Evaluation Benchmark Suite
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Empirical classification accuracy and confusion matrix measured against labeled policy pairs
            </p>
          </div>

          <button
            onClick={() => {
              setLoadingMetrics(true);
              api.getEvaluationMetrics().then((d) => {
                setMetrics(d);
                setLoadingMetrics(false);
              });
            }}
            disabled={loadingMetrics}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors self-start sm:self-auto cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingMetrics ? 'animate-spin' : ''}`} />
            <span>Re-run Evaluation</span>
          </button>
        </div>

        {metrics ? (
          <div className="space-y-6">
            {/* Top Metric Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-center">
                <span className="text-xs font-medium text-slate-500 block">Overall Accuracy</span>
                <span className="text-3xl font-extrabold text-blue-600 block mt-1">
                  {(metrics.accuracy * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-slate-400 mt-1 block">{metrics.total_samples} Labeled Test Cases</span>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-center">
                <span className="text-xs font-medium text-slate-500 block">Macro-Averaged F1</span>
                <span className="text-3xl font-extrabold text-indigo-600 block mt-1">
                  {(metrics.macro_f1 * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-slate-400 mt-1 block">Harmonic Mean</span>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-center">
                <span className="text-xs font-medium text-slate-500 block">Macro Precision</span>
                <span className="text-3xl font-extrabold text-emerald-600 block mt-1">
                  {(metrics.macro_precision * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-slate-400 mt-1 block">Low False Positive Rate</span>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-center">
                <span className="text-xs font-medium text-slate-500 block">Macro Recall</span>
                <span className="text-3xl font-extrabold text-amber-600 block mt-1">
                  {(metrics.macro_recall * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-slate-400 mt-1 block">High Change Capture</span>
              </div>
            </div>

            {/* Per-Class Performance Table */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                Per-Class Classification Metrics
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border border-slate-200 rounded-lg overflow-hidden">
                  <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
                    <tr>
                      <th className="p-3">Class Label</th>
                      <th className="p-3">Support (Samples)</th>
                      <th className="p-3">Precision</th>
                      <th className="p-3">Recall</th>
                      <th className="p-3">F1-Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {Object.entries(metrics.per_class).map(([cls, vals]) => (
                      <tr key={cls} className="hover:bg-slate-50">
                        <td className="p-3 font-bold text-slate-800">{cls}</td>
                        <td className="p-3 text-slate-600">{vals.support}</td>
                        <td className="p-3 text-slate-700">{(vals.precision * 100).toFixed(1)}%</td>
                        <td className="p-3 text-slate-700">{(vals.recall * 100).toFixed(1)}%</td>
                        <td className="p-3 font-semibold text-blue-700">{(vals.f1_score * 100).toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Confusion Matrix */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                Confusion Matrix (Predicted vs Actual)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-center text-xs border border-slate-200 rounded-lg overflow-hidden">
                  <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
                    <tr>
                      <th className="p-2.5 text-left">Actual \ Predicted</th>
                      {Object.keys(metrics.confusion_matrix).map((c) => (
                        <th key={c} className="p-2.5">{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {Object.entries(metrics.confusion_matrix).map(([actClass, row]) => (
                      <tr key={actClass}>
                        <td className="p-2.5 text-left font-bold text-slate-800 bg-slate-50">{actClass}</td>
                        {Object.entries(row).map(([predClass, count]) => {
                          const isDiag = actClass === predClass;
                          return (
                            <td
                              key={predClass}
                              className={`p-2.5 font-mono ${
                                isDiag && count > 0
                                  ? 'bg-emerald-50 text-emerald-800 font-bold'
                                  : count > 0
                                  ? 'bg-rose-50 text-rose-800 font-bold'
                                  : 'text-slate-400'
                              }`}
                            >
                              {count}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-400">Loading benchmark dataset...</div>
        )}
      </section>

      {/* 10-Stage Pipeline Breakdown */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-600" />
          The 10-Stage NLP Processing Pipeline
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {[
            {
              num: '1',
              title: 'Document Ingestion',
              desc: 'Extracts text, hierarchy, and page indices from PDF (PyMuPDF), DOCX, and TXT with scanned image detection.',
            },
            {
              num: '2',
              title: 'Text Preprocessing',
              desc: 'Unicode NFKC normalization, whitespace grooming, and sentence tokenization with abbreviation protection.',
            },
            {
              num: '3',
              title: 'Rule & Heading Segmentation',
              desc: 'Identifies numbered clauses, bullet conditions, and sections to bind context to each rule unit.',
            },
            {
              num: '4',
              title: 'Cross-Version Alignment',
              desc: 'Computes dense semantic vectors + RapidFuzz token-set ratios to solve bipartite cross-version rule matching.',
            },
            {
              num: '5',
              title: 'Change Classification',
              desc: 'Categorizes rules into ADDED, REMOVED, MODIFIED, and UNCHANGED based on semantic and entity cues.',
            },
            {
              num: '6',
              title: 'Entity & Threshold Extraction',
              desc: 'Detects dates, deadlines, attendance percentages, fees, credit counts, and student cohort scopes.',
            },
            {
              num: '7',
              title: 'Modality & Negation Analysis',
              desc: 'Evaluates obligation transitions ("must" vs "may") and reversals in conduct prohibitions.',
            },
            {
              num: '8',
              title: 'Rule-Based Priority Heuristics',
              desc: 'Assigns Critical, High, Medium, or Low priority based on examination, eligibility, or financial impact.',
            },
            {
              num: '9',
              title: 'Grounded Plain-English Generator',
              desc: 'Produces transparent explanations strictly derived from extracted diffs without generative hallucination.',
            },
            {
              num: '10',
              title: 'Confidence Scoring & Traceability',
              desc: 'Exposes alignment similarity and confidence scores, linking every conclusion back to original source excerpts.',
            },
          ].map((stage) => (
            <div key={stage.num} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold shrink-0 mt-0.5">
                {stage.num}
              </span>
              <div>
                <strong className="block text-slate-800 font-semibold mb-0.5">{stage.title}</strong>
                <p className="text-slate-500 leading-relaxed">{stage.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Technology Stack & Limitations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-3">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Code2 className="w-4 h-4 text-blue-600" />
            Technology Stack
          </h2>
          <ul className="text-xs text-slate-600 space-y-2">
            <li><strong>Frontend:</strong> React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Recharts</li>
            <li><strong>Backend:</strong> Python 3.12, FastAPI, Uvicorn, Pydantic v2</li>
            <li><strong>Persistence:</strong> SQLite with SQLAlchemy 2.0 ORM</li>
            <li><strong>NLP:</strong> Sentence Transformers (all-MiniLM-L6-v2), Scikit-Learn Cosine Similarity, RapidFuzz</li>
            <li><strong>Document Parsers:</strong> PyMuPDF (fitz), python-docx, ReportLab for PDF compilation</li>
          </ul>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-3">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Limitations & Institutional Disclaimer
          </h2>
          <div className="text-xs text-slate-600 space-y-2 leading-relaxed">
            <p>
              <strong>Scanned Documents:</strong> Image-only PDFs require an upstream OCR engine (e.g. Tesseract) to
              generate a searchable text layer prior to semantic alignment.
            </p>
            <p>
              <strong>Disclaimer:</strong> PolicyDiff is an automated decision-support and assistive review tool. It is
              not a replacement for official institutional governance, academic senate approval, or formal legal advice.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
