'use client';

import {
  DollarSign,
  LayoutList,
  MapPin,
  Maximize2,
  RotateCcw,
  ShieldCheck,
  SlidersHorizontal,
  Zap,
} from 'lucide-react';

export type FeedbackOption =
  | 'good_recommendation'
  | 'too_expensive'
  | 'too_risky'
  | 'wrong_location'
  | 'need_more_acreage'
  | 'need_utilities'
  | 'prefer_lower_price_per_acre'
  | 'show_alternatives';

type FeedbackDef = {
  key: FeedbackOption;
  label: string;
  icon: React.ElementType;
};

const FEEDBACK_OPTIONS: FeedbackDef[] = [
  { key: 'too_expensive', label: 'Budget', icon: DollarSign },
  { key: 'wrong_location', label: 'Location', icon: MapPin },
  { key: 'need_more_acreage', label: 'Acreage', icon: Maximize2 },
  { key: 'need_utilities', label: 'Utilities', icon: Zap },
  { key: 'prefer_lower_price_per_acre', label: 'Value', icon: SlidersHorizontal },
  { key: 'too_risky', label: 'Lower Risk', icon: ShieldCheck },
  { key: 'show_alternatives', label: 'Show Alternatives', icon: LayoutList },
];

type Props = {
  onFeedback: (option: FeedbackOption) => void;
  onRestart: () => void;
  loading: boolean;
  activeFeedback?: FeedbackOption;
};

export default function FeedbackBar({ onFeedback, onRestart, loading, activeFeedback }: Props) {
  return (
    <section className="rounded-2xl border border-[#E7D3CC] bg-white px-5 py-4 shadow-sm">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <p className="text-base font-bold text-slate-950">Refine Your Recommendation</p>
          <p className="mt-1 text-sm text-slate-500">
            Tell us what matters most and we&apos;ll find an even better match.
          </p>
        </div>

        <div className="flex flex-wrap gap-2.5">
          {FEEDBACK_OPTIONS.map(({ key, label, icon: Icon }) => {
            const isActive = activeFeedback === key;
            const isLoading = loading && isActive;
            return (
              <button
                key={key}
                id={`feedback-${key}`}
                onClick={() => onFeedback(key)}
                disabled={loading}
                className={`inline-flex items-center gap-2 rounded-full border px-4 py-2.5 text-sm font-semibold transition-all disabled:cursor-not-allowed disabled:opacity-50 ${isActive
                    ? 'border-[#C7745A] bg-[#F8E8E1] text-[#C7745A]'
                    : 'border-[#E7D3CC] bg-white text-slate-700 hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-[#C7745A]'
                  }`}
              >
                {isLoading ? (
                  <span className="h-4 w-4 rounded-full border-2 border-current/30 border-t-current animate-spin" />
                ) : (
                  <Icon size={16} />
                )}
                {label}
              </button>
            );
          })}

          <button
            onClick={onRestart}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-full border border-[#E7D3CC] bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-[#C7745A] disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RotateCcw size={16} />
            Start Over
          </button>
        </div>
      </div>
    </section>
  );
}
