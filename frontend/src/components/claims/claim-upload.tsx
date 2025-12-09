"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useDropzone } from "react-dropzone";
import { useMutation } from "@tanstack/react-query";
import {
  Upload,
  FileText,
  X,
  Loader2,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export function ClaimUpload() {
  const t = useTranslations("claims");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [country, setCountry] = useState<string>("SK");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    multiple: true,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadMutation = useMutation({
    mutationFn: async () => {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/claims/upload?country=${country}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      return response.json();
    },
    onSuccess: (data) => {
      toast.success("Claim created successfully");
      router.push(`/claims/${data.id}`);
    },
    onError: () => {
      toast.error("Failed to upload files");
    },
  });

  const handleSubmit = () => {
    if (files.length === 0) {
      toast.error("Please select at least one file");
      return;
    }
    uploadMutation.mutate();
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">{t("newClaim")}</h1>
        <p className="text-zinc-400">{t("uploadDocuments")}</p>
      </div>

      {/* Country Selection */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader>
          <CardTitle className="text-white">{t("selectCountry")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label className="text-zinc-300">{t("country")}</Label>
            <Select value={country} onValueChange={setCountry}>
              <SelectTrigger className="border-zinc-700 bg-zinc-800 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SK">🇸🇰 Slovakia</SelectItem>
                <SelectItem value="IT">🇮🇹 Italy</SelectItem>
                <SelectItem value="DE">🇩🇪 Germany</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* File Upload */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader>
          <CardTitle className="text-white">{t("documents")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
              isDragActive
                ? "border-emerald-500 bg-emerald-500/10"
                : "border-zinc-700 hover:border-zinc-600"
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-zinc-500" />
            <p className="mt-4 text-zinc-300">
              {isDragActive
                ? "Drop files here..."
                : "Drag & drop PDF files here, or click to select"}
            </p>
            <p className="mt-2 text-sm text-zinc-500">
              Only PDF files are accepted
            </p>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-800/50 p-3"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-zinc-500" />
                    <div>
                      <p className="text-sm font-medium text-white">
                        {file.name}
                      </p>
                      <p className="text-xs text-zinc-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(index)}
                    className="text-zinc-400 hover:text-red-400"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Submit */}
      <div className="flex justify-end gap-3">
        <Button
          variant="outline"
          onClick={() => router.back()}
          className="border-zinc-700 text-zinc-300"
        >
          {tCommon("cancel")}
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={files.length === 0 || uploadMutation.isPending}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          {uploadMutation.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <CheckCircle className="mr-2 h-4 w-4" />
              {t("uploadDocuments")}
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

