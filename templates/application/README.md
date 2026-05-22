# Application Workspace Template

Use this folder structure for one targeted application.

This folder is intended to stay private unless you deliberately sanitize it.

Folder naming convention:

```text
applications/YYYY-MM/<company_role>__<category>/
```

## Files

```text
jd.md          # Paste the job description here
analysis.md    # AI fit analysis and rewrite plan
resume.tex     # Tailored LaTeX resume for this role
Steven_Chou_<Company>_<Role>.pdf  # Generated PDF output
```

## Recommended process

1. Decide whether the role is worth applying to: platform lift, function lift, ownership lift, or a clear strategic reason.
2. Paste the JD into `jd.md`.
3. Run the prompt in `templates/prompts/resume-tailoring.md` with:
   - `jd.md`
   - the closest base resume from `pm/` or `engineer/`
4. Save the AI analysis to `analysis.md`.
5. Copy the base resume to this folder:

```bash
cp ../../engineer/resume.tex resume.tex
# or
cp ../../pm/resume.tex resume.tex
```

6. Apply only truthful, defensible edits.
7. Build:

```bash
tectonic resume.tex
```

8. Rename output to a professional role-specific filename:

```bash
mv resume.pdf Steven_Chou_<Company>_<Role>.pdf
```

## Final checklist

- [ ] One-page resume unless the target market expects otherwise
- [ ] Opportunity is worth applying to, or explicitly marked as backup / low priority
- [ ] Important JD keywords appear naturally
- [ ] Each major bullet has impact, scale, or specificity
- [ ] No invented claims
- [ ] Missing or stale skills are not hidden as current strengths
- [ ] No private identifiers committed
- [ ] PDF text is selectable
- [ ] Filename is professional and role-specific
