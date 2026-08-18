import type { ReactNode } from 'react'

import { cn } from '@/lib/cn'

interface CardProps {
  title?: string
  action?: ReactNode
  className?: string
  bodyClassName?: string
  children: ReactNode
}

export function Card({
  title,
  action,
  className,
  bodyClassName,
  children,
}: CardProps) {
  return (
    <section
      className={cn(
        'bg-surface border-surface-border rounded-lg border',
        className,
      )}
    >
      {(title || action) && (
        <header className="border-surface-border flex items-center justify-between border-b px-5 py-3">
          {title && (
            <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
          )}
          {action}
        </header>
      )}
      <div className={cn('p-5', bodyClassName)}>{children}</div>
    </section>
  )
}
