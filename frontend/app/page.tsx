'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import SearchHero from '@/components/SearchHero';
import PlotCard from '@/components/PlotCard';
import RightPanel from '@/components/RightPanel';
import { Plot } from '@/data/mockPlots';

export default function Home() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<number | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [aiReasons, setAiReasons] = useState<Record<number, string[]>>({});

  async function fetchPlots(searchQuery = '') {
    try {
      setLoading(true);
      setError('');

      const url = searchQuery
        ? `http://localhost:8000/plots?search=${encodeURIComponent(searchQuery)}`
        : 'http://localhost:8000/plots';

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Failed to fetch plots');
      }

      const data: Plot[] = await response.json();

      setPlots(data);
      setSelectedPlotId(data[0]?.id ?? null);
    } catch (error) {
      console.error('Error fetching plots:', error);

      setError('Could not load plots from the database.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchPlots();
  }, []);

  const selectedPlot =
    plots.find((plot) => plot.id === selectedPlotId) ?? plots[0];

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        <SearchHero onSearch={fetchPlots} />

        <div className="mt-10 flex items-center justify-between">
          <p className="font-semibold text-slate-900">
            {loading
              ? 'Loading plots...'
              : `${plots.length} plots match your preferences`}
          </p>

          <p className="text-sm text-slate-500">
            Sort by:{' '}
            <span className="font-semibold text-slate-900">Relevance</span>
          </p>
        </div>

        {error && (
          <div className="mt-6 rounded-2xl border border-red-100 bg-red-50 p-5 text-sm font-medium text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && plots.length === 0 && (
          <div className="mt-6 rounded-2xl bg-white p-8 text-slate-600 shadow-sm">
            No plots found in the database.
          </div>
        )}

        <div className="mt-6 space-y-5">
          {plots.map((plot) => (
            <PlotCard
              key={plot.id}
              plot={{
                ...plot,
                aiReasons: aiReasons[plot.id],
              }}
              selected={plot.id === selectedPlotId}
              onSelect={() => setSelectedPlotId(plot.id)}
            />
          ))}
        </div>
      </section>

      {selectedPlot && (
        <RightPanel plot={selectedPlot} setAiReasons={setAiReasons} />
      )}
    </main>
  );
}
