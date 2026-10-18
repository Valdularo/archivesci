# MxO Archive

This is a static site and can be hosted on GitHub Pages without a build step or package installation. The searchable landing page is `index.html`; the original archived pages and image assets are kept in their mirrored folders. Archived pages use a shared dark-green theme from `archive/archive-theme.css`.

## Publish with GitHub Pages

1. Create a GitHub repository and add the site files.
2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, select the publishing branch and the repository root (`/`), then save.

The site uses relative links, so it works both at a GitHub Pages project URL and from a local copy. `.nojekyll` tells GitHub Pages to serve the archive as-is.

## Submitting logs

The **Submit Your Logs** page links to a GitHub issue form because GitHub Pages cannot receive file uploads. Submissions are public and contributors need a GitHub account. Contributors can paste short logs into the form or attach a `.txt` file in a follow-up issue comment. Review submissions before adding any material to the archive.

## Updating the search index

The searchable index and transcript next/previous sequence are generated from collection pages in `archive/`. If those pages change, rebuild them with:

```sh
python3 tools/build_catalog.py
```

This also updates `transcript-navigation.js` and adds its script reference to available transcript pages.

Keep the `archive/` directory and the external-image directories alongside the landing page so that archived transcripts and images continue to resolve. Keep `archive-theme.css` in `archive/` so its pages retain the matching design. HTTrack cookies, cache, and crawl logs are not needed to browse or host the site and should not be published.
