import os
import fitz  # PyMuPDF
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Simple PDF Summarizer ---
def summarize_text(text, num_sentences=5):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    word_frequencies = {}
    for word in words:
        if word.isalpha() and word not in stop_words:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1

    sentences = sent_tokenize(text)
    sentence_scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in word_frequencies:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + word_frequencies[word]

    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = "\n- ".join(summary_sentences)
    return "Main points:\n- " + summary

# --- PDF Text Extractor ---
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# --- Handle PDF Uploads ---
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = "temp.pdf"
    await file.download_to_drive(file_path)
    await update.message.reply_text("📘 Chill Kiasi nikam⏳")

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        await update.message.reply_text("❌ Hii file haiwezi.")
        return

    summary = summarize_text(text)
    await update.message.reply_text(summary[:4000])  # Telegram message limit
    os.remove(file_path)

# --- Main Bot Setup ---
if __name__ == "__main__":
    TOKEN = "8000998534:AAFDjyrg4XecGZSwin58c4h5Nyq30UNDu9o"  # Paste your BotFather token here
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    print("🤖 Bot is running... send your PDF to it on Telegram!")
    app.run_polling()
