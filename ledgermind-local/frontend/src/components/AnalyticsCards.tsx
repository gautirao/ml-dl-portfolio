import React from "react";
import type { SpendingSummary } from "../api/types";
import { TrendingDown, TrendingUp, Wallet, Activity } from "lucide-react";

interface AnalyticsCardsProps {
  summary: SpendingSummary | null;
  isLoading: boolean;
}

const AnalyticsCards: React.FC<AnalyticsCardsProps> = ({
  summary,
  isLoading,
}) => {
  const cards = [
    {
      name: "Total Spending",
      value: summary ? `£${summary.total_outflow.toLocaleString()}` : "£0",
      icon: TrendingDown,
      color: "text-red-600",
      bg: "bg-red-50",
    },
    {
      name: "Total Income",
      value: summary ? `£${summary.total_inflow.toLocaleString()}` : "£0",
      icon: TrendingUp,
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      name: "Net Cash Flow",
      value: summary ? `£${summary.net_amount.toLocaleString()}` : "£0",
      icon: Wallet,
      color: summary && summary.net_amount >= 0 ? "text-indigo-600" : "text-amber-600",
      bg: "bg-indigo-50",
    },
    {
      name: "Transactions",
      value: summary ? summary.transaction_count.toString() : "0",
      icon: Activity,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-pulse"
          >
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.name}
          className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4"
        >
          <div className={`${card.bg} p-3 rounded-lg`}>
            <card.icon className={card.color} size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">{card.name}</p>
            <p className="text-2xl font-bold text-gray-900">{card.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AnalyticsCards;
