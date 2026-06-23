import { ComparisonPlot, ComparePlotProfile } from '@/types/comparisons';
import React from 'react';

type Props = {
  plots: ComparisonPlot[];
  profiles?: ComparePlotProfile[];
};

export default function ComparisonTable({ plots, profiles }: Props) {
  const profileMap = React.useMemo(() => {
    const map = new Map<number, ComparePlotProfile>();
    if (profiles) {
      profiles.forEach((p) => map.set(p.plot_id, p));
    }
    return map;
  }, [profiles]);

  if (plots.length === 0) {
    return (
      <div className="rounded-3xl border border-[#E7D3CC] bg-white p-8 text-slate-500 shadow-sm">
        No plots selected for comparison yet.
      </div>
    );
  }

  return (
    <section className="rounded-[2rem] border border-[#E7D3CC] bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-bold text-slate-900">Compare Plots</h1>
      <p className="mt-1 text-sm text-slate-500">
        Review land options side by side.
      </p>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[900px] border-separate border-spacing-0 text-left">
          <thead>
            <tr>
              <th className="w-48 rounded-tl-2xl bg-[#FBF7F4] p-4 text-sm font-semibold text-slate-500">
                Feature
              </th>
              {plots.map((plot) => {
                const profile = profileMap.get(plot.id);
                return (
                  <th
                    key={plot.id}
                    className="bg-[#FBF7F4] p-4 text-sm font-semibold text-slate-900 align-top"
                  >
                    {profile?.award_label && (
                      <div className="mb-2">
                        <span className="inline-block rounded-full bg-[#F3E6E1] px-2.5 py-1 text-xs font-semibold text-[#B8644C] border border-[#E7D3CC] shadow-sm whitespace-nowrap">
                          🏆 {profile.award_label}
                        </span>
                      </div>
                    )}
                    <div>{plot.title}</div>
                  </th>
                );
              })}
            </tr>
          </thead>

          <tbody>
            {profiles && (
              <>
                <Row
                  label="AI Suitability Score"
                  values={plots.map((p) => {
                    const score = profileMap.get(p.id)?.suitability_score;
                    return score !== undefined ? `${score} / 10` : 'N/A';
                  })}
                  isHighlight
                />
                <Row
                  label="Key Trade-offs"
                  values={plots.map((p) => {
                    return profileMap.get(p.id)?.key_tradeoff || 'N/A';
                  })}
                />
              </>
            )}
            <Row
              label="Price"
              values={plots.map((p) => `$${p.price.toLocaleString()}`)}
            />
            <Row
              label="Acres"
              values={plots.map((p) => `${p.area_acres} acres`)}
            />
            <Row
              label="Location"
              values={plots.map((p) => `${p.city}, ${p.state}`)}
            />
            <Row label="Zoning" values={plots.map((p) => p.zoning_type)} />
            <Row
              label="Road access"
              values={plots.map((p) => yesNo(p.road_access))}
            />
            <Row
              label="Water access"
              values={plots.map((p) => yesNo(p.water_access))}
            />
            <Row
              label="Electricity"
              values={plots.map((p) => yesNo(p.electricity))}
            />
            <Row label="Sewer" values={plots.map((p) => yesNo(p.sewer))} />
            <Row
              label="Risk notes"
              values={plots.map((p) => p.risk_notes || 'Not specified')}
            />
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Row({
  label,
  values,
  isHighlight = false,
}: {
  label: string;
  values: string[];
  isHighlight?: boolean;
}) {
  return (
    <tr>
      <td className="border-t border-[#E7D3CC] bg-[#FBF7F4] p-4 text-sm font-semibold text-slate-600">
        {label}
      </td>

      {values.map((value, index) => (
        <td
          key={`${label}-${index}`}
          className={`border-t border-[#E7D3CC] p-4 text-sm ${
            isHighlight
              ? 'font-bold text-[#B8644C] bg-[#FAF5F2]'
              : 'text-slate-700'
          }`}
        >
          {value}
        </td>
      ))}
    </tr>
  );
}

function yesNo(value: boolean) {
  return value ? 'Yes' : 'No';
}
