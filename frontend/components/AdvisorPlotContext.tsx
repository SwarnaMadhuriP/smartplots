'use client';

import { MapPin, DollarSign, AlertTriangle, Star } from 'lucide-react';

type Props = {
  plot: {
    id: number;
    title: string;
    city: string;
    state: string;
    price: string;
    matchScore: number;
    riskLevel: string;
    acres: string;
  };
};

export default function AdvisorPlotContext({ plot }: Props) {
  const riskColor =
    plot.riskLevel === 'low'
      ? 'text-emerald-600 bg-emerald-50 border-emerald-200'
      : plot.riskLevel === 'high'
        ? 'text-red-600 bg-red-50 border-red-200'
        : 'text-amber-600 bg-amber-50 border-amber-200';

  return (
    <div className="flex items-center gap-4 rounded-2xl border border-[#E7D3CC] bg-[#FAF5F2] px-5 py-4">
      {/* Score ring */}
      <div className="relative shrink-0 w-12 h-12">
        <svg className="w-12 h-12 -rotate-90" viewBox="0 0 48 48">
          <circle cx="24" cy="24" r="20" fill="none" stroke="#E7D3CC" strokeWidth="4" />
          <circle
            cx="24" cy="24" r="20" fill="none"
            stroke="#C7745A" strokeWidth="4"
            strokeDasharray={`${(plot.matchScore / 10) * 125.7} 125.7`}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-slate-800">
          {plot.matchScore}
        </span>
      </div>

      {/* Info */}
      <div className="min-w-0 flex-1">
        <p className="text-xs text-slate-400 mb-0.5">Plot #{plot.id}</p>
        <p className="font-semibold text-slate-900 text-sm truncate">{plot.title}</p>
        <div className="flex items-center gap-3 mt-1 flex-wrap">
          <span className="flex items-center gap-1 text-xs text-slate-500">
            <MapPin size={11} />
            {plot.city}, {plot.state}
          </span>
          <span className="flex items-center gap-1 text-xs text-slate-500">
            <DollarSign size={11} />
            {plot.price}
          </span>
          <span className="flex items-center gap-1 text-xs text-slate-500">
            <Star size={11} />
            {plot.acres}
          </span>
        </div>
      </div>

      {/* Risk badge */}
      <span className={`shrink-0 flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium ${riskColor}`}>
        <AlertTriangle size={10} />
        {plot.riskLevel} risk
      </span>
    </div>
  );
}
