"use client";

import { useTranslations } from "next-intl";
import { 
  Upload, 
  FileText, 
  Sparkles, 
  Lock, 
  CheckCircle2, 
  Brain,
  FileCheck,
  AlertCircle,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WorkflowStep {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  statuses: string[];
}

const workflowSteps: WorkflowStep[] = [
  {
    id: "upload",
    label: "Upload",
    icon: Upload,
    statuses: ["PROCESSING"],
  },
  {
    id: "ocr",
    label: "OCR",
    icon: FileText,
    statuses: ["PROCESSING", "OCR_REVIEW"],
  },
  {
    id: "cleaning",
    label: "Cleaning",
    icon: Sparkles,
    statuses: ["CLEANING"],
  },
  {
    id: "anonymization",
    label: "Anonymization",
    icon: Lock,
    statuses: ["ANONYMIZING", "ANONYMIZATION_REVIEW"],
  },
  {
    id: "ready",
    label: "Ready",
    icon: CheckCircle2,
    statuses: ["READY_FOR_ANALYSIS"],
  },
  {
    id: "analysis",
    label: "Analysis",
    icon: Brain,
    statuses: ["ANALYZING"],
  },
  {
    id: "complete",
    label: "Complete",
    icon: FileCheck,
    statuses: ["ANALYZED"],
  },
];

interface WorkflowProgressProps {
  currentStatus: string;
  className?: string;
}

export function WorkflowProgress({ currentStatus, className }: WorkflowProgressProps) {
  const t = useTranslations("claims");
  
  // Determine which step is currently active
  const getCurrentStepIndex = () => {
    if (currentStatus === "FAILED") return -1;
    
    for (let i = 0; i < workflowSteps.length; i++) {
      if (workflowSteps[i].statuses.includes(currentStatus)) {
        return i;
      }
    }
    return 0;
  };

  const currentStepIndex = getCurrentStepIndex();
  const isFailed = currentStatus === "FAILED";

  const getStepState = (index: number): "completed" | "active" | "pending" | "failed" => {
    if (isFailed && index === currentStepIndex) return "failed";
    if (isFailed) return "pending";
    if (index < currentStepIndex) return "completed";
    if (index === currentStepIndex) return "active";
    return "pending";
  };

  const getStepColor = (state: string) => {
    switch (state) {
      case "completed":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
      case "active":
        return "bg-blue-500/20 text-blue-400 border-blue-500/40 animate-pulse";
      case "pending":
        return "bg-zinc-800 text-zinc-500 border-zinc-700";
      case "failed":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      default:
        return "bg-zinc-800 text-zinc-500 border-zinc-700";
    }
  };

  const getConnectorColor = (index: number) => {
    const state = getStepState(index);
    if (state === "completed") return "bg-emerald-500/40";
    if (state === "active") return "bg-blue-500/40";
    return "bg-zinc-700";
  };

  return (
    <div className={cn("w-full", className)}>
      {/* Failed state banner */}
      {isFailed && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>Workflow failed. Please check the error and retry.</span>
        </div>
      )}

      {/* Progress steps */}
      <div className="relative flex items-center justify-between">
        {workflowSteps.map((step, index) => {
          const state = getStepState(index);
          const Icon = step.icon;
          const isLast = index === workflowSteps.length - 1;

          return (
            <div key={step.id} className="relative flex flex-1 items-center">
              {/* Step circle */}
              <div className="relative z-10 flex flex-col items-center gap-2">
                <div
                  className={cn(
                    "flex h-12 w-12 items-center justify-center rounded-full border-2 transition-all",
                    getStepColor(state)
                  )}
                  title={step.label}
                >
                  {state === "active" && (
                    <Clock className="h-5 w-5 animate-spin" />
                  )}
                  {state === "completed" && (
                    <CheckCircle2 className="h-5 w-5" />
                  )}
                  {state === "failed" && (
                    <AlertCircle className="h-5 w-5" />
                  )}
                  {state === "pending" && (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <span
                  className={cn(
                    "text-xs font-medium transition-colors",
                    state === "completed" && "text-emerald-400",
                    state === "active" && "text-blue-400",
                    state === "pending" && "text-zinc-500",
                    state === "failed" && "text-red-400"
                  )}
                >
                  {step.label}
                </span>
              </div>

              {/* Connector line */}
              {!isLast && (
                <div className="relative flex-1 px-2">
                  <div
                    className={cn(
                      "h-0.5 w-full transition-all",
                      getConnectorColor(index)
                    )}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Current status text */}
      <div className="mt-4 text-center text-sm text-zinc-400">
        Current status:{" "}
        <span className="font-medium text-white">
          {currentStatus.replace(/_/g, " ")}
        </span>
      </div>
    </div>
  );
}

