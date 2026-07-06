'use client';

import { Play, PlayCircle } from 'lucide-react';

const SMARTPLOTS_DEMO_URL =
  process.env.NEXT_PUBLIC_SMARTPLOTS_DEMO_URL ??
  'https://www.youtube.com/watch?v=TODO_SMARTPLOTS_DEMO';

export default function SidebarInfoCard() {
  return (
    <section className="relative mt-4 rounded-3xl border border-[#E7D3CC] bg-white p-4 shadow-md shadow-[#E7D3CC]/40">
      <div className="absolute right-3 top-3 rounded-full border border-[#E7D3CC] bg-[#FFFCFA] px-2.5 py-1 text-[11px] font-bold text-[#B8644C] shadow-sm">
        5 min
      </div>

      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#F3E6E1] text-[#C7745A] shadow-sm">
        <PlayCircle size={21} />
      </div>

      <h2 className="mt-4 text-base font-bold leading-snug text-slate-900">
        See SmartPlots in Action
      </h2>

      <a
        href={SMARTPLOTS_DEMO_URL}
        target="_blank"
        rel="noreferrer"
        className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#C7745A] px-4 py-3 text-sm font-bold text-white shadow-md shadow-[#E7D3CC] transition hover:-translate-y-0.5 hover:bg-[#B8644C] hover:shadow-lg active:translate-y-0"
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/20">
          <Play size={13} className="ml-0.5 fill-current" />
        </span>
        <span className="whitespace-nowrap">Watch Demo</span>
      </a>

      <p className="mt-4 text-xs leading-5 text-slate-600">
        See how agents, search, document intelligence, and scoring recommend
        the right property.
      </p>
    </section>
  );
}
