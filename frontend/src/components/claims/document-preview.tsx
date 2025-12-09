"use client";

import { useState } from "react";
import { X, Download, FileText, Eye, Lock, Brain } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface DocumentPreviewProps {
  document: {
    id: number;
    filename: string;
    s3_key?: string;
    original_text?: string;
    cleaned_text?: string;
    anonymized_text?: string;
  };
  analysisResult?: any;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DocumentPreview({
  document,
  analysisResult,
  open,
  onOpenChange,
}: DocumentPreviewProps) {
  const [activeTab, setActiveTab] = useState("original");

  const handleDownload = (type: string, content: string) => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement("a");
    a.href = url;
    a.download = `${document.filename.replace(".pdf", "")}_${type}.txt`;
    window.document.body.appendChild(a);
    a.click();
    window.document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const tabs = [
    {
      value: "original",
      label: "Original PDF",
      icon: FileText,
      available: !!document.s3_key,
      content: document.s3_key,
    },
    {
      value: "ocr",
      label: "OCR Text",
      icon: Eye,
      available: !!document.original_text,
      content: document.original_text,
    },
    {
      value: "cleaned",
      label: "Cleaned Text",
      icon: FileText,
      available: !!document.cleaned_text,
      content: document.cleaned_text,
    },
    {
      value: "anonymized",
      label: "Anonymized",
      icon: Lock,
      available: !!document.anonymized_text,
      content: document.anonymized_text,
    },
    {
      value: "analysis",
      label: "Analysis",
      icon: Brain,
      available: !!analysisResult,
      content: analysisResult,
    },
  ];

  const availableTabs = tabs.filter((tab) => tab.available);
  const activeTabData = availableTabs.find((tab) => tab.value === activeTab);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[98vw] h-[98vh] bg-zinc-900 border-zinc-800 flex flex-col overflow-hidden p-0">
        <DialogHeader className="px-6 py-4 border-b border-zinc-800">
          <DialogTitle className="flex items-center justify-between">
            <span className="text-white">{document.filename}</span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onOpenChange(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {/* Horizontal Layout: Sidebar + Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Tabs Sidebar - Left */}
          <div className="w-44 border-r border-zinc-800 bg-zinc-900/50 p-3 flex flex-col gap-2">
            {availableTabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <Button
                  key={tab.value}
                  variant={activeTab === tab.value ? "default" : "ghost"}
                  className={`w-full justify-start ${
                    activeTab === tab.value
                      ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                      : "text-zinc-400 hover:text-white hover:bg-zinc-800"
                  }`}
                  onClick={() => setActiveTab(tab.value)}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {tab.label}
                </Button>
              );
            })}
          </div>

          {/* Content Area - Right */}
          <div className="flex-1 overflow-hidden p-4">
            {activeTabData?.value === "original" && activeTabData.content ? (
              <div className="h-full w-full rounded-lg border border-zinc-700 overflow-hidden bg-zinc-950">
                <iframe
                  src={`${apiUrl}/api/v1/documents/${document.id}/download`}
                  className="w-full h-full"
                  title={document.filename}
                />
              </div>
            ) : activeTabData?.value === "analysis" ? (
              <ScrollArea className="h-full">
                <pre className="rounded-lg bg-zinc-800 p-4 text-sm text-zinc-300 whitespace-pre-wrap break-words">
                  {typeof activeTabData.content === "string"
                    ? activeTabData.content
                    : JSON.stringify(activeTabData.content, null, 2)}
                </pre>
              </ScrollArea>
            ) : (
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between mb-4 flex-shrink-0">
                  <Badge variant="outline" className="text-zinc-400">
                    {(activeTabData?.content as string)?.length || 0} characters
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      activeTabData &&
                      handleDownload(activeTabData.value, activeTabData.content as string)
                    }
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </div>
                <ScrollArea className="flex-1">
                  <pre className="rounded-lg bg-zinc-800 p-4 text-sm text-zinc-300 whitespace-pre-wrap break-words">
                    {activeTabData?.content as string}
                  </pre>
                </ScrollArea>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
