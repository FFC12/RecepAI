## RecepAI Assistant - Based on ChatGPT-3.5

It is a Selenium bot that interacts with ChatGPT and answers the responses by utilizing Text-to-Speech (TTS) using espeak. I'm mainly focused on English and Turkish (my native language) but you can use it with any language that ChatGPT supports.

Also, you can use the microphone to talk with the bot. It uses Whisper to convert speech to text.  (voice-mode)

**Attention:** This is an educational project for me. I'm not responsible for any damage caused by this project. Use it at your own risk.

### Why do I use espeak?

Because, It's free and open source. Maybe the results are not good as Google's TTS but it's enough for me.

### Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
pip install -r requirements.txt --user
```

### Usage

```bash
python3.9 main.py
```

When you run the first time, you have to log in the ChatGPT. After that, you can use it without logging in again since it saves the Chrome options and cookies.

**Note:** You need to have `espeak` installed on your system. Additionally, you need to have Python version 3.9 installed. If you attempt to run it with Python 3.10 or 3.11, it will not work as the model is only compatible with PyTorch, which supports Python 3.9.
You need to have `chromedriver` installed on your system. And also, I developed and tested on Arch Linux. I don't know if it works on Windows or MacOS. 

### License

[MIT](https://choosealicense.com/licenses/mit/)

