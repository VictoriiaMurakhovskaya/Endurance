import unittest
from unittest import TestCase
import re
import numpy as np


class TestNdArray(TestCase):

    def setUp(self) -> None:
        self.array = np.ones(290)

    def test_append(self):
        qty = 300 - len(self.array)
        self.array = np.hstack((self.array, np.ones(qty)))
        self.assertEqual(300, len(self.array))