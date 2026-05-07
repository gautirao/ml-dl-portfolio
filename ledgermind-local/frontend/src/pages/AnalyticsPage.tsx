import React, { useEffect, useState } from "react";
import AnalyticsCards from "../components/AnalyticsCards";
import TopMerchantsChart from "../components/TopMerchantsChart";
import RecurringPaymentsList from "../components/RecurringPaymentsList";
import CategorySummary from "../components/CategorySummary";
import { api } from "../api/client";
import type {
  SpendingSummary,
  TopMerchant,
  RecurringPayment,
  CategorySummaryItem,
} from "../api/types";
import { Calendar, Filter } from "lucide-react";

const AnalyticsPage: React.FC = () => {
  const [spendingSummary, setSpendingSummary] = useState<SpendingSummary | null>(null);
  const [topMerchants, setTopMerchants] = useState<TopMerchant[]>([]);
  const [recurringPayments, setRecurringPayments] = useState<RecurringPayment[]>([]);
  const [categorySummary, setCategorySummary] = useState<CategorySummaryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    date_from: "",
    date_to: "",
    source_bank: "",
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const params = {
        date_from: filters.date_from || undefined,
        date_to: filters.date_to || undefined,
        source_bank: filters.source_bank || undefined,
      };

      const [summary, merchants, recurring, categories] = await Promise.all([
        api.getSpendingSummary(params),
        api.getTopMerchants({ ...params, limit: 5 }),
        api.getRecurringPayments({ source_bank: params.source_bank }),
        api.getCategorySummary(params),
      ]);

      setSpendingSummary(summary);
      setTopMerchants(merchants);
      setRecurringPayments(recurring);
      setCategorySummary(categories);
    } catch (error) {
      console.error("Failed to fetch analytics data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Financial Insights
          </h1>
          <p className="text-gray-500 mt-2">
            Deterministic analysis of your spending habits and recurring costs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-gray-400" />
            <input
              type="date"
              name="date_from"
              value={filters.date_from}
              onChange={handleFilterChange}
              className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 border p-1"
            />
            <span className="text-gray-400 text-xs">to</span>
            <input
              type="date"
              name="date_to"
              value={filters.date_to}
              onChange={handleFilterChange}
              className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 border p-1"
            />
          </div>
          <div className="h-6 w-px bg-gray-200"></div>
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-gray-400" />
            <select
              name="source_bank"
              value={filters.source_bank}
              onChange={handleFilterChange}
              className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 border p-1"
            >
              <option value="">All Banks</option>
              <option value="Monzo">Monzo</option>
              <option value="HSBC">HSBC</option>
            </select>
          </div>
        </div>
      </div>

      <AnalyticsCards summary={spendingSummary} isLoading={isLoading} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopMerchantsChart data={topMerchants} isLoading={isLoading} />
        <CategorySummary data={categorySummary} isLoading={isLoading} />
      </div>

      <RecurringPaymentsList payments={recurringPayments} isLoading={isLoading} />
    </div>
  );
};

export default AnalyticsPage;
