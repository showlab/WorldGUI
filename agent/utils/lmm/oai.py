
import os
import requests

from agent.utils.lmm.lmm_utils import is_image_path, encode_image
from openai import OpenAI


def run_gpt4o_interleaved(prompt, llm, max_tokens=1000, temperature=0, stop=None):

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return {"error": "API key not found in environment variables."}
    
    messages = []
    content = []
    messages.append({"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"})
    if isinstance(prompt, list):
        for item in prompt:
            if is_image_path(item):  # Ensure you define this function
                base64_image = encode_image(item)  # Ensure you define this function
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                })
            else:
                content.append({
                    "type": "text",
                    "text": item
                })
    else:
        content = [{
            "type": "text",
            "text": prompt
        }]

    messages.append({
        "role": "user",
        "content": content
    })

    try:
        # API call
        response = client.chat.completions.create(
            model=llm,
            messages=messages,
            temperature=temperature,
        )
        
        # Process the response
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

