import React, { useState } from "react";
import type { PlannerPlan, ToolResult } from "../api/types";
import { ChevronDown, ChevronRight, Cpu, Wrench, Search, Eye } from "lucide-react";

interface EvidencePanelProps {
  plan: PlannerPlan | null | undefined;
  toolResult: ToolResult | null | undefined;
  evidence: Record<string, any> | null | undefined;
}

const EvidencePanel: React.FC<EvidencePanelProps> = ({
  plan,
  toolResult,
  evidence,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!plan) return null;

  return (
    <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Eye size={16} className="text-indigo-500" />
          <span>Planner & Evidence</span>
          <span className="ml-2 px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[10px] uppercase font-bold">
            {plan.tool}
          </span>
        </div>
        {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-gray-200 space-y-4 text-xs font-mono">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Plan Details */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-500 font-bold uppercase tracking-tight">
                <Cpu size={14} />
                <span>Planner Logic</span>
              </div>
              <div className="bg-white p-3 rounded border border-gray-200 space-y-1 overflow-x-auto">
                <p><span className="text-indigo-600">Intent:</span> {plan.intent}</p>
                <p><span className="text-indigo-600">Tool:</span> {plan.tool}</p>
                <p><span className="text-indigo-600">Plan Strategy:</span> {plan.reasoning_summary}</p>
                <p><span className="text-indigo-600">Confidence:</span> {(plan.confidence * 100).toFixed(1)}%</p>
              </div>
            </div>

            {/* Tool Execution */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-500 font-bold uppercase tracking-tight">
                <Wrench size={14} />
                <span>Tool Execution</span>
              </div>
              <div className="bg-white p-3 rounded border border-gray-200 space-y-1 overflow-x-auto">
                <p><span className="text-green-600">Status:</span> {toolResult?.execution_status || "N/A"}</p>
                <p><span className="text-green-600">Arguments:</span> {JSON.stringify(plan.arguments)}</p>
                {toolResult?.result && (
                  <p><span className="text-green-600">Result Summary:</span> Found {Array.isArray(toolResult.result) ? toolResult.result.length : "object"} records</p>
                )}
              </div>
            </div>
          </div>

          {/* Evidence Data */}
          {evidence && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-500 font-bold uppercase tracking-tight">
                <Search size={14} />
                <span>Evidence Data</span>
              </div>
              <div className="bg-gray-900 text-gray-300 p-3 rounded border border-gray-800 overflow-x-auto max-h-48 overflow-y-auto">
                {plan.tool === "semantic_spending_search" && (
                  <div className="mb-3 p-2 bg-indigo-900/50 border border-indigo-700/50 rounded text-indigo-200">
                    <p className="font-bold mb-1">ℹ️ Semantic Match Note</p>
                    <p>Semantic search selected candidate merchants/categories based on your query. 
                       The final totals shown were calculated deterministically using DuckDB.</p>
                  </div>
                )}
                {plan.tool === "knowledge_lookup" && evidence.knowledge_sources && (
                  <div className="mb-3 space-y-2">
                    <p className="font-bold text-indigo-400 mb-1">📚 Knowledge Sources</p>
                    {evidence.knowledge_sources.map((src: any, idx: number) => (
                      <div key={idx} className="p-2 bg-indigo-900/30 border border-indigo-700/30 rounded text-indigo-200">
                        <p className="font-bold">{src.source} (Section {src.section})</p>
                        <p className="text-gray-400 text-[10px] mt-1 italic">"{src.snippet}"</p>
                      </div>
                    ))}
                  </div>
                )}
                <pre>{JSON.stringify(evidence, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EvidencePanel;
