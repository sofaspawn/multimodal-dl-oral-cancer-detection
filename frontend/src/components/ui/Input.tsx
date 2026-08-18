import { useId, type ComponentPropsWithRef } from 'react'

import { cn } from '@/lib/cn'

interface InputProps extends ComponentPropsWithRef<'input'> {
  label: string
  /** Validation message. Its presence also sets aria-invalid. */
  error?: string
  hint?: string
}

export function Input({
  label,
  error,
  hint,
  id,
  className,
  ...props
}: InputProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const errorId = `${inputId}-error`
  const hintId = `${inputId}-hint`

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="text-sm font-medium text-slate-700">
        {label}
      </label>
      {hint && (
        <p id={hintId} className="text-xs text-slate-500">
          {hint}
        </p>
      )}
      <input
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={cn(error && errorId, hint && hintId) || undefined}
        className={cn(
          'bg-surface h-10 rounded-md border px-3 text-sm text-slate-900',
          'placeholder:text-slate-400',
          'disabled:cursor-not-allowed disabled:bg-slate-50',
          error ? 'border-risk-high' : 'border-surface-border',
          className,
        )}
        {...props}
      />
      {error && (
        <p id={errorId} className="text-risk-high text-xs">
          {error}
        </p>
      )}
    </div>
  )
}
