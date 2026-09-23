// @ts-check
import { defineConfig } from 'astro/config';

// GitHub Pages serves a project site from https://<user>.github.io/<repo>/, so the
// build needs a base path. Both values come from the environment, which keeps this
// file unchanged when the site moves to its own repository.
//   SITE_URL  e.g. https://<user>.github.io   or https://camlock.app
//   BASE_PATH e.g. /camlock-website/          ("/" for a user site or a custom domain)
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://example.github.io',
  base: process.env.BASE_PATH ?? '/',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
