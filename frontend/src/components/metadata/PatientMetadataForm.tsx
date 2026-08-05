import { zodResolver } from '@hookform/resolvers/zod'
import { Controller, useForm, useWatch } from 'react-hook-form'
import type { ReactNode } from 'react'

import { BooleanField } from '@/components/ui/BooleanField'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import {
  LESION_SITE_OPTIONS,
  SEX_OPTIONS,
  TOBACCO_TYPE_OPTIONS,
  patientMetadataSchema,
  type PatientMetadataValues,
} from '@/lib/metadataSchema'

interface PatientMetadataFormProps {
  onSubmit: (values: PatientMetadataValues) => void | Promise<void>
  /**
   * Called on a submit attempt that fails this form's own validation. The
   * parent uses it to surface problems it owns -- a missing image -- at the
   * same time as the field errors, instead of one round of fixes later.
   */
  onInvalid?: () => void
  submitting?: boolean
  /** Rendered above the submit button, e.g. an upload error from the parent. */
  footer?: ReactNode
}

/** Empty string -> undefined, so a blank number field reports "required"
 *  rather than "expected number, received NaN". */
const numberField = { setValueAs: (v: string) => (v === '' ? undefined : Number(v)) }

function Fieldset({
  legend,
  children,
}: {
  legend: string
  children: ReactNode
}) {
  return (
    <fieldset className="flex flex-col gap-4">
      <legend className="mb-2 text-xs font-semibold tracking-wide text-slate-500 uppercase">
        {legend}
      </legend>
      {children}
    </fieldset>
  )
}

export function PatientMetadataForm({
  onSubmit,
  onInvalid,
  submitting = false,
  footer,
}: PatientMetadataFormProps) {
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PatientMetadataValues>({
    resolver: zodResolver(patientMetadataSchema),
  })

  // useWatch rather than watch(): it returns a value instead of a function, so
  // the React Compiler can still optimise this component.
  const usesTobacco = useWatch({ control, name: 'tobacco_use' })

  return (
    <form
      onSubmit={handleSubmit(onSubmit, onInvalid)}
      noValidate
      className="flex flex-col gap-8"
    >
      <Fieldset legend="Demographics">
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Age"
            type="number"
            inputMode="numeric"
            min={1}
            max={120}
            error={errors.age?.message}
            {...register('age', numberField)}
          />
          <Select
            label="Sex"
            options={SEX_OPTIONS}
            error={errors.sex?.message}
            {...register('sex')}
          />
        </div>
      </Fieldset>

      <Fieldset legend="Risk factors">
        <Controller
          control={control}
          name="tobacco_use"
          render={({ field }) => (
            <BooleanField
              label="Tobacco use"
              value={field.value}
              onChange={field.onChange}
              error={errors.tobacco_use?.message}
            />
          )}
        />

        {usesTobacco && (
          <div className="border-brand-200 grid gap-4 border-l-2 pl-4 sm:grid-cols-2">
            <Select
              label="Type of tobacco"
              options={TOBACCO_TYPE_OPTIONS}
              error={errors.tobacco_type?.message}
              {...register('tobacco_type')}
            />
            <Input
              label="Years of use"
              type="number"
              inputMode="numeric"
              min={0}
              max={100}
              error={errors.tobacco_years?.message}
              {...register('tobacco_years', numberField)}
            />
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <Controller
            control={control}
            name="betel_quid_use"
            render={({ field }) => (
              <BooleanField
                label="Betel quid / areca nut use"
                value={field.value}
                onChange={field.onChange}
                error={errors.betel_quid_use?.message}
              />
            )}
          />
          <Controller
            control={control}
            name="alcohol_use"
            render={({ field }) => (
              <BooleanField
                label="Alcohol use"
                value={field.value}
                onChange={field.onChange}
                error={errors.alcohol_use?.message}
              />
            )}
          />
        </div>
      </Fieldset>

      <Fieldset legend="Lesion">
        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label="Site"
            options={LESION_SITE_OPTIONS}
            error={errors.lesion_site?.message}
            {...register('lesion_site')}
          />
          <Input
            label="Duration (weeks)"
            type="number"
            inputMode="numeric"
            min={0}
            max={520}
            error={errors.lesion_duration_weeks?.message}
            {...register('lesion_duration_weeks', numberField)}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Controller
            control={control}
            name="pain"
            render={({ field }) => (
              <BooleanField
                label="Pain"
                value={field.value}
                onChange={field.onChange}
                error={errors.pain?.message}
              />
            )}
          />
          <Controller
            control={control}
            name="bleeding"
            render={({ field }) => (
              <BooleanField
                label="Bleeding"
                value={field.value}
                onChange={field.onChange}
                error={errors.bleeding?.message}
              />
            )}
          />
        </div>

        <Controller
          control={control}
          name="prior_lesion_history"
          render={({ field }) => (
            <BooleanField
              label="History of prior oral lesions"
              value={field.value}
              onChange={field.onChange}
              error={errors.prior_lesion_history?.message}
            />
          )}
        />
      </Fieldset>

      {footer}

      <Button type="submit" size="lg" loading={submitting}>
        Run analysis
      </Button>
    </form>
  )
}
