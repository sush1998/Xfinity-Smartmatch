

# google AI Studio function 
import base64
import os
import google.generativeai as genai
from google.genai import types
import json
import streamlit as st

def get_LLM_response(prompt, keywords='', api_key = "SUPER_SECRET_API_KEY"):

    
    api_key = st.secrets["AIzaSyAerG1bzf9EdiA_HfxnW1rA_PoeATo9G5c"] 

    with open('Xfinity_data.json', 'r') as file:
        xfinity_products = json.load(file)

    context = f"""
                    We have the following x-finity products under 4 categories as the following: {xfinity_products}. Users can be recommended a single 
                    service or a combination of them based on their input prompt. Based on the user prompt and some keywords, return a list of a total 
                    of three services or three combinations of services (in the same input format) you would deem to be the best fit for their needs. 
                    User prompt: {prompt} Keywords: {keywords}
        """


    def generate():
        client = genai.Client(
            api_key=os.environ.get(api_key),
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text = context
                    ),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="application/json",
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")


    llm_response = generate()
    return llm_response

a="i want a wifi plan"
output= get_LLM_response(a)
print(output)


