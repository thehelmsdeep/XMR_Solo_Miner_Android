import argparse
import unittest

from tools.benchmark_randomx_threads import parse_threads


class ParseThreadsTests(unittest.TestCase):
    def test_parses_thread_list(self):
        self.assertEqual(parse_threads("1, 2,4,8"), [1, 2, 4, 8])

    def test_rejects_empty_list(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_threads(" , ")

    def test_rejects_non_integer(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_threads("1,two,4")

    def test_rejects_out_of_range(self):
        for value in ("0", "257"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    parse_threads(value)

    def test_rejects_duplicates(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_threads("1,2,1")


if __name__ == "__main__":
    unittest.main()
