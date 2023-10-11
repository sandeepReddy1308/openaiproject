# API to summarize content of a given URL using ChatGPT API.
import requests
from bs4 import BeautifulSoup
import openai
from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import config

# Configuration variables
OPENAI_API_KEY = config.OPENAI_API_KEY
MODEL = config.MODEL

PROMPT_MAJOR_POINTS = config.PROMPT_MAJOR_POINTS
PROMPT_SUMMARY = config.PROMPT_SUMMARY

UNDERLINE_BOLD_FLAG = config.UNDERLINE_BOLD_FLAG

PROMPT_UNDERLINE_BOLD = config.PROMPT_UNDERLINE_BOLD

TEMPERATURE_LOW = config.TEMPERATURE_LOW
TEMPERATURE_MEDIUM = config.TEMPERATURE_MEDIUM
TEMPERATURE_HIGH = config.TEMPERATURE_HIGH
TEMPERATURE = config.TEMPERATURE

SUMMARY_LENGTH = config.SUMMARY_LENGTH_MEDIUM
MAX_TOKENS = 200
SUMMARY_LENGTH_SHORT = config.SUMMARY_LENGTH_SHORT
SUMMARY_LENGTH_MEDIUM = config.SUMMARY_LENGTH_MEDIUM
SUMMARY_LENGTH_LONG = config.SUMMARY_LENGTH_LONG

NUMBER_OF_POINTS = config.NUMBER_OF_POINTS

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key here
openai.api_key = OPENAI_API_KEY

# Function to fetch content from a URL
def fetch_content(url):
    response = requests.get(url)
    return response.text
    if response.status_code == 200:
        return response.text
    return None

# Function to clean HTML content and get text
def clean_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()

def text_davinci_003_call(prompt):
    print (prompt)
    return openai.Completion.create(
        model=MODEL,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

# cost in RS
def API_call_cost(model, max_tokens, temperature):
    usd = (max_tokens / 1000) * 0.06
    rs = usd * 75
    return rs

# Function to generate major points from text using ChatGPT
def generate_major_points(text):
    prompt = prompt_generator(text, "points")
    response = text_davinci_003_call(prompt)
    summary = response.choices[0].text.strip()
    bullet_points = summary.split("\n")
    bullet_points = [point.strip() for point in bullet_points if point.strip() != ""]
    
    # Add numbers to each bullet point
    bullet_points = bullet_points[:NUMBER_OF_POINTS]

    return bullet_points

# Function to generate summary from text using ChatGPT
def generate_summary(text):
    prompt = prompt_generator(text, "summary")
    response = text_davinci_003_call(prompt)
    summary = response.choices[0].text.strip()
    return summary

def prompt_generator(text, prompt_type):
    if prompt_type == "summary":
        prompt = PROMPT_SUMMARY
        if UNDERLINE_BOLD_FLAG:
            prompt = PROMPT_UNDERLINE_BOLD
            
    elif prompt_type == "points":
        prompt = PROMPT_MAJOR_POINTS
        if UNDERLINE_BOLD_FLAG:
            prompt = PROMPT_UNDERLINE_BOLD
        prompt = prompt + text
        
    return prompt

# Function to remove blank lines from text
def remove_blank_lines(input_text):
    lines = input_text.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != ""]
    return '\n'.join(non_empty_lines)

# Function to split text into smaller chunks
def split_into_chunks(text, chunk_size):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size
    return chunks

# Function to generate output for short text
def generate_output_for_short_text(text, output_type):
    if output_type == "summary":
        return generate_summary(text)
    elif output_type == "points":
        return generate_major_points(text)

# Function to process large content by chunking and generating output
def process_large_content(clean_text, output_type):
    chunked_text = split_into_chunks(clean_text, 4090)  # Some buffer for safety
    generated_output = ""

    for chunk in chunked_text:
        chunk_output = generate_output_for_short_text(chunk, output_type)
        generated_output += str(chunk_output) + " "
        
    return generated_output

@app.route('/api', methods=['POST'])
def api_call():
    data = request.get_json()
    url = data.get("url")
    output_type = data.get("type", "summary")
    
    # set the temperature
    temperature = data.get("temperature", None)
    if temperature is None:
        temperature = TEMPERATURE
    elif temperature == "low":
        temperature = TEMPERATURE_LOW
    elif temperature == "medium":
        temperature = TEMPERATURE_MEDIUM
    elif temperature == "high":
        temperature = TEMPERATURE_HIGH

      # set the model token length
    summary_length = data.get("summary_length", SUMMARY_LENGTH)
    if summary_length == "short":
        summary_length = SUMMARY_LENGTH_SHORT
    elif summary_length == "long":
        summary_length = SUMMARY_LENGTH_LONG
    MAX_TOKENS = summary_length
    
    
    number_of_points = data.get("number_of_points", NUMBER_OF_POINTS)
    prompt_summary = data.get("prompt_summary", PROMPT_SUMMARY)
    prompt_major_points = data.get("prompt_major_points", PROMPT_MAJOR_POINTS)

    underline_bold_flag = data.get("underline_bold_flag", None)
    if underline_bold_flag is None:
        underline_bold_flag = UNDERLINE_BOLD_FLAG
              
    if url is None:
        return jsonify({"error": "URL not provided"}), 400
    
    content = fetch_content(url)
    if content is None:
        return jsonify({"error": "Failed to retrieve the content"}), 500

    clean_text = clean_html(content)
    clean_text = remove_blank_lines(clean_text)

    # LOW_API_CONSUMPTION is is TRUE, then we will limit the text to 4096 characters
    clean_text = clean_text[:4096]
    
    # when text is too large
    if len(clean_text) > 4096:
        generated_output = process_large_content(clean_text, output_type)
        return jsonify({output_type: generated_output})

    output = generate_output_for_short_text(clean_text, output_type)

if __name__ == '__main__':
    app.run(debug=True)
