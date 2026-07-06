'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  ArrowRight,
  BarChart3,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Code2,
  FileSearch,
  Layers3,
  LineChart,
  MessageSquareText,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
} from 'lucide-react';


const capabilities = [
  {
    title: 'AI Search',
    description: 'Search naturally instead of using dozens of filters.',
    icon: Search,
  },
  {
    title: 'Personalized Recommendations',
    description: 'Every recommendation is tailored to your goals.',
    icon: Target,
  },
  {
    title: 'Document Intelligence',
    description:
      'Ask questions about brochures, zoning documents, HOA documents, and parcel reports.',
    icon: FileSearch,
  },
  {
    title: 'Investment Insights',
    description:
      'Understand appreciation, readiness, resale potential, and investment risks.',
    icon: LineChart,
  },
];

const workflow = [
  { title: 'Natural Language Query', icon: MessageSquareText },
  { title: 'Intent Understanding', icon: Code2 },
  { title: 'PostgreSQL + pgvector Retrieval', icon: Layers3 },
  { title: 'Deterministic Scoring', icon: BarChart3 },
  { title: 'Document RAG Context', icon: FileSearch },
  { title: 'AI Advisor Explanation', icon: ClipboardCheck },
];

const reasons = [
  {
    title: 'Intent-Based Search',
    description:
      'Describe budget, location, zoning, utilities, and buyer goals in plain English.',
    icon: MessageSquareText,
  },
  {
    title: 'Ranked Property Matches',
    description:
      'Combines structured filters, PostgreSQL data, pgvector retrieval, and deterministic scoring.',
    icon: Layers3,
  },
  {
    title: 'Document-Grounded Advice',
    description:
      'Uses property documents and AI reasoning to explain risks, readiness, and investment fit.',
    icon: FileSearch,
  },
];

const technologies = [
  'Next.js',
  'React',
  'TypeScript',
  'Tailwind CSS',
  'FastAPI',
  'Python',
  'SQLAlchemy',
  'Google ADK',
  'LangGraph',
  'Gemini',
  'Google GenAI',
  'PostgreSQL',
  'pgvector',
  'RAG',
  'Docker',
];

const recommendationReasons = [
  'Tech corridor access',
  'Excellent road access',
  'Utilities available',
  'Build-ready residential land',
];

function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#C7745A]">
        {eyebrow}
      </p>
      <h2 className="mt-4 text-3xl font-black tracking-tight text-slate-950 md:text-5xl">
        {title}
      </h2>
      {description ? (
        <p className="mt-5 text-lg leading-8 text-slate-600">{description}</p>
      ) : null}
    </div>
  );
}

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#F6EFE8] text-slate-950">
      <section className="mx-auto max-w-7xl px-5 py-5 sm:px-8">
        <nav className="flex items-center justify-between rounded-full border border-[#E7D3CC] bg-white/80 px-5 py-3 shadow-sm backdrop-blur">
          <Link href="/landing" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#C7745A] text-white shadow-sm">
              <Sparkles size={18} />
            </span>
            <span>
              <span className="block text-xl font-black tracking-tight text-slate-950">
                SmartPlots
              </span>
              <span className="block text-xs font-semibold uppercase tracking-[0.16em] text-[#C7745A]">
                AI Land Advisor
              </span>
            </span>
          </Link>

          <div className="hidden items-center gap-7 text-sm font-semibold text-slate-600 md:flex">
            <a href="#capabilities" className="transition hover:text-[#C7745A]">
              Capabilities
            </a>
            <a href="#workflow" className="transition hover:text-[#C7745A]">
              Workflow
            </a>
            <a href="#technology" className="transition hover:text-[#C7745A]">
              Technology
            </a>
          </div>

          <Link
            href="/"
            className="inline-flex h-11 items-center gap-2 rounded-full bg-[#C7745A] px-5 text-sm font-bold text-white shadow-sm shadow-[#D9B7AA] transition hover:-translate-y-0.5 hover:bg-[#B8644C]"
          >
            Open App
            <ArrowRight size={16} />
          </Link>
        </nav>

        <section className="grid min-h-[calc(100vh-92px)] items-center gap-12 py-16 lg:grid-cols-[1fr_0.9fr] lg:py-20">
          <div>
            <h1 className="max-w-4xl text-5xl font-black leading-[1.02] tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
              Meet Your AI Land Investment Advisor.
            </h1>

            <p className="mt-7 max-w-2xl text-xl leading-9 text-slate-600">
              Discover, compare, and understand land opportunities using AI
              agents, natural language search, and intelligent land
              insights.
            </p>

            <div className="mt-9 flex flex-wrap gap-4">
              <Link
                href="/"
                className="inline-flex h-14 items-center gap-2 rounded-full bg-[#C7745A] px-7 text-base font-bold text-white shadow-lg shadow-[#D8B4A6]/50 transition hover:-translate-y-0.5 hover:bg-[#B8644C]"
              >
                Try AI Search
                <Search size={18} />
              </Link>

              <Link
                href="/insights"
                className="inline-flex h-14 items-center gap-2 rounded-full border border-[#E7D3CC] bg-white px-7 text-base font-bold text-slate-800 shadow-sm transition hover:-translate-y-0.5 hover:border-[#C7745A] hover:text-[#C7745A]"
              >
                Explore Demo
                <ArrowRight size={18} />
              </Link>
            </div>


          </div>

          <div className="relative">
            <div className="absolute -inset-5 rounded-[2.5rem] bg-white/45 blur-2xl" />
            <section className="relative overflow-hidden rounded-[2rem] border border-[#E7D3CC] bg-white shadow-2xl shadow-[#D8B4A6]/30">
              <div className="flex items-center gap-2 border-b border-[#EFE0D8] bg-[#FFFCFA] px-5 py-4">
                <span className="h-3 w-3 rounded-full bg-[#E8A18E]" />
                <span className="h-3 w-3 rounded-full bg-[#E9D2A9]" />
                <span className="h-3 w-3 rounded-full bg-[#9AC5A6]" />
                <div className="ml-3 flex h-9 flex-1 items-center rounded-full bg-[#F8F3ED] px-4 text-xs font-semibold text-slate-500">
                  smartplots.ai/discover
                </div>
              </div>

              <div className="min-h-[560px] bg-[#F8F3ED] p-5 sm:p-6">
                <div className="mx-auto max-w-2xl">
                  <div className="flex items-center gap-3 rounded-full bg-white px-4 py-3 shadow-lg shadow-[#E7D3CC]/50">
                    <Sparkles size={18} className="shrink-0 text-[#C7745A]" />
                    <span className="min-w-0 flex-1 truncate text-sm font-medium text-slate-400">
                      i want plots that have access to tech corridor
                    </span>
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#C7745A] text-white">
                      <Search size={18} />
                    </span>
                  </div>

                  <div className="mt-4 flex items-center justify-between gap-3">
                    <p className="text-sm font-black text-slate-950">
                      7 plots match your preferences
                    </p>
                  </div>

                  <article className="mt-5 overflow-hidden rounded-3xl border-2 border-[#C7745A] bg-white shadow-xl shadow-[#D8B4A6]/30">
                    <div className="relative h-56 overflow-hidden">
                      <Image
                        src="/plots/plot-1.png"
                        alt="San Jose Tech Corridor Residential Lot"
                        fill
                        priority
                        sizes="(max-width: 1024px) 100vw, 560px"
                        className="object-cover"
                      />
                    </div>
                    <div className="p-6">
                      <div className="flex items-start justify-between gap-5">
                        <div>
                          <span className="rounded-full bg-[#C7745A] px-3 py-1.5 text-xs font-bold text-white">
                            Best Match
                          </span>
                          <h2 className="mt-4 text-2xl font-black leading-tight text-slate-950">
                            San Jose Tech Corridor Residential Lot
                          </h2>
                          <p className="mt-2 text-sm font-semibold text-slate-500">
                            San Jose, CA
                          </p>
                          <p className="mt-3 text-xl font-black text-[#B8644C]">
                            $425,000
                          </p>
                        </div>

                        <div className="rounded-2xl border border-[#E7D3CC] bg-[#FFFCFA] px-4 py-3 text-center shadow-sm">
                          <p className="text-3xl font-black text-[#C7745A]">
                            10/10
                          </p>
                          <p className="text-[11px] font-bold text-slate-500">
                            Plot Readiness Score
                          </p>
                        </div>
                      </div>

                      <div className="mt-6 rounded-2xl bg-[#F3ECE5] p-5">
                        <p className="text-sm font-black text-slate-950">
                          Why SmartPlots Recommends This
                        </p>
                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          {recommendationReasons.map((reason) => (
                            <div
                              key={reason}
                              className="flex items-center gap-2 text-xs font-semibold text-slate-700"
                            >
                              <CheckCircle2
                                size={14}
                                className="shrink-0 text-[#C7745A]"
                              />
                              {reason}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </article>

                  <div className="mt-4 rounded-3xl border border-[#E7D3CC] bg-white p-5 shadow-sm">
                    <div className="flex items-start gap-3">
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#C7745A] text-white">
                        <Bot size={16} />
                      </span>
                      <div>
                        <p className="text-sm font-black text-slate-950">
                          AI Search Summary
                        </p>
                        <p className="mt-1 text-sm leading-6 text-slate-600">
                          SmartPlots found 7 matching plots and ranked this
                          property highest because it best matches the
                          buyer&apos;s location, readiness, and investment
                          criteria.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </section>
      </section>

      <section id="capabilities" className="border-y border-[#E7D3CC] bg-white">
        <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8">
          <SectionHeader
            eyebrow="What SmartPlots Can Do"
            title="AI workflows for the full land decision journey."
            description="SmartPlots moves beyond listings by helping users search, reason, compare, and understand the tradeoffs behind each parcel."
          />

          <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {capabilities.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="group rounded-3xl border border-[#E7D3CC] bg-[#FFFCFA] p-6 shadow-sm transition hover:-translate-y-1 hover:border-[#C7745A] hover:shadow-lg hover:shadow-[#E7D3CC]/60"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#FAF1EC] text-[#C7745A] transition group-hover:bg-[#C7745A] group-hover:text-white">
                  <Icon size={22} />
                </span>
                <h3 className="mt-6 text-xl font-black tracking-tight text-slate-950">
                  {title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="workflow" className="bg-[#F6EFE8]">
        <div className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <SectionHeader
            eyebrow="How It Works"
            title="From buyer intent to explainable land recommendations."
            description="SmartPlots turns natural language into structured filters, retrieves matching plots from PostgreSQL and pgvector, scores each property, adds document context, and explains the final recommendation."
          />

          <div className="mt-14 rounded-[2rem] border border-[#E7D3CC] bg-white p-5 shadow-xl shadow-[#E7D3CC]/30 md:p-8">
            <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
              {workflow.map(({ title, icon: Icon }, index) => (
                <div key={title} className="relative">
                  <div className="flex h-full min-h-40 flex-col justify-between rounded-3xl border border-[#E7D3CC] bg-[#FFFCFA] p-5 transition hover:-translate-y-1 hover:border-[#C7745A] hover:shadow-md">
                    <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#FAF1EC] text-[#C7745A]">
                      <Icon size={20} />
                    </span>
                    <div>
                      <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">
                        Step {index + 1}
                      </p>
                      <h3 className="mt-2 text-base font-black leading-6 text-slate-950">
                        {title}
                      </h3>
                    </div>
                  </div>

                  {index < workflow.length - 1 ? (
                    <ChevronRight
                      size={22}
                      className="absolute -right-3 top-1/2 z-10 hidden -translate-y-1/2 rounded-full bg-white text-[#C7745A] xl:block"
                    />
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white">
        <div className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <SectionHeader
            eyebrow="Why SmartPlots"
            title="Built for decisions, not endless browsing."
          />

          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {reasons.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="rounded-[2rem] border border-[#E7D3CC] bg-[#FFFCFA] p-8 shadow-sm transition hover:-translate-y-1 hover:shadow-lg hover:shadow-[#E7D3CC]/50"
              >
                <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#C7745A] text-white shadow-sm">
                  <Icon size={24} />
                </span>
                <h3 className="mt-8 text-2xl font-black tracking-tight text-slate-950">
                  {title}
                </h3>
                <p className="mt-4 text-base leading-7 text-slate-600">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="technology" className="bg-[#F6EFE8]">
        <div className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <div className="grid gap-10 lg:grid-cols-[0.8fr_1fr] lg:items-center">
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#C7745A]">
                Technology
              </p>
              <h2 className="mt-4 text-3xl font-black tracking-tight text-slate-950 md:text-5xl">
                Built with Modern AI Infrastructure
              </h2>
              <p className="mt-5 text-lg leading-8 text-slate-600">
                A full-stack architecture connects product UI, agent workflows,
                structured data, vector retrieval, and explainable AI outputs.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              {technologies.map((tech) => (
                <div
                  key={tech}
                  className="flex h-20 items-center justify-center rounded-3xl border border-[#E7D3CC] bg-white px-5 text-base font-black text-slate-800 shadow-sm transition hover:-translate-y-1 hover:border-[#C7745A] hover:text-[#C7745A]"
                >
                  {tech}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white">
        <div className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <SectionHeader
            eyebrow="Demo Preview"
            title="The product experience behind the advisor."
            description="A focused workspace for recommendations, investment context, documents, and match signals."
          />

          <div className="mt-14 overflow-hidden rounded-[2rem] border border-[#E7D3CC] bg-[#F8F3ED] shadow-2xl shadow-[#D8B4A6]/30">
            <div className="flex items-center gap-2 border-b border-[#E7D3CC] bg-white px-5 py-4">
              <span className="h-3 w-3 rounded-full bg-[#E8A18E]" />
              <span className="h-3 w-3 rounded-full bg-[#E9D2A9]" />
              <span className="h-3 w-3 rounded-full bg-[#9AC5A6]" />
              <div className="ml-4 flex h-9 flex-1 items-center rounded-full bg-[#F8F3ED] px-4 text-sm font-semibold text-slate-500">
                smartplots.ai/insights
              </div>
            </div>

            <div className="min-h-[620px] bg-[#F8F3ED]">
              <div className="border-b border-[#E7D3CC] bg-[#FFFCFA] px-7 py-6">
                <div className="flex items-center gap-4">
                  <span className="flex h-12 w-12 items-center justify-center rounded-full bg-[#FAF1EC] text-[#C7745A]">
                    <Sparkles size={20} />
                  </span>
                  <div>
                    <h3 className="text-2xl font-black tracking-tight text-slate-950">
                      AI Advisor
                    </h3>
                    <p className="mt-1 text-sm font-medium text-slate-500">
                      Goal-based land recommendations, tailored to you.
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-b border-[#E7D3CC] bg-[#FFFCFA] px-7 py-4">
                <div className="flex items-center gap-3 text-sm font-bold">
                  <span className="text-[#C7745A]">Choose Goal</span>
                  <span className="text-[#D8C7BE]">›</span>
                  <span className="text-[#D8C7BE]">Your Preferences</span>
                  <span className="text-[#D8C7BE]">›</span>
                  <span className="text-[#D8C7BE]">Recommendation</span>
                </div>
              </div>

              <div className="px-6 py-14">
                <div className="mx-auto max-w-4xl text-center">
                  <h3 className="text-2xl font-black tracking-tight text-slate-950">
                    What are you looking to achieve?
                  </h3>
                  <p className="mx-auto mt-4 max-w-xl text-sm font-medium leading-6 text-slate-500">
                    Your goal shapes every recommendation — choose the one that
                    best describes your intention.
                  </p>
                </div>

                <div className="mx-auto mt-12 grid max-w-4xl gap-5 md:grid-cols-3">
                  {[
                    {
                      label: 'Ready-to-Build Land',
                      title: 'Build a Home',
                      description:
                        'Utilities, road access, and residential zoning matched to your budget.',
                      icon: Target,
                      accent: '#C7745A',
                    },
                    {
                      label: 'High-Growth Potential',
                      title: 'Invest for Appreciation',
                      description:
                        'Plots with strong upside, matched to your risk appetite and time horizon.',
                      icon: LineChart,
                      accent: '#7CA383',
                    },
                    {
                      label: 'Peaceful & Low-Risk',
                      title: 'Retirement / Lifestyle',
                      description:
                        'Quiet, scenic land with everything you need for a comfortable life.',
                      icon: ShieldCheck,
                      accent: '#8D7AAE',
                    },
                  ].map(({ label, title, description, icon: Icon, accent }) => (
                    <article
                      key={title}
                      className="rounded-3xl border border-[#E7D3CC] bg-white p-6 text-left shadow-md shadow-[#D8B4A6]/20"
                      style={{ borderTopColor: accent, borderTopWidth: 3 }}
                    >
                      <span
                        className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#FAF5F2] shadow-sm"
                        style={{ color: accent }}
                      >
                        <Icon size={22} />
                      </span>
                      <p
                        className="mt-8 text-xs font-black uppercase tracking-[0.16em]"
                        style={{ color: accent }}
                      >
                        {label}
                      </p>
                      <h4 className="mt-3 text-xl font-black text-slate-950">
                        {title}
                      </h4>
                      <p className="mt-4 text-sm font-medium leading-6 text-slate-500">
                        {description}
                      </p>
                    </article>
                  ))}
                </div>

                <div className="mx-auto mt-5 grid max-w-3xl gap-5 md:grid-cols-2">
                  {[
                    {
                      label: 'Business-Ready Plots',
                      title: 'Commercial Development',
                      description:
                        'Commercial zoning, road access, and scale for your development plans.',
                      icon: BarChart3,
                      accent: '#5D8EC1',
                    },
                    {
                      label: 'Best Land Per Dollar',
                      title: 'Maximize Value',
                      description:
                        'The lowest price per acre in your preferred area, without compromising quality.',
                      icon: BrainCircuit,
                      accent: '#A6844E',
                    },
                  ].map(({ label, title, description, icon: Icon, accent }) => (
                    <article
                      key={title}
                      className="rounded-3xl border border-[#E7D3CC] bg-white p-6 text-left shadow-md shadow-[#D8B4A6]/20"
                      style={{ borderTopColor: accent, borderTopWidth: 3 }}
                    >
                      <span
                        className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#FAF5F2] shadow-sm"
                        style={{ color: accent }}
                      >
                        <Icon size={22} />
                      </span>
                      <p
                        className="mt-8 text-xs font-black uppercase tracking-[0.16em]"
                        style={{ color: accent }}
                      >
                        {label}
                      </p>
                      <h4 className="mt-3 text-xl font-black text-slate-950">
                        {title}
                      </h4>
                      <p className="mt-4 text-sm font-medium leading-6 text-slate-500">
                        {description}
                      </p>
                    </article>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#E7D3CC] bg-[#211B18] text-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-8 px-5 py-10 sm:px-8 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#C7745A]">
                <Layers3 size={18} />
              </span>
              <p className="text-xl font-black">SmartPlots</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 text-sm font-bold text-white/70">
            <a className="transition hover:text-white" href="#">
              GitHub
            </a>
            <a className="transition hover:text-white" href="#">
              Documentation
            </a>
            <a className="transition hover:text-white" href="#workflow">
              Architecture
            </a>
            <Link className="transition hover:text-white" href="/">
              Demo
            </Link>
            <a className="transition hover:text-white" href="#capabilities">
              About
            </a>
            <Code2 size={18} className="text-white/40" />
          </div>
        </div>
      </footer>
    </main>
  );
}
