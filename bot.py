import logging
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, time

from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start_handler(bot, update):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text(
        "Hello from Python!\nPress /random to get random number")


def today_handler(bot, update):
    today = str(datetime.today()).split()[0]
    url = 'https://www.championat.com/stat/football/#' + today
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    html = BeautifulSoup(r.text, 'html.parser')
    [s.extract() for s in html('script')]
    tournaments = html.findAll("div", {"class": "seo-results__tournament"})
    print(tournaments)
    print(html.find("div", {"class": "seo-results"}))
    matches = html.find("div", {"class": "seo-results"}).findAll("ul")
    events = []
    for index, tournament in enumerate(tournaments):
        tournament_matches = []
        for match in matches[index].findAll("li"):
            tournament_matches.append({"title": match.a.text, "time": match.find(
                "span", {"class": "seo-results__item-date"}).text})
        events.append({"title": tournament.a.text,
                       "matches": tournament_matches})
    message = ""
    for event in events:
        message += event.get("title")
        for match in event.get("matches"):
            message += "\r\n{}. Начало: {}".format(
                match.get("title"), match.get("time"))
        message += "\r\n\r\n"
    update.message.reply_text(message)


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("today", today_handler))

    run(updater)
