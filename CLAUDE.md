# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A browser word-guessing game for children aged 6–8, based on the Italian word game *Abaco zuzzurellone*: a secret word lies between two dictionary ends, and each guess only reveals whether it comes before or after in alphabetical order. Live at https://vcutrona.github.io/abaco-zuzzurellone-kids/.

The entire game (HTML, CSS and JS) lives in a single file, `index.html`. There is no build step, no dependencies, no package manager, no test suite and no linter. To run it, open `index.html` directly or use `python3 -m http.server 8000`.

Development is spec-driven: the author writes the specs and reviews every iteration, and Claude writes code, word lists and texts.

## Working conventions

- **Languages.** Talk to the author in Italian. Code is in English: identifiers, comments, CSS classes, ids and the internal values (e.g. `data-theme` is `light`/`dark`). Only the Italian UI strings (`TEXTS.it`, `CATEGORIES_IT`, the Italian `GROUPS` labels and funny names) are in Italian. The README, commit messages and GitHub templates are in English too.
- **Answers.** Explain choices and trade-offs. When there are several options, propose a few and recommend one.
- **Previews.** When the author asks for a preview ("solo anteprima, non applicare"), work on a copy and show comparison screenshots, without touching `index.html`.
- **Visual checks.** Check every visual change with Playwright (Chromium):
  - at widths 300, 320, 360, 390, 600, 760, 900 and 1280 px, in both light and dark theme;
  - measuring sizes and alignments;
  - confirming that the page never scrolls sideways (`scrollWidth > innerWidth`) and that there are no JS errors.

  If Google Fonts is unreachable, load the real font from the `@fontsource/*` npm packages.
- **Edits to `index.html`.** Make text replacements whose search string occurs exactly once. A too-broad replacement once left stray text in the page (the favicon bug), so after each change also check that no stray text leaked into the page.
- **Persistence.** There is deliberately none: no cookies, no `localStorage`, no tracking. Language, theme, name and selected word groups last only while the page is open. The only external request is the Google Fonts `<link>` for Baloo 2.

## Architecture of `index.html`

### Head and body

- **`<head>`:**
  - meta tags (`viewport-fit=cover`, `theme-color`) and an inline SVG favicon;
  - a tiny script that sets `data-theme` (`light`/`dark`) before paint, which avoids a colour flash;
  - Google Fonts and the main `<style>`.
- **`<body>`:**
  - a shared header on a 3-column grid: language switch or "⬅ Menu" on the left, small logo in the middle, `.controls` with the sun/moon switch on the right;
  - the screens `<section class="screen" id="s-…">`: `s-name`, `s-menu`, `s-secret` (mode 1 setup), `s-groups` (mode 2 group picker), `s-game` (shared by both modes) and `s-end`;
  - the footer.
- **`show(id)`** switches screens and decides what appears in the header and footer for each one.

### Main script

The main script runs in this order:

1. Word data `CATEGORIES_IT` / `CATEGORIES_EN`: 19 categories and 500 words per language. Each entry has the form `{ group, hint, words }`, where `hint` is the category-hint sentence.
2. Tunable constants: `VERSION`, `CPU_GUESS_OPTIONS`, `MAX_CPU_GUESSES`, `NUM_HINTS`, `MAX_CHILD_GUESSES`, `CPU_WORDS`, `NOISE`. They are documented in the README's customisation table, which must stay in sync.
3. `LANGUAGES`, `GROUPS` and `TEXTS`:
   - **`LANGUAGES`** holds, per language, the dictionary ends `start`/`end`, the rules example word, the categories, the surprise-nickname names and adjectives (aligned by index across languages, so the nickname translates when the language changes; Italian adds the gender agreement), and `makeName`.
   - **`GROUPS`** holds the 11 selectable groups `{ id, emoji, it, en }`. Each has at least 21 words per language: small categories, such as musical instruments, are merged so a game is never trivial.
   - **`TEXTS`** holds the UI strings per language. Values are strings or functions with parameters.
4. Utilities, state and functions, then startup.

### i18n

- **Text attributes.** HTML elements carry `data-t`, `data-t-ph` (placeholder) and `data-t-aria` keys. `applyTexts()` fills them through `t(key, …args)`.
- **Changing language.** `loadWords()` rebuilds the deduplicated, sorted dictionary `DICT` and the word→hint map.
- **Allowed screens.** The language can be switched only on the name and menu screens.
- **Initial language.** The first supported language in `navigator.languages`, falling back to English.
- **Adding a language.** Add an entry to `LANGUAGES` and to `TEXTS`, and add its labels to `GROUPS`.

### Words

- `norm()` lowercases and strips accents (NFD), and `cmp()` compares in plain a–z order. `U()` uppercases for display: words are always shown in block capitals.
- Guesses and the secret word must match `/^[a-z]+$/` and lie strictly inside the current interval.

### State

A single `state` object holds the game. The interval is `state.low`/`state.high`. `prevLevel` drives the zoom highlight, `cpuDict` holds the computer's words for this game, and `groups` (a `Set`) holds the selected groups.

## Game specs and decisions

### Mode 1: the child thinks of the word, the computer guesses

- **Secret word.** The child types it in a password field with a "Mostra" button. The UI promises the computer doesn't peek: the word is only used to check the child's answers.
- **Computer guesses.** `cpuTurn` knows only a random subset of `CPU_WORDS` words and picks near the middle of the remaining candidates, with ±`NOISE` noise.
- **Wrong answers.** `answer` checks the child's answer. If the child gets the order wrong, `explain` explains the comparison letter by letter and highlights the two compared letters.
- **Answer buttons.** On phones, Before and After sit side by side with "È lei!" full width below. From 600px they sit in one row.
- **Outcomes.** The child wins if the computer runs out of guesses or knows no word in the interval.
- **Rejected ideas:**
  - forcing the secret word into the computer's vocabulary, which would break the "doesn't peek" promise;
  - a draw for words outside the dictionary;
  - plural recognition;
  - a warning for unknown words.

  Made-up words are an accepted loophole.
- **Reference simulation.** If the computer always knew the word, with ±40% noise it would win 96% of games with 10 guesses. With ±80% noise it drops to 60%, and to 24% with 6 guesses. These changes were not applied.

### Mode 2: the computer thinks of the word, the child guesses

- **Group picker (`s-groups`).** All groups start selected and at least one is required. The word count is always shown. "Gioca ancora" keeps the same groups.
- **Secret word.** It is always drawn from the selected groups, but guesses may be any word.
- **Hints.** `NUM_HINTS` progressive hints, in order: category, first letter, last letter, length. The boxes below them show `B …`, then `B _ _ _ _ O` once the length is known. "Mi arrendo" appears only after the last hint.
- **Free category hint.** If every word in play shares one category, the category hint is given for free (`freeHints`) and the button starts at "Aiuto 1 di 3".
- **Try button.** Under 600px it sits below the field at full width, the same size as the hint button, so it's the natural button to press after typing (the big yellow hint button used to win). From 600px it sits next to the field, and both buttons share a `min-width: 12rem` so they stay the same size (tablets are touch devices too, so the same imbalance applies there).
- **Keyboard.** On touch devices it closes after each guess, so the updated abacus is visible. With a fine pointer the field stays focused.

### The abacus

`draw()` → `drawAbacus()` draws it.

- **Rods.** 26 letter beads: two rods (A–M, N–Z) under 600px, one rod from 600px up.
- **Highlight bar as a mask.**
  - Grey beads sit underneath, with a coloured copy on top clipped by `clip-path` to the bar's shape.
  - Boundary beads are coloured only for the part inside the interval.
  - Where the bar continues onto the other rod, its edge stays straight.
  - At the alphabet ends it overhangs by 6px, so the curve doesn't cut A and Z.
- **Position.** `position(w)` maps a word to 0–26 using its first letters. `START` and `END` are exactly 0 and 26.
- **Bead size.** `--d` is the real diameter: at most `--bead` and never more than 80% of the column, computed with `cqw` units under `@supports`. Bar, wire and beads all use `--d`.
- **Zoom.**
  - When both ends share a prefix (`commonPrefix`), the abacus shows the next letter. For example, between ZEBBA and ZERBA it shows the third letter, from B to R.
  - The row "Iniziano con [Z][E][?]" above it shows the prefix.
  - When the zoom goes one letter deeper, that row turns yellow until the next guess.
  - Letters are highlighted only when they concern the position shown.
- **Accessibility.** The abacus has `role="img"` and a descriptive `aria-label`.
- **Tiles.** The three tiles show the low bound ("dopo"), the word in play and the high bound ("prima di"). `fitTiles()` shrinks long words until they fit.

### UI and design

- **Look.** Flat and colourful, Baloo 2, minimal animation that respects `prefers-reduced-motion`.
- **Layout.** Mobile-first base rules, with breakpoints at 600px and 900px. From 900px the list of tried words moves into a side column.
- **Header sizing.** `--t` sets the header size: the small-logo pills and both switches are always `1.6em` tall. Under 420px "⬅ Menu" becomes an arrow only, and under 340px `--t` drops to `.7rem`.
- **Switches.** The theme and language switches are identical in size, shadow and animation, with `role="switch"` and a 64×44px touch area. The theme follows `prefers-color-scheme` until the child touches the switch.
- **iOS.** Respect safe areas (`env(safe-area-inset-*)`) and keep input fonts at 16px or more to avoid iOS auto-zoom.
- **Texts.**
  - Messages avoid gendered adjectives, for example "Hai vinto, X!".
  - The footer shows only on the name and menu screens: version, GitHub, MIT licence, "made with Claude", and Wikipedia. Its items wrap whole, without separator dots.

## Releases and deployment

- **Versions.** The project uses SemVer. `VERSION` in `index.html` must equal the Git tag without the `v`.
- **GitHub Pages.** The source is *GitHub Actions*. The `github-pages` environment allows deployments from `v*` tags.
- **When it deploys.** `.github/workflows/deploy.yml` runs only on `v*` tag pushes, or manually from a tag. Commits on `main` without a tag publish nothing.
- **Workflow checks.** It verifies that the run is for a tag, that the tag is on `main`, and that it matches `VERSION`.
- **Published files.** Only the files listed in the "Prepare the site folder" step are published, currently just `index.html`.
- **Release steps:**
  1. Run `bump-my-version bump patch|minor|major`. With `.bumpversion.toml` it updates `VERSION`, commits, and creates the annotated tag `vX.Y.Z` locally.
  2. Run `git push origin main`.
  3. Push the tag separately with `git push origin vX.Y.Z`.
- **The v1.0.0 deploy.** Pushing the tag did not start the workflow: the tag had been deleted and recreated, and the workflow file reached GitHub in the same push. The manual run from the tag worked. If a fresh tag pushed on its own doesn't start the workflow either, investigate.

## Roadmap

**Next, agreed: PWA**
- `manifest.json` with PNG icons and an `apple-touch-icon`.
- A service worker for offline use.
- Self-hosting the font instead of loading it from Google Fonts, and updating the README Privacy section accordingly.
- Adding all the new files to the workflow's "Prepare the site folder" step.

**Ideas, not decided:**
- **Mobile stores.** Package the game with Capacitor or a TWA. In the kids category the footer links would need a parental gate.
- **Mode 1 word groups.** Let the child pick groups in mode 1 too ("pensa a un animale!").
- **Difficulty label.** Show easy, medium or hard under the choice of computer guesses.
- **Menu intro.** Shorten it, since it partly repeats "Come si gioca".
- **Font.** Playpen Sans was previewed and not adopted. If adopted, check the small logo on narrow phones, because the font is wider.
- **Zoom across two letters.** When the bounds straddle two first letters (e.g. YAK–ZEBU), the bar stays narrow. Not addressed yet.
- **Feedback without a GitHub account.** For now there is no channel.
