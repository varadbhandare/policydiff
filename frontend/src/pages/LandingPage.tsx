import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitCompare,
  ArrowRight,
  Sparkles,
  Calendar,
  Percent,
  CheckCircle2,
  FileText,
  FileCheck,
  ShieldAlert,
  Download,
  Search,
  BookOpen,
  Scale,
  Loader2,
} from 'lucide-react';
import { api } from '../services/api';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleExploreDemo = async () => {
    setLoadingDemo(true);
    try {
      const demoResult = await api.getDemoComparison();
      navigate(`/results/${demoResult.id}`);
    } catch (err) {
      console.error('Failed to load demo:', err);
      // Fallback navigate to compare page
      navigate('/compare');
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 bg-linear-to-b from-white via-slate-50/50 to-slate-100/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column: Heading & CTAs */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Next-Gen NLP Document Intelligence</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.12]">
                Understand Every <br />
                <span className="text-transparent bg-clip-text bg-linear-to-r from-blue-600 via-indigo-600 to-sky-600">
                  Policy Change.
                </span>
              </h1>

              <p className="text-base sm:text-lg text-slate-600 max-w-xl leading-relaxed">
                Compare policy versions, discover meaningful changes, and never overlook a critical rule.
                Powered by semantic vector embeddings, RapidFuzz alignment, and deterministic entity difference detection.
              </p>

              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={() => navigate('/compare')}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/25 transition-all text-sm group cursor-pointer"
                >
                  <span>Compare Policies</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>

                <button
                  onClick={handleExploreDemo}
                  disabled={loadingDemo}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 shadow-xs transition-all text-sm cursor-pointer disabled:opacity-75"
                >
                  {loadingDemo ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      <span>Loading Demonstration...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-amber-500" />
                      <span>Explore Sample Comparison</span>
                    </>
                  )}
                </button>
              </div>

              {/* Supported formats pills */}
              <div className="flex items-center gap-4 pt-4 text-xs text-slate-500 font-medium">
                <span>Supported Formats:</span>
                <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">PDF</span>
                <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">DOCX</span>
                <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">TXT</span>
              </div>
            </div>

            {/* Right Column: Visual Comparison Illustration */}
            <div className="lg:col-span-5">
              <div className="relative">
                {/* Decorative background glow */}
                <div className="absolute -inset-4 bg-linear-to-r from-blue-500/10 to-indigo-500/10 rounded-3xl blur-xl" />

                <div className="relative bg-white rounded-2xl border border-slate-200/80 shadow-xl p-6 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Live Semantic Alignment
                    </span>
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Difference Detected
                    </span>
                  </div>

                  {/* Document 1 Card */}
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-500" />
                        <span className="text-xs font-bold text-slate-700">2025 Academic Regulations</span>
                      </div>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-sm bg-rose-100 text-rose-800">
                        Previous Rule
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      "Students must maintain at least <strong className="text-rose-700 line-through">75%</strong>{' '}
                      attendance to qualify for end-semester examinations."
                    </p>
                  </div>

                  {/* Connecting Comparison Indicator */}
                  <div className="flex items-center justify-center -my-2 relative z-10">
                    <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-md">
                      <GitCompare className="w-5 h-5" />
                    </div>
                  </div>

                  {/* Document 2 Card */}
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <FileCheck className="w-4 h-4 text-blue-600" />
                        <span className="text-xs font-bold text-slate-700">2026 Academic Regulations</span>
                      </div>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-sm bg-emerald-100 text-emerald-800">
                        Updated Rule
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      "Students must maintain at least <strong className="text-emerald-700 font-bold">80%</strong>{' '}
                      attendance to qualify for end-semester examinations."
                    </p>
                  </div>

                  {/* Generated Explanation Preview */}
                  <div className="bg-sky-50 rounded-xl p-3 border border-sky-100 text-xs text-sky-900 flex items-start gap-2">
                    <Sparkles className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
                    <div>
                      <strong className="block text-[11px] font-bold text-sky-950 uppercase tracking-wider">
                        Automated Plain-English Insight
                      </strong>
                      <p>The minimum attendance threshold has increased from 75% to 80% (High Priority).</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="py-16 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Built for Deep Academic Rule Intelligence
            </h2>
            <p className="text-sm text-slate-500 mt-2">
              Beyond simple word-level diffs: analyze obligations, detect shifted deadlines, and uncover restrictive clauses.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center mb-3">
                <GitCompare className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">Semantic Comparison</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Aligns sections and sentences across versions even when paragraphs are reordered or reworded in passive voice.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center mb-3">
                <Calendar className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">Deadline & Date Detection</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Pinpoints changed submission dates, grace periods, exam schedules, and registration cutoffs automatically.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center mb-3">
                <Percent className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">Thresholds & Eligibility</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Highlights changes in attendance percentages, credit limits, CGPA criteria, scholarship bounds, and fees.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center mb-3">
                <Scale className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">Grounded Explanations</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Every detected change is explained in clear plain English, strictly grounded in the original source excerpts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4-Step Workflow Section */}
      <section className="py-16 bg-slate-50 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-xl mx-auto mb-12">
            <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">How It Works</span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
              Four Seamless Steps
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: '01',
                title: 'Upload Documents',
                desc: 'Select or drag-and-drop previous and updated policies in PDF, DOCX, or TXT formats.',
                icon: FileText,
              },
              {
                step: '02',
                title: 'NLP Analysis',
                desc: 'Bipartite alignment matches rules, extracts numerical entities, and analyzes modality shifts.',
                icon: Sparkles,
              },
              {
                step: '03',
                title: 'Review Changes',
                desc: 'Filter by priority, inspect side-by-side excerpts, and review plain-English explanations.',
                icon: CheckCircle2,
              },
              {
                step: '04',
                title: 'Export Reports',
                desc: 'Download a formal executive PDF report or export structured records as CSV.',
                icon: Download,
              },
            ].map((s, idx) => {
              const Icon = s.icon;
              return (
                <div key={idx} className="bg-white rounded-xl p-6 border border-slate-200 relative shadow-xs">
                  <span className="text-3xl font-extrabold text-slate-200 block mb-2">{s.step}</span>
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 mb-1">{s.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
};
