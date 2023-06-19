from bot import Bot

if __name__ == '__main__':
    # create the bot
    bot = Bot()

    # if you want to use noise reduction, set the parameter to True
    # it takes more time to process the audio but it's more accurate
    bot.start(noise_reduction=False)
