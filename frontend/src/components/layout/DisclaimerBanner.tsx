import { cn } from '@/lib/cn'

/**
 * Regulatory guard rail.
 *
 * This app renders model output that looks like a diagnosis. It must be
 * impossible to see a prediction without also seeing this. Rendered once in the
 * app shell and again on the result page -- the duplication is deliberate.
 */
export function DisclaimerBanner({ className }: { className?: string }) {
  return (
    <p
      role="note"
      className={cn(
        'border-risk-moderate-border bg-risk-moderate-bg text-risk-moderate',
        'flex items-center gap-2 border-b px-4 py-2 text-xs sm:text-sm',
        className,
      )}
    >
      <svg
        viewBox="0 0 20 20"
        fill="currentColor"
        className="h-4 w-4 shrink-0"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.515 2.625H3.72c-1.345 0-2.188-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 10 5zm0 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"
          clipRule="evenodd"
        />
      </svg>
      <span>
        <strong className="font-semibold">Research prototype.</strong> Not a
        medical device and not for diagnostic use. All output requires review by
        a qualified clinician.
      </span>
    </p>
  )
}
