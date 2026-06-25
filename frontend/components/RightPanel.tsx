'use client';

import Image from 'next/image';
import { MapPin, MoreVertical } from 'lucide-react';
import { useState } from 'react';
import { Plot } from '@/data/mockPlots';
import ReactMarkdown from 'react-markdown';

type Props = {
  plot: Plot;
};

export default function RightPanel({ plot }: Props) {
  return <RightPanelContent key={plot.id} plot={plot} />;
}

function RightPanelContent({ plot }: Props) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<{ filename: string; page: number | null; excerpt: string }[]>([]);
  const [hasDocs, setHasDocs] = useState(false);
  const [askLoading, setAskLoading] = useState(false);

  async function handleAskQuestion() {
    if (!question.trim()) return;

    try {
      setAskLoading(true);
      setAnswer('');
      setSources([]);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/${plot.id}/ask`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question }),
        },
      );

      if (!response.ok) {
        throw new Error('Failed to ask AI');
      }

      const data = await response.json();

      setAnswer(data.answer || 'No answer returned.');
      setSources(data.sources || []);
      setHasDocs(data.has_documents ?? false);
    } catch {
      setAnswer('Something went wrong while asking AI.');
    } finally {
      setAskLoading(false);
    }
  }

  return (
    <aside className="h-screen w-[440px] shrink-0 overflow-y-auto border-l border-[#E7D3CC] bg-[#F8F3ED] p-6">
      <div className="rounded-3xl bg-white p-5 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">Plot Overview</h3>

          <MoreVertical size={20} />
        </div>

        <div className="relative h-56 overflow-hidden rounded-2xl bg-stone-100">
          <Image
            src={plot.image}
            alt={plot.title}
            fill
            className="object-cover"
          />
        </div>

        <h2 className="mt-8 text-2xl font-bold text-slate-950">{plot.title}</h2>

        <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
          <MapPin size={16} />
          {plot.location}
        </div>

        <p className="mt-3 text-sm text-slate-600">
          {plot.acres} • {plot.zone}
        </p>

        <div className="mt-8 rounded-3xl bg-[#F3E6E1] p-6 shadow-sm">
          <p className="text-sm font-semibold text-slate-900">AI Match Score</p>

          <div className="mt-4 flex items-center justify-between">
            <div>
              <span className="text-5xl font-bold text-[#B8644C]">
                {plot.matchScore}
              </span>

              <span className="text-sm text-slate-500"> /10</span>
            </div>

            <p className="w-32 text-sm leading-relaxed text-slate-600">
              Ranked using your search intent
            </p>
          </div>
        </div>

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

              <span className="font-semibold text-[#B8644C]">
                {plot.riskLevel}
              </span>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h4 className="font-bold text-slate-900">Key Highlights</h4>

          <ul className="mt-4 space-y-3 text-sm text-slate-600">
            {plot.highlights.map((item) => (
              <li key={item}>🏡 {item}</li>
            ))}
          </ul>
        </div>

        <div className="mt-6 rounded-3xl border border-[#E7D3CC] bg-white p-6">
          <h4 className="font-bold text-slate-900">Ask SmartPlots about this plot</h4>
          <p className="mt-1 text-sm text-slate-500">
            Powered by brochures, reports, and property records.
          </p>

          <div className="mt-4 flex gap-2">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleAskQuestion();
                }
              }}
              placeholder="Ask about risks, utilities, zoning..."
              className="min-w-0 flex-1 rounded-xl border border-[#E7D3CC] px-4 py-3 text-sm outline-none focus:border-[#C7745A]"
            />

            <button
              onClick={handleAskQuestion}
              disabled={askLoading}
              className="rounded-xl bg-[#C7745A] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#B8644C] disabled:opacity-60"
            >
              {askLoading ? '...' : 'Ask'}
            </button>
          </div>

          {answer && (
            <div className="mt-4 space-y-3">
              <div className="prose prose-sm max-w-none rounded-xl bg-[#FAF5F2] p-4 text-slate-700 prose-headings:text-slate-900 prose-strong:text-slate-900">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>

              {hasDocs && sources.length > 0 && (
                <div className="rounded-xl border border-[#E7D3CC] bg-white p-3">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {sources.map((src, i) => (
                      <span
                        key={i}
                        title={src.excerpt}
                        className="inline-flex items-center gap-1 rounded-full border border-[#E7D3CC] bg-[#FAF5F2] px-3 py-1 text-xs text-slate-600"
                      >
                        📄 {src.filename}{src.page ? ` · p${src.page}` : ''}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {!hasDocs && (
                <p className="text-xs text-slate-400 italic">No uploaded documents for this plot — answered from plot data.</p>
              )}
            </div>
          )}
        </div>

      </div>
    </aside>
  );
}
