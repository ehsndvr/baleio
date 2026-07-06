---
sd_hide_title: true
---

# baleio

```{eval-rst}
.. raw:: html

   <h1 style="font-size:3rem;margin-bottom:0">baleio</h1>
```

<p class="baleio-hero">
A modern, fully-async framework for <a href="https://bale.ai">Bale</a> (بله) bots —
inspired by <a href="https://github.com/aiogram/aiogram">aiogram</a>. Same architecture,
same patterns: routers, magic filters, FSM, dependency injection, keyboard builders,
callback-data factories and centralized error handling.
</p>

```{code-block} python
from baleio import Bot, Dispatcher
from baleio.filters import CommandStart
from baleio.types import Message

dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello from baleio! 🌟")

# await dp.start_polling(Bot("123456:TOKEN"))
```

::::{grid} 1 1 2 2
:gutter: 3
:margin: 4 0 0 0

:::{grid-item-card} 🚀 Installation
:link: installation
:link-type: doc
Install baleio and its dependencies in one command.
:::

:::{grid-item-card} ⚡ Quick start
:link: quickstart
:link-type: doc
The aiogram quickstart, ported to baleio almost line-for-line.
:::

:::{grid-item-card} 🧩 Dispatcher & Router
:link: dispatcher
:link-type: doc
Event routing, nested routers, middlewares and dependency injection.
:::

:::{grid-item-card} 🎯 Filters
:link: filters
:link-type: doc
`Command`, magic `F`, combinators, and the `CallbackData` factory.
:::

:::{grid-item-card} 💾 FSM
:link: fsm
:link-type: doc
Finite State Machine with `StatesGroup`, `State` and storages.
:::

:::{grid-item-card} 🧯 Error handling
:link: errors
:link-type: doc
Centralized error handling with `@dp.errors()` and `ErrorEvent`.
:::

::::

## Why baleio?

- **Familiar.** If you know aiogram 3.x, you already know baleio.
- **Typed.** Pydantic v2 models for every Bale API object.
- **Complete.** Every documented Bale method, plus keyboards, FSM and payments.
- **Async-first.** Built on `aiohttp`, with long polling and webhook support.

```{toctree}
:hidden:
:caption: Getting started

installation
quickstart
```

```{toctree}
:hidden:
:caption: Guide

dispatcher
filters
callback_data
fsm
keyboards
errors
```

```{toctree}
:hidden:
:caption: Reference

api
```

```{toctree}
:hidden:
:caption: Project

changelog
GitHub <https://github.com/ehsndvr/baleio>
```
