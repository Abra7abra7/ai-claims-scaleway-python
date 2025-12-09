"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ArrowLeft, Save, Check, Eye, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import type { 
  OCRReviewDocument, 
  OCRReviewResponse, 
  CleaningStats, 
  CleaningPreviewDocument 
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function OCRReviewPage() {
  const params = useParams();
  const router = useRouter();
  const claimId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [data, setData] = useState<OCRReviewResponse | null>(null);
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const [editedTexts, setEditedTexts] = useState<Record<number, string>>({});
  const [cleaningPreview, setCleaningPreview] = useState<CleaningPreviewDocument[] | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOCRData();
  }, [claimId]);

  const fetchOCRData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/ocr`, {
        credentials: "include",
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to load OCR data");
      }

      const result: OCRReviewData = await response.json();
      setData(result);

      // Initialize edited texts
      const initial: Record<number, string> = {};
      result.documents.forEach((doc) => {
        initial[doc.id] = doc.original_text || "";
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

  const saveChanges = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/ocr/edit`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ edits: editedTexts }),
      });

      if (!response.ok) {
        throw new Error("Failed to save changes");
      }

      toast.success("Changes saved");
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  const previewCleaning = async () => {
    try {
      setShowPreview(true);
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/ocr/preview-cleaning`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to preview cleaning");
      }

      const result = await response.json();
      setCleaningPreview(result.documents);
    } catch (err: any) {
      toast.error(err.message);
      setShowPreview(false);
    }
  };

  const approveOCR = async () => {
    try {
      setApproving(true);
      
      // First save any changes
      await saveChanges();

      // Then approve
      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}/ocr/approve`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to approve OCR");
      }

      toast.success("OCR approved, cleaning started");
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
            <CardDescription>{error || "Failed to load OCR data"}</CardDescription>
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
            <h1 className="text-2xl font-bold">OCR Review</h1>
            <p className="text-zinc-400">Claim #{claimId} • {data.country}</p>
          </div>
        </div>
        <Badge variant="outline" className="text-emerald-400 border-emerald-400">
          OCR_REVIEW
        </Badge>
      </div>

      {/* Document Navigation */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              Document {currentDocIndex + 1} of {totalDocs}
            </CardTitle>
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
          <CardDescription>{currentDoc.filename}</CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            value={editedTexts[currentDoc.id] || ""}
            onChange={(e) => handleTextChange(currentDoc.id, e.target.value)}
            className="min-h-[400px] font-mono text-sm bg-zinc-950 border-zinc-700"
            placeholder="No OCR text extracted..."
          />
        </CardContent>
      </Card>

      {/* Cleaning Preview */}
      {showPreview && cleaningPreview && (
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <CardTitle className="text-lg">Cleaning Preview</CardTitle>
            <CardDescription>
              Preview how text will look after cleaning rules are applied
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {cleaningPreview.map((doc) => (
              <div key={doc.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{doc.filename}</span>
                  <Badge variant="secondary">
                    -{doc.stats.reduction_percent}% ({doc.stats.characters_removed} chars)
                  </Badge>
                </div>
                <Textarea
                  value={doc.cleaned_text}
                  readOnly
                  className="min-h-[200px] font-mono text-sm bg-zinc-950 border-zinc-700"
                />
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <Button variant="outline" onClick={previewCleaning} disabled={showPreview}>
          <Eye className="mr-2 h-4 w-4" />
          Preview Cleaning
        </Button>

        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={saveChanges} disabled={saving}>
            {saving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            Save Changes
          </Button>

          <Button
            onClick={approveOCR}
            disabled={approving}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {approving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Check className="mr-2 h-4 w-4" />
            )}
            Approve & Start Cleaning
          </Button>
        </div>
      </div>
    </div>
  );
}

