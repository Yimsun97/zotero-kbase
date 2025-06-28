import json
import os
import shutil

import requests
from huggingface_hub import snapshot_download


def download_json(url):
    # 下载JSON文件
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    return response.json()


def download_and_modify_json(url, local_filename, modifications):
    if os.path.exists(local_filename):
        data = json.load(open(local_filename))
        config_version = data.get('config_version', '0.0.0')
        if config_version < '1.2.0':
            data = download_json(url)
    else:
        data = download_json(url)

    # 修改内容
    for key, value in modifications.items():
        data[key] = value

    # 保存修改后的内容
    with open(local_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':

    mineru_patterns = [
        # "models/Layout/LayoutLMv3/*",
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_hf_small_2503/*",
        "models/OCR/paddleocr_torch/*",
        # "models/TabRec/TableMaster/*",
        # "models/TabRec/StructEqTable/*",
    ]
    model_dir = snapshot_download('opendatalab/PDF-Extract-Kit-1.0', allow_patterns=mineru_patterns)

    layoutreader_pattern = [
        "*.json",
        "*.safetensors",
    ]
    layoutreader_model_dir = snapshot_download('hantian/layoutreader', allow_patterns=layoutreader_pattern)

    model_dir = model_dir + '/models'
    print(f'model_dir is: {model_dir}')
    print(f'layoutreader_model_dir is: {layoutreader_model_dir}')

    # Change magic-pdf.json
    from config import MINERU_DIR
    with open("magic-pdf-template.json", 'r', encoding='utf-8') as f:
        magic_pdf_config = json.load(f)
    magic_pdf_config['models-dir'] = MINERU_DIR + model_dir.split("huggingface")[-1]
    magic_pdf_config['layoutreader-model-dir'] = MINERU_DIR + layoutreader_model_dir.split("huggingface")[-1]

    print(f"magic_pdf_config['models-dir'] is: {magic_pdf_config['models-dir']}")
    print(f"magic_pdf_config['layoutreader-model-dir'] is: {magic_pdf_config['layoutreader-model-dir']}")

    # Save the modified magic-pdf.json
    with open(MINERU_DIR + "\\magic-pdf.json", 'w', encoding='utf-8') as f:
        json.dump(magic_pdf_config, f, ensure_ascii=False, indent=4)
    print(f"magic-pdf.json saved to {MINERU_DIR}\\magic-pdf.json")

    # Copy the models to the mineru directory
    if not os.path.exists(magic_pdf_config['models-dir']):
        os.makedirs(magic_pdf_config['models-dir'])
    if not os.path.exists(magic_pdf_config['layoutreader-model-dir']):
        os.makedirs(magic_pdf_config['layoutreader-model-dir'])
    shutil.copytree(model_dir, magic_pdf_config['models-dir'], dirs_exist_ok=True)
    shutil.copytree(layoutreader_model_dir, magic_pdf_config['layoutreader-model-dir'], dirs_exist_ok=True)
    print(f"Models copied to {magic_pdf_config['models-dir']}")
    print(f"LayoutReader models copied to {magic_pdf_config['layoutreader-model-dir']}")
