import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from tracker import Tracker


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        config = root / "config.json"
        config.write_text(json.dumps({"endpoint": "https://collector.test", "admin_token": "test"}))
        self.tracker = Tracker(config, root / "state.sqlite3")
        self.tracker.notify = Mock(return_value=True)

    def tearDown(self):
        self.directory.cleanup()

    def response(self, events):
        return {"total": 101, "tests": 0, "events": events, "recent": [], "latest_seq": 101}

    def test_backlog_pages_and_persistent_cursor_do_not_lose_or_repeat_notifications(self):
        events = [{"seq": n, "first_seen": n, "is_test": 0} for n in range(1, 102)]
        self.tracker.request = Mock(side_effect=[{}, self.response(events[:100]), self.response(events[100:])])
        self.tracker.sync()
        self.assertEqual(self.tracker.setting("cursor"), 101)
        self.assertEqual(self.tracker.request.call_args_list[-1].args[0], "/admin/status?after=100")
        self.tracker.deliver_pending()
        self.tracker.notify.assert_called_once()
        self.assertIn("101 new", self.tracker.notify.call_args.args[0])
        self.tracker.deliver_pending()
        self.tracker.notify.assert_called_once()

    def test_unavailable_desktop_preserves_alerts_for_retry(self):
        self.tracker.request = Mock(side_effect=[{}, self.response([{"seq": 3, "first_seen": 10, "is_test": 1}])])
        self.tracker.sync()
        self.tracker.notify.return_value = False
        self.tracker.deliver_pending()
        self.tracker.notify.return_value = True
        self.tracker.deliver_pending()
        self.assertEqual(self.tracker.notify.call_count, 2)
        self.assertTrue(self.tracker.notify.call_args.args[0].startswith("[Test]"))
        self.tracker.deliver_pending()
        self.assertEqual(self.tracker.notify.call_count, 2)

    def test_network_failure_does_not_advance_cursor(self):
        self.tracker.request = Mock(side_effect=OSError("offline"))
        self.tracker.poll_once()
        self.assertEqual(self.tracker.setting("cursor", 0), 0)
        self.assertEqual(self.tracker.setting("last_error"), "OSError")
        self.tracker.notify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
