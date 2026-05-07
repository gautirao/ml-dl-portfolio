import React, { useEffect, useState } from "react";
import TransactionTable from "../components/TransactionTable";
import { api } from "../api/client";
import type { Transaction } from "../api/types";
import { Search, X } from "lucide-react";

const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    merchant: "",
    category: "",
    source_bank: "",
    direction: "",
  });

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      const data = await api.getTransactions({
        merchant: filters.merchant || undefined,
        category: filters.category || undefined,
        source_bank: filters.source_bank || undefined,
        direction: filters.direction || undefined,
        limit: 100,
      });
      setTransactions(data);
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTransactions();
    }, 300);
    return () => clearTimeout(timer);
  }, [filters]);

  const handleFilterChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setFilters({
      merchant: "",
      category: "",
      source_bank: "",
      direction: "",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Transactions
          </h1>
          <p className="text-gray-500 mt-2">
            Browse and filter your imported financial history.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={16} className="text-gray-400" />
            </div>
            <input
              type="text"
              name="merchant"
              value={filters.merchant}
              onChange={handleFilterChange}
              placeholder="Search merchants..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>

          <select
            name="category"
            value={filters.category}
            onChange={handleFilterChange}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          >
            <option value="">All Categories</option>
            <option value="Shopping">Shopping</option>
            <option value="Groceries">Groceries</option>
            <option value="Transport">Transport</option>
            <option value="Dining">Dining</option>
            <option value="Entertainment">Entertainment</option>
            <option value="Bills">Bills</option>
            <option value="Income">Income</option>
            <option value="Transfers">Transfers</option>
            <option value="General">General</option>
          </select>

          <select
            name="source_bank"
            value={filters.source_bank}
            onChange={handleFilterChange}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          >
            <option value="">All Banks</option>
            <option value="Monzo">Monzo</option>
            <option value="HSBC">HSBC</option>
          </select>

          <select
            name="direction"
            value={filters.direction}
            onChange={handleFilterChange}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          >
            <option value="">All Types</option>
            <option value="outflow">Spending (Outflow)</option>
            <option value="inflow">Income (Inflow)</option>
          </select>

          <button
            onClick={clearFilters}
            className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
          >
            <X size={16} className="mr-2" />
            Clear
          </button>
        </div>
      </div>

      <TransactionTable transactions={transactions} isLoading={isLoading} />
    </div>
  );
};

export default TransactionsPage;
