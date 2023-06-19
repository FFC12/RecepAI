import os
import sys

import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time

import whisper

import sounddevice
from audio import record, audio_init


class Bot:
    def __init__(self):
        """
        Bot class
        """
        # set the options
        self.driver = None
        self.options = Options()

        # keep the user logged in
        self.options.add_argument('--user-data-dir=chrome-data')

    def start(self, noise_reduction=False):
        """
        This function starts the bot
        :param noise_reduction:
        :return:
        """

        # initialize the audio
        audio_init()

        # We use undetected_chromedriver to avoid the detection of the bot
        self.driver = uc.Chrome(headless=False, use_subprocess=False, options=self.options)
        self.driver.get('https://chat.openai.com')

        self._bot_loop()

    def _input_audio(self, noise_reduction=False):
        """
        This function records the audio and transcribes it using the whisper library
        :param noise_reduction:
        :return:
        """
        record(noise_reduction=noise_reduction)

        model = whisper.load_model('base')
        result = model.transcribe('temp.wav', fp16=False)

        return result['text'], result['language']

    def _bot_loop(self):
        """
        This function is the main loop of the bot

        How it works:
            1. It finds the prompt text area
            2. It asks the user to enter the prompt or record the prompt
            3. It sends the prompt to the prompt text area
            4. It clicks the send button
            5. It waits for the response
            6. It gets the response and prints it or reads it (if voice mode is on)
            7. It goes back to step 1

        :return:
        """
        try:
            # find all buttons on the page
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')

            # click if its text is 'Login in'
            for button in buttons:
                if button.text == 'Log in':
                    button.click()
                    break
        except WebDriverException:
            print('Already logged in')
            pass

        # wait for the login in manually
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.ID, 'prompt-textarea'))
        )

        responses = {}

        first_time = True
        voice_mode = True

        while True:
            # put a text in the prompt
            prompt = self.driver.find_element(By.ID, 'prompt-textarea')

            selected_language = ''
            if not first_time:
                if voice_mode:
                    while selected_language == '' or selected_language is None or 'tr' not in selected_language.lower() and 'en' not in selected_language.lower():
                        prompt_text, selected_language = self._input_audio()
                else:
                    if selected_language == '':
                        selected_language = input('Enter the language you want to use (tr/en): ')
                        if 'tr' in selected_language.lower():
                            selected_language = 'tr'
                        elif 'en' in selected_language.lower():
                            selected_language = 'en'
                        else:
                            selected_language = 'tr'
                            print('Invalid language. Default language is Turkish.')

                    prompt_text = input('Enter your prompt (Type \'exit\'): ')
            else:
                # Change this for your own language if you want to use this in your own language. Basicall, It tells
                # the ChatGPT how it should act (first prompt)
                prompt_text = 'Sen benim asistanım olarak çalışıyorsun. Bu rolün icabı bana yardımcı olman gerekiyor.' \
                              'Ayrıca sana yaratıcın kim dediğimde bunun "Fatih" olduğunu söylemelisin.' \
                              'Sana ismini sorduğumda kendini Recep olarak takdim et.' \
                              'Vereceğin cevaplar diyalog akışında sanki konuşuyormuşsun gibi olsun. Ayrıca kısa ve özet ' \
                              'cevaplar olsun.'

                selected_language = 'tr'

            if prompt_text is None or 'exit' in prompt_text.lower() or 'çıkış' in prompt_text.lower():
                if responses:
                    with open('responses.txt', 'w') as f:
                        for key, value in responses.items():
                            f.write(key + '\n')
                            f.write(value + '\n')
                self.driver.close()
                sys.exit(0)

            if 'sesli moda geç' in prompt_text.lower():
                voice_mode = True
                continue

            if 'yazılı moda geç' in prompt_text.lower():
                voice_mode = False
                continue

            # send the prompt
            prompt.send_keys(prompt_text)

            # wait for the response to be generated
            time.sleep(1)

            # find all buttons on the page
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')

            # click if its style is 'background-color: rgb(25, 195, 125); '
            for button in buttons:
                # print(f"{button.text} - {button.get_attribute('style')}")
                if 'background-color: rgb(25, 195, 125);' in button.get_attribute('style'):
                    button.click()
                    break

            # flag to check if the response is generated
            response_generated = False

            # wait for the response to be generated
            while True:
                # retreive buttons again and check it has a text 'Regenerate response'
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')

                for button in buttons:
                    try:
                        if button.text == 'Continue generating':
                            button.click()
                            continue
                        if button.text == 'Regenerate response':
                            response_generated = True
                            break
                    # Stalement exception is thrown if the button is not visible
                    except StaleElementReferenceException:
                        # print('Stalement exception')
                        pass
                    except WebDriverException:
                        # print('WebDriverException')
                        pass

                if response_generated:
                    break

                time.sleep(2)

            # get all elements with the class name which contains 'markdown'
            try:
                last_p_tags_count = 0
                text = ''

                while True:
                    divs = self.driver.find_elements(By.CLASS_NAME, 'markdown')

                    # get the last element
                    div = divs[-1]

                    # get the text from all p tags inside the div
                    p_tags = div.find_elements(By.TAG_NAME, 'p')

                    if len(p_tags) > last_p_tags_count:
                        for p_tag in p_tags[last_p_tags_count:]:
                            phrase = p_tag.text.replace('`', '').replace('**', '').replace('*', '').replace('"',
                                                                                                            '') + '\n'
                            text += phrase

                            if selected_language == 'tr':
                                os.system("espeak -v tr+f2 -s 150 \"" + phrase + '"' + ' > /dev/null 2>&1')
                            else:
                                os.system("espeak -v en+f2 -s 150 \"" + phrase + '"' + ' > /dev/null 2>&1')
                        last_p_tags_count = len(p_tags)
                        time.sleep(1)
                    else:
                        break
            except WebDriverException:
                print('Error while getting the div-s')
                sys.exit(1)

            responses[prompt_text] = text

            # print the text
            print(text)

            if first_time:
                first_time = False

        # save the responses to a file
        with open('responses.txt', 'w') as f:
            for key, value in responses.items():
                f.write("Question:" + key + '\n')
                f.write("Answer:" + value + '\n')

        self.driver.close()












