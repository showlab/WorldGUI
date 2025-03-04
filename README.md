<p align="center" style="margin:0">
  <img src="./assets/title.jpg">
  <p align="center" style="margin-top: 10px">
        <a href="https://arxiv.org/abs/2502.08047"><img src='https://img.shields.io/badge/arXiv-2502.08047-b31b1b.svg?logo=arXiv' alt='Paper PDF'></a>
        <a href='https://showlab.github.io/WorldGUI'><img src='https://img.shields.io/badge/Project_Page-WorldGUI-green' alt='Project Page'></a>
  </p>
</p>

<h4 align="center"> If you like our project, please give us a star ⭐ on GitHub for the latest update.</h4>

## 📢 Update (Stay tuned)
* [05/03/2025] Our GUI-Thinker now supports both [instructional video](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-test-with-a-prepared-demo-case-under-the-folder-data) and [non-video](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-test-with-your-own-user-query) inputs. Enjoy!
* [05/03/2025] 😊 We release the code of GUI-Thinker. Now, we support running our GUI agent on your Windows computer locally [Getting started](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-getting-started-with-computer-use-agent-gui-thinker).
* [13/02/2025] We release the WorldGUI in [arxiv](https://arxiv.org/abs/2502.08047).

## What is the WorldGUI?

<p align="center"><img src="./assets/teaser.jpg" alt="" style="width: 50%"/></p>

**WorldGUI** is a novel GUI benchmark that sets itself apart from earlier benchmarks like OSWorld, AssistGUI, and WindowsAgentArena. While those benchmarks primarily focus on static testing as shown in the left of the figure, WorldGUI designs each GUI task with various initial states to better reflect the complex and dynamic nature of real-world computer usage as shown in the right of the figure.


<!-- ### Benchmark Overview -->
<!-- 
<p align="center"><img src="./assets/benchoverview.jpg" alt="benchmark" style="width: 80%"/></p>

<b>WorldGUI</b>: An illustration of our proposed real-world GUI benchmark. The left shows that for each task, WorldGUI provides a user query, instructional video, and pre-actions. The pre-actions lead to different initial states. The key characteristic of our WorldGUI is the various initial states of the same task to stimulate the real-world testing process. The right shows the software included in our benchmark and the interactions about testing the agents in our GUI environment. -->

## What is the GUI-Thinker?

**GUI-Thinker** is a comprehensive GUI agent that employs critical thinking to enhance task success rates.

<p align="center"><img src="./assets/agentoverview.jpg" alt="agent" style="width: 80%" /></p>

<!-- An overview of <b>GUI-Thinker</b>. The Planner module receives the user query and an instructional video as input and generates an initial plan for the Planner-Critic process. This plan is then refined and executed step by step. Before each step is passed to the Actor module, it undergoes a Step-Check. After the Actor produces an action, the Actor-Critic module iteratively verifies the completion of the action and makes corrections if needed. -->

## 🚀 Getting Started with Computer Use Agent (GUI-Thinker)

### 1. 📂 Clone the Repository 
Open the Conda Terminal. (After installation Of Miniconda, it will appear in the Start menu.)
Run the following command on **Conda Terminal**.
```bash
git clone https://github.com/showlab/WorldGUI.git
cd WorldGUI
```

### 2. 🔨 Env setup

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

### 3. 🔧 Set API Key
We recommend running one or more of the following command to set API keys to the environment variables. On Windows Powershell (via the set command if on cmd):

>```bash
>$env:ANTHROPIC_API_KEY="sk-xxxxx" (Replace with your own key)
>$env:GEMINI_API_KEY="sk-xxxxx"
>$env:OPENAI_API_KEY="sk-xxxxx"
>```

### 4. 🔧 Set Google Clound Vision API
We implement our GUI parser with the help of [google clound vision service](https://cloud.google.com/vision?hl=zh_cn). We recommend you following this [guidance](https://cloud.google.com/vision/product-search/docs/auth?hl=zh-cn) to save a local file for the identity verification.

```bash
gcloud auth activate-service-account --key-file KEY_FILE

$env:GOOGLE_APPLICATION_CREDENTIALS="PATH_TO_KEY_FILE"
```

(Optional) Set the path of `KEY_FILE` in the path [agent/gui_parser/server.py#L18](https://github.com/showlab/WorldGUI/blob/main/agent/gui_parser/server.py#L18)

### 5. ⭐ Quick Start

#### Start the server

For windows:
```bash
.\shells\start_server.bat
```

Every time you change the files under the folder **`agent`**, you need to restart the server.

#### Restart the server

For windows:
```bash
.\shells\end_server.bat
.\shells\start_server.bat
```

#### 💻 Test with a prepared demo case under the folder `data`:
```bash
python test_guithinker_demo.py
``` 

User Query: Select all text and apply numbered list for them. Use '1, 2, 3' symbol of numbered list.

Initial Screenshot:
<p align="center"><img src="./assets/306_start.png" alt="" style="width: 80%"/></p>

Intermediate Screenshot:
<p align="center"><img src="./assets/306_inter.png" alt="" style="width: 80%"/></p>

Invoke Region Search in Step-Check Module and the resulted image:
<p align="center"><img src="./assets/region_locate.png" alt="" style="width: 80%"/></p>

Reducing the resolution and directing the agent's focus toward highly relevant regions will enhance its critique decisions.

Final Screnshot:
<p align="center"><img src="./assets/306_end.png" alt="" style="width: 80%"/></p>

#### 🎈 Test with your own user query

```bash
python test_guithinker_custom.py --userquery "Set the transitions of the second ppt to Push" --projfile_path "data/project_files/300. PowerPoint Applying Transitions/project.pptx"
``` 


## ❤ Acknowledgement

- We express our great thanks to Kaiming Yang, Mingyi Yan, Wendi Yu for their hard work for data ananotation and baseline testing.

- [OOTB (Computer Use)](https://github.com/showlab/computer_use_ootb?tab=readme-ov-file): Computer Use OOTB is an out-of-the-box (OOTB) solution for Desktop GUI Agent, including API-based (Claude 3.5 Computer Use) and locally-running models (ShowUI, UI-TARS).

- [ShowUI](https://github.com/showlab/ShowUI): Open-source, End-to-end, Lightweight, Vision-Language-Action model for GUI Agent & Computer Use.

- [AssistGUI](https://arxiv.org/pdf/2312.13108): AssistGUI is the first work that focuses on desktop productivity software usage with over 100 realistic GUI tasks.

- [VideoGUI](https://github.com/showlab/videogui): A Benchmark for GUI Automation from Instructional Videos. Can a GUI agent behave like a human when giving an image-style effect and a user query?


- [SWE-bench Multimodal](https://www.swebench.com/multimodal.html): SWE-bench Multimodal is a dataset for evaluating AI systems on visual software engineering tasks.

## 🎓 BibTeX

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