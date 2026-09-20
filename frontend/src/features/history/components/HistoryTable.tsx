import { Clock, Download, Eye, Trash2 } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { DualModelComparisonResult } from "@/types/inference";
import { useHistoryStore } from "../store/historyStore";
import { ExportModal } from "./ExportModal";

interface HistoryTableProps {
  onSelectRecord?: (record: DualModelComparisonResult) => void;
}

export function HistoryTable({ onSelectRecord }: HistoryTableProps) {
  const { history, removeRecord, clearAll } = useHistoryStore();
  const [selectedForExport, setSelectedForExport] = useState<DualModelComparisonResult | null>(
    null
  );

  if (history.length === 0) {
    return (
      <div className="glass-panel p-10 rounded-2xl border border-white/10 text-center space-y-3">
        <Clock className="size-8 text-zinc-500 mx-auto" />
        <h4 className="text-base font-mono font-bold text-white">NO INFERENCE AUDIT RECORDS YET</h4>
        <p className="text-xs text-zinc-400 max-w-md mx-auto">
          Analyses executed in the Inference Studio are automatically indexed and encrypted in your
          local session. Run an inference above to generate your first audit record.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white font-mono tracking-tight">
            PERSISTENT LOCAL INFERENCE AUDIT TRAIL
          </h3>
          <p className="text-xs text-zinc-400">
            {history.length} verification events stored in browser localStorage.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={clearAll}
          className="text-xs font-mono border-rose-500/30 text-rose-400 hover:bg-rose-500/10"
        >
          <Trash2 className="size-3.5 mr-1" />
          Clear Trail
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-zinc-900/60 text-zinc-400 uppercase text-[10px]">
              <th className="p-3">Timestamp</th>
              <th className="p-3">Headline / Excerpt</th>
              <th className="p-3">BERT Verdict</th>
              <th className="p-3">Bi-LSTM Verdict</th>
              <th className="p-3">Consensus</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {history.map((item) => {
              const bertVerdict = item.bert?.verdict;
              const lstmVerdict = item.lstm?.verdict;
              const isConsensus = item.consensus === "AGREEMENT";

              return (
                <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="p-3 whitespace-nowrap text-zinc-400 text-[11px]">
                    {new Date(item.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </td>
                  <td className="p-3 max-w-xs">
                    <div className="font-bold text-white truncate">
                      {item.title || "Untitled Article"}
                    </div>
                    <div className="text-zinc-500 truncate text-[11px]">{item.text}</div>
                  </td>
                  <td className="p-3 whitespace-nowrap">
                    {bertVerdict ? (
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          bertVerdict === "REAL"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                            : bertVerdict === "FAKE"
                              ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                              : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                        }`}
                      >
                        {bertVerdict} ({((item.bert?.confidence ?? 0) * 100).toFixed(0)}%)
                      </span>
                    ) : (
                      <span className="text-zinc-600">—</span>
                    )}
                  </td>
                  <td className="p-3 whitespace-nowrap">
                    {lstmVerdict ? (
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          lstmVerdict === "REAL"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                            : lstmVerdict === "FAKE"
                              ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                              : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                        }`}
                      >
                        {lstmVerdict} ({((item.lstm?.confidence ?? 0) * 100).toFixed(0)}%)
                      </span>
                    ) : (
                      <span className="text-zinc-600">—</span>
                    )}
                  </td>
                  <td className="p-3 whitespace-nowrap">
                    {item.consensus ? (
                      <Badge
                        variant="outline"
                        className={`text-[10px] ${
                          isConsensus
                            ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                            : "border-amber-500/30 text-amber-400 bg-amber-500/10"
                        }`}
                      >
                        {isConsensus ? "AGREEMENT" : "DIVERGENCE"}
                      </Badge>
                    ) : (
                      <span className="text-zinc-500 text-[10px]">Single Model</span>
                    )}
                  </td>
                  <td className="p-3 text-right whitespace-nowrap space-x-1">
                    {onSelectRecord && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onSelectRecord(item)}
                        title="Re-examine analysis"
                        className="h-7 w-7 p-0 text-zinc-400 hover:text-white"
                      >
                        <Eye className="size-3.5" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedForExport(item)}
                      title="Export report"
                      className="h-7 w-7 p-0 text-zinc-400 hover:text-indigo-400"
                    >
                      <Download className="size-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeRecord(item.id)}
                      title="Delete record"
                      className="h-7 w-7 p-0 text-zinc-400 hover:text-rose-400"
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <ExportModal
        open={Boolean(selectedForExport)}
        onOpenChange={(open) => !open && setSelectedForExport(null)}
        item={selectedForExport}
      />
    </div>
  );
}
