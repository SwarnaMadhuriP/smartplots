'use client';

import { Search, Sparkles } from 'lucide-react';

type Props = {
  searchQuery: string;
  setSearchQuery: (value: string) => void;
  onSearch: (query: string) => void;
};

export default function SearchHero({
  searchQuery,
  setSearchQuery,
  onSearch,
}: Props) {
  function handleSearch() {
    onSearch(searchQuery);
  }

  return (
    <section className="mb-8 px-4 pb-4 pt-2">
      <div className="mt-4 flex items-center gap-4 rounded-full bg-white px-6 py-4 shadow-lg shadow-[#E7D3CC]">
        <Sparkles className="text-[#C7745A]" size={22} />

        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
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
    </section>
  );
}
