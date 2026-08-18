import { useId } from 'react'

import { cn } from '@/lib/cn'

interface BooleanFieldProps {
  label: string
  value: boolean | undefined
  onChange: (value: boolean) => void
  error?: string
}

const CHOICES = [
  { label: 'Yes', value: true },
  { label: 'No', value: false },
]

/**
 * A yes/no question rendered as a segmented pair of radios.
 *
 * Starts unanswered on purpose. Defaulting a clinical risk factor to "No"
 * would silently record an answer the clinician never gave.
 */
export function BooleanField({
  label,
  value,
  onChange,
  error,
}: BooleanFieldProps) {
  const name = useId()
  const errorId = `${name}-error`

  return (
    <fieldset
      className="flex flex-col gap-1.5"
      aria-invalid={error ? true : undefined}
      aria-describedby={error ? errorId : undefined}
    >
      <legend className="text-sm font-medium text-slate-700">{label}</legend>
      <div className="flex gap-2">
        {CHOICES.map((choice) => {
          const selected = value === choice.value
          return (
            <label
              key={choice.label}
              className={cn(
                'flex cursor-pointer items-center justify-center rounded-md border px-4 py-1.5 text-sm font-medium transition-colors',
                'has-[:focus-visible]:outline-brand-600 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2',
                selected
                  ? 'border-brand-600 bg-brand-50 text-brand-700'
                  : 'border-surface-border bg-surface text-slate-600 hover:bg-slate-50',
                error && !selected && 'border-risk-high-border',
              )}
            >
              <input
                type="radio"
                name={name}
                className="sr-only"
                checked={selected}
                onChange={() => onChange(choice.value)}
              />
              {choice.label}
            </label>
          )
        })}
      </div>
      {error && (
        <p id={errorId} className="text-risk-high text-xs">
          {error}
        </p>
      )}
    </fieldset>
  )
}
