import Image from 'next/image';
import { Bookmark, MapPin } from 'lucide-react';
import { Plot } from '@/data/mockPlots';

type Props = {
  plot: Plot;
  selected: boolean;
  onSelect: () => void;
};

export default function PlotCard({ plot, selected, onSelect }: Props) {
  return (
    <button
      onClick={onSelect}
      className={`grid w-full grid-cols-[36%_1fr] overflow-hidden rounded-3xl text-left transition hover:-translate-y-1 hover:shadow-xl ${
        selected
          ? 'border-2 border-[#EADBD4] bg-white shadow-xl shadow-[#EFE3DD]'
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

        <div className="absolute left-4 top-4 rounded-full bg-[#B8644C] px-4 py-2 text-xs font-semibold text-white shadow">
          ⭐ Best Match
        </div>

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
                Preference Match
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

        <div className="mt-5 flex items-center justify-between">
          <span className="rounded-2xl bg-[#F3E6E1] px-4 py-2 text-sm font-semibold text-[#B8644C] transition hover:bg-[#EADBD4]">
            View details
          </span>

          <Bookmark size={20} className="text-[#B0897A]" />
        </div>
      </div>
    </button>
  );
}
