'use client';

import { ThumbsUp, DollarSign, ShieldOff, MapPinOff, Maximize2, LayoutList, RotateCcw } from 'lucide-react';

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
  style: 'positive' | 'neutral' | 'negative';
};

const FEEDBACK_OPTIONS: FeedbackDef[] = [
  { key: 'good_recommendation', label: 'Looks Good', icon: ThumbsUp, style: 'positive' },
  { key: 'too_expensive', label: 'Too Expensive', icon: DollarSign, style: 'negative' },
  { key: 'too_risky', label: 'Too Risky', icon: ShieldOff, style: 'negative' },
  { key: 'need_more_acreage', label: 'Need More Acreage', icon: Maximize2, style: 'neutral' },
  { key: 'wrong_location', label: 'Different Location', icon: MapPinOff, style: 'negative' },
  { key: 'show_alternatives', label: 'Show Alternatives', icon: LayoutList, style: 'neutral' },
];

const BASE_STYLES: Record<string, string> = {
  positive: 'border-[#C0DCBF] text-[#4A7E55] hover:bg-[#EDF5EF]',
  neutral:  'border-[#E7D3CC] text-slate-600 hover:border-[#C7745A] hover:text-[#C7745A] hover:bg-[#FAF5F2]',
  negative: 'border-[#EACAC5] text-[#B05040] hover:bg-[#FAF0EE]',
};

const ACTIVE_STYLES: Record<string, string> = {
  positive: 'border-[#6BA875] bg-[#EDF5EF] text-[#4A7E55]',
  neutral:  'border-[#C7745A] bg-[#F3E6E1] text-[#C7745A]',
  negative: 'border-[#C7745A] bg-[#F3E6E1] text-[#C7745A]',
};

type Props = {
  onFeedback: (option: FeedbackOption) => void;
  onRestart: () => void;
  loading: boolean;
  activeFeedback?: FeedbackOption;
};

export default function FeedbackBar({ onFeedback, onRestart, loading, activeFeedback }: Props) {
  return (
    <div className="flex w-full flex-col gap-2.5 bg-[#FAF5F2] px-4 py-3.5">

      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-semibold text-slate-800">Was this recommendation helpful?</p>
        <button
          onClick={onRestart}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-slate-400 transition-colors hover:text-[#C7745A] disabled:opacity-40"
        >
          <RotateCcw size={11} />
          Start over
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {FEEDBACK_OPTIONS.map(({ key, label, icon: Icon, style }) => {
          const isActive = activeFeedback === key;
          const isLoading = loading && isActive;
          return (
            <button
              key={key}
              id={`feedback-${key}`}
              onClick={() => onFeedback(key)}
              disabled={loading}
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition-all bg-white disabled:opacity-50 ${
                isActive ? ACTIVE_STYLES[style] : BASE_STYLES[style]
              }`}
            >
              {isLoading ? (
                <span className="h-3 w-3 rounded-full border-2 border-current/30 border-t-current animate-spin" />
              ) : (
                <Icon size={13} />
              )}
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
