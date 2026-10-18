# Archival Science local website

This is a static site and can be hosted on GitHub Pages without a build step or package installation. The searchable landing page is `index.html`; the original archived pages and image assets are kept in their mirrored folders. Archived pages use a shared dark-green theme from `archivalscience.shock-therapy.org/archive-theme.css`.

## Publish with GitHub Pages

1. Create a GitHub repository and add the site files.
2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, select the publishing branch and the repository root (`/`), then save.

The site uses relative links, so it works both at a GitHub Pages project URL and from a local copy. `.nojekyll` tells GitHub Pages to serve the archive as-is.

## Updating the search index

The searchable index is generated from collection pages in `archivalscience.shock-therapy.org/`. If those pages change, rebuild `catalog.js` with:

```sh
python3 tools/build_catalog.py
```

Keep the mirrored site directory and the external-image directories alongside the landing page so that archived transcripts and images continue to resolve. Keep `archive-theme.css` in the mirrored directory so its pages retain the matching design. HTTrack cookies, cache, and crawl logs are not needed to browse or host the site and should not be published.
