import React from "react";
import type { ImportPreview as ImportPreviewType } from "../api/types";
import { CheckCircle, AlertTriangle, Info, ArrowRight } from "lucide-react";

interface ImportPreviewProps {
  preview: ImportPreviewType;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading: boolean;
}

const ImportPreview: React.FC<ImportPreviewProps> = ({
  preview,
  onConfirm,
  onCancel,
  isLoading,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Import Preview</h2>
          <p className="text-sm text-gray-500">
            Verify the detected format and data before importing.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
          >
            {isLoading ? "Importing..." : "Confirm Import"}
            {!isLoading && <ArrowRight size={16} />}
          </button>
        </div>
      </div>

      <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Detected Bank
          </span>
          <div className="mt-1 flex items-center gap-2">
            <span className="text-xl font-bold text-gray-900">
              {preview.detected_bank}
            </span>
            {preview.confidence > 0.8 ? (
              <CheckCircle size={18} className="text-green-500" />
            ) : (
              <Info size={18} className="text-blue-500" />
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Confidence: {(preview.confidence * 100).toFixed(0)}%
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Transactions Found
          </span>
          <div className="mt-1 text-xl font-bold text-gray-900">
            {preview.row_count}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Rows in {preview.filename}
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Headers Detected
          </span>
          <div className="mt-1 flex flex-wrap gap-1">
            {preview.headers.length > 0 ? (
              preview.headers.slice(0, 3).map((h, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-mono"
                >
                  {h}
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-400">No headers found (Raw data)</span>
            )}
            {preview.headers.length > 3 && (
              <span className="text-xs text-gray-400">+{preview.headers.length - 3} more</span>
            )}
          </div>
        </div>
      </div>

      {preview.warnings.length > 0 && (
        <div className="px-6 pb-6">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3">
            <AlertTriangle className="text-amber-500 flex-shrink-0" size={20} />
            <div>
              <h4 className="text-sm font-semibold text-amber-800">Warnings</h4>
              <ul className="mt-1 text-sm text-amber-700 list-disc list-inside">
                {preview.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="px-6 pb-6 overflow-x-auto">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">
          Preview (First 5 Rows)
        </h3>
        <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
          <thead className="bg-gray-50">
            <tr>
              {preview.headers.length > 0
                ? preview.headers.map((h, i) => (
                    <th
                      key={i}
                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  ))
                : Object.keys(preview.preview_rows[0] || {}).map((k, i) => (
                    <th
                      key={i}
                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Col {k}
                    </th>
                  ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {preview.preview_rows.map((row, i) => (
              <tr key={i}>
                {preview.headers.length > 0
                  ? preview.headers.map((h, j) => (
                      <td
                        key={j}
                        className="px-3 py-2 whitespace-nowrap text-xs text-gray-600 font-mono"
                      >
                        {String(row[h] ?? "")}
                      </td>
                    ))
                  : Object.values(row).map((v, j) => (
                      <td
                        key={j}
                        className="px-3 py-2 whitespace-nowrap text-xs text-gray-600 font-mono"
                      >
                        {String(v ?? "")}
                      </td>
                    ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ImportPreview;
