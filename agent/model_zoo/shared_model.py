import os
import sys
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
print(os.sys.path)
from qwen import init_qwen_vl_chat, run_qwen_vl_chat

class SharedModel:
    _instances = {}

    def __new__(cls, model_name, **kwargs):
        if model_name not in cls._instances:
            instance = super(SharedModel, cls).__new__(cls)
            instance.model_dict = cls.initialize_model(model_name)
            cls._instances[model_name] = instance
        return cls._instances[model_name]

    @classmethod
    def initialize_model(cls, model_name, **kwargs):
        if model_name == 'groundingdino':
            return cls.init_groundingdino(**kwargs)
        elif model_name == 'qwen_vl_chat':
            return init_qwen_vl_chat(**kwargs)
        elif model_name == 'whisper':
            return cls.init_whisper(**kwargs)
        elif model_name == 'sam':
            return cls.init_segment_anything(**kwargs)
        elif model_name == 'ofa':
            return cls.init_ofa(**kwargs)
        elif model_name == 'promptcap':
            return cls.init_promptcap(**kwargs)
        elif model_name == 'instruct_blip':
            return cls.init_instruct_blip(**kwargs)
        elif model_name == 'blip_2':
            return cls.init_blip2(**kwargs)
        elif model_name == 'yolov8':
            return cls.init_yolov8(**kwargs)
        else:
            raise NotImplementedError(f"Model {model_name} not implemented. Supported models: "
                                      f"groundingdino, qwen-vl-chat, whisper, sam, ofa, promptcap, instruct_blip, blip_2")

    @classmethod
    def run_model(cls, model_name, **kwargs):
        if model_name == 'groundingdino':
            raise NotImplementedError
        elif model_name == 'qwen_vl_chat':
            model_dict = cls._instances[model_name].model_dict
            kwargs.update(model_dict)
            return run_qwen_vl_chat(**kwargs)
        elif model_name == 'whisper':
            raise NotImplementedError
        elif model_name == 'sam':
            raise NotImplementedError
        elif model_name == 'ofa':
            raise NotImplementedError
        elif model_name == 'promptcap':
            raise NotImplementedError
        elif model_name == 'instruct_blip':
            raise NotImplementedError
        elif model_name == 'blip_2':
            raise NotImplementedError
        else:
            raise NotImplementedError(f"Model {model_name} not implemented. Supported models: "
                                      f"groundingdino, qwen-vl-chat, whisper, sam, ofa, promptcap, instruct_blip, blip_2")

    @classmethod
    def init_groundingdino(cls, **kwargs):
        print(f"==Loading GroundingDINO model==")
        from groundingdino.models import build_model
        from groundingdino.util.slconfig import SLConfig
        from groundingdino.util.utils import clean_state_dict
        from groundingdino.util.inference import annotate, load_image, predict
        from huggingface_hub import hf_hub_download

        def load_model_hf(repo_id, filename, ckpt_config_filename, device='cpu'):
            cache_config_file = hf_hub_download(repo_id=repo_id, filename=ckpt_config_filename)

            args = SLConfig.fromfile(cache_config_file)
            model = build_model(args)
            args.device = device

            cache_file = hf_hub_download(repo_id=repo_id, filename=filename)
            checkpoint = torch.load(cache_file, map_location='cpu')
            log = model.load_state_dict(clean_state_dict(checkpoint['model']), strict=False)
            print(f"Model loaded from {cache_file} \n => {log}")
            model.eval()
            return model

        ckpt_repo_id = "ShilongLiu/GroundingDINO" if kwargs.get("ckpt_repo_id") is None else kwargs.get("ckpt_repo_id")
        ckpt_filename = "groundingdino_swint_ogc.pth" if kwargs.get("ckpt_filename") is None else kwargs.get(
            "ckpt_filename")
        ckpt_config_filename = "GroundingDINO_SwinT_OGC.cfg.py" if kwargs.get(
            "ckpt_config_filename") is None else kwargs.get("ckpt_config_filename")


        model = load_model_hf(ckpt_repo_id, ckpt_filename, ckpt_config_filename)
        return {'model': model}

    @classmethod
    def init_qwen_vl_chat(cls, **kwargs):
        print("==Loading Qwen-VL-Chat model==")
        from assistgui.model.qwen_vl.qwen_generation_utils import (
            HistoryType,
            make_context,
            decode_tokens,
            get_stop_words_ids,
            StopWordsLogitsProcessor,
        )

        # qwen_vl_chat = kwargs.get("model",
        #                           "/Users/difei/.cache/huggingface/hub/models--Qwen--Qwen-VL-Chat/snapshots/0eecbfae27b784c8d5e69b1d497d3589874565a8")
        qwen_vl_chat = "Qwen/Qwen-VL-Chat"
        tokenizer = AutoTokenizer.from_pretrained(qwen_vl_chat, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(qwen_vl_chat, device_map="auto",
                                                     trust_remote_code=True,
                                                     fp16=True).eval()
        model.generation_config = GenerationConfig.from_pretrained(qwen_vl_chat, trust_remote_code=True)
        stop_words_ids = get_stop_words_ids('chatml', tokenizer)
        return {'model': model, 'tokenizer': tokenizer, 'stop_words_ids': stop_words_ids}

    @classmethod
    def init_segment_anything(cls, **kwargs):
        from segment_anything import sam_model_registry
        from segment_anything import SamPredictor

        SAM_MODELS = {
            "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
            "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
            "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
        }

        sam_type = kwargs.get("sam_type", 'vit_h')
        ckpt_path = kwargs.get("ckpt_path", None)
        device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")

        if ckpt_path is None:
            print(f"==Loading SAM model {sam_type} from torch hub==")
            checkpoint_url = SAM_MODELS[sam_type]
            state_dict = torch.hub.load_state_dict_from_url(checkpoint_url)
            sam = sam_model_registry[sam_type]()
            sam.load_state_dict(state_dict, strict=True)
        else:
            print(f"==Loading SAM model {sam_type} from {ckpt_path}==")
            sam = sam_model_registry[sam_type](ckpt_path)

        sam.to(device=device)
        sam = SamPredictor(sam)

        return {'model': sam}

    @classmethod
    def init_whisper(cls, **kwargs):
        print("==Loading whisper model==")
        import whisper
        model = whisper.load_model("base")
        return {'model': model}

    @classmethod
    def init_ofa(cls, **kwargs):
        print("==Loading OFA model==")

        from fairseq import utils, tasks
        from fairseq import checkpoint_utils
        from tasks.mm_tasks.refcoco import RefcocoTask
        from models.ofa import OFAModel
        from PIL import Image
        from torchvision import transforms

        def load_ofa():
            # turn on cuda if GPU is available
            use_cuda = torch.cuda.is_available()

            # Register refcoco task
            tasks.register_task('refcoco', RefcocoTask)

            # use fp16 only when GPU is available
            use_fp16 = False

            # Load pretrained ckpt & config
            overrides = {"bpe_dir": "/Users/difei/workspace/assistgui/models/OFA/utils/BPE"}
            models, cfg, task = checkpoint_utils.load_model_ensemble_and_task(
                utils.split_paths('/Users/difei/workspace/assistgui/models/OFA/checkpoints/refcocog.pt'),
                arg_overrides=overrides
            )

            cfg.common.seed = 7
            cfg.generation.beam = 5
            cfg.generation.min_len = 4
            cfg.generation.max_len_a = 0
            cfg.generation.max_len_b = 4
            cfg.generation.no_repeat_ngram_size = 3

            # Fix seed for stochastic decoding
            if cfg.common.seed is not None and not cfg.generation.no_seed_provided:
                np.random.seed(cfg.common.seed)
                utils.set_torch_seed(cfg.common.seed)

            # Move models to GPU
            for model in models:
                model.eval()
                if use_fp16:
                    model.half()
                if use_cuda and not cfg.distributed_training.pipeline_model_parallel:
                    model.cuda()
                model.prepare_for_inference_(cfg)

            # Initialize generator
            generator = task.build_generator(models, cfg.generation)

            mean = [0.5, 0.5, 0.5]
            std = [0.5, 0.5, 0.5]

            patch_resize_transform = transforms.Compose([
                lambda image: image.convert("RGB"),
                transforms.Resize((cfg.task.patch_image_size, cfg.task.patch_image_size), interpolation=Image.BICUBIC),
                transforms.ToTensor(),
                transforms.Normalize(mean=mean, std=std),
            ])

            # Text preprocess
            bos_item = torch.LongTensor([task.src_dict.bos()])
            eos_item = torch.LongTensor([task.src_dict.eos()])
            pad_idx = task.src_dict.pad()

            def encode_text(text, length=None, append_bos=False, append_eos=False):
                s = task.tgt_dict.encode_line(
                    line=task.bpe.encode(text.lower()),
                    add_if_not_exist=False,
                    append_eos=False
                ).long()
                if length is not None:
                    s = s[:length]
                if append_bos:
                    s = torch.cat([bos_item, s])
                if append_eos:
                    s = torch.cat([s, eos_item])
                return s

            # Construct input for refcoco task
            patch_image_size = cfg.task.patch_image_size

            def construct_sample(image: Image, text: str):
                w, h = image.size
                w_resize_ratio = torch.tensor(patch_image_size / w).unsqueeze(0)
                h_resize_ratio = torch.tensor(patch_image_size / h).unsqueeze(0)
                patch_image = patch_resize_transform(image).unsqueeze(0)
                patch_mask = torch.tensor([True])
                src_text = encode_text(' which region does the text " {} " describe?'.format(text), append_bos=True,
                                       append_eos=True).unsqueeze(0)
                src_length = torch.LongTensor([s.ne(pad_idx).long().sum() for s in src_text])
                sample = {
                    "id": np.array(['42']),
                    "net_input": {
                        "src_tokens": src_text,
                        "src_lengths": src_length,
                        "patch_images": patch_image,
                        "patch_masks": patch_mask,
                    },
                    "w_resize_ratios": w_resize_ratio,
                    "h_resize_ratios": h_resize_ratio,
                    "region_coords": torch.randn(1, 4)
                }
                return sample

            # Function to turn FP32 to FP16
            def apply_half(t):
                if t.dtype is torch.float32:
                    return t.to(dtype=torch.half)
                return t

            return generator, construct_sample, task, models

        generator, processor, task, model = load_ofa()
        return {'generator': generator, 'processor': processor, 'task': task, 'model': model}

    def init_promptcap(self, **kwargs):
        print("==Loading promptcap model==")
        from promptcap import PromptCap
        model = PromptCap("vqascore/promptcap-coco-vqa")
        model = model.cuda()
        return {'model': model}

    def init_instruct_blip(self, **kwargs):
        print("==Loading instruct_blip model==")
        from lavis.models import load_model_and_preprocess
        gpu_id = kwargs.get("gpu_id", 0)
        model, vis_processors, _ = load_model_and_preprocess(name="blip2_vicuna_instruct",
                                                             model_type="vicuna7b",
                                                             is_eval=True,
                                                             device=f"cuda:{gpu_id}")
        return {'model': model, 'vis_processors': vis_processors}

    def init_blip2(self, **kwargs):
        print("==Loading blip2 model==")
        from transformers import Blip2Processor, Blip2ForConditionalGeneration
        model_name = "Salesforce/blip2-flan-t5-xl"
        processor = Blip2Processor.from_pretrained(model_name)
        model = Blip2ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)
        model = model.cuda()
        return {'model': model, 'processor': processor}

    def init_yolov8(self, **kwargs):
        print("==Loading yolov8 model==")
        from ultralytics import YOLO
        model_name = 'yolov8n-oiv7.pt'
        model = YOLO(model_name)
        return {'model': model}

    # TODO: add more models here
