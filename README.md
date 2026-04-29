# Steven Chou — Resume

双线简历系统：PM 和 Engineer 两个方向独立维护、定制化投递。

## 目录结构

```
resume/
├── pm/                  # 产品经理方向
│   └── resume.tex
├── engineer/            # 工程师方向
│   └── resume.tex
├── build.sh             # 一键编译（动态命名）
├── SPACING_GUIDE.md     # LaTeX 间距调整教程
├── sourabh_bajaj_resume.tex  # 原始模板参考
└── Dockerfile
```

## 构建

```bash
bash build.sh
```

输出文件自动命名为 `{Name}_{Position}_{Date}.pdf`，其中：
- `Name` 默认是 `Resume`，可用环境变量覆盖：`RESUME_NAME=Your_Name bash build.sh`
- `Position` 从 tex 文件顶部 `% POSITION: PM` 注释中读取
- `Date` 取当天日期（如 `Apr15`）

依赖 [tectonic](https://tectonic-typesetting.github.io/)（`brew install tectonic`）。

## AI 辅助投递流程

这个仓库现在沉淀的是一套可复用流程：

```text
JD → AI 匹配分析 → 选择 PM/Engineer 基础简历 → 定向改写 → ATS/排版检查 → PDF
```

详细说明见：[`docs/AI_RESUME_WORKFLOW.md`](docs/AI_RESUME_WORKFLOW.md)

Prompt 和模板见：

- [`templates/prompts/resume-tailoring.md`](templates/prompts/resume-tailoring.md)
- [`templates/application/README.md`](templates/application/README.md)
- [`templates/checklists/final-review.md`](templates/checklists/final-review.md)

## 投递流程

1. 拿到 JD → 保存到本地私有 `applications/<company_role>/jd.md`
2. 用 AI prompt 做匹配分析和改写建议
3. 选择 `pm/` 或 `engineer/` 方向作为基础版本
4. 只应用真实、可面试解释的修改
5. `tectonic resume.tex` 或 `bash build.sh` 生成 PDF
6. 检查排版、ATS 可读性和隐私 → 投递

> 默认不要提交具体 JD、分析笔记、个人 PDF 或含隐私的定制简历。公开仓库只保留通用流程、模板和可复用方法。
