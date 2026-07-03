'use client';

import { Suspense, useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import ComparisonTable from '@/components/ComparisonTable';
import { ComparisonPlot, ComparisonAnalysis } from '@/types/comparisons';
import { Sparkles, Loader2 } from 'lucide-react';
import { useSearchParams } from 'next/navigation';

const MAX_COMPARE_PLOTS = 3;
type ComparisonSource = 'manual' | 'ai_advisor';

function parseComparisonIds(value: string | null) {
  if (!value) return [];

  return value
    .split(',')
    .map((id) => Number(id))
    .filter((id) => Number.isFinite(id) && id > 0)
    .slice(0, MAX_COMPARE_PLOTS);
}

type PlotApiResponse = Partial<ComparisonPlot> & {
  rawPrice?: number;
  rawAcres?: number;
  location?: string;
  zone?: string;
  price?: number | string;
};

function numericValue(value: unknown): number {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = Number(value.replace(/[$,]/g, '').replace('Acres', '').trim());
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function normalizeComparisonPlot(plot: PlotApiResponse): ComparisonPlot {
  const [locationCity, locationState] = (plot.location ?? '')
    .split(',')
    .map((part) => part.trim());

  return {
    id: Number(plot.id),
    title: plot.title ?? `Plot #${plot.id}`,
    price: numericValue(plot.rawPrice ?? plot.price),
    area_acres: numericValue(plot.area_acres ?? plot.rawAcres),
    city: plot.city ?? locationCity ?? 'Unknown',
    state: plot.state ?? locationState ?? 'Unknown',
    zoning_type: plot.zoning_type ?? plot.zone ?? 'General',
    road_access: Boolean(plot.road_access),
    water_access: Boolean(plot.water_access),
    electricity: Boolean(plot.electricity),
    sewer: Boolean(plot.sewer),
    risk_notes: plot.risk_notes,
  };
}

function ComparisonsPageContent() {
  const [plots, setPlots] = useState<ComparisonPlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState<ComparisonAnalysis | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [goal, setGoal] = useState('');
  const [comparisonSource, setComparisonSource] = useState<ComparisonSource>('manual');
  const searchParams = useSearchParams();

  async function fetchAnalysis(plotIds: number[], currentGoal?: string) {
    if (plotIds.length === 0) return;
    try {
      setLoadingAnalysis(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/compare`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            plot_ids: plotIds,
            goal: currentGoal || undefined,
          }),
        },
      );

      if (!response.ok) {
        throw new Error('Failed to fetch AI comparison analysis');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Error fetching AI comparison analysis:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  }

  useEffect(() => {
    async function loadComparisonPlots() {
      try {
        const sourceParam = searchParams.get('source');
        const nextSource: ComparisonSource =
          sourceParam === 'ai_advisor' ? 'ai_advisor' : 'manual';
        const queryIds = parseComparisonIds(searchParams.get('ids'));
        const queryGoal = searchParams.get('goal') ?? '';
        const storedIds = localStorage.getItem('comparisonPlotIds');
        const ids: number[] = queryIds.length > 0
          ? queryIds
          : storedIds
            ? JSON.parse(storedIds).slice(0, MAX_COMPARE_PLOTS)
            : [];

        setComparisonSource(nextSource);
        setGoal(queryGoal);
        setAnalysis(null);

        if (queryIds.length > 0) {
          localStorage.setItem('comparisonPlotIds', JSON.stringify(queryIds));
        }

        if (ids.length === 0) {
          setPlots([]);
          return;
        }

        const responses = await Promise.all(
          ids.map((id) =>
            fetch(`${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/${id}`),
          ),
        );

        const data = await Promise.all(
          responses.map((response) => {
            if (!response.ok) {
              throw new Error('Failed to fetch comparison plot');
            }

            return response.json();
          }),
        );

        setPlots(data.map(normalizeComparisonPlot));
        if (nextSource === 'ai_advisor') {
          fetchAnalysis(ids, queryGoal);
        }
      } catch (error) {
        console.error('Error loading comparison plots:', error);

        setPlots([]);
      } finally {
        setLoading(false);
      }
    }

    loadComparisonPlots();
  }, [searchParams]);

  const handleClearComparison = () => {
    localStorage.removeItem('comparisonPlotIds');
    setPlots([]);
    setAnalysis(null);
    setGoal('');
    setComparisonSource('manual');
  };

  const handleCustomAnalyze = () => {
    const plotIds = plots.map((p) => p.id);
    fetchAnalysis(plotIds, goal);
  };

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        {loading ? (
          <div className="rounded-3xl bg-white p-8 text-slate-500 shadow-sm">
            Loading comparison...
          </div>
        ) : (
          <>
            <div className="mb-4 flex justify-end">
              <button
                onClick={handleClearComparison}
                className="rounded-full border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-[#C7745A] shadow-sm transition hover:bg-[#F3E6E1]"
              >
                Clear Comparison
              </button>
            </div>

            {plots.length > 0 && (
              <div className="mb-6 rounded-[2rem] border border-[#E7D3CC] bg-white p-6 shadow-sm">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#F3ECE5] pb-4">
                  <div>
                    <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                      <Sparkles className="text-[#C7745A]" size={20} />
                      AI Plot Comparison
                    </h2>
                    <p className="text-sm text-slate-500 mt-1">
                      {comparisonSource === 'ai_advisor'
                        ? 'Comparing the AI Advisor recommendation against its closest alternatives.'
                        : 'Specify an optional goal to analyze the selected plots.'}
                    </p>
                  </div>

                  <div className="flex gap-2 flex-1 max-w-xl">
                    <input
                      type="text"
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleCustomAnalyze();
                      }}
                      placeholder="e.g., Building a house, Farming..."
                      className="min-w-0 flex-1 rounded-full border border-[#E7D3CC] px-4 py-2.5 text-sm outline-none focus:border-[#C7745A] bg-[#FAF5F2]"
                    />
                    <button
                      onClick={handleCustomAnalyze}
                      disabled={loadingAnalysis}
                      className="rounded-full bg-[#C7745A] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#B8644C] disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2 shrink-0 shadow-sm"
                    >
                      {loadingAnalysis && (
                        <Loader2 size={16} className="animate-spin" />
                      )}
                      {loadingAnalysis ? 'Analyzing...' : 'Analyze'}
                    </button>
                  </div>
                </div>

                {loadingAnalysis ? (
                  <div className="flex flex-col items-center justify-center py-10 gap-2">
                    <Loader2
                      className="animate-spin text-[#C7745A]"
                      size={32}
                    />
                    <p className="text-sm text-slate-500">
                      Evaluating plot suitability...
                    </p>
                  </div>
                ) : analysis ? (
                  <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2 space-y-4">
                      <div>
                        <h3 className="text-sm font-semibold text-[#B8644C]">
                          Overall Recommendation
                        </h3>
                        <p className="mt-2 text-sm leading-relaxed text-slate-700">
                          {analysis.overall_recommendation}
                        </p>
                      </div>
                    </div>
                    <div className="border-t lg:border-t-0 lg:border-l border-[#F3ECE5] pt-4 lg:pt-0 lg:pl-6">
                      <h3 className="text-sm font-semibold text-slate-900">
                        Key Summary Points
                      </h3>
                      <ul className="mt-3 space-y-2">
                        {analysis.summary_points.map((point, index) => (
                          <li
                            key={index}
                            className="text-sm text-slate-600 flex items-start gap-2"
                          >
                            <span className="text-[#C7745A] mt-1 shrink-0">
                              •
                            </span>
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="mt-6 text-center py-6 text-slate-400 text-sm">
                    Enter a goal above and click Analyze to generate AI
                    insights.
                  </div>
                )}
              </div>
            )}

            <ComparisonTable plots={plots} profiles={analysis?.profiles} />
          </>
        )}
      </section>
    </main>
  );
}

export default function ComparisonsPage() {
  return (
    <Suspense
      fallback={
        <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
          <Sidebar />
          <section className="flex-1 overflow-y-auto px-10 py-10">
            <div className="rounded-3xl bg-white p-8 text-slate-500 shadow-sm">
              Loading comparison...
            </div>
          </section>
        </main>
      }
    >
      <ComparisonsPageContent />
    </Suspense>
  );
}
