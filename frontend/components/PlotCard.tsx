import Image from 'next/image';
import { Heart, MapPin } from 'lucide-react';
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

type StandoutSignal = {
  icon: string;
  label: string;
};

function getStandoutSignals(plot: Plot): StandoutSignal[] {
  const signals: StandoutSignal[] = [];
  const addSignal = (signal: StandoutSignal) => {
    if (
      signals.length < 3 &&
      !signals.some((item) => item.label === signal.label)
    ) {
      signals.push(signal);
    }
  };

  const text = [
    plot.title,
    plot.description,
    plot.location,
    plot.nearby_landmarks,
    plot.ideal_for,
    plot.zoning_type,
    plot.zone,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  if (/tech|microsoft|amazon|nintendo|domain|legacy west|star/.test(text)) {
    addSignal({ icon: '🏢', label: 'Tech corridor' });
  } else if (/corridor|growth corridor/.test(text)) {
    addSignal({ icon: '📈', label: 'Growth corridor' });
  }
  if (/downtown|urban|infill|brooklyn|queens|hudson|metro-north/.test(text)) {
    addSignal({ icon: '🏙️', label: 'Urban infill upside' });
  }
  if (/lake|waterfront|beach|bay|river|coastal|sound|pier/.test(text)) {
    addSignal({ icon: '🌊', label: 'Lifestyle location' });
  }
  if (/mountain|tahoe|sedona|flagstaff|yosemite|recreation|cabin/.test(text)) {
    addSignal({ icon: '🏕️', label: 'Recreation appeal' });
  }
  if (/airport|port|highway|logistics|industrial/.test(text)) {
    addSignal({ icon: '🚗', label: 'Excellent road access' });
  }

  const utilityCount = [
    plot.road_access,
    plot.water_access,
    plot.electricity,
    plot.sewer,
  ].filter(Boolean).length;

  if (utilityCount === 4) {
    addSignal({ icon: '⚡', label: 'Utilities available' });
  } else if (utilityCount >= 3) {
    addSignal({ icon: '⚡', label: 'Strong utility readiness' });
  }

  const zoning = (plot.zoning_type ?? plot.zone ?? '').toLowerCase();
  if (/commercial|mixed/.test(zoning)) {
    addSignal({ icon: '🏗️', label: 'Flexible development' });
  } else if (/residential/.test(zoning)) {
    addSignal({ icon: '🏡', label: 'Residential build potential' });
  } else if (/agricultural|ranch|farm|vineyard/.test(text)) {
    addSignal({ icon: '🌾', label: 'Rural land use potential' });
  }

  if (plot.appreciation === 'High') {
    addSignal({ icon: '📈', label: 'Strong appreciation potential' });
  }
  if (plot.liquidity === 'High') {
    addSignal({ icon: '💰', label: 'Resale-friendly profile' });
  }
  if (plot.riskLevel === 'Low') {
    addSignal({ icon: '🛡️', label: 'Lower-risk fundamentals' });
  }

  const fallbackSignals = plot.highlights?.length
    ? plot.highlights
    : plot.reasons;

  fallbackSignals.forEach((signal) =>
    addSignal({ icon: '✓', label: signal }),
  );

  return signals.slice(0, 3);
}

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
  const standoutSignals = getStandoutSignals(plot);

  return (
    <div
      onClick={onSelect}
      role="button"
      tabIndex={0}
      className={`grid w-full grid-cols-[36%_1fr] overflow-hidden rounded-3xl text-left transition hover:-translate-y-1 hover:shadow-xl ${selected
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

            <div className="w-[156px] shrink-0 rounded-2xl border border-[#E7D3CC] bg-[#FAF5F2] px-4 py-3 shadow-sm">
              <div className="flex items-end gap-1">
                <span className="text-4xl font-bold leading-none text-[#B8644C]">
                  {plot.matchScore}
                </span>
                <span className="pb-1 text-sm font-semibold text-slate-500">/10</span>
              </div>

              <p className="mt-2 text-xs font-bold leading-snug text-slate-700">
                Plot Readiness Score
              </p>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white">
                <div
                  className="h-full rounded-full bg-[#C7745A]"
                  style={{ width: `${Math.max(0, Math.min(10, plot.matchScore)) * 10}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-5 rounded-2xl bg-[#F3ECE5] p-4">
            <p className="mb-2 text-sm font-semibold text-slate-900">
              Why SmartPlots Recommends This
            </p>

            <ul className="space-y-2 text-sm leading-relaxed text-slate-600">
              {standoutSignals.map((signal) => (
                <li key={signal.label} className="flex items-start gap-2">
                  <span className="shrink-0">{signal.icon}</span>
                  <span>{signal.label}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-5 flex items-center gap-3">

          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleCompare?.();
            }}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition ${isCompared
              ? 'border-[#C7745A] bg-[#F3E6E1] text-[#C7745A]'
              : 'border-[#E7D3CC] bg-white text-slate-600 hover:bg-[#F3E6E1]'
              }`}
          >
            {isCompared ? 'Added to Compare' : 'Compare'}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleWatchlist();
            }}
            className={`flex items-center gap-1.5 rounded-full border px-4 py-2 text-sm font-medium transition ${isSaved
              ? 'border-[#C7745A] bg-[#F3E6E1] text-[#C7745A]'
              : 'border-[#E7D3CC] bg-white text-slate-600 hover:bg-[#F3E6E1]'
              }`}
          >
            <Heart
              size={15}
              className={isSaved ? 'fill-[#C7745A]' : undefined}
            />
            {isSaved ? 'Saved' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
