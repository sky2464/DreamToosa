# Synthetic Plan and Backlog

## 1. Open Review Findings

### 1.1 Engineering Review

#### 1.1.1 Architecture

| ID | Sev | Location | Finding | Recommendation |
|----|-----|----------|---------|----------------|
| A1 | Critical | `src/engine/pay.ts:44-52` | synthetic wallet state corrupt after reload | synthetic recommendation |
| A2 | High | `src/engine/pay.ts:90` | synthetic naming drift | synthetic recommendation |

#### 1.1.2 Types

| ID | Sev | Location | Finding | Recommendation |
|----|-----|----------|---------|----------------|
| TC1 | Critical | `src/engine/roll.ts:90` | synthetic missing coverage for roll resolution | synthetic recommendation |
| UX-R1 | Critical | n/a | synthetic layout reflow on resize | synthetic recommendation |

### 1.3 Test Coverage

#### 1.3.1 Critical gaps

| ID | Sev | File | Gap |
|----|-----|------|-----|
| TC9 | Critical | `src/engine/odds.ts:1` | synthetic secret handling gap |

## 4. Resolved Items

| ID | Sev | Location | Finding | Recommendation |
|----|-----|----------|---------|----------------|
| A7 | Critical | `src/engine/old.ts:10` | synthetic leak fixed earlier | synthetic note |
