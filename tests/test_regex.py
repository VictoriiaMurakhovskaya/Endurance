import unittest
from unittest import TestCase
import re


class TestStrings(TestCase):

    def setUp(self) -> None:
        self.string_list_1 = ['1-е место', 'Гонщик 27: NFS Ko']

    def test_regex(self):
        result = re.sub(r"[\[\]:\*\?/]", '', ';'.join(self.string_list_1))
        self.assertEqual('1-е место;Гонщик 27 NFS Ko', result)