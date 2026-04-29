# Application Workspace Template

Use this folder structure for one targeted application.

This folder is intended to stay private unless you deliberately sanitize it.

## Files

```text
jd.md          # Paste the job description here
analysis.md    # AI fit analysis and rewrite plan
resume.tex     # Tailored LaTeX resume for this role
final.pdf      # Generated PDF output
```

## Recommended process

1. Paste the JD into `jd.md`.
2. Run the prompt in `templates/prompts/resume-tailoring.md` with:
   - `jd.md`
   - the closest base resume from `pm/` or `engineer/`
3. Save the AI analysis to `analysis.md`.
4. Copy the base resume to this folder:

```bash
cp ../../engineer/resume.tex resume.tex
# or
cp ../../pm/resume.tex resume.tex
```

5. Apply only truthful, defensible edits.
6. Build:

```bash
tectonic resume.tex
```

7. Rename output if needed:

```bash
mv resume.pdf final.pdf
```

## Final checklist

- [ ] One-page resume unless the target market expects otherwise
- [ ] Important JD keywords appear naturally
- [ ] Each major bullet has impact, scale, or specificity
- [ ] No invented claims
- [ ] No private identifiers committed
- [ ] PDF text is selectable
- [ ] Filename is professional and role-specific
