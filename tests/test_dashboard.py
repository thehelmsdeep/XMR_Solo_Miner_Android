import unittest

from miner.dashboard import MinerDashboard


class DashboardTests(unittest.TestCase):
    def test_pool_and_job_update_dashboard(self):
        dashboard = MinerDashboard("4" + "a" * 94)
        self.assertTrue(dashboard.consume(
            "[2026-10-09] net use pool xmrpool.eu:3333 TLSv1.3 57.129.130.178"
        ))
        self.assertEqual(dashboard.status, "Connected")
        dashboard.consume(
            "[2026-10-09] net new job from xmrpool.eu:3333 diff 45000 algo rx/0 height 3780282 (41 tx)"
        )
        self.assertEqual(dashboard.status, "Mining...")
        self.assertEqual(dashboard.pool_diff, "45000")
        self.assertEqual(dashboard.last_job, "rx/0 @ height 3780282")

    def test_speed_and_share_counters(self):
        dashboard = MinerDashboard("4" + "a" * 94)
        self.assertTrue(dashboard.consume(
            "[2026-10-09] miner speed 10s/60s/15m 1.25 1.20 n/a kH/s max 1.30 kH/s"
        ))
        self.assertEqual(dashboard.hashrate_hs, 1250)
        self.assertEqual(dashboard.interval_hashes, 12500)
        dashboard.consume("[2026-10-09] net accepted (3/1) diff 45000 (12 ms)")
        self.assertEqual(dashboard.accepted, 3)
        self.assertEqual(dashboard.rejected, 1)
        self.assertIn("estimated", dashboard.render().lower())

    def test_dns_error_changes_status(self):
        dashboard = MinerDashboard("4" + "a" * 94)
        dashboard.consume('xmrpool.eu:3333 DNS error: "no address"')
        self.assertEqual(dashboard.status, "Connection error")
        self.assertIn("DNS error", dashboard.last_event)


if __name__ == "__main__":
    unittest.main()
