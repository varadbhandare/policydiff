import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  History,
  Trash2,
  ExternalLink,
  Download,
  AlertTriangle,
  Calendar,
  Layers,
  ArrowRight,
  GitCompare,
  Plus,
} from 'lucide-react';
import { api } from '../services/api';
import { ComparisonListItem } from '../types';

export const HistoryPage: React.FC = () => {
  const [comparisons, setComparisons] = useState<ComparisonListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const fetchComparisons = () => {
    setLoading(true);
    api.getComparisons()
      .then((data) => {
        setComparisons(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch comparisons:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchComparisons();
  }, []);

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await api.deleteComparison(id);
      setComparisons((prev) => prev.filter((c) => c.id !== id));
      setConfirmDeleteId(null);
    } catch (err) {
      console.error('Failed to delete comparison:', err);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Comparison History
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse and retrieve previous policy analysis sessions persisted in SQLite.
          </p>
        </div>

        <Link
          to="/compare"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-xs hover:shadow-md transition-all self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>New Comparison</span>
        </Link>
      </div>

      {loading ? (
        <div className="p-16 text-center">
          <div className="w-10 h-10 rounded-full border-2 border-blue-600 border-t-transparent animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-500">Loading stored comparison history...</p>
        </div>
      ) : comparisons.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-xs">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4">
            <History className="w-6 h-6" />
          </div>
          <h2 className="text-base font-bold text-slate-800">No comparison history yet</h2>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-6">
            Compare two versions of an academic regulation or run the demo to see past reports saved here.
          </p>
          <Link
            to="/compare"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-xs"
          >
            <GitCompare className="w-4 h-4" />
            <span>Launch Document Comparison</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {comparisons.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-xl border border-slate-200 hover:border-slate-300 p-5 shadow-xs transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                  {item.institution && (
                    <span className="text-xs px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium">
                      {item.institution}
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    {new Date(item.created_at).toLocaleDateString(undefined, {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                  <span>•</span>
                  <span>
                    <strong className="text-slate-700">{item.old_filename}</strong> ({item.old_version}) vs{' '}
                    <strong className="text-slate-700">{item.new_filename}</strong> ({item.new_version})
                  </span>
                </div>

                {/* Metrics Breakdown */}
                <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                  <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-semibold border border-blue-150">
                    {item.total_changes} Total Changes
                  </span>
                  {item.high_priority_count > 0 && (
                    <span className="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 font-semibold border border-rose-200 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3 text-rose-600" />
                      {item.high_priority_count} High/Critical
                    </span>
                  )}
                  <span className="text-slate-400">
                    ({item.added_count} added, {item.modified_count} modified, {item.removed_count} removed)
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                <Link
                  to={`/results/${item.id}`}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
                >
                  <span>Open Results</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>

                <a
                  href={api.getPdfReportUrl(item.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
                  title="Download PDF Report"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">PDF</span>
                </a>

                {confirmDeleteId === item.id ? (
                  <div className="flex items-center gap-1.5 bg-rose-50 p-1 rounded-lg border border-rose-200">
                    <span className="text-[11px] font-bold text-rose-700 px-1">Confirm delete?</span>
                    <button
                      onClick={() => handleDelete(item.id)}
                      disabled={deletingId === item.id}
                      className="px-2 py-1 rounded-md bg-rose-600 text-white text-[11px] font-bold hover:bg-rose-700 disabled:opacity-50 cursor-pointer"
                    >
                      Delete
                    </button>
                    <button
                      onClick={() => setConfirmDeleteId(null)}
                      className="px-2 py-1 rounded-md bg-slate-200 text-slate-700 text-[11px] font-bold hover:bg-slate-300 cursor-pointer"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmDeleteId(item.id)}
                    className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                    title="Delete record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
