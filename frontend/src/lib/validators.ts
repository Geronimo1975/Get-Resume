import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Bitte geben Sie eine gultige E-Mail-Adresse ein'),
  password: z.string().min(1, 'Passwort ist erforderlich'),
})

export const registerSchema = z.object({
  first_name: z.string().min(1, 'Vorname ist erforderlich'),
  last_name: z.string().min(1, 'Nachname ist erforderlich'),
  email: z.string().email('Bitte geben Sie eine gultige E-Mail-Adresse ein'),
  password1: z.string().min(10, 'Passwort muss mindestens 10 Zeichen lang sein'),
  password2: z.string().min(1, 'Passwort-Bestatigung ist erforderlich'),
  privacy_accepted: z.literal(true, {
    errorMap: () => ({ message: 'Sie mussen die Datenschutzerklarung akzeptieren' }),
  }),
}).refine((data) => data.password1 === data.password2, {
  message: 'Passworter stimmen nicht uberein',
  path: ['password2'],
})

export const profileSchema = z.object({
  anrede: z.enum(['herr', 'frau', 'divers', 'keine']),
  geburtsdatum: z.string().nullable(),
  telefon: z.string(),
  strasse: z.string(),
  plz: z.string().regex(/^\d{5}$/, 'PLZ muss 5 Ziffern haben').or(z.literal('')),
  stadt: z.string(),
  bundesland: z.string(),
})

export const documentSchema = z.object({
  title: z.string().min(1, 'Titel ist erforderlich').max(255),
  doc_type: z.enum(['lebenslauf', 'anschreiben', 'deckblatt']),
  template: z.string().nullable(),
})

export type LoginForm = z.infer<typeof loginSchema>
export type RegisterForm = z.infer<typeof registerSchema>
export type ProfileForm = z.infer<typeof profileSchema>
export type DocumentForm = z.infer<typeof documentSchema>
