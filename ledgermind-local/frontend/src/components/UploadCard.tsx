import React, { useRef, useState } from "react";
import { Upload, AlertCircle, Loader2 } from "lucide-react";

interface UploadCardProps {
  onFileSelect: (file: File, bankOverride: string) => void;
  isLoading: boolean;
}

const UploadCard: React.FC<UploadCardProps> = ({ onFileSelect, isLoading }) => {
  const [bankOverride, setBankOverride] = useState("auto");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0], bankOverride);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0], bankOverride);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Upload Statements</h2>
        <p className="text-gray-500 mt-1">
          Select your bank statement file (CSV, XLS, or XLSX).
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="md:col-span-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bank Type (Optional Override)
          </label>
          <select
            value={bankOverride}
            onChange={(e) => setBankOverride(e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          >
            <option value="auto">Auto-detect (Recommended)</option>
            <option value="Monzo">Monzo</option>
            <option value="HSBC">HSBC (Minimal)</option>
          </select>
        </div>
      </div>

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
          dragActive
            ? "border-indigo-500 bg-indigo-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".csv,.xls,.xlsx"
          onChange={handleChange}
        />

        {isLoading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="h-10 w-10 text-indigo-500 animate-spin" />
            <p className="mt-2 text-sm text-gray-600 font-medium">
              Analysing file...
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="bg-indigo-100 p-3 rounded-full mb-4">
              <Upload className="h-6 w-6 text-indigo-600" />
            </div>
            <p className="text-base font-medium text-gray-900">
              Click to upload or drag and drop
            </p>
            <p className="text-sm text-gray-500 mt-1">
              CSV, XLS, or XLSX up to 10MB
            </p>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-start gap-2 p-3 bg-blue-50 rounded-md text-blue-700 text-sm">
        <AlertCircle size={18} className="flex-shrink-0" />
        <p>
          Your data never leaves your machine. Processing is done by the local
          LedgerMind backend.
        </p>
      </div>
    </div>
  );
};

export default UploadCard;
