import { Outlet } from 'react-router-dom'

import { MobileNav, Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function AppShell() {
  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex flex-1">
        <Sidebar />

        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar />
          {/* Bottom padding clears the mobile nav bar. */}
          <main className="flex-1 p-4 pb-20 sm:p-6 md:pb-6">
            <Outlet />
          </main>
        </div>
      </div>

      <MobileNav />
    </div>
  )
}
