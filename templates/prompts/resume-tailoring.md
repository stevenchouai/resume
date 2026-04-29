# Resume Tailoring Prompt

Use this prompt with an AI assistant when tailoring a resume to a specific job description.

## Input

```text
<Job Description>
[Paste JD here]
</Job Description>

<Base Resume>
[Paste the most relevant base resume here, e.g. pm/resume.tex or engineer/resume.tex]
</Base Resume>

<Constraints>
- Keep the resume truthful and interview-defensible.
- Do not invent experience, employers, credentials, or metrics.
- Prefer one page unless the local job market expects otherwise.
- Preserve LaTeX syntax and compileability.
- Optimize for ATS readability and fast recruiter comprehension.
</Constraints>
```

## Task

Act as a senior recruiter, hiring manager, and resume editor. Analyze the JD against the base resume and produce a targeted resume plan.

Return the output in this structure:

### 1. Role understanding

- What the company is really hiring for
- Must-have skills
- Nice-to-have skills
- Seniority / ownership signals
- Domain-specific vocabulary

### 2. Match score

Give a score from 0–100 and explain:

- strongest fit evidence
- biggest gaps
- likely recruiter objections
- whether this is worth applying to

### 3. Keyword map

Create a table:

| JD keyword / requirement | Resume evidence | Current strength | Rewrite recommendation |
|---|---|---:|---|

### 4. Rewrite plan

Recommend targeted edits by section:

- headline / summary, if present
- skills
- experience bullets
- projects
- education / certifications, if relevant

For each rewritten bullet:

- use the XYZ formula: **Accomplished X, measured by Y, by doing Z**
- keep claims truthful
- preserve LaTeX formatting
- avoid keyword stuffing

### 5. ATS and formatting scan

Flag:

- parsing risks
- overly dense lines
- weak verbs
- missing keywords
- repeated claims
- bullets that may sound exaggerated

### 6. Final tailored LaTeX patch

Provide a minimal patch or replacement snippets for the base resume. Do not rewrite unrelated sections.

### 7. Interview defense

For the top 5 strongest tailored bullets, provide:

- the likely interviewer follow-up question
- the real story the candidate must be able to tell
- risk level if challenged

## Output standard

Be direct. Prioritize interview probability, not sounding impressive. If the candidate is weak for the role, say so and recommend either a different angle or not applying.
