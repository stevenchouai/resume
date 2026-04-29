# AI-Assisted Resume Tailoring Workflow

This repository is not just a LaTeX resume template. It is a repeatable workflow for turning a job description into a targeted, ATS-friendly resume variant.

The core idea:

> Paste a JD into an AI assistant, let it analyze fit, choose the right resume base, rewrite only the relevant bullets, then compile a polished PDF.

This is designed for job seekers who need to apply with precision without spending hours manually reformatting every resume.

## What this workflow does

1. **JD intake** — save the target job description in a private application folder.
2. **Role fit analysis** — extract responsibilities, required skills, keywords, seniority signals, and hidden evaluation criteria.
3. **Resume direction selection** — choose the closest base resume, e.g. product-oriented or engineering-oriented.
4. **Targeted rewriting** — rewrite bullets using measurable impact, the XYZ formula, and the language of the JD.
5. **ATS scan** — check keyword coverage, layout risks, title alignment, and recruiter readability.
6. **PDF build** — compile the final LaTeX resume into a role-specific PDF.
7. **Review packet** — keep a short analysis note explaining why the version is targeted.

## Repository layout

```text
resume/
├── pm/                    # Product-oriented base resume
├── engineer/              # Engineering-oriented base resume
├── skills/resume-reviewer/ # AI resume review skill and references
├── templates/             # Sanitized workflow templates
├── docs/                  # Public workflow documentation
└── build.sh               # Compile base resumes
```

Private application material should stay out of git by default:

```text
applications/<company_role>/
├── jd.md                  # Private JD copy
├── analysis.md            # Private AI fit analysis
├── resume.tex             # Private tailored resume variant
└── final.pdf              # Private generated output
```

## Quick start

### 1. Create a private application folder

```bash
mkdir -p applications/<company_role>
cp templates/application/README.md applications/<company_role>/README.md
```

Save the JD as:

```text
applications/<company_role>/jd.md
```

### 2. Ask AI for the fit analysis

Use `templates/prompts/resume-tailoring.md` as the prompt. Provide:

- the JD
- the closest base resume: `pm/resume.tex` or `engineer/resume.tex`
- any constraints, e.g. one page, ATS-friendly, no fabrication

Expected output:

```text
applications/<company_role>/analysis.md
```

The analysis should include:

- match score
- top missing keywords
- strongest transferable evidence
- risky claims to avoid
- proposed bullet rewrites
- final checklist before submission

### 3. Create the tailored resume

Copy the closest base resume:

```bash
cp engineer/resume.tex applications/<company_role>/resume.tex
# or
cp pm/resume.tex applications/<company_role>/resume.tex
```

Then apply only the AI-recommended changes that are true and defensible.

### 4. Compile the PDF

From the application folder:

```bash
tectonic resume.tex
```

Or compile the base resumes:

```bash
bash build.sh
```

## Quality bar

A good tailored resume should satisfy all of these:

- **Truthful** — no inflated claims, no invented domain experience.
- **Specific** — bullets include scale, constraints, tools, impact, or measurable outcomes.
- **JD-aligned** — mirrors important keywords without keyword stuffing.
- **ATS-safe** — simple structure, readable section names, PDF text selectable.
- **Recruiter-fast** — the first 10 seconds should make the role fit obvious.
- **Interview-defensible** — every bullet can be backed up with a real story.

## Privacy rules

Do not commit:

- generated PDFs
- private JDs
- company-specific analysis notes
- phone numbers, addresses, private emails, or personal identifiers
- unreleased employer details or confidential metrics

Keep public docs generic and template-driven. Keep application-specific work in ignored folders unless deliberately sanitized.

## Why this matters

Most candidates either apply with a generic resume or spend too much time manually editing. This workflow makes high-quality tailoring cheap enough to do repeatedly:

```text
JD → AI analysis → targeted rewrite → ATS check → polished PDF
```

The result is a resume that feels intentionally written for the role instead of lightly rebranded.