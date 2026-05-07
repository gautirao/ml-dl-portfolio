import React from "react";
import type { TopMerchant } from "../api/types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface TopMerchantsChartProps {
  data: TopMerchant[];
  isLoading: boolean;
}

const COLORS = ["#4f46e5", "#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe"];

const TopMerchantsChart: React.FC<TopMerchantsChartProps> = ({
  data,
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
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Merchants</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" hide />
            <YAxis
              dataKey="merchant"
              type="category"
              width={100}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value: any) => [`£${Number(value).toLocaleString()}`, "Spent"]}
              contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
            />
            <Bar dataKey="total_amount" radius={[0, 4, 4, 0]} barSize={24}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TopMerchantsChart;
