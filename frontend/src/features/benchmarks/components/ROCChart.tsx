import { useState } from "react";
import { BENCHMARK_MODELS } from "../data/benchmarksData";

export function ROCChart() {
  const [activeModelKey, setActiveModelKey] = useState<string | null>(null);

  const width = 500;
  const height = 300;
  const padding = 45;

  const innerW = width - padding * 2;
  const innerH = height - padding * 2;

  // Convert (fpr, tpr) to SVG (x, y)
  const toSvgCoords = (fpr: number, tpr: number) => {
    const x = padding + fpr * innerW;
    const y = height - padding - tpr * innerH;
    return `${x},${y}`;
  };

  const getPathData = (points: Array<{ fpr: number; tpr: number }>) => {
    return points.reduce((acc, pt, index) => {
      const coord = toSvgCoords(pt.fpr, pt.tpr);
      return index === 0 ? `M ${coord}` : `${acc} L ${coord}`;
    }, "");
  };

  const colors = [
    { stroke: "#818cf8", glow: "rgba(129, 140, 248, 0.5)", name: "BERT Transformer" },
    { stroke: "#fb7185", glow: "rgba(251, 113, 133, 0.5)", name: "Bi-LSTM" },
    { stroke: "#34d399", glow: "rgba(52, 211, 153, 0.5)", name: "L2 Champion" },
    { stroke: "#fbbf24", glow: "rgba(251, 191, 36, 0.5)", name: "XGBoost" },
  ];

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white font-mono tracking-tight">
            RECEIVER OPERATING CHARACTERISTIC (ROC) CURVES
          </h3>
          <p className="text-xs text-zinc-400">
            True Positive Rate vs. False Positive Rate across classification threshold variations.
          </p>
        </div>
      </div>

      <div className="relative flex justify-center overflow-x-auto py-2">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full max-w-lg overflow-visible font-mono text-[10px]"
          role="img"
          aria-label="ROC Curve Comparison Chart"
        >
          {/* Grid lines */}
          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={height - padding}
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth="1.5"
          />
          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={height - padding}
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth="1.5"
          />

          {/* Diagonal Random Chance line (AUC = 0.50) */}
          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={padding}
            stroke="rgba(255, 255, 255, 0.15)"
            strokeDasharray="4 4"
            strokeWidth="1"
          />

          {/* Model Curves */}
          {BENCHMARK_MODELS.map((model, idx) => {
            const color = colors[idx] ?? colors[0];
            const isFaded = activeModelKey !== null && activeModelKey !== model.name;
            const isHighlight = activeModelKey === model.name;

            return (
              <g
                key={model.name}
                className="transition-opacity duration-200"
                style={{ opacity: isFaded ? 0.2 : 1 }}
              >
                <path
                  d={getPathData(model.rocCurve)}
                  fill="none"
                  stroke={color.stroke}
                  strokeWidth={isHighlight ? "3.5" : "2"}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    filter: isHighlight ? `drop-shadow(0 0 8px ${color.glow})` : undefined,
                  }}
                />
              </g>
            );
          })}

          {/* Axis labels */}
          <text x={width / 2} y={height - 10} fill="#a1a1aa" textAnchor="middle">
            False Positive Rate (1 - Specificity)
          </text>
          <text
            x={15}
            y={height / 2}
            fill="#a1a1aa"
            textAnchor="middle"
            transform={`rotate(-90 15 ${height / 2})`}
          >
            True Positive Rate (Sensitivity)
          </text>
        </svg>
      </div>

      {/* Interactive Legend */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-white/5 font-mono text-xs">
        {BENCHMARK_MODELS.map((model, idx) => {
          const color = colors[idx] ?? colors[0];
          const isSelected = activeModelKey === model.name;

          return (
            <button
              key={model.name}
              type="button"
              onMouseEnter={() => setActiveModelKey(model.name)}
              onMouseLeave={() => setActiveModelKey(null)}
              onClick={() => setActiveModelKey(isSelected ? null : model.name)}
              className={`p-2 rounded-lg border text-left transition-all ${
                isSelected
                  ? "bg-zinc-800/90 border-white/30 shadow-lg"
                  : "bg-zinc-900/40 border-white/5 hover:border-white/20"
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: color.stroke }}
                />
                <span className="text-[11px] font-bold text-zinc-200 truncate">{color.name}</span>
              </div>
              <div className="text-[11px] text-zinc-400">
                AUC: <span className="text-white font-bold">{model.rocAuc.toFixed(4)}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
