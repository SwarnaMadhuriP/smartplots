import Image from 'next/image';
import Link from 'next/link';
import { Bookmark, MapPin, Sparkles } from 'lucide-react';
import { Plot } from '@/data/mockPlots';

type Props = {
  plot: Plot;
  selected: boolean;
  isSaved: boolean;
  onToggleWatchlist: () => void;
  onSelect: () => void;
  isCompared?: boolean;
  onToggleCompare?: () => void;
  isBestMatch?: boolean;
};

export default function PlotCard({
  plot,
  selected,
  isSaved,
  onToggleWatchlist,
  onSelect,
  isCompared = false,
  onToggleCompare,
  isBestMatch = false,
}: Props) {
  return (
    <div
      onClick={onSelect}
      role="button"
      tabIndex={0}
      className={`grid w-full grid-cols-[36%_1fr] overflow-hidden rounded-3xl text-left transition hover:-translate-y-1 hover:shadow-xl ${
        selected
          ? 'border-2 border-[#C7745A] bg-white shadow-xl shadow-[#D8B4A6]/50 ring-4 ring-[#F3E6E1]'
          : 'border border-transparent bg-white shadow-sm'
      }`}
    >
      <div className="relative h-full min-h-[280px]">
        <Image
          src={plot.image}
          alt={plot.title}
          fill
          className="object-cover object-center"
        />
        {isBestMatch && (
          <div className="absolute left-4 top-4 rounded-full bg-[#B8644C] px-4 py-2 text-xs font-semibold text-white shadow">
            ⭐ Best Match
          </div>
        )}
        {selected && (
          <div className="absolute right-4 top-4 rounded-full bg-white px-4 py-2 text-xs font-semibold text-[#B8644C] shadow">
            Selected
          </div>
        )}
        <div className="absolute bottom-4 right-4 rounded-full bg-black/60 px-4 py-2 text-xs font-semibold text-white">
          {plot.acres}
        </div>
      </div>

      <div className="flex flex-col justify-between p-6">
        <div>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-2xl font-bold leading-tight text-slate-950">
                {plot.title}
              </h3>

              <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                <MapPin size={16} />
                {plot.location}
              </div>

              <p className="mt-3 text-xl font-bold text-[#B8644C]">
                {plot.price}
              </p>
            </div>

            <div className="rounded-2xl bg-[#EDF2EC] px-5 py-4 text-center">
              <p className="text-3xl font-bold text-[#5F7666]">
                {plot.matchScore}
              </p>

              <p className="mt-1 text-xs font-medium leading-tight text-slate-500">
                AI Match Score
              </p>
            </div>
          </div>

          <div className="mt-5 rounded-2xl bg-[#F3ECE5] p-4">
            <p className="mb-2 text-sm font-semibold text-slate-900">
              Why this matches you
            </p>

            <ul className="space-y-2 text-sm leading-relaxed text-slate-600">
              {(plot.aiReasons?.length ? plot.aiReasons : plot.reasons).map(
                (reason) => (
                  <li key={reason}>✓ {reason}</li>
                ),
              )}
            </ul>
          </div>
        </div>

        <div className="mt-5 flex items-center gap-3">
          <span className="mr-auto rounded-2xl bg-[#F3E6E1] px-4 py-2 text-sm font-semibold text-[#B8644C] transition hover:bg-[#EADBD4]">
            View details
          </span>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleWatchlist();
            }}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-[#E7D3CC] bg-white transition hover:bg-[#F3E6E1]"
          >
            <Bookmark
              size={20}
              className={
                isSaved ? 'fill-[#B8644C] text-[#B8644C]' : 'text-[#B0897A]'
              }
            />
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleCompare?.();
            }}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
              isCompared
                ? 'border-[#C7745A] bg-[#F3E6E1] text-[#C7745A]'
                : 'border-[#E7D3CC] bg-white text-slate-600 hover:bg-[#F3E6E1]'
            }`}
          >
            {isCompared ? 'Added to Compare' : 'Compare'}
          </button>

          <Link
            href={`/insights`}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1.5 rounded-full border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-[#F3E6E1]"
          >
            <Sparkles size={14} className="text-[#C7745A]" />
            Ask SmartPlots
          </Link>
        </div>
      </div>
    </div>
  );
}
