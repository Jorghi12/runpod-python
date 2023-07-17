''' Tests for runpod.serverless.modules.rp_ping '''

import os
import importlib

import unittest
from unittest.mock import patch, Mock

from runpod.serverless.modules import rp_ping

class TestPing(unittest.TestCase):
    ''' Tests for rp_ping '''

    def test_variables(self):
        '''
        Tests that the variables are set correctly
        '''
        os.environ["RUNPOD_WEBHOOK_PING"] = "PING_NOT_SET"

        importlib.reload(rp_ping)

        self.assertEqual(rp_ping.PING_URL, "PING_NOT_SET")
        self.assertEqual(rp_ping.PING_INTERVAL, 10000)

        os.environ["RUNPOD_WEBHOOK_PING"] = "https://test.com/ping"
        os.environ["RUNPOD_PING_INTERVAL"] = "20000"

        importlib.reload(rp_ping)

        self.assertEqual(rp_ping.PING_URL, "https://test.com/ping")
        self.assertEqual(rp_ping.PING_INTERVAL, 20000)

    def test_start_ping(self):
        '''
        Tests that the start_ping function works correctly
        '''
        os.environ["RUNPOD_WEBHOOK_PING"] = "https://test.com/ping"

        with patch("requests.Session.get") as mock_get:

            # Normal case
            mock_get.return_value = Mock(status_code=200)

            importlib.reload(rp_ping)
            new_ping = rp_ping.HeartbeatSender()

            self.assertFalse(new_ping._thread.is_alive()) # pylint: disable=protected-access
            mock_session = Mock()
            mock_session.headers.update = Mock()

            new_ping.start_ping()

            rp_ping.PING_URL = "https://test.com/ping"

            self.assertEqual(rp_ping.PING_URL, "https://test.com/ping")
            self.assertIsNotNone(new_ping._thread) # pylint: disable=protected-access
            self.assertTrue(new_ping._thread.is_alive()) # pylint: disable=protected-access

            # Exception case
            mock_get.side_effect = Exception("Test exception")

            with patch("runpod.serverless.modules.rp_ping.log.error") as mock_log_error:
                new_ping._send_ping() # pylint: disable=protected-access
                assert mock_log_error.call_count == 2
