# Neutral social preview (E3.1a)

`social-preview.svg` is the editable local source for `social-preview.png`
(1200 × 630). It uses repository design-token colours, two equally sized document
symbols, and generic Spanish interface copy. It contains no party logos, programme
positions, quotes, dates, election results, or review badges. It is shared by the
2026 test build and the explicitly labelled private 2023 rehearsal.

The PNG is committed so offline builds need no image renderer or external assets.
The generator copies it to a content-hashed filename for immutable asset caching.
The SVG and this note are not shipped. To regenerate locally with development-only
CairoSVG tooling:

```sh
uv run --with cairosvg python -c 'import cairosvg; cairosvg.svg2png(url="site/assets/social-preview.svg", write_to="site/assets/social-preview.png")'
```

Fonts can differ between rendering environments; inspect the regenerated PNG before
committing it. Human approval of the preview image and copy is pending. Code review
and automated metadata tests do not constitute editorial or release approval.

Metadata follows the [Open Graph protocol](https://ogp.me/): the canonical URL is
also `og:url`; PNG type, dimensions, and Spanish image alternative accompany
`og:image`. Topic URLs describe the topic; current home-route comparison queries
receive generic home metadata. Static HTML cannot select a topic or party pair from
query parameters. No claim about a specific pair is generated for link previews.
