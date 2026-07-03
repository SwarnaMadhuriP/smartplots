'use client';

import { useState, useEffect, useCallback } from 'react';
import GoalSelector, { GoalKey } from './GoalSelector';
import GoalForm, { GoalPreferences } from './GoalForm';
import RecommendationCard, { AdvisorRecommendation } from './RecommendationCard';
import FeedbackBar, { FeedbackOption } from './FeedbackBar';
import { Sparkles, AlertCircle } from 'lucide-react';

const LS_KEY = 'smartplots_advisor_state';
const COMPARE_LS_KEY = 'comparisonPlotIds';
const MAX_COMPARE_PLOTS = 3;

type Step = 'goal_select' | 'inputs' | 'loading' | 'recommendation';

type PersistedState = {
  goal?: GoalKey;
  prefs?: GoalPreferences;
  recommendation?: AdvisorRecommendation | null;
  activeFeedback?: FeedbackOption;
  showAlternatives?: boolean;
};

function loadPersistedState(): PersistedState {
  try {
    const raw = typeof window !== 'undefined' ? localStorage.getItem(LS_KEY) : null;
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function persistState(state: PersistedState) {
  try {
    if (typeof window !== 'undefined') {
      localStorage.setItem(LS_KEY, JSON.stringify(state));
    }
  } catch {
    // ignore
  }
}

function loadComparisonPlotIds() {
  try {
    const raw = typeof window !== 'undefined' ? localStorage.getItem(COMPARE_LS_KEY) : null;
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

const STEPS: Step[] = ['goal_select', 'inputs', 'recommendation'];

type Props = {
  initialGoal?: GoalKey;
};

const API_BASE = process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL ?? '';

function formatAdvisorError(raw: unknown, fallback: string) {
  const message = typeof raw === 'string' ? raw : fallback;
  const lower = message.toLowerCase();

  if (lower.includes('quota') || message.includes('RESOURCE_EXHAUSTED')) {
    return 'Daily AI quota reached. Please try again tomorrow.';
  }

  if (
    lower.includes('503') ||
    lower.includes('unavailable') ||
    lower.includes('overloaded') ||
    lower.includes('high demand') ||
    lower.includes('model is currently experiencing')
  ) {
    return 'The AI advisor is temporarily busy due to high demand. Please try again in a few minutes.';
  }

  return message;
}

export default function AdvisorShell({ initialGoal }: Props) {
  const [step, setStep] = useState<Step>(
    initialGoal ? 'inputs' : 'goal_select',
  );
  const [goal, setGoal] = useState<GoalKey | undefined>(initialGoal);
  const [prefs, setPrefs] = useState<GoalPreferences | undefined>();
  const [recommendation, setRecommendation] = useState<AdvisorRecommendation | null>(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [activeFeedback, setActiveFeedback] = useState<FeedbackOption | undefined>();
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [comparisonPlotIds, setComparisonPlotIds] = useState<number[]>([]);
  const [compareMessage, setCompareMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    queueMicrotask(() => {
      if (!isMounted) return;

      const saved = loadPersistedState();
      const shouldRestoreRecommendation =
        Boolean(saved.recommendation) && (!initialGoal || initialGoal === saved.goal);

      setComparisonPlotIds(loadComparisonPlotIds());

      if (shouldRestoreRecommendation) {
        setGoal(saved.goal);
        setPrefs(saved.prefs);
        setRecommendation(saved.recommendation ?? null);
        setActiveFeedback(saved.activeFeedback);
        setShowAlternatives(Boolean(saved.showAlternatives));
        setStep('recommendation');
        return;
      }

      if (!initialGoal && saved.goal) {
        setGoal(saved.goal);
        setPrefs(saved.prefs);
        setStep('inputs');
      }
    });

    return () => {
      isMounted = false;
    };
  }, [initialGoal]);

  useEffect(() => {
    persistState({
      goal,
      prefs,
      recommendation,
      activeFeedback,
      showAlternatives,
    });
  }, [goal, prefs, recommendation, activeFeedback, showAlternatives]);

  function handleToggleCompare(plotId: number) {
    setComparisonPlotIds((prev) => {
      const isAlreadyCompared = prev.includes(plotId);
      const updated = isAlreadyCompared
        ? prev.filter((id) => id !== plotId)
        : prev.length >= MAX_COMPARE_PLOTS
          ? prev
          : [...prev, plotId];

      if (!isAlreadyCompared && prev.length >= MAX_COMPARE_PLOTS) {
        setCompareMessage('Compare list is full. Remove a plot before adding another.');
        return prev;
      }

      localStorage.setItem(COMPARE_LS_KEY, JSON.stringify(updated));
      setCompareMessage(
        isAlreadyCompared
          ? 'Removed from compare.'
          : `Added to compare (${updated.length}/${MAX_COMPARE_PLOTS}).`,
      );
      return updated;
    });
  }

  function handleGoalSelect(selectedGoal: GoalKey) {
    setGoal(selectedGoal);
    setPrefs(undefined);
    setRecommendation(null);
    setStep('inputs');
    setError('');
    setActiveFeedback(undefined);
    setShowAlternatives(false);
  }

  function handleBack() {
    setGoal(undefined);
    setPrefs(undefined);
    setRecommendation(null);
    setStep('goal_select');
    setError('');
    setActiveFeedback(undefined);
    setShowAlternatives(false);
  }

  function handleRestart() {
    setGoal(undefined);
    setPrefs(undefined);
    setRecommendation(null);
    setStep('goal_select');
    setError('');
    setActiveFeedback(undefined);
    setShowAlternatives(false);
    try { localStorage.removeItem(LS_KEY); } catch { /* */ }
  }

  const fetchRecommendation = useCallback(async (
    selectedGoal: GoalKey,
    selectedPrefs: GoalPreferences,
  ) => {
    setStep('loading');
    setError('');
    setRecommendation(null);
    setActiveFeedback(undefined);
    setShowAlternatives(false);

    try {
      const res = await fetch(`${API_BASE}/advisor/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: selectedGoal, preferences: selectedPrefs }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(formatAdvisorError(data.detail, 'Recommendation failed.'));
      }
      const data: AdvisorRecommendation = await res.json();
      setRecommendation(data);
      setStep('recommendation');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Something went wrong.');
      setStep('inputs');
    }
  }, []);

  async function handleFormSubmit(selectedPrefs: GoalPreferences) {
    if (!goal) return;
    setPrefs(selectedPrefs);
    await fetchRecommendation(goal, selectedPrefs);
  }

  async function handleFeedback(feedback: FeedbackOption) {
    if (!recommendation) return;

    if (feedback === 'good_recommendation') {
      setActiveFeedback(feedback);
      return;
    }
    if (feedback === 'show_alternatives') {
      setShowAlternatives(true);
      setActiveFeedback(feedback);
      setTimeout(() => {
        document.getElementById('advisor-alternatives')?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }, 0);
      return;
    }

    setActiveFeedback(feedback);
    setFeedbackLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_BASE}/advisor/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: recommendation.session_token, feedback }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(formatAdvisorError(data.detail, 'Refinement failed.'));
      }
      const refined: AdvisorRecommendation = await res.json();
      setRecommendation(refined);
      setActiveFeedback(undefined);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Something went wrong.');
      setActiveFeedback(undefined);
    } finally {
      setFeedbackLoading(false);
    }
  }

  // Current step index for the breadcrumb
  const stepIndex = STEPS.indexOf(step === 'loading' ? 'inputs' : step);
  const stepTextClass = (index: number) => {
    if (stepIndex > index) return 'text-[#374151] font-medium';
    if (stepIndex === index) return 'text-[#C7745A] font-bold';
    return 'text-slate-300 font-normal';
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">

      {/* Step breadcrumb */}
      <div className="shrink-0 px-10 py-4 bg-[#F8F3ED] border-b border-[#E7D3CC]">
        <div className="flex items-center gap-3 flex-wrap">
          <span className={`text-sm transition-colors ${stepTextClass(0)}`}>
            {stepIndex > 0 && <span aria-hidden="true" className="mr-1">✓</span>}
            Choose Goal
          </span>

          <span className="text-[#D4BAB0] text-sm">›</span>
          <span className={`text-sm transition-colors ${stepTextClass(1)}`}>
            Your Preferences
          </span>

          <span className="text-[#D4BAB0] text-sm">›</span>
          <span className={`text-sm transition-colors ${stepTextClass(2)}`}>
            Recommendation
          </span>
        </div>
      </div>

      {/* Scrollable content */}
      <div className={step === 'recommendation' ? 'flex-1 overflow-hidden' : 'flex-1 overflow-y-auto'}>
        <div className={step === 'recommendation' ? 'h-full px-2 py-2 md:px-3' : 'px-4 py-5 md:px-6'}>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-3 mb-6 max-w-2xl mx-auto rounded-3xl border border-[#EACAC5] bg-[#FAF0EE] px-5 py-4">
              <AlertCircle size={16} className="mt-0.5 shrink-0 text-[#C7745A]" />
              <p className="text-sm text-[#A05040]">{error}</p>
            </div>
          )}

          {/* Loading state */}
          {step === 'loading' && (
            <div className="flex flex-col items-center justify-center py-24 gap-5 animate-fadeIn">
              <div className="relative">
                <div className="h-16 w-16 rounded-full border-4 border-[#E7D3CC] border-t-[#C7745A] animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Sparkles size={18} className="text-[#C7745A]" />
                </div>
              </div>
              <div className="text-center">
                <p className="font-semibold text-slate-700">Analyzing your catalog…</p>
                <p className="mt-1 text-sm text-slate-400">Scoring plots and generating your recommendation.</p>
              </div>
            </div>
          )}

          {/* Goal selection */}
          {step === 'goal_select' && (
            <GoalSelector onSelect={handleGoalSelect} />
          )}

          {/* Input form */}
          {step === 'inputs' && goal && (
            <GoalForm
              goal={goal}
              initialPrefs={prefs}
              onBack={handleBack}
              onSubmit={handleFormSubmit}
              loading={false}
            />
          )}

          {/* Recommendation + feedback */}
          {step === 'recommendation' && recommendation && (
            <RecommendationCard
              recommendation={recommendation}
              goal={goal}
              showAlternatives={showAlternatives}
              comparisonPlotIds={comparisonPlotIds}
              compareMessage={compareMessage}
              onToggleCompare={handleToggleCompare}
              feedbackSlot={(
                <FeedbackBar
                  onFeedback={handleFeedback}
                  onRestart={handleRestart}
                  loading={feedbackLoading}
                  activeFeedback={activeFeedback}
                />
              )}
            />
          )}

        </div>
      </div>
    </div>
  );
}
