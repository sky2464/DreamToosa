"""Offline tests for DreamsClient using a fake SDK client. Run: python3 -m pytest -q  (or python3 this file)."""
from types import SimpleNamespace as NS

import dreams_implementation as di


class FakeDreams:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.created = None
        self.canceled = []

    def create(self, **kw):
        self.created = kw
        return NS(id="drm_1", status="pending")

    def retrieve(self, _id):
        s = self.statuses.pop(0)
        outs = [NS(type="memory_store", memory_store_id="memstore_out")] if s == "completed" else []
        return NS(id="drm_1", status=s, outputs=outs, error="boom" if s == "failed" else None,
                  usage=NS(input_tokens=5, output_tokens=2), session_id="sesn_x")

    def cancel(self, i):
        self.canceled.append(i)


def make(statuses):
    d = FakeDreams(statuses)
    return di.DreamsClient(NS(beta=NS(dreams=d))), d


def test_create_shape_and_validation():
    dc, d = make([])
    dc.create("memstore_1", ["s1", "s2"], "focus", "claude-opus-5-5")
    assert d.created["inputs"] == [
        {"type": "memory_store", "memory_store_id": "memstore_1"},
        {"type": "sessions", "session_ids": ["s1", "s2"]},
    ]
    assert d.created["instructions"] == "focus"
    for bad in (lambda: dc.create("m", ["s"] * 101), lambda: dc.create("m", model="gpt-x")):
        try:
            bad()
            assert False
        except ValueError:
            pass


def test_run_completes_and_returns_output_store():
    dc, _ = make(["pending", "running", "completed"])
    r = dc.run("memstore_1", poll_s=0)
    assert r.status == "completed" and r.output_store_id == "memstore_out"


def test_run_failed_raises():
    dc, _ = make(["running", "failed"])
    try:
        dc.run("memstore_1", poll_s=0)
        assert False
    except di.DreamError as e:
        assert "failed" in str(e)


def test_timeout():
    dc, _ = make(["running"] * 5)
    try:
        dc.wait("drm_1", poll_s=0, timeout_s=-1)
        assert False
    except di.DreamError:
        pass


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
