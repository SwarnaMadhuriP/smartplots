'use client';

import { Home, TrendingUp, Sunset, Building2, Gauge } from 'lucide-react';

export type GoalKey =
  | 'build_home'
  | 'invest_appreciation'
  | 'retirement_lifestyle'
  | 'commercial'
  | 'maximize_value';

export type GoalDef = {
  key: GoalKey;
  icon: React.ElementType;
  title: string;
  tagline: string;
  description: string;
  accent: string;
};

export const GOALS: GoalDef[] = [
  {
    key: 'build_home',
    icon: Home,
    title: 'Build a Home',
    tagline: 'Ready-to-build land',
    description: 'Utilities, road access, and residential zoning matched to your budget.',
    accent: '#C7745A',
  },
  {
    key: 'invest_appreciation',
    icon: TrendingUp,
    title: 'Invest for Appreciation',
    tagline: 'High-growth potential',
    description: 'Plots with strong upside, matched to your risk appetite and time horizon.',
    accent: '#7A9E7E',
  },
  {
    key: 'retirement_lifestyle',
    icon: Sunset,
    title: 'Retirement / Lifestyle',
    tagline: 'Peaceful & low-risk',
    description: 'Quiet, scenic land with everything you need for a comfortable life.',
    accent: '#8B7EA8',
  },
  {
    key: 'commercial',
    icon: Building2,
    title: 'Commercial Development',
    tagline: 'Business-ready plots',
    description: 'Commercial zoning, road access, and scale for your development plans.',
    accent: '#5B8DB8',
  },
  {
    key: 'maximize_value',
    icon: Gauge,
    title: 'Maximize Value',
    tagline: 'Best land per dollar',
    description: 'The lowest price per acre in your preferred area, without compromising quality.',
    accent: '#A0845C',
  },
];

type Props = {
  onSelect: (goal: GoalKey) => void;
};

export default function GoalSelector({ onSelect }: Props) {
  return (
    <div className="flex flex-col gap-10 max-w-3xl mx-auto w-full py-8">
      {/* Heading */}
      <div className="text-center">
        <p className="text-xl font-semibold text-slate-800 tracking-tight">
          What are you looking to achieve?
        </p>
        <p className="mt-2 text-sm text-slate-500 max-w-md mx-auto">
          Your goal shapes every recommendation — choose the one that best describes your intention.
        </p>
      </div>

      {/* 3-col top row + 2-col bottom row */}
      <div className="flex flex-col gap-3">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {GOALS.slice(0, 3).map((goal) => (
            <GoalCard key={goal.key} goal={goal} onSelect={onSelect} />
          ))}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl mx-auto w-full">
          {GOALS.slice(3).map((goal) => (
            <GoalCard key={goal.key} goal={goal} onSelect={onSelect} />
          ))}
        </div>
      </div>
    </div>
  );
}

function GoalCard({ goal, onSelect }: { goal: GoalDef; onSelect: (k: GoalKey) => void }) {
  const Icon = goal.icon;
  return (
    <button
      id={`goal-${goal.key}`}
      onClick={() => onSelect(goal.key)}
      className="group relative flex flex-col gap-4 rounded-3xl border border-[#E7D3CC] bg-white p-6 text-left shadow-sm transition-all duration-200 hover:shadow-md hover:-translate-y-1 hover:border-[#D4A898] overflow-hidden"
    >
      {/* Subtle warm tint on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#FAF5F2] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none" />

      {/* Accent bar */}
      <div
        className="absolute top-0 left-0 right-0 h-0.5 rounded-t-3xl transition-all duration-300 group-hover:h-1"
        style={{ backgroundColor: goal.accent }}
      />

      {/* Icon */}
      <div
        className="relative flex h-11 w-11 items-center justify-center rounded-2xl shadow-sm transition-transform duration-200 group-hover:scale-110"
        style={{ backgroundColor: `${goal.accent}18` }}
      >
        <Icon size={20} style={{ color: goal.accent }} />
      </div>

      {/* Text */}
      <div className="relative">
        <span
          className="text-[10px] font-semibold uppercase tracking-widest"
          style={{ color: goal.accent }}
        >
          {goal.tagline}
        </span>
        <p className="mt-0.5 text-base font-bold text-slate-900">{goal.title}</p>
        <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">{goal.description}</p>
      </div>

      {/* Arrow hint */}
      <div className="relative self-end text-xs font-medium text-slate-300 group-hover:text-[#C7745A] transition-colors duration-200">
        Select →
      </div>
    </button>
  );
}
