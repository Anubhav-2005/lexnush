# Performance report

## Summary

The Flask pages are server-rendered and lightweight in application logic, so time-to-first-byte should be reasonable on a healthy small deployment. The main user-perceived performance risks are image payload, remote fonts, multiple CSS files, a deliberate preloader, and no verified production compression/cache configuration.

## Measured asset observations

| Asset | Observed size/dimensions | Impact | Action |
|---|---|---|---|
| `static/images/lexnush-hero-editorial.png` | about 1.7 MB, 1799×874 | Likely LCP image on homepage; costly on mobile | Export AVIF/WebP, responsive sizes, optimize quality |
| `static/images/anushka.jpeg` | about 940 KB, 3120×4160 | Large for a portrait, though lazy-loaded | Resize to displayed dimensions and serve modern format |
| `static/logo.png` | JPEG data, 1024×1024, about 56 KB | File extension/type mismatch; unnecessary dimensions | Export actual PNG/SVG/WebP and correct MIME/path |

## Estimated Lighthouse ranges

These are engineering estimates, not a live Lighthouse run. Production hosting, device, network, cache, and image conversion can change them substantially.

| Metric | Estimate | Main reason |
|---|---:|---|
| Performance | 60–75 | Large hero image, fonts, CSS requests, preloader |
| Accessibility | 80–90 | Good semantic/focus baseline; contrast and table work pending |
| Best Practices | 75–85 | HTTPS/security patterns good; image/type and production checks pending |
| SEO | 80–90 | Server render and metadata/schema are strong |

## Core Web Vitals interpretation

- **LCP:** the homepage hero image is the likely largest element. Its 1.7 MB PNG can delay LCP, especially on mobile.
- **FCP:** multiple CSS files and Google font requests can delay first paint, though total script complexity is low.
- **CLS:** declared image dimensions help. Verify after real font/image loading and on pages with form errors.
- **INP:** JavaScript is modest and search is debounced; the application should be responsive at low traffic. SQLite write contention could affect interactions under abuse/load.

## Recommendations, in order

1. Convert hero/portrait images to responsive AVIF or WebP, use `srcset`/`sizes`, and retain an appropriate fallback.
2. Remove the artificial preloader or ensure it never blocks initial content.
3. Preload only the single critical font, reduce font weights, and use `font-display: swap`.
4. Bundle/minify CSS for production where it produces a measurable win; remove selectors proven unused only after visual regression testing.
5. Configure host/CDN Brotli or gzip compression and immutable caching for fingerprinted static files. Keep dynamic form HTML deliberately private.
6. Run Lighthouse on the deployed domain using mobile throttling and track CWV in Search Console.

## Performance score: 62/100

The code is not heavy, but media optimisation and production delivery configuration are essential before calling the site fast.
