import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/Button'

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-4 text-center">
      <p className="text-brand-700 text-sm font-semibold">404</p>
      <h1 className="text-2xl font-semibold text-slate-900">Page not found</h1>
      <p className="max-w-sm text-sm text-slate-600">
        That page does not exist. It may have been moved, or the link may be
        out of date.
      </p>
      <Link to="/">
        <Button variant="secondary">Back to dashboard</Button>
      </Link>
    </div>
  )
}
