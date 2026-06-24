'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';
import {
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  DollarSign,
  FileText,
  GitCompare,
  Info,
  Layers,
  ListOrdered,
  MapPin,
  Trophy,
} from 'lucide-react';

type PlotItem = {
  plot_id: number;
  title: string;
  location: string;
  price: string;
  acres: string;
  score: number;
  match_reason: string;
};

type AltItem = {
  plot_id: number;
  title: string;
  location: string;
  price: string;
  acres: string;
  key_differentiator: string;
};

export type AdvisorRecommendation = {
  recommended_plots: PlotItem[];
  primary_recommendation: PlotItem;
  confidence: number;
  reasoning: string[];
  risks: string[];
  tradeoffs: string[];
  alternatives: AltItem[];
  next_steps: string[];
  session_token: string;
};

type EvidenceItem = {
  label: string;
  detail: string;
};

type Props = {
  recommendation: AdvisorRecommendation;
  showAlternatives?: boolean;
  feedbackSlot?: ReactNode;
};

export default function RecommendationCard({ recommendation, feedbackSlot }: Props) {
  const { primary_recommendation: primary, alternatives } = recommendation;
  const confidencePct = Math.round(recommendation.confidence * 100);
  const comparisonIds = [primary.plot_id, ...alternatives.slice(0, 2).map((a) => a.plot_id)].join(',');
  const evidenceItems: EvidenceItem[] = [];

  function getAlternativeScore(plotId: number) {
    return recommendation.recommended_plots.find((plot) => plot.plot_id === plotId)?.score;
  }

  return (
    <div className="flex h-full w-full min-w-0 flex-col gap-2 overflow-hidden py-0 animate-fadeIn">
      <section className="z-20 shrink-0 overflow-hidden border border-[#E7D3CC] bg-white shadow-md shadow-[#EFE3DD]/70">
        <div className="h-1.5 bg-[#C7745A]" />
        <div className="p-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0 flex-1">
              <p className="mb-1.5 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[#B8644C]">
                <Trophy size={14} />
                Recommended Plot
              </p>
              <h2 className="text-2xl font-bold leading-tight text-slate-950">{primary.title}</h2>

              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-slate-500">
                <span className="flex items-center gap-1.5">
                  <MapPin size={14} className="text-[#B0897A]" />
                  {primary.location}
                </span>
                <span className="flex items-center gap-1.5">
                  <DollarSign size={14} className="text-[#B0897A]" />
                  {primary.price}
                </span>
                <span className="flex items-center gap-1.5">
                  <Layers size={14} className="text-[#B0897A]" />
                  {primary.acres}
                </span>
              </div>

              <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-600">{primary.match_reason}</p>
            </div>

            <div className="grid grid-cols-2 gap-2 lg:w-[270px]">
              <div className="border border-[#E7D3CC] bg-[#FAF5F2] px-3 py-2.5">
                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Match Score
                  <span className="group relative">
                    <Info size={11} />
                    <span className="pointer-events-none absolute right-0 top-5 z-10 hidden w-56 rounded-2xl bg-slate-900 px-3 py-2 text-xs font-normal leading-relaxed text-white shadow-lg group-hover:block">
                      Match Score = how well the plot matches preferences.
                    </span>
                  </span>
                </div>
                <p className="mt-1 text-xl font-bold leading-none text-slate-950">{primary.score.toFixed(1)}/10</p>
              </div>

              <div className="border border-[#E7D3CC] bg-[#FAF5F2] px-3 py-2.5">
                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Advisor Confidence
                  <span className="group relative">
                    <Info size={11} />
                    <span className="pointer-events-none absolute right-0 top-5 z-10 hidden w-64 rounded-2xl bg-slate-900 px-3 py-2 text-xs font-normal leading-relaxed text-white shadow-lg group-hover:block">
                      Advisor Confidence = confidence in the recommendation given available data.
                    </span>
                  </span>
                </div>
                <p className="mt-1 text-xl font-bold leading-none text-slate-950">{confidencePct}%</p>
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2.5">
            <Link
              href={`/plots/${primary.plot_id}`}
              className="flex items-center gap-2 rounded-2xl bg-[#C7745A] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#B8644C] active:scale-[0.98]"
            >
              View Plot
              <ArrowUpRight size={14} />
            </Link>

            {alternatives.length > 0 && (
              <Link
                href={`/comparisons?ids=${comparisonIds}`}
                className="flex items-center gap-2 rounded-2xl border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-[#C7745A]"
              >
                <GitCompare size={14} />
                Compare
              </Link>
            )}

            {alternatives.length > 0 && (
              <a
                href="#advisor-alternatives"
                className="rounded-2xl border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-[#C7745A]"
              >
                Show Alternatives
              </a>
            )}
          </div>
        </div>
      </section>

      <section className="min-h-0 flex-1 overflow-y-auto border border-[#E7D3CC] bg-white p-4 shadow-sm">
        {feedbackSlot}

        <div className="mt-4 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <div className="mb-3 flex items-center gap-2">
              <CheckCircle2 size={17} className="text-[#6BA875]" />
              <h3 className="text-base font-bold text-slate-900">Why We Recommend It</h3>
            </div>
            <ul className="grid gap-2 sm:grid-cols-2">
              {recommendation.reasoning.map((reason, index) => (
                <li key={index} className="flex items-start gap-2.5 text-sm leading-snug text-slate-600">
                  <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-[#6BA875]" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="border border-[#F0E8E3] bg-[#FAF5F2] p-3.5">
            <div className="mb-3 flex items-center gap-2">
              <ListOrdered size={16} className="text-[#C7745A]" />
              <h3 className="text-sm font-bold text-slate-900">Suggested Next Steps</h3>
            </div>
            <ol className="space-y-2.5">
              {recommendation.next_steps.slice(0, 4).map((step, index) => (
                <li key={index} className="flex items-start gap-2.5 text-sm leading-snug text-slate-600">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white text-[11px] font-bold text-[#B8644C]">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>

        <div className="mt-4 border-t border-[#F0E8E3] pt-3.5">
          <div className="mb-3 flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-500" />
            <h3 className="text-sm font-bold text-slate-900">Potential Risks</h3>
          </div>
          {recommendation.risks.length === 0 ? (
            <p className="text-sm italic text-slate-400">No major risks identified.</p>
          ) : (
            <ul className="grid gap-2 sm:grid-cols-2">
              {recommendation.risks.map((risk, index) => (
                <li key={index} className="flex items-start gap-2.5 text-sm leading-snug text-slate-600">
                  <AlertTriangle size={14} className="mt-0.5 shrink-0 text-amber-500" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {recommendation.tradeoffs.length > 0 && (
          <div className="mt-4 border-t border-[#F0E8E3] pt-3.5">
            <p className="mb-3 text-sm font-bold text-slate-900">Advisor Tradeoffs</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {recommendation.tradeoffs.map((tradeoff, index) => (
                <p
                  key={index}
                  className="border-l-2 border-[#E7D3CC] pl-3 text-sm leading-snug text-slate-600"
                >
                  {tradeoff}
                </p>
              ))}
            </div>
          </div>
        )}

        {alternatives.length > 0 && (
          <div id="advisor-alternatives" className="mt-4 border-t border-[#F0E8E3] pt-3.5">
            <div className="mb-3 flex items-end justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Alternatives Considered</p>
                <h3 className="mt-1 text-base font-bold text-slate-900">Alternative Opportunities</h3>
              </div>
              <p className="hidden text-xs text-slate-400 sm:block">Shortlist reviewed by the advisor</p>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {alternatives.slice(0, 3).map((alternative, index) => {
                const altScore = getAlternativeScore(alternative.plot_id);

                return (
                  <div
                    key={alternative.plot_id}
                    className="flex min-h-[126px] flex-col justify-between border border-[#F0E8E3] bg-[#FAF5F2] px-3.5 py-3"
                  >
                    <div className="min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-wider text-[#B8644C]">#{index + 2}</p>
                          <p className="mt-1 text-sm font-semibold leading-tight text-slate-800">{alternative.title}</p>
                        </div>
                        {altScore !== undefined && (
                          <div className="bg-white px-2.5 py-1 text-center">
                            <p className="text-sm font-bold leading-none text-slate-800">{altScore.toFixed(1)}</p>
                            <p className="mt-0.5 text-[9px] font-medium uppercase tracking-wide text-slate-400">Score</p>
                          </div>
                        )}
                      </div>
                      <p className="mt-1 text-xs text-slate-500">{alternative.key_differentiator}</p>
                      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
                        <span className="flex items-center gap-1">
                          <MapPin size={11} />
                          {alternative.location}
                        </span>
                        <span className="flex items-center gap-1">
                          <DollarSign size={11} />
                          {alternative.price}
                        </span>
                        <span className="flex items-center gap-1">
                          <Layers size={11} />
                          {alternative.acres}
                        </span>
                      </div>
                    </div>
                    <Link
                      href={`/plots/${alternative.plot_id}`}
                      className="mt-3 self-start rounded-xl border border-[#E7D3CC] bg-white px-3.5 py-1.5 text-xs font-medium text-slate-500 transition hover:border-[#C7745A] hover:bg-[#F3E6E1] hover:text-[#C7745A]"
                    >
                      View
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {evidenceItems.length > 0 && (
          <div className="mt-4 border-t border-[#F0E8E3] pt-3.5">
            <div className="mb-4 flex items-center gap-2">
              <FileText size={17} className="text-[#C7745A]" />
              <h3 className="text-base font-bold text-slate-900">Evidence</h3>
            </div>
            <div className="grid gap-3">
              {evidenceItems.map((item) => (
                <div key={item.label} className="border border-[#F0E8E3] px-4 py-3">
                  <p className="text-sm font-semibold text-slate-800">{item.label}</p>
                  <p className="mt-1 text-sm text-slate-500">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
