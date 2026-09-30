"""Offline regression tests; never contact the real attendance service."""
from datetime import datetime
from types import SimpleNamespace
import json

import httpx
import pytest

from zimyo_attendance.tools import zimyo_client


@pytest.fixture
def make_client(monkeypatch):
    clients = []
    monkeypatch.setattr(
        zimyo_client, "get_settings",
        lambda: SimpleNamespace(zimyo_base_url="https://attendance.invalid"),
    )

    def factory(statuses, *, punch_error=None, reject_punch=False):
        statuses = iter(statuses)
        requests = []

        def handle(request):
            requests.append(request)
            if request.url.path.endswith("/check-clock-in-out-status"):
                status = next(statuses)
                if isinstance(status, Exception):
                    raise status
                if status is None:
                    return httpx.Response(503)
                data = {"attendance": {
                    "IN_OUT_STATUS": status,
                    # Both may be populated regardless of current status.
                    "PUNCH_IN_TIME": "2026-09-30 09:00:00",
                    "PUNCH_OUT_TIME": "2026-09-30 15:36:00",
                }}
            else:
                assert request.url.path.endswith("/clock-in-out")
                if punch_error:
                    raise punch_error
                if reject_punch:
                    return httpx.Response(200, json={
                        "error": True, "code": 422, "message": "Punch rejected",
                        "time": 0, "data": {},
                    })
                data = {}
            return httpx.Response(200, json={
                "error": False, "code": 200, "message": "",
                "time": 0, "data": data,
            })

        client = zimyo_client.ZimyoClient()
        client.client.close()
        client.client = httpx.Client(transport=httpx.MockTransport(handle))
        client._authenticated = True
        client._employee_id = 123
        clients.append(client)
        return client, requests

    yield factory
    for client in clients:
        client.close()


def punches(requests):
    return [r for r in requests if r.url.path.endswith("/clock-in-out")]


@pytest.mark.parametrize("action", ["clock_in", "clock_out"])
@pytest.mark.parametrize("status", [None, "", "Unknown", "Break"])
def test_unavailable_or_unknown_status_never_punches(make_client, action, status):
    client, requests = make_client([status])
    assert getattr(client, action)() is False
    assert not punches(requests)
    assert "status" in client.last_action_message.lower()


@pytest.mark.parametrize("status,expected", [("In", True), ("Out", False), (" in ", True)])
def test_status_overrides_presence_of_both_timestamps(make_client, status, expected):
    client, _ = make_client([status])
    attendance = client.get_attendance_status()
    assert attendance.punch_in_time and attendance.punch_out_time
    assert attendance.is_clocked_in is expected


@pytest.mark.parametrize("action,status", [("clock_in", "In"), ("clock_out", "Out")])
def test_already_in_target_state_does_not_toggle(make_client, action, status):
    client, requests = make_client([status])
    assert getattr(client, action)() is True
    assert not punches(requests)
    assert "Already clocked" in client.last_action_message


@pytest.mark.parametrize("action,before,after", [
    ("clock_in", "Out", "In"), ("clock_out", "In", "Out"),
])
def test_punch_is_verified_and_repeat_request_is_safe(make_client, action, before, after):
    client, requests = make_client([before, after, after])
    assert getattr(client, action)() is True
    assert "status verified" in client.last_action_message
    assert client.last_attendance.in_out_status == after
    assert getattr(client, action)() is True
    assert "Already clocked" in client.last_action_message
    assert len(punches(requests)) == 1
    payload = json.loads(punches(requests)[0].content)
    assert payload == {"EMP_ID": 123, "SOURCE": "Web", "DATE": datetime.now().strftime("%Y-%m-%d"), "PLACE": ""}


@pytest.mark.parametrize("action,before", [("clock_in", "Out"), ("clock_out", "In")])
@pytest.mark.parametrize("verification", [None, "Unknown", "unchanged"])
def test_unconfirmed_punch_is_not_reported_as_success_or_retried(make_client, action, before, verification):
    after = before if verification == "unchanged" else verification
    client, requests = make_client([before, after])
    assert getattr(client, action)() is False
    assert len(punches(requests)) == 1
    assert len(requests) == 3
    assert "request accepted" in client.last_action_message
    assert "unconfirmed" in client.last_action_message
    assert "No retry" in client.last_action_message


@pytest.mark.parametrize("action,before", [("clock_in", "Out"), ("clock_out", "In")])
def test_punch_timeout_does_not_retry(make_client, action, before):
    client, requests = make_client([before], punch_error=httpx.ReadTimeout("Timeout"))
    assert getattr(client, action)() is False
    assert len(punches(requests)) == 1
    assert "outcome unconfirmed" in client.last_action_message
    assert client.last_attendance is None


def test_status_timeout_never_punches(make_client):
    client, requests = make_client([httpx.ReadTimeout("Timeout")])
    assert client.clock_in() is False
    assert not punches(requests)


def test_api_rejection_is_reported(make_client):
    client, requests = make_client(["Out"], reject_punch=True)
    assert client.clock_in() is False
    assert "Punch rejected" in client.last_action_message
    assert len(punches(requests)) == 1


@pytest.fixture
def graph_setup(monkeypatch, tmp_path):
    from zimyo_attendance.agent import graph
    settings = SimpleNamespace(
        storage_path=tmp_path / "attendance.json",
        clock_in_window_start="08:55", clock_in_window_end="09:05",
        clock_out_window_start="16:55", clock_out_window_end="17:10",
    )
    monkeypatch.setattr(graph, "get_settings", lambda: settings)
    return graph, settings


@pytest.mark.parametrize("action,status", [("clock_in", "In"), ("clock_out", "Out")])
def test_manual_graph_reports_skip_and_saves_record(graph_setup, make_client, monkeypatch, action, status):
    graph, settings = graph_setup
    initial, _ = make_client([status])
    guard, requests = make_client([status])
    clients = iter([initial, guard])
    monkeypatch.setattr(graph, "create_zimyo_client", lambda: next(clients))
    result = graph.run_attendance_agent(action)
    assert result["success"] is True
    assert result["error"] is None
    assert "Already clocked" in result["result"]
    assert not punches(requests)
    record = json.loads(settings.storage_path.read_text())["records"][0]
    assert "Already clocked" in record["result"]


@pytest.mark.parametrize("action", ["clock_in", "clock_out", "auto"])
@pytest.mark.parametrize("status", [None, "Unknown"])
def test_graph_stops_on_failed_initial_status(graph_setup, make_client, monkeypatch, action, status):
    graph, _ = graph_setup
    client, requests = make_client([status])
    clients = iter([client])
    monkeypatch.setattr(graph, "create_zimyo_client", lambda: next(clients))
    result = graph.run_attendance_agent(action)
    assert result["success"] is False
    assert result["error"]
    assert not punches(requests)


@pytest.mark.parametrize("hour,before,after", [
    (9, "Out", "In"), (17, "In", "Out"),
    (9, "In", None), (17, "Out", None),
])
def test_auto_uses_current_status_and_time_window(graph_setup, make_client, monkeypatch, hour, before, after):
    graph, _ = graph_setup

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            value = cls(2026, 9, 30, hour, 0)
            return tz.localize(value) if tz else value

    monkeypatch.setattr(graph, "datetime", FixedDatetime)
    initial, _ = make_client([before])
    guard, requests = make_client([before, after])
    clients = iter([initial, guard])
    monkeypatch.setattr(graph, "create_zimyo_client", lambda: next(clients))
    result = graph.run_attendance_agent("auto")
    assert result["success"] is True
    assert result["error"] is None
    assert len(punches(requests)) == (1 if after else 0)


def test_client_rechecks_state_after_graph_snapshot(graph_setup, make_client, monkeypatch):
    graph, _ = graph_setup
    initial, _ = make_client(["Out"])
    guard, requests = make_client(["In"])
    clients = iter([initial, guard])
    monkeypatch.setattr(graph, "create_zimyo_client", lambda: next(clients))
    result = graph.run_attendance_agent("clock_in")
    assert result["success"] is True
    assert "Already clocked in" in result["result"]
    assert not punches(requests)


def test_graph_preserves_unconfirmed_result(graph_setup, make_client, monkeypatch):
    graph, settings = graph_setup
    initial, _ = make_client(["In"])
    guard, requests = make_client(["In", None])
    clients = iter([initial, guard])
    monkeypatch.setattr(graph, "create_zimyo_client", lambda: next(clients))
    result = graph.run_attendance_agent("clock_out")
    assert result["success"] is False
    assert "request accepted" in result["error"]
    assert "unconfirmed" in result["result"]
    assert len(punches(requests)) == 1
    record = json.loads(settings.storage_path.read_text())["records"][0]
    assert record["success"] is False
    assert "unconfirmed" in record["error"]


def test_cli_exits_with_failure_for_unconfirmed_action(monkeypatch):
    import sys
    from zimyo_attendance import __main__ as cli
    monkeypatch.setattr(sys, "argv", ["zimyo_attendance", "clock_out"])
    monkeypatch.setattr(cli, "run_attendance_agent", lambda action: {
        "success": False, "result": "Outcome unconfirmed", "error": "Outcome unconfirmed",
    })
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
