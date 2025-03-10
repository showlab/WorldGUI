import os
from agent.utils.lmm.lmm_utils import encode_image, is_image_path

import anthropic

def run_claude_interleaved(prompt, llm, max_tokens=1000, temperature=0):

    client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

    image_media_type = "image/png"

    content = []

    if type(prompt) == list:
        for item in prompt:
            if is_image_path(item):
                # messages.append(upload_to_gemini(item, mime_type='image/jpeg')) # 2 times slow than base64 from simple test
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": encode_image(item)
                    }
                })
            else:
                content.append({"type": "text", "text": item})

    else:
        content.append({
            "type": "text",
            "text": prompt
        })



    try:
        response = client.messages.create(
            model=llm,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{
                "role": "user",
                "content": content}])

        text = response.content[0].text
        return text
    # return error message if the response is not successful
    except Exception as e:
        return e

if __name__ == '__main__':
    prompt = "hello, what is the name of APPLE Inc."
    llm = "claude-3-5-sonnet-20241022"
    response = run_claude_interleaved(prompt, llm)
    print(response)