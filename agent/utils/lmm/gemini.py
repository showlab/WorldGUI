import os
from agent.utils.lmm.lmm_utils import encode_image, is_image_path

import google.generativeai as genai

def run_gemini_interleaved(prompt, llm, max_tokens=1000, temperature=0, stop=None):

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Create the model
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": max_tokens,
        "stop_sequences": stop,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name=llm,
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    messages = []

    if type(prompt) == list:
        for item in prompt:
            if is_image_path(item):
                # messages.append(upload_to_gemini(item, mime_type='image/jpeg')) # 2 times slow than base64 from simple test
                messages.append({"data": encode_image(item), "mime_type": "image/png"}
               )
            else:
                messages.append(item)

    else:
        messages.append(prompt)

    try:
        response = model.generate_content(
            messages, generation_config=generation_config)
        text = response.text
        return text
    # return error message if the response is not successful
    except Exception as e:
        return e
    

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file