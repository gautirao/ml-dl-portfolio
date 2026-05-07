import axios from "axios";
import type {
  ChatResponse,
  Transaction,
  ImportPreview,
  ImportSummary,
  SpendingSummary,
  TopMerchant,
  CategorySummaryItem,
  RecurringPayment,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
});

export const api = {
  // Chat
  chat: async (message: string): Promise<ChatResponse> => {
    const response = await client.post<ChatResponse>("/api/chat", { message });
    return response.data;
  },

  // Transactions
  getTransactions: async (params?: {
    date_from?: string;
    date_to?: string;
    source_bank?: string;
    direction?: string;
    merchant?: string;
    category?: string;
    limit?: number;
    offset?: number;
  }): Promise<Transaction[]> => {
    const response = await client.get<{ transactions: Transaction[] }>(
      "/api/transactions",
      {
        params,
      }
    );
    return response.data.transactions;
  },

  // Ingestion
  previewImport: async (
    file: File,
    bankOverride: string = "auto"
  ): Promise<ImportPreview> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_bank_override", bankOverride);

    const response = await client.post<ImportPreview>(
      "/api/import/preview",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return response.data;
  },

  confirmImport: async (
    file: File,
    bankOverride: string = "auto"
  ): Promise<ImportSummary> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_bank_override", bankOverride);

    const response = await client.post<ImportSummary>(
      "/api/import",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return response.data;
  },

  // Analytics
  getSpendingSummary: async (params?: {
    date_from?: string;
    date_to?: string;
    source_bank?: string;
  }): Promise<SpendingSummary> => {
    const response = await client.get<SpendingSummary>(
      "/api/analytics/spending-summary",
      { params }
    );
    return response.data;
  },

  getTopMerchants: async (params?: {
    date_from?: string;
    date_to?: string;
    source_bank?: string;
    limit?: number;
  }): Promise<TopMerchant[]> => {
    const response = await client.get<TopMerchant[]>(
      "/api/analytics/top-merchants",
      { params }
    );
    return response.data;
  },

  getCategorySummary: async (params?: {
    date_from?: string;
    date_to?: string;
    source_bank?: string;
  }): Promise<CategorySummaryItem[]> => {
    const response = await client.get<CategorySummaryItem[]>(
      "/api/analytics/category-summary",
      { params }
    );
    return response.data;
  },

  getRecurringPayments: async (params?: {
    source_bank?: string;
  }): Promise<RecurringPayment[]> => {
    const response = await client.get<RecurringPayment[]>(
      "/api/analytics/recurring-payments",
      { params }
    );
    return response.data;
  },
};
