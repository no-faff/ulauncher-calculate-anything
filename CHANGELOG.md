# Changelog

Notable changes to this fork. There are no formal releases; Ulauncher installs
the extension straight from the repository, so dates are when a change landed on
the `main` branch.

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
  rates..." line shows while the first fetch loads. (#7, originally raised in #1)
- **babel** is now a core dependency, installed automatically with the others.
  It gives locale-aware formatting: correct plurals, full currency names, and
  local spellings such as metres and litres on en_GB systems. (#5)

### Changed

- Saved preferences now take effect on the next keystroke instead of needing a
  Ulauncher restart. In API v2 compat mode Ulauncher does not reliably signal
  preference changes, so the extension re-reads and re-applies them itself.
- Dependencies install automatically from a root `requirements.txt`; the manual
  `pip install` step is gone. (#5)

### Fixed

- The timezone database is now rebuilt atomically after an extension update.
  The old approach deleted the cached database before rebuilding, so an
  interrupted rebuild left none and `time` showed no cities until a later run.
  It now swaps in only once complete and keeps the previous database on failure.
- babel formatting on systems where only the `.UTF-8` form of a locale is
  generated; it previously errored and fell back to non-localised output. (#6)
