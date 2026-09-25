/** Single place for the strings that change when the site goes live. */
export const SITE = {
  name: 'CamLock',
  tagline: 'The phone locks itself when your child picks it up.',
  description:
    'CamLock is an Android app that recognises your own children on the front camera and locks the phone behind a calls-only screen. All face data stays on the device.',
  /**
   * The Play listing. EMPTY UNTIL THE APP IS ACTUALLY PUBLISHED.
   *
   * Do not put a guessed store URL here. A `details?id=` link resolves to whatever
   * app currently owns that package name, which may not be ours, so a placeholder
   * sends visitors to a stranger's listing. While this is empty, every store call
   * to action renders as a non-clickable "Coming to Google Play" badge instead.
   */
  playUrl: '',
  supportEmail: 'camlock-studio@proton.me',
  /** Product credit until the issued business identity has been reviewed. */
  vendor: 'CamLock',
  /** Fill only from Micky's issued registry documents before commercial publication. */
  operator: {
    legalName: '',
    address: '',
    registrationNumber: '',
  },
  lastUpdated: '2026-09-25',
} as const;

/** Prefix an internal path with Astro's configured base, so project-page URLs work. */
export function url(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}/${path.replace(/^\//, '')}`.replace(/\/$/, '') || '/';
}
