'use client';

import { Play, PlayCircle } from 'lucide-react';

const SMARTPLOTS_DEMO_URL =
  process.env.NEXT_PUBLIC_SMARTPLOTS_DEMO_URL ??
  'https://www.youtube.com/watch?v=TODO_SMARTPLOTS_DEMO';

export default function SidebarInfoCard() {
  return (
    <section className="relative mt-4 rounded-3xl border border-[#E7D3CC] bg-white p-5 shadow-md shadow-[#E7D3CC]/40">
      <div className="absolute right-4 top-4 rounded-full border border-[#E7D3CC] bg-[#FFFCFA] px-2.5 py-1 text-[11px] font-bold text-[#B8644C] shadow-sm">
        5 min
      </div>

      <div className="flex h-13 w-13 items-center justify-center rounded-full bg-[#F3E6E1] text-[#C7745A] shadow-sm">
        <PlayCircle size={24} />
      </div>

      <h2 className="mt-5 text-lg font-bold leading-snug text-slate-900">
        See SmartPlots in Action
      </h2>

      <p className="mt-3 text-sm leading-6 text-slate-600">
        Discover how SmartPlots uses AI agents, intelligent search, document
        intelligence, and deterministic scoring to recommend the right property
        for every buyer.
      </p>

      <a
        href={SMARTPLOTS_DEMO_URL}
        target="_blank"
        rel="noreferrer"
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#C7745A] px-4 py-3.5 text-sm font-bold text-white shadow-md shadow-[#E7D3CC] transition hover:-translate-y-0.5 hover:bg-[#B8644C] hover:shadow-lg active:translate-y-0"
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/20">
          <Play size={13} className="ml-0.5 fill-current" />
        </span>
        <span className="whitespace-nowrap">Watch Demo</span>
      </a>
    </section>
  );
}
