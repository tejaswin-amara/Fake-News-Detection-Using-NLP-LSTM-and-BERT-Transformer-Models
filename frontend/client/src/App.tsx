import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import DashboardLayout from "./components/DashboardLayout";
import AnalyzePage from "./pages/AnalyzePage";
import ApiKeysPage from "./pages/ApiKeysPage";
import DriftPage from "./pages/DriftPage";
import EvaluationPage from "./pages/EvaluationPage";
import ExplainabilityPage from "./pages/ExplainabilityPage";
import HealthPage from "./pages/HealthPage";
import HistoryPage from "./pages/HistoryPage";
import ModelComparisonPage from "./pages/ModelComparisonPage";
import OverviewPage from "./pages/OverviewPage";
import UnsupervisedPage from "./pages/UnsupervisedPage";

function Router() {
  // make sure to consider if you need authentication for certain routes
  return (
    <DashboardLayout>
      <Switch>
        <Route path={"/"} component={AnalyzePage} />
        <Route path={"/overview"} component={OverviewPage} />
        <Route path={"/models"} component={ModelComparisonPage} />
        <Route path={"/explainability"} component={ExplainabilityPage} />
        <Route path={"/evaluation"} component={EvaluationPage} />
        <Route path={"/unsupervised"} component={UnsupervisedPage} />
        <Route path={"/history"} component={HistoryPage} />
        <Route path={"/drift"} component={DriftPage} />
        <Route path={"/health"} component={HealthPage} />
        <Route path={"/api-keys"} component={ApiKeysPage} />
        <Route path={"/404"} component={NotFound} />
        <Route component={NotFound} />
      </Switch>
    </DashboardLayout>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
