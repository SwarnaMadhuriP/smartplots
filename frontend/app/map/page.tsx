'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import dynamic from 'next/dynamic';

import RightPanel from '@/components/RightPanel';
import { Plot } from '@/data/mockPlots';

const MapExplorer = dynamic(() => import('@/components/MapExplorer'), {
  ssr: false,
});

export default function MapPage() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPlots() {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots`,
        );

        if (!response.ok) {
          throw new Error('Failed to fetch plots');
        }

        const data: Plot[] = await response.json();

        setPlots(data);
        setSelectedPlotId(data[0]?.id ?? null);
      } catch (error) {
        console.error('Error fetching map plots:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchPlots();
  }, []);

  const selectedPlot =
    plots.find((plot) => plot.id === selectedPlotId) ?? plots[0];

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        {loading ? (
          <div className="rounded-3xl bg-white p-8 text-slate-500 shadow-sm">
            Loading map...
          </div>
        ) : (
          <MapExplorer
            plots={plots}
            selectedPlotId={selectedPlotId}
            onSelectPlot={setSelectedPlotId}
          />
        )}
      </section>

      {selectedPlot && (
        <RightPanel plot={selectedPlot} />
      )}
    </main>
  );
}
