# LaTeX 间距调整教程

针对本项目 resume.tex 的排版微调指南。

## 核心概念

LaTeX 中控制垂直间距的几种方式，按优先级排列：

| 命令 | 作用 | 示例 |
|------|------|------|
| `\vspace{Xpt}` | 插入固定垂直间距（正值加大，负值缩小） | `\vspace{4pt}` |
| `\\[Xpt]` | 行末换行并加额外间距 | `\\[2pt]` |
| 空行 | 产生段落间距（`\parskip`） | 通常 0pt+1pt |
| `%` 行尾 | 阻止换行产生额外空白 | `}%` |

## 常见调整场景

### 1. Heading 和下方文字太近/太远

```latex
% 调整 experienceHeading 定义中的 vspace
\newcommand{\experienceHeading}[2]{
  \vspace{3pt}          % ← 控制 heading 上方间距
  \noindent\begin{tabular*}{\textwidth}[t]{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #2 \\
  \end{tabular*}\vspace{-2pt}  % ← 控制 heading 下方间距
}
```

**示例**：成都理工和百篇优秀论文之间太近？在中间加间距：

```latex
\experienceHeading{成都理工大学 -- ...}{2020.09 -- 2024.07}
\vspace{1pt}    % ← 加这一行，增加 1pt 间距
\small{百篇优秀学士学位论文 ...}
```

### 2. 同一 section 内子标题间距过大

用 `\tightHeading` 替代 `\experienceHeading`（已在 PM 简历中定义）：

```latex
% tightHeading: 上方 2pt，下方 -5pt（比 experienceHeading 更紧凑）
\newcommand{\tightHeading}[2]{
  \vspace{2pt}
  \noindent\begin{tabular*}{\textwidth}[t]{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #2 \\
  \end{tabular*}\vspace{-5pt}
}
```

### 3. 文字溢出一两个字到下一行

**方法 A**：缩短措辞（推荐）

```latex
% 改前（溢出 2 字）
\item 设计Pipeline自动门禁系统，集成风险扫描、合规校验与自动化回归卡点，实现高风险操作自动拦截与可追溯审计

% 改后（收回来了）
\item 设计Pipeline自动门禁，集成风险扫描、合规校验与回归卡点，实现高风险操作自动拦截与审计追溯
```

**方法 B**：微调页边距（影响全局，慎用）

```latex
% 在 preamble 中调整，每次 0.05in 递增测试
\addtolength{\textwidth}{0.05in}
\addtolength{\oddsidemargin}{-0.025in}
```

**方法 C**：局部缩小字号

```latex
{\footnotesize 这一行会稍微小一点，能多塞几个字}
```

### 4. Section 之间的间距

由 `\titleformat` 控制：

```latex
\titleformat{\section}{
  \vspace{-4pt}    % ← section 标题上方间距（负值=更紧）
  \bfseries\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]  % ← 标题下方横线后间距
```

### 5. 列表项之间的间距

```latex
\begin{enumerate}[
  leftmargin=*,   % 缩进
  nosep           % 无额外间距（最紧凑）
]
```

如果想要微调列表项之间的间距：

```latex
\begin{enumerate}[
  leftmargin=*,
  itemsep=2pt,    % 项目之间
  topsep=2pt,     % 列表与上方文字之间
  parsep=0pt,     % 段落间（通常 0）
]
```

## 调试技巧

1. **先编译查看效果**：每次只改一个间距值，编译后对比 PDF
2. **pt 参考**：1pt ≈ 0.35mm，6pt ≈ 1 行间距的一半
3. **负值可用**：`\vspace{-3pt}` 可以让内容往上"吃"空间
4. **编译命令**：`cd pm && tectonic resume.tex`（单独编译某个方向快速查看）
