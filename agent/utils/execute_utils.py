import re


def post_process_gui_code(code, software_name=None):

    def extract_python_code(input_string):
        # Regular expression to extract content from '```python ... ```'
        pattern = r'```python(.*?)```'
        # Extract content
        matches = re.findall(pattern, input_string, re.DOTALL)  # re.DOTALL allows '.' to match newlines as well
        # Return the first match if exists, else original
        return matches[0].strip() if matches else input_string

    if code != "":
        code = extract_python_code(code)
        out = ["from pyautogui import *", "from time import sleep"]

        for line in code.split("\n"):
            if "```" in line:
                continue
            if "#" not in line[:1] and line and "update_gui()" not in line:
                out.append(line)

        out = "\n".join(out)
    else:
        out = ""
    return out
