import React from "react";
import type { Transaction } from "../api/types";
import { ArrowUpRight, ArrowDownLeft, Landmark } from "lucide-react";

interface TransactionTableProps {
  transactions: Transaction[];
  isLoading: boolean;
}

const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  isLoading,
}) => {
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
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                    {t.category}
                  </span>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TransactionTable;
