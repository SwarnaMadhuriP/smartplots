'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import ComparisonTable from '@/components/ComparisonTable';
import { ComparisonPlot } from '@/types/comparisons';

export default function ComparisonsPage() {
  const [plots, setPlots] = useState<ComparisonPlot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadComparisonPlots() {
      try {
        const storedIds = localStorage.getItem('comparisonPlotIds');

        const ids: number[] = storedIds ? JSON.parse(storedIds) : [];

        if (ids.length === 0) {
          setPlots([]);
          return;
        }

        const responses = await Promise.all(
          ids.map((id) =>
            fetch(`${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots/${id}`),
          ),
        );

        const data = await Promise.all(
          responses.map((response) => {
            if (!response.ok) {
              throw new Error('Failed to fetch comparison plot');
            }

            return response.json();
          }),
        );

        setPlots(data);
      } catch (error) {
        console.error('Error loading comparison plots:', error);

        setPlots([]);
      } finally {
        setLoading(false);
      }
    }

    loadComparisonPlots();
  }, []);

  const handleClearComparison = () => {
    localStorage.removeItem('comparisonPlotIds');
    setPlots([]);
  };

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        {loading ? (
          <div className="rounded-3xl bg-white p-8 text-slate-500 shadow-sm">
            Loading comparison...
          </div>
        ) : (
          <>
            <div className="mb-4 flex justify-end">
              <button
                onClick={handleClearComparison}
                className="rounded-full border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-[#C7745A] shadow-sm transition hover:bg-[#F3E6E1]"
              >
                Clear Comparison
              </button>
            </div>

            <ComparisonTable plots={plots} />
          </>
        )}
      </section>
    </main>
  );
}
