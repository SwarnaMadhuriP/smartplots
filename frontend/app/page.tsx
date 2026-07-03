'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import SearchHero, {
  SearchFilters,
  emptySearchFilters,
} from '@/components/SearchHero';
import PlotCard from '@/components/PlotCard';
import RightPanel from '@/components/RightPanel';
import { Plot } from '@/data/mockPlots';
import { SavedSearch } from '@/types/savedSearch';
import { useSearchParams } from 'next/navigation';

type SortOption =
  | 'best_match'
  | 'price_asc'
  | 'price_desc'
  | 'acres_asc'
  | 'acres_desc'
  | 'newest'
  | 'ai_investment_score';

type SearchMode = 'db' | 'ai';

const SORT_LABELS: Record<SortOption, string> = {
  best_match: 'Best Match',
  price_asc: 'Price: Low to High',
  price_desc: 'Price: High to Low',
  acres_asc: 'Acres: Small to Large',
  acres_desc: 'Acres: Large to Small',
  newest: 'Newest Listings',
  ai_investment_score: 'AI Investment Score',
};

function numericValue(value: unknown): number {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = Number(
      value.replace(/[$,]/g, '').replace('Acres', '').trim(),
    );
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function sortPlots(plots: Plot[], sortBy: SortOption): Plot[] {
  if (sortBy === 'best_match') return [...plots];

  return [...plots].sort((a, b) => {
    if (sortBy === 'price_asc') {
      return (
        numericValue(a.rawPrice ?? a.price) -
        numericValue(b.rawPrice ?? b.price)
      );
    }
    if (sortBy === 'price_desc') {
      return (
        numericValue(b.rawPrice ?? b.price) -
        numericValue(a.rawPrice ?? a.price)
      );
    }
    if (sortBy === 'acres_asc') {
      return (
        numericValue(a.rawAcres ?? a.acres) -
        numericValue(b.rawAcres ?? b.acres)
      );
    }
    if (sortBy === 'acres_desc') {
      return (
        numericValue(b.rawAcres ?? b.acres) -
        numericValue(a.rawAcres ?? a.acres)
      );
    }
    if (sortBy === 'newest') {
      return (b.createdAt ?? '').localeCompare(a.createdAt ?? '');
    }
    if (sortBy === 'ai_investment_score') {
      return (
        numericValue(b.aiInvestmentScore ?? b.investmentScore ?? b.matchScore) -
        numericValue(a.aiInvestmentScore ?? a.investmentScore ?? a.matchScore)
      );
    }
    return 0;
  });
}

function HomeContent() {
  const [plots, setPlots] = useState<Plot[]>([]);
  const [basePlots, setBasePlots] = useState<Plot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<number | null>(null);
  const [watchlist, setWatchlist] = useState<number[]>([]);
  const [watchlistLoaded, setWatchlistLoaded] = useState(false);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFilters, setSearchFilters] =
    useState<SearchFilters>(emptySearchFilters);
  const searchParams = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [aiReasons] = useState<Record<number, string[]>>({});
  const [comparisonPlotIds, setComparisonPlotIds] = useState<number[]>([]);
  const [aiResponse, setAiResponse] = useState<string>('');
  const [searchMode, setSearchMode] = useState<SearchMode>('db');
  const [sortBy, setSortBy] = useState<SortOption>('best_match');

  const sortOptions = useMemo(() => {
    const options: SortOption[] = [
      'best_match',
      'price_asc',
      'price_desc',
      'acres_asc',
      'acres_desc',
      'newest',
    ];
    if (searchMode === 'ai') {
      options.push('ai_investment_score');
    }
    return options;
  }, [searchMode]);

  function selectPlotFromResults(data: Plot[], preferredPlotId?: number) {
    const preferredPlot = preferredPlotId
      ? data.find((plot) => plot.id === preferredPlotId)
      : undefined;

    setSelectedPlotId(preferredPlot?.id ?? data[0]?.id ?? null);
  }

  function normalizeFilters(filters: SearchFilters) {
    const normalized: Record<string, string | number | boolean> = {};

    Object.entries(filters).forEach(([key, value]) => {
      if (!value) return;

      if (['min_price', 'max_price', 'min_area', 'max_area'].includes(key)) {
        const numeric = Number(value);
        if (Number.isFinite(numeric)) {
          normalized[key] = numeric;
        }
        return;
      }

      if (
        ['road_access', 'water_access', 'electricity', 'sewer'].includes(key)
      ) {
        normalized[key] = value === 'Yes';
        return;
      }

      normalized[key] = value;
    });

    return normalized;
  }

  async function runUnifiedSearch(
    query = '',
    filters = searchFilters,
    preferredPlotId?: number,
  ) {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/search`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query,
            filters: normalizeFilters(filters),
            sort_by: sortBy,
          }),
        },
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      const mode: SearchMode = data.search_mode === 'ai' ? 'ai' : 'db';
      const nextSortBy =
        mode === 'db' && sortBy === 'ai_investment_score'
          ? 'best_match'
          : sortBy;

      setSearchMode(mode);
      setSortBy(nextSortBy);
      setBasePlots(data.plots);
      setPlots(sortPlots(data.plots, nextSortBy));
      setAiResponse(mode === 'ai' ? data.ai_summary || '' : '');
      selectPlotFromResults(sortPlots(data.plots, nextSortBy), preferredPlotId);
    } catch (error) {
      console.error('Error running search:', error);
      setError('Could not run search.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const searchFromUrl = searchParams.get('search') ?? '';
    const plotIdFromUrl = Number(searchParams.get('plotId'));
    const preferredPlotId =
      Number.isFinite(plotIdFromUrl) && plotIdFromUrl > 0
        ? plotIdFromUrl
        : undefined;

    setSearchQuery(searchFromUrl);
    runUnifiedSearch(searchFromUrl, emptySearchFilters, preferredPlotId);
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

  useEffect(() => {
    if (loading || !selectedPlotId) return;

    document
      .getElementById(`plot-card-${selectedPlotId}`)
      ?.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }, [loading, selectedPlotId]);

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

  const handleSearch = async (query: string, filters: SearchFilters) => {
    setSearchQuery(query);
    setSearchFilters(filters);
    await runUnifiedSearch(query, filters);
  };

  function handleSortChange(nextSortBy: SortOption) {
    setSortBy(nextSortBy);
    const sorted = sortPlots(basePlots, nextSortBy);
    setPlots(sorted);
    selectPlotFromResults(sorted, selectedPlotId ?? undefined);
  }

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
          filters={searchFilters}
          setFilters={setSearchFilters}
          onSearch={handleSearch}
        />

        <div className="mt-10 flex items-center justify-between">
          <p className="font-semibold text-slate-900">
            {loading
              ? 'Loading plots...'
              : `${plots.length} plots match your preferences`}
          </p>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-slate-500">
              Sort by:
              <select
                value={sortBy}
                onChange={(e) => handleSortChange(e.target.value as SortOption)}
                className="rounded-full border border-[#E7D3CC] bg-white px-3 py-2 text-sm font-semibold text-slate-900 outline-none transition focus:border-[#C7745A]"
              >
                {sortOptions.map((option) => (
                  <option key={option} value={option}>
                    {SORT_LABELS[option]}
                  </option>
                ))}
              </select>
            </label>

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
          {plots.map((plot, index) => (
            <div
              key={plot.id}
              id={`plot-card-${plot.id}`}
              className="scroll-mt-8"
            >
              <PlotCard
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
                isBestMatch={index === 0}
              />
            </div>
          ))}
        </div>
      </section>

      {selectedPlot && <RightPanel plot={selectedPlot} />}
    </main>
  );
}

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
          <Sidebar />
          <section className="flex-1 overflow-y-auto px-10 py-10">
            <div className="rounded-3xl bg-white p-8 text-slate-500 shadow-sm">
              Loading plots...
            </div>
          </section>
        </main>
      }
    >
      <HomeContent />
    </Suspense>
  );
}
