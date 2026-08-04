/**
 * Phase 0 scaffold check.
 *
 * This is a temporary placeholder that proves Tailwind compiled, the design
 * tokens resolve, and the env flags are being read. It is replaced by the
 * router and AppShell in Phase 2.
 */
function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  const useMocks = import.meta.env.VITE_USE_MOCKS === 'true'

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-8 p-8">
      <header>
        <p className="text-brand-700 text-sm font-semibold tracking-wide uppercase">
          Research prototype
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-900">
          Multimodal Oral Cancer Detection
        </h1>
        <p className="mt-2 text-slate-600">
          Scaffold verified. Tailwind, design tokens and environment flags are
          wired.
        </p>
      </header>

      <section className="border-surface-border bg-surface rounded-lg border p-6">
        <h2 className="mb-4 text-sm font-semibold text-slate-900">
          Environment
        </h2>
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 font-mono text-sm">
          <dt className="text-slate-500">VITE_API_BASE_URL</dt>
          <dd className="text-slate-900">{apiBaseUrl}</dd>
          <dt className="text-slate-500">VITE_USE_MOCKS</dt>
          <dd className="text-slate-900">
            {String(useMocks)}
            <span className="ml-2 font-sans text-slate-500">
              {useMocks ? '(serving fixtures)' : '(calling real backend)'}
            </span>
          </dd>
        </dl>
      </section>

      <section className="border-surface-border bg-surface rounded-lg border p-6">
        <h2 className="mb-4 text-sm font-semibold text-slate-900">
          Diagnostic palette
        </h2>
        <div className="flex flex-wrap gap-3">
          <span className="border-risk-low-border bg-risk-low-bg text-risk-low rounded-full border px-3 py-1 text-sm font-medium">
            Non-Cancer
          </span>
          <span className="border-risk-moderate-border bg-risk-moderate-bg text-risk-moderate rounded-full border px-3 py-1 text-sm font-medium">
            Suspicious
          </span>
          <span className="border-risk-high-border bg-risk-high-bg text-risk-high rounded-full border px-3 py-1 text-sm font-medium">
            Cancer
          </span>
        </div>
      </section>

      <p className="border-risk-moderate-border bg-risk-moderate-bg text-risk-moderate rounded-md border px-4 py-3 text-sm">
        Research prototype. Not a medical device. Not for diagnostic use.
      </p>
    </main>
  )
}

export default App
