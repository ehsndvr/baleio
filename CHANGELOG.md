# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-07-06

### Added
- Initial release of **baleio**, an aiogram-style async framework for the Bale bot API.
- `Bot` client covering every documented Bale method, with `aiohttp` session and
  automatic JSON / `multipart/form-data` request serialization.
- Pydantic v2 models for all Bale API types.
- `Dispatcher` / `Router` with per-event observers, nested routers, and dependency
  injection.
- Filters: `Command`, `CommandStart`, `StateFilter`, magic filter `F`, `&` / `|` / `~`
  combinators, and the `CallbackData` factory.
- Finite State Machine: `StatesGroup`, `State`, `FSMContext`, `MemoryStorage`.
- Inline and reply keyboard builders.
- Centralized error handling via `@dp.errors()` and `ErrorEvent`
  (`ExceptionTypeFilter`, `ExceptionMessageFilter`).
- Message shortcuts (`answer`, `reply`, `send_copy`, `edit_text`, …) and Markdown
  helpers (`md`).
- Long polling and webhook support.

[Unreleased]: https://github.com/ehsndvr/baleio/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ehsndvr/baleio/releases/tag/v0.1.0
