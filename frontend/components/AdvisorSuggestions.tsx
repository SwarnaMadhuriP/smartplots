'use client';

import { Sparkles } from 'lucide-react';

type Props = {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
};

export default function AdvisorSuggestions({ suggestions, onSelect }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-6">
      <div className="text-center">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#F3E6E1]">
          <Sparkles className="text-[#C7745A]" size={22} />
        </div>
        <p className="text-sm font-medium text-slate-700">What would you like to know?</p>
        <p className="mt-1 text-xs text-slate-400">Choose a question below or type your own.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => onSelect(s)}
            className="rounded-2xl border border-[#E7D3CC] bg-white px-4 py-3 text-left text-sm text-slate-700 shadow-sm transition hover:border-[#C7745A] hover:bg-[#FAF5F2] hover:text-slate-900"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
