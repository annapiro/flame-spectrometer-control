import os
import re

import matplotlib.pyplot as plt

from config import *


class Spectrum:
    _CLEAN_PATTERN = re.compile(r'[^\d\s]')

    def __init__(self, filepath):
        self.filename = os.path.basename(filepath)

        # error tracking
        self.valid = True
        self.error = None

        # metadata
        self.start_of_spectrum: int | None = None
        self.data_size_flag: int | None = None
        self.nr_of_scans: int | None = None
        self.integration_time_ms: int | None = None
        self.baseline_I: int | None = None
        self.baseline_II: int | None = None
        self.pixel_mode: int | None = None
        self.end_of_spectrum: int | None = None

        # spectral data
        self.data = []

        # parse file
        self._parse_file(filepath)

    def _parse_file(self, filepath: str):
        try:
            with open(filepath, mode='r', encoding='utf8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            self.valid = False
            self.error = str(e)
            return

        # clean the file content from all characters that aren't digits or spaces,
        # split by whitespace and convert values to integers
        content_list = [int(x) for x in self._CLEAN_PATTERN.sub('', content).split()]

        # too few values means the file is invalid
        if len(content_list) < 10:
            self.valid = False
            self.error = "Too few values"
            return

        self.start_of_spectrum = content_list[0]
        self.data_size_flag = content_list[1]
        self.nr_of_scans = content_list[2]
        self.integration_time_ms = content_list[3]
        self.baseline_I = content_list[4]
        self.baseline_II = content_list[5]
        self.pixel_mode = content_list[6]
        # if pixel mode is 1 then things work kinda differently, idk I haven't seen it yet
        self.data = content_list[7:-1] if self.pixel_mode == 0 else []
        self.end_of_spectrum = content_list[-1]

    # TODO: add option to customize filename maybe
    def plot(self, title: str = None, save_to_file: bool = False):
        filename_no_ext = os.path.splitext(self.filename)[0]

        plt.plot(WAVELENGTHS, self.data)
        plt.xlabel("Wavelength [nm]")
        plt.ylabel("Counts")
        plt.title(title if title else filename_no_ext)
        if save_to_file:
            plt.savefig(f"{filename_no_ext}.png", dpi=150)
        plt.show()

    # TODO: maybe also add string representation?
    def pretty_print(self):
        print(f"File: {self.filename}")
        if self.error:
            print(f"Error: {self.error}")
        else:
            # print(f"Spectral data:\n\tNr of values: {len(self.data)}\n\tMin: {min(self.data)}\n\tMax: {max(self.data)}")
            print(f"Pixels: {len(self.data)}\tMin: {min(self.data)}\tMax: {max(self.data)}")
