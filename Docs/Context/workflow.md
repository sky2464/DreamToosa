# Workflow Configuration

<!-- Fill in during /agtoosa-init. These values drive build and review behavior. -->

## TDD

tdd: true
<!-- Red-Green-Refactor is enforced in /agtoosa-build by default (AgToosa is a TDD framework). Set to false to relax strict ordering. -->

## Coverage

coverage_threshold: 80
<!-- Minimum test coverage % required by /agtoosa-review QA Lead and /agtoosa-qa -->

## Branch Naming

branch_naming: "feat/ISSUE-ID-SHORT-DESC"
<!-- Pattern for feature branches (e.g., feat/DEV-123-add-login) -->

## Commit Strategy

commit_strategy: "conventional"
<!-- Options: conventional | free-form -->

## Linting

linter: ""
<!-- Tool used (e.g., eslint, ruff, golangci-lint) -->

lint_config: ""
<!-- Config file path (e.g., .eslintrc.json, pyproject.toml) -->

## Cross-model review

cross_model: recommended
<!-- off | on-demand | recommended | required — controls independent reviewer subagents during /agtoosa-review (see Docs/AgToosa_CrossModelReview.md) -->

reviewer_model: parent
<!-- parent | ask — parent = same model tier as this chat unless user approves premium; ask = always confirm model before delegating -->

## Notes
<!-- Add team workflow rules, code review requirements, or release policies here. -->

## Standing Corrections

Dated, deduped always/never lessons from **AgToosa Project Intake**. Agents must read this section before classifying freeform asks (see `Docs/AgToosa_Agent.md` → Project Intake Protocol).

| Date | Correction | Origin |
|------|------------|--------|
| _(none yet)_ | — | — |

Dedupe: if an equivalent correction already exists, refresh the date instead of adding a duplicate row. Do not store secrets — record intent only.
