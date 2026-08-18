import type { PredictionOutcome } from '@/api/types'
import { usePrefersReducedMotion } from '@/hooks/usePrefersReducedMotion'
import { cn } from '@/lib/cn'
import { confidenceBand, formatPercent } from '@/lib/format'

const RADIUS = 80
const ARC_LENGTH = Math.PI * RADIUS
/** Semicircle from left to right across the top. */
const ARC_PATH = `M 20 100 A ${RADIUS} ${RADIUS} 0 0 1 180 100`

const COLOURS: Record<PredictionOutcome['prediction'], string> = {
  Cancer: 'text-risk-high',
  'Non-Cancer': 'text-risk-low',
  Pending: 'text-slate-400',
}

interface ConfidenceGaugeProps {
  value: number
  prediction: PredictionOutcome['prediction']
}

export function ConfidenceGauge({ value, prediction }: ConfidenceGaugeProps) {
  const reducedMotion = usePrefersReducedMotion()
  const clamped = Math.min(Math.max(value, 0), 1)
  const offset = ARC_LENGTH * (1 - clamped)
  const band = confidenceBand(clamped)

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-full max-w-[240px]">
        <svg
          viewBox="0 0 200 110"
          className={cn('w-full', COLOURS[prediction])}
          role="meter"
          aria-valuenow={Math.round(clamped * 100)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuetext={`${formatPercent(clamped)} confidence, ${band.label.toLowerCase()}`}
          aria-label="Model confidence"
        >
          <path
            d={ARC_PATH}
            fill="none"
            stroke="currentColor"
            strokeWidth="14"
            strokeLinecap="round"
            className="opacity-15"
          />
          <path
            d={ARC_PATH}
            fill="none"
            stroke="currentColor"
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={ARC_LENGTH}
            strokeDashoffset={offset}
          >
            {/* SMIL rather than a CSS transition: the final value is correct on
                first paint, so a transition would have nothing to animate from.
                Omitted entirely when the viewer asks for reduced motion. */}
            {!reducedMotion && (
              <animate
                attributeName="stroke-dashoffset"
                from={ARC_LENGTH}
                to={offset}
                dur="0.9s"
                fill="freeze"
                calcMode="spline"
                keySplines="0.22 1 0.36 1"
                keyTimes="0;1"
              />
            )}
          </path>
        </svg>

        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center">
          <span className="text-3xl font-semibold text-slate-900 tabular-nums">
            {formatPercent(clamped)}
          </span>
          <span className="text-xs font-medium tracking-wide text-slate-500 uppercase">
            {band.label} confidence
          </span>
        </div>
      </div>

      <p className="max-w-xs text-center text-xs text-slate-600">
        {band.description}
      </p>
    </div>
  )
}
