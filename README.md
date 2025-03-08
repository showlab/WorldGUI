

<div align="center">
  <img style="width: 500px" src="./assets/guithinker-logo.png">
  <h1 align="center"> A Basic yet Comprehensive GUI Agent Developed with Self-Reflection</h1>
</div>

<h4 align="center"> If you find our project useful, please consider giving it a star ⭐ on GitHub for our latest update.</h4>

<div align="center" style="margin-bottom: 0">
  <!-- <img style="width: 70%" src="./assets/guithinker-logo.png"> -->
  <!-- <img style="width: 80%" src="./assets/title.jpg"> -->
<a href="https://arxiv.org/abs/2502.08047"><img src='https://img.shields.io/badge/arXiv-2502.08047-b31b1b.svg?logo=arXiv' alt='Paper PDF'></a>
<a href='https://showlab.github.io/GUI-Thinker'><img src='https://img.shields.io/badge/Project_Page-WorldGUI-green' alt='Project Page'></a>
<a href='https://github.com/showlab/Awesome-GUI-Agent'><img src='https://img.shields.io/badge/Github-AwesomeGUI-orange' alt='AwesomeGUI'>
 </a>
</div>

Welcome to GUI-Thinker! GUI-Thinker is a basic yet comprehensive GUI agent with self-reflection, deployable **without requiring Docker or a virtual machine**. It is included in the paper [WorldGUI](https://showlab.github.io/GUI-Thinker/).🌐


<!-- ## ✨ Key Features
- Easy Setup: Quick and straightforward installation steps to get you started with desktop GUI agent.
- Comprehensive Documentation: Detailed guides and usage examples to help you understand and leverage the full capabilities of the project.
- Regular Updates: Our project is actively maintained, with new features and bug fixes released regularly. -->

## Introduction


<!-- <details> -->
<!-- <summary style="font-size:18px">What is the GUI-Thinker?</summary> -->

### What's new in GUI-Thinker?

**GUI-Thinker** is a newly developed GUI agent based on a self-reflection mechanism. We systematically investigate GUI automation and establish the following workflow, incorporating three key self-reflection modules:

- Planner-Critic (Post-Planning Critique): Self-corrects the initial plans to ensure their accuracy

- Step-Check (Pre-Execution Validation): Remove redundant steps or modify them if necessary.

- Actor-Critic (Post-Action Evaluation): Review the task completion status and apply necessary corrections.

<!-- - GUI-Thinker is an end-to-end agent that accepts the user query and executes the plan step by step.

- GUI-Thinker supports both instructional video and non-video as the inputs for controlling the computer like a human.

- GUI-Thinker supports adjusting its actions before the Actor when encountering unpredicted interfaces (e.g., last time user settings are impossible to be predetermined when you open a popup window).

- After the Actor, we propose to iteratively execute the verify-then-correct process to ensure the step completion. -->


<p align="center"><img src="./assets/agentoverview.jpg" alt="agent" style="width: 80%" /></p>


<!-- </details> -->

## 📢 Update
* [05/03/2025] ⚡ Our GUI-Thinker now supports both [instructional video](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-test-with-a-prepared-demo-case-under-the-folder-data) and [non-video](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-test-with-your-own-user-query) inputs. Enjoy!
* [05/03/2025] 😊 We release the code of GUI-Thinker. Now, we support running our GUI agent on your Windows computer locally [Getting started](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-getting-started-with-computer-use-agent-gui-thinker). GUI-Thinker now supports various base LMMs through API calling, including GPT-4o, Gemini-2.0, and Claude-3.5-Sonnet. Local model support will be available soon.

* [13/02/2025] We release the WorldGUI in [arxiv](https://arxiv.org/abs/2502.08047).



## 🚀 Getting Started with Computer-Using Agent (GUI-Thinker)

## 1. Clone the Repository 📂
Open the Conda Terminal. (After installation Of Miniconda, it will appear in the Start menu.)
Run the following command on **Conda Terminal**.
```bash
git clone https://github.com/showlab/WorldGUI.git
cd GUI-Thinker
```

## 2. Env setup 🔨

To create a Conda virtual environment and activate it, follow these steps:

Create a new Conda environment named `guithinker` with Python 3.11 installed:

```bash
conda create -n guithinker python=3.11
conda activate guithinker
pip install -r requirements.txt
```

Install the dependencies:
```bash
pip install -r requirements.txt
```
Moreover, you can refer to the files under folder `.log` to manually install the corresponding modules.

## 3. Set API Key ✏️
We recommend running one or more of the following command to set API keys to the environment variables. On Windows Powershell (via the set command if on cmd):

>```bash
>$env:ANTHROPIC_API_KEY="sk-xxxxx" (Replace with your own key)
>$env:GEMINI_API_KEY="sk-xxxxx"
>$env:OPENAI_API_KEY="sk-xxxxx"
>```

## 4. Set Google Clound Vision API 🔧
We implement our GUI parser with the help of [google clound vision service](https://cloud.google.com/vision?hl=zh_cn). We recommend you following this [guidance](https://cloud.google.com/vision/product-search/docs/auth?hl=zh-cn) to save a local file for the identity verification.

```bash
gcloud auth activate-service-account --key-file KEY_FILE

$env:GOOGLE_APPLICATION_CREDENTIALS="PATH_TO_KEY_FILE"
```

(Optional) Set the path of `KEY_FILE` in the path [agent/gui_parser/server.py#L18](https://github.com/showlab/WorldGUI/blob/main/agent/gui_parser/server.py#L18)

## 5. Quick Start ⭐

Start with your own query or included query in folder `data`.

### 5.1 Start the server

We implemented a backend and frontend system that separates screenshot capture from agent execution, enabling remote deployment of the agent via API calls. The frontend can run on Windows or other platforms (e.g., mobile devices).

For windows:
```bash
.\shells\start_server.bat
```
You can track the status by checking the files under folder `.log`. Every time you change the files under the folder **`agent`**, you need to restart the server.

### Restart the server

For windows:
```bash
.\shells\end_server.bat
.\shells\start_server.bat
```
### 🎈 5.2 Test with your own user query

Here, we provide a straightforward example demonstrating how to operate a YouTube video using the Claude-3.5-Sonnet as the base model. Check the configuration of file `agent\config\basic.yaml` to edit the base model.

Command:
```bash
python test_guithinker_custom.py --userquery "Open the video "https://www.youtube.com/watch?v=uTuuz__8gUM", add to watch later and create a watch list 'work & jazz'." --projfile_path "" --software_name "Youtube"
```

Demo Video (The video has been sped up):

https://github.com/user-attachments/assets/5d25c079-4c84-4435-8280-591f32f89700

See 1080p version from https://www.youtube.com/watch?v=RoJ-cbjfZmg

Initial Screenshot:
<p align="left"><img src="./assets/step0.png" alt="" style="width: 70%"/></p>

(Milestone 1) Task 1: Add video to Watch Later 

Subtask 1: Click on "More actions" button [1231, 936]
<p align="left"><img src="./assets/step1.png" alt="" style="width: 70%"/></p>
Subtask 2: Click on "Save" option in the menu that appears
<p align="left"><img src="./assets/step2.png" alt="" style="width: 70%"/></p>
Subtask 3: Click on "Watch Later" option in the save menu
<p align="left"><img src="./assets/step3.png" alt="" style="width: 70%"/></p>

(Milestone 2) Task 2: Create new playlist "work & jazz" 

Subtask 1: Click on "More actions" button again if the menu closed

Output of Step-Check: `<Pass>`. Therefore no change in current step. (See the deatail design of Step-Check from [paper](https://arxiv.org/abs/2502.08047))

<p align="left"><img src="./assets/step4.png" alt="" style="width: 70%"/></p>

Subtask 2: Click on "Save" option if the save menu is not open

Output of Step-Check: `<Pass>`. Therefore no change in current step.
<p align="left"><img src="./assets/step5.png" alt="" style="width: 70%"/></p>

Subtask 3: Click on "+ Create new playlist" option at the bottom of the save menu
<p align="left"><img src="./assets/step6.png" alt="" style="width: 70%"/></p>

Subtask 4: Type "work & jazz" in the playlist name field
<p align="left"><img src="./assets/step7.png" alt="" style="width: 70%"/></p>

Subtask 5: Click "Create" button to confirm the new playlist creation
<p align="left"><img src="./assets/step8.png" alt="" style="width: 70%"/></p>


### 💻 5.3 Test with a simple demo case under the folder `data`:
```bash
python test_guithinker_demo.py
``` 

User Query: Select all text and apply numbered list for them. Use '1, 2, 3' symbol of numbered list.

Initial Screenshot:
<p align="left"><img src="./assets/demo_start.png" alt="" style="width: 70%"/></p>

Intermediate Screenshot:
<p align="left"><img src="./assets/demo_inter.png" alt="" style="width: 70%"/></p>

Invoke the *Region Search* component in the Step-Check Module, which yields the following image:
<p align="left"><img src="./assets/region_locate.png" alt="" style="width: 70%"/></p>

Reducing the resolution and directing the agent's focus toward highly relevant regions will enhance its critique decisions.

Final Screenshot:
<p align="left"><img src="./assets/demo_end.png" alt="" style="width: 70%"/></p>

## ✅ Todo List

GUI-Thinker is continuously evolving! Here's what's coming:

- 🖥️ **Lightweight Version**: Supporting a lightweight version specially design for Claude-3.5-Sonnet Computer Use without the GUI parser.

- 👓 **OOTB Usage**: Supporting a user-frendly interface based on Gradio.

- 📊 **Locally-running Models**: Supporting the ShowUI or UI-TARS as the Actor in our framework.

- 🎨 **Huggingface Demo**: Developing online demo in Huggingface.

Have ideas or suggestions? Feel free to open an issue! Stay tuned for more exciting updates! 🚀


## ❤ Acknowledgement
- Special thanks to [Difei Gao](https://scholar.google.com/citations?user=No9OsocAAAAJ&hl=en) for his hard work on devleoping the codebase.

- We express our great thanks to Kaiming Yang, Mingyi Yan, Wendi Yu for their hard work for data ananotation and baseline testing.

- [OOTB (Computer Use)](https://github.com/showlab/computer_use_ootb?tab=readme-ov-file): Computer Use OOTB is an out-of-the-box (OOTB) solution for Desktop GUI Agent, including API-based (Claude 3.5 Computer Use) and locally-running models (ShowUI, UI-TARS).

- [ShowUI](https://github.com/showlab/ShowUI): Open-source, End-to-end, Lightweight, Vision-Language-Action model for GUI Agent & Computer Use.

- [AssistGUI](https://arxiv.org/pdf/2312.13108): AssistGUI is the first work that focuses on desktop productivity software usage with over 100 realistic GUI tasks.

- [VideoGUI](https://github.com/showlab/videogui): A Benchmark for GUI Automation from Instructional Videos. Can a GUI agent behave like a human when giving an image-style effect and a user query?


- [SWE-bench Multimodal](https://www.swebench.com/multimodal.html): SWE-bench Multimodal is a dataset for evaluating AI systems on visual software engineering tasks.

# 🎓 BibTeX

If you find WorldGUI useful, please cite using this BibTeX:

```bibtex
@misc{zhao2025worldguidynamictestingcomprehensive,
      title={WorldGUI: Dynamic Testing for Comprehensive Desktop GUI Automation}, 
      author={Henry Hengyuan Zhao and Difei Gao and Mike Zheng Shou},
      year={2025},
      eprint={2502.08047},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2502.08047}, 
}
```
