class Time:
    def __init__(self, time_str):
        self.time_str = time_str
        self.time_int = self.time_to_int(time_str)

    def time_to_int(self, time_str):
        hh, mm, ss, ff = map(int, time_str.split(":"))
        return ((hh * 3600 + mm * 60 + ss) * 100) + ff

    def int_to_time(self, time_int):
        ff = time_int % 100
        time_int //= 100
        ss = time_int % 60
        time_int //= 60
        mm = time_int % 60
        hh = time_int // 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

    def __add__(self, other):
        return Time(self.int_to_time(self.time_int + other.time_int))

    def __sub__(self, other):
        return Time(self.int_to_time(self.time_int - other.time_int))

    def __mul__(self, multiplier):
        return Time(self.int_to_time(self.time_int * multiplier))

    def __truediv__(self, divisor):
        return Time(self.int_to_time(self.time_int // divisor))

    def __str__(self):
        return self.time_str

    # 测试
    # time1 = Time("00:00:01:00")
    # time2 = Time("00:00:0 0:50")
    #
    # time_add = time1 + time2
    # print("加法:", time_add)
    #
    # time_subtract = time1 - time2
    # print("减法:", time_subtract)
    #
    # time_multiply = time1 * 2
    # print("乘法:", time_multiply)
    #
    # time_divide = time1 / 2
    # print("除法:", time_divide)


def format_gui(data, indent=0, in_elements=False, inner_elements=False):
    lines = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'elements':
                lines.append(' ' * indent + str(key) + ':')
                if not is_two_dimensional(value):
                    # print(value)
                    value = sort_elements_by_xy(value)
                lines.extend(format_gui(value, indent + 2, True))
            elif key in ['rectangle', 'position', 'name']:
                if len(value) < 100:
                    lines.append(' ' * indent + str(key) + ': ' + str(value))
            elif key in ['type', 'depth', 'class_name']:
                continue
            else:
                lines.append(' ' * indent + str(key) + ':')
                lines.extend(format_gui(value, indent + 2))
    elif isinstance(data, list):
        if in_elements:
            for value in data:
                # print(value)
                lines.extend(format_gui(value, indent, False, True))
        elif inner_elements:
            element_line = []
            for element in data:
                if type(element) is dict:
                    name = element.get('name', '')
                    rectangle = element.get('rectangle', [])
                    position = element.get('position', [])
                    if len(name) >= 500:
                        continue
                    if position:
                        element_line.append(f"{name} {position}")
                    else:
                        element_line.append(f"{name} {rectangle}")
            lines.append(' ' * indent + '; '.join(element_line))
        else:
            for value in data:
                lines.extend(format_gui(value, indent))
    else:
        return [' ' * indent + str(data)]
    return lines


def compress_gui(com_gui):
    # compress gui
    for window_name, window_data in com_gui.items():
        for panel_item in window_data:
            for row in panel_item.get("elements", []):
                if type(row) is list:
                    for element in row:
                        try:
                            element['position'] = [int((element['rectangle'][0] + element['rectangle'][2]) / 2),
                                                   int((element['rectangle'][1] + element['rectangle'][3]) / 2)]
                            del element['rectangle']
                        except TypeError:
                            print(element, row, panel_item)
                elif type(row) is dict:
                    row['position'] = [int((row['rectangle'][0] + row['rectangle'][2]) / 2),
                                       int((row['rectangle'][1] + row['rectangle'][3]) / 2)]
                    del row['rectangle']

    return com_gui


# 检查是否为二维列表
def is_two_dimensional(lst):
    return all(isinstance(item, list) for item in lst)

# 单独的按Y轴（垂直位置）排序的函数
def sort_elements_by_y(lst):
    try:
        return sorted(lst, key=lambda x: x['rectangle'][1])
    except:
        return sorted(lst, key=lambda x: x['position'][1])

# 单独的按X轴（水平位置）排序的函数
def sort_elements_by_x(lst):
    try:
        return sorted(lst, key=lambda x: x['rectangle'][0])
    except:
        return sorted(lst, key=lambda x: x['position'][0])

# 综合排序函数，先按Y轴排序，然后对同一行的元素按X轴排序
def sort_elements_by_xy(lst):
    if is_two_dimensional(lst):
        return lst
    
    y_sorted = sort_elements_by_y(lst)  # 先按Y轴排序
    grouped_sorted = []  # 分组后每组按X轴排序的结果
    current_line = []  # 当前处理的行
    line_threshold = 10  # Y轴上判定同一行的阈值

    for item in y_sorted:
        # 判断是否开启新的一行
        if 'rectangle' in item:
            key = 'rectangle'
        else:
            key = 'position'
        
        if not current_line or abs(item[key][1] - current_line[-1][key][1]) <= line_threshold:
            current_line.append(item)
        else:
            # 新行开始，先对当前行按X轴排序，再加入到最终结果
            grouped_sorted.append(sort_elements_by_x(current_line))
            current_line = [item]  # 创建新行

    # 处理最后一行
    if current_line:
        grouped_sorted.append(sort_elements_by_x(current_line))

    return grouped_sorted
