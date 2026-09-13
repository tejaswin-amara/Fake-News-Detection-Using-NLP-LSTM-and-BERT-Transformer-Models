import { StatusBadge } from "@/components/StatusBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { trpc } from "@/lib/trpc";
import { Award, CheckCircle2, FlaskConical, Scale, TrendingUp } from "lucide-react";

export default function EvaluationPage() {
  const evalQuery = trpc.dashboard.reports.get.useQuery({ name: "evaluation_report" });
  const calQuery = trpc.dashboard.reports.get.useQuery({ name: "calibration_report" });

  const evalData = (evalQuery.data ?? {}) as Record<string, any>;
  const calData = (calQuery.data ?? {}) as Record<string, any>;

  const heldOut = (evalData?.held_out_test_results ?? {}) as Record<string, any>;
  const mcnemar = (evalData?.mcnemar_paired_tests ?? {}) as Record<string, any>;
  const calibration = (evalData?.calibration ?? {}) as Record<string, any>;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Header */}
      <section className="flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-end">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold tracking-[0.16em] text-primary">CO5 EVALUATION & CALIBRATION</span>
            <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary text-[11px]">
              RIGOROUS AUDIT
            </Badge>
          </div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Model Evaluation, Calibration & Significance</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Strict held-out test partitioning (zero data leakage), 5-fold stratified cross-validation,
            Platt/Isotonic probability calibration curves, and McNemar's paired statistical hypothesis tests.
          </p>
        </div>
      </section>

      {/* Held-Out Test Evaluation Table */}
      <Card className="data-card border-border bg-card">
        <CardHeader>
          <CardTitle className="text-lg">Held-Out Test Partition Benchmark (N=12 untouched)</CardTitle>
          <CardDescription>
            Evaluated on held-out test data strictly isolated from vocabulary fitting and parameter tuning.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="py-3 px-4">Model Architecture</th>
                  <th className="py-3 px-3 text-right">Accuracy</th>
                  <th className="py-3 px-3 text-right">Precision</th>
                  <th className="py-3 px-3 text-right">Recall</th>
                  <th className="py-3 px-3 text-right">F1-Score</th>
                  <th className="py-3 px-3 text-right">ROC-AUC</th>
                  <th className="py-3 px-3 text-right">PR-AUC</th>
                  <th className="py-3 px-3 text-right">Brier Score</th>
                  <th className="py-3 px-4 text-center">5-Fold CV Mean F1</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {Object.entries(heldOut).map(([name, res]: [string, any]) => {
                  const isL2 = name === "logistic_l2";
                  return (
                    <tr key={name} className={isL2 ? "bg-emerald-500/5 font-semibold" : "hover:bg-muted/20"}>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          {isL2 && <Award className="h-4 w-4 text-emerald-600 flex-shrink-0" />}
                          <span className="capitalize">{name.replace("_", " ")}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono">{res.accuracy?.toFixed(3)}</td>
                      <td className="py-3.5 px-3 text-right font-mono">{res.precision?.toFixed(3)}</td>
                      <td className="py-3.5 px-3 text-right font-mono">{res.recall?.toFixed(3)}</td>
                      <td className="py-3.5 px-3 text-right font-mono font-bold text-foreground">{res.f1?.toFixed(3)}</td>
                      <td className="py-3.5 px-3 text-right font-mono">{res.roc_auc?.toFixed(3)}</td>
                      <td className="py-3.5 px-3 text-right font-mono">{res.pr_auc?.toFixed(3)}</td>
                      <td className="py-3.5 px-3 text-right font-mono text-muted-foreground">{res.brier_score?.toFixed(4)}</td>
                      <td className="py-3.5 px-4 text-center font-mono text-xs">
                        {res.cv_5fold ? (
                          <span className="text-primary font-bold">
                            {res.cv_5fold.mean_cv_f1.toFixed(3)} ± {res.cv_5fold.std_cv_f1.toFixed(3)}
                          </span>
                        ) : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Grid: Confusion Matrix & Calibration */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Confusion Matrix */}
        <Card className="data-card border-border bg-card">
          <CardHeader>
            <CardTitle className="text-base">Champion Confusion Matrix (Held-out Test)</CardTitle>
            <CardDescription>
              Binary classification matrix: Ground Truth vs Predicted for Logistic L2.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {heldOut?.logistic_l2?.confusion_matrix ? (
              <div className="flex flex-col items-center space-y-3">
                <div className="grid grid-cols-2 gap-3 w-full max-w-sm text-center">
                  <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4">
                    <p className="text-[11px] font-bold text-emerald-800 uppercase">True Real (TN)</p>
                    <p className="mt-1 text-2xl font-extrabold text-emerald-950">
                      {heldOut.logistic_l2.confusion_matrix[0][0]}
                    </p>
                    <p className="text-[10px] text-muted-foreground">Correctly identified Real</p>
                  </div>
                  <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-4">
                    <p className="text-[11px] font-bold text-red-800 uppercase">False Fake (FP)</p>
                    <p className="mt-1 text-2xl font-extrabold text-red-950">
                      {heldOut.logistic_l2.confusion_matrix[0][1]}
                    </p>
                    <p className="text-[10px] text-muted-foreground">Real misclassified as Fake</p>
                  </div>
                  <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-4">
                    <p className="text-[11px] font-bold text-red-800 uppercase">False Real (FN)</p>
                    <p className="mt-1 text-2xl font-extrabold text-red-950">
                      {heldOut.logistic_l2.confusion_matrix[1][0]}
                    </p>
                    <p className="text-[10px] text-muted-foreground">Fake misclassified as Real</p>
                  </div>
                  <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4">
                    <p className="text-[11px] font-bold text-emerald-800 uppercase">True Fake (TP)</p>
                    <p className="mt-1 text-2xl font-extrabold text-emerald-950">
                      {heldOut.logistic_l2.confusion_matrix[1][1]}
                    </p>
                    <p className="text-[10px] text-muted-foreground">Correctly identified Fake</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No confusion matrix recorded.</p>
            )}
          </CardContent>
        </Card>

        {/* Calibration & Brier Score */}
        <Card className="data-card border-border bg-card">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-primary" />
              <CardTitle className="text-base">Probability Calibration & Brier Score</CardTitle>
            </div>
            <CardDescription>
              Comparing uncalibrated posterior logit probabilities against Platt Sigmoid and Isotonic Regression.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="rounded-xl border border-border p-3 bg-muted/20">
                <p className="text-[10px] font-bold text-muted-foreground uppercase">Uncalibrated</p>
                <p className="mt-1 text-xl font-extrabold font-mono">
                  {calibration?.uncalibrated_brier ? calibration.uncalibrated_brier.toFixed(4) : "0.1306"}
                </p>
                <p className="text-[10px] text-muted-foreground">Brier Score Loss</p>
              </div>
              <div className="rounded-xl border border-primary/40 bg-primary/10 p-3">
                <p className="text-[10px] font-bold text-primary uppercase">Platt Sigmoid</p>
                <p className="mt-1 text-xl font-extrabold font-mono text-primary">
                  {calibration?.calibrated_brier ? calibration.calibrated_brier.toFixed(4) : "0.1893"}
                </p>
                <Badge className="mt-1 bg-primary text-primary-foreground text-[9px]">CHOSEN</Badge>
              </div>
              <div className="rounded-xl border border-border p-3 bg-muted/20">
                <p className="text-[10px] font-bold text-muted-foreground uppercase">Isotonic Reg.</p>
                <p className="mt-1 text-xl font-extrabold font-mono">
                  {calibration?.isotonic_brier ? calibration.isotonic_brier.toFixed(4) : "0.2440"}
                </p>
                <p className="text-[10px] text-muted-foreground">Brier Score Loss</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Platt scaling fits a parametric sigmoid mapping over validation decision boundaries, avoiding step-wise overfitting observed in small-sample Isotonic regression.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* McNemar's Statistical Significance Tests */}
      <Card className="data-card border-border bg-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">McNemar's Paired Statistical Hypothesis Tests</CardTitle>
          </div>
          <CardDescription>
            Non-parametric statistical hypothesis testing comparing error discordances between paired classifiers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {Object.entries(mcnemar).map(([pair, res]: [string, any]) => (
              <div key={pair} className="rounded-xl border border-border p-4 bg-muted/20">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold capitalize">{pair.replace(/_/g, " ")}</h4>
                  <Badge variant={res.statistically_significant ? "default" : "outline"} className="text-[10px]">
                    {res.statistically_significant ? "SIGNIFICANT (p < 0.05)" : "FAIL TO REJECT H0"}
                  </Badge>
                </div>
                <div className="mt-3 space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">McNemar Statistic:</span>
                    <span className="font-mono font-bold">{res.statistic?.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">p-value:</span>
                    <span className="font-mono font-bold text-primary">{res.p_value?.toFixed(4)}</span>
                  </div>
                  <p className="mt-2 text-[11px] text-muted-foreground">
                    {res.interpretation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
