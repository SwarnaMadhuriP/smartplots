'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import type { ReactNode } from 'react';
import {
  ArrowUpRight,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  Download,
  FileText,
  GitCompare,
  Heart,
  Home,
  Layers,
  MapPin,
  MessageCircle,
  Shield,
  ShieldCheck,
  Sparkles,
  Star,
  Trophy,
  X,
  Zap,
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
  notices?: string[];
  reasoning: string[];
  risks: string[];
  tradeoffs: string[];
  alternatives: AltItem[];
  next_steps: string[];
  decision_trace?: {
    route: 'fast_recommendation' | 'specialist_review' | string;
    selected_specialists: string[];
    reason_for_route: string;
    top_score: number;
    score_gap: number;
  } | null;
  session_token: string;
};

type Props = {
  recommendation: AdvisorRecommendation;
  showAlternatives?: boolean;
  feedbackSlot?: ReactNode;
  comparisonPlotIds?: number[];
  compareMessage?: string;
  onToggleCompare?: (plotId: number) => void;
};

const PLOT_IMAGES_BY_ID: Record<number, string> = {
  1: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80',
  2: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
  3: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80',
  4: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1200&q=80',
  5: 'https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&w=1200&q=80',
  6: 'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80',
  7: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80',
  8: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=80',
};

function imageForPlot(plotId: number) {
  return PLOT_IMAGES_BY_ID[plotId] ?? PLOT_IMAGES_BY_ID[1];
}

function clampScore(value: number, max = 100) {
  return Math.max(0, Math.min(max, value));
}

function percentFromScore(score: number) {
  return Math.round(clampScore(score * 10));
}

function normalizeScore(score: number | undefined) {
  if (score === undefined) return undefined;
  return percentFromScore(score);
}

function zoningFromTitle(title: string) {
  const text = title.toLowerCase();
  if (text.includes('commercial')) return 'Commercial Zoning';
  if (text.includes('farm') || text.includes('ranch')) return 'Agricultural Zoning';
  return 'Residential Zoning';
}

function FitItem({ icon: Icon, text }: { icon: React.ElementType; text: string }) {
  return (
    <li className="flex items-start gap-3">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FAF1EC] text-[#C7745A]">
        <Icon size={16} />
      </span>
      <div className="min-w-0">
        <p className="text-sm font-normal leading-snug text-slate-700">{text}</p>
      </div>
    </li>
  );
}

function NextStep({
  icon: Icon,
  title,
  href,
  onClick,
}: {
  icon: React.ElementType;
  title: string;
  href?: string;
  onClick?: () => void;
}) {
  const content = (
    <>
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-[#FAF1EC] text-[#C7745A]">
        <Icon size={18} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-bold text-slate-900">{title}</p>
      </div>
      <ChevronRight size={17} className="text-slate-500" />
    </>
  );

  if (href) {
    return (
    <Link
      href={href}
      className="flex items-center gap-3 rounded-2xl border border-[#E7D3CC] bg-white px-4 py-3 shadow-sm transition hover:border-[#C7745A] hover:bg-[#FAF5F2]"
    >
      {content}
    </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-2xl border border-[#E7D3CC] bg-white px-4 py-3 text-left shadow-sm transition hover:border-[#C7745A] hover:bg-[#FAF5F2]"
    >
      {content}
    </button>
  );
}

const DOCUMENT_GROUPS = [
  {
    title: 'Overview',
    count: 3,
    description: 'Basic property information, highlights, parcel details, and neighborhood context.',
    icon: FileText,
    tone: 'green',
    files: ['brochure.pdf', 'property_fact_sheet.pdf', 'neighborhood_guide.pdf'],
  },
  {
    title: 'Investment',
    count: 2,
    description: 'Market analysis, ROI potential, and county growth insights.',
    icon: Trophy,
    tone: 'orange',
    files: ['investment_report.pdf', 'county_growth_report.pdf'],
  },
  {
    title: 'Land Readiness',
    count: 2,
    description: 'Utilities, soil quality, and land suitability reports.',
    icon: Layers,
    tone: 'blue',
    files: ['utility_report.pdf', 'soil_report.pdf'],
  },
  {
    title: 'Legal & Zoning',
    count: 2,
    description: 'Zoning rules, restrictions, disclosures, and compliance.',
    icon: ShieldCheck,
    tone: 'red',
    files: ['zoning_report.pdf', 'property_disclosure.pdf'],
  },
  {
    title: 'Due Diligence',
    count: 1,
    description: 'Checklist and key items to review before purchase.',
    icon: ClipboardList,
    tone: 'yellow',
    files: ['due_diligence_checklist.pdf'],
  },
];

const DOCUMENT_TONES: Record<string, string> = {
  green: 'bg-emerald-50 text-emerald-700',
  orange: 'bg-[#FAF1EC] text-[#C7745A]',
  blue: 'bg-sky-50 text-sky-700',
  red: 'bg-rose-50 text-rose-700',
  yellow: 'bg-amber-50 text-amber-700',
};

export default function RecommendationCard({
  recommendation,
  showAlternatives = false,
  feedbackSlot,
}: Props) {
  const { primary_recommendation: primary, alternatives } = recommendation;
  const [documentsOpen, setDocumentsOpen] = useState(false);
  const [selectedDocumentGroup, setSelectedDocumentGroup] = useState(DOCUMENT_GROUPS[0].title);
  const [alternativesExpanded, setAlternativesExpanded] = useState(false);
  const [selectedAlternative, setSelectedAlternative] = useState<AltItem | null>(null);
  const matchPct = percentFromScore(primary.score);
  const shouldShowAllAlternatives = showAlternatives || alternativesExpanded;
  const visibleAlternatives = shouldShowAllAlternatives ? alternatives : alternatives.slice(0, 3);
  const sortedScores = recommendation.recommended_plots
    .map((plot) => plot.score)
    .filter((score): score is number => Number.isFinite(score))
    .sort((a, b) => b - a);
  const fallbackTopScore = primary.score;
  const nextBestScore = sortedScores.find((score) => score < fallbackTopScore);
  const fallbackScoreGap = nextBestScore === undefined ? fallbackTopScore : fallbackTopScore - nextBestScore;
  const trace = recommendation.decision_trace;
  const topScore = trace?.top_score ?? fallbackTopScore;
  const scoreGap = trace?.score_gap ?? fallbackScoreGap;
  const decisionPath = trace?.route === 'specialist_review'
    ? 'Specialist Review'
    : 'Fast Recommendation';

  function getAlternativeScore(plotId: number) {
    return normalizeScore(
      recommendation.recommended_plots.find((plot) => plot.plot_id === plotId)?.score,
    );
  }

  function openDocuments() {
    setSelectedDocumentGroup(DOCUMENT_GROUPS[0].title);
    setDocumentsOpen(true);
  }

  const fitItems = recommendation.reasoning.length > 0
    ? recommendation.reasoning.slice(0, 6)
    : [primary.match_reason];

  const nextSteps = [
    {
      icon: FileText,
      title: 'View property documents',
      onClick: openDocuments,
    },
    {
      icon: MapPin,
      title: 'Open in map',
      href: '/map',
    },
    {
      icon: GitCompare,
      title: 'Compare with alternatives',
      href: `/comparisons?ids=${primary.plot_id}`,
    },
    {
      icon: MessageCircle,
      title: 'Ask SmartPlots',
      href: `/plots?plotId=${primary.plot_id}`,
    },
    {
      icon: Heart,
      title: 'Save to watchlist',
      href: '/watchlist',
    },
  ];
  const activeDocumentGroup =
    DOCUMENT_GROUPS.find((group) => group.title === selectedDocumentGroup) ?? DOCUMENT_GROUPS[0];
  const documentsModal = documentsOpen && typeof document !== 'undefined'
    ? createPortal(
      <div className="fixed inset-y-0 left-0 right-0 z-[1000] flex items-center justify-center bg-[#F3ECE5]/80 px-6 py-6 backdrop-blur-md md:left-64">
        <button
          type="button"
          aria-label="Close property documents"
          className="absolute inset-0 cursor-default"
          onClick={() => setDocumentsOpen(false)}
        />

        <section className="relative flex max-h-[calc(100vh-3rem)] w-full max-w-[820px] flex-col overflow-hidden rounded-3xl border border-[#E7D3CC] bg-white shadow-2xl shadow-[#D8C5BC]/60 animate-fadeIn">
          <div className="sticky top-0 z-10 flex items-start justify-between gap-6 border-b border-[#F0E4DF] bg-white px-6 py-5">
            <div>
              <h2 className="text-lg font-bold text-slate-950">Property Documents</h2>
              <p className="mt-1.5 text-sm leading-6 text-slate-600">
                10 verified reports used to generate this recommendation.
              </p>
            </div>
            <button
              type="button"
              aria-label="Close property documents"
              onClick={() => setDocumentsOpen(false)}
              className="rounded-full p-2 text-slate-500 transition hover:bg-[#FAF5F2] hover:text-slate-900"
            >
              <X size={20} />
            </button>
          </div>

          <div className="overflow-y-auto px-6 py-5">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-2xl border border-[#E7D3CC] bg-[#FBF8F5] px-4 py-3.5">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-sky-50 text-sky-700">
                    <FileText size={18} />
                  </span>
                  <div>
                    <p className="text-lg font-bold text-slate-950">10</p>
                    <p className="text-xs font-medium text-slate-500">Documents</p>
                  </div>
                </div>
              </div>
              <div className="rounded-2xl border border-[#E7D3CC] bg-[#FBF8F5] px-4 py-3.5">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-50 text-blue-700">
                    <ShieldCheck size={18} />
                  </span>
                  <div>
                    <p className="text-lg font-bold text-slate-950">100%</p>
                    <p className="text-xs font-medium text-slate-500">Verified</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {DOCUMENT_GROUPS.map(({ title, count, description, icon: Icon, tone }) => (
                <button
                  key={title}
                  type="button"
                  onClick={() => setSelectedDocumentGroup(title)}
                  className={`flex w-full items-center gap-4 rounded-2xl border px-4 py-4 text-left transition focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C7745A] ${
                    selectedDocumentGroup === title
                      ? 'border-[#C7745A] bg-[#FFF7F3]'
                      : 'border-[#E7D3CC] bg-white hover:border-[#C7745A] hover:bg-[#FAF5F2]'
                  }`}
                >
                  <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl ${DOCUMENT_TONES[tone]}`}>
                    <Icon size={19} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-slate-950">
                        {title} ({count})
                      </p>
                      <span className="rounded-md bg-[#FAF1EC] px-2 py-0.5 text-[10px] font-bold text-[#B8644C]">
                        PDF
                      </span>
                    </div>
                    <p className="mt-1 text-xs leading-5 text-slate-600">{description}</p>
                  </div>
                  <ChevronRight size={18} className="text-slate-500" />
                </button>
              ))}
            </div>

            <div className="mt-4 rounded-2xl border border-[#E7D3CC] bg-[#FFFCFA] px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-bold text-slate-950">
                    {activeDocumentGroup.title} documents
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {activeDocumentGroup.files.length} files in this category
                  </p>
                </div>
                <span className="rounded-md bg-[#FAF1EC] px-2 py-1 text-[10px] font-bold text-[#B8644C]">
                  PDF
                </span>
              </div>

              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {activeDocumentGroup.files.map((file) => (
                  <button
                    key={file}
                    type="button"
                    className="flex items-center gap-2 rounded-xl border border-[#EFE1DA] bg-white px-3 py-2 text-left text-xs font-medium text-slate-700 transition hover:border-[#C7745A] hover:text-[#C7745A]"
                  >
                    <FileText size={14} className="shrink-0 text-[#C7745A]" />
                    <span className="truncate">{file}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3.5">
              <div className="flex items-start gap-3">
                <Shield size={18} className="mt-0.5 shrink-0 text-emerald-700" />
                <p className="text-xs leading-5 text-slate-700">
                  All documents are verified and sourced from official reports, county records, and trusted public databases.
                </p>
              </div>
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-[11px] leading-5 text-slate-400">
                backend/uploads/documents/plot-{primary.plot_id}/
              </p>
              <button
                type="button"
                className="flex items-center justify-center gap-2 rounded-2xl border border-[#D65B3F] bg-white px-4 py-3 text-sm font-bold text-[#D65B3F] transition hover:bg-[#FAF1EC]"
              >
                <Download size={16} />
                Download All Documents
              </button>
            </div>
          </div>
        </section>
      </div>,
      document.body,
    )
    : null;
  const selectedAlternativeScore = selectedAlternative
    ? getAlternativeScore(selectedAlternative.plot_id)
    : undefined;
  const selectedAlternativeRawScore = selectedAlternativeScore === undefined
    ? undefined
    : selectedAlternativeScore / 10;
  const selectedAlternativeRank = selectedAlternative
    ? alternatives.findIndex((alternative) => alternative.plot_id === selectedAlternative.plot_id) + 2
    : undefined;
  const alternativeModal = selectedAlternative && typeof document !== 'undefined'
    ? createPortal(
      <div className="fixed inset-y-0 left-0 right-0 z-[1000] flex items-center justify-center bg-[#F3ECE5]/80 px-6 py-6 backdrop-blur-md md:left-64">
        <button
          type="button"
          aria-label="Close plot details"
          className="absolute inset-0 cursor-default"
          onClick={() => setSelectedAlternative(null)}
        />

        <section className="relative grid max-h-[calc(100vh-3rem)] w-full max-w-[880px] overflow-hidden rounded-3xl border border-[#E7D3CC] bg-white shadow-2xl shadow-[#D8C5BC]/60 animate-fadeIn md:grid-cols-[320px_1fr]">
          <div className="relative min-h-[240px] md:min-h-full">
            <Image
              src={imageForPlot(selectedAlternative.plot_id)}
              alt={selectedAlternative.title}
              fill
              sizes="(min-width: 768px) 320px, 100vw"
              className="object-cover"
            />
            {selectedAlternativeRank && (
              <span className="absolute left-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white text-sm font-bold text-slate-800 shadow-md">
                {selectedAlternativeRank}
              </span>
            )}
          </div>

          <div className="flex max-h-[calc(100vh-3rem)] flex-col overflow-y-auto px-6 py-5">
            <div className="flex items-start justify-between gap-5">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-[#C7745A]">Alternative Match</p>
                <h2 className="mt-2 text-2xl font-bold leading-tight text-slate-950">
                  {selectedAlternative.title}
                </h2>
                <p className="mt-2 text-sm font-semibold text-slate-600">
                  Score: {selectedAlternativeRawScore === undefined ? 'N/A' : `${selectedAlternativeRawScore.toFixed(1)} / 10`}
                </p>
              </div>
              <button
                type="button"
                aria-label="Close plot details"
                onClick={() => setSelectedAlternative(null)}
                className="rounded-full p-2 text-slate-500 transition hover:bg-[#FAF5F2] hover:text-slate-900"
              >
                <X size={20} />
              </button>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm font-medium text-slate-600">
              <span className="flex items-center gap-1.5">
                <MapPin size={15} className="text-slate-500" />
                {selectedAlternative.location}
              </span>
              <span className="text-[#D4BAB0]">•</span>
              <span className="flex items-center gap-1.5">
                <Layers size={15} className="text-slate-500" />
                {selectedAlternative.acres}
              </span>
              <span className="text-[#D4BAB0]">•</span>
              <span className="flex items-center gap-1.5">
                <Home size={15} className="text-slate-500" />
                {zoningFromTitle(selectedAlternative.title)}
              </span>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-[#E7D3CC] bg-[#FBF8F5] px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Price</p>
                <p className="mt-1 text-xl font-bold text-[#C95438]">{selectedAlternative.price}</p>
              </div>
              <div className="rounded-2xl border border-[#E7D3CC] bg-[#FBF8F5] px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Score</p>
                <p className="mt-1 text-xl font-bold text-slate-950">
                  {selectedAlternativeRawScore === undefined ? 'N/A' : `${selectedAlternativeRawScore.toFixed(1)} / 10`}
                </p>
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-[#E7D3CC] bg-[#FFFCFA] px-4 py-4">
              <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Why it is an alternative</p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {selectedAlternative.key_differentiator}
              </p>
            </div>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/plots?plotId=${selectedAlternative.plot_id}`}
                className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl bg-[#D65B3F] px-5 text-sm font-bold text-white shadow-md shadow-[#E7D3CC] transition hover:bg-[#BF4E36] active:scale-[0.98]"
              >
                View Plot Details
                <ArrowUpRight size={16} />
              </Link>
              <Link
                href={`/plots?plotId=${selectedAlternative.plot_id}`}
                className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl border border-[#E7D3CC] bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-[#C7745A]"
              >
                <Sparkles size={16} />
                Ask SmartPlots
              </Link>
            </div>
          </div>
        </section>
      </div>,
      document.body,
    )
    : null;

  return (
    <div className="flex h-full min-w-0 flex-col overflow-y-auto py-2 animate-fadeIn">
      <div className="mx-auto flex w-full max-w-[1600px] flex-col gap-3 px-2 pb-2">
        <section className="rounded-2xl border border-[#E7D3CC] bg-white p-4 shadow-sm shadow-[#E7D3CC]/50">
          <div className="grid gap-6 xl:grid-cols-[460px_minmax(0,1fr)_320px]">
            <div className="relative min-h-[260px] overflow-hidden rounded-2xl">
              <Image
                src={imageForPlot(primary.plot_id)}
                alt={primary.title}
                fill
                sizes="(min-width: 1280px) 460px, 100vw"
                className="object-cover"
              />
              <div className="absolute left-4 top-4 inline-flex items-center gap-2 rounded-full bg-[#D65B3F] px-4 py-2 text-xs font-bold uppercase tracking-wide text-white shadow-md">
                <Star size={14} fill="currentColor" />
                Top Recommendation
              </div>
            </div>

            <div className="flex min-w-0 flex-col justify-center">
              <div className="inline-flex w-fit items-center gap-2 rounded-full border border-[#E7D3CC] bg-[#FAF5F2] px-3 py-1.5 text-sm font-semibold text-slate-800">
                <Trophy size={15} className="text-[#C7745A]" />
                Best Match
              </div>

              <h2 className="mt-4 text-3xl font-bold leading-tight tracking-tight text-slate-950">
                {primary.title}
              </h2>

              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm font-medium text-slate-600">
                <span className="flex items-center gap-1.5">
                  <MapPin size={15} className="text-slate-500" />
                  {primary.location}
                </span>
                <span className="text-[#D4BAB0]">•</span>
                <span className="flex items-center gap-1.5">
                  <Layers size={15} className="text-slate-500" />
                  {primary.acres}
                </span>
                <span className="text-[#D4BAB0]">•</span>
                <span className="flex items-center gap-1.5">
                  <Home size={15} className="text-slate-500" />
                  {zoningFromTitle(primary.title)}
                </span>
              </div>

              <div className="mt-5 flex flex-wrap items-center gap-3">
                <p className="text-3xl font-bold text-[#C95438]">{primary.price}</p>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-[#FAF1EC] px-3 py-1.5 text-xs font-semibold text-slate-700">
                  <Zap size={13} className="text-[#C7745A]" />
                  Strong preference fit
                </span>
              </div>

              <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-700">
                {primary.match_reason}
              </p>

              <div className="mt-7 flex flex-wrap items-center gap-3">
                <Link
                  href={`/plots?plotId=${primary.plot_id}`}
                  className="inline-flex h-12 items-center gap-2 rounded-2xl bg-[#D65B3F] px-5 text-sm font-bold text-white shadow-md shadow-[#E7D3CC] transition hover:bg-[#BF4E36] active:scale-[0.98]"
                >
                  View Plot Details
                  <ArrowUpRight size={16} />
                </Link>
              </div>
            </div>

            <aside className="rounded-2xl bg-[#FBF4F0] p-7">
              <div className="text-xs font-bold uppercase tracking-wide text-slate-700">
                Smart Match
              </div>
              <div className="mt-3 flex items-end gap-1">
                <p className="text-5xl font-bold leading-none text-slate-950">{matchPct}</p>
                <p className="pb-1 text-lg font-medium text-slate-500">/100</p>
              </div>
              <div className="mt-7 grid gap-5 border-t border-[#E7D3CC] pt-5">
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wide text-slate-700">Decision Path</p>
                  <div className="inline-flex min-h-9 items-center gap-2 rounded-full bg-white px-3 py-2 text-sm font-bold text-slate-900">
                    <Zap size={15} className="text-[#C95438]" />
                    {decisionPath}
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wide text-slate-700">Top Score</p>
                  <p className="min-h-9 py-2 text-sm font-bold text-slate-900">{topScore.toFixed(1)} / 10</p>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wide text-slate-700">Score Gap</p>
                  <p className="min-h-9 py-2 text-sm font-bold text-slate-900">
                    +{scoreGap.toFixed(1)} over next best plot
                  </p>
                </div>
              </div>
            </aside>
          </div>
        </section>

        {recommendation.notices && recommendation.notices.length > 0 && (
          <section className="rounded-2xl border border-[#E7D3CC] bg-[#FAF5F2] px-5 py-4">
            <div className="flex flex-col gap-1 text-sm text-slate-700">
              {recommendation.notices.map((notice) => (
                <p key={notice}>{notice}</p>
              ))}
            </div>
          </section>
        )}

        <div className="grid gap-3 xl:grid-cols-[1.05fr_0.75fr_0.85fr]">
          <section className="rounded-2xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-950">Why this is a great fit</h3>
            <ul className="mt-6 grid gap-5 sm:grid-cols-2">
              {fitItems.map((reason, index) => {
                const icons = [CheckCircle2, MapPin, Layers, Home, ShieldCheck, Zap];
                const Icon = icons[index % icons.length];
                return <FitItem key={`${reason}-${index}`} icon={Icon} text={reason} />;
              })}
            </ul>
          </section>

          <section className="rounded-2xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-lg font-bold text-slate-950">Other great matches</h3>
              {alternatives.length > visibleAlternatives.length && (
                <button
                  type="button"
                  onClick={() => setAlternativesExpanded(true)}
                  className="text-xs font-semibold text-[#C95438] transition hover:text-[#A8452D]"
                >
                  View all ({alternatives.length})
                </button>
              )}
            </div>

            <div id="advisor-alternatives" className="mt-5 space-y-4">
              {visibleAlternatives.map((alternative, index) => {
                const altScore = getAlternativeScore(alternative.plot_id);

                return (
                  <button
                    key={alternative.plot_id}
                    type="button"
                    onClick={() => setSelectedAlternative(alternative)}
                    className="grid w-full grid-cols-[76px_1fr_64px] items-center gap-3 rounded-2xl text-left transition hover:bg-[#FAF5F2] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C7745A]"
                  >
                    <div className="relative h-16 overflow-hidden rounded-xl">
                      <Image
                        src={imageForPlot(alternative.plot_id)}
                        alt={alternative.title}
                        fill
                        sizes="76px"
                        className="object-cover"
                      />
                      <span className="absolute left-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-white text-xs font-bold text-slate-700">
                        {index + 2}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-bold text-slate-950">{alternative.title}</p>
                      <p className="mt-0.5 text-xs text-slate-500">{alternative.acres} · {alternative.location}</p>
                      <p className="mt-1 text-xs font-bold text-[#C95438]">{alternative.price}</p>
                    </div>
                    <div className="rounded-xl bg-[#FAF5F2] px-2 py-3 text-center">
                      <p className="text-lg font-bold leading-none text-slate-900">
                        {altScore === undefined ? 'N/A' : `${altScore}%`}
                      </p>
                      <p className="mt-1 text-[10px] font-medium text-slate-500">Match</p>
                    </div>
                  </button>
                );
              })}
            </div>

            {alternatives.length > visibleAlternatives.length && (
              <button
                type="button"
                onClick={() => setAlternativesExpanded(true)}
                className="mt-5 flex w-full items-center justify-center gap-2 rounded-2xl border border-[#E7D3CC] bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-[#C7745A]"
              >
                View All Alternatives
                <ArrowUpRight size={15} />
              </button>
            )}
          </section>

          <section className="rounded-2xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-950">Recommended next steps</h3>
            <div className="mt-5 space-y-3">
              {nextSteps.map((step) => (
                <NextStep key={step.title} {...step} />
              ))}
            </div>
          </section>
        </div>

        {(recommendation.risks.length > 0 || recommendation.tradeoffs.length > 0) && (
          <section className="grid gap-3 xl:grid-cols-2">
            {recommendation.risks.length > 0 && (
              <div className="rounded-2xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
                <h3 className="text-base font-bold text-slate-950">Risks to verify</h3>
                <ul className="mt-4 grid gap-3">
                  {recommendation.risks.slice(0, 4).map((risk, index) => (
                    <li key={index} className="flex items-start gap-3 text-sm leading-6 text-slate-600">
                      <ShieldCheck size={16} className="mt-1 shrink-0 text-[#C7745A]" />
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {recommendation.tradeoffs.length > 0 && (
              <div className="rounded-2xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
                <h3 className="text-base font-bold text-slate-950">Tradeoffs</h3>
                <ul className="mt-4 grid gap-3">
                  {recommendation.tradeoffs.slice(0, 4).map((tradeoff, index) => (
                    <li key={index} className="flex items-start gap-3 text-sm leading-6 text-slate-600">
                      <ClipboardList size={16} className="mt-1 shrink-0 text-[#C7745A]" />
                      {tradeoff}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {feedbackSlot}
      </div>

      {documentsModal}
      {alternativeModal}
    </div>
  );
}
