import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip, ColorClip, CompositeVideoClip

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token to'g'ridan-to'g'ri biriktirildi
BOT_TOKEN = "8809603921:AAGnil80NGUb93pQoAzVl9DlalnG6V6oUdY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Menga ixtiyoriy matn yuboring.\n"
        "Men uni o'zbekcha ovozlashtirib, video ko'rinishida tayyorlab beraman."
    )

def generate_video_process(text: str, user_id: int) -> str:
    """Videoni qayta ishlash va xatolarsiz yaratish funksiyasi"""
    audio_path = f"audio_{user_id}.mp3"
    video_path = f"video_{user_id}.mp4"

    audio_clip = None
    final_video = None

    try:
        # 1. Matnni audio ovozga aylantirish
        tts = gTTS(text=text, lang='uz')
        tts.save(audio_path)

        # 2. Audio davomiyligini tekshirish
        audio_clip = AudioFileClip(audio_path)
        duration = max(audio_clip.duration, 2.0)

        # 3. Vertikal orqa fon yaratish (1080x1920 - Reels/TikTok)
        background = ColorClip(size=(1080, 1920), color=(20, 20, 30), duration=duration)

        # 4. Matn o'lchami va sig'imini moslash
        txt_clip = TextClip(
            text,
            fontsize=44,
            color='white',
            font='DejaVu-Sans-Bold',
            method='caption',
            size=(900, None)
        ).set_duration(duration).set_position('center')

        # 5. Audio va videoni birlashtirish
        final_video = CompositeVideoClip([background, txt_clip]).set_audio(audio_clip)

        # 6. Faylni saqlash
        final_video.write_videofile(
            video_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )

        return video_path

    finally:
        # Xotira va vaqtinchalik fayllarni tozalash
        if audio_clip:
            audio_clip.close()
        if final_video:
            final_video.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.message.from_user.id

    # Cheklovlar
    if not user_text or len(user_text.strip()) < 3:
        await update.message.reply_text("Iltimos, kamida 3 ta harfdan iborat matn yuboring.")
        return

    if len(user_text) > 500:
        await update.message.reply_text("Matn juda uzun. Iltimos, 500 ta belgidan oshmaydigan matn yuboring.")
        return

    status_msg = await update.message.reply_text("⏳ Video tayyorlanmoqda, kuting...")

    video_file_path = None
    try:
        # Asinxron ravishda render qilish
        loop = asyncio.get_running_loop()
        video_file_path = await loop.run_in_executor(None, generate_video_process, user_text, user_id)

        # Videoni foydalanuvchiga yuborish
        with open(video_file_path, 'rb') as video:
            await update.message.reply_video(
                video=video,
                caption=f"🎬 **Video tayyor!**\n\n💬 Matn: {user_text}"
            )

    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await update.message.reply_text("❌ Videoni yaratishda xatolik yuz berdi. Qaytadan urinib ko'ring.")

    finally:
        # Vaqtinchalik videoni o'chirish
        if video_file_path and os.path.exists(video_file_path):
            os.remove(video_file_path)
        try:
            await status_msg.delete()
        except Exception:
            pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
