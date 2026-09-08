# Spec — DEV-002: Root README and Control-Plane CI

- **ID:** DEV-002
- **Epic:** DEV-100
- **Type:** Chore
- **Status:** Shipped
- **Created:** 2026-09-07
- **Shipped:** 2026-09-08

---

## 1. Goal Contract

### 1.1 Goal
Provide clear repository orientation and automated invariant testing for the DreamToosa control plane to catch configuration errors before routine execution.

### 1.2 User Outcome
Maintainers and scheduled agents can trust that manifest (`repos.yml`) and cross-run state (`state.json`) adhere to required schemas, rotation constraints, and profile mappings.

### 1.3 Success Condition
- `dreamtoosa/validate.py` implements 16 invariant checks.
- `.github/workflows/control-plane.yml` runs on push and PR touching `dreamtoosa/`.
- Root `README.md` documents repository layout and canonical Dreams references.

### 1.4 Proof / Evidence
- CI runs green on PR #5 and PR #6.
- Local `dreamtoosa/validate.py` execution passes 16/16 checks.

---

## 2. Acceptance Criteria

| ID | Priority | Description | Verification |
|----|----------|-------------|--------------|
| AC-1 | Must | Control-plane validator checks manifest syntax and cross-run state parity | `python3 dreamtoosa/validate.py` exits 0 |
| AC-2 | Must | CI workflow triggers on control plane modifications and fails on invalid configurations | GitHub Actions workflow execution |
| AC-3 | Must | Root README indexes active vs legacy documentation | File inspection |

---

## ✅ Spec Approved
- **Approved by:** Chicademy & Navid
- **Timestamp:** 2026-09-07T22:30:00Z
