import React, { useState } from 'react';
import { PolicyChange } from '../types';
import { DiffBadge } from './DiffBadge';
import { PriorityBadge } from './PriorityBadge';
import {
  Calendar,
  Percent,
  DollarSign,
  AlertCircle,
  FileCheck2,
  Check,
  ChevronRight,
  ShieldAlert,
  ArrowRight,
  Hash,
  Scale,
} from 'lucide-react';

interface Props {
  change: PolicyChange;
  oldVersionLabel?: string;
  newVersionLabel?: string;
  onToggleReview: (changeId: string, currentStatus: boolean) => Promise<void>;
}

export const ChangeCard: React.FC<Props> = ({
  change,
  oldVersionLabel = 'Old Policy',
  newVersionLabel = 'New Policy',
  onToggleReview,
}) => {
  const [isUpdating, setIsUpdating] = useState(false);

  const handleReviewToggle = async () => {
    setIsUpdating(true);
    try {
      await onToggleReview(change.id, change.is_reviewed);
    } finally {
      setIsUpdating(false);
    }
  };

  // Border accents by change type
  const borderClass =
    change.change_type === 'ADDED'
      ? 'border-emerald-200 hover:border-emerald-400'
      : change.change_type === 'REMOVED'
      ? 'border-rose-200 hover:border-rose-400'
      : change.change_type === 'MODIFIED'
      ? 'border-amber-200 hover:border-amber-400'
      : 'border-slate-200 hover:border-slate-300';

  return (
    <div
      className={`bg-white rounded-xl border ${borderClass} shadow-xs hover:shadow-md transition-all p-5 mb-4 relative overflow-hidden`}
    >
      {/* Top Header Row */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3 pb-3 border-b border-slate-100">
        <div className="flex flex-wrap items-center gap-2">
          <DiffBadge type={change.change_type} />
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            {change.category}
          </span>
          <PriorityBadge priority={change.priority} />
        </div>

        <div className="flex items-center gap-3">
          {/* Similarity & Confidence Metric */}
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span title="Semantic & Lexical Alignment Score">
              Similarity: <strong className="text-slate-800 font-semibold">{Math.round(change.similarity_score * 100)}%</strong>
            </span>
            <span className="text-slate-300">•</span>
            <span title="Alignment Confidence">
              Confidence: <strong className="text-slate-800 font-semibold">{Math.round(change.alignment_confidence * 100)}%</strong>
            </span>
          </div>

          {/* Mark as Reviewed Button */}
          <button
            onClick={handleReviewToggle}
            disabled={isUpdating}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
              change.is_reviewed
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100'
                : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
            }`}
          >
            {change.is_reviewed ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                Reviewed
              </>
            ) : (
              <>
                <FileCheck2 className="w-3.5 h-3.5 text-slate-400" />
                Mark Reviewed
              </>
            )}
          </button>
        </div>
      </div>

      {/* Plain-English Explanation Banner */}
      <div className="bg-sky-50/70 border border-sky-150 rounded-lg p-3.5 mb-4 text-sm text-sky-950 flex items-start gap-2.5">
        <div className="p-1 rounded-md bg-sky-100 text-sky-700 shrink-0 mt-0.5">
          <ChevronRight className="w-4 h-4" />
        </div>
        <div>
          <span className="font-semibold text-sky-900 block text-xs uppercase tracking-wider mb-0.5">
            Plain-English Explanation
          </span>
          <p className="leading-relaxed">{change.explanation}</p>
        </div>
      </div>

      {/* Side-by-Side Excerpt Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-3">
        {/* Old Policy Panel */}
        <div className="bg-slate-50/80 rounded-lg border border-slate-200/80 p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2 font-medium">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-400" />
                {oldVersionLabel}
              </span>
              {change.old_section && (
                <span className="text-[11px] truncate max-w-[200px]" title={change.old_section}>
                  {change.old_section} {change.old_page ? `(p. ${change.old_page})` : ''}
                </span>
              )}
            </div>
            <p className="text-sm text-slate-800 leading-relaxed font-normal">
              {change.old_text ? (
                change.old_text
              ) : (
                <span className="italic text-slate-400 font-light">— No previous provision (Newly introduced rule) —</span>
              )}
            </p>
          </div>
        </div>

        {/* New Policy Panel */}
        <div className="bg-slate-50/80 rounded-lg border border-slate-200/80 p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2 font-medium">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                {newVersionLabel}
              </span>
              {change.new_section && (
                <span className="text-[11px] truncate max-w-[200px]" title={change.new_section}>
                  {change.new_section} {change.new_page ? `(p. ${change.new_page})` : ''}
                </span>
              )}
            </div>
            <p className="text-sm text-slate-800 leading-relaxed font-normal">
              {change.new_text ? (
                change.new_text
              ) : (
                <span className="italic text-slate-400 font-light">— Provision rescinded (Removed from updated policy) —</span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Entity & Threshold Differences Pills */}
      {change.entities_diff && change.entities_diff.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 mb-3 pt-1">
          <span className="text-xs font-semibold text-slate-600">Extracted Discrepancies:</span>
          {change.entities_diff.map((item, idx) => {
            let Icon = AlertCircle;
            if (item.entity_type === 'percentage') Icon = Percent;
            if (item.entity_type === 'date') Icon = Calendar;
            if (item.entity_type === 'monetary') Icon = DollarSign;
            if (item.entity_type === 'modality' || item.entity_type === 'prohibition') Icon = Scale;

            return (
              <div
                key={idx}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs bg-slate-100 text-slate-700 border border-slate-200"
                title={item.details}
              >
                <Icon className="w-3.5 h-3.5 text-blue-600" />
                <span className="capitalize font-medium text-slate-500">{item.entity_type}:</span>
                <span className="text-rose-600 line-through font-mono">{item.old_value || 'None'}</span>
                <ArrowRight className="w-3 h-3 text-slate-400" />
                <span className="text-emerald-700 font-bold font-mono">{item.new_value || 'None'}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Detection Reason & Priority Rationale Footer */}
      {(change.reason || change.priority_rationale) && (
        <div className="mt-2 pt-2 border-t border-slate-100 text-xs text-slate-500 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          {change.reason && (
            <p className="truncate">
              <strong className="text-slate-600 font-medium">Detection Factor:</strong> {change.reason}
            </p>
          )}
          {change.priority_rationale && (
            <p className="shrink-0 text-slate-500 italic">
              <strong>Rationale:</strong> {change.priority_rationale}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
