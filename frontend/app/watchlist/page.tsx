'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import PlotCard from '@/components/PlotCard';
import { Plot } from '@/data/mockPlots';

export default function WatchlistPage() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [watchlist, setWatchlist] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPlots() {
      try {
        const saved = localStorage.getItem('watchlist');

        if (!saved) {
          setLoading(false);
          return;
        }

        const savedIds: number[] = JSON.parse(saved);

        setWatchlist(savedIds);

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots`,
        );

        const data: Plot[] = await response.json();

        const savedPlots = data.filter((plot) => savedIds.includes(plot.id));

        setPlots(savedPlots);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    fetchPlots();
  }, []);

  function toggleWatchlist(plotId: number) {
    const updated = watchlist.filter((id) => id !== plotId);

    setWatchlist(updated);

    localStorage.setItem('watchlist', JSON.stringify(updated));

    setPlots((prev) => prev.filter((plot) => plot.id !== plotId));
  }

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-950">
              Your Watchlist
            </h1>

            <p className="mt-2 text-slate-500">
              Saved land opportunities you want to revisit.
            </p>
          </div>

          <div className="rounded-2xl bg-white px-5 py-3 shadow-sm">
            <p className="text-sm text-slate-500">Saved Plots</p>

            <p className="text-2xl font-bold text-[#B8644C]">{plots.length}</p>
          </div>
        </div>

        {loading ? (
          <div className="mt-10 text-slate-500">Loading watchlist...</div>
        ) : plots.length === 0 ? (
          <div className="mt-10 rounded-3xl bg-white p-10 text-center shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900">
              No saved plots yet
            </h2>

            <p className="mt-3 text-slate-500">
              Start bookmarking plots to build your investment shortlist.
            </p>
          </div>
        ) : (
          <div className="mt-8 space-y-5">
            {plots.map((plot) => (
              <PlotCard
                key={plot.id}
                plot={plot}
                selected={false}
                isSaved={true}
                onSelect={() => {}}
                onToggleWatchlist={() => toggleWatchlist(plot.id)}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
