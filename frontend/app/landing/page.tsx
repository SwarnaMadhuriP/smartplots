'use client';

import Link from 'next/link';
import { ArrowRight, Map, Search, Sparkles, Scale } from 'lucide-react';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#F3ECE5] text-slate-950">
      <section className="mx-auto max-w-7xl px-8 py-4">
        <nav className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight text-[#C7745A]">
              SmartPlots
            </h1>

            <p className="mt-1 text-lg text-slate-500">
              Find Your Acre, Smarter.
            </p>
          </div>

          <Link
            href="/"
            className="rounded-full bg-[#C7745A] px-7 py-4 text-sm font-semibold text-white shadow transition hover:scale-[1.02] hover:bg-[#B8644C]"
          >
            Open App
          </Link>
        </nav>

        <div className="mt-6 grid items-center gap-12 lg:grid-cols-2">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[#E7D3CC] bg-white px-5 py-3 text-sm text-[#C7745A] shadow-sm">
              <Sparkles size={16} />
              AI-powered land discovery
            </div>

            <h2 className="mt-8 text-7xl font-black leading-[0.95] tracking-tight text-slate-950">
              Find Your Acre,
              <span className="mt-3 block text-[#C7745A]">Smarter.</span>
            </h2>

            <p className="mt-8 max-w-xl text-2xl leading-relaxed text-slate-600">
              Discover, compare, and evaluate land plots using natural language
              search, geospatial exploration, and AI-generated investment
              insights.
            </p>

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                href="/"
                className="flex items-center gap-2 rounded-full bg-[#C7745A] px-8 py-5 text-lg font-semibold text-white shadow-lg shadow-[#E7D3CC] transition hover:-translate-y-0.5 hover:bg-[#B8644C]"
              >
                Start Exploring
                <ArrowRight size={20} />
              </Link>

              <Link
                href="/map"
                className="flex items-center gap-2 rounded-full border border-[#E7D3CC] bg-white px-8 py-5 text-lg font-semibold text-[#C7745A] shadow-sm transition hover:bg-[#F8F3EF]"
              >
                View Map
                <Map size={18} />
              </Link>
            </div>
          </div>

          <div className="rounded-[2.5rem] border border-[#E7D3CC] bg-white p-6 shadow-[0_20px_60px_rgba(0,0,0,0.08)]">
            <div className="rounded-[2rem] bg-[#F8F3EF] p-5">
              <div className="rounded-full border border-[#E7D3CC] bg-white px-6 py-4 text-base text-slate-500 shadow-sm">
                “Austin land under 100k with road access”
              </div>

              <div className="mt-5 space-y-4">
                {[
                  {
                    title: 'Green Valley Residential Plot',
                    location: 'Austin, TX',
                    price: '$85,000',
                    reason: '✓ Utilities available',
                  },
                  {
                    title: 'Farmland Opportunity',
                    location: 'Waco, TX',
                    price: '$60,000',
                    reason: '✓ Long-term land holding',
                  },
                  {
                    title: 'Budget Starter Plot',
                    location: 'Waco, TX',
                    price: '$45,000',
                    reason: '✓ Affordable entry point',
                  },
                ].map((plot) => (
                  <div
                    key={plot.title}
                    className="rounded-3xl border border-[#E7D3CC] bg-white p-5 transition hover:-translate-y-1 hover:shadow-md"
                  >
                    <h3 className="text-2xl font-bold text-slate-900">
                      {plot.title}
                    </h3>

                    <p className="mt-2 text-lg text-slate-500">
                      {plot.location}
                    </p>

                    <p className="mt-4 text-2xl font-bold text-[#C7745A]">
                      {plot.price}
                    </p>

                    <p className="mt-3 text-sm text-slate-500">{plot.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <section className="mt-24 pb-20">
          <h2 className="text-center text-4xl font-extrabold tracking-tight text-slate-950">
            How It Works: Agentic Workflow
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-center text-lg text-slate-500">
            SmartPlots orchestrates a team of specialized AI agents to automate
            land due diligence in seconds.
          </p>

          <div className="mx-auto mt-16 max-w-4xl rounded-[2.5rem] border border-[#E7D3CC] bg-white p-10 shadow-lg shadow-[#E7D3CC]/30">
            <div className="flex flex-col items-center">
              {/* User Query Node */}
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-6 py-4 font-semibold text-slate-700 shadow-sm transition hover:scale-105">
                💬 User Query
              </div>

              {/* Connector Arrow */}
              <div className="h-10 w-0.5 bg-[#C7745A]"></div>

              {/* Planner Agent Node */}
              <div className="rounded-2xl border border-[#C7745A] bg-[#FDF9F6] px-8 py-5 text-center shadow-md transition hover:scale-105">
                <span className="block text-xs font-bold uppercase tracking-wider text-[#C7745A]">
                  Orchestrator
                </span>
                <span className="text-xl font-extrabold text-slate-900">
                  Planner Agent
                </span>
              </div>

              {/* Branching Lines and Sub-Agents */}
              <div className="w-full">
                {/* Horizontal Bar */}
                <div className="flex justify-center">
                  <div className="h-0.5 w-[80%] bg-[#C7745A]"></div>
                </div>

                {/* Vertical Drops */}
                <div className="mx-auto flex w-[80%] justify-between">
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                </div>

                {/* Agent Cards */}
                <div className="grid grid-cols-5 gap-3 text-center">
                  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                    <span className="text-2xl">🔍</span>
                    <h4 className="mt-2 font-bold text-slate-900">
                      Search Agent
                    </h4>
                    <p className="mt-1 text-xs text-slate-400">
                      Extracts filters & retrieves plots
                    </p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                    <span className="text-2xl">💵</span>
                    <h4 className="mt-2 font-bold text-slate-900">
                      Investment Agent
                    </h4>
                    <p className="mt-1 text-xs text-slate-400">
                      Calculates scores & projections
                    </p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                    <span className="text-2xl">⚠️</span>
                    <h4 className="mt-2 font-bold text-slate-900">
                      Risk Agent
                    </h4>
                    <p className="mt-1 text-xs text-slate-400">
                      Evaluates site-specific risks
                    </p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                    <span className="text-2xl">📍</span>
                    <h4 className="mt-2 font-bold text-slate-900">
                      Location Agent
                    </h4>
                    <p className="mt-1 text-xs text-slate-400">
                      Analyzes regional growth & access
                    </p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                    <span className="text-2xl">📄</span>
                    <h4 className="mt-2 font-bold text-slate-900">
                      Doc Intel Agent
                    </h4>
                    <p className="mt-1 text-xs text-slate-400">
                      RAG similarity search on pgvector
                    </p>
                  </div>
                </div>
              </div>

              {/* Vertical Drops to Recommendation */}
              <div className="w-full">
                <div className="mx-auto flex w-[80%] justify-between">
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                  <div className="h-8 w-0.5 bg-[#C7745A]"></div>
                </div>

                <div className="flex justify-center">
                  <div className="h-0.5 w-[80%] bg-[#C7745A]"></div>
                </div>
              </div>

              <div className="h-10 w-0.5 bg-[#C7745A]"></div>

              {/* Recommendation Agent Node */}
              <div className="rounded-2xl border border-[#C7745A] bg-[#FDF9F6] px-8 py-5 text-center shadow-md transition hover:scale-105">
                <span className="block text-xs font-bold uppercase tracking-wider text-[#C7745A]">
                  Evaluator
                </span>
                <span className="text-xl font-extrabold text-slate-900">
                  Recommendation Agent
                </span>
              </div>

              {/* Connector Arrow */}
              <div className="h-10 w-0.5 bg-[#C7745A]"></div>

              {/* SmartPlots Response Node */}
              <div className="rounded-2xl bg-[#C7745A] px-6 py-4 font-semibold text-white shadow-md transition hover:scale-105">
                ✨ SmartPlots Response
              </div>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
