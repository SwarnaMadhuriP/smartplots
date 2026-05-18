'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import SavedSearches from '@/components/SavedSearches';
import { SavedSearch } from '@/types/savedSearch';
import { useRouter } from 'next/navigation';

export default function SavedSearchesPage() {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const router = useRouter();

  useEffect(() => {
    const stored = localStorage.getItem('savedSearches');

    if (stored) {
      setSavedSearches(JSON.parse(stored));
    }
  }, []);

  const handleDeleteSavedSearch = (id: string) => {
    const updated = savedSearches.filter((search) => search.id !== id);

    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));
  };

  const handleRunSavedSearch = (query: string) => {
    router.push(`/?search=${encodeURIComponent(query)}`);
  };

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 overflow-y-auto px-10 py-10">
        <SavedSearches
          savedSearches={savedSearches}
          onRunSearch={handleRunSavedSearch}
          onDeleteSearch={handleDeleteSavedSearch}
        />
      </section>
    </main>
  );
}
