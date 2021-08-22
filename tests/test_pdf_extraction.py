from application.pdf_reader import PdfReader
from unittest import TestCase
import glob
import os
import pathlib


class TestPdfReader(TestCase):
    FILE_IN = 'test_files/data_endurance.pdf'
    FILE_OUT = 'out_files/data_out.xlsx'

    def setUp(self) -> None:
        out_dir = pathlib.Path(__file__).parent.resolve() / 'out_files'
        filelist = glob.glob(os.path.join(out_dir, "*.*"))
        for f in filelist:
            os.remove(f)

    def test_extraction(self):
        PdfReader.pdf_to_excel(self.FILE_IN, self.FILE_OUT)
        self.assertTrue(os.path.exists(self.FILE_OUT))

