

<div align="center">
  <img style="width: 500px" src="./assets/guithinker-logo.png">
  <h1 align="center"> A Basic yet Comprehensive GUI Agent Developed with Self-Reflection</h1>
</div>

<h4 align="center"> Welcome to GUI-Thinker! If you find this repo useful, please give a star ⭐ for encouragement.</h4>

<div align="center" style="margin-bottom: 0">
  <!-- <img style="width: 70%" src="./assets/guithinker-logo.png"> -->
  <!-- <img style="width: 80%" src="./assets/title.jpg"> -->
<a href="https://arxiv.org/abs/2502.08047"><img src='https://img.shields.io/badge/arXiv-2502.08047-b31b1b.svg?logo=arXiv' alt='Paper PDF'></a>
<a href='https://showlab.github.io/GUI-Thinker'><img src='https://img.shields.io/badge/Project_Page-WorldGUI-green' alt='Project Page'></a>
<a href='https://github.com/showlab/Awesome-GUI-Agent'><img src='https://img.shields.io/badge/Github-AwesomeGUI-orange' alt='AwesomeGUI'>
 </a>
</div>

<!-- Welcome to GUI-Thinker! GUI-Thinker is a basic yet comprehensive GUI agent with self-reflection, deployable **without requiring Docker or a virtual machine**. It is included in the paper [WorldGUI](https://showlab.github.io/GUI-Thinker/).🌐 -->


<!-- ## ✨ Key Features
- Easy Setup: Quick and straightforward installation steps to get you started with desktop GUI agent.
- Comprehensive Documentation: Detailed guides and usage examples to help you understand and leverage the full capabilities of the project.
- Community Driven: We welcome contributions, feedback, and ideas. Feel free to open issues or submit pull requests if you have suggestions for improvement.
- Regular Updates: Our project is actively maintained, with new features and bug fixes released regularly. -->



<!-- <details> -->
<!-- <summary style="font-size:18px">What is the GUI-Thinker?</summary> -->

## ✨ What's new in GUI-Thinker?

**GUI-Thinker** is a newly developed GUI agent based on a self-reflection mechanism. We systematically investigate GUI automation and establish the following workflow, incorporating three key self-reflection modules:

- Planner-Critic (Post-Planning Critique): Self-corrects the initial plans to ensure their accuracy

- Step-Check (Pre-Execution Validation): Remove redundant steps or modify them if necessary.

- Actor-Critic (Post-Action Evaluation): Review the task completion status and apply necessary corrections.



<p align="center" style="margin:0"><img src="./assets/agentoverview.jpg" alt="agent" style="width: 80%" /></p>

<p align="center">Figure 1: Overview of GUI-Thinker.</p>

<p align="center" style="margin:0"><img src="./assets/com_barchart.png" alt="results" style="width: 80%" /></p>

<p align="center">Figure 2: Comparison of various agents on the WorldGUI Benchmark (meta task).</p>

<!-- </details> -->

## 📢 Update

* [08/03/2025] We made a demo for showing the GUI-Thinker.
* [05/03/2025] ⚡ Our GUI-Thinker now supports both [instructional video](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-test-with-a-prepared-demo-case-under-the-folder-data) and [non-video](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-test-with-your-own-user-query) inputs. Enjoy!
* [05/03/2025] 😊 We release the code of GUI-Thinker. Now, we support running our GUI agent on your Windows computer locally [Getting started](https://github.com/showlab/WorldGUI/tree/main?tab=readme-ov-file#-getting-started-with-computer-use-agent-gui-thinker). GUI-Thinker now supports various base LMMs through API calling, including GPT-4o, Gemini-2.0, and Claude-3.5-Sonnet. Local model support will be available soon.

* [13/02/2025] We release the WorldGUI in [arxiv](https://arxiv.org/abs/2502.08047).


## ✅ Todo List

GUI-Thinker is continuously evolving! Here's what's coming:

- 🖥️ **Lightweight Version**: Supporting a lightweight version specially design for Claude-3.5-Sonnet Computer Use without the GUI parser.

- 👓 **OOTB Usage**: Supporting a user-frendly interface based on Gradio.

- 📊 **Locally-running Models**: Supporting the ShowUI or UI-TARS as the Actor in our framework.

- 🎨 **Huggingface Demo**: Developing online demo in Huggingface.

Feel free to open issues or submit pull requests if you have suggestions. Our project is actively maintained, with new features and bug fixes released regularly. 🚀


## 🖥️ Demo of Computer Using

Demo Video (The video has been sped up):

https://github.com/user-attachments/assets/5d25c079-4c84-4435-8280-591f32f89700

See 1080p version from https://www.youtube.com/watch?v=RoJ-cbjfZmg


## 🚀 Getting Started


See [Get Started](./Get%20Started.md) for local computer running.

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

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=showlab/GUI-Thinker&type=Date)](https://star-history.com/#showlab/GUI-Thinker&Date)


## 🔔 Contact
If you have any questions or suggestions, please don't hesitate to let us know. You can directly email [Henry Hengyuan Zhao](https://zhaohengyuan1.github.io/) at NUS using the email address hubylidayuan@gmail.com, or post an issue on this repository. We welcome contributions. Feel free to submit pull requests if you have suggestions for improvement.

I'm open to discussing AI agents and research collaboration if you're interested. My personal Wechat is here:

<p align="left" style="margin:0"><img src="./assets/henrywechat.jpg" alt="agent" style="width: 40%" /></p>

