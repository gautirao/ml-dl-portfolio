import React from "react";
import type { CategorySummaryItem } from "../api/types";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

interface CategorySummaryProps {
  data: CategorySummaryItem[];
  isLoading: boolean;
}

const COLORS = ["#4f46e5", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#6b7280"];

const CategorySummary: React.FC<CategorySummaryProps> = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-80 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const chartData = data
    .filter(item => item.total_amount > 0)
    .map(item => ({
      name: item.category,
      value: item.total_amount,
    }));

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Spending by Category</h3>
      <div className="h-64">
        {chartData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">No category data available</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: any) => [`£${Number(value).toLocaleString()}`, "Amount"]}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default CategorySummary;
