# Accessibility report

## Scope

This is a code and manual-behaviour review against WCAG 2.2 principles. It is not a formal accessibility conformance certification. Automated axe/WAVE scans and testing with screen-reader users were not run during this audit.

| Area | Score | What is good | What to improve |
|---|---:|---|---|
| Keyboard support | 8/10 | Mobile menu/search support Escape, focus trap, and return focus | Test all controls with keyboard in production browser builds |
| Focus visibility | 8/10 | Shared reset includes focus styling | Verify contrast in both themes and avoid focus hidden behind fixed header |
| Semantic structure | 8/10 | Server HTML, headings, forms, navigation, and footer have meaningful structure | Audit actual heading sequence on every page as content changes |
| Form accessibility | 8/10 | Labels, error links/state and server validation are present | Add `aria-describedby` consistently and explain success/failure timing |
| ARIA usage | 7/10 | Dialog/menu interactions have useful ARIA/focus treatment | Add `aria-current="page"` to active navigation; avoid ARIA where native HTML suffices |
| Images/media | 7/10 | Decorative/meaningful imagery is handled in templates | Review every alternative text against the image’s purpose; logo file type should be corrected |
| Contrast/theme | 7/10 | Light/dark themes use deliberate variables | Measure all text, muted labels, borders, and focus rings with a contrast tool |
| Motion | 8/10 | Reduced-motion styles exist | Remove unnecessary preloader and test no-motion state |
| Tables/content | 6/10 | Article uses structured content | Add a visible or screen-reader table caption and header scope where appropriate |
| Touch and mobile | 7/10 | Spacious controls and menu exist | Test real-device target sizes/overlap at every viewport |

## Findings in simple English

The site already does several difficult things well: dialog focus is managed, most form fields have visible labels, and the browser gets semantic HTML instead of a JavaScript-only shell. The main remaining risks are not obvious to sighted mouse users: colour contrast in every theme/state, navigation current-page announcement, table context, floating-control overlap, and real screen-reader/device testing.

## Priority fixes

1. Run axe-core plus manual NVDA/VoiceOver keyboard checks for Home, Journal, article, Contact, 404, mobile menu and search.
2. Add `aria-current="page"` to the selected primary nav link.
3. Add a caption (or accessible caption) and correct header scope to the article table.
4. Test contrast for muted text, button states, theme toggle, and focus outline against WCAG AA.
5. Ensure nonessential animation/preloader cannot delay content or confuse assistive technology.

## Accessibility score: 78/100

Strong foundations, but not yet enough evidence for a formal WCAG claim.
