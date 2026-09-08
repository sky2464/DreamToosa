# Reports

Output of the **"Dream Report – Daily Code Review"** routine. See
[`../dreamtoosa/README.md`](../dreamtoosa/README.md) for how it is produced.

```
reports/
├── dream-report-YYYY-MM-DD.md     ← per-run index across all repos
├── AgToosa/
│   └── dream-report-YYYY-MM-DD.md
├── Crapsino/
├── DreamToosa/
└── miToosa/
```

The index carries the status table (repo · commits reviewed · findings · skipped
reason) and names which repo held the fix rotation that run. Per-repo files carry
the detail: what improved, what needs attention, and up to three prioritized
action items.

Reports for **every** target repo land here rather than in the target repos
themselves — one merge point, and target repos stay clean.
