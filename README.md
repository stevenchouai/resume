# Steven Chou — Resume

双线简历系统：PM 和 Engineer 两个方向独立维护、定制化投递。

## 目录结构

```
resume/
├── pm/                  # 产品经理方向
│   └── resume.tex
├── engineer/            # 工程师方向
│   └── resume.tex
├── tools/               # 本地 JD/Resume 匹配分析 CLI
├── tests/               # 脱敏样例与自动化测试
├── docs/examples/       # 脱敏样例输出
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
JD → 本地匹配报告 → AI 深度分析 → 选择 PM/Engineer 基础简历 → 定向改写 → ATS/排版检查 → PDF
```

详细说明见：[`docs/AI_RESUME_WORKFLOW.md`](docs/AI_RESUME_WORKFLOW.md)

本仓库的投递判断、目录命名、PDF 命名和真实性边界见：[`docs/APPLICATION_RULES.md`](docs/APPLICATION_RULES.md)

Prompt 和模板见：

- [`templates/prompts/resume-tailoring.md`](templates/prompts/resume-tailoring.md)
- [`templates/application/README.md`](templates/application/README.md)
- [`templates/checklists/final-review.md`](templates/checklists/final-review.md)

## 本地 JD/Resume 匹配报告

可以先用本地 CLI 做一版确定性的匹配报告，不调用外部服务，也不会修改基础简历：

```bash
python3 tools/resume_jd_tailor.py \
  applications/YYYY-MM/<company_role>__<category>/jd.md \
  engineer/resume.tex \
  --output applications/YYYY-MM/<company_role>__<category>/match-report.md
```

报告包含：

- match score
- JD keywords
- missing keywords
- resume evidence hits
- bullet rewrite suggestions
- no-fabrication guardrails

脱敏样例：

```bash
python3 tools/resume_jd_tailor.py \
  tests/fixtures/sanitized_jd.md \
  tests/fixtures/sanitized_resume.tex \
  --output docs/examples/sanitized-tailoring-report.md
```

查看样例输出：[`docs/examples/sanitized-tailoring-report.md`](docs/examples/sanitized-tailoring-report.md)

运行测试：

```bash
python3 -m unittest discover -v
```

## 投递流程

1. 拿到 JD → 先判断平台、职能和 ownership 是否值得投
2. 保存到本地私有 `applications/YYYY-MM/<company_role>__<category>/jd.md`
3. 运行本地 CLI 生成 `match-report.md`，先看关键词覆盖和缺口
4. 用 AI prompt 做更深的匹配分析和改写建议
5. 选择 `pm/`、`engineer/` 或 hybrid 方向作为基础版本
6. 只应用真实、可面试解释的修改
7. `tectonic resume.tex` 生成 PDF，并重命名为 `Steven_Chou_<Company>_<Role>.pdf`
8. 检查排版、ATS 可读性、机会优先级和隐私 → 决定是否投递

> 默认不要提交具体 JD、分析笔记、个人 PDF 或含隐私的定制简历。公开仓库只保留通用流程、模板和可复用方法。
