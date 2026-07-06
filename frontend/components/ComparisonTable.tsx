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
              <th className="w-48 rounded-tl-2xl bg-[#FBF7F4] p-4 text-sm font-semibold text-slate-600 align-bottom">
                Feature
              </th>
              {plots.map((plot) => {
                const profile = profileMap.get(plot.id);
                return (
                  <th
                    key={plot.id}
                    className="bg-white p-4 text-sm font-semibold text-slate-900 align-bottom"
                  >
                    <div className="flex flex-col gap-1.5">
                      <div className="text-xs font-normal text-slate-400">Plot #{plot.id}</div>
                      <div className="font-semibold text-slate-900">{plot.title}</div>
                      {profile?.award_label && (
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <span className="h-1.5 w-1.5 rounded-full bg-[#C7745A] flex-shrink-0" />
                          <span className="text-xs font-medium text-[#B8644C] tracking-wide uppercase">
                            {profile.award_label}
                          </span>
                        </div>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>

          <tbody>
            {profiles && (
              <>
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
          className={`border-t border-[#E7D3CC] p-4 text-sm ${isHighlight
              ? 'font-bold text-[#B8644C] bg-white'
              : 'text-slate-700 bg-white'
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
