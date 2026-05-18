import { SavedSearch } from '@/types/savedSearch';
import { Search, Trash2, Bookmark } from 'lucide-react';

type SavedSearchesProps = {
  savedSearches: SavedSearch[];
  onRunSearch: (query: string) => void;
  onDeleteSearch: (id: string) => void;
};

export default function SavedSearches({
  savedSearches,
  onRunSearch,
  onDeleteSearch,
}: SavedSearchesProps) {
  return (
    <section className="rounded-[2rem] border border-[#E7D3CC] bg-white p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#F3E6E1] text-[#C7745A]">
          <Bookmark size={20} />
        </div>

        <div>
          <h2 className="text-xl font-bold text-slate-900">Saved Searches</h2>
          <p className="mt-1 text-sm text-slate-500">
            Quickly revisit land searches you care about.
          </p>
        </div>
      </div>

      <div className="mt-6 space-y-4">
        {savedSearches.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-[#E7D3CC] bg-[#FBF7F4] p-8 text-sm text-slate-500">
            No saved searches yet.
          </div>
        ) : (
          savedSearches.map((search) => (
            <div
              key={search.id}
              className="rounded-3xl border border-[#E7D3CC] bg-[#FBF7F4] p-5 transition hover:shadow-md"
            >
              <p className="text-base font-semibold text-slate-900">
                {search.label}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Saved {new Date(search.createdAt).toLocaleDateString()}
              </p>

              <div className="mt-4 flex gap-3">
                <button
                  onClick={() => onRunSearch(search.query)}
                  className="flex items-center gap-2 rounded-full bg-[#C7745A] px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-[#B8644C]"
                >
                  <Search size={15} />
                  Run Search
                </button>

                <button
                  onClick={() => onDeleteSearch(search.id)}
                  className="flex items-center gap-2 rounded-full border border-red-200 bg-white px-4 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50"
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
