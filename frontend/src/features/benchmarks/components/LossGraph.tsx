import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface EpochPoint {
  epoch: number;
  trainLoss: number;
  valLoss: number;
  valAccuracy: number;
}

const BERT_EPOCH_DATA: EpochPoint[] = [
  { epoch: 1, trainLoss: 0.542, valLoss: 0.384, valAccuracy: 0.842 },
  { epoch: 2, trainLoss: 0.312, valLoss: 0.276, valAccuracy: 0.881 },
  { epoch: 3, trainLoss: 0.218, valLoss: 0.245, valAccuracy: 0.892 },
  { epoch: 4, trainLoss: 0.165, valLoss: 0.238, valAccuracy: 0.895 },
  { epoch: 5, trainLoss: 0.124, valLoss: 0.252, valAccuracy: 0.891 }, // Slight overfit inflection point
];

const LSTM_EPOCH_DATA: EpochPoint[] = [
  { epoch: 1, trainLoss: 0.685, valLoss: 0.612, valAccuracy: 0.685 },
  { epoch: 2, trainLoss: 0.542, valLoss: 0.495, valAccuracy: 0.748 },
  { epoch: 3, trainLoss: 0.448, valLoss: 0.421, valAccuracy: 0.792 },
  { epoch: 4, trainLoss: 0.382, valLoss: 0.385, valAccuracy: 0.812 },
  { epoch: 5, trainLoss: 0.335, valLoss: 0.362, valAccuracy: 0.825 },
  { epoch: 6, trainLoss: 0.298, valLoss: 0.348, valAccuracy: 0.832 },
  { epoch: 7, trainLoss: 0.271, valLoss: 0.345, valAccuracy: 0.831 },
  { epoch: 8, trainLoss: 0.248, valLoss: 0.352, valAccuracy: 0.829 },
  { epoch: 9, trainLoss: 0.229, valLoss: 0.365, valAccuracy: 0.826 },
  { epoch: 10, trainLoss: 0.212, valLoss: 0.381, valAccuracy: 0.822 },
];

export function LossGraph() {
  const [selectedModel, setSelectedModel] = useState<"bert" | "lstm">("bert");
  const [hoveredEpoch, setHoveredEpoch] = useState<EpochPoint | null>(null);

  const data = selectedModel === "bert" ? BERT_EPOCH_DATA : LSTM_EPOCH_DATA;
  const numEpochs = data.length;

  const width = 580;
  const height = 260;
  const padding = { top: 25, right: 35, bottom: 45, left: 45 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const maxLoss = 0.75;
  const minLoss = 0.0;

  const getX = (epoch: number) => {
    return padding.left + ((epoch - 1) / (numEpochs - 1)) * plotWidth;
  };

  const getY = (loss: number) => {
    return padding.top + plotHeight - ((loss - minLoss) / (maxLoss - minLoss)) * plotHeight;
  };

  // Build SVG path strings
  const trainPath = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${getX(d.epoch)} ${getY(d.trainLoss)}`)
    .join(" ");

  const valPath = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${getX(d.epoch)} ${getY(d.valLoss)}`)
    .join(" ");

  const trainArea = `${trainPath} L ${getX(data[data.length - 1].epoch)} ${getY(0)} L ${getX(data[0].epoch)} ${getY(0)} Z`;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold font-mono tracking-tight text-white">
            TRAINING & VALIDATION LOSS CONVERGENCE
          </h3>
          <p className="text-xs text-zinc-400">
            Empirical loss trajectories across training epochs showing gradient stability and
            regularization.
          </p>
        </div>

        <Tabs
          value={selectedModel}
          onValueChange={(val) => setSelectedModel(val as "bert" | "lstm")}
          className="w-auto"
        >
          <TabsList className="bg-zinc-900 border border-white/10 p-1">
            <TabsTrigger value="bert" className="text-xs font-mono">
              BERT (5 Epochs)
            </TabsTrigger>
            <TabsTrigger value="lstm" className="text-xs font-mono">
              Bi-LSTM (10 Epochs)
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="flex flex-col lg:flex-row items-center gap-6">
        {/* SVG Chart */}
        <div className="w-full max-w-[580px] relative select-none">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="w-full h-auto overflow-visible"
            role="img"
          >
            <title>Training and Validation Loss Trajectories</title>
            <defs>
              <linearGradient id="trainGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#818cf8" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#818cf8" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Grid horizontal lines */}
            {[0.2, 0.4, 0.6].map((tick) => {
              const y = getY(tick);
              return (
                <g key={tick}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={width - padding.right}
                    y2={y}
                    stroke="rgba(255,255,255,0.08)"
                    strokeDasharray="3,3"
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 3}
                    textAnchor="end"
                    className="text-[10px] font-mono fill-zinc-500"
                  >
                    {tick.toFixed(1)}
                  </text>
                </g>
              );
            })}

            {/* Epoch X-axis ticks */}
            {data.map((d) => {
              const x = getX(d.epoch);
              return (
                <g key={d.epoch}>
                  <line
                    x1={x}
                    y1={height - padding.bottom}
                    x2={x}
                    y2={height - padding.bottom + 5}
                    stroke="rgba(255,255,255,0.2)"
                  />
                  <text
                    x={x}
                    y={height - padding.bottom + 18}
                    textAnchor="middle"
                    className="text-[10px] font-mono fill-zinc-400"
                  >
                    E{d.epoch}
                  </text>
                </g>
              );
            })}

            {/* Shaded Area under Training Loss */}
            <path d={trainArea} fill="url(#trainGrad)" />

            {/* Training Loss Line */}
            <path d={trainPath} fill="none" stroke="#818cf8" strokeWidth="2.5" />

            {/* Validation Loss Line */}
            <path
              d={valPath}
              fill="none"
              stroke="#fb7185"
              strokeWidth="2.5"
              strokeDasharray="4,3"
            />

            {/* Data Points */}
            {data.map((d) => {
              const x = getX(d.epoch);
              const trainY = getY(d.trainLoss);
              const valY = getY(d.valLoss);
              return (
                // biome-ignore lint/a11y/noStaticElementInteractions: hover telemetry for loss data points
                <g
                  key={d.epoch}
                  onMouseEnter={() => setHoveredEpoch(d)}
                  onMouseLeave={() => setHoveredEpoch(null)}
                  className="cursor-pointer"
                >
                  <circle
                    cx={x}
                    cy={trainY}
                    r="4"
                    fill="#818cf8"
                    stroke="#09090b"
                    strokeWidth="1.5"
                  />
                  <circle
                    cx={x}
                    cy={valY}
                    r="4"
                    fill="#fb7185"
                    stroke="#09090b"
                    strokeWidth="1.5"
                  />
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div className="flex items-center justify-center gap-6 mt-3 font-mono text-xs">
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-indigo-400" />
              <span className="text-zinc-300">Training Loss (Cross-Entropy)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-rose-400 border-t border-dashed" />
              <span className="text-zinc-300">Validation Loss (Holdout)</span>
            </div>
          </div>
        </div>

        {/* Telemetry / Detail Card */}
        <div className="flex-1 w-full p-4 rounded-xl bg-zinc-900/50 border border-white/5 space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 uppercase text-[11px] font-bold">
              {hoveredEpoch ? `Epoch ${hoveredEpoch.epoch} Telemetry` : "Checkpoint Summary"}
            </span>
            <Badge variant="outline" className="text-[10px] text-indigo-300 border-indigo-500/30">
              {selectedModel === "bert" ? "AdamW (lr=2e-5)" : "Adam (lr=1e-3)"}
            </Badge>
          </div>

          <div className="space-y-2 pt-1">
            <div className="flex justify-between items-center text-zinc-300">
              <span>Train Loss:</span>
              <span className="font-bold text-indigo-400">
                {hoveredEpoch
                  ? hoveredEpoch.trainLoss.toFixed(3)
                  : data[data.length - 1].trainLoss.toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span>Validation Loss:</span>
              <span className="font-bold text-rose-400">
                {hoveredEpoch
                  ? hoveredEpoch.valLoss.toFixed(3)
                  : data[data.length - 1].valLoss.toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span>Validation Accuracy:</span>
              <span className="font-bold text-emerald-400">
                {(
                  (hoveredEpoch ? hoveredEpoch.valAccuracy : data[data.length - 1].valAccuracy) *
                  100
                ).toFixed(1)}
                %
              </span>
            </div>
          </div>

          <p className="text-[11px] text-zinc-400 pt-2 border-t border-white/5 italic leading-relaxed">
            {selectedModel === "bert"
              ? "Early stopping triggered at Epoch 4 before overfitting inflection on deceptive stylistic tokens."
              : "Gradient clipping at norm 1.0 prevented exploding recurrent gates across extended sequence lengths."}
          </p>
        </div>
      </div>
    </div>
  );
}

export default LossGraph;
