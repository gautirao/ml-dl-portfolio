import React, { useState } from "react";
import type { Transaction } from "../api/types";
import { ArrowUpRight, ArrowDownLeft, Landmark, Edit2, RotateCcw, Check, X as CloseIcon } from "lucide-react";
import { api } from "../api/client";

interface TransactionTableProps {
  transactions: Transaction[];
  isLoading: boolean;
  onRefresh?: () => void;
}

const CATEGORIES = [
  "Groceries", "Dining", "Shopping", "Transport", "Bills", 
  "Entertainment", "Personal Care", "General", "Income", "Transfers", "Fuel"
];

const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  isLoading,
  onRefresh,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [newCategory, setNewCategory] = useState("");
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleStartEdit = (t: Transaction) => {
    setEditingId(t.id);
    setNewCategory(t.effective_category || t.category || "");
    setReason("");
  };

  const handleCancelEdit = () => {
    setEditingId(null);
  };

  const handleApplyOverride = async (id: string) => {
    setIsSubmitting(true);
    try {
      await api.applyCategoryOverride(id, {
        new_category: newCategory,
        reason: reason || undefined
      });
      setEditingId(null);
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error("Failed to apply override:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemoveOverride = async (id: string) => {
    if (!confirm("Are you sure you want to remove the category override?")) return;
    try {
      await api.removeCategoryOverride(id);
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error("Failed to remove override:", error);
    }
  };

  const getSourceBadgeColor = (source?: string) => {
    switch (source) {
      case "override": return "bg-purple-100 text-purple-700 border-purple-200";
      case "merchant_rule": return "bg-blue-100 text-blue-700 border-blue-200";
      case "imported": return "bg-gray-100 text-gray-700 border-gray-200";
      case "uncategorised": return "bg-yellow-100 text-yellow-700 border-yellow-200";
      default: return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-20 flex flex-col items-center justify-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-500 font-medium">Loading transactions...</p>
        </div>
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-20 flex flex-col items-center justify-center text-center">
          <Landmark className="h-12 w-12 text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">No transactions found</h3>
          <p className="text-gray-500 max-w-xs mx-auto">
            Try adjusting your filters or upload a bank statement to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Merchant / Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Bank
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {transactions.map((t) => (
              <tr key={t.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {t.transaction_date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-gray-900">
                      {t.merchant || "Unknown Merchant"}
                    </span>
                    <span className="text-xs text-gray-500 truncate max-w-xs">
                      {t.description}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {editingId === t.id ? (
                    <div className="flex flex-col gap-2">
                      <select
                        value={newCategory}
                        onChange={(e) => setNewCategory(e.target.value)}
                        className="text-xs border rounded px-1 py-1"
                        autoFocus
                      >
                        {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                      <input 
                        type="text" 
                        placeholder="Reason (optional)"
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        className="text-[10px] border rounded px-1 py-0.5"
                      />
                    </div>
                  ) : (
                    <div className="flex flex-col gap-1">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 w-fit">
                        {t.effective_category || t.category || "Uncategorised"}
                      </span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getSourceBadgeColor(t.category_source)} w-fit uppercase font-bold tracking-tighter`}>
                        {t.category_source || "imported"}
                      </span>
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center gap-1.5">
                    <Landmark size={14} className="text-gray-400" />
                    {t.source_bank}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold">
                  <div
                    className={`flex items-center justify-end gap-1 ${
                      t.direction === "inflow"
                        ? "text-green-600"
                        : "text-gray-900"
                    }`}
                  >
                    {t.direction === "inflow" ? (
                      <ArrowDownLeft size={14} />
                    ) : (
                      <ArrowUpRight size={14} />
                    )}
                    {t.currency === "GBP" ? "£" : t.currency}
                    {Math.abs(t.amount).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                    })}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {editingId === t.id ? (
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={() => handleApplyOverride(t.id)}
                        disabled={isSubmitting}
                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                        title="Save"
                      >
                        <Check size={16} />
                      </button>
                      <button 
                        onClick={handleCancelEdit}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Cancel"
                      >
                        <CloseIcon size={16} />
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={() => handleStartEdit(t)}
                        className="p-1 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                        title="Correct Category"
                      >
                        <Edit2 size={16} />
                      </button>
                      {t.category_source === "override" && (
                        <button 
                          onClick={() => handleRemoveOverride(t.id)}
                          className="p-1 text-gray-400 hover:text-orange-600 hover:bg-orange-50 rounded"
                          title="Remove Override"
                        >
                          <RotateCcw size={16} />
                        </button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TransactionTable;
