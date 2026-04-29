'use client';

import { useState } from 'react';
import { Search, Sparkles, Plus } from 'lucide-react';

type Props = {
  onSearch: (query: string) => void;
};

export default function SearchHero({ onSearch }: Props) {
  const [query, setQuery] = useState('');

  function handleSearch() {
    onSearch(query);
  }

  return (
    <section className="mb-8 px-4 pb-4 pt-2">
      <div className="mt-4 flex items-center gap-4 rounded-full bg-white px-6 py-4 shadow-lg shadow-[#E7D3CC]">
        <Sparkles className="text-[#C7745A]" size={22} />

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          className="flex-1 bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
          placeholder="Try: Austin under 100k, Dallas commercial, farmland..."
        />

        <button
          onClick={handleSearch}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-[#C7745A] text-white shadow-lg shadow-[#E7D3CC] transition hover:bg-[#B8644C]"
        >
          <Search size={22} />
        </button>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        {['Austin', 'Under 100k', 'Commercial', 'Residential', 'Farmland'].map(
          (chip) => (
            <button
              key={chip}
              onClick={() => {
                const newQuery = chip;
                setQuery(newQuery);
                onSearch(newQuery);
              }}
              className="rounded-full border border-[#E7D3CC] bg-white px-5 py-2 text-sm text-slate-700 shadow-sm transition hover:bg-[#F3E6E1]"
            >
              {chip}
            </button>
          ),
        )}

        <button className="flex items-center gap-2 rounded-full border border-[#E7D3CC] bg-white px-5 py-2 text-sm text-slate-700 shadow-sm transition hover:bg-[#F3E6E1]">
          <Plus size={16} />
          Add preference
        </button>

        <button
          onClick={() => {
            setQuery('');
            onSearch('');
          }}
          className="text-sm text-slate-400 transition hover:text-slate-600"
        >
          Clear all
        </button>
      </div>
    </section>
  );
}
