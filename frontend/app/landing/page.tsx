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

        <section className="mt-16 grid gap-8 pb-20 md:grid-cols-3">
          <div className="rounded-[2rem] border border-[#E7D3CC] bg-white p-8 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#F8E9E2] text-[#C7745A]">
              <Search size={24} />
            </div>

            <h3 className="mt-6 text-2xl font-bold text-slate-900">
              Natural Language Search
            </h3>

            <p className="mt-4 text-lg leading-relaxed text-slate-500">
              Search for land the way you think, using budget, location, zoning,
              and investment intent.
            </p>
          </div>

          <div className="rounded-[2rem] border border-[#E7D3CC] bg-white p-8 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#F8E9E2] text-[#C7745A]">
              <Map size={24} />
            </div>

            <h3 className="mt-6 text-2xl font-bold text-slate-900">
              Map Explorer
            </h3>

            <p className="mt-4 text-lg leading-relaxed text-slate-500">
              Explore plot locations visually with an interactive geospatial map
              experience.
            </p>
          </div>

          <div className="rounded-[2rem] border border-[#E7D3CC] bg-white p-8 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#F8E9E2] text-[#C7745A]">
              <Scale size={24} />
            </div>

            <h3 className="mt-6 text-2xl font-bold text-slate-900">
              Smart Comparisons
            </h3>

            <p className="mt-4 text-lg leading-relaxed text-slate-500">
              Compare plots side by side across price, acreage, utilities,
              zoning, and risk.
            </p>
          </div>
        </section>
      </section>
    </main>
  );
}
