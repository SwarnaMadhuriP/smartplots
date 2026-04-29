import { Home, Map, Sparkles, Heart, Scale, Bookmark } from 'lucide-react';

const navItems = [
  { label: 'Discover Plots', icon: Home, active: true },
  { label: 'Map Explorer', icon: Map },
  { label: 'AI Insights', icon: Sparkles },
  { label: 'Watchlist', icon: Heart },
  { label: 'Comparisons', icon: Scale },
  { label: 'Saved Searches', icon: Bookmark },
];

export default function Sidebar() {
  return (
    <aside className="h-screen w-64 shrink-0 border-r border-[#E7D3CC] bg-[#F8F3ED] p-6">
      <div className="mb-10">
        <h1 className="tracking-tight text-2xl font-bold text-slate-900">
          SmartPlots
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          Find land. Make smarter moves.
        </p>
      </div>

      <nav className="space-y-3">
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className={`flex w-full items-center gap-4 rounded-2xl px-5 py-4 text-left text-sm font-medium transition ${
                item.active
                  ? 'bg-[#C7745A] text-white shadow-lg shadow-[#E7D3CC]'
                  : 'text-slate-700 hover:bg-[#F3E6E1]'
              }`}
            >
              <Icon size={20} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="mt-16 rounded-3xl border border-[#E7D3CC] bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold leading-snug text-slate-900">
          Land decisions deserve clarity.
        </h2>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          SmartPlots uses AI and real-world data to surface the right
          opportunities for you.
        </p>

        <button className="mt-6 text-sm font-semibold text-[#B8644C] transition hover:text-[#9F5E49]">
          How it works →
        </button>
      </div>
    </aside>
  );
}
