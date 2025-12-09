"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Save, Check, RefreshCw, ChevronLeft, ChevronRight, Loader2, RotateCcw } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import type { AnonReviewDocument, AnonReviewResponse } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AnonymizationReviewPage() {
  const params = useParams();
  const router = useRouter();
  const claimId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [data, setData] = useState<AnonReviewResponse | null>(null);
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const [editedTexts, setEditedTexts] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnonData();
  }, [claimId]);

  const fetchAnonData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/anon`, {
        credentials: "include",
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to load anonymization data");
      }

      const result: AnonReviewResponse = await response.json();
      setData(result);

      // Initialize edited texts
      const initial: Record<number, string> = {};
      result.documents.forEach((doc) => {
        initial[doc.id] = doc.anonymized_text || "";
      });
      setEditedTexts(initial);
    } catch (err: any) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (docId: number, text: string) => {
    setEditedTexts((prev) => ({ ...prev, [docId]: text }));
  };

  const saveCurrentDocument = async () => {
    if (!data) return;
    
    try {
      setSaving(true);
      const currentDoc = data.documents[currentDocIndex];
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/anon/edit`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          edits: { [currentDoc.id]: editedTexts[currentDoc.id] || "" }
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save document");
      }

      toast.success(`Saved: ${currentDoc.filename}`);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  const saveAllDocuments = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/anon/edit`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ edits: editedTexts }),
      });

      if (!response.ok) {
        throw new Error("Failed to save changes");
      }

      toast.success("All documents saved");
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  const retryAnonymization = async () => {
    try {
      setRetrying(true);
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/anon/retry`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to retry anonymization");
      }

      toast.success("Anonymization restarted");
      fetchAnonData();
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setRetrying(false);
    }
  };

  const approveAnonymization = async () => {
    try {
      setApproving(true);
      
      // First save any changes
      await saveAllDocuments();

      // Then approve
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/anon/approve`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to approve anonymization");
      }

      toast.success("Anonymization approved");
      router.push(`/claims/${claimId}`);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setApproving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <Card className="border-red-800 bg-red-950/20">
          <CardHeader>
            <CardTitle className="text-red-400">Error</CardTitle>
            <CardDescription>{error || "Failed to load anonymization data"}</CardDescription>
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

  const currentDoc = data.documents[currentDocIndex];
  const totalDocs = data.documents.length;

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
            <h1 className="text-2xl font-bold">Anonymization Review</h1>
            <p className="text-zinc-400">Claim #{claimId} • {data.country}</p>
          </div>
        </div>
        <Badge variant="outline" className="text-amber-400 border-amber-400">
          ANONYMIZATION_REVIEW
        </Badge>
      </div>

      {/* Document Navigation */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-500">Document</p>
              <p className="text-lg font-semibold text-white">
                {currentDocIndex + 1} of {totalDocs}
              </p>
              <p className="text-sm text-zinc-400">{currentDoc.filename}</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                disabled={currentDocIndex === 0}
                onClick={() => setCurrentDocIndex((prev) => prev - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                disabled={currentDocIndex === totalDocs - 1}
                onClick={() => setCurrentDocIndex((prev) => prev + 1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Horizontal Layout: Anonymized Text (left) + Cleaned Text (right) */}
      <div className="grid grid-cols-2 gap-6">
        {/* Left: Anonymized Text (Editable) */}
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <CardTitle className="text-lg text-white">Anonymized Text</CardTitle>
            <CardDescription>Review and edit anonymized text</CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={editedTexts[currentDoc.id] || ""}
              onChange={(e) => handleTextChange(currentDoc.id, e.target.value)}
              className="min-h-[600px] font-mono text-sm bg-zinc-950 border-zinc-700 text-white"
              placeholder="No anonymized text..."
            />
          </CardContent>
        </Card>

        {/* Right: Cleaned Text (Read-only for comparison) */}
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <CardTitle className="text-lg text-white">Cleaned Text (Original)</CardTitle>
            <CardDescription>Original cleaned text for comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={currentDoc.cleaned_text || ""}
              readOnly
              className="min-h-[600px] font-mono text-sm bg-zinc-950 border-zinc-700 text-zinc-300"
            />
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <Button variant="outline" onClick={retryAnonymization} disabled={retrying}>
          {retrying ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RotateCcw className="mr-2 h-4 w-4" />
          )}
          Retry Anonymization
        </Button>

        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={saveCurrentDocument} disabled={saving}>
            {saving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            Save Current
          </Button>

          <Button variant="outline" onClick={saveAllDocuments} disabled={saving}>
            {saving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            Save All
          </Button>

          <Button
            onClick={approveAnonymization}
            disabled={approving}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {approving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Check className="mr-2 h-4 w-4" />
            )}
            Approve & Continue
          </Button>
        </div>
      </div>
    </div>
  );
}
