'use client';

import {
  ChevronDown,
  RotateCcw,
  Search,
  SlidersHorizontal,
  Sparkles,
} from 'lucide-react';
import { useMemo, useState } from 'react';

export type SearchFilters = {
  city: string;
  state: string;
  min_price: string;
  max_price: string;
  min_area: string;
  max_area: string;
  zoning_type: string;
  listing_type: string;
  status: string;
  road_access: string;
  water_access: string;
  electricity: string;
  sewer: string;
};

export const emptySearchFilters: SearchFilters = {
  city: '',
  state: '',
  min_price: '',
  max_price: '',
  min_area: '',
  max_area: '',
  zoning_type: '',
  listing_type: '',
  status: '',
  road_access: '',
  water_access: '',
  electricity: '',
  sewer: '',
};

type Props = {
  searchQuery: string;
  setSearchQuery: (value: string) => void;
  filters: SearchFilters;
  setFilters: (filters: SearchFilters) => void;
  onSearch: (query: string, filters: SearchFilters) => void;
};

export default function SearchHero({
  searchQuery,
  setSearchQuery,
  filters,
  setFilters,
  onSearch,
}: Props) {
  const [filtersOpen, setFiltersOpen] = useState(false);
  const activeFilterCount = useMemo(
    () => Object.values(filters).filter(Boolean).length,
    [filters],
  );

  function handleSearch() {
    onSearch(searchQuery, filters);
  }

  function updateFilter(key: keyof SearchFilters, value: string) {
    setFilters({ ...filters, [key]: value });
  }

  function clearFilters() {
    setFilters(emptySearchFilters);
    onSearch(searchQuery, emptySearchFilters);
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
          placeholder="Search by city, landmark, budget, acres, or ask naturally..."
        />

        <button
          onClick={handleSearch}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-[#C7745A] text-white shadow-lg shadow-[#E7D3CC] transition hover:bg-[#B8644C]"
        >
          <Search size={22} />
        </button>
      </div>

      <div className="mt-3 flex items-center justify-between px-2">
        <button
          onClick={() => setFiltersOpen((open) => !open)}
          className="flex items-center gap-2 rounded-full border border-[#E7D3CC] bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-[#F3E6E1]"
        >
          <SlidersHorizontal size={16} className="text-[#C7745A]" />
          Filters
          {activeFilterCount > 0 && (
            <span className="rounded-full bg-[#F3E6E1] px-2 py-0.5 text-xs font-semibold text-[#C7745A]">
              {activeFilterCount}
            </span>
          )}
          <ChevronDown
            size={16}
            className={`transition ${filtersOpen ? 'rotate-180' : ''}`}
          />
        </button>

        {activeFilterCount > 0 && !filtersOpen && (
          <button
            onClick={clearFilters}
            className="text-sm font-medium text-[#C7745A] transition hover:text-[#B8644C]"
          >
            Clear Filters
          </button>
        )}
      </div>

      {filtersOpen && (
        <div className="mt-3 rounded-2xl border border-[#E7D3CC] bg-white p-4 shadow-sm">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <FilterInput
              label="City"
              value={filters.city}
              onChange={(value) => updateFilter('city', value)}
            />
            <FilterInput
              label="State"
              value={filters.state}
              onChange={(value) => updateFilter('state', value)}
            />
            <FilterInput
              label="Min Price"
              type="number"
              value={filters.min_price}
              onChange={(value) => updateFilter('min_price', value)}
            />
            <FilterInput
              label="Max Price"
              type="number"
              value={filters.max_price}
              onChange={(value) => updateFilter('max_price', value)}
            />
            <FilterInput
              label="Min Acres"
              type="number"
              value={filters.min_area}
              onChange={(value) => updateFilter('min_area', value)}
            />
            <FilterInput
              label="Max Acres"
              type="number"
              value={filters.max_area}
              onChange={(value) => updateFilter('max_area', value)}
            />
            <FilterSelect
              label="Zoning Type"
              value={filters.zoning_type}
              onChange={(value) => updateFilter('zoning_type', value)}
              options={['Residential', 'Commercial', 'Agricultural']}
            />
            <FilterSelect
              label="Listing Type"
              value={filters.listing_type}
              onChange={(value) => updateFilter('listing_type', value)}
              options={['sale', 'lease']}
            />
            <FilterSelect
              label="Status"
              value={filters.status}
              onChange={(value) => updateFilter('status', value)}
              options={['available', 'pending', 'sold']}
            />
            <BooleanSelect
              label="Road Access"
              value={filters.road_access}
              onChange={(value) => updateFilter('road_access', value)}
            />
            <BooleanSelect
              label="Water Access"
              value={filters.water_access}
              onChange={(value) => updateFilter('water_access', value)}
            />
            <BooleanSelect
              label="Electricity"
              value={filters.electricity}
              onChange={(value) => updateFilter('electricity', value)}
            />
            <BooleanSelect
              label="Sewer"
              value={filters.sewer}
              onChange={(value) => updateFilter('sewer', value)}
            />
            <button
              onClick={clearFilters}
              className="flex h-[42px] items-center justify-center gap-2 self-end rounded-xl border border-[#E7D3CC] bg-[#FAF5F2] px-3 text-sm font-medium text-slate-600 transition hover:bg-[#F3E6E1]"
            >
              <RotateCcw size={15} />
              Clear Filters
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

type FieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
};

function FilterInput({
  label,
  value,
  onChange,
  type = 'text',
}: FieldProps & { type?: 'text' | 'number' }) {
  return (
    <label className="text-xs font-semibold text-slate-500">
      {label}
      <input
        type={type}
        value={value}
        min={type === 'number' ? 0 : undefined}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 h-[42px] w-full rounded-xl border border-[#E7D3CC] bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-[#C7745A]"
      />
    </label>
  );
}

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: FieldProps & { options: string[] }) {
  return (
    <label className="text-xs font-semibold text-slate-500">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 h-[42px] w-full rounded-xl border border-[#E7D3CC] bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-[#C7745A]"
      >
        <option value="">Any</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function BooleanSelect({ label, value, onChange }: FieldProps) {
  return (
    <FilterSelect
      label={label}
      value={value}
      onChange={onChange}
      options={['Yes', 'No']}
    />
  );
}
