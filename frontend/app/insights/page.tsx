'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { Plot } from '@/data/mockPlots';
import { Sparkles, TrendingUp, AlertTriangle, MapPin } from 'lucide-react';

export default function InsightsPage() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPlots() {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots`,
        );

        const data: Plot[] = await response.json();
        setPlots(data);
      } catch (error) {
        console.error('Failed to fetch insights:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchPlots();
  }, []);

  const averageScore =
    plots.length > 0
      ? (
          plots.reduce((sum, plot) => sum + Number(plot.matchScore || 0), 0) /
          plots.length
        ).toFixed(1)
      : '0';

  const highRiskPlots = plots.filter(
    (plot) => plot.riskLevel?.toLowerCase() === 'high',
  );

  const bestPlots = [...plots]
    .sort((a, b) => Number(b.matchScore || 0) - Number(a.matchScore || 0))
    .slice(0, 3);

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        <div className="mb-10">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-[#C7745A] p-3 text-white">
              <Sparkles size={24} />
            </div>

            <div>
              <h1 className="text-4xl font-bold text-slate-950">AI Insights</h1>
              <p className="mt-1 text-slate-500">
                Smart signals across your land discovery pipeline.
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <p className="text-slate-500">Loading AI insights...</p>
        ) : (
          <>
            <div className="grid grid-cols-3 gap-5">
              <InsightCard
                title="Total Plots"
                value={plots.length.toString()}
                subtitle="Available opportunities"
              />

              <InsightCard
                title="Average Match"
                value={`${averageScore}/10`}
                subtitle="Across all visible plots"
              />

              <InsightCard
                title="High Risk"
                value={highRiskPlots.length.toString()}
                subtitle="Plots needing deeper review"
              />
            </div>

            <div className="mt-10 grid grid-cols-[1.2fr_0.8fr] gap-6">
              <div className="rounded-3xl bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center gap-2">
                  <TrendingUp className="text-[#C7745A]" size={22} />
                  <h2 className="text-xl font-bold text-slate-900">
                    Best Opportunities
                  </h2>
                </div>

                <div className="space-y-4">
                  {bestPlots.map((plot) => (
                    <div
                      key={plot.id}
                      className="rounded-2xl border border-[#E7D3CC] bg-[#FAF5F2] p-5"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">
                            {plot.title}
                          </h3>

                          <p className="mt-1 flex items-center gap-2 text-sm text-slate-500">
                            <MapPin size={15} />
                            {plot.location}
                          </p>

                          <p className="mt-3 text-sm text-slate-600">
                            {plot.reasons?.[0] ||
                              'Strong match based on available data.'}
                          </p>
                        </div>

                        <div className="rounded-2xl bg-[#EDF2EC] px-4 py-3 text-center">
                          <p className="text-2xl font-bold text-[#5F7666]">
                            {plot.matchScore}
                          </p>
                          <p className="text-xs text-slate-500">Match</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center gap-2">
                  <AlertTriangle className="text-[#C7745A]" size={22} />
                  <h2 className="text-xl font-bold text-slate-900">
                    AI Review Notes
                  </h2>
                </div>

                <div className="space-y-4 text-sm leading-relaxed text-slate-600">
                  <p>
                    Prioritize plots with strong infrastructure, clear zoning,
                    and low missing-data risk.
                  </p>

                  <p>
                    Plots with missing utility, sewer, or flood-risk information
                    should be reviewed before shortlisting.
                  </p>

                  <p>
                    Use full AI analysis to compare growth potential, risk
                    level, and development readiness.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

function InsightCard({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className="mt-3 text-4xl font-bold text-[#B8644C]">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
    </div>
  );
}
