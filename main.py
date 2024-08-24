import numpy as np
import pandas as pd
from googletrans import Translator
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import re

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

openai.api_key = 'sk-proj-bwtcrL3ycaeZiAn4vF4tT3BlbkFJ2zcGxe0lD6c37lVROmqq'

#'sk-proj-lMr1nrrc3lbsMzNzGXDJT3BlbkFJH4yoUP7QVAeBh8YdLvDE'

# Hàm để gửi câu hỏi tới ChatGPT và nhận phản hồi
def ask_gpt(context, prompt):
    content = f"""Answer the following question: {prompt} and put the answer after "Answer: ", 
    if the question is incorrect in spelling or grammar, correct it and put it after: "You mean: \n"."""
    context += [{
        "role": "user",
        "content": content
    }]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Hoặc "gpt-4" nếu bạn muốn sử dụng GPT-4
        #messages=[
        #    {"role": "system", "content": "You are a helpful assistant."},
        #    {"role": "user", "content": prompt},
        #],
        messages=context,
        max_tokens=150,
        temperature=0.7,
    )

    return response['choices'][0]['message']['content'].strip()

# Hàm để dịch phản hồi từ tiếng Anh sang tiếng Việt
#def translate_to_vietnamese(text):
#    try:
#        translator = Translator()
#        translated = translator.translate(text, src='en', dest='vi')
#
#        return translated.text
#    except Exception as e:
#        print(f"Error: {e}")
#        return None

def extract_substring(text, pattern):
    # Tìm chuỗi con khớp với pattern
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return None

def remove_special_characters(text):
    # Sử dụng regex để giữ lại số, chữ cái và khoảng trắng
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return cleaned_text

# Hàm chính của trợ lý ảo
def virtual_assistant(context, prompt):
    
    # Nhận phản hồi từ ChatGPT
    response = ask_gpt(context, prompt)
    print(response)
    result = ''
    pattern1 = r"you mean:\s*(.*?)\n"
    correctTencent =  extract_substring(response, pattern1)
    if (correctTencent):
        text = remove_special_characters(correctTencent)
        print('here::::::::')
        print(text)
        if (text.lower() != prompt.lower()):
            result += f"you mean: {correctTencent} \n"
    
    pattern2 = r"answer:\s*(.*?)\s*(?=\n|$)"
    answer = extract_substring(response, pattern2)
    
    result += answer
    # Dịch phản hồi sang tiếng Việt
    #translated_response = translate_to_vietnamese(response)
    #print(f"Response in Vietnamese: {translated_response}")
    
    return result

@app.route('/api/assistant', methods=['POST'])
def main():
    data = request.get_json()
    # Ví dụ sử dụng
    prompt = data.get('prompt')
    context = data.get('context')
    translated_response = virtual_assistant(context, prompt)

    return jsonify({"result": translated_response}), 200

if __name__ == "__main__":
    app.run(debug=True)
