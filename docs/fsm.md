# Finite State Machine

baleio ships an FSM for multi-step conversations, modeled on aiogram's.

Define states as a `StatesGroup`:

```python
from baleio.fsm import State, StatesGroup

class Form(StatesGroup):
    name = State()
    age = State()
```

Drive the conversation with an injected `FSMContext`:

```python
from baleio.filters import Command
from baleio.fsm import FSMContext
from baleio.types import Message

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("What's your name?")

@dp.message(Form.name)                       # a State used directly as a filter
async def got_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("How old are you?")

@dp.message(Form.age)
async def got_age(message: Message, state: FSMContext):
    data = await state.update_data(age=message.text)
    await state.clear()
    await message.answer(f"{data['name']} — {data['age']}")
```

## States as filters

You can pass a `State` (or the whole `StatesGroup`) directly to a handler decorator; it
is wrapped in a `StateFilter` automatically:

```python
@dp.message(Form.name)      # only when the current state is Form.name
@dp.message(Form)           # any state in the Form group
```

`StateFilter(None)` matches users with **no** active state.

## FSMContext API

`await state.set_state(Form.age)`
: set the current state (or `None` to leave the machine).

`await state.get_state()`
: return the current state string, or `None`.

`await state.update_data(**kwargs)` / `await state.get_data()` / `await state.set_data(dict)`
: read & write the per-user data bag; `update_data` returns the merged data.

`await state.clear()`
: clear both state and data.

## Storage

The default `MemoryStorage` keeps state in-process (great for development and small
bots). The storage interface is pluggable — implement `BaseStorage` to back it with
Redis, a database, etc.

```python
from baleio import Dispatcher
from baleio.fsm import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())
```
