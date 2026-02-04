import nest_asyncio
nest_asyncio.apply()

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from deep_translator import GoogleTranslator

# ================== TOKEN ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ================== FSM ==================
class TranslateState(StatesGroup):
    waiting_text = State()

# ================== BOT ==================
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ================== TILLAR ==================
LANGS = {
    "uz": "🇺🇿 Uzbek",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Russian",
    "tr": "🇹🇷 Turkish"
}

# ================== KLAVIATURALAR ==================
def pair_keyboard(src, dst):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{LANGS[src]} ➡️ {LANGS[dst]}",
                    callback_data="swap"
                )
            ],
            [
                InlineKeyboardButton(text="⬅️ Chap til", callback_data="set_src"),
                InlineKeyboardButton(text="O‘ng til ➡️", callback_data="set_dst")
            ]
        ]
    )

def lang_keyboard(prefix):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=name, callback_data=f"{prefix}_{code}")
            ] for code, name in LANGS.items()
        ]
    )

# ================== /start ==================
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(src="uz", dst="en")
    await state.set_state(TranslateState.waiting_text)

    await message.answer(
        "🌍 Tarjima bot (Google Translate uslubi)",
        reply_markup=pair_keyboard("uz", "en")
    )

# ================== SWAP ==================
@dp.callback_query(F.data == "swap")
async def swap_langs(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    src, dst = data["src"], data["dst"]
    src, dst = dst, src

    await state.update_data(src=src, dst=dst)
    await cb.message.edit_reply_markup(reply_markup=pair_keyboard(src, dst))
    await cb.answer()

# ================== TIL TANLASH ==================
@dp.callback_query(F.data == "set_src")
async def choose_src(cb: CallbackQuery):
    await cb.message.answer(text="⬅️ Chap tilni tanlang:", reply_markup=lang_keyboard("src"))
    await cb.answer()

@dp.callback_query(F.data == "set_dst")
async def choose_dst(cb: CallbackQuery):
    await cb.message.answer(text="O‘ng tilni tanlang ➡️", reply_markup=lang_keyboard("dst"))
    await cb.answer()

@dp.callback_query(F.data.startswith("src_"))
async def set_src(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    data = await state.get_data()
    await state.update_data(src=lang)
    await cb.message.answer(
        "✅ Chap til o‘zgartirildi",
        reply_markup=pair_keyboard(lang, data["dst"])
    )
    await cb.answer()

@dp.callback_query(F.data.startswith("dst_"))
async def set_dst(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    data = await state.get_data()
    await state.update_data(dst=lang)
    await cb.message.answer(
        "✅ O‘ng til o‘zgartirildi",
        reply_markup=pair_keyboard(data["src"], lang)
    )
    await cb.answer()

# ================== TARJIMA ==================
@dp.message(TranslateState.waiting_text)
async def translate(message: Message, state: FSMContext):
    data = await state.get_data()
    src, dst = data["src"], data["dst"]

    try:
        result = GoogleTranslator(source=src, target=dst).translate(message.text)
        await message.answer(f"📌 Tarjima:\n\n{result}")
    except:
        await message.answer("❌ Tarjima xatosi")

# ================== START () ==================
async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
