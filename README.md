<p align="center">

  <!-- <h1 align="center">WorldGUI: Dynamic Testing for Comprehensive Desktop GUI Automation</h1> -->
  <img src="./assets/title.jpg">
  <p align="center">
    <a href="https://scholar.google.com/citations?user=QLSk-6IAAAAJ&hl=zh-CN"><strong>Henry Hengyuan Zhao</strong></a>
    ·
    <a href="https://scholar.google.com/citations?user=No9OsocAAAAJ&hl=en"><strong>Difei Gao</strong></a>
    ·
    <a href="https://sites.google.com/view/showlab"><strong>Mike Zheng Shou</strong></a>
    <br>
    <br>
        <a href="https://arxiv.org/pdf/2502.08047"><img src='https://img.shields.io/badge/arXiv-WorldGUI-red' alt='Paper PDF'></a>
        <a href='https://showlab.github.io/WorldGUI'><img src='https://img.shields.io/badge/Project_Page-WorldGUI-green' alt='Project Page'></a>
    </br>
    <br>
    <b>Show Lab, National University of Singapore </b>
    </br>
  </p>

</p>

<!-- ## Abstract -->



## 📢 News
* [13/02/2025] 🔥 We release the WorldGUI [paper](https://arxiv.org/pdf/2502.08047).

## Benchmark Overview

<p align="center"><img src="./assets/benchoverview.jpg" alt="benchmark"/></p>

<b>WorldGUI</b>: An illustration of our proposed real-world GUI benchmark. The left shows that for each task, WorldGUI provides a user query, instructional video, and pre-actions. The pre-actions lead to different initial states. The key characteristic of our WorldGUI is the various initial states of the same task to stimulate the real-world testing process. The right shows the software included in our benchmark and the interactions about testing the agents in our GUI environment.

## Agent Framework Overview

<p align="center"><img src="./assets/agentoverview.jpg" alt="agent"/></p>

An overview of <b>GUI-Thinker</b>, includes five proposed components: Planner, Planner-Critic, Step-Check, Actor, and Actor-Critic. The Planner module receives the user query and an instructional video as input and generates an initial plan for the Planner-Critic process. This plan is then refined and executed step by step. Before each step is passed to the Actor module, it undergoes a Step-Check. After the Actor produces an action, the Actor-Critic module iteratively verifies the completion of the action and makes corrections if needed.

## 🙏 Acknowledgement

- [OOTB (Computer Use)](https://github.com/showlab/computer_use_ootb?tab=readme-ov-file): Computer Use OOTBStar is an out-of-the-box (OOTB) solution for Desktop GUI Agent, including API-based (Claude 3.5 Computer Use) and locally-running models (ShowUI, UI-TARS).

- [ShowUI](https://github.com/showlab/ShowUI): Open-source, End-to-end, Lightweight, Vision-Language-Action model for GUI Agent & Computer Use.
- [SWE-bench Multimodal] (https://www.swebench.com/multimodal.html)

## 🎓 Citation

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
