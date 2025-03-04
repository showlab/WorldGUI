import base64
import logging

from agent.utils.lmm.oai import run_gpt4o_interleaved
from agent.utils.lmm.gemini import run_gemini_interleaved
from agent.utils.lmm.claude import run_claude_interleaved

def run_lmm(prompt, lmm="gpt-4o-2024-08-06", max_tokens=1024, temperature=0, stop=None):
    log_prompt(prompt)
    
    # turn string prompt into list
    if isinstance(prompt, str):
        prompt = [prompt]
    elif isinstance(prompt, list):
        pass
    else:
        raise ValueError(f"Invalid prompt type: {type(prompt)}")
    
    if lmm.startswith("gpt-4o"): # gpt series

        if len(prompt) == 2:
            text_prompt, screenshot_path = prompt
            if isinstance(screenshot_path, list):
                prompt = [text_prompt] + screenshot_path
        else:
            pass

        out = run_gpt4o_interleaved(
            prompt, 
            lmm, 
            max_tokens, 
            temperature, 
            stop
        )
    elif lmm.startswith("gemini"): # gemini series

        out = run_gemini_interleaved(
            prompt, 
            lmm, 
            max_tokens,
            temperature, 
            stop
        )

    elif lmm.startswith("claude"):

        out = run_claude_interleaved(
            prompt, 
            lmm, 
            max_tokens,
            temperature
        )
    else:
        raise ValueError(f"Invalid lmm: {lmm}")
    logging.info(
        f"========Output for {lmm}=======\n{out}\n============================")
    return out

def log_prompt(prompt):
    if isinstance(prompt, str):
        prompt_display = [prompt]
    elif isinstance(prompt, list):
        prompt_display = [prompt[0]]

    # prompt_display = [prompt] if isinstance(prompt, str) else prompt
    prompt_display = "\n\n".join(prompt_display)
    logging.info(
        f"========Prompt=======\n{prompt_display}\n============================")
    