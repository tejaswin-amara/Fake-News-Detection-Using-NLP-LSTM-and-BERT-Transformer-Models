import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { BENCHMARK_MODELS } from "../data/benchmarksData";

interface MetricDimension {
  key: "accuracy" | "precision" | "recall" | "f1Score" | "rocAuc";
  label: string;
}

const DIMENSIONS: MetricDimension[] = [
  { key: "accuracy", label: "Accuracy" },
  { key: "precision", label: "Precision" },
  { key: "recall", label: "Recall" },
  { key: "f1Score", label: "F1-Score" },
  { key: "rocAuc", label: "ROC-AUC" },
];

const MODEL_COLORS: Record<string, { stroke: string; fill: string; dot: string; text: string }> = {
  "Fine-Tuned BERT (bert-base-uncased)": {
    stroke: "#818cf8", // indigo-400
    fill: "rgba(129, 140, 248, 0.25)",
    dot: "#6366f1",
    text: "text-indigo-400",
  },
  "GloVe + Stacked BiLSTM": {
    stroke: "#fbbf24", // amber-400
    fill: "rgba(251, 191, 36, 0.25)",
    dot: "#f59e0b",
    text: "text-amber-400",
  },
  "TF-IDF + Logistic Regression (L2 - Champion)": {
    stroke: "#34d399", // emerald-400
    fill: "rgba(52, 211, 153, 0.2)",
    dot: "#10b981",
    text: "text-emerald-400",
  },
};

export function MetricsRadar() {
  const [selectedModels, setSelectedModels] = useState<string[]>([
    "Fine-Tuned BERT (bert-base-uncased)",
    "GloVe + Stacked BiLSTM",
    "TF-IDF + Logistic Regression (L2 - Champion)",
  ]);
  const [hoveredPoint, setHoveredPoint] = useState<{
    model: string;
    metric: string;
    val: number;
    x: number;
    y: number;
  } | null>(null);

  const cx = 175;
  const cy = 160;
  const radius = 110;
  const numDimensions = DIMENSIONS.length;

  const getCoordinates = (dimensionIndex: number, value: number) => {
    // Top axis at index 0: angle = -PI / 2
    const angle = (dimensionIndex * 2 * Math.PI) / numDimensions - Math.PI / 2;
    const r = radius * value;
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  };

  const toggleModel = (name: string) => {
    if (selectedModels.includes(name)) {
      if (selectedModels.length > 1) {
        setSelectedModels(selectedModels.filter((m) => m !== name));
      }
    } else {
      setSelectedModels([...selectedModels, name]);
    }
  };

  // Concentric polygon grids (20%, 40%, 60%, 80%, 100%)
  const gridLevels = [0.2, 0.4, 0.6, 0.8, 1.0];

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold font-mono tracking-tight text-white">
            MULTI-DIMENSIONAL ARCHITECTURE RADAR
          </h3>
          <p className="text-xs text-zinc-400">
            Pentagonal cross-metric comparative analysis: Accuracy, Precision, Recall, F1, and
            AUC-ROC.
          </p>
        </div>

        {/* Model Toggle Chips */}
        <div className="flex flex-wrap gap-2">
          {BENCHMARK_MODELS.slice(0, 3).map((m) => {
            const isSelected = selectedModels.includes(m.name);
            const colors = MODEL_COLORS[m.name];
            return (
              <button
                key={m.name}
                type="button"
                onClick={() => toggleModel(m.name)}
                className={`px-3 py-1 rounded-lg text-xs font-mono border transition-all cursor-pointer flex items-center gap-1.5 ${
                  isSelected
                    ? "bg-zinc-900 border-white/30 text-white font-bold"
                    : "bg-zinc-950/40 border-white/5 text-zinc-500 opacity-60"
                }`}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: colors?.stroke ?? "#fff" }}
                />
                <span className="truncate max-w-[140px]">{m.name.split(" ")[0]}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex flex-col lg:flex-row items-center justify-center gap-8">
        {/* Radar SVG */}
        <div className="relative w-[350px] h-[320px] shrink-0 select-none">
          <svg viewBox="0 0 350 320" className="w-full h-full overflow-visible" role="img">
            <title>Multi-Dimensional Model Metrics Radar</title>
            {/* Concentric Web Grid */}
            {gridLevels.map((lvl) => {
              const points = DIMENSIONS.map((_, i) => {
                const { x, y } = getCoordinates(i, lvl);
                return `${x},${y}`;
              }).join(" ");
              return (
                <polygon
                  key={lvl}
                  points={points}
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="1"
                />
              );
            })}

            {/* Radial Axes */}
            {DIMENSIONS.map((dim, i) => {
              const { x, y } = getCoordinates(i, 1.0);
              const labelCoord = getCoordinates(i, 1.22);
              return (
                <g key={dim.key}>
                  <line
                    x1={cx}
                    y1={cy}
                    x2={x}
                    y2={y}
                    stroke="rgba(255, 255, 255, 0.12)"
                    strokeDasharray="2,2"
                  />
                  <text
                    x={labelCoord.x}
                    y={labelCoord.y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-[10px] font-mono fill-zinc-400 font-semibold"
                  >
                    {dim.label}
                  </text>
                </g>
              );
            })}

            {/* Render Model Radar Polygons */}
            {BENCHMARK_MODELS.filter((m) => selectedModels.includes(m.name)).map((m) => {
              const colors = MODEL_COLORS[m.name];
              const pointsStr = DIMENSIONS.map((dim, i) => {
                const val = m[dim.key] as number;
                const { x, y } = getCoordinates(i, val);
                return `${x},${y}`;
              }).join(" ");

              return (
                <g key={m.name}>
                  <polygon
                    points={pointsStr}
                    fill={colors?.fill ?? "rgba(255,255,255,0.1)"}
                    stroke={colors?.stroke ?? "#fff"}
                    strokeWidth="2"
                    className="transition-all duration-300"
                  />
                  {DIMENSIONS.map((dim, i) => {
                    const val = m[dim.key] as number;
                    const { x, y } = getCoordinates(i, val);
                    return (
                      // biome-ignore lint/a11y/noStaticElementInteractions: hover telemetry for radar vertices
                      <circle
                        key={dim.key}
                        cx={x}
                        cy={y}
                        r="3.5"
                        fill={colors?.dot ?? "#fff"}
                        stroke="#09090b"
                        strokeWidth="1.5"
                        className="cursor-pointer transition-transform hover:scale-150"
                        onMouseEnter={() =>
                          setHoveredPoint({ model: m.name, metric: dim.label, val, x, y })
                        }
                        onMouseLeave={() => setHoveredPoint(null)}
                      />
                    );
                  })}
                </g>
              );
            })}
          </svg>

          {/* Floating Hover Tooltip */}
          {hoveredPoint && (
            <div
              className="pointer-events-none absolute z-20 px-2 py-1 bg-zinc-950/95 border border-white/20 rounded-md font-mono text-[10px] text-white shadow-xl -translate-x-1/2 -translate-y-full mb-2"
              style={{ left: hoveredPoint.x, top: hoveredPoint.y }}
            >
              <div className="font-bold">{hoveredPoint.model.split(" ")[0]}</div>
              <div className="text-zinc-400">
                {hoveredPoint.metric}:{" "}
                <span className="text-emerald-400 font-bold">
                  {(hoveredPoint.val * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Legend & Breakdown Table */}
        <div className="flex-1 w-full space-y-3 font-mono text-xs">
          <div className="grid grid-cols-6 text-zinc-500 text-[10px] uppercase border-b border-white/10 pb-2">
            <span className="col-span-2">Model Architecture</span>
            <span className="text-right">Acc</span>
            <span className="text-right">Prec</span>
            <span className="text-right">Rec</span>
            <span className="text-right">AUC</span>
          </div>

          {BENCHMARK_MODELS.slice(0, 3).map((m) => {
            const isSelected = selectedModels.includes(m.name);
            const colors = MODEL_COLORS[m.name];
            return (
              <div
                key={m.name}
                className={`grid grid-cols-6 py-1.5 px-2 rounded-lg items-center transition-colors ${
                  isSelected ? "bg-zinc-900/60 text-white" : "opacity-40 text-zinc-500"
                }`}
              >
                <div className="col-span-2 flex items-center gap-2 truncate">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: colors?.stroke ?? "#fff" }}
                  />
                  <span className="truncate font-semibold">{m.name.split(" ")[0]}</span>
                  {m.isChampion && (
                    <Badge
                      variant="outline"
                      className="text-[9px] py-0 px-1 text-emerald-400 border-emerald-500/30"
                    >
                      Top
                    </Badge>
                  )}
                </div>
                <span className="text-right text-zinc-300">{(m.accuracy * 100).toFixed(1)}%</span>
                <span className="text-right text-zinc-300">{(m.precision * 100).toFixed(1)}%</span>
                <span className="text-right text-zinc-300">{(m.recall * 100).toFixed(1)}%</span>
                <span className="text-right text-indigo-400 font-bold">
                  {(m.rocAuc * 100).toFixed(1)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default MetricsRadar;
