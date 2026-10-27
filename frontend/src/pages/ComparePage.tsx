import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  Trash2,
  GitCompare,
  Sparkles,
  AlertCircle,
  Building2,
  Tag,
  FileType,
} from 'lucide-react';
import { api } from '../services/api';
import { LoadingModal } from '../components/LoadingModal';

export const ComparePage: React.FC = () => {
  const navigate = useNavigate();

  // Form State
  const [title, setTitle] = useState('Academic Policy Comparison');
  const [institution, setInstitution] = useState('');
  const [oldVersion, setOldVersion] = useState('2025 Regulations');
  const [newVersion, setNewVersion] = useState('2026 Regulations');

  // Files State
  const [oldFile, setOldFile] = useState<File | null>(null);
  const [newFile, setNewFile] = useState<File | null>(null);
  const [oldPreview, setOldPreview] = useState<string>('');
  const [newPreview, setNewPreview] = useState<string>('');

  // UI State
  const [isComparing, setIsComparing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const oldInputRef = useRef<HTMLInputElement>(null);
  const newInputRef = useRef<HTMLInputElement>(null);

  // File Handlers
  const handleFileSelect = (
    file: File,
    type: 'old' | 'new'
  ) => {
    setErrorMessage(null);
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setErrorMessage(`Unsupported format: ${file.name}. Only PDF, DOCX, and TXT files are accepted.`);
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage(`File ${file.name} exceeds 15MB size limit.`);
      return;
    }

    if (type === 'old') {
      setOldFile(file);
      if (ext === '.txt') {
        const reader = new FileReader();
        reader.onload = (e) => setOldPreview((e.target?.result as string).slice(0, 500));
        reader.readAsText(file);
      } else {
        setOldPreview(`[${ext.toUpperCase().replace('.', '')} Document loaded: ${file.name}]`);
      }
    } else {
      setNewFile(file);
      if (ext === '.txt') {
        const reader = new FileReader();
        reader.onload = (e) => setNewPreview((e.target?.result as string).slice(0, 500));
        reader.readAsText(file);
      } else {
        setNewPreview(`[${ext.toUpperCase().replace('.', '')} Document loaded: ${file.name}]`);
      }
    }
  };

  // Drag and Drop
  const handleDrop = (e: React.DragEvent, type: 'old' | 'new') => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0], type);
    }
  };

  // Load Demo Documents Button
  const handleLoadDemo = async () => {
    setErrorMessage(null);
    setIsComparing(true);
    try {
      const demoResult = await api.getDemoComparison();
      navigate(`/results/${demoResult.id}`);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Failed to load demo comparison.');
      setIsComparing(false);
    }
  };

  // Submit Comparison
  const handleCompare = async () => {
    setErrorMessage(null);

    if (!oldFile || !newFile) {
      setErrorMessage('Please upload both the Old Policy and the New Policy before comparing.');
      return;
    }

    setIsComparing(true);
    try {
      const formData = new FormData();
      formData.append('old_file', oldFile);
      formData.append('new_file', newFile);
      formData.append('title', title.trim() || 'Academic Policy Comparison');
      if (institution.trim()) formData.append('institution', institution.trim());
      formData.append('old_version', oldVersion.trim() || 'Old Version');
      formData.append('new_version', newVersion.trim() || 'New Version');

      const result = await api.compareDocuments(formData);
      navigate(`/results/${result.id}`);
    } catch (err: any) {
      setIsComparing(false);
      const detail = err.response?.data?.detail || err.message || 'An error occurred during comparison.';
      setErrorMessage(detail);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <LoadingModal isOpen={isComparing} />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Document Comparison Workspace
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload two policy versions to detect added, removed, modified, and critical requirement changes.
          </p>
        </div>

        <button
          onClick={handleLoadDemo}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 transition-all cursor-pointer shadow-xs shrink-0"
        >
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Load Demo Documents (Apex University)</span>
        </button>
      </div>

      {/* Metadata Configuration Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs mb-8">
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
          Optional Document Metadata
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Comparison Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Academic Examination Policy"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                Institution / Dept
              </span>
            </label>
            <input
              type="text"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="e.g. Faculty of Engineering"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              <span className="flex items-center gap-1">
                <Tag className="w-3.5 h-3.5 text-rose-500" />
                Previous Version Label
              </span>
            </label>
            <input
              type="text"
              value={oldVersion}
              onChange={(e) => setOldVersion(e.target.value)}
              placeholder="e.g. 2025 Edition"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              <span className="flex items-center gap-1">
                <Tag className="w-3.5 h-3.5 text-emerald-500" />
                Updated Version Label
              </span>
            </label>
            <input
              type="text"
              value={newVersion}
              onChange={(e) => setNewVersion(e.target.value)}
              placeholder="e.g. 2026 Edition"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Error Message Alert */}
      {errorMessage && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <strong className="block font-semibold">Upload or Processing Notice</strong>
            <p className="mt-0.5 leading-relaxed">{errorMessage}</p>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-500 hover:text-rose-700 text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Two-Panel Comparison Upload Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Left Panel: Old Policy */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold text-xs">
                  OLD
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 text-sm">Previous Policy Document</h3>
                  <p className="text-[11px] text-slate-400">{oldVersion}</p>
                </div>
              </div>

              {oldFile && (
                <button
                  onClick={() => {
                    setOldFile(null);
                    setOldPreview('');
                  }}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  title="Remove file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>

            <input
              type="file"
              ref={oldInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0], 'old')}
              accept=".pdf,.docx,.txt"
              className="hidden"
            />

            {!oldFile ? (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => handleDrop(e, 'old')}
                onClick={() => oldInputRef.current?.click()}
                className="border-2 border-dashed border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px]"
              >
                <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mb-3">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-slate-700">Drop previous policy file here</p>
                <p className="text-xs text-slate-400 mt-1">or click to browse your computer</p>
                <div className="flex items-center gap-2 mt-4 text-[11px] text-slate-400">
                  <span>PDF</span> • <span>DOCX</span> • <span>TXT</span> (max 15MB)
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="overflow-hidden">
                    <p className="text-xs font-bold text-slate-800 truncate">{oldFile.name}</p>
                    <p className="text-[11px] text-slate-500">{(oldFile.size / 1024).toFixed(1)} KB • Ready for extraction</p>
                  </div>
                </div>

                {oldPreview && (
                  <div className="bg-slate-50/70 rounded-lg border border-slate-200 p-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      Text Snippet Preview
                    </span>
                    <p className="text-xs text-slate-700 font-mono leading-relaxed max-h-36 overflow-y-auto whitespace-pre-wrap">
                      {oldPreview}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: New Policy */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs">
                  NEW
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 text-sm">Updated Policy Document</h3>
                  <p className="text-[11px] text-slate-400">{newVersion}</p>
                </div>
              </div>

              {newFile && (
                <button
                  onClick={() => {
                    setNewFile(null);
                    setNewPreview('');
                  }}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  title="Remove file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>

            <input
              type="file"
              ref={newInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0], 'new')}
              accept=".pdf,.docx,.txt"
              className="hidden"
            />

            {!newFile ? (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => handleDrop(e, 'new')}
                onClick={() => newInputRef.current?.click()}
                className="border-2 border-dashed border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px]"
              >
                <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mb-3">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-slate-700">Drop updated policy file here</p>
                <p className="text-xs text-slate-400 mt-1">or click to browse your computer</p>
                <div className="flex items-center gap-2 mt-4 text-[11px] text-slate-400">
                  <span>PDF</span> • <span>DOCX</span> • <span>TXT</span> (max 15MB)
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="overflow-hidden">
                    <p className="text-xs font-bold text-slate-800 truncate">{newFile.name}</p>
                    <p className="text-[11px] text-slate-500">{(newFile.size / 1024).toFixed(1)} KB • Ready for extraction</p>
                  </div>
                </div>

                {newPreview && (
                  <div className="bg-slate-50/70 rounded-lg border border-slate-200 p-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      Text Snippet Preview
                    </span>
                    <p className="text-xs text-slate-700 font-mono leading-relaxed max-h-36 overflow-y-auto whitespace-pre-wrap">
                      {newPreview}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Compare Policies Action Button */}
      <div className="text-center pt-2">
        <button
          onClick={handleCompare}
          disabled={!oldFile || !newFile || isComparing}
          className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-blue-500/20 text-base transition-all cursor-pointer"
        >
          <GitCompare className="w-5 h-5" />
          <span>Compare Policies & Detect Changes</span>
        </button>
      </div>
    </div>
  );
};
