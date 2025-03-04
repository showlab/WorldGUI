import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
from qwen_generation_utils import (
    HistoryType,
    make_context,
    decode_tokens,
    get_stop_words_ids,
    StopWordsLogitsProcessor,
)


def init_qwen_vl_chat(**kwargs):
    print("==Loading Qwen-VL-Chat model==")
    qwen_vl_chat = "Qwen/Qwen-VL-Chat"
    # qwen_vl_chat = kwargs.get("model",
    #                           "/Users/difei/.cache/huggingface/hub/models--Qwen--Qwen-VL-Chat/snapshots/0eecbfae27b784c8d5e69b1d497d3589874565a8")
    tokenizer = AutoTokenizer.from_pretrained(qwen_vl_chat, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(qwen_vl_chat, device_map="auto",
                                                 trust_remote_code=True,
                                                 fp16=True).eval()
    model.generation_config = GenerationConfig.from_pretrained(qwen_vl_chat, trust_remote_code=True)
    stop_words_ids = get_stop_words_ids('chatml', tokenizer)
    return {'model': model, 'tokenizer': tokenizer, 'stop_words_ids': stop_words_ids}


def run_qwen_vl_chat(**kwargs):
    query = kwargs.get("query")
    image_path = kwargs.get("image_path")
    batch_size = kwargs.get("batch_size", 16)

    model = kwargs.get("model")
    tokenizer = kwargs.get("tokenizer")
    stop_words_ids = kwargs.get("stop_words_ids")

    raw_text, context_tokens = tokenize(query, image_path, model, tokenizer)

    captions = []
    for i in range(0, len(context_tokens), batch_size):
        input_ids = torch.tensor(context_tokens[i:min(i + batch_size, len(context_tokens))]).to(model.device)
        outputs = model.generate(
            input_ids,
            stop_words_ids=stop_words_ids,
            return_dict_in_generate=False,
            do_sample=False,
        )

        # decode the output
        for op in outputs:
            caption = decode_tokens(
                op,
                tokenizer,
                raw_text_len=len(raw_text[0]),
                context_length=len(context_tokens[0]),  # the length are all the same for different frames
                chat_format='chatml',
                verbose=False,
                errors='replace'
            )
            captions.append(caption)

    return captions


def tokenize(text_query, image_path, model, tokenizer):
    if type(text_query) is str:
        text_query = [text_query]

    if type(image_path) is not list:
        image_path = [image_path]

    context_tokens_frames = []
    raw_text_frames = []
    query_list = []
    if len(text_query) != len(image_path):
        for t_q in text_query:
            for im_path in image_path:
                query_list.append(tokenizer.from_list_format([{'image': im_path, 'text': t_q}]))
    else:
        for ix in range(len(text_query)):
            query_list.append(tokenizer.from_list_format([{'image': image_path[ix], 'text': text_query[ix]}]))

    for query in query_list:
        raw_text, context_tokens = make_context(
            tokenizer,
            query,
            history=[],
            system="You are a helpful assistant.",
            max_window_size=model.generation_config.max_window_size,
            chat_format="chatml")
        context_tokens_frames.append(context_tokens)
        raw_text_frames.append(raw_text)

    return raw_text_frames, context_tokens_frames