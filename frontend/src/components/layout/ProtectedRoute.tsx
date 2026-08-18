import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/hooks/useAuth'

function FullPageSpinner() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Spinner className="text-brand-600 h-8 w-8" label="Checking session" />
    </div>
  )
}

/** Gate for authenticated routes. Remembers where the user was headed. */
export function ProtectedRoute() {
  const { user, initialising } = useAuth()
  const location = useLocation()

  if (initialising) return <FullPageSpinner />

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  return <Outlet />
}

/**
 * Keeps signed-in users away from the login and register pages.
 *
 * This guard owns the post-login redirect. The auth pages deliberately do not
 * call navigate() themselves: signing in sets the user, which re-renders this
 * component, and two redirects issued in the same tick race each other -- the
 * guard wins and the remembered destination is lost.
 */
export function PublicOnlyRoute() {
  const { user, initialising } = useAuth()
  const location = useLocation()

  if (initialising) return <FullPageSpinner />

  if (user) {
    const from = (location.state as { from?: string } | null)?.from ?? '/'
    return <Navigate to={from} replace />
  }

  return <Outlet />
}
