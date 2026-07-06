'use client';

import { Home, Map, Sparkles, Heart, Scale, Bookmark } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import SidebarInfoCard from './SidebarInfoCard';

const navItems = [
  { label: 'Discover Plots', icon: Home, href: '/' },
  { label: 'Map Explorer', icon: Map, href: '/map' },
  { label: 'AI Advisor', icon: Sparkles, href: '/insights' },
  { label: 'Watchlist', icon: Heart, href: '/watchlist' },
  { label: 'Comparisons', icon: Scale, href: '/comparisons' },
  { label: 'Saved Searches', icon: Bookmark, href: '/savedSearches' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="h-screen w-64 shrink-0 overflow-y-auto border-r border-[#E7D3CC] bg-[#F8F3ED] p-6">
      <div className="mb-8">
        <h1 className="tracking-tight text-2xl font-bold text-slate-900">
          SmartPlots
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          AI-Powered Land Investment Advisor
        </p>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === '/'
              ? pathname === '/'
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex w-full items-center gap-4 rounded-2xl px-5 py-3.5 text-left text-sm font-medium transition ${isActive
                ? 'bg-[#C7745A] text-white shadow-lg shadow-[#E7D3CC]'
                : 'text-slate-700 hover:bg-[#F3E6E1]'
                }`}
            >
              <Icon size={20} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <SidebarInfoCard />
    </aside>
  );
}
