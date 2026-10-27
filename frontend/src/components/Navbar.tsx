import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { GitCompare, FileText, History, Info, Cpu } from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [engineInfo, setEngineInfo] = useState<{ nlp_engine: string; is_fallback: boolean } | null>(null);

  useEffect(() => {
    api.getHealth()
      .then((data) => setEngineInfo({ nlp_engine: data.nlp_engine, is_fallback: data.is_fallback }))
      .catch(() => setEngineInfo(null));
  }, []);

  const navLinks = [
    { to: '/', label: 'Home', icon: FileText },
    { to: '/compare', label: 'Compare Documents', icon: GitCompare },
    { to: '/history', label: 'History', icon: History },
    { to: '/about', label: 'Methodology & Benchmark', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-linear-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <GitCompare className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg text-slate-900 tracking-tight">PolicyDiff</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-sm bg-blue-100 text-blue-700 border border-blue-200">
                NLP v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium leading-none">Semantic Policy Change Detector</p>
          </div>
        </Link>

        {/* Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Active Engine Badge */}
        <div className="flex items-center gap-3">
          {engineInfo ? (
            <div
              className={`hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${
                engineInfo.is_fallback
                  ? 'bg-amber-50 text-amber-800 border-amber-200'
                  : 'bg-emerald-50 text-emerald-800 border-emerald-200'
              }`}
              title={`Active NLP engine: ${engineInfo.nlp_engine}`}
            >
              <Cpu className="w-3.5 h-3.5 text-current" />
              <span>{engineInfo.is_fallback ? 'Fallback Mode: TF-IDF + Fuzzy' : 'Transformer: MiniLM-L6'}</span>
            </div>
          ) : (
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-50 text-slate-600 border border-slate-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Backend Ready</span>
            </div>
          )}

          <Link
            to="/compare"
            className="hidden sm:inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs hover:shadow-md transition-all"
          >
            New Comparison
          </Link>
        </div>
      </div>
    </header>
  );
};
