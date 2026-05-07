import React, { useState, useRef, useEffect } from "react";
import { api } from "../api/client";
import type { ChatResponse } from "../api/types";
import { Send, User, Bot, Loader2, ShieldCheck } from "lucide-react";
import GuardrailBadge from "../components/GuardrailBadge";
import EvidencePanel from "../components/EvidencePanel";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  timestamp: Date;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.chat(userMessage.content);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        response: response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: error.response?.data?.detail || "Sorry, I encountered an error connecting to the local LLM. Make sure Ollama is running.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] max-w-4xl mx-auto">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
          AI Assistant
        </h1>
        <p className="text-gray-500 mt-1">
          Ask questions about your finances. Your data stays local.
        </p>
      </div>

      <div className="flex-grow bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
        {/* Message Area */}
        <div className="flex-grow overflow-y-auto p-4 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <div className="bg-indigo-50 p-4 rounded-full mb-4">
                <Bot size={48} className="text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                Ready to analyze your local data
              </h3>
              <p className="text-gray-500 max-w-xs mx-auto mt-2">
                Try asking: "What was my total spending last month?" or "How much did I spend at Amazon?"
              </p>
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {["Show me my top merchants", "List my recurring payments", "Summarize my spending"].map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); }}
                    className="px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-xs font-medium text-gray-600 hover:bg-gray-100 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-4 ${
                m.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              <div
                className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
                  m.role === "user"
                    ? "bg-gray-200 text-gray-600"
                    : "bg-indigo-600 text-white"
                }`}
              >
                {m.role === "user" ? <User size={20} /> : <Bot size={20} />}
              </div>

              <div
                className={`max-w-[80%] space-y-2 ${
                  m.role === "user" ? "text-right" : "text-left"
                }`}
              >
                <div
                  className={`inline-block p-4 rounded-2xl text-sm ${
                    m.role === "user"
                      ? "bg-indigo-600 text-white rounded-tr-none"
                      : "bg-gray-100 text-gray-900 rounded-tl-none border border-gray-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>

                {m.response && (
                  <div className="flex flex-col gap-2">
                    <div className="flex flex-wrap gap-2 justify-start mt-1">
                      <GuardrailBadge type="input" status={m.response.guardrails.input_allowed} />
                      <GuardrailBadge type="plan" status={m.response.guardrails.plan_valid} />
                      <GuardrailBadge type="output" status={m.response.guardrails.output_verified} />
                    </div>
                    <EvidencePanel 
                      plan={m.response.plan} 
                      toolResult={m.response.tool_result} 
                      evidence={m.response.evidence} 
                    />
                  </div>
                )}

                <p className="text-[10px] text-gray-400 font-medium">
                  {m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-4 flex-row">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-600 text-white flex items-center justify-center">
                <Bot size={20} />
              </div>
              <div className="bg-gray-100 p-4 rounded-2xl rounded-tl-none border border-gray-200 flex items-center gap-2">
                <Loader2 size={16} className="text-indigo-600 animate-spin" />
                <span className="text-sm text-gray-500 font-medium italic">Assistant is planning...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <form onSubmit={handleSend} className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your finances..."
              disabled={isLoading}
              className="w-full bg-white border border-gray-300 rounded-full pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 top-1.5 h-9 w-9 bg-indigo-600 text-white rounded-full flex items-center justify-center hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              <Send size={18} />
            </button>
          </form>
          <div className="mt-2 flex items-center justify-center gap-1 text-[10px] text-gray-400 font-bold uppercase tracking-widest">
            <ShieldCheck size={12} />
            Local Processing • No Cloud Sync
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
