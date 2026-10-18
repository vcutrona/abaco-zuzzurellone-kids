# Abaco… Zuzzurellone!

A colourful word-guessing game for children aged 6–8, based on the classic Italian word game *Abaco zuzzurellone*. It runs entirely in the browser, in Italian and English, and can be installed on phones and tablets to play offline.

**Play it:** [vcutrona.github.io/abaco-zuzzurellone-kids](https://vcutrona.github.io/abaco-zuzzurellone-kids/)

## The game

[*Abaco zuzzurellone*](https://it.wikipedia.org/wiki/Abaco_zuzzurellone) is a traditional Italian word game (Wikipedia article in Italian). One player thinks of a secret word, and the others try to guess it. After each guess, the only clue is whether the secret word comes **before** or **after** the guessed word in alphabetical order. Each answer narrows the interval, until someone finds the word.

The game takes its name from the two words that open and close the interval at the start. *Abaco* is among the first entries of an Italian dictionary, and *zuzzurellone* (a playful, childish person) is traditionally known as the last one. In the English version, the interval runs from *aardvark* to *zyzzyva*, the first and last words of many English dictionaries.

Without ever saying so, the game is a binary search over a dictionary. It is also a fun way for children to practise the alphabet and alphabetical order.

## Features

**Two game modes**
- *You think of the word.* The child is the one who knows the secret word, and the computer tries to guess it within a number of guesses chosen at the start (6 to 15). The child answers *before*, *after* or *that's it!*. If the child gets the alphabetical order wrong, the game explains the comparison letter by letter.
- *You guess the word.* The computer picks a secret word and the child has 20 guesses to find it. Four progressive hints are available: the word's category, its first letter, its last letter, and its length.

**Word groups.** In the second mode, the child can choose which groups of words to play with, for example only animals or only clothes. With a single group, the category hint is given for free.

**The alphabet abacus.** The current interval is drawn as an abacus with 26 letter beads, and a highlight bar marks where the secret word can still be. When both ends of the interval start with the same letters, the abacus zooms in on the next letter. For example, between *ZEBBA* and *ZERBA* it shows the third letter, from B to R.

**Child-friendly design**
- Words are shown in block capitals, the first alphabet children learn to write.
- Flat, colourful graphics with minimal animation.
- Optional name or nickname, or a funny surprise nickname such as *Dancing Penguin*.

**Two languages.** The game is available in Italian and English, each with its own 500 simple nouns in 19 categories. On first load, the language is picked from the browser's preferred languages, with English as fallback.

**Light and dark theme.** The game follows the device setting, and a sun/moon switch changes it.

**Mobile-first.** The layout is designed for phones first and adapts to tablets and desktops. The abacus splits into two rods on narrow screens.

**Accessible.** The game supports keyboard navigation, uses screen reader labels, and respects reduced-motion settings.

**Installable and offline.** The game is a Progressive Web App: it can be added to the home screen and, after the first visit, it works without an internet connection.

**No tracking, no storage.** There are no cookies and no accounts, and nothing is saved between sessions. The browser only keeps a copy of the game files, for offline use.

## How to run it

The game is plain HTML, CSS and JavaScript in `index.html`, with no build step and no dependencies. Next to it are the files of the installable app: `manifest.webmanifest`, the service worker `sw.js`, the icons in `icons/` and the font in `fonts/`.

**Locally:** serve the folder with any static server:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` directly also works, but without offline support: service workers only run over `http` or `https`.

**On GitHub Pages:** the workflow in `.github/workflows/deploy.yml` publishes the game when a version tag (for example `v1.0.3`) is pushed. In *Settings → Pages*, the source must be *GitHub Actions*. Only the files listed in the workflow's "Prepare the site folder" step are published.

## Versioning

The game follows [Semantic Versioning](https://semver.org/). The current version is shown in the footer of the start screens and is set by the `VERSION` constant at the top of the script (the same constant in `sw.js` names the offline cache). Each release should update both and get a matching Git tag (for example `v1.0.0`). [bump-my-version](https://github.com/callowayproject/bump-my-version) does all three: `bump-my-version bump patch` (or `minor`, `major`) updates the version, commits and tags.

## Customisation

All settings are at the top of the script in `index.html`:

| Constant | Default | Meaning |
|---|---|---|
| `CPU_GUESS_OPTIONS` | `[6, 8, 10, 12, 15]` | Guess limits the child can give the computer |
| `MAX_CPU_GUESSES` | `10` | Preselected guess limit for the computer |
| `MAX_CHILD_GUESSES` | `20` | Guesses available to the child |
| `NUM_HINTS` | `4` | Number of hints |
| `CPU_WORDS` | `100` | How many words the computer knows in each game (a random subset) |
| `NOISE` | `0.4` | How far the computer strays from the middle of the interval (±40%) |

The computer does not play a perfect binary search. It picks a word near the middle of the remaining interval, with some random noise, and it only knows a random subset of 100 words in each game. This keeps it beatable: a child who thinks of an unusual word has a good chance of winning.

**Word lists.** The lists are `CATEGORIES_IT` and `CATEGORIES_EN`. Each category has a group (used for word selection), a hint sentence and a list of words. Duplicates and ordering are handled automatically.

**Adding a language:**
1. Add an entry to `LANGUAGES` with the interval words, an example word, the word list and the surprise names.
2. Add its texts to `TEXTS`.
3. Add its labels to `GROUPS`.

## Privacy

The game makes no requests to other sites: the *Baloo 2* font is served together with the game.

## Credits

This game was entirely generated by Claude (Opus 5.5), Anthropic's AI assistant, through a spec-driven process. The author wrote the specifications, reviewed every iteration and guided the design. Claude wrote all the code, word lists and texts.

- Font: [Baloo 2](https://fonts.google.com/specimen/Baloo+2) by Ek Type, licensed under the SIL Open Font License (see `fonts/OFL.txt`).
- Game concept: the traditional Italian word game [*Abaco zuzzurellone*](https://it.wikipedia.org/wiki/Abaco_zuzzurellone).

## License

Released under the [MIT License](LICENSE).
