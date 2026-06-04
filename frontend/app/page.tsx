'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import SearchHero from '@/components/SearchHero';
import PlotCard from '@/components/PlotCard';
import RightPanel from '@/components/RightPanel';
import { Plot } from '@/data/mockPlots';
import { SavedSearch } from '@/types/savedSearch';
import { useSearchParams } from 'next/navigation';

export default function Home() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<number | null>(null);
  const [watchlist, setWatchlist] = useState<number[]>([]);
  const [watchlistLoaded, setWatchlistLoaded] = useState(false);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const searchParams = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [aiReasons, setAiReasons] = useState<Record<number, string[]>>({});
  const [comparisonPlotIds, setComparisonPlotIds] = useState<number[]>([]);
  const [aiResponse, setAiResponse] = useState<string>('');

  async function fetchPlots(searchQuery = '') {
    try {
      setLoading(true);
      setError('');
      setAiResponse('');

      const url = searchQuery
        ? `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots?search=${encodeURIComponent(searchQuery)}`
        : `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/plots`;

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

  async function fetchAIPlots(searchQuery: string) {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/ai/search`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: searchQuery,
          }),
        },
      );

      if (!response.ok) {
        throw new Error('AI search failed');
      }

      const data = await response.json();

      setPlots(data.plots);
      setAiResponse(data.response);
      setSelectedPlotId(data.plots[0]?.id ?? null);
    } catch (error) {
      console.error('Error fetching AI plots:', error);
      setError('Could not run AI search.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const searchFromUrl = searchParams.get('search') ?? '';

    setSearchQuery(searchFromUrl);
    fetchPlots(searchFromUrl);
  }, [searchParams]);

  useEffect(() => {
    const saved = localStorage.getItem('watchlist');
    const stored = localStorage.getItem('savedSearches');
    const storedComparisonIds = localStorage.getItem('comparisonPlotIds');

    if (stored) {
      setSavedSearches(JSON.parse(stored));
    }
    if (saved) {
      try {
        setWatchlist(JSON.parse(saved));
      } catch {
        localStorage.removeItem('watchlist');
      }
    }
    if (storedComparisonIds) {
      setComparisonPlotIds(JSON.parse(storedComparisonIds));
    }

    setWatchlistLoaded(true);
  }, []);

  useEffect(() => {
    if (!watchlistLoaded) return;

    localStorage.setItem('watchlist', JSON.stringify(watchlist));
  }, [watchlist, watchlistLoaded]);

  const selectedPlot =
    plots.find((plot) => plot.id === selectedPlotId) ?? plots[0];

  function toggleWatchlist(plotId: number) {
    setWatchlist((prev) =>
      prev.includes(plotId)
        ? prev.filter((id) => id !== plotId)
        : [...prev, plotId],
    );
  }

  const handleSaveSearch = (query: string) => {
    if (!query.trim()) return;

    const alreadyExists = savedSearches.some(
      (search) => search.query.toLowerCase() === query.toLowerCase(),
    );

    if (alreadyExists) return;

    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      label: query,
      query,
      createdAt: new Date().toISOString(),
    };

    const updated = [newSearch, ...savedSearches];

    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));
  };

  const handleDeleteSavedSearch = (id: string) => {
    const updated = savedSearches.filter((search) => search.id !== id);

    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);

    if (query.trim()) {
      await fetchAIPlots(query);
    } else {
      setAiResponse('');
      await fetchPlots();
    }
  };

  const toggleCompare = (plotId: number) => {
    setComparisonPlotIds((prev) => {
      const updated = prev.includes(plotId)
        ? prev.filter((id) => id !== plotId)
        : [...prev, plotId].slice(0, 3);

      localStorage.setItem('comparisonPlotIds', JSON.stringify(updated));

      return updated;
    });
  };

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        <SearchHero
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearch={handleSearch}
        />

        <div className="mt-10 flex items-center justify-between">
          <p className="font-semibold text-slate-900">
            {loading
              ? 'Loading plots...'
              : `${plots.length} plots match your preferences`}
          </p>

          <div className="flex items-center gap-4">
            <p className="text-sm text-slate-500">
              Sort by:{' '}
              <span className="font-semibold text-slate-900">Relevance</span>
            </p>

            <button
              onClick={() => handleSaveSearch(searchQuery)}
              className="rounded-full border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-[#C7745A] shadow-sm transition hover:bg-[#F3E6E1]"
            >
              Save Search
            </button>
          </div>
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

        {aiResponse && (
          <div className="mt-6 rounded-2xl border border-[#E7D3CC] bg-white p-5 text-sm font-medium text-slate-700 shadow-sm">
            {aiResponse}
          </div>
        )}

        <div className="mt-6 space-y-5">
          {plots.map((plot) => (
            <PlotCard
              key={plot.id}
              isSaved={watchlist.includes(plot.id)}
              isCompared={comparisonPlotIds.includes(plot.id)}
              onToggleWatchlist={() => toggleWatchlist(plot.id)}
              onToggleCompare={() => toggleCompare(plot.id)}
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
