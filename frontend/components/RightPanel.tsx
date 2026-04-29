'use client';

import Image from 'next/image';
import { MapPin, MoreVertical, Scale, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Plot } from '@/data/mockPlots';
import ReactMarkdown from 'react-markdown';

type Props = {
  plot: Plot;
  setAiReasons: React.Dispatch<React.SetStateAction<Record<number, string[]>>>;
};

type Analysis = {
  plot_id: number;
  investment_score: number;
  risk_level: string;
  growth_potential: string;
  summary: string;
  reasons: string[];
  pros: string[];
  cons: string[];
};

export default function RightPanel({ plot, setAiReasons }: Props) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [askLoading, setAskLoading] = useState(false);

  useEffect(() => {
    setAnalysis(null);
    setLoading(false);
    setQuestion('');
    setAnswer('');
    setAskLoading(false);
  }, [plot.id]);

  async function handleAnalyze() {
    try {
      setLoading(true);
      setAnalysis(null);

      const response = await fetch(
        `http://localhost:8000/plots/${plot.id}/analyze`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: 'Analyze this plot for investment potential.',
          }),
        },
      );

      if (!response.ok) {
        throw new Error('Failed to analyze plot');
      }

      const data = await response.json();

      setAnalysis(data);

      setAiReasons((prev) => ({
        ...prev,
        [plot.id]: data.reasons || [],
      }));
    } catch {
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleAskQuestion() {
    if (!question.trim()) return;

    try {
      setAskLoading(true);
      setAnswer('');

      const response = await fetch(
        `http://localhost:8000/plots/${plot.id}/analyze`,
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

      setAnswer(data.summary || data.answer || 'No answer returned.');
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
          <p className="text-sm font-semibold text-slate-900">
            {analysis ? 'AI Investment Score' : 'Preference Match'}
          </p>

          <div className="mt-4 flex items-center justify-between">
            <div>
              <span className="text-5xl font-bold text-[#B8644C]">
                {analysis ? analysis.investment_score : plot.matchScore}
              </span>

              <span className="text-sm text-slate-500"> /10</span>
            </div>

            <p className="w-32 text-sm leading-relaxed text-slate-600">
              {analysis
                ? `${analysis.growth_potential} growth potential`
                : 'Based on your selected preferences'}
            </p>
          </div>
        </div>

        <div className="mt-8">
          <h4 className="font-bold text-slate-900">Investment Snapshot</h4>

          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Est. Appreciation (5 yr)</span>

              <span className="font-semibold">{plot.appreciation}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">Rental Demand</span>

              <span className="font-semibold">{plot.rentalDemand}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">Liquidity</span>

              <span className="font-semibold">{plot.liquidity}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">Risk Level</span>

              <span className="font-semibold text-[#B8644C]">
                {analysis?.risk_level ?? plot.riskLevel}
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

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="mt-8 flex w-full items-center justify-center gap-2 rounded-2xl bg-[#C7745A] py-4 font-semibold text-white shadow-lg shadow-[#E7D3CC] transition hover:bg-[#B8644C] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading && <Loader2 size={18} className="animate-spin" />}

          {loading ? 'Analyzing plot...' : 'View full analysis →'}
        </button>

        {analysis && (
          <div className="mt-6 space-y-5 rounded-3xl border border-[#E7D3CC] bg-[#FAF5F2] p-6">
            <h4 className="text-lg font-bold text-slate-900">
              AI Full Analysis
            </h4>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-white p-4">
                <p className="text-xs text-slate-500">Investment Score</p>

                <p className="mt-1 text-2xl font-bold text-[#B8644C]">
                  {analysis.investment_score}/10
                </p>
              </div>

              <div className="rounded-xl bg-white p-4">
                <p className="text-xs text-slate-500">Risk Level</p>

                <p className="mt-1 text-2xl font-bold text-[#B8644C]">
                  {analysis.risk_level}
                </p>
              </div>

              <div className="col-span-2 rounded-xl bg-white p-4">
                <p className="text-xs text-slate-500">Growth Potential</p>

                <p className="mt-1 text-lg font-semibold text-[#B8644C]">
                  {analysis.growth_potential}
                </p>
              </div>
            </div>

            <div>
              <h5 className="mb-2 font-semibold text-slate-900">Summary</h5>

              <p className="break-words text-sm leading-relaxed text-slate-700">
                {analysis.summary}
              </p>
            </div>

            <div>
              <h5 className="mb-2 font-semibold text-slate-900">Reasons</h5>

              <ul className="space-y-2">
                {analysis.reasons?.map((reason, index) => (
                  <li
                    key={index}
                    className="rounded-xl bg-white/80 p-3 text-sm text-slate-700"
                  >
                    ✓ {reason}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h5 className="mb-2 font-semibold text-slate-900">Pros</h5>

              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
                {analysis.pros?.map((pro, index) => (
                  <li key={index}>{pro}</li>
                ))}
              </ul>
            </div>

            <div>
              <h5 className="mb-2 font-semibold text-slate-900">Cons</h5>

              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
                {analysis.cons?.map((con, index) => (
                  <li key={index}>{con}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        <div className="mt-6 rounded-3xl border border-[#E7D3CC] bg-white p-6">
          <h4 className="font-bold text-slate-900">Ask about this plot</h4>

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
            <div className="prose prose-sm mt-4 max-w-none rounded-xl bg-[#FAF5F2] p-4 text-slate-700 prose-headings:text-slate-900 prose-strong:text-slate-900">
              <ReactMarkdown>{answer}</ReactMarkdown>
            </div>
          )}
        </div>

        <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-2xl border border-[#E7D3CC] bg-white py-4 font-semibold text-slate-700 transition hover:bg-[#FAF5F2]">
          <Scale size={18} />
          Compare this plot
        </button>
      </div>
    </aside>
  );
}
