import React, { useState } from "react";
import UploadCard from "../components/UploadCard";
import ImportPreview from "../components/ImportPreview";
import { api } from "../api/client";
import type { ImportPreview as ImportPreviewType, ImportSummary } from "../api/types";
import { CheckCircle2, AlertCircle, RefreshCcw } from "lucide-react";
import { Link } from "react-router-dom";

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [bankOverride, setBankOverride] = useState("auto");
  const [preview, setPreview] = useState<ImportPreviewType | null>(null);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (selectedFile: File, override: string) => {
    setFile(selectedFile);
    setBankOverride(override);
    setError(null);
    setSummary(null);
    setIsLoading(true);

    try {
      const result = await api.previewImport(selectedFile, override);
      setPreview(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to preview file.");
      setFile(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);

    try {
      const result = await api.confirmImport(file, bankOverride);
      setSummary(result);
      setPreview(null);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to import transactions.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setPreview(null);
    setFile(null);
    setError(null);
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setSummary(null);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Import Data
          </h1>
          <p className="text-gray-500 mt-2">
            Add transactions from your bank statements to LedgerMind Local.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 text-red-700">
          <AlertCircle size={20} className="flex-shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {!preview && !summary && (
        <UploadCard onFileSelect={handleFileSelect} isLoading={isLoading} />
      )}

      {preview && (
        <ImportPreview
          preview={preview}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
          isLoading={isLoading}
        />
      )}

      {summary && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle2 size={32} className="text-green-600" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Import Complete!</h2>
          <p className="text-gray-500 mt-2">
            Successfully processed <strong>{summary.filename}</strong>
          </p>

          <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
              <p className="text-xs font-semibold text-gray-400 uppercase">
                Imported
              </p>
              <p className="text-xl font-bold text-gray-900">
                {summary.imported_count}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
              <p className="text-xs font-semibold text-gray-400 uppercase">
                Duplicates
              </p>
              <p className="text-xl font-bold text-gray-900">
                {summary.duplicate_count}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-100 col-span-2">
              <p className="text-xs font-semibold text-gray-400 uppercase">
                Date Range
              </p>
              <p className="text-sm font-bold text-gray-900 mt-1">
                {summary.date_min} to {summary.date_max}
              </p>
            </div>
          </div>

          <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/transactions"
              className="px-6 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700 transition-colors"
            >
              View Transactions
            </Link>
            <button
              onClick={reset}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCcw size={18} />
              Import Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
