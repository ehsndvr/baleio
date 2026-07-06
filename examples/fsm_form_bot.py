"""A registration form using the FSM.

    export BALE_TOKEN=123456:xxxxxxxx
    python examples/fsm_form_bot.py
"""
from __future__ import annotations

import asyncio
import os

from baleio import Bot, Dispatcher
from baleio.filters import Command
from baleio.fsm import FSMContext, State, StatesGroup
from baleio.types import Message


class Form(StatesGroup):
    name = State()
    age = State()


dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer("اسمت چیه؟")


@dp.message(Form.name)
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("چند سالته؟")


@dp.message(Form.age, lambda m: bool(m.text and m.text.isdigit()))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.update_data(age=int(message.text))
    await state.clear()
    await message.answer(
        f"ثبت شد ✅\nنام: {data['name']}\nسن: {data['age']}"
    )


@dp.message(Form.age)
async def bad_age(message: Message) -> None:
    await message.answer("لطفاً یک عدد وارد کن.")


async def main() -> None:
    bot = Bot(os.environ["BALE_TOKEN"])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
