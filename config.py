"""
Contains all the configuration variables 
"""
OPENAI_API_KEY = "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"
LOW_API_CONSUMPTION_MODE = True
MAX_TOKENS = 100

API_SAVER = True
NUMBER_OF_POINTS = 15   

SUMMARY_LENGTH_SHORT = 60
SUMMARY_LENGTH_LONG = 250

TEMPERATURE_LOW = 0.5
TEMPERATURE_MEDIUM = 0.75
TEMPERATURE_HIGH = 1.5
TEMPERATURE = TEMPERATURE_MEDIUM

UNDERLINE_BOLD_FLAG = True
MODEL = "text-davinci-003"

PROMPT_SUMMARY = "Generate summary from the following text:\n\n"
PROMPT_MAJOR_POINTS = "Generate major points from the following text, split by newlines, one point size is aprox 10 to 20 words:\n\n"
PROMPT_UNDERLINE_BOLD = "Underline the important points in the text and make them bold, using <u> </u> and <b> </b>.\n\n"