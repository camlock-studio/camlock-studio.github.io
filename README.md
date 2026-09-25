# CamLock website

Promotional site for the CamLock Android app. Astro, no UI framework, no CSS framework,
one npm dependency. It is a static build, intended for GitHub Pages.

This directory is self-contained and is meant to be moved into its own repository. Nothing
outside it is referenced.

## Commands

| Command | What it does |
|---|---|
| `npm install` | install dependencies |
| `npm run dev` | dev server on http://localhost:4321 |
| `npm run build` | static build into `dist/` |
| `npm run preview` | serve the built `dist/` |

## Structure

```
public/            static files copied as-is (favicon, robots.txt, .nojekyll)
src/consts.ts      the strings that change at launch: Play URL, support email, dates
src/styles/        global.css: the dark token set, buttons, cards, reveal utility
src/layouts/       Base.astro: head, header, footer, the scroll-reveal observer
src/components/    Header, Footer, Logo, Phone, Flow, Marquee, Contain
src/pages/         index, privacy, support, 404
.github/workflows/ deploy.yml, which belongs at the repository root after the move
```

Every page style is scoped inside its `.astro` file. Only `src/styles/global.css` is global.

## Design notes

- **Dark only.** The site borrows the child-facing lock screen's identity rather than the
  parent theme, so the teal accent carries the page. There is no light variant by design.
- **`Phone.astro` is the product shot.** Four screens built in CSS — enrolment, Home while
  armed, a live check, the lock screen — matching `docs/DESIGN.md`. `mode="loop"` cycles
  itself in the hero; `mode="scroll"` is driven by `Flow.astro` as the steps scroll past.
  Replace it with real device screenshots when the app is ready to be photographed.
- **Motion.** Scroll reveals and the phone loop both use IntersectionObserver, pause off
  screen, and stop entirely under `prefers-reduced-motion`.
- **Typography** uses device/system fonts. No Google Fonts stylesheet or font-host request is made.

## Before publishing

1. `src/consts.ts` — set `supportEmail` to a real address, and set `playUrl` **only once the Play
   listing actually exists**. It is deliberately empty: a `details?id=` URL resolves to whichever
   app owns that package name, so a guessed link points visitors at a stranger's listing. While it
   is empty, every store call to action renders as a non-clickable "Coming to Google Play" badge.
   `src/components/StoreCta.astro` is the only place allowed to link to a store.
2. `.github/workflows/deploy.yml` — set `SITE_URL` and `BASE_PATH`, and move the file to the
   repository root as `.github/workflows/deploy.yml`.
3. In the GitHub repository: Settings → Pages → Source → GitHub Actions.
4. Have the privacy policy (`src/pages/privacy.astro`) reviewed. It describes what the app
   actually does, but it has not been checked by a lawyer, and Play requires a hosted policy URL.
5. Fill `SITE.operator` only from the issued, reviewed Micky registry documents and agree the
   legal identity/address/contact presentation before commercial publication. They are intentionally
   empty in this local preparation; do not treat a successful build as completed legal identification.
   Set the footer credit as appropriate once the operator is verified. No ID-card images or private
   registration/tax records belong in this repository.
6. Check the final app's handling before submitting Play Data safety: on-device processing and
   optional CSV exports are different flows. A file saved through a cloud document provider can
   leave the phone even though CamLock has no internet permission. The provisional Console draft
   is in the separate app repository at `docs/play-console.md`.
7. Re-check wording if behaviour changes: face templates are biometric measurements, history
   exports can contain child names, removing a child does not clear older history, and app deletion
   does not erase exports or gallery originals. Battery and call behaviour are not guaranteed.
8. Review the support correspondence retention criteria, ordinary-support legal basis and provider
   handling against the actual operation before publication. The current policy describes the
   proposed support workflow, not a completed legal-compliance assessment.
9. Publish only after review, then verify the actual public privacy/support URLs and app link.
   Local changes are not an update to the hosted site until the deployment runs.

## Deploying elsewhere

The build is plain static output in `dist/`. Netlify, Cloudflare Pages and Vercel need
`npm run build` and `dist` as the publish directory, with `BASE_PATH` left at `/`.
