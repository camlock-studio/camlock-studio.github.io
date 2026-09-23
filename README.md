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
- **Typography** is Inter, loaded from Google Fonts in `Base.astro`. Swap that link for
  self-hosted files if you want the site to make no third-party requests.

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
5. Re-check the claims if the app changes: the copy states under 5 seconds to lock, Android
   8.0+, six children, a 90-day default event retention, and that nothing is transmitted.

## Deploying elsewhere

The build is plain static output in `dist/`. Netlify, Cloudflare Pages and Vercel need
`npm run build` and `dist` as the publish directory, with `BASE_PATH` left at `/`.
