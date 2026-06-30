'use client';

import Image from 'next/image';
import {
  MapPin,
  MoreVertical,
  FileText,
  RefreshCw,
  X,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
} from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { Plot } from '@/data/mockPlots';
import ReactMarkdown from 'react-markdown';

type Source = {
  filename: string;
  page: number | null;
  excerpt: string;
  document_type: string;
};

type PlotContext = {
  price: number;
  area_acres: number;
  zoning_type: string | null;
  city: string;
  state: string;
  road_access: boolean;
  water_access: boolean;
  electricity: boolean;
  sewer: boolean;
  nearby_landmarks: string | null;
  risk_notes: string | null;
};

type Props = {
  plot: Plot;
};

export default function RightPanel({ plot }: Props) {
  return <RightPanelContent key={plot.id} plot={plot} />;
}

const SUGGESTED_QUESTIONS = [
  { label: '📈 Investment Potential', query: 'Is this plot worth investing in?' },
  { label: '📜 Zoning & Rules', query: 'What are the zoning restrictions and land use rules?' },
  { label: '⚡ Utilities Check', query: 'What utilities and road access are available?' },
  { label: '⚠️ Risk Analysis', query: 'What are the key risk factors mentioned in reports?' },
];

function RightPanelContent({ plot }: Props) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [hasDocs, setHasDocs] = useState(false);
  const [askLoading, setAskLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [plotContext, setPlotContext] = useState<PlotContext | null>(null);

  // UI state
  const [openPillIndex, setOpenPillIndex] = useState<number | null>(null);
  const [showParcelData, setShowParcelData] = useState(false);
  const [feedbackVote, setFeedbackVote] = useState<'up' | 'down' | null>(null);

  const [isExpanded, setIsExpanded] = useState(false);
  const answerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (answer) {
      answerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [answer]);

  function toggleExpand() {
    setIsExpanded((prev) => !prev);
  }

  async function handleAskQuestion(queryToSubmit?: string) {
    const activeQuery = queryToSubmit || question;
    if (!activeQuery.trim()) return;

    setAskLoading(true);
    setAnswer('');
    setErrorMsg('');
    setSources([]);
    setMissingFields([]);
    setPlotContext(null);
    setShowParcelData(false);
    setOpenPillIndex(null);
    setFeedbackVote(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/${plot.id}/ask`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: activeQuery }),
        },
      );

      if (!response.ok) {
        setErrorMsg(
          response.status === 429
            ? 'The AI is temporarily rate-limited. Please wait a moment and try again.'
            : 'Something went wrong. Please try again.',
        );
        return;
      }

      const data = await response.json();

      setAnswer(data.answer || 'No answer returned.');
      setSources(data.sources || []);
      setHasDocs(data.has_documents ?? false);
      setMissingFields(data.missing_fields || []);
      setPlotContext(data.plot_context || null);
    } catch {
      setErrorMsg('Something went wrong. Please try again.');
    } finally {
      setAskLoading(false);
    }
  }

  async function handleFeedback(vote: 'up' | 'down') {
    setFeedbackVote(vote);
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/${plot.id}/ask/feedback`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, answer, vote }),
        },
      );
    } catch {
      // silently fail — feedback is best-effort
    }
  }

  const cleanAnswer = answer.replace(/\s*\(Source:[^)]+\)/gi, '').trim();

  return (
    <aside
      className={`relative h-screen shrink-0 border-l border-[#E7D3CC] bg-[#F8F3ED] transition-all duration-200 ${isExpanded ? 'w-[720px]' : 'w-[440px]'}`}
    >
      {/* Scrollable content */}
      <div className="h-full overflow-y-auto">
        <div className="p-6">
          <div className="rounded-3xl bg-white p-5 shadow-sm">
            {/* Header */}
            <div className="mb-5 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">Plot Overview</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={toggleExpand}
                  className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-[#C7745A] bg-stone-100 hover:bg-[#F3E6E1] px-2.5 py-1.5 rounded-xl transition shadow-xs"
                  title={isExpanded ? 'Collapse panel' : 'Expand panel for easier reading'}
                >
                  {isExpanded ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
                  <span>{isExpanded ? 'Collapse' : 'Expand'}</span>
                </button>
                <MoreVertical size={20} className="text-slate-400 hover:text-slate-600 cursor-pointer" />
              </div>
            </div>

            {/* Plot Image */}
            <div className="relative h-56 overflow-hidden rounded-2xl bg-stone-100">
              <Image src={plot.image} alt={plot.title} fill className="object-cover" />
            </div>

            {/* Title & Location */}
            <h2 className="mt-8 text-2xl font-bold text-slate-950">{plot.title}</h2>
            <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
              <MapPin size={16} />
              {plot.location}
            </div>
            <p className="mt-3 text-sm text-slate-600">
              {plot.acres} • {plot.zone}
            </p>

            {/* AI Match Score */}
            <div className="mt-8 rounded-3xl bg-[#F3E6E1] p-6 shadow-sm">
              <p className="text-sm font-semibold text-slate-900">AI Match Score</p>
              <div className="mt-4 flex items-center justify-between">
                <div>
                  <span className="text-5xl font-bold text-[#B8644C]">{plot.matchScore}</span>
                  <span className="text-sm text-slate-500"> /10</span>
                </div>
                <p className="w-32 text-sm leading-relaxed text-slate-600">
                  Ranked using your search intent
                </p>
              </div>
            </div>

            {/* Investment Snapshot */}
            <div className="mt-8">
              <h4 className="font-bold text-slate-900">Investment Snapshot</h4>
              <div className="mt-4 space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">5-Year Appreciation</span>
                  <span className="font-semibold">{plot.appreciation}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Rental Demand</span>
                  <span className="font-semibold">{plot.rentalDemand}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Ease of Resale</span>
                  <span className="font-semibold">{plot.liquidity}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Investment Risk</span>
                  <span className="font-semibold text-[#B8644C]">{plot.riskLevel}</span>
                </div>
              </div>
            </div>

            {/* Key Highlights */}
            <div className="mt-8">
              <h4 className="font-bold text-slate-900">Key Highlights</h4>
              <ul className="mt-4 space-y-3 text-sm text-slate-600">
                {plot.highlights.map((item) => (
                  <li key={item}>🏡 {item}</li>
                ))}
              </ul>
            </div>

            {/* Ask SmartPlots */}
            <div className="mt-6 rounded-3xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
              <h4 className="font-bold text-slate-900">Ask SmartPlots about this plot</h4>
              <p className="mt-1 text-sm text-slate-500">
                Powered by brochures, reports, and property records.
              </p>

              {/* Suggested questions */}
              <div className="mt-4">
                <div className="flex flex-wrap gap-1.5">
                  {SUGGESTED_QUESTIONS.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuestion(item.query);
                        handleAskQuestion(item.query);
                      }}
                      disabled={askLoading}
                      className="rounded-md border border-[#E7D3CC] bg-[#FAF5F2] px-2 py-1 text-[11px] font-medium text-slate-700 transition hover:border-[#C7745A] hover:bg-[#F3E6E1] hover:text-[#B8644C] disabled:opacity-50 text-left"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input */}
              <div className="mt-4 flex gap-2">
                <div className="relative flex min-w-0 flex-1 items-center">
                  <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAskQuestion(); }}
                    placeholder="Ask about risks, utilities, zoning..."
                    className="w-full rounded-xl border border-[#E7D3CC] px-4 py-3 pr-8 text-sm outline-none focus:border-[#C7745A]"
                  />
                  {question && (
                    <button
                      onClick={() => setQuestion('')}
                      className="absolute right-2 text-slate-400 hover:text-slate-600 p-1"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>
                <button
                  onClick={() => handleAskQuestion()}
                  disabled={askLoading || !question.trim()}
                  className="rounded-xl bg-[#C7745A] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#B8644C] disabled:opacity-60 flex items-center justify-center min-w-[60px]"
                >
                  {askLoading ? <RefreshCw size={16} className="animate-spin" /> : 'Ask'}
                </button>
              </div>

              {/* Error banner */}
              {errorMsg && (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 flex items-start gap-2">
                  <AlertTriangle size={14} className="text-red-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-red-700">{errorMsg}</p>
                </div>
              )}

              {/* Response */}
              {answer && (
                <div ref={answerRef} className="mt-4 space-y-3">
                  {/* Answer */}
                  <div className="prose prose-sm max-w-none rounded-xl bg-[#FAF5F2] p-4 text-slate-700 leading-relaxed">
                    <ReactMarkdown
                      components={{
                        h3: ({ children, ...props }) => (
                          <h3 className="text-sm font-bold text-slate-900 mt-3 mb-1.5 pb-1 border-b border-stone-200/60" {...props}>
                            {children}
                          </h3>
                        ),
                        h4: ({ children, ...props }) => (
                          <h4 className="text-xs font-bold text-slate-800 mt-2 mb-1" {...props}>
                            {children}
                          </h4>
                        ),
                        p: ({ children, ...props }) => (
                          <p className="mb-2.5 text-xs text-slate-700 leading-relaxed" {...props}>
                            {children}
                          </p>
                        ),
                        ul: ({ children, ...props }) => (
                          <ul className="my-2 space-y-1 pl-1 text-xs text-slate-700" {...props}>
                            {children}
                          </ul>
                        ),
                        li: ({ children, ...props }) => (
                          <li className="flex items-start gap-1.5 my-1 leading-relaxed" {...props}>
                            <span className="text-[#C7745A] font-bold mt-0.5">•</span>
                            <span className="flex-1">{children}</span>
                          </li>
                        ),
                        strong: ({ children, ...props }) => (
                          <strong className="font-semibold text-slate-900" {...props}>{children}</strong>
                        ),
                      }}
                    >
                      {cleanAnswer}
                    </ReactMarkdown>
                  </div>

                  {/* Anti-hallucination alert */}
                  {missingFields.length > 0 && (
                    <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 flex items-start gap-2">
                      <AlertTriangle size={14} className="text-amber-500 shrink-0 mt-0.5" />
                      <p className="text-xs text-amber-700">
                        Zoning or boundary data not verified in county records. Please cross-reference with the local planning department.
                      </p>
                    </div>
                  )}

                  {/* Citation pills */}
                  {hasDocs && sources.length > 0 && (
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1.5 flex items-center gap-1">
                        <FileText size={11} className="text-[#C7745A]" />
                        Sources
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {sources.map((src, i) => (
                          <div key={i} className="relative">
                            <button
                              onClick={() => setOpenPillIndex(openPillIndex === i ? null : i)}
                              className="flex items-center gap-1 rounded-full border border-[#E7D3CC] bg-[#FAF5F2] px-2.5 py-1 text-[11px] font-medium text-slate-600 hover:border-[#C7745A] hover:bg-[#F3E6E1] transition"
                            >
                              <FileText size={10} className="text-[#C7745A] shrink-0" />
                              <span className="max-w-[120px] truncate">{src.filename}</span>
                              {src.page && <span className="text-slate-400">· p.{src.page}</span>}
                            </button>

                            {openPillIndex === i && (
                              <div className="absolute bottom-full mb-2 left-0 w-64 bg-white rounded-xl border border-[#E7D3CC] shadow-lg p-3 z-30 text-left">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                                    {src.document_type || 'Document'}
                                  </span>
                                  <button onClick={() => setOpenPillIndex(null)} className="text-slate-400 hover:text-slate-600">
                                    <X size={12} />
                                  </button>
                                </div>
                                <p className="text-xs font-medium text-slate-800 mb-2">
                                  {src.filename}{src.page ? ` · Page ${src.page}` : ''}
                                </p>
                                <p className="font-mono text-[10px] leading-relaxed text-slate-600 bg-stone-50 p-2 rounded border border-stone-100 mb-2">
                                  &ldquo;{src.excerpt}&rdquo;
                                </p>
                                {plotContext && (
                                  <div className="text-[10px] text-slate-500 space-y-0.5 border-t border-stone-100 pt-2">
                                    <div>💰 ${plotContext.price.toLocaleString()}</div>
                                    <div>📐 {plotContext.area_acres} acres</div>
                                    {plotContext.zoning_type && <div>🏷️ Zoned: {plotContext.zoning_type}</div>}
                                    <div>
                                      🔌{' '}
                                      {[
                                        plotContext.road_access && 'Road',
                                        plotContext.water_access && 'Water',
                                        plotContext.electricity && 'Electric',
                                        plotContext.sewer && 'Sewer',
                                      ].filter(Boolean).join(' · ') || 'No utilities confirmed'}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Parcel data accordion */}
                  {plotContext && (
                    <div>
                      <button
                        onClick={() => setShowParcelData(!showParcelData)}
                        className="flex items-center gap-1 text-xs text-[#B8644C] font-medium hover:underline underline-offset-2"
                      >
                        Show parcel data used
                        {showParcelData ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                      </button>
                      {showParcelData && (
                        <ul className="mt-2 space-y-1.5 text-xs text-slate-600 bg-[#FAF5F2] rounded-xl p-3 border border-[#E7D3CC]">
                          <li className="flex justify-between">
                            <span className="text-slate-500">Road Access</span>
                            <span>{plotContext.road_access ? '✅' : '❌'}</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-slate-500">Water Access</span>
                            <span>{plotContext.water_access ? '✅' : '❌'}</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-slate-500">Electricity</span>
                            <span>{plotContext.electricity ? '✅' : '❌'}</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-slate-500">Sewer</span>
                            <span>{plotContext.sewer ? '✅' : '❌'}</span>
                          </li>
                          {plotContext.zoning_type && (
                            <li className="flex justify-between">
                              <span className="text-slate-500">Zoning</span>
                              <span className="font-medium capitalize">{plotContext.zoning_type}</span>
                            </li>
                          )}
                          <li className="flex justify-between">
                            <span className="text-slate-500">Area</span>
                            <span>{plotContext.area_acres} acres</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-slate-500">Location</span>
                            <span>{plotContext.city}, {plotContext.state}</span>
                          </li>
                          {plotContext.nearby_landmarks && (
                            <li>
                              <span className="text-slate-500 block">Nearby landmarks</span>
                              <span className="text-slate-700">{plotContext.nearby_landmarks}</span>
                            </li>
                          )}
                          {plotContext.risk_notes && (
                            <li>
                              <span className="text-slate-500 block">Known risks</span>
                              <span className="text-slate-700">{plotContext.risk_notes}</span>
                            </li>
                          )}
                        </ul>
                      )}
                    </div>
                  )}

                  {!hasDocs && (
                    <p className="text-xs text-slate-400 italic">
                      No uploaded documents for this plot — answered from plot data.
                    </p>
                  )}

                  {/* Feedback */}
                  <div className="flex items-center gap-2 pt-2 border-t border-stone-100">
                    <span className="text-[11px] text-slate-400">Was this helpful?</span>
                    <button
                      onClick={() => handleFeedback('up')}
                      disabled={feedbackVote !== null}
                      className={`rounded-lg p-1.5 transition ${feedbackVote === 'up' ? 'bg-green-100 text-green-600' : 'text-slate-400 hover:bg-stone-100 hover:text-slate-700'} disabled:opacity-60`}
                      title="Helpful"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      onClick={() => handleFeedback('down')}
                      disabled={feedbackVote !== null}
                      className={`rounded-lg p-1.5 transition ${feedbackVote === 'down' ? 'bg-amber-100 text-amber-600' : 'text-slate-400 hover:bg-stone-100 hover:text-slate-700'} disabled:opacity-60`}
                      title="Flag as inaccurate"
                    >
                      <ThumbsDown size={14} />
                    </button>
                    {feedbackVote === 'up' && (
                      <span className="text-[11px] text-green-600">Thanks for the feedback!</span>
                    )}
                    {feedbackVote === 'down' && (
                      <span className="text-[11px] text-amber-600">Flagged as inaccurate</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
