import React from "react";
import type { RecurringPayment } from "../api/types";
import { Calendar, RefreshCw } from "lucide-react";

interface RecurringPaymentsListProps {
  payments: RecurringPayment[];
  isLoading: boolean;
}

const RecurringPaymentsList: React.FC<RecurringPaymentsListProps> = ({
  payments,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-80 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <RefreshCw size={20} className="text-indigo-600" />
        Identified Recurring Payments
      </h3>
      <div className="space-y-4 max-h-64 overflow-y-auto pr-2">
        {payments.length === 0 ? (
          <p className="text-gray-500 text-center py-10">No recurring payments detected yet.</p>
        ) : (
          payments.map((p, i) => (
            <div
              key={i}
              className="flex justify-between items-center p-3 rounded-lg bg-gray-50 border border-gray-100"
            >
              <div className="flex flex-col">
                <span className="text-sm font-bold text-gray-900">
                  {p.merchant}
                </span>
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Calendar size={12} />
                  Every {p.frequency_days} days (Last: {p.last_date})
                </span>
              </div>
              <div className="text-right">
                <span className="text-sm font-bold text-gray-900">
                  £{p.avg_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
                <p className="text-[10px] text-gray-400 uppercase font-semibold">
                  Avg Amount
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RecurringPaymentsList;
