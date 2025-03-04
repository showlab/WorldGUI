import cv2
import numpy as np
import time
import os
import re
import glob
import json
from agent.gui_parser.utils import multivalue_image


def non_max_suppression(boxes, overlap_thresh, scores):
    boxes = np.array(boxes)

    if len(boxes) == 0:
        return [], []

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []

    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(scores)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

    return boxes[pick].astype("int"), pick


def load_icon_templates(asset_folder, software_name="premiere", panel_name=None, icon_type="icons"):
    # 初始化空的路径列表
    if panel_name:
        template_folder = f'{asset_folder}/{software_name}/{panel_name}/{icon_type}'
    else:
        template_folder = f'{asset_folder}/{software_name}'

    # print("loading icon templates... from ", template_folder)
    icon_path = glob.glob(f'{template_folder}/**/*.png', recursive=True)
    # print("found ", len(icon_path), " icons")

    icons = []
    for template_path in icon_path:
        # 读取模板图片
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        # 获取模板图片的名称
        # print(template_path)
        name = re.search(r'[^\\/]+(?=\.\w+$)', template_path).group(0)
        name = re.sub(r'^\d+_', '', name) + "_icon"
        # print(name)

        # 将模板图片的名称和图片加入到列表中
        icons.append({'name': name, 'template': template, 'path': template_path})
    return icons


def multi_scale_template_matching(image, template, threshold=0.9, scales=[i / 10.0 for i in range(5, 2, 21)]):
    all_matches = []
    all_score = []
    all_scale = 1
    for scale in scales:
        # resized_template = cv2.resize(template, (int(template.shape[1] * scale), int(template.shape[0] * scale)))

        resized_template = cv2.resize(template, (
        int(template.shape[1] * scale * all_scale), int(template.shape[0] * scale * all_scale)))
        image = cv2.resize(image, (int(image.shape[1] * all_scale), int(image.shape[0] * all_scale)))

        if resized_template.shape[0] > image.shape[0] or resized_template.shape[1] > image.shape[1]:
            continue

        result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)

        # _, max_val, _, max_loc = cv2.minMaxLoc(result)

        locs = np.where(result >= threshold)
        for pt in zip(*locs[::-1]):  # Switch cols and rows
            all_matches.append((pt, scale))
            score_at_pt = result[pt[1], pt[0]]
            all_score.append(score_at_pt)

    return all_matches, all_score


def get_best_matching_scale(image, template, threshold=0.8, scales=None):
    if scales is None:
        scales = [i / 10.0 for i in range(5, 2, 21)]

    all_matches = []
    max_score = -1
    best_scale = 1
    best_location = None
    for scale in scales:
        resized_template = cv2.resize(template, (int(template.shape[1] * scale), int(template.shape[0] * scale)))

        if resized_template.shape[0] > image.shape[0] or resized_template.shape[1] > image.shape[1]:
            continue

        result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > max_score:
            max_score = max_val
            best_scale = scale
            best_location = max_loc

    return best_scale


def preprocess_image(img, software_name):
    # 转换为灰度
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化
    # _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    if software_name in ["premiere", "after effect"]:
        threshold = 60
    elif software_name in ["word", "excel", "powerpoint"]:
        threshold = 190
    else:
        threshold = 130

    binary, saved_path = multivalue_image(
        img,
        mode='None',  # 或者您可以用其他任何字符串，这里不重要
        thresholds=[threshold],  # 一个单一的阈值
        interval_values=[0, 255],  # 两个区间值
        save=False,  # 是否保存图像
        cache_folder='./.cache'  # 缓存文件夹
    )
    return binary

# detect blue and non-blue area for PR and AE
def divide_activated_area(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the scope of blue
    lower_blue = np.array([105, 100, 100])
    upper_blue = np.array([130, 255, 255])

    # Creates a mask that sets parts within a specified color range to white and other parts to black
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Perform a bitwise AND operation on the original image and the mask to extract the blue part
    blue = cv2.bitwise_and(image, image, mask=mask)

    non_blue_part = cv2.bitwise_not(image, image, mask)
    
    
    return blue, non_blue_part


def detect_button_pr_ae(image, software_name="premiere", panel_name=None, asset_folder="./assistgui/asset", icon_type=None, threshold=0.78):
    # image的格式 cv2.imread(image_path, cv2.IMREAD_COLOR)   最理想情况是1080p的图片否则质量不会太好
    # button_folder button 库位置
    # threshold 模版匹配的阈值， 越高越准确，但是button数目有时会变少

    # image_path = "extracted_img/frame9725.jpg"
    # image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    blue_image,  non_blue_image = divide_activated_area(image)
    non_blue_image = preprocess_image(non_blue_image, software_name)
    if 'Accessory' in software_name:
        panel_name = 'Accessory'
    templates = load_icon_templates(asset_folder, software_name, panel_name)

    all_boxes, all_scores, labels = [], [], []
    # count = 0
    for i, template in enumerate(templates):
        icon_name = template['name']
        icon_template = template['template']
        icon_template_blue, icon_template_non_blue = divide_activated_area(icon_template)
        icon_template_non_blue = preprocess_image(icon_template_non_blue, software_name)
        
        # find the best scale for the template at the first iteration
        if i == 0:
            best_scale_blue = 1
            if "activated" in icon_name:
                best_scale_blue = get_best_matching_scale(blue_image, icon_template_blue)
            best_scale_non_blue = get_best_matching_scale(non_blue_image, icon_template_non_blue)
            
        if "activated" in icon_name:
            matches_blue, scores_blue = multi_scale_template_matching(blue_image, icon_template_blue, threshold=threshold,
                                                        scales=[best_scale_blue])

            icon_width = icon_template_blue.shape[1]
            icon_height = icon_template_blue.shape[0]
            for match, score in zip(matches_blue, scores_blue):
                (pt_x, pt_y), scale = match

                end_x = int(pt_x + icon_width * scale)
                end_y = int(pt_y + icon_height * scale)

                # 保存所有的框到all_boxes
                all_boxes.append([pt_x, pt_y, end_x, end_y])
                all_scores.append(score)
                labels.append(icon_name)
        
        if "activated" not in icon_name:
            matches_non_blue, scores_non_blue = multi_scale_template_matching(non_blue_image, icon_template_non_blue, threshold=threshold,
                                                            scales=[best_scale_non_blue])
            icon_width = icon_template_non_blue.shape[1]
            icon_height = icon_template_non_blue.shape[0]
            for match, score in zip(matches_non_blue, scores_non_blue):
                (pt_x, pt_y), scale = match

                end_x = int(pt_x + icon_width * scale)
                end_y = int(pt_y + icon_height * scale)

                # 保存所有的框到all_boxes
                all_boxes.append([pt_x, pt_y, end_x, end_y])
                all_scores.append(score)
                labels.append(icon_name)

    # print(threshold, labels)
    # 应用NMS bbox 去重
    nms_boxes, pick = non_max_suppression(all_boxes, 0.5, all_scores)
    labels = [labels[i] for i in pick]

    button_items = []
    for ix, box in enumerate(nms_boxes):
        if 'scroll bar' in labels[ix] or 'effects submenu' in labels[ix]:
            item = {"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click', 'dragTo']}
        else:
            item = {"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click']}
        button_items.append(item)

    # button_items = [{"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click']} for ix, box in enumerate(nms_boxes)]

    return button_items

def detect_button(image, software_name="premiere", panel_name=None, asset_folder="./assistgui/asset", icon_type=None, threshold=0.78):
    # image的格式 cv2.imread(image_path, cv2.IMREAD_COLOR)   最理想情况是1080p的图片否则质量不会太好
    # button_folder button 库位置
    # threshold 模版匹配的阈值， 越高越准确，但是button数目有时会变少

    # image_path = "extracted_img/frame9725.jpg"
    # image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    binary_image = preprocess_image(image, software_name)
    templates = load_icon_templates(asset_folder, software_name, panel_name)

    all_boxes, all_scores, labels = [], [], []
    for i, template in enumerate(templates):
        icon_name = template['name']
        icon_template = template['template']
        icon_template_binary = preprocess_image(icon_template, software_name)

        # find the best scale for the template at the first iteration
        if i == 0:
            best_scale = get_best_matching_scale(binary_image, icon_template_binary)

        matches, scores = multi_scale_template_matching(binary_image, icon_template_binary, threshold=threshold,
                                                        scales=[best_scale])

        icon_width = icon_template_binary.shape[1]
        icon_height = icon_template_binary.shape[0]
        for match, score in zip(matches, scores):
            (pt_x, pt_y), scale = match

            end_x = int(pt_x + icon_width * scale)
            end_y = int(pt_y + icon_height * scale)

            # 保存所有的框到all_boxes
            all_boxes.append([pt_x, pt_y, end_x, end_y])
            all_scores.append(score)
            labels.append(icon_name)

    # # 应用NMS bbox 去重
    nms_boxes, pick = non_max_suppression(all_boxes, 0.5, all_scores)
    labels = [labels[i] for i in pick]

    button_items = []
    for ix, box in enumerate(nms_boxes):
        if 'scroll bar' in labels[ix] or 'effects submenu' in labels[ix]:
            item = {"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click', 'dragTo']}
        else:
            item = {"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click']}
        button_items.append(item)

    # button_items = [{"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click']} for ix, box in enumerate(nms_boxes)]

    return button_items


def process_image_4_new(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 定义两个阈值
    # threshold1 = 50
    # threshold2 = 70
    # threshold3 = 140

    threshold1 = 50
    threshold2 = 100
    threshold3 = 150

    # 进行三值化
    # 小于threshold1的像素设为0（黑色）
    # 大于threshold2的像素设为255（白色）
    # 位于threshold1和threshold2之间的像素设为128（灰色）
    image_trivalued = np.zeros_like(img)

    # 白色区间
    image_trivalued[img > threshold3] = 255

    # 蓝色区间
    image_trivalued[(img > threshold2) & (img <= threshold3)] = 0

    # 浅色区间？
    image_trivalued[(img > threshold1) & (img <= threshold2)] = 86

    # 白色
    image_trivalued[(img < threshold1)] = 172
    return image_trivalued


def process_image_3(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 定义两个阈值
    # threshold1 = 50
    # threshold2 = 70
    # threshold3 = 140

    threshold1 = 40
    threshold2 = 150

    # 进行三值化
    # 小于threshold1的像素设为0（黑色）
    # 大于threshold2的像素设为255（白色）
    # 位于threshold1和threshold2之间的像素设为128（灰色）
    image_trivalued = np.zeros_like(img)

    # 白色区间
    image_trivalued[img > threshold2] = 255

    # 蓝色区间
    image_trivalued[(img > threshold1) & (img <= threshold2)] = 0

    # 浅色区间？
    image_trivalued[img < threshold1] = 128
    return image_trivalued


def process_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 定义两个阈值
    # threshold1 = 50
    # threshold2 = 70
    # threshold3 = 140

    threshold1 = 30
    threshold2 = 50
    threshold3 = 150

    # 进行三值化
    # 小于threshold1的像素设为0（黑色）
    # 大于threshold2的像素设为255（白色）
    # 位于threshold1和threshold2之间的像素设为128（灰色）
    image_trivalued = np.zeros_like(img)

    # 白色区间
    image_trivalued[img > threshold3] = 255

    # 蓝色区间
    image_trivalued[(img > threshold2) & (img <= threshold3)] = 172

    # 浅色区间？
    image_trivalued[(img > threshold1) & (img <= threshold2)] = 86
    return image_trivalued



