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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
    const a = document.createElement("a");
    a.href = url;
    a.download = `${document.filename.replace(".pdf", "")}_${type}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[80vh] bg-zinc-900 border-zinc-800">
        <DialogHeader>
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

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col"
        >
          <TabsList className="bg-zinc-800 border-zinc-700">
            {availableTabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <TabsTrigger
                  key={tab.value}
                  value={tab.value}
                  className="data-[state=active]:bg-zinc-700"
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {tab.label}
                </TabsTrigger>
              );
            })}
          </TabsList>

          {availableTabs.map((tab) => (
            <TabsContent
              key={tab.value}
              value={tab.value}
              className="flex-1 mt-4"
            >
              {tab.value === "original" && tab.content ? (
                <div className="flex flex-col items-center justify-center h-full space-y-4">
                  <FileText className="h-16 w-16 text-zinc-600" />
                  <p className="text-zinc-400">PDF Preview not available</p>
                  <Button
                    variant="outline"
                    onClick={() => {
                      // Open PDF in new tab
                      const apiUrl =
                        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                      window.open(
                        `${apiUrl}/api/v1/documents/${document.id}/download`,
                        "_blank"
                      );
                    }}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF
                  </Button>
                </div>
              ) : tab.value === "analysis" ? (
                <ScrollArea className="h-full">
                  <pre className="rounded-lg bg-zinc-800 p-4 text-sm text-zinc-300">
                    {typeof tab.content === "string"
                      ? tab.content
                      : JSON.stringify(tab.content, null, 2)}
                  </pre>
                </ScrollArea>
              ) : (
                <div className="flex flex-col h-full">
                  <div className="flex items-center justify-between mb-4">
                    <Badge variant="outline" className="text-zinc-400">
                      {(tab.content as string)?.length || 0} characters
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        handleDownload(tab.value, tab.content as string)
                      }
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                  <ScrollArea className="flex-1">
                    <pre className="rounded-lg bg-zinc-800 p-4 text-sm text-zinc-300 whitespace-pre-wrap">
                      {tab.content as string}
                    </pre>
                  </ScrollArea>
                </div>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

