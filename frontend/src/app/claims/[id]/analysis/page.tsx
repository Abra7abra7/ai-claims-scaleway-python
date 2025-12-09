"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Play, RotateCcw, Download, Loader2, CheckCircle, AlertCircle, Brain } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import type { PromptSummary, PromptListResponse, ClaimDetail } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const claimId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [prompts, setPrompts] = useState<PromptSummary[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<string>("");
  const [claim, setClaim] = useState<ClaimDetail | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, [claimId]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch claim data
      const claimRes = await fetch(`${API_URL}/api/v1/claims/${claimId}`, {
        credentials: "include",
      });

      if (!claimRes.ok) {
        throw new Error("Failed to load claim");
      }

      const claimData: ClaimData = await claimRes.json();
      setClaim(claimData);

      // Fetch prompts
      const promptsRes = await fetch(`${API_URL}/api/v1/prompts`, {
        credentials: "include",
      });

      if (promptsRes.ok) {
        const promptsData: PromptListResponse = await promptsRes.json();
        setPrompts(promptsData.prompts);
        setSelectedPrompt(promptsData.default);
      }

      // Fetch analysis result if available
      if (claimData.status === "analyzed" || claimData.analysis_result) {
        try {
          const resultRes = await fetch(`${API_URL}/api/v1/claims/${claimId}/analysis/result`, {
            credentials: "include",
          });

          if (resultRes.ok) {
            const resultData = await resultRes.json();
            setAnalysisResult(resultData);
          }
        } catch {
          // Analysis result not available
        }
      }
    } catch (err: any) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startAnalysis = async () => {
    try {
      setStarting(true);

      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/analysis/start`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt_id: selectedPrompt }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to start analysis");
      }

      toast.success("Analysis started");
      
      // Refresh data after a delay
      setTimeout(() => {
        fetchData();
      }, 2000);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setStarting(false);
    }
  };

  const resetStatus = async () => {
    try {
      setResetting(true);

      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/anon/reset-status`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to reset status");
      }

      toast.success("Status reset to READY_FOR_ANALYSIS");
      fetchData();
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setResetting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (error || !claim) {
    return (
      <div className="p-6">
        <Card className="border-red-800 bg-red-950/20">
          <CardHeader>
            <CardTitle className="text-red-400">Error</CardTitle>
            <CardDescription>{error || "Failed to load data"}</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href={`/claims/${claimId}`}>
              <Button variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Claim
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const canStartAnalysis = claim.status === "ready_for_analysis";
  const canReset = ["analyzing", "failed", "analyzed"].includes(claim.status);
  const isAnalyzing = claim.status === "analyzing";
  const hasResult = claim.analysis_result || analysisResult;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={`/claims/${claimId}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Analysis</h1>
            <p className="text-zinc-400">Claim #{claimId} • {claim.country}</p>
          </div>
        </div>
        <Badge
          variant="outline"
          className={
            claim.status === "analyzed"
              ? "text-emerald-400 border-emerald-400"
              : claim.status === "failed"
              ? "text-red-400 border-red-400"
              : "text-blue-400 border-blue-400"
          }
        >
          {claim.status.toUpperCase()}
        </Badge>
      </div>

      {/* Analyzing Status */}
      {isAnalyzing && (
        <Card className="border-blue-800 bg-blue-950/20">
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-blue-400">Analysis in Progress</h3>
              <p className="text-zinc-400 mt-2">
                Please wait while AI analyzes the documents...
              </p>
              <Button variant="outline" className="mt-4" onClick={fetchData}>
                <RotateCcw className="mr-2 h-4 w-4" />
                Refresh Status
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Prompt Selection */}
      {canStartAnalysis && (
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-emerald-400" />
              Select Analysis Prompt
            </CardTitle>
            <CardDescription>
              Choose the prompt template for AI analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RadioGroup
              value={selectedPrompt}
              onValueChange={setSelectedPrompt}
              className="space-y-4"
            >
              {prompts.map((prompt) => (
                <div
                  key={prompt.id}
                  className={`flex items-start space-x-4 p-4 rounded-lg border transition-colors ${
                    selectedPrompt === prompt.id
                      ? "border-emerald-500 bg-emerald-950/20"
                      : "border-zinc-700 hover:border-zinc-600"
                  }`}
                >
                  <RadioGroupItem value={prompt.id} id={prompt.id} className="mt-1" />
                  <div className="flex-1">
                    <Label htmlFor={prompt.id} className="font-medium cursor-pointer">
                      {prompt.name}
                    </Label>
                    {prompt.description && (
                      <p className="text-sm text-zinc-400 mt-1">{prompt.description}</p>
                    )}
                    <Badge variant="secondary" className="mt-2">
                      {prompt.llm_model}
                    </Badge>
                  </div>
                </div>
              ))}
            </RadioGroup>

            <Button
              onClick={startAnalysis}
              disabled={starting || !selectedPrompt}
              className="w-full mt-6 bg-emerald-600 hover:bg-emerald-700"
            >
              {starting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Start Analysis
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Analysis Result */}
      {hasResult && (
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {claim.status === "analyzed" ? (
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-amber-400" />
                )}
                Analysis Result
              </CardTitle>
              {claim.analysis_model && (
                <Badge variant="secondary">{claim.analysis_model}</Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-zinc-950 rounded-lg p-4 border border-zinc-700">
              <pre className="whitespace-pre-wrap text-sm font-mono text-zinc-300">
                {typeof (analysisResult?.result || claim.analysis_result) === "object"
                  ? JSON.stringify(analysisResult?.result || claim.analysis_result, null, 2)
                  : analysisResult?.result || claim.analysis_result}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      {canReset && (
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-zinc-800">
          <Button variant="outline" onClick={resetStatus} disabled={resetting}>
            {resetting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="mr-2 h-4 w-4" />
            )}
            Reset & Re-analyze
          </Button>
        </div>
      )}
    </div>
  );
}

