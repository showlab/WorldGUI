import os
import json
import glob
import copy
import re

import PIL.Image
import numpy as np

os.sys.path.append("../")

from agent.utils.lmm.run_lmm import run_lmm


def imagecentercrop(img, center, W, H):
    # W, H is the width and height of screenshot
    x, y = center

    half_w = W//2
    half_h = H//2

    left_y = np.max([0, y-half_h])
    left_x = np.max([0, x-half_w])

    right_y = np.min([H, y+half_h])
    right_x = np.min([W, x+half_w])

    
    img_crop = img.crop((left_x, left_y, right_x, right_y))
    
    return img_crop

def extract_plaintext(result):
    match = re.search(r"```plaintext\n\[\d+, \d+\]\n```", result, re.DOTALL)

    if match:
        extracted_text = match.group().strip()

        new_txt = ''
        for line in extracted_text.split("\n"):
            if not line.startswith('#'):
                new_txt += line.strip()
        extracted_text = new_txt
    else:
        extracted_text = ''
    return extracted_text
    


def extract_corr(result):

    inside_plaintext = re.search(r'```plaintext\n(.*?)\n```', result, re.DOTALL)

    print(inside_plaintext)
    if inside_plaintext:

        coordinates_text = inside_plaintext.group(1)

        match = re.findall(r"\[(\d+\.?\d*),\s*(\d+\.?\d*)\]", coordinates_text, re.DOTALL)

        print(match)
        if match:
            extracted_corr = [[int(float(item[0])), int(float(item[1]))] for item in match]
        else:
            extracted_corr = ''
        
    else:
        extracted_corr = ''
    
    return extracted_corr

def run_locateregion(LMM, software_name, current_task, gui_info, screenshot_path):
    text_prompt =  f'''You are very smart, I would like your assistance for Desktop GUI automation.

I will provide the software name, task details and the parsed gui information of screenshot.

The main objective is to locate the coordinate of the screenshot which helps the subtask to be executed successfully.

Software name: {software_name}

Information about Task:
Current Task: {current_task}

Parsed GUI Screenshot Info: [Note that: element format is "name [its position]", separate with comma], the position is the center of the element.
GUI Info: {gui_info}


The output format should be:

```plaintext
[x, y]
```

Note:
1) The text should be selected in the main pane, thus do not select the text in the left thumbnail.
2) When selecting the text, there maybe two candicates from left thumbnail and main pane, please omit the text in the left thumbnail.

# Remember to reason in comment if needed.
'''

    prompt = [text_prompt]

    response = run_lmm(prompt, lmm=LMM, max_tokens=1000, temperature=0)

    img_screen = PIL.Image.open(screenshot_path)
    W, H = img_screen.size

    ext_corr = extract_corr(response)

    if ext_corr == '':
        x, y = W//2, H//2
    elif isinstance(ext_corr, list):
        x, y = ext_corr[0]
    else:
        x, y = ext_corr


    croped_image = imagecentercrop(img_screen, [x, y], W, H)

    crop_screenshot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tmp_screenshot/tmp.png'))
    croped_image.save(crop_screenshot_path, quality=95)
    
    return crop_screenshot_path