# AI-Assisted Resume Tailoring Workflow

This repository is not just a LaTeX resume template. It is a repeatable workflow for turning a job description into a targeted, ATS-friendly resume variant.

The core idea:

> Paste a JD into an AI assistant, let it analyze fit, choose the right resume base, rewrite only the relevant bullets, then compile a polished PDF.

The repository also includes a local CLI for a first-pass match report before deeper AI analysis.

This is designed for job seekers who need to apply with precision without spending hours manually reformatting every resume.

## What this workflow does

1. **Opportunity triage** — decide whether the role is worth pursuing based on platform, function, ownership, and truthful fit.
2. **JD intake** — save the target job description in a private monthly application folder.
3. **Local match report** — run the deterministic CLI to get keyword coverage, missing terms, evidence hits, and no-fabrication rewrite prompts.
4. **Role fit analysis** — extract responsibilities, required skills, keywords, seniority signals, hidden evaluation criteria, and hard gaps.
5. **Resume direction selection** — choose the closest base resume, e.g. product-oriented, engineering-oriented, or a hybrid owner version.
6. **Targeted rewriting** — rewrite bullets using measurable impact, the XYZ formula, and the language of the JD.
7. **ATS scan** — check keyword coverage, layout risks, title alignment, and recruiter readability.
8. **PDF build** — compile the final LaTeX resume into a role-specific PDF.
9. **Review packet** — keep a short analysis note explaining why the version is targeted and whether it is worth submitting.

## Repository layout

```text
resume/
├── pm/                    # Product-oriented base resume
├── engineer/              # Engineering-oriented base resume
├── tools/                 # Local workflow CLI tools
├── tests/                 # Sanitized fixtures and automated tests
├── skills/resume-reviewer/ # AI resume review skill and references
├── templates/             # Sanitized workflow templates
├── docs/                  # Public workflow documentation
└── build.sh               # Compile base resumes
```

Private application material should stay out of git by default. Organize applications by month with one directory level under the month:

```text
applications/YYYY-MM/<company_role>__<category>/
├── jd.md                  # Private JD copy
├── analysis.md            # Private AI fit analysis
├── resume.tex             # Private tailored resume variant
├── match-report.md         # Local deterministic match report
└── Steven_Chou_<Company>_<Role>.pdf
```

Rules for naming, opportunity triage, and truthfulness boundaries are maintained in [`docs/APPLICATION_RULES.md`](APPLICATION_RULES.md).

## Quick start

### 1. Create a private application folder

```bash
mkdir -p applications/YYYY-MM/<company_role>__<category>
cp templates/application/README.md applications/YYYY-MM/<company_role>__<category>/README.md
```

Save the JD as:

```text
applications/YYYY-MM/<company_role>__<category>/jd.md
```

### 2. Generate a local match report

Run the local CLI before asking for deeper AI help:

```bash
python3 tools/resume_jd_tailor.py \
  applications/YYYY-MM/<company_role>__<category>/jd.md \
  engineer/resume.tex \
  --output applications/YYYY-MM/<company_role>__<category>/match-report.md
```

Use `pm/resume.tex` instead of `engineer/resume.tex` when the PM base is closer to the JD.

The report includes:

- match score
- missing keywords
- JD keywords
- evidence hits from the base resume
- bullet rewrite suggestions grounded in existing evidence

The CLI is intentionally conservative: missing keywords are reported as gaps and should not be added unless they are true and interview-defensible. It does not modify the base resume.

Sanitized sample input/output is available at:

- `tests/fixtures/sanitized_jd.md`
- `tests/fixtures/sanitized_resume.tex`
- `docs/examples/sanitized-tailoring-report.md`

### 3. Ask AI for the fit analysis

Use `templates/prompts/resume-tailoring.md` as the prompt. Provide:

- the JD
- the closest base resume: `pm/resume.tex` or `engineer/resume.tex`
- optionally, the local `match-report.md`
- any constraints, e.g. one page, ATS-friendly, no fabrication

Expected output:

```text
applications/YYYY-MM/<company_role>__<category>/analysis.md
```

The analysis should include:

- whether the opportunity is worth applying to
- platform / function / ownership lift
- match score
- top missing keywords
- strongest transferable evidence
- risky claims to avoid
- proposed bullet rewrites
- final checklist before submission

### 4. Create the tailored resume

Copy the closest base resume:

```bash
cp engineer/resume.tex applications/YYYY-MM/<company_role>__<category>/resume.tex
# or
cp pm/resume.tex applications/YYYY-MM/<company_role>__<category>/resume.tex
```

Then apply only the AI-recommended changes that are true and defensible.

### 5. Compile the PDF

From the application folder:

```bash
tectonic resume.tex
mv resume.pdf Steven_Chou_<Company>_<Role>.pdf
```

Or compile the base resumes:

```bash
bash build.sh
```

If `tectonic` is not installed, skip the PDF build and still run the local checks/tests for workflow changes:

```bash
python3 -m unittest discover -v
```

## Quality bar

A good tailored resume should satisfy all of these:

- **Truthful** — no inflated claims, no invented domain experience.
- **Worth applying to** — the role offers platform lift, function lift, ownership lift, or another explicit reason to spend time on it.
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
JD → local match report → AI analysis → targeted rewrite → ATS check → polished PDF
```

The result is a resume that feels intentionally written for the role instead of lightly rebranded.
