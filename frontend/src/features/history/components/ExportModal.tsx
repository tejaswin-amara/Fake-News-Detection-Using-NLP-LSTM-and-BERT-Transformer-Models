import { Check, Copy, Download, FileCode, FileText } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { DualModelComparisonResult } from "@/types/inference";

interface ExportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: DualModelComparisonResult | null;
}

export function ExportModal({ open, onOpenChange, item }: ExportModalProps) {
  const [copied, setCopied] = useState(false);

  if (!item) return null;

  const jsonString = JSON.stringify(item, null, 2);

  const csvEscape = (str: string) => `"${(str || "").replace(/"/g, '""')}"`;
  const csvHeaders =
    "id,timestamp,model,verdict,confidence,probabilityReal,probabilityFake,latencyMs,paramCount,consensus,title";
  const csvRows = [
    item.bert
      ? [
          item.id,
          item.timestamp,
          "BERT",
          item.bert.verdict,
          item.bert.confidence,
          item.bert.probabilityReal,
          item.bert.probabilityFake,
          item.bert.latencyMs,
          csvEscape(item.bert.paramCount),
          item.consensus ?? "N/A",
          csvEscape(item.title || ""),
        ].join(",")
      : null,
    item.lstm
      ? [
          item.id,
          item.timestamp,
          "Bi-LSTM",
          item.lstm.verdict,
          item.lstm.confidence,
          item.lstm.probabilityReal,
          item.lstm.probabilityFake,
          item.lstm.latencyMs,
          csvEscape(item.lstm.paramCount),
          item.consensus ?? "N/A",
          csvEscape(item.title || ""),
        ].join(",")
      : null,
  ]
    .filter(Boolean)
    .join("\n");
  const csvString = `${csvHeaders}\n${csvRows}`;

  const markdownString = `# VERITAS AI Verification Audit Report

**ID:** \`${item.id}\`  
**Timestamp:** \`${item.timestamp}\`  
**Consensus:** **${item.consensus ?? "SINGLE MODEL"}**  
**Mode:** ${item.isSimulated ? "Simulated Local Fallback" : "Live API Inference"}  

## Article Metadata
- **Title:** ${item.title || "(Untitled Article)"}
- **Text Length:** ${item.text.length} characters (${item.text.split(/\s+/).filter(Boolean).length} words)

---

## Model Classification Breakdown

### 1. Fine-Tuned BERT Transformer
- **Verdict:** **${item.bert?.verdict ?? "N/A"}**
- **Confidence:** ${item.bert ? `${(item.bert.confidence * 100).toFixed(2)}%` : "N/A"}
- **Probability Real:** ${item.bert ? `${(item.bert.probabilityReal * 100).toFixed(2)}%` : "N/A"}
- **Probability Deceptive:** ${item.bert ? `${(item.bert.probabilityFake * 100).toFixed(2)}%` : "N/A"}
- **Latency:** ${item.bert ? `${item.bert.latencyMs} ms` : "N/A"}
- **Parameter Size:** ${item.bert?.paramCount ?? "N/A"}

### 2. GloVe + Stacked Bi-LSTM
- **Verdict:** **${item.lstm?.verdict ?? "N/A"}**
- **Confidence:** ${item.lstm ? `${(item.lstm.confidence * 100).toFixed(2)}%` : "N/A"}
- **Probability Real:** ${item.lstm ? `${(item.lstm.probabilityReal * 100).toFixed(2)}%` : "N/A"}
- **Probability Deceptive:** ${item.lstm ? `${(item.lstm.probabilityFake * 100).toFixed(2)}%` : "N/A"}
- **Latency:** ${item.lstm ? `${item.lstm.latencyMs} ms` : "N/A"}
- **Parameter Size:** ${item.lstm?.paramCount ?? "N/A"}

---

## Article Content Analyzed
> ${item.text.slice(0, 1000)}${item.text.length > 1000 ? "... [truncated]" : ""}
`;

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="glass-panel-elevated max-w-2xl text-white border border-white/10 rounded-2xl">
        <DialogHeader>
          <DialogTitle className="font-mono text-lg font-bold flex items-center gap-2">
            EXPORT AUDIT REPORT
          </DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Export structured prediction records for compliance, governance, and audit trails.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="markdown" className="w-full">
          <TabsList className="bg-zinc-900 border border-white/10 w-full justify-start flex-wrap relative z-10">
            <TabsTrigger value="markdown" className="text-xs font-mono flex items-center gap-2">
              <FileText className="size-3.5" />
              Markdown Summary (.md)
            </TabsTrigger>
            <TabsTrigger value="json" className="text-xs font-mono flex items-center gap-2">
              <FileCode className="size-3.5" />
              Raw JSON (.json)
            </TabsTrigger>
            <TabsTrigger value="csv" className="text-xs font-mono flex items-center gap-2">
              <Download className="size-3.5" />
              Spreadsheet CSV (.csv)
            </TabsTrigger>
          </TabsList>

          <TabsContent value="markdown" className="space-y-4 pt-2">
            <div className="bg-zinc-950 p-3 rounded-xl border border-white/10 max-h-72 overflow-y-auto font-mono text-xs text-zinc-300 whitespace-pre-wrap">
              {markdownString}
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(markdownString)}
                className="text-xs font-mono border-white/10"
              >
                {copied ? (
                  <Check className="size-3.5 mr-1 text-emerald-400" />
                ) : (
                  <Copy className="size-3.5 mr-1" />
                )}
                {copied ? "Copied" : "Copy Markdown"}
              </Button>
              <Button
                size="sm"
                onClick={() =>
                  handleDownload(markdownString, `audit-${item.id}.md`, "text/markdown")
                }
                className="text-xs font-mono bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                <Download className="size-3.5 mr-1" />
                Download .md
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="json" className="space-y-4 pt-2">
            <div className="bg-zinc-950 p-3 rounded-xl border border-white/10 max-h-72 overflow-y-auto font-mono text-xs text-zinc-300 whitespace-pre">
              {jsonString}
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(jsonString)}
                className="text-xs font-mono border-white/10"
              >
                {copied ? (
                  <Check className="size-3.5 mr-1 text-emerald-400" />
                ) : (
                  <Copy className="size-3.5 mr-1" />
                )}
                {copied ? "Copied" : "Copy JSON"}
              </Button>
              <Button
                size="sm"
                onClick={() =>
                  handleDownload(jsonString, `audit-${item.id}.json`, "application/json")
                }
                className="text-xs font-mono bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                <Download className="size-3.5 mr-1" />
                Download .json
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="csv" className="space-y-4 pt-2">
            <div className="bg-zinc-950 p-3 rounded-xl border border-white/10 max-h-72 overflow-y-auto font-mono text-xs text-zinc-300 whitespace-pre">
              {csvString}
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(csvString)}
                className="text-xs font-mono border-white/10"
              >
                {copied ? (
                  <Check className="size-3.5 mr-1 text-emerald-400" />
                ) : (
                  <Copy className="size-3.5 mr-1" />
                )}
                {copied ? "Copied" : "Copy CSV"}
              </Button>
              <Button
                size="sm"
                onClick={() => handleDownload(csvString, `audit-${item.id}.csv`, "text/csv")}
                className="text-xs font-mono bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                <Download className="size-3.5 mr-1" />
                Download .csv
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
