# -*- coding: utf-8 -*-

"""Tests for mds-provider client."""

import pytest

from mds_provider_client.client import *


class TestMdsProviderClient:
    def test_basic_building(self):
        client = ProviderClient(url="http://python.org")
        assert client.url == "http://python.org"
