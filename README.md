<p align="center">

  <img src="./assets/title.jpg">
  <p align="center" style="margin-top: 10px">
    <!-- <br> -->
        <a href="https://arxiv.org/abs/2502.08047"><img src='https://img.shields.io/badge/arXiv-WorldGUI-red' alt='Paper PDF'></a>
        <a href='https://showlab.github.io/WorldGUI'><img src='https://img.shields.io/badge/Project_Page-WorldGUI-green' alt='Project Page'></a>
    </br>
    </br>
  </p>

</p>


## 📢 Update
* [04/03/2025] We release the code of agent GUI-Thinker. Now, we support running our agent on your Windows computer locally.
* [13/02/2025] We release the WorldGUI in [arxiv](https://arxiv.org/abs/2502.08047).

## What is the WorldGUI?

<p align="center"><img src="./assets/teaser.jpg" alt="" style="width: 50%"/></p>

**WorldGUI** is a novel GUI benchmark that sets itself apart from earlier benchmarks like OSWorld, AssistGUI, and WindowsAgentArena. While those benchmarks primarily focus on static testing as shown in the left of the figure, WorldGUI designs each GUI task with various initial states to better reflect the complex and dynamic nature of real-world computer usage as shown in the right of the figure.

Additionally, we develop a new agent framework, **GUI-Thinker**, leveraging a critique mechanism, that effectively manages the unpredictability and complexity of GUI interactions.


### Benchmark Overview

<p align="center"><img src="./assets/benchoverview.jpg" alt="benchmark" style="width: 80%"/></p>

<b>WorldGUI</b>: An illustration of our proposed real-world GUI benchmark. The left shows that for each task, WorldGUI provides a user query, instructional video, and pre-actions. The pre-actions lead to different initial states. The key characteristic of our WorldGUI is the various initial states of the same task to stimulate the real-world testing process. The right shows the software included in our benchmark and the interactions about testing the agents in our GUI environment.

### Agent Framework Overview

<p align="center"><img src="./assets/agentoverview.jpg" alt="agent" style="width: 80%" /></p>

An overview of <b>GUI-Thinker</b>. The Planner module receives the user query and an instructional video as input and generates an initial plan for the Planner-Critic process. This plan is then refined and executed step by step. Before each step is passed to the Actor module, it undergoes a Step-Check. After the Actor produces an action, the Actor-Critic module iteratively verifies the completion of the action and makes corrections if needed.

## Computer Use Agent (GUI-Thinker)

### 1. Env setup

To create a Conda virtual environment and activate it, follow these steps:

1. Open your terminal (or Anaconda Prompt if you are on Windows).

2. Create a new Conda environment named `guithinker` with Python 3.11 installed:

```bash
conda create -n guithinker python=3.11
conda activate guithinker
pip install -r requirements.txt
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```
Moreover, you can refer to the files under folder `.log` to manually install the corresponding modules.

### 2. Set API Key
We recommend running one or more of the following command to set API keys to the environment variables. On Windows Powershell (via the set command if on cmd):

```bash
$env:ANTHROPIC_API_KEY="sk-xxxxx" (Replace with your own key)
$env:GEMINI_API_KEY="sk-xxxxx"
$env:OPENAI_API_KEY="sk-xxxxx"
```

### 3. Set Google Clound Vision API
We implement our GUI parser with the help of [google clound vision service](https://cloud.google.com/vision?hl=zh_cn). We recommend you following this [guidance](https://cloud.google.com/vision/product-search/docs/auth?hl=zh-cn) to save a local file for the identity verification.

```bash
gcloud auth activate-service-account --key-file KEY_FILE

$env:GOOGLE_APPLICATION_CREDENTIALS="PATH_TO_KEY_FILE"
```


### 3. Quick Start
The BasicGUI uses GPT-4 or Gemini, first set OPENAI_API_KEY and GEMINI_API_KEY in your environment.
In BasicGUI, each module has been separated into its own service. Use the following command to start replication, after which you will be able to access each module via API:

For windows:
```bash
.\shells\start_server.bat
```

Every time you change the files under the folder **`agent`**, you need to restart the server.

For windows:
```bash
.\shells\end_server.bat
.\shells\start_server.bat
```


### 3. Fast evaluation
```bash
python test_examples\test_autopc_henry.py
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
If you like our project, please give us a star ⭐ on GitHub for the latest update.