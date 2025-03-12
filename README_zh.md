<div align="center">
  <img src="./assets/logo.png" style="width: 100%">
  <!-- <h1>基于自反思机制的全能高效GUI智能体 🤖</h1> -->
</div>

<h5 align="center"> 
欢迎来到 GUI-Thinker！如果你觉得本项目有帮助，欢迎点个 Star ⭐ 支持我们一下！
</h5>

<h5 align="center"> 

[English](README.md) | 中文

[![arXiv](https://img.shields.io/badge/ArXiv-2502.08047-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2502.08047)
[![Project Page](https://img.shields.io/badge/Project_Page-WorldGUI-white?color=7289DA)](https://showlab.github.io/GUI-Thinker)
[![Project Page](https://img.shields.io/badge/Github-AwesomeGUI-blue)](https://github.com/showlab/Awesome-GUI-Agent)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fshowlab%2FGUI-Thinker&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

</h5>

## <img src="./assets/clickicon.png" alt="点击" style="height:25px; vertical-align:middle; filter: invert(1) brightness(2);"> 项目概览

- **GUI-Thinker** 是一款具备**高自适应性**与**自我反思能力**的桌面 GUI 智能体，能够在动态的图形界面环境中完成多种操作。

- **无需 Docker 或虚拟机**，即可快速部署和运行。

- 更多详情点击了解[WorldGUI](https://showlab.github.io/GUI-Thinker)。

User Query: 关闭'Battery saver'通知
GUI-Thinker:
<p align="center"><img src="./assets/sucessexample.jpg" alt="agent" style="width: 100%" /></p>

## 项目介绍

<details>
<summary>GUI-Thinker 有哪些创新？</summary>

GUI-Thinker 在 GUI 自动化领域引入了**自反思机制**，我们对 GUI 自动化进行了系统性的研究，并构建了如下工作流程，其中包含三个关键的自反思模块：

1. **Planner-Critic**：对初始生成的操作规划进行自我审查和修正，减少错误。
2. **Step-Check**：在执行之前去除或修正冗余、不必要或无效的步骤。
3. **Actor-Critic**：执行后对状态进行评估并校正操作，以保证任务顺利完成。

### 技术细节

<p align="center"><img src="./assets/agentoverview.jpg" alt="agent" style="width: 80%" /></p>
<p align="center">GUI-Thinker 整体框架</p>

<p align="center"><img src="./assets/plannercritic_flow.png" alt="agent" style="width: 60%" /></p>
<p align="center">State-Aware Planner 和 Planner-Critic 模块</p>

<p align="center"><img src="./assets/stepcheck_flow.png" alt="agent" style="width: 60%" /></p>
<p align="center">Step-Check 模块</p>

<p align="center"><img src="./assets/actorcritic_flow.png" alt="agent" style="width: 60%" /></p>
<p align="center">Actor-Critic 模块</p>

### 与现有最先进的GUI智能体比较

<p align="center"><img src="./assets/com_barchart.png" alt="results" style="width: 80%" /></p>
<p align="center">在WorldGUI基准测试（元任务）中，各智能体性能对比。</p>

</details>

## 📢 更新日志

- **[2025.03.11]** ⚡ 发布 **快速版 GUI-Thinker**：使用 Anthropic Claude-3.5 与 Claude-3.7 模型作为 Actor，无需 GUI Parser，显著提升操作速度。运行 [test_guithinker_fast.py](./test_guithinker_fast.py) 即可体验！

- **[2025.03.08]** 推出 GUI-Thinker 演示 Demo。

- **[2025.03.05]** ⚡ GUI-Thinker 同时支持[教学视频输入](./Get%20Started.md#%E5%AF%BC%E5%85%A5%E6%95%99%E5%AD%A6%E8%A7%86%E9%A2%91)和[无视频输入](./Get%20Started.md#%E7%9B%B4%E6%8E%A5%E8%BE%93%E5%85%A5%E7%94%A8%E6%88%B7%E6%8C%87%E4%BB%A4)模式。

- **[2025.03.05]** 😊 项目正式开源，支持在 Windows 本地部署，参见[快速上手指南](./Get%20Started.md)。
- **[2025.02.13]** WorldGUI 论文在 [arXiv](https://arxiv.org/abs/2502.08047) 发布。

## ✨ 核心特性

- 🏆 **高性能**：在 WorldGUI 基准测试中相比 Claude-3.5 Computer Use 提升 14.9%。
- 🌐 **通用LMM支持**：支持多种大型多模态模型（OpenAI, Anthropic, Gemini等）。
- 🔀 **灵活交互方式**：既支持**教学视频输入**，也支持**无视频输入**。
- 🚀 **简单部署**：无需 Docker 或虚拟机，只需执行 `.\shells\start_server.bat` 和 `python test_guithinker_custom.py` 即可运行。

## 🤖 主要组件：

项目包含如下组件：

- [x] **GUI Parser**：使用 Google OCR 与 PyAutoGUI 获取界面元素信息。
- [x] **State-Aware Planner**：基于屏幕截图或教学视频生成操作规划。
- [x] **Planner-Critic**：对 Planner 生成的初始步骤进行审校。
- [x] **Step-Check**：预执行检查，移除多余或无效步骤。
- [x] **Actor**：将文字描述转化为可以真正执行的鼠标键盘操作代码，如 `click(100, 200)`。
- [x] **Actor-Critic**：通过对比执行前后的界面截图来验证操作结果，并进行纠错。
- [x] **教学视频输入模式：** 可支持基于教学视频的任务执行。
- [x] **非视频输入模式：** 可直接依据用户指令执行操作。
- [x] **前后端通信系统：** 支持前后端分离，以灵活部署本地模型并与用户前端交互。

同时我们还发布了一个全新整理的Desktop GUI基准测试集 **WorldGUI**。

更多技术细节请参阅[论文](https://arxiv.org/abs/2502.08047)。

## ✅ 待办事项

持续更新中，未来计划包括：

- [x] ⚡ 快速版（Anthropic模型，无需GUI解析器）
- [ ] 👓 用户友好的Gradio前端界面
- [ ] 📊 支持本地运行模型（ShowUI、UI-TARS）
- [ ] 🎨 Huggingface在线演示

欢迎提出Issue或PR共同建设本项目！本项目会持续维护，定期发布新功能与修复问题。🚀

## 🖥️ 演示视频

演示Demo视频（已加速版）：

https://www.youtube.com/watch?v=RoJ-cbjfZmg

1080p版本：https://www.youtube.com/watch?v=RoJ-cbjfZmg

## 🚀 快速上手

参见本地运行指南：[快速上手](./Get%20Started.md)

## ❤ 致谢

- 特别感谢 [Difei Gao](https://scholar.google.com/citations?user=No9OsocAAAAJ&hl=en) 对代码库开发的贡献。
- 感谢 Kaiming Yang、Mingyi Yan、Wendi Yu 等人的数据标注与测试工作。
- [OOTB (Computer Use)](https://github.com/showlab/computer_use_ootb?tab=readme-ov-file)：一套开箱即用（OOTB）的桌面GUI智能体解决方案，支持API模型（如Claude 3.5 Computer Use）以及本地运行模型（如ShowUI、UI-TARS）。
- [ShowUI](https://github.com/showlab/ShowUI)：一个开源、端到端、轻量级的视觉-语言-动作（Vision-Language-Action）模型，适用于GUI智能体与电脑操作任务。

- [AssistGUI](https://arxiv.org/pdf/2312.13108)：首个专注于桌面生产力软件自动化使用的研究，涵盖超过100个真实的GUI任务场景。

- [VideoGUI](https://github.com/showlab/videogui)：一个基于教学视频的GUI自动化基准测试，探索GUI智能体能否在图像示例和用户指令下实现类似人类的行为。

- [SWE-bench Multimodal](https://www.swebench.com/multimodal.html)：专为评估AI系统在视觉化软件工程任务中表现而设计的数据集。

## 🎓 引用方式

如果你觉得我们的 WorldGUI 对你的研究或应用有帮助，请使用以下 BibTeX 进行引用：

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

## 🌟 Star增长趋势

[![Star趋势图](https://api.star-history.com/svg?repos=showlab/GUI-Thinker&type=Date)](https://star-history.com/#showlab/GUI-Thinker&Date)

## **🔔 联系我们**

如有疑问或建议，欢迎通过以下方式与我们联系：

- **邮箱**：[Henry Hengyuan Zhao](https://zhaohengyuan1.github.io/) (hubylidayuan@gmail.com)

- **在本仓库提 Issue**：我们会及时回复，期待你的建议和贡献！