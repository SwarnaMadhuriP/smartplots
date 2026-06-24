'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import AdvisorShell from '@/components/advisor/AdvisorShell';
import { GoalKey } from '@/components/advisor/GoalSelector';
import { Sparkles } from 'lucide-react';

const VALID_GOALS: GoalKey[] = [
  'build_home',
  'invest_appreciation',
  'retirement_lifestyle',
  'commercial',
  'maximize_value',
];

function AdvisorPage() {
  const searchParams = useSearchParams();
  const goalParam = searchParams.get('goal') as GoalKey | null;
  const initialGoal =
    goalParam && VALID_GOALS.includes(goalParam) ? goalParam : undefined;

  return (
    <main className="flex h-screen overflow-hidden bg-[#F3ECE5] text-slate-900">
      <Sidebar />

      <section className="flex-1 flex flex-col overflow-hidden">
        {/* Page header — mirrors comparisons/RightPanel style */}
        <div className="shrink-0 px-10 py-7 bg-[#F8F3ED] border-b border-[#E7D3CC]">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[#F3E6E1]">
              <Sparkles size={18} className="text-[#C7745A]" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI Advisor</h1>
              <p className="text-sm text-slate-500">Goal-based land recommendations, tailored to you.</p>
            </div>
          </div>
        </div>

        {/* Shell — breadcrumb + content */}
        <AdvisorShell initialGoal={initialGoal} />
      </section>
    </main>
  );
}

export default function AdvisorPageWrapper() {
  return (
    <Suspense fallback={null}>
      <AdvisorPage />
    </Suspense>
  );
}
