import React from "react";
import { ShieldAlert, ShieldCheck } from "lucide-react";

interface GuardrailBadgeProps {
  type: "input" | "plan" | "output";
  status: boolean;
}

const GuardrailBadge: React.FC<GuardrailBadgeProps> = ({ type, status }) => {
  const labels = {
    input: "Input Safety",
    plan: "Plan Integrity",
    output: "Output Verified",
  };

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
        status
          ? "bg-green-100 text-green-700 border border-green-200"
          : "bg-red-100 text-red-700 border border-red-200"
      }`}
    >
      {status ? (
        <ShieldCheck size={12} className="text-green-600" />
      ) : (
        <ShieldAlert size={12} className="text-red-600" />
      )}
      {labels[type]}
    </div>
  );
};

export default GuardrailBadge;
