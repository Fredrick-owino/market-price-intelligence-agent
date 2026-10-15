import { recordedQuantity, sourceDate, workflowTime } from './presentation'
import Icon from './icons'
import { useCallback, useEffect, useRef, useState } from 'react'

type Market = {
  market: string
  quote_id: string
  normalized_price_per_kg: string
  sellable_kg: string
  gross_proceeds: string
  costs: Record<string, string | null>
  total_cost: string | null
  estimated_net_proceeds: string | null
  source_reference: string
}
type Comparison = {
  synthetic: boolean
  as_of_date: string
  currency: string
  winner: string | null
  advantage_kes: string | null
  markets: Market[]
  assumptions: string[]
  limitations: string[]
  snapshot_sha256: string
  retrieval_provenance?: Record<string, unknown>
}
type Draft = {
  created_at?: string | null
  workflow_id: string
  draft_id: string
  version: number
  content_hash: string
  status: string
  content: {
    calculation: { quantity: string; unit: string }
    quote_references: { quote_id: string; source_reference: string }[]
    assumptions: string[]
    limitations: string[]
    retrieval_provenance?: Record<string, unknown>
  }
}
type Run = {
  started_at?: string | null
  completed_at?: string | null
  advisory_created_at?: string | null
  officer_decision_at?: string | null
  officer_decision?: string | null
  workflow_id: string
  status: 'RUNNING' | 'PENDING_REVIEW' | 'COMPLETED' | 'FAILED'
  error_code?: string | null
  phase?: string[]
  outcome?: string | null
  draft_id?: string
  version?: number
  content_hash?: string
  draft_status?: string
  pending_nodes?: string[]
  comparison?: Comparison | null
  retrieval_provenance?: Record<string, unknown> | null
}

type ToolEvent = { timestamp: string; tool: string; server: string; phase: string; input?: unknown; output?: unknown; elapsed_ms?: number }

const STORAGE_KEY = 'sokosignal-demo-workflow-id'
const fixed = {
  commodity: 'demo-maize', variant: 'dry-demo', grade: 'DEMO-1',
  origin: 'synthetic-region', sale_basis: 'wholesale',
  as_of_date: '2026-10-10', markets: 'Market A and Market B',
} as const

function formatError(status: number, value: unknown): string {
  const detail = value && typeof value === 'object' && 'detail' in value ? (value as { detail: unknown }).detail : value
  if (status === 401) return 'Credential missing or invalid. Enter the local officer token again.'
  if (status === 403) return 'This officer is not permitted to access this workflow.'
  if (status === 409 && typeof detail === 'string' && detail.startsWith('A model workflow')) return detail
  if (status === 409) return 'The draft or request changed. Refresh its current status before retrying.'
  if (status === 422) return 'Check the supported input and try again.'
  return typeof detail === 'string' ? detail : `Request failed (${status}).`
}

export default function App() {
  const [token, setToken] = useState('')
  const [authenticated, setAuthenticated] = useState(false)
  const [quantity, setQuantity] = useState('1000')
  const [workflowId, setWorkflowId] = useState(() => sessionStorage.getItem(STORAGE_KEY) || '')
  const [run, setRun] = useState<Run | null>(null)
  const [draft, setDraft] = useState<Draft | null>(null)
  const [pending, setPending] = useState<Draft[]>([])
  const [events, setEvents] = useState<ToolEvent[]>([])
  const [reviewer, setReviewer] = useState<{ id: string; demo: boolean } | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [note, setNote] = useState('')
  const [demoAccess, setDemoAccess] = useState<{ token: string } | null>(null)
  const [showDemoHelp, setShowDemoHelp] = useState(false)
  const refreshRevision = useRef(0)
  const startKey = useRef(crypto.randomUUID())
  const decisionKeys = useRef<Record<string, string>>({})

  useEffect(() => {
    let cancelled = false
    void fetch('/api/v1/demo-access', { cache: 'no-store' })
      .then(response => response.ok ? response.json() : null)
      .then(value => {
        if (!cancelled && value?.enabled === true && typeof value.token === 'string') {
          setDemoAccess({ token: value.token })
        }
      }).catch(() => {})
    return () => { cancelled = true }
  }, [])

  const api = useCallback(async <T,>(path: string, init?: RequestInit): Promise<T> => {
    const response = await fetch(path, {
      ...init,
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', ...init?.headers },
      cache: 'no-store',
    })
    const value: unknown = await response.json().catch(() => null)
    if (!response.ok) throw new Error(formatError(response.status, value))
    return value as T
  }, [token])

  const refreshPending = useCallback(async () => {
    const result = await api<{ drafts: Draft[]; reviewer: { id: string; demo: boolean } }>('/api/v1/drafts/pending')
    setPending(result.drafts)
    setReviewer(result.reviewer)
  }, [api])

  const refresh = useCallback(async (id: string) => {
    const revision = ++refreshRevision.current
    const result = await api<Run>(`/api/v1/runs/${encodeURIComponent(id)}`)
    const [activity, current] = await Promise.all([
      api<{ events: ToolEvent[] }>(`/api/v1/runs/${encodeURIComponent(id)}/events`),
      result.draft_id ? api<Draft>(`/api/v1/runs/${encodeURIComponent(id)}/draft`) : Promise.resolve(null),
    ])
    // Ignore responses from a previously selected run.
    if (revision === refreshRevision.current) {
      setRun(result)
      setEvents(activity.events)
      setDraft(current)
    }
    return result
  }, [api])

  useEffect(() => {
    if (!authenticated || !workflowId) return
    let cancelled = false
    const poll = async () => {
      try {
        const next = await refresh(workflowId)
        if (!cancelled && next.status !== 'RUNNING') await refreshPending()
      } catch (caught) {
        if (!cancelled) setError((caught as Error).message)
      }
    }
    void poll()
    const timer = window.setInterval(() => { void poll() }, 3000)
    return () => { cancelled = true; window.clearInterval(timer) }
  }, [authenticated, workflowId, refresh, refreshPending])

  async function signIn(event: React.FormEvent) {
    event.preventDefault()
    setBusy(true); setError('')
    try {
      await refreshPending()
      setAuthenticated(true)
    } catch (caught) { setError((caught as Error).message) }
    finally { setBusy(false) }
  }

  async function start(event: React.FormEvent) {
    event.preventDefault()
    const amount = Number(quantity)
    if (!Number.isInteger(amount) || amount < 1 || amount > 1000) {
      setError('Enter a whole kilogram quantity from 1 to 1000.')
      return
    }
    setBusy(true); setError('')
    try {
      const result = await api<{ workflow_id: string }>('/api/v1/requests', {
        method: 'POST', body: JSON.stringify({ ...fixed, quantity_kg: amount, idempotency_key: startKey.current }),
      })
      setWorkflowId(result.workflow_id)
      sessionStorage.setItem(STORAGE_KEY, result.workflow_id)
      await refresh(result.workflow_id)
    } catch (caught) { setError((caught as Error).message) }
    finally { setBusy(false) }
  }

  async function decide(choice: 'approve' | 'reject') {
    if (!draft) return
    const identity = `${draft.workflow_id}:${draft.version}:${choice}`
    const key = decisionKeys.current[identity] ||= crypto.randomUUID()
    setBusy(true); setError('')
    try {
      await api(`/api/v1/runs/${encodeURIComponent(draft.workflow_id)}/decisions`, {
        method: 'POST', body: JSON.stringify({
          draft_id: draft.draft_id, version: draft.version, content_hash: draft.content_hash,
          decision: choice, idempotency_key: key, note,
        }),
      })
      await refresh(draft.workflow_id)
      await refreshPending()
    } catch (caught) { setError((caught as Error).message); await refresh(draft.workflow_id).catch(() => {}) }
    finally { setBusy(false) }
  }

  function selectDraft(item: Draft) {
    refreshRevision.current++
    setWorkflowId(item.workflow_id)
    sessionStorage.setItem(STORAGE_KEY, item.workflow_id)
    setRun(null); setDraft(null); setEvents([]); setNote(''); setError('')
  }

  function newAttempt() {
    refreshRevision.current++
    startKey.current = crypto.randomUUID()
    setWorkflowId(''); setRun(null); setDraft(null); setEvents([]); setNote(''); setError('')
    sessionStorage.removeItem(STORAGE_KEY)
  }

  async function retry() {
    setError('')
    try {
      if (workflowId) {
        const next = await refresh(workflowId)
        if (next.status !== 'RUNNING') await refreshPending()
      } else if (authenticated) {
        await refreshPending()
      }
    } catch (caught) { setError((caught as Error).message) }
  }

  const loading = busy || run?.status === 'RUNNING'

  return <main className="shell">
    <header className="appbar">
      <div className="appbar-brand">
        <span className="mark" aria-hidden="true">S</span>
        <span className="appbar-id">
          <strong>SokoSignal</strong>
          <small>Market intelligence</small>
        </span>
      </div>
      {authenticated && reviewer && (
        <div className="user-area">
          <Icon name="user" size={16} />
          <span className="user-id" title={reviewer.id}>{reviewer.id}</span>
        </div>
      )}
    </header>

    <section className="hero"><p className="eyebrow">OFFICER WORKSPACE / MARKET REVIEW</p><h1>A clearer view of the market.<br /><em>Officer judgement.</em></h1><p className="page-intro">Compare market options, assess costs, and review the evidence before approving an advisory.</p></section>

    <p className="notice" role="note">
        <Icon name="info" size={16} />
        <span><strong>SAMPLE DATA</strong> · Illustrative prices and costs · market-data date {sourceDate(fixed.as_of_date)} · for internal review</span>
    </p>

    {error && (
      <div className="alert" role="alert">
        <Icon name="alert" size={18} />
        <div className="alert-body">
          <p>{error}</p>
          {authenticated && <button type="button" className="btn btn-text" disabled={busy} onClick={() => void retry()}>
            <Icon name="refresh" size={16} /> Refresh status
          </button>}
        </div>
      </div>
    )}

    {!authenticated ? (
      <section className="panel signin">
        <div className="signin-copy">
          <h2>Officer sign in</h2>
          <p>Enter your local bearer token. It stays in this page’s memory and is cleared on refresh.</p>
        </div>
        <form className="signin-form" onSubmit={signIn}>
          <label className="field">
            <span className="field-label">Officer token</span>
            <input type="password" autoComplete="off" value={token} onFocus={() => setShowDemoHelp(true)} aria-describedby={demoAccess && showDemoHelp ? 'demo-access-help' : undefined} onChange={event => setToken(event.target.value)} required />
          </label>
          {demoAccess && <div className="demo-access">
            <button type="button" className="btn btn-text" aria-expanded={showDemoHelp} aria-controls="demo-access-help" onClick={() => setShowDemoHelp(value => !value)}>Try the demo</button>
            {showDemoHelp && <div id="demo-access-help">
              <p><strong>Demo token: <code>{demoAccess.token}</code></strong></p>
              <p>Click Use demo token, then Open review desk. Enter a quantity from 1 to 1,000 kg to compare the sample markets.</p>
              <p className="section-sub">Shared sample workspace. Anyone with this code can review its demo drafts. Demo decisions are not verified officer approvals.</p>
              <button type="button" className="btn btn-outlined" onClick={() => setToken(demoAccess.token)}>Use demo token</button>
            </div>}
          </div>}
          <button type="submit" className="btn btn-filled" disabled={busy}>Open review desk</button>
        </form>
      </section>
    ) : (
      <div className="workspace">
        <div className="col col-input">
          <section className="panel">
            <h2 className="section-title">Comparison request</h2>
            <p className="section-sub">This demo supports one crop, grade, date and two invented markets. Quantity is the only variable.</p>
            <form className="request-form" onSubmit={start}>
              <label className="field">
                <span className="field-label">Farmer quantity <span className="field-hint">whole kilograms, max 1,000</span></span>
                <input type="number" min="1" max="1000" step="1" required value={quantity} onChange={event => { setQuantity(event.target.value); startKey.current = crypto.randomUUID() }} />
              </label>
              <dl className="facts">
                <div><dt>Crop / grade</dt><dd>Demo maize · DEMO-1</dd></div>
                <div><dt>Origin</dt><dd>Synthetic region</dd></div>
                <div><dt>Markets</dt><dd>Market A + Market B</dd></div>
                <div><dt>Data date</dt><dd>{sourceDate(fixed.as_of_date)}</dd></div>
              </dl>
              <div className="form-actions">
                <button type="submit" className="btn btn-filled" disabled={busy || run?.status === 'RUNNING'}>
                  <Icon name="zap" size={16} /> Start comparison
                </button>
                {run && <button type="button" className="btn btn-text" disabled={busy} onClick={newAttempt}>New attempt</button>}
              </div>
            </form>
          </section>

          <section className="panel pending-panel">
            <h2 className="section-title">Pending drafts</h2>
            {pending.length ? (
              <div className="inbox">
                {pending.map(item => (
                  <button className="inbox-item" key={item.draft_id} aria-current={workflowId === item.workflow_id ? true : undefined} disabled={busy} onClick={() => selectDraft(item)}>
                    <span className="inbox-main">
                      <strong>{item.workflow_id}</strong>
                      <small>Version {item.version} · {item.content.calculation.quantity} {item.content.calculation.unit} · created {workflowTime(item.created_at)}</small>
                    </span>
                    <Icon name="chevron-right" size={16} />
                  </button>
                ))}
              </div>
            ) : (
              <p className="empty">No pending drafts in your permitted workflows.</p>
            )}
          </section>
        </div>

        <div className="col col-output">
          <section className="panel">
            <div className="section-head">
              <h2 className="section-title">Run status</h2>
              {run && <span role="status" className={`chip chip-${run.status.toLowerCase()}`}>{run.status.replaceAll('_', ' ')}</span>}
            </div>
            {run ? (
              <>
                <p className="run-id">{run.workflow_id}</p>
                <dl className="timeline">
                  <div><dt>Workflow started</dt><dd>{workflowTime(run.started_at)}</dd></div>
                  <div><dt>Workflow completed</dt><dd>{workflowTime(run.completed_at)}</dd></div>
                  <div><dt>Advisory created</dt><dd>{workflowTime(run.advisory_created_at)}</dd></div>
                  <div><dt>Officer decision{run.officer_decision ? ` · ${run.officer_decision}` : ' · none recorded'}</dt><dd>{workflowTime(run.officer_decision_at)}</dd></div>
                </dl>
                {run.status === 'PENDING_REVIEW' && <p className="note-line">Waiting for officer review. The workflow has not completed.</p>}
                {run.status === 'RUNNING' && <p className="note-line">Retrieval, model tool calls and draft creation can take several minutes. This page checks the persisted run every 3 seconds. The workflow is still running.</p>}
                {run.status === 'FAILED' && <p className="note-line note-error">The run stopped: <strong>{run.error_code || 'unknown failure'}</strong>. No reviewable draft was created. Check the local services and start a new attempt.</p>}
                {run.outcome && <p className="note-line"><strong>Outcome:</strong> {run.outcome === 'approved_internal_review' ? 'Approved for internal review only; nothing was delivered.' : run.outcome === 'rejected' ? 'Rejected; nothing was delivered.' : run.outcome}</p>}
              </>
            ) : workflowId ? (
              <div className="skeleton-blocks" role="status" aria-label="Loading workflow">
                <div className="skeleton skeleton-line" />
                <div className="skeleton skeleton-line short" />
                <div className="skeleton skeleton-card" />
              </div>
            ) : (
              <p className="empty">No run selected. Start a comparison or open a pending draft.</p>
            )}
          </section>

          {run?.comparison ? (
            <section className="panel">
              <h2 className="section-title">Market options</h2>
              <p className="comparison-summary">
                {run.comparison.currency} · sample-data date {sourceDate(run.comparison.as_of_date)} · recorded {recordedQuantity(draft)}
                {run.comparison.winner ? ` · ${run.comparison.winner} leads by ${run.comparison.advantage_kes} KES` : ' · No defensible net winner'}
              </p>
              <div className="markets">
                {run.comparison.markets.map(market => (
                  <article className={`market ${run.comparison?.winner === market.market ? 'leading' : ''}`} key={market.quote_id}>
                    <div className="market-head">
                      <h3>{market.market}</h3>
                      {run.comparison?.winner === market.market && <span className="chip chip-success">Highest estimated net</span>}
                    </div>
                    <div className="market-price">
                      <span className="market-price-value">{market.estimated_net_proceeds ?? 'Unknown'}</span>
                      <small>KES net</small>
                    </div>
                    <dl className="market-rows">
                      <div><dt>Sellable quantity</dt><dd>{market.sellable_kg} kg</dd></div>
                      <div><dt>Price / kg (KES)</dt><dd>{market.normalized_price_per_kg}</dd></div>
                      <div><dt>Gross proceeds</dt><dd>{market.gross_proceeds}</dd></div>
                      <div><dt>Transport</dt><dd>{market.costs.transport_total ?? 'Unknown'}</dd></div>
                      <div><dt>Handling</dt><dd>{market.costs.handling_total ?? 'Unknown'}</dd></div>
                      <div><dt>Market fees</dt><dd>{market.costs.market_fees_total ?? 'Unknown'}</dd></div>
                      <div className="market-total"><dt>Total costs (KES)</dt><dd>{market.total_cost ?? 'Unknown'}</dd></div>
                    </dl>
                    <p className="market-source">Quote {market.quote_id} · {market.source_reference}</p>
                  </article>
                ))}
              </div>
            </section>
          ) : workflowId && loading ? (
            <section className="panel">
              <h2 className="section-title">Market options</h2>
              <div className="skeleton-blocks" role="status" aria-label="Loading workflow">
                <div className="skeleton skeleton-line" />
                <div className="skeleton skeleton-line short" />
                <div className="skeleton skeleton-card" />
              </div>
            </section>
          ) : null}

          {draft && (
            <section className="panel">
              <div className="section-head">
                <h2 className="section-title">Draft version {draft.version}</h2>
                <span className={`chip chip-${draft.status.toLowerCase()}`}>{draft.status.replaceAll('_', ' ')}</span>
              </div>
              <p className="draft-meta">ID {draft.draft_id}<br />SHA-256 {draft.content_hash}</p>
              <p>Advisory created: {workflowTime(draft.created_at)}</p>
              <div className="evidence">
                <div>
                  <h3>Source &amp; provenance</h3>
                  <p>Synthetic fixture snapshot: {run?.comparison?.snapshot_sha256 || 'See stored draft'}</p>
                  <pre>{JSON.stringify(draft.content.retrieval_provenance || run?.retrieval_provenance || {}, null, 2)}</pre>
                </div>
                <div>
                  <h3>Assumptions &amp; limits</h3>
                  <ul>{[...draft.content.assumptions, ...draft.content.limitations].map((item, index) => <li key={index}>{item}</li>)}</ul>
                </div>
              </div>
              {draft.status === 'PENDING_REVIEW' && (
                <div className="decision">
                  <p className="decision-reviewer"><strong>{reviewer?.demo ? 'Demo reviewer identity' : 'Reviewer'}:</strong> {reviewer?.id} · internal review only</p>
                  <label className="field">
                    <span className="field-label">Decision note <span className="field-hint">optional · max 500 characters</span></span>
                    <textarea maxLength={500} value={note} onChange={event => setNote(event.target.value)} />
                  </label>
                  <div className="form-actions">
                    <button className="btn btn-filled" disabled={busy} onClick={() => void decide('approve')}>Approve internal review</button>
                    <button className="btn btn-danger" disabled={busy} onClick={() => void decide('reject')}>Reject draft</button>
                  </div>
                </div>
              )}
            </section>
          )}
          {workflowId && (
            <section className="panel">
              <div className="section-head">
                <h2 className="section-title">Live tool activity</h2>
                <span className="chip chip-neutral">Sanitized</span>
              </div>
              <p className="section-sub" role="status">
                {run?.status === 'RUNNING'
                  ? `In progress · ${events.at(-1)?.tool || 'waiting for retrieval'} · ${events.at(-1)?.phase || 'queued'}`
                  : `${events.filter(event => event.phase === 'completed').length} completed steps · ${run?.status.replaceAll('_', ' ') || 'loading'}`}
              </p>
              {events.length ? (
                <details className="execution-trace" open={run?.status === 'RUNNING'}>
                  <summary>Execution trace · {events.length} recorded events</summary>
                  <div className="tool-events">
                  {events.map((event, index) => (
                    <article className="tool-event" key={index}>
                      <div className="tool-event-head">
                        <strong>{event.tool} · {event.phase}</strong>
                        <small>{event.server} · {workflowTime(event.timestamp)}{event.elapsed_ms !== undefined ? ` · ${(event.elapsed_ms / 1000).toFixed(3)} s` : ''}</small>
                      </div>
                      {event.input !== undefined && <details><summary>Tool input</summary><pre>{JSON.stringify(event.input, null, 2)}</pre></details>}
                      {event.output !== undefined && <details><summary>Tool output</summary><pre>{JSON.stringify(event.output, null, 2)}</pre></details>}
                    </article>
                  ))}
                  </div>
                </details>
              ) : (
                <p className="empty">Waiting for actual execution events.</p>
              )}
            </section>
          )}

        </div>
      </div>
    )}

    <footer>SokoSignal · local synthetic demonstration · no live market evidence or farmer delivery</footer>
  </main>
}
