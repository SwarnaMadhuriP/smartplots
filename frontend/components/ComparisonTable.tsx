import { ComparisonPlot } from '@/types/comparisons';

type Props = {
  plots: ComparisonPlot[];
};

export default function ComparisonTable({ plots }: Props) {
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
              {plots.map((plot) => (
                <th
                  key={plot.id}
                  className="bg-[#FBF7F4] p-4 text-sm font-semibold text-slate-900"
                >
                  {plot.title}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
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

function Row({ label, values }: { label: string; values: string[] }) {
  return (
    <tr>
      <td className="border-t border-[#E7D3CC] bg-[#FBF7F4] p-4 text-sm font-semibold text-slate-600">
        {label}
      </td>

      {values.map((value, index) => (
        <td
          key={`${label}-${index}`}
          className="border-t border-[#E7D3CC] p-4 text-sm text-slate-700"
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
