'use client';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Loader2, Sparkles, User } from 'lucide-react';

type Message = {
  role: 'user' | 'ai';
  content: string;
  followUps?: string[];
};

type Props = {
  plotId?: number;
  initialQuestion?: string;
  onFirstMessage?: () => void;
};

export default function AdvisorChat({ plotId, initialQuestion, onFirstMessage }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const hasFiredInitial = useRef(false);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Fire initial question from URL param on mount
  useEffect(() => {
    if (initialQuestion && !hasFiredInitial.current) {
      hasFiredInitial.current = true;
      sendMessage(initialQuestion);
    }
  }, [initialQuestion]);

  async function sendMessage(question: string) {
    if (!question.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: question };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError('');
    onFirstMessage?.();

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKENDAPI_BASE_URL}/advisor/ask`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question,
            plot_id: plotId ?? null,
          }),
        },
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
      const raw = data.detail || 'Advisor request failed.';
      // Surface a clean message for quota/rate limit errors
      const isQuota = raw.includes('quota') || raw.includes('RESOURCE_EXHAUSTED') || raw.includes('429');
      throw new Error(
        isQuota
          ? '⏳ Daily AI quota reached. Please try again tomorrow or use a paid API key.'
          : raw,
      );
      }

      const data = await res.json();

      const aiMessage: Message = {
        role: 'ai',
        content: data.answer,
        followUps: data.suggested_follow_ups ?? [],
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Something went wrong.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Message thread */}
      <div className="flex-1 overflow-y-auto space-y-5 pb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 animate-fadeIn ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'ai' && (
              <div className="shrink-0 mt-1 flex h-7 w-7 items-center justify-center rounded-full bg-[#F3E6E1]">
                <Sparkles size={14} className="text-[#C7745A]" />
              </div>
            )}

            <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-first' : ''}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-[#C7745A] text-white rounded-br-sm'
                    : 'bg-white border border-[#E7D3CC] text-slate-700 rounded-bl-sm shadow-sm'
                }`}
              >
                {msg.role === 'ai' ? (
                  <div className="prose prose-sm prose-slate max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0.5 prose-strong:text-slate-800">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>

              {/* Follow-up chips */}
              {msg.role === 'ai' && msg.followUps && msg.followUps.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {msg.followUps.map((fu) => (
                    <button
                      key={fu}
                      onClick={() => sendMessage(fu)}
                      className="rounded-full border border-[#E7D3CC] bg-white px-3 py-1.5 text-xs text-slate-600 shadow-sm transition hover:border-[#C7745A] hover:text-[#C7745A]"
                    >
                      {fu}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="shrink-0 mt-1 flex h-7 w-7 items-center justify-center rounded-full bg-slate-200">
                <User size={14} className="text-slate-600" />
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-3 justify-start animate-fadeIn">
            <div className="shrink-0 mt-1 flex h-7 w-7 items-center justify-center rounded-full bg-[#F3E6E1]">
              <Sparkles size={14} className="text-[#C7745A]" />
            </div>
            <div className="rounded-2xl rounded-bl-sm border border-[#E7D3CC] bg-white px-4 py-3 shadow-sm">
              <Loader2 size={16} className="animate-spin text-[#C7745A]" />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        className="mt-4 flex items-center gap-3 rounded-2xl border border-[#E7D3CC] bg-white px-4 py-3 shadow-sm"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            plotId
              ? 'Ask anything about this plot…'
              : 'Ask anything about the catalog…'
          }
          className="flex-1 bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#C7745A] text-white transition hover:bg-[#B8644C] disabled:opacity-40"
        >
          <Send size={15} />
        </button>
      </form>
    </div>
  );
}
