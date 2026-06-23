'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { Plot } from '@/data/mockPlots';
import {
  Sparkles,
  TrendingUp,
  AlertTriangle,
  MapPin,
  Loader2,
  MessageSquare,
  FileText,
  CheckCircle2,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

type MarketReport = {
  market_overview: string;
  top_picks: string[];
  critical_risk_alerts: string[];
  development_readiness_notes: string;
};

export default function InsightsPage() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<MarketReport | null>(null);
  const [loadingReport, setLoadingReport] = useState(true);

  const [advisorQuestion, setAdvisorQuestion] = useState('');
  const [advisorAnswer, setAdvisorAnswer] = useState('');
  const [advisorLoading, setAdvisorLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setLoadingReport(true);

        const plotsRes = await fetch(
          `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots`,
        );
        let plotsData: Plot[] = [];
        if (plotsRes.ok) {
          plotsData = await plotsRes.json();
          setPlots(plotsData);
        }

        const insightsRes = await fetch(
          `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/insights`,
        );
        if (insightsRes.ok) {
          const insightsData = await insightsRes.json();
          setReport(insightsData);
        }
      } catch (error) {
        console.error('Failed to load insights:', error);
      } finally {
        setLoading(false);
        setLoadingReport(false);
      }
    }

    loadData();
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

  async function handleAskAdvisor(questionText?: string) {
    const q = questionText || advisorQuestion;
    if (!q.trim()) return;

    if (questionText) {
      setAdvisorQuestion(questionText);
    }

    try {
      setAdvisorLoading(true);
      setAdvisorAnswer('');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/advise`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: q }),
        },
      );

      if (!response.ok) {
        throw new Error('Advisor request failed');
      }

      const data = await response.json();
      setAdvisorAnswer(data.answer);
    } catch (error) {
      console.error('Advisor error:', error);
      setAdvisorAnswer(
        'Something went wrong. Please check your connection and try again.',
      );
    } finally {
      setAdvisorLoading(false);
    }
  }

  const suggestions = [
    'Identify the plot with the lowest price per acre.',
    'Which plots have road access and are zoned residential?',
    'Compare the risk levels of Austin vs Waco plots.',
  ];

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        <div className="mb-10">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-[#C7745A] p-3 text-white shadow-md shadow-[#C7745A]/20">
              <Sparkles size={24} />
            </div>

            <div>
              <h1 className="text-4xl font-bold text-slate-950">AI Insights</h1>
              <p className="mt-1 text-slate-500">
                Portfolio intelligence, risk alerts, and land advising agent.
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center gap-2 text-slate-500">
            <Loader2 className="animate-spin text-[#C7745A]" size={20} />
            <p>Loading AI insights...</p>
          </div>
        ) : (
          <>
            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <InsightCard
                title="Total Opportunities"
                value={plots.length.toString()}
                subtitle="Active land catalog listings"
                indicatorColor="border-l-4 border-l-[#C7745A]"
              />

              <InsightCard
                title="Average Match Score"
                value={`${averageScore}/10`}
                subtitle="Overall suitability rating"
                indicatorColor="border-l-4 border-l-[#5F7666]"
              />

              <InsightCard
                title="Risk Warnings"
                value={highRiskPlots.length.toString()}
                subtitle="Plots flagged as high risk"
                indicatorColor={`border-l-4 ${
                  highRiskPlots.length > 0
                    ? 'border-l-red-500'
                    : 'border-l-[#E7D3CC]'
                }`}
                highlightValue={highRiskPlots.length > 0}
              />
            </div>

            {/* Main Content Grid */}
            <div className="mt-8 grid grid-cols-1 xl:grid-cols-3 gap-6">
              {/* Left Column: AI Market Report & Best Opportunities */}
              <div className="xl:col-span-2 space-y-6">
                {/* AI Market Report */}
                <div className="rounded-3xl bg-white p-6 shadow-sm border border-[#E7D3CC]">
                  <div className="mb-5 flex items-center gap-2">
                    <FileText className="text-[#C7745A]" size={22} />
                    <h2 className="text-xl font-bold text-slate-900">
                      AI Market Intelligence Report
                    </h2>
                  </div>

                  {loadingReport ? (
                    <div className="flex items-center gap-2 py-6 text-slate-400">
                      <Loader2 className="animate-spin" size={18} />
                      <p className="text-sm">
                        Synthesizing catalog insights...
                      </p>
                    </div>
                  ) : report ? (
                    <div className="space-y-6 text-sm leading-relaxed text-slate-700">
                      <div>
                        <h3 className="font-semibold text-slate-900 text-base">
                          Market Overview
                        </h3>
                        <p className="mt-2 text-slate-600">
                          {report.market_overview}
                        </p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-[#F3ECE5]">
                        <div>
                          <h3 className="font-semibold text-slate-900 flex items-center gap-1.5">
                            <CheckCircle2
                              className="text-[#5F7666]"
                              size={16}
                            />{' '}
                            Top Value Picks
                          </h3>
                          <ul className="mt-2.5 space-y-2">
                            {report.top_picks.map((pick, idx) => (
                              <li
                                key={idx}
                                className="text-slate-600 pl-3 border-l-2 border-[#E7D3CC]"
                              >
                                {pick}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h3 className="font-semibold text-slate-900">
                            Development Readiness
                          </h3>
                          <p className="mt-2 text-slate-600 bg-[#FAF5F2] p-3 rounded-2xl border border-[#E7D3CC]">
                            {report.development_readiness_notes}
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-slate-400 text-sm py-4">
                      No report analysis available.
                    </p>
                  )}
                </div>

                {/* Best Opportunities */}
                <div className="rounded-3xl bg-white p-6 shadow-sm border border-[#E7D3CC]">
                  <div className="mb-5 flex items-center gap-2">
                    <TrendingUp className="text-[#C7745A]" size={22} />
                    <h2 className="text-xl font-bold text-slate-900">
                      Best Catalog Matches
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {bestPlots.map((plot) => (
                      <div
                        key={plot.id}
                        className="rounded-2xl border border-[#E7D3CC] bg-[#FAF5F2] p-5 flex flex-col justify-between hover:shadow-md transition duration-200"
                      >
                        <div>
                          <div className="flex justify-between items-start gap-2">
                            <h3 className="font-bold text-slate-900 line-clamp-1">
                              {plot.title}
                            </h3>
                            <span className="shrink-0 inline-block rounded-full bg-[#EDF2EC] px-2 py-0.5 text-xs font-semibold text-[#5F7666]">
                              {plot.matchScore}/10
                            </span>
                          </div>

                          <p className="mt-2 flex items-center gap-1 text-xs text-slate-500">
                            <MapPin size={12} />
                            {plot.location}
                          </p>

                          <p className="mt-3 text-xs text-slate-600 line-clamp-3">
                            {plot.reasons?.[0] ||
                              'Strong match based on available data.'}
                          </p>
                        </div>

                        <div className="mt-4 pt-3 border-t border-[#F3ECE5] flex justify-between items-center text-xs font-medium">
                          <span className="text-[#B8644C]">{plot.price}</span>
                          <span className="text-slate-500">{plot.acres}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Alerts & AI Advisor Chat */}
              <div className="space-y-6">
                {/* AI Portfolio Risk Alerts */}
                <div className="rounded-3xl bg-white p-6 shadow-sm border border-[#E7D3CC]">
                  <div className="mb-5 flex items-center gap-2">
                    <AlertTriangle className="text-red-500" size={22} />
                    <h2 className="text-xl font-bold text-slate-900">
                      AI Portfolio Risk Alerts
                    </h2>
                  </div>

                  {loadingReport ? (
                    <div className="flex items-center gap-2 py-4 text-slate-400">
                      <Loader2 className="animate-spin" size={16} />
                      <p className="text-sm">Scanning for risks...</p>
                    </div>
                  ) : report && report.critical_risk_alerts.length > 0 ? (
                    <ul className="space-y-3">
                      {report.critical_risk_alerts.map((alert, idx) => (
                        <li
                          key={idx}
                          className="rounded-xl border border-red-100 bg-red-50/50 p-3 text-sm text-red-900/80 flex items-start gap-2"
                        >
                          <span className="text-red-500 mt-0.5">•</span>
                          <span>{alert}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-slate-500 text-sm leading-relaxed">
                      No critical portfolio-wide alerts or restrictions detected
                      in the active listings.
                    </p>
                  )}
                </div>

                {/* AI Land Advisor Chat Box */}
                <div className="rounded-3xl bg-white p-6 shadow-sm border border-[#E7D3CC] flex flex-col justify-between">
                  <div>
                    <div className="mb-4 flex items-center gap-2">
                      <MessageSquare className="text-[#C7745A]" size={22} />
                      <h2 className="text-xl font-bold text-slate-900">
                        AI Portfolio Advisor
                      </h2>
                    </div>

                    <p className="text-xs text-slate-500 leading-relaxed mb-4">
                      Ask about specific parameters, compare locations, or get
                      recommendations across all catalog land listings.
                    </p>

                    {/* Suggestions */}
                    <div className="space-y-2 mb-4">
                      {suggestions.map((s, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleAskAdvisor(s)}
                          className="w-full text-left text-xs bg-[#FAF5F2] hover:bg-[#F3E6E1] text-[#B8644C] border border-[#E7D3CC] rounded-xl px-3 py-2 transition"
                        >
                          💡 {s}
                        </button>
                      ))}
                    </div>

                    {/* Advisor Answer Screen */}
                    {advisorAnswer && (
                      <div className="prose prose-sm max-h-[220px] overflow-y-auto rounded-2xl bg-[#FAF5F2] border border-[#E7D3CC] p-4 text-slate-700 mb-4 text-xs prose-headings:text-slate-900 prose-strong:text-slate-900">
                        <ReactMarkdown>{advisorAnswer}</ReactMarkdown>
                      </div>
                    )}
                  </div>

                  {/* Input Console */}
                  <div className="flex gap-2">
                    <input
                      value={advisorQuestion}
                      onChange={(e) => setAdvisorQuestion(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleAskAdvisor();
                        }
                      }}
                      placeholder="Ask the catalog advisor..."
                      className="min-w-0 flex-1 rounded-xl border border-[#E7D3CC] px-3.5 py-2.5 text-xs outline-none focus:border-[#C7745A] bg-[#FAF5F2]"
                    />

                    <button
                      onClick={() => handleAskAdvisor()}
                      disabled={advisorLoading}
                      className="rounded-xl bg-[#C7745A] px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-[#B8644C] disabled:opacity-60 shrink-0"
                    >
                      {advisorLoading ? '...' : 'Ask'}
                    </button>
                  </div>
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
  indicatorColor,
  highlightValue = false,
}: {
  title: string;
  value: string;
  subtitle: string;
  indicatorColor: string;
  highlightValue?: boolean;
}) {
  return (
    <div
      className={`rounded-3xl bg-white p-6 shadow-sm border border-[#E7D3CC] ${indicatorColor}`}
    >
      <p className="text-xs font-semibold text-slate-500">{title}</p>
      <p
        className={`mt-3 text-3xl font-bold ${highlightValue ? 'text-red-500 animate-pulse' : 'text-[#B8644C]'}`}
      >
        {value}
      </p>
      <p className="mt-1.5 text-xs text-slate-500">{subtitle}</p>
    </div>
  );
}
