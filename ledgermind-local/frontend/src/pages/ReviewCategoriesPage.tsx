import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import type { CategorySuggestion } from "../api/types";
import { Check, X, Edit2, Loader2, AlertCircle, RefreshCw, Info } from "lucide-react";

const ReviewCategoriesPage: React.FC = () => {
  const [suggestions, setSuggestions] = useState<CategorySuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<{
    merchant: string;
    category: string;
    subcategory: string;
    applyAll: boolean;
  }>({ merchant: "", category: "", subcategory: "", applyAll: true });

  const fetchSuggestions = async () => {
    setIsLoading(true);
    try {
      const data = await api.getCategorySuggestions({ status: "pending" });
      setSuggestions(data);
      setError(null);
    } catch (err) {
      setError("Failed to load suggestions. Make sure the backend is running.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await api.generateCategorySuggestions();
      await fetchSuggestions();
    } catch (err) {
      setError("Failed to generate suggestions.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await api.approveCategorySuggestion(id, true);
      setSuggestions(suggestions.filter((s) => s.id !== id));
    } catch (err) {
      setError("Failed to approve suggestion.");
    }
  };

  const handleReject = async (id: string) => {
    try {
      await api.rejectCategorySuggestion(id);
      setSuggestions(suggestions.filter((s) => s.id !== id));
    } catch (err) {
      setError("Failed to reject suggestion.");
    }
  };

  const startEdit = (s: CategorySuggestion) => {
    setEditingId(s.id);
    setEditValues({
      merchant: s.suggested_merchant || "",
      category: s.suggested_category || "",
      subcategory: s.suggested_subcategory || "",
      applyAll: true,
    });
  };

  const handleEditSubmit = async (id: string) => {
    try {
      await api.editCategorySuggestion(id, {
        suggested_merchant: editValues.merchant,
        suggested_category: editValues.category,
        suggested_subcategory: editValues.subcategory,
        apply_to_matching: editValues.applyAll,
      });
      setSuggestions(suggestions.filter((s) => s.id !== id));
      setEditingId(null);
    } catch (err) {
      setError("Failed to save edit.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Review Categories</h1>
          <p className="text-gray-500">
            Approve or edit AI-suggested categories for your transactions.
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {isGenerating ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <RefreshCw size={18} />
          )}
          Generate Suggestions
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 flex items-start gap-3">
          <AlertCircle className="text-red-400 flex-shrink-0" size={20} />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="animate-spin text-indigo-600" size={40} />
        </div>
      ) : suggestions.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Check className="mx-auto text-green-500 mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-900">All caught up!</h3>
          <p className="text-gray-500 mt-2">
            No pending category suggestions. Click "Generate Suggestions" to find more.
          </p>
        </div>
      ) : (
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Raw Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Suggested Merchant
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Suggested Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {suggestions.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                    {s.merchant_text}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {editingId === s.id ? (
                      <input
                        type="text"
                        value={editValues.merchant}
                        onChange={(e) =>
                          setEditValues({ ...editValues, merchant: e.target.value })
                        }
                        className="border border-gray-300 rounded px-2 py-1 w-full"
                      />
                    ) : (
                      s.suggested_merchant || (
                        <span className="italic text-gray-400">Unknown</span>
                      )
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {editingId === s.id ? (
                      <input
                        type="text"
                        value={editValues.category}
                        onChange={(e) =>
                          setEditValues({ ...editValues, category: e.target.value })
                        }
                        className="border border-gray-300 rounded px-2 py-1 w-full"
                      />
                    ) : (
                      s.suggested_category || (
                        <span className="italic text-gray-400">Uncategorized</span>
                      )
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full ${
                            s.confidence > 0.8
                              ? "bg-green-500"
                              : s.confidence > 0.5
                              ? "bg-yellow-500"
                              : "bg-red-500"
                          }`}
                          style={{ width: `${s.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span>{(s.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {editingId === s.id ? (
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEditSubmit(s.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Save"
                        >
                          <Check size={20} />
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="text-gray-600 hover:text-gray-900"
                          title="Cancel"
                        >
                          <X size={20} />
                        </button>
                      </div>
                    ) : (
                      <div className="flex justify-end gap-3">
                        <button
                          onClick={() => handleApprove(s.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Approve"
                        >
                          <Check size={20} />
                        </button>
                        <button
                          onClick={() => handleReject(s.id)}
                          className="text-red-600 hover:text-red-900"
                          title="Reject"
                        >
                          <X size={20} />
                        </button>
                        <button
                          onClick={() => startEdit(s)}
                          className="text-indigo-600 hover:text-indigo-900"
                          title="Edit"
                        >
                          <Edit2 size={20} />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Info className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              <strong>Human-in-the-loop:</strong> Suggestions are generated using
              semantic matching against your existing transactions. Approving a
              suggestion creates a deterministic rule that will be automatically
              applied to future imports.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewCategoriesPage;
