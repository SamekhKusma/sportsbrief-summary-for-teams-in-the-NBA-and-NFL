import { useEffect, useMemo, useState } from 'react';
import { AlertCircle, ExternalLink, RefreshCcw, Sparkles } from 'lucide-react';
import { getLeagues, getNews, getSourceStatus, getTeams, summarize } from './api';

const TIME_RANGES = [
  { label: 'Last 24 hours', value: '24h' },
  { label: 'Last 3 days', value: '3d' },
  { label: 'Last 7 days', value: '7d' }
];

const sentimentStyles = {
  Positive: 'bg-green-100 text-green-700 border-green-200',
  Negative: 'bg-red-100 text-red-700 border-red-200',
  Neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  Mixed: 'bg-amber-100 text-amber-700 border-amber-200'
};

function App() {
  const [leagues, setLeagues] = useState([]);
  const [league, setLeague] = useState('NBA');
  const [teams, setTeams] = useState([]);
  const [team, setTeam] = useState('');
  const [range, setRange] = useState('7d');
  const [articles, setArticles] = useState([]);
  const [brief, setBrief] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sourceStatus, setSourceStatus] = useState(null);

  useEffect(() => {
    getSourceStatus()
      .then((data) => setSourceStatus(data))
      .catch(() => setSourceStatus(null));

    getLeagues()
      .then((data) => setLeagues(data))
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    setError('');
    setBrief(null);
    setArticles([]);
    getTeams(league)
      .then((data) => {
        setTeams(data);
        setTeam(data[0]?.name || '');
      })
      .catch((err) => setError(err.message));
  }, [league]);

  const selectedTeam = useMemo(() => {
    return teams.find((item) => item.name === team);
  }, [teams, team]);

  async function generateBrief() {
    if (!league || !team) {
      setError('Select a league and team first.');
      return;
    }

    setLoading(true);
    setError('');
    setBrief(null);

    try {
      const news = await getNews({ league, team, range });
      setArticles(news);
      const summary = await summarize({ league, team, articles: news });
      setBrief(summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-slate-900 p-3 text-white shadow-sm">
              <Sparkles size={22} />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-950">SportsBrief AI</h1>
              <p className="text-sm text-slate-600">NBA and NFL team news summarized with source links.</p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-5 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr_320px] lg:px-8">
        <aside className="h-fit rounded-2xl border bg-white p-4 shadow-sm">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">Filters</h2>

          <label className="mb-2 block text-sm font-medium text-slate-700">League</label>
          <select
            className="mb-4 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-slate-900"
            value={league}
            onChange={(event) => setLeague(event.target.value)}
          >
            {leagues.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>

          <label className="mb-2 block text-sm font-medium text-slate-700">Team</label>
          <select
            className="mb-4 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-slate-900"
            value={team}
            onChange={(event) => setTeam(event.target.value)}
          >
            {teams.map((item) => (
              <option key={item.name} value={item.name}>{item.name}</option>
            ))}
          </select>

          <label className="mb-2 block text-sm font-medium text-slate-700">Time range</label>
          <select
            className="mb-5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-slate-900"
            value={range}
            onChange={(event) => setRange(event.target.value)}
          >
            {TIME_RANGES.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>

          {selectedTeam && (
            <div className="mb-5 rounded-xl bg-slate-50 p-3 text-sm text-slate-600">
              <div className="font-semibold text-slate-900">{selectedTeam.name}</div>
              <div>{selectedTeam.conference} · {selectedTeam.division}</div>
            </div>
          )}

          <button
            onClick={generateBrief}
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? <RefreshCcw className="animate-spin" size={17} /> : <Sparkles size={17} />}
            {loading ? 'Generating...' : 'Generate Brief'}
          </button>
        </aside>

        <section className="space-y-5">
          {error && (
            <div className="flex gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <AlertCircle className="mt-0.5" size={18} />
              <span>{error}</span>
            </div>
          )}

          {sourceStatus && (
            <div className={`rounded-2xl border p-4 text-sm shadow-sm ${sourceStatus.live_news_enabled ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-800'}`}>
              <div className="font-semibold">Data source: {sourceStatus.article_source}</div>
              <div className="mt-1">{sourceStatus.note}</div>
            </div>
          )}

          {!brief && !loading && !error && (
            <div className="rounded-2xl border bg-white p-8 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-700">
                <Sparkles size={22} />
              </div>
              <h2 className="text-xl font-bold text-slate-950">Generate a team brief</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">
                Pick a league, team, and time range. The MVP will fetch matching live or cached articles and return grouped summaries.
              </p>
            </div>
          )}

          {loading && (
            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="mb-4 h-5 w-40 animate-pulse rounded bg-slate-200" />
              <div className="space-y-3">
                <div className="h-4 animate-pulse rounded bg-slate-100" />
                <div className="h-4 w-5/6 animate-pulse rounded bg-slate-100" />
                <div className="h-4 w-2/3 animate-pulse rounded bg-slate-100" />
              </div>
            </div>
          )}

          {brief && (
            <>
              <div className="rounded-2xl border bg-white p-5 shadow-sm">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold text-white">{brief.league}</span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{brief.team}</span>
                </div>
                <h2 className="mb-2 text-xl font-bold text-slate-950">Team Summary</h2>
                <p className="text-sm leading-6 text-slate-700">{brief.summary}</p>
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                {brief.topics.map((topic, index) => (
                  <TopicCard key={`${topic.category}-${index}`} topic={topic} />
                ))}
              </div>

              {brief.topics.length === 0 && (
                <div className="rounded-2xl border bg-white p-5 text-sm text-slate-600 shadow-sm">
                  No topic cards were generated for this selection.
                </div>
              )}
            </>
          )}
        </section>

        <aside className="h-fit rounded-2xl border bg-white p-4 shadow-sm">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Sources</h2>
            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">{articles.length}</span>
          </div>

          <div className="space-y-3">
            {articles.length === 0 && (
              <p className="text-sm text-slate-500">Sources appear here after generating a brief.</p>
            )}

            {articles.map((article) => (
              <a
                key={article.source_url}
                href={article.source_url}
                target="_blank"
                rel="noreferrer"
                className="block rounded-xl border border-slate-200 p-3 transition hover:border-slate-400 hover:bg-slate-50"
              >
                <div className="mb-1 flex items-start justify-between gap-2">
                  <h3 className="text-sm font-semibold leading-5 text-slate-900">{article.title}</h3>
                  <ExternalLink className="shrink-0 text-slate-400" size={15} />
                </div>
                <p className="mb-2 line-clamp-2 text-xs leading-5 text-slate-600">{article.description}</p>
                <div className="text-xs text-slate-500">
                  {article.source_name} · {formatDate(article.published_at)}
                </div>
              </a>
            ))}
          </div>
        </aside>
      </main>
    </div>
  );
}

function TopicCard({ topic }) {
  return (
    <article className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{topic.category}</span>
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${sentimentStyles[topic.sentiment] || sentimentStyles.Neutral}`}>
          {topic.sentiment}
        </span>
        <span className="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600">
          Importance {topic.importance}/5
        </span>
      </div>
      <h3 className="mb-2 text-base font-bold leading-6 text-slate-950">{topic.headline}</h3>
      <p className="mb-4 text-sm leading-6 text-slate-700">{topic.summary}</p>
      <div className="space-y-2">
        {topic.sources.map((source) => (
          <a
            key={`${source.url}-${source.title}`}
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-600 hover:bg-slate-100"
          >
            <span className="line-clamp-1">{source.source_name}: {source.title}</span>
            <ExternalLink size={14} className="shrink-0" />
          </a>
        ))}
      </div>
    </article>
  );
}

function formatDate(value) {
  if (!value) return 'Unknown date';
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date(value));
}

export default App;
