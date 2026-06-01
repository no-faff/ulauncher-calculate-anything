# Changelog

Changes to this fork of [tchar's calculate-anything](https://github.com/tchar/ulauncher-albert-calculate-anything),
the work done on top of the original to fix it for Ulauncher 6 and harden it.
There are no formal releases; Ulauncher installs the extension straight from the
repository, so dates are when a change landed on the `main` branch.

## 2026-06-01

An audit pass over the whole module: the calculator and base-n evaluation, the
currency, time and unit domains, the localisation layer, dependency handling and
the docs. Every fix below ships with regression tests (the suite went from 365 to
387, and both the babel and non-babel test paths stay green).

### Security

- The expression evaluator no longer allows attribute access, so string and
  bytes methods can no longer be reached. `= 'a'.center(500000000)` previously
  allocated hundreds of megabytes from a one-line input. Numbers, operators
  and the built-in function names are the only tokens the calculator and base-n
  evaluators now accept.
- The power operator caps the exponent rather than the simpleeval default of
  four million, so `= 9 ^ 4000000` is rejected before it is computed instead of
  spending over a second building a multi-million-digit integer. The memory
  power and root functions (`m0e`, `m0r`) go through the same guard.
- A pasted query longer than 1000 characters is refused before it reaches any
  handler, so an oversized paste cannot be used to drive the regex or evaluation
  paths.
- The time-query split pattern was made linear. A run of spaces after `time`
  caused quadratic backtracking, so a long whitespace paste froze the launcher
  for seconds on every keystroke.
- Removed three unused regexes, two of which (the old currency-query patterns)
  backtracked catastrophically, so they cannot be reintroduced into a live path
  by mistake.

### Fixed

- Negative base-n results keep their sign. `dec 3 - 5` showed `b10`, `o2` and
  `x2` for binary, octal and hex instead of `-10`, `-2` and `-2`.
- A power past the float range, such as `= 2 ^ 1024`, no longer interrupts the
  query while building its result; it returns no result cleanly.
- `= 9 ^ 9 ^ 9` and similar oversized powers no longer log a spurious error
  every keystroke; they are recognised as a normal rejection.
- `time at Athens, AL` and other state-code lookups work again. The state match
  in the city database compared the wrong identifiers and never matched, so only
  the local time showed.
- A corrupt or truncated timezone cache no longer breaks the `time` command. The
  damaged file is now detected when it is opened and the built-in database is
  used instead, where before the first query failed and showed no cities until
  the file was deleted by hand.
- `time minus 1 day` reads as "Yesterday" rather than "last week" when the day
  before falls in the previous calendar week.
- The percentage subtraction `= 50 - 10%` is described as a subtraction, not an
  addition. The result was already correct.
- Equality between imaginary values is correct: `= 2i = 3i` is false, where it
  previously compared only the real parts and returned true.
- A malformed exchange rate from mycurrency.net (a non-numeric value) is now
  dropped on its own instead of discarding every rate from that fetch.
- Bare unit names like `pint` and the `currency_` internal prefix are stripped
  correctly. The previous code removed a set of characters rather than a prefix,
  which mangled some lowercase aliases.
- Missing pytz shows a clear "install pytz" message rather than stopping the
  whole extension from loading, matching how the other dependencies already
  degrade.
- Temperatures localise on the same minimal-locale systems where other units
  already did; the two paths now resolve the locale the same way.
- Text you type in a `time until ...` query keeps its capitalisation in the
  result: "until March" is no longer echoed back as "Until march".

### Changed

- The exchange-rate cache is written atomically. It is serialised to a temporary
  file and swapped into place, so a crash or a concurrent read during the write
  can no longer leave a half-written `currency_data.json`.

### Internal

- Corrected the `CurrencyRate` type to name the field the providers actually
  write (`timestamp_refresh`), fixed the `is_not_types` type hints, and replaced
  two mutable default arguments with `None`.
- Fixed the percentage-handler error logs that all read "inverse percentage"
  regardless of which percentage path they came from.
- Added a `capitalize_first` helper so only the first character of a string is
  upper-cased, leaving acronyms and non-English words intact.
- Added the `of` and `is` keys to the calculator translation strings, so the
  percentage descriptions can be localised rather than falling back to English.
- Added regression tests across the calculator, base-n, percentage, time,
  currency and utility suites for every fix above, plus a missing-pytz path and a
  corrupt-cache path.

### Documentation

- Corrected the README worked examples (`3 + 2 * pi % of cos(pi) + 5` is
  0.371327; the `until midnight` and SI-case-symbol notes now match the
  behaviour) and dropped the stale "requires cache" note on default currencies
  now that they fetch on demand.
- Fixed the manifest preference help text: two entries used a misspelt key, so
  Ulauncher showed no description for Default Currencies and Default Cities, and
  the units-conversion-mode entry had no description at all.
- Made the API documentation examples actually run: corrected the import paths,
  the `QueryHandler` class name, the handler call and the logging-handler
  example, and added the service-start calls the query example needs.
- Added a missing-pytz install message to the locale strings.
- Fixed clear spelling slips in the inherited comments and docstrings, leaving
  the original wording and tone otherwise untouched.

## 2026-05-31

### Added

- **Imperial/US units** preference deciding what bare unit names like `pint`
  and `gallon` mean: US (default, unchanged) or imperial. With imperial set,
  `= 26 pints to litres` gives 14.77 rather than 12.30. Explicit `us_`, `uk_`,
  `imp_` and `imperial_` forms such as `uk_pint` always work, in any case.
- Currency conversion now works with the **Currency Cache** preference set to
  **None**. None means "do not store a cache" rather than "currency off": rates
  are fetched on demand when you convert, held in memory only, and reused
  briefly so back-to-back conversions do not refetch. A "Fetching exchange
  rates..." line shows while the first fetch loads. (#7, originally raised in #1
  by [Karl Lundgren](https://github.com/kallegrens))
- **babel** is now a core dependency, installed automatically with the others.
  It gives locale-aware formatting: correct plurals, full currency names, and
  local spellings such as metres and litres on en_GB systems. Contributed by
  [Karl Lundgren](https://github.com/kallegrens). (#5)

### Changed

- Saved preferences now take effect on the next keystroke instead of needing a
  Ulauncher restart. In API v2 compat mode Ulauncher does not reliably signal
  preference changes, so the extension re-reads and re-applies them itself.
- Dependencies install automatically from a root `requirements.txt`; the manual
  `pip install` step is gone. Contributed by
  [Karl Lundgren](https://github.com/kallegrens). (#5)

### Fixed

- The timezone database is now rebuilt atomically after an extension update.
  The old approach deleted the cached database before rebuilding, so an
  interrupted rebuild left none and `time` showed no cities until a later run.
  It now swaps in only once complete and keeps the previous database on failure.
- babel formatting on systems where only the `.UTF-8` form of a locale is
  generated; it previously errored and fell back to non-localised output. (#6)

### Documentation

- Expanded and corrected the README: per-mode command syntax, the
  keyword-then-space rule, `to` (not `in`) for conversions, the SI symbol case
  rule, base-n syntax and the imperial/US setting, plus fixes to the default
  currencies list and several typos.

## 2026-03-28

The fork's foundation: making the extension work on Ulauncher 6, whose version 6
beta had broken it, plus the deadlock fix that makes currency conversion
reliable under load.

### Fixed

- Ulauncher 6 compatibility. Version 6 changed the query API so a handler
  receives a Query object rather than a string, which stopped the extension
  working; the keyword handling was updated to suit.
- Fixed a deadlock where the currency service could block the query handler
  while it waited on a network request. The service now uses fine-grained
  locking and sets a timeout on every request, so a slow or unreachable provider
  no longer freezes the launcher. The fix is a cherry-pick of
  [nnqnn](https://github.com/nnqnn)'s work in the upstream PR #67.

### Changed

- Saved preferences take effect on the next keystroke rather than needing a
  Ulauncher restart.

### Documentation

- Reworked the README for the fork: attribution to the original by tchar,
  context on the Ulauncher 6 situation, and removal of stale badges and the
  Albert references that are untested here.

## 2025-12-03

Calculator features contributed by Cyril Li, carried forward into this fork.

### Added

- A trigonometry mode covering degrees, radians and gradians, with `deg` and
  `rad` functions to convert between them.
- The reciprocal trig functions `csc`, `sec`, `cot` and their inverses `acsc`,
  `asec` and `acot`.
- Ten persistent calculator memory slots, `m0` to `m9`, with functions to load,
  clear, add, subtract, multiply, divide, raise to a power and take a root of
  each slot, `mc()` to clear them all, and `ans()` for the last result.
