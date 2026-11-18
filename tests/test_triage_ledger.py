#!/usr/bin/env python3
"""Ledger carry-forward tests (DEV-005b TRI-B-001..008)."""
import hashlib
import unittest
import dreamtoosa.triage as t

DAY = "2026-10-13"
PUB = "C1:fixture-owner/AgToosa:#11"

def finding(fid, rule, sev, public=True, repo="fixture-owner/AgToosa"):
    return {"id": fid, "rule": rule, "sev": sev, "public": public, "repo": repo}

def wrap(comment):
    return "<!-- fleet-triage:begin -->\n" + comment + "\n<!-- fleet-triage:end -->\n"

class TestLedgerCarryForward(unittest.TestCase):
    def test_new_carried_escalated_downgraded_keep_first_seen(self):
        prev_rows = [
            {"id": PUB, "rule": "C1", "sev": "HIGH", "first_seen": "2026-10-01", "last_seen": "2026-10-12", "misses": 0, "status": "OPEN"},
            {"id": "U1:fixture-owner/AgToosa:ci.yml", "rule": "U1", "sev": "URGENT", "first_seen": "2026-09-01", "last_seen": "2026-10-12", "misses": 0, "status": "OPEN"},
        ]
        prev = t.Ledger(t._LSCH, "2026-10-12", prev_rows, t._ng())
        cur = [finding(PUB, "C1", "CRITICAL"), finding("U1:fixture-owner/AgToosa:ci.yml", "H1", "HIGH"), finding("H2:fixture-owner/AgToosa:ci.yml", "H2", "HIGH")]
        deltas, led = t.merge_ledger(cur, set(), prev, DAY)
        by = {d["id"]: d for d in deltas}
        self.assertEqual(by[PUB]["delta"], "ESCALATED")
        self.assertEqual(by["U1:fixture-owner/AgToosa:ci.yml"]["delta"], "DOWNGRADED")
        self.assertEqual(by["U1:fixture-owner/AgToosa:ci.yml"]["rule"], "H1")
        self.assertEqual(by["H2:fixture-owner/AgToosa:ci.yml"]["delta"], "NEW")
        stored = {r["id"]: r for r in led.findings}
        self.assertEqual(stored[PUB]["first_seen"], "2026-10-01")
        self.assertEqual(stored["H2:fixture-owner/AgToosa:ci.yml"]["first_seen"], DAY)
        self.assertNotIn("--", t.serialize_ledger(led).split(" ", 2)[2].split(" -->")[0].replace("-\\u002d", ""))

class TestResolution(unittest.TestCase):
    def prev(self, misses=0):
        row = {"id": PUB, "rule": "C1", "sev": "HIGH", "first_seen": "2026-10-01", "last_seen": "2026-10-12", "misses": misses, "status": "OPEN"}
        return t.Ledger(t._LSCH, "2026-10-12", [row], t._ng())
    def test_evidence_resolves_and_is_not_stored(self):
        deltas, led = t.merge_ledger([], set(), self.prev(), DAY, [{"id": PUB, "covers_first_seen": True}])
        self.assertEqual(deltas[0]["delta"], "RESOLVED")
        self.assertEqual(led.findings, [])
    def test_evidence_that_does_not_cover_first_seen_is_a_miss(self):
        deltas, led = t.merge_ledger([], set(), self.prev(), DAY, [{"id": PUB, "covers_first_seen": False}])
        self.assertEqual(deltas[0]["text"], "Pending resolution (miss 1/2)")
        self.assertEqual(led.findings[0]["misses"], 1)
    def test_two_misses_resolve_and_not_evaluable_does_not(self):
        deltas, led = t.merge_ledger([], set(), self.prev(1), DAY)
        self.assertEqual(deltas[0]["by"], "two-miss")
        self.assertEqual(led.findings, [])
        deltas, led = t.merge_ledger([], {"C1"}, self.prev(), DAY)
        self.assertTrue(deltas[0].get("not_evaluable"))
        self.assertEqual(led.findings[0]["misses"], 0)

class TestLedgerIntegrity(unittest.TestCase):
    def ledger(self):
        _d, led = t.merge_ledger([finding(PUB, "C1", "HIGH")], set(), None, DAY)
        return led
    def test_round_trip_and_baseline(self):
        led = self.ledger()
        text = wrap(t.serialize_ledger(led))
        again = t.serialize_ledger(t.parse_ledger(text))
        self.assertEqual(again, t.serialize_ledger(led))
        self.assertEqual(t.parse_ledger(wrap("## Fleet Triage\n")).code, "BASELINE")
        self.assertIn("-\\u002d", t.serialize_ledger(t.Ledger(t._LSCH, DAY, [{"id": "H1:fixture-owner/AgToosa:a--b.yml", "rule": "H1", "sev": "HIGH", "first_seen": DAY, "last_seen": DAY, "misses": 0, "status": "OPEN"}], {"id": "DEV-153", "since": DAY, "status": "OPEN"})))
    def test_malformed_inputs_return_codes_and_hide_secrets(self):
        base = wrap(t.serialize_ledger(self.ledger()))
        self.assertEqual(t.parse_ledger(base + base).code, "E_LEDGER_DUP")
        secret = "gh" + "p_" + "a" * 20
        bad = base.replace(PUB, secret)
        err = t.parse_ledger(bad)
        self.assertEqual(err.code, "E_SECRET_PATTERN")
        self.assertEqual(err.field, "ledger")
        self.assertNotIn(secret, err.code + err.field)
        self.assertEqual(t.parse_ledger(wrap("<!-- fleet-triage-ledger:v1 {\"schema\":1} -->")).code, "E_LEDGER_SCHEMA")
        forged = base.replace("fleet-triage:end", "fleet-triage:end --> <!-- fleet-triage:begin -->")
        self.assertIn(t.parse_ledger(forged).code, ("E_LEDGER_MARKERS", "E_LEDGER_DUP", "E_LEDGER_SCHEMA"))

class TestPrivateOpaqueKeys(unittest.TestCase):
    def test_private_finding_is_an_opaque_key_with_no_title_or_path(self):
        canonical = "C1:sky2464/Crapsino:src/pay.ts"
        opaque = "P-" + hashlib.sha256(canonical.encode()).hexdigest()[:12]
        self.assertEqual(t.opaque_key(canonical), opaque)
        deltas, led = t.merge_ledger([finding(canonical, "C1", "CRITICAL", public=False, repo="sky2464/Crapsino")], set(), None, DAY)
        blob = t.serialize_ledger(led) + deltas[0]["id"]
        self.assertIn(opaque, blob)
        for hidden in ("Crapsino", "src/pay.ts", "pay.ts"):
            self.assertNotIn(hidden, blob)
        msg = t.notify_message(["READ_ONLY"], [deltas[0]["id"]], DAY)
        self.assertNotIn("src/pay.ts", msg)
        self.assertRegex(msg, r"^[A-Za-z0-9:/_.#\- ,]{1,200}$")

class TestSerializeRoundTrip(unittest.TestCase):
    def test_plan_id_and_opaque_golden_round_trip(self):
        for gid in ("DEV-153", t.opaque_key("BL-42")):
            led = t.Ledger(t._LSCH, DAY, [], {"id": gid, "since": DAY, "status": "OPEN"})
            self.assertEqual(t.parse_ledger(wrap(t.serialize_ledger(led))).golden["id"], gid)

if __name__ == "__main__":
    unittest.main()
