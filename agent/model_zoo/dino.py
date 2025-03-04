import torch
from groundingdino.models import build_model
from groundingdino.util.slconfig import SLConfig
from groundingdino.util.utils import clean_state_dict
from huggingface_hub import hf_hub_download
from groundingdino.util.inference import annotate, load_image, predict


def init_groundingdino(**kwargs):
    print(f"==Loading GroundingDINO model==")

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

