import base64
import pickle
from collections import OrderedDict


class TaskManager:
    def __init__(self, name, parent=None):
        self.name = name
        self.is_completed = False
        self.subtasks = OrderedDict()
        self.subtasks_list = []
        self.current_subtask_index = 0
        self.parent = parent
        self.record = {}

    def add_subtasks(self, subtask_names):
        for subtask_name in subtask_names:
            subtask = TaskManager(subtask_name, parent=self)
            self.subtasks[subtask_name] = subtask
            self.subtasks_list.append(subtask)

    def current_subtask(self):
        if self.current_subtask_index < len(self.subtasks_list):
            return self.subtasks_list[self.current_subtask_index]
        else:
            return None

    def check_completion(self):
        if all(subtask.is_completed for subtask in self.subtasks_list):
            self.is_completed = True
            if self.parent:
                self.parent.check_completion()

    def execute_task(self):
        print(f"Executing task: {self.name}")
        if not self.subtasks_list:  # If the task is a leaf node, execute it
            self.is_completed = True

    def list_uncompleted_tasks(self):
        uncompleted_tasks = []
        if not self.is_completed:
            uncompleted_tasks.append(self.name)
        for subtask in self.subtasks_list:
            uncompleted_tasks.extend(subtask.list_uncompleted_tasks())
        return uncompleted_tasks

    def next(self, recursive=True):
        if recursive:
            # this model will skip the task node
            return self.next_recursive()
        else:
            return self.next_node()
    
    def next_recursive(self):
        next_node = self.next_node()
        if next_node:
            return self.skip_task_node(next_node)
        return None
        
    def next_node(self):
        while self.current_subtask_index < len(self.subtasks_list):
            if not self.subtasks_list[self.current_subtask_index].is_completed:
                return self.subtasks_list[self.current_subtask_index]
            self.current_subtask_index += 1

        # self.current_subtask_index = 0  # Reset for next traversa
        self.check_completion()

        # Move upwards to find the next uncompleted task
        parent_task = self.parent
        while parent_task:
            next_parent_subtask = parent_task.next()
            if next_parent_subtask:
                return next_parent_subtask
            parent_task = parent_task.parent

        return None  # If reached here, all tasks are complete
    
    def skip_task_node(self, node):
        if node:
            if "Subtask" not in node.name:
                return node.next_node()
            else:
                return node
        else:
            return None

    def replan(self):
        pass


def ordered_dict_to_tasks(task_dict, parent=None):
    if not task_dict:
        return None

    root = TaskManager(list(task_dict.keys())[0], parent)
    if isinstance(task_dict[root.name], OrderedDict):  # Added this check
        for subtask_name, subtask_value in task_dict[root.name].items():
            subtask = ordered_dict_to_tasks(OrderedDict([(subtask_name, subtask_value)]), root)
            root.subtasks[subtask_name] = subtask
            root.subtasks_list.append(subtask)

    return root


def parse_tasks(input_str):
    lines = input_str.strip().split('\n')
    root = OrderedDict()
    tasks = OrderedDict()
    current_task = None
    current_subtask = None

    for line in lines:
        line = line.strip()
        if line.startswith('Task') or line.startswith('任务'):
            current_task = line
            tasks[current_task] = OrderedDict()
        elif line.startswith('Subtask ') or line.startswith('子任务'):
            current_subtask = line
            tasks[current_task][current_subtask] = []
        elif line.startswith('Sub-subtask '):
            tasks[current_task][current_subtask].append(line)

    root['Root'] = tasks
    return root


def turn_text_steps_to_iter(plan):
    parsed_tasks = parse_tasks(plan)
    root_task = ordered_dict_to_tasks(parsed_tasks)
    # The first task is "root", so move to the next task
    current_task = root_task.next() if root_task is not None else None
    return parsed_tasks, current_task, root_task


def encode_task(task):
    if isinstance(task, str):
        return task
    else:
        return base64.b64encode(pickle.dumps(task)).decode('utf-8')


def decode_task(task):
    try:
        return pickle.loads(base64.b64decode(task)) 
    except:
        return task

# Usage Example
if __name__ == "__main__":
    plan = '''Task 1: 新建合成
    Subtask 1: 将合成命名为”文字“
    Subtask 2: 设置合成大小为1920×1080
    Subtask 3: 设置帧速率为30，持续时间为3秒

    Task 2: 添加文字图层
    Subtask 1: 双击添加文字图层
    Subtask 2: 输入文字内容为”一键三连“
    Subtask 3: 选择一个免费字体'''

    parsed_tasks = parse_tasks(plan)
    task_tree = ordered_dict_to_tasks(parsed_tasks)
    current_task = task_tree
    while current_task:
        current_task.execute_task()
        current_task = current_task.next()
