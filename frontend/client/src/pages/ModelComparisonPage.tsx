import { StatusBadge } from "@/components/StatusBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { trpc } from "@/lib/trpc";
import { Award, Cpu, Database, Gauge, GitCompare, HardDrive, Info, Layers, ShieldCheck, Zap } from "lucide-react";

export default function ModelComparisonPage() {
  const modelCompQuery = trpc.dashboard.reports.get.useQuery({ name: "model_comparison" });
  const linearCompQuery = trpc.dashboard.reports.get.useQuery({ name: "linear_models_comparison" });
  const treeCompQuery = trpc.dashboard.reports.get.useQuery({ name: "tree_models_comparison" });
  const championQuery = trpc.dashboard.reports.get.useQuery({ name: "champion_model" });

  const modelComp = (modelCompQuery.data ?? {}) as Record<string, any>;
  const linearComp = (linearCompQuery.data ?? {}) as Record<string, any>;
  const treeComp = (treeCompQuery.data ?? {}) as Record<string, any>;
  const champion = (championQuery.data ?? {}) as Record<string, any>;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Header */}
      <section className="flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-end">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold tracking-[0.16em] text-primary">CO2 • CO3 • CO6</span>
            <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary text-[11px]">
              MODEL HIERARCHY
            </Badge>
          </div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Model Comparison & Champion Selection</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Empirical evaluation across linear baselines (M2), tree ensembles (M3), deep learning architectures,
            and multi-criteria operational trade-offs for production deployment.
          </p>
        </div>
        {champion?.model_name && (
          <div className="flex items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3">
            <Award className="h-6 w-6 text-emerald-600" />
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-800">Production Champion</p>
              <p className="text-sm font-extrabold text-emerald-900">{champion.model_name}</p>
            </div>
          </div>
        )}
      </section>

      {/* Primary Multi-Attribute Comparison Table */}
      <Card className="data-card border-border bg-card">
        <CardHeader>
          <CardTitle className="text-lg">Full Capstone Model Comparison Matrix</CardTitle>
          <CardDescription>
            Direct empirical comparison between Classical ML, Tree Ensembles, Recurrent GloVe BiLSTM, and Fine-Tuned BERT.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="py-3 px-4">Architecture</th>
                  <th className="py-3 px-4">Family</th>
                  <th className="py-3 px-3 text-right">F1-Score</th>
                  <th className="py-3 px-3 text-right">ROC-AUC</th>
                  <th className="py-3 px-3 text-right">Brier Score</th>
                  <th className="py-3 px-3 text-right">Latency (p95)</th>
                  <th className="py-3 px-3 text-right">Size</th>
                  <th className="py-3 px-3 text-right">RAM</th>
                  <th className="py-3 px-4">Interpretability</th>
                  <th className="py-3 px-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {Object.entries(modelComp).map(([name, m]: [string, any]) => {
                  const isChamp = m.selected_as_champion;
                  return (
                    <tr key={name} className={isChamp ? "bg-emerald-500/5 font-medium" : "hover:bg-muted/20"}>
                      <td className="py-3.5 px-4 font-semibold">
                        <div className="flex items-center gap-2">
                          {isChamp && <Award className="h-4 w-4 text-emerald-600 flex-shrink-0" />}
                          <span>{name}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-muted-foreground">{m.family}</td>
                      <td className="py-3.5 px-3 text-right font-mono font-bold text-foreground">
                        {m.f1_score ? m.f1_score.toFixed(3) : "—"}
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono text-muted-foreground">
                        {m.roc_auc ? m.roc_auc.toFixed(3) : "—"}
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono text-muted-foreground">
                        {m.brier_score ? m.brier_score.toFixed(3) : "—"}
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono">
                        <span className={m.inference_latency_ms < 5 ? "text-emerald-600 font-bold" : m.inference_latency_ms > 50 ? "text-red-600 font-bold" : "text-foreground"}>
                          {m.inference_latency_ms} ms
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono text-muted-foreground">
                        {m.model_size_mb} MB
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono text-muted-foreground">
                        {m.ram_footprint_mb} MB
                      </td>
                      <td className="py-3.5 px-4 text-xs text-muted-foreground max-w-[200px] truncate" title={m.interpretability}>
                        {m.interpretability}
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        {isChamp ? (
                          <Badge className="bg-emerald-600 text-white text-[10px]">CHAMPION</Badge>
                        ) : (
                          <Badge variant="outline" className="text-[10px] text-muted-foreground">BASELINE</Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Tabs: Linear vs Tree Detailed Modules */}
      <Tabs defaultValue="linear" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="linear">Linear Regularization (M2)</TabsTrigger>
          <TabsTrigger value="trees">Tree Ensembles (M3)</TabsTrigger>
        </TabsList>

        {/* Tab 1: Linear Models */}
        <TabsContent value="linear" className="mt-4 space-y-4">
          <Card className="data-card border-border bg-card">
            <CardHeader>
              <CardTitle className="text-base">M2: Linear Models, Regularization & Sparsity Analysis</CardTitle>
              <CardDescription>
                Comparing L1 (Lasso) feature selection vs L2 (Ridge) vs ElasticNet mixing penalty.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                {Object.entries(linearComp).map(([key, item]: [string, any]) => {
                  if (typeof item !== "object" || !item.metrics) return null;
                  return (
                    <div key={key} className="rounded-xl border border-border p-4 bg-muted/20">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-bold capitalize">{key.replace("_", " ")}</h4>
                        <Badge variant="outline" className="text-[10px]">
                          {item.metrics.active_features} / {item.metrics.total_features} features
                        </Badge>
                      </div>
                      <div className="mt-3 space-y-1.5 text-xs">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Test F1:</span>
                          <span className="font-mono font-bold">{item.metrics.f1.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">ROC-AUC:</span>
                          <span className="font-mono font-bold">{item.metrics.roc_auc.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Sparsity Rate:</span>
                          <span className="font-mono font-bold text-primary">{(item.metrics.sparsity_percentage ?? 0).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Penalty:</span>
                          <span className="font-mono">{item.metrics.penalty ?? "L2"}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Tree Models */}
        <TabsContent value="trees" className="mt-4 space-y-4">
          <Card className="data-card border-border bg-card">
            <CardHeader>
              <CardTitle className="text-base">M3: Tree-Based Models & Ensembles</CardTitle>
              <CardDescription>
                Evaluating pruned Decision Trees, Out-Of-Bag (OOB) Random Forest, XGBoost, and LightGBM.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                {Object.entries(treeComp.metrics ?? {}).map(([key, metrics]: [string, any]) => (
                  <div key={key} className="rounded-xl border border-border p-4 bg-muted/20">
                    <h4 className="text-sm font-bold capitalize">{key.replace("_", " ")}</h4>
                    <div className="mt-3 space-y-1.5 text-xs">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Accuracy:</span>
                        <span className="font-mono font-bold">{metrics.accuracy?.toFixed(3)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">F1 Score:</span>
                        <span className="font-mono font-bold">{metrics.f1?.toFixed(3)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">ROC-AUC:</span>
                        <span className="font-mono font-bold">{metrics.roc_auc?.toFixed(3)}</span>
                      </div>
                      {metrics.oob_score !== undefined && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">OOB Score:</span>
                          <span className="font-mono font-bold text-emerald-600">{metrics.oob_score.toFixed(3)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Champion Selection Rationale */}
      <Card className="data-card border-border bg-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Award className="h-5 w-5 text-emerald-600" />
            <CardTitle className="text-lg">Champion Model Decision Rationale</CardTitle>
          </div>
          <CardDescription>
            Why TF-IDF + Logistic Regression (L2) with Platt Scaling is selected as champion despite BERT's +0.018 raw F1 margin.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-border p-4 bg-card">
              <div className="flex items-center gap-2 text-primary font-bold text-xs">
                <Zap className="h-4 w-4" /> 1. Latency SLA
              </div>
              <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                0.25ms CPU inference easily satisfies the strict 50ms p95 SLA. BERT takes 145ms on CPU, violating production constraints.
              </p>
            </div>
            <div className="rounded-xl border border-border p-4 bg-card">
              <div className="flex items-center gap-2 text-primary font-bold text-xs">
                <HardDrive className="h-4 w-4" /> 2. Resource Footprint
              </div>
              <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                50 KB disk artifact and &lt;50 MB RAM footprint allow high-density Kubernetes pod auto-scaling on cheap commodity nodes.
              </p>
            </div>
            <div className="rounded-xl border border-border p-4 bg-card">
              <div className="flex items-center gap-2 text-primary font-bold text-xs">
                <ShieldCheck className="h-4 w-4" /> 3. Legal Auditability
              </div>
              <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                Direct linear weights eliminate black-box hallucination and provide legally defensible word-level attribution in moderation.
              </p>
            </div>
            <div className="rounded-xl border border-border p-4 bg-card">
              <div className="flex items-center gap-2 text-primary font-bold text-xs">
                <Cpu className="h-4 w-4" /> 4. Zero GPU Reliance
              </div>
              <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                No CUDA driver or dedicated GPU daemon required, preventing out-of-memory container crashes in headless production clusters.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
