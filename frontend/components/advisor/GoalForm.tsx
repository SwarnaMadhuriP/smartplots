'use client';

import { useState } from 'react';
import { ChevronLeft, Loader2 } from 'lucide-react';
import { GoalKey } from './GoalSelector';

export type GoalPreferences = {
  budget_max?: number;
  preferred_location?: string;
  min_acres?: number;
  utilities_required: string[];
  utilities_preferred: string[];
  road_access_required: boolean;
  zoning_preference?: string;
  commercial_zoning_required?: boolean;
  risk_tolerance?: string;
  time_horizon?: string;
  quiet_area?: boolean;
  price_per_acre_priority?: boolean;
};

const DEFAULT_PREFS: GoalPreferences = {
  utilities_required: [],
  utilities_preferred: [],
  road_access_required: false,
};

type FieldBase = {
  key: keyof GoalPreferences;
  label: string;
};

type FieldDef =
  | (FieldBase & { type: 'number'; placeholder: string; prefix?: string })
  | (FieldBase & { type: 'text'; placeholder: string })
  | (FieldBase & { type: 'radio'; options: { value: string; label: string }[] })
  | (FieldBase & { type: 'checkbox_group'; options: { value: string; label: string }[] })
  | (FieldBase & { type: 'toggle'; description?: string });

const UTILITY_OPTIONS = [
  { value: 'water', label: 'Water' },
  { value: 'electricity', label: 'Electricity' },
  { value: 'sewer', label: 'Sewer' },
];

const RISK_OPTIONS = [
  { value: 'low', label: 'Conservative' },
  { value: 'medium', label: 'Moderate' },
  { value: 'high', label: 'Aggressive' },
];

const HORIZON_OPTIONS = [
  { value: '1-3 years', label: '1–3 yrs' },
  { value: '3-5 years', label: '3–5 yrs' },
  { value: '5+ years', label: '5+ yrs' },
];

const GOAL_FIELDS: Record<GoalKey, FieldDef[]> = {
  build_home: [
    { type: 'number', key: 'budget_max', label: 'Maximum Budget', placeholder: '150,000', prefix: '$' },
    { type: 'text', key: 'preferred_location', label: 'Preferred Location', placeholder: 'City, State or Region' },
    { type: 'number', key: 'min_acres', label: 'Minimum Acreage', placeholder: '1.0' },
    { type: 'checkbox_group', key: 'utilities_required', label: 'Required Utilities', options: UTILITY_OPTIONS },
    { type: 'toggle', key: 'road_access_required', label: 'Road Access' },
    { type: 'text', key: 'zoning_preference', label: 'Preferred Zoning', placeholder: 'e.g. Residential, Agricultural' },
    { type: 'radio', key: 'risk_tolerance', label: 'Risk Tolerance', options: RISK_OPTIONS },
  ],
  invest_appreciation: [
    { type: 'number', key: 'budget_max', label: 'Maximum Budget', placeholder: '200,000', prefix: '$' },
    { type: 'text', key: 'preferred_location', label: 'Preferred Location', placeholder: 'City, State or Region' },
    { type: 'radio', key: 'risk_tolerance', label: 'Risk Tolerance', options: RISK_OPTIONS },
    { type: 'radio', key: 'time_horizon', label: 'Investment Horizon', options: HORIZON_OPTIONS },
    { type: 'number', key: 'min_acres', label: 'Minimum Acreage', placeholder: '1.0' },
    { type: 'checkbox_group', key: 'utilities_preferred', label: 'Preferred Utilities', options: UTILITY_OPTIONS },
  ],
  retirement_lifestyle: [
    { type: 'number', key: 'budget_max', label: 'Maximum Budget', placeholder: '120,000', prefix: '$' },
    { type: 'text', key: 'preferred_location', label: 'Preferred Location', placeholder: 'City, State or Region' },
    { type: 'toggle', key: 'quiet_area', label: 'Quiet / Rural Area', description: 'Prefer peaceful, less developed surroundings' },
    { type: 'checkbox_group', key: 'utilities_required', label: 'Required Utilities', options: UTILITY_OPTIONS },
    { type: 'toggle', key: 'road_access_required', label: 'Road Access' },
    { type: 'number', key: 'min_acres', label: 'Minimum Acreage', placeholder: '1.0' },
  ],
  commercial: [
    { type: 'number', key: 'budget_max', label: 'Maximum Budget', placeholder: '300,000', prefix: '$' },
    { type: 'text', key: 'preferred_location', label: 'Preferred Location', placeholder: 'City, State or Region' },
    { type: 'toggle', key: 'commercial_zoning_required', label: 'Preferred Zoning', description: 'Focus on plots with commercial zoning.' },
    { type: 'toggle', key: 'road_access_required', label: 'Road Access' },
    { type: 'number', key: 'min_acres', label: 'Minimum Acreage', placeholder: '2.0' },
    { type: 'radio', key: 'risk_tolerance', label: 'Risk Tolerance', options: RISK_OPTIONS },
  ],
  maximize_value: [
    { type: 'number', key: 'budget_max', label: 'Maximum Budget', placeholder: '100,000', prefix: '$' },
    { type: 'text', key: 'preferred_location', label: 'Preferred Location', placeholder: 'City, State or Region' },
    { type: 'number', key: 'min_acres', label: 'Minimum Acreage', placeholder: '2.0' },
    { type: 'toggle', key: 'price_per_acre_priority', label: 'Prioritize Lowest $/Acre', description: 'Weight recommendations towards best price per acre' },
    { type: 'checkbox_group', key: 'utilities_preferred', label: 'Preferred Utilities', options: UTILITY_OPTIONS },
    { type: 'radio', key: 'risk_tolerance', label: 'Risk Tolerance', options: RISK_OPTIONS },
  ],
};

export const GOAL_LABELS: Record<GoalKey, string> = {
  build_home: 'Build a Home',
  invest_appreciation: 'Invest for Appreciation',
  retirement_lifestyle: 'Retirement / Lifestyle',
  commercial: 'Commercial Development',
  maximize_value: 'Maximize Value',
};

const GOAL_BADGE_ICONS: Record<GoalKey, string> = {
  build_home: '🏡',
  invest_appreciation: '📈',
  retirement_lifestyle: '🌿',
  commercial: '🏢',
  maximize_value: '💰',
};

const GOAL_BADGE_LABELS: Record<GoalKey, string> = {
  build_home: 'Building a Home',
  invest_appreciation: 'Investing for Appreciation',
  retirement_lifestyle: 'Retirement & Lifestyle',
  commercial: 'Commercial Development',
  maximize_value: 'Maximize Value',
};

type Props = {
  goal: GoalKey;
  initialPrefs?: GoalPreferences;
  onBack: () => void;
  onSubmit: (prefs: GoalPreferences) => void;
  loading: boolean;
};

export default function GoalForm({ goal, initialPrefs, onBack, onSubmit, loading }: Props) {
  const [prefs, setPrefs] = useState<GoalPreferences>(initialPrefs ?? { ...DEFAULT_PREFS });
  const [validationMessage, setValidationMessage] = useState('');

  const fields = GOAL_FIELDS[goal] ?? [];

  function setField(key: keyof GoalPreferences, value: unknown) {
    setValidationMessage('');
    setPrefs((prev) => ({ ...prev, [key]: value }));
  }

  function toggleInList(key: 'utilities_required' | 'utilities_preferred', value: string) {
    setValidationMessage('');
    setPrefs((prev) => {
      const list = (prev[key] ?? []) as string[];
      return {
        ...prev,
        [key]: list.includes(value) ? list.filter((v) => v !== value) : [...list, value],
      };
    });
  }

  function hasAnyPreference(values: GoalPreferences) {
    return Object.values(values).some((value) => {
      if (Array.isArray(value)) return value.length > 0;
      if (typeof value === 'string') return value.trim().length > 0;
      if (typeof value === 'number') return Number.isFinite(value);
      if (typeof value === 'boolean') return value;
      return false;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!hasAnyPreference(prefs)) {
      setValidationMessage('Tell us at least one preference so SmartPlots can generate personalized recommendations.');
      return;
    }
    onSubmit(prefs);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 max-w-xl mx-auto w-full py-6 animate-fadeIn">
      {/* Goal badge + back */}
      <div className="flex items-center justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-1.5 text-sm font-medium text-slate-400 hover:text-slate-700 transition-colors"
        >
          <ChevronLeft size={15} />
          Change Goal
        </button>
        <div className="flex items-center gap-2 rounded-full border border-[#E7D3CC] bg-[#F8E8E1] px-4 py-1.5 text-sm font-semibold text-[#C7745A]">
          <span aria-hidden="true">{GOAL_BADGE_ICONS[goal]}</span>
          {GOAL_BADGE_LABELS[goal]}
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-[#E7D3CC]" />

      <p className="text-sm leading-6 text-slate-500">
        Tell us what&apos;s important to you.
      </p>

      {validationMessage && (
        <div className="rounded-2xl border border-[#E7D3CC] bg-[#F8E8E1] px-4 py-3 text-sm font-medium text-[#A85E47]">
          {validationMessage}
        </div>
      )}

      {/* Fields */}
      <div className="flex flex-col gap-5">
        {fields.map((field) => {
          /* Number / Text */
          if (field.type === 'number' || field.type === 'text') {
            return (
              <label key={String(field.key)} className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-slate-700">{field.label}</span>
                <div className="flex items-center gap-2 rounded-2xl border border-[#E7D3CC] bg-white px-4 py-3.5 shadow-sm transition focus-within:border-[#C7745A] focus-within:shadow-md">
                  {field.type === 'number' && 'prefix' in field && field.prefix && (
                    <span className="text-slate-400 font-medium">{field.prefix}</span>
                  )}
                  <input
                    type={field.type === 'number' ? 'number' : 'text'}
                    placeholder={field.placeholder}
                    value={(prefs[field.key] as string | number) ?? ''}
                    min={field.type === 'number' ? 0 : undefined}
                    onChange={(e) =>
                      setField(
                        field.key,
                        field.type === 'number'
                          ? e.target.value === '' ? undefined : parseFloat(e.target.value)
                          : e.target.value || undefined,
                      )
                    }
                    className="flex-1 bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-300"
                  />
                </div>
              </label>
            );
          }

          /* Radio pill group */
          if (field.type === 'radio') {
            return (
              <div key={String(field.key)} className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-slate-700">{field.label}</span>
                <div className="flex gap-2 flex-wrap">
                  {field.options.map((opt) => {
                    const active = prefs[field.key] === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setField(field.key, opt.value)}
                        className={`rounded-full border px-5 py-2 text-sm font-medium transition ${active
                          ? 'bg-[#C7745A] border-[#C7745A] text-white shadow-sm'
                          : 'border-[#E7D3CC] bg-white text-slate-500 hover:border-[#C7745A] hover:text-[#C7745A]'
                          }`}
                      >
                        {opt.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          }

          /* Checkbox group */
          if (field.type === 'checkbox_group') {
            const listKey = field.key as 'utilities_required' | 'utilities_preferred';
            const list = (prefs[listKey] ?? []) as string[];
            return (
              <div key={String(field.key)} className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-slate-700">{field.label}</span>
                <div className="flex gap-2 flex-wrap">
                  {field.options.map((opt) => {
                    const active = list.includes(opt.value);
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => toggleInList(listKey, opt.value)}
                        className={`rounded-full border px-5 py-2 text-sm font-medium transition ${active
                          ? 'bg-[#C7745A] border-[#C7745A] text-white shadow-sm'
                          : 'border-[#E7D3CC] bg-white text-slate-500 hover:border-[#C7745A] hover:text-[#C7745A]'
                          }`}
                      >
                        {opt.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          }

          /* Toggle */
          if (field.type === 'toggle') {
            const val = !!(prefs[field.key] as boolean | undefined);
            return (
              <div
                key={String(field.key)}
                className="flex items-center justify-between gap-4 rounded-2xl border border-[#E7D3CC] bg-white px-5 py-4 shadow-sm"
              >
                <div>
                  <p className="text-sm font-semibold text-slate-700">{field.label}</p>
                  {field.description && (
                    <p className="mt-0.5 text-xs leading-5 text-slate-400">{field.description}</p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => setField(field.key, !val)}
                  className={`relative shrink-0 h-6 w-11 rounded-full transition-colors duration-200 ${val ? 'bg-[#C7745A]' : 'bg-[#E7D3CC]'
                    }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${val ? 'translate-x-5' : ''
                      }`}
                  />
                </button>
              </div>
            );
          }

          return null;
        })}
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="mt-2 flex w-full items-center justify-center gap-2.5 rounded-2xl bg-[#C7745A] py-4 font-semibold text-white shadow-lg shadow-[#E7D3CC] transition hover:bg-[#B8644C] active:scale-[0.98] disabled:opacity-60"
      >
        {loading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            Finding your best plots…
          </>
        ) : (
          'Generate Recommendations'
        )}
      </button>
    </form>
  );
}
