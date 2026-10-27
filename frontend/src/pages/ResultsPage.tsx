import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileText,
  Download,
  Filter,
  Search,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Share2,
  Sparkles,
  BarChart3,
  Check,
  RefreshCw,
  PlusCircle,
  MinusCircle,
  Clock,
  Layers,
  Cpu,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import { api } from '../services/api';
import { ComparisonResponse, PolicyChange } from '../types';
import { ChangeCard } from '../components/ChangeCard';

export const ResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedPriority, setSelectedPriority] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [reviewedOnly, setReviewedOnly] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api.getComparison(id)
      .then((data) => {
        setComparison(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to retrieve comparison record.');
        setLoading(false);
      });
  }, [id]);

  const handleToggleReview = async (changeId: string, currentStatus: boolean) => {
    try {
      await api.updateReviewStatus(changeId, !currentStatus);
      if (comparison) {
        setComparison({
          ...comparison,
          changes: comparison.changes.map((c) =>
            c.id === changeId ? { ...c, is_reviewed: !currentStatus } : c
          ),
        });
      }
    } catch (err) {
      console.error('Failed to update review status:', err);
    }
  };

  // Filtered Changes Memo
  const filteredChanges = useMemo(() => {
    if (!comparison) return [];

    return comparison.changes.filter((c) => {
      // Type filter
      if (selectedType !== 'ALL' && c.change_type !== selectedType) return false;

      // Priority filter
      if (selectedPriority !== 'ALL') {
        if (selectedPriority === 'CRITICAL_HIGH') {
          if (c.priority !== 'Critical' && c.priority !== 'High') return false;
        } else if (c.priority !== selectedPriority) {
          return false;
        }
      }

      // Category filter
      if (selectedCategory !== 'ALL' && c.category !== selectedCategory) return false;

      // Review filter
      if (reviewedOnly && !c.is_reviewed) return false;

      // Search query (matches old text, new text, explanation, reason, category)
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const haystack = `${c.old_text || ''} ${c.new_text || ''} ${c.explanation} ${c.reason || ''} ${c.category}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }

      return true;
    });
  }, [comparison, selectedType, selectedPriority, selectedCategory, reviewedOnly, searchQuery]);

  // Dynamic Chart Data
  const categoryChartData = useMemo(() => {
    if (!comparison) return [];
    const counts: Record<string, number> = {};

    comparison.changes.forEach((c) => {
      if (c.change_type !== 'UNCHANGED') {
        const cat = c.category.replace(' & ', '\n');
        counts[cat] = (counts[cat] || 0) + 1;
      }
    });

    return Object.entries(counts).map(([name, count]) => ({
      name,
      count,
    }));
  }, [comparison]);

  const typeChartData = useMemo(() => {
    if (!comparison) return [];
    return [
      { name: 'Added', value: comparison.summary.added_count, color: '#10b981' },
      { name: 'Modified', value: comparison.summary.modified_count, color: '#f59e0b' },
      { name: 'Removed', value: comparison.summary.removed_count, color: '#ef4444' },
      { name: 'Unchanged', value: comparison.summary.unchanged_count, color: '#94a3b8' },
    ].filter((item) => item.value > 0);
  }, [comparison]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center">
        <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 animate-spin">
          <RefreshCw className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-slate-800">Loading Comparison Results</h2>
        <p className="text-xs text-slate-500 mt-1">Retrieving persistent records from SQLite...</p>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-slate-800">Comparison Record Not Found</h2>
        <p className="text-xs text-slate-500 mt-1 mb-6">{error || 'This comparison ID does not exist in local storage.'}</p>
        <Link
          to="/compare"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Workspace</span>
        </Link>
      </div>
    );
  }

  const { summary } = comparison;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <Link
            to="/compare"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-blue-600 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Comparison Workspace</span>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {comparison.title}
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
            {comparison.institution && (
              <span className="font-medium text-slate-700">{comparison.institution}</span>
            )}
            <span>•</span>
            <span>
              Comparing <strong className="text-slate-700 font-semibold">{comparison.old_version}</strong> ({comparison.old_filename}) vs{' '}
              <strong className="text-slate-700 font-semibold">{comparison.new_version}</strong> ({comparison.new_filename})
            </span>
            <span>•</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              <Cpu className="w-3 h-3 text-blue-600" />
              {comparison.nlp_engine}
            </span>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2.5 shrink-0">
          <a
            href={api.getPdfReportUrl(comparison.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 shadow-xs hover:shadow-md transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>

          <a
            href={api.getCsvReportUrl(comparison.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-xs transition-all cursor-pointer"
          >
            <Download className="w-4 h-4 text-slate-500" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* KPI Cards (Calculated dynamically) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-xs font-medium text-slate-500 block mb-1">Total Detected Changes</span>
          <span className="text-2xl font-extrabold text-slate-900">{summary.total_changes}</span>
          <span className="text-[11px] text-slate-400 block mt-1">Excludes unchanged clauses</span>
        </div>

        <div className="bg-white rounded-xl border border-emerald-200 p-4 shadow-xs bg-emerald-50/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-emerald-800">Added Rules</span>
            <PlusCircle className="w-4 h-4 text-emerald-600" />
          </div>
          <span className="text-2xl font-extrabold text-emerald-700 mt-1 block">{summary.added_count}</span>
          <span className="text-[11px] text-emerald-600/80 block mt-1">Newly introduced provisions</span>
        </div>

        <div className="bg-white rounded-xl border border-rose-200 p-4 shadow-xs bg-rose-50/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-800">Removed Rules</span>
            <MinusCircle className="w-4 h-4 text-rose-600" />
          </div>
          <span className="text-2xl font-extrabold text-rose-700 mt-1 block">{summary.removed_count}</span>
          <span className="text-[11px] text-rose-600/80 block mt-1">Rescinded conditions</span>
        </div>

        <div className="bg-white rounded-xl border border-amber-200 p-4 shadow-xs bg-amber-50/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-amber-900">Modified Rules</span>
            <RefreshCw className="w-4 h-4 text-amber-600" />
          </div>
          <span className="text-2xl font-extrabold text-amber-800 mt-1 block">{summary.modified_count}</span>
          <span className="text-[11px] text-amber-700/80 block mt-1">Thresholds & rephrased</span>
        </div>

        <div className="bg-white rounded-xl border border-red-300 p-4 shadow-xs bg-red-50/30">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-red-900">Critical / High Priority</span>
            <AlertTriangle className="w-4 h-4 text-red-600" />
          </div>
          <span className="text-2xl font-extrabold text-red-700 mt-1 block">{summary.high_priority_count}</span>
          <span className="text-[11px] text-red-600/80 block mt-1">Requires immediate attention</span>
        </div>
      </div>

      {/* Dynamic Distribution Chart & Type Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Category Distribution Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-800">Changes by Policy Category</h2>
              <p className="text-xs text-slate-400">Distribution of modifications across academic domains</p>
            </div>
            <BarChart3 className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-56 w-full">
            {categoryChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No categorical variations detected.
              </div>
            )}
          </div>
        </div>

        {/* Change Breakdown Pie Chart */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-sm font-bold text-slate-800">Change Composition</h2>
              <p className="text-xs text-slate-400">Proportions of rule types</p>
            </div>
            <Layers className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-44 w-full flex items-center justify-center">
            {typeChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={typeChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={65}
                    paddingAngle={3}
                  >
                    {typeChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-400">No rule data available</div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-100">
            {typeChartData.map((item, idx) => (
              <div key={idx} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-slate-600">{item.name}:</span>
                <strong className="text-slate-900">{item.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs mb-6">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          {/* Search Box */}
          <div className="md:col-span-4 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search changes, dates, percentages..."
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Change Type Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full px-2.5 py-2 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 text-slate-700 font-medium"
            >
              <option value="ALL">All Types</option>
              <option value="MODIFIED">Modified Only</option>
              <option value="ADDED">Added Only</option>
              <option value="REMOVED">Removed Only</option>
              <option value="UNCHANGED">Unchanged Only</option>
            </select>
          </div>

          {/* Priority Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="w-full px-2.5 py-2 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 text-slate-700 font-medium"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL_HIGH">Critical & High</option>
              <option value="Critical">Critical Only</option>
              <option value="High">High Only</option>
              <option value="Medium">Medium Only</option>
              <option value="Low">Low Only</option>
            </select>
          </div>

          {/* Category Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-2.5 py-2 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500 text-slate-700 font-medium"
            >
              <option value="ALL">All Categories</option>
              <option value="Attendance & Leaves">Attendance & Leaves</option>
              <option value="Examinations & Grading">Examinations & Grading</option>
              <option value="Deadlines & Schedules">Deadlines & Schedules</option>
              <option value="Financial & Fees">Financial & Fees</option>
              <option value="Eligibility & Admission">Eligibility & Admission</option>
              <option value="Administrative & Governance">Administrative</option>
            </select>
          </div>

          {/* Reviewed Toggle */}
          <div className="md:col-span-2 flex items-center justify-end">
            <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-600">
              <input
                type="checkbox"
                checked={reviewedOnly}
                onChange={(e) => setReviewedOnly(e.target.checked)}
                className="w-4 h-4 rounded-sm text-blue-600 focus:ring-blue-500 border-slate-300"
              />
              <span>Reviewed Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Changes Count Banner */}
      <div className="flex items-center justify-between text-xs text-slate-500 mb-4 px-1">
        <span>
          Showing <strong>{filteredChanges.length}</strong> of{' '}
          <strong>{comparison.changes.length}</strong> total extracted rules
        </span>
        {(selectedType !== 'ALL' || selectedPriority !== 'ALL' || selectedCategory !== 'ALL' || searchQuery || reviewedOnly) && (
          <button
            onClick={() => {
              setSelectedType('ALL');
              setSelectedPriority('ALL');
              setSelectedCategory('ALL');
              setSearchQuery('');
              setReviewedOnly(false);
            }}
            className="text-blue-600 hover:underline font-semibold"
          >
            Clear All Filters
          </button>
        )}
      </div>

      {/* Change Cards Explorer List */}
      {filteredChanges.length > 0 ? (
        <div className="space-y-4">
          {filteredChanges.map((change) => (
            <ChangeCard
              key={change.id}
              change={change}
              oldVersionLabel={comparison.old_version}
              newVersionLabel={comparison.new_version}
              onToggleReview={handleToggleReview}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-xs">
          <CheckCircle2 className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No matching changes found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Try adjusting your search query or relaxing your filter selections to see other clauses.
          </p>
        </div>
      )}
    </div>
  );
};
