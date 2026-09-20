import { Activity, BarChart3, Cpu, Grid2X2, LineChart, TrendingDown } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArchitectureSpecs } from "./ArchitectureSpecs";
import { ComparativeMetricsTable } from "./ComparativeMetricsTable";
import { ConfusionMatrix } from "./ConfusionMatrix";
import { LossGraph } from "./LossGraph";
import { MetricsRadar } from "./MetricsRadar";
import { ROCChart } from "./ROCChart";

export function BenchmarksHub() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div>
          <h2 className="text-2xl font-bold text-white font-mono tracking-tight">
            EMPIRICAL EVALUATION & BENCHMARKS HUB
          </h2>
          <p className="text-xs text-zinc-400">
            Comprehensive empirical metrics, confusion matrices, ROC curves, loss convergence, and
            training pipelines from reproducible ML runs.
          </p>
        </div>
      </div>

      <Tabs defaultValue="metrics" className="w-full space-y-6">
        <TabsList className="bg-zinc-900/80 border border-white/10 p-1 flex-wrap">
          <TabsTrigger value="metrics" className="text-xs font-mono flex items-center gap-2">
            <BarChart3 className="size-3.5" />
            Comparative Metrics
          </TabsTrigger>
          <TabsTrigger value="radar" className="text-xs font-mono flex items-center gap-2">
            <Activity className="size-3.5" />
            Metrics Radar
          </TabsTrigger>
          <TabsTrigger value="loss" className="text-xs font-mono flex items-center gap-2">
            <TrendingDown className="size-3.5" />
            Loss Convergence
          </TabsTrigger>
          <TabsTrigger value="confusion" className="text-xs font-mono flex items-center gap-2">
            <Grid2X2 className="size-3.5" />
            Confusion Matrix (2x2)
          </TabsTrigger>
          <TabsTrigger value="roc" className="text-xs font-mono flex items-center gap-2">
            <LineChart className="size-3.5" />
            ROC-AUC Curves
          </TabsTrigger>
          <TabsTrigger value="specs" className="text-xs font-mono flex items-center gap-2">
            <Cpu className="size-3.5" />
            Architecture Specs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="metrics" className="space-y-6">
          <ComparativeMetricsTable />
        </TabsContent>

        <TabsContent value="radar" className="space-y-6">
          <MetricsRadar />
        </TabsContent>

        <TabsContent value="loss" className="space-y-6">
          <LossGraph />
        </TabsContent>

        <TabsContent value="confusion" className="space-y-6">
          <ConfusionMatrix />
        </TabsContent>

        <TabsContent value="roc" className="space-y-6">
          <ROCChart />
        </TabsContent>

        <TabsContent value="specs" className="space-y-6">
          <ArchitectureSpecs />
        </TabsContent>
      </Tabs>
    </div>
  );
}
