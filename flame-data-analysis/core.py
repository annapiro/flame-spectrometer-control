from datetime import datetime
import os
import re

import matplotlib.pyplot as plt
import numpy as np

from config import *


class Spectrum:
    _CLEAN_PATTERN = re.compile(r'[^\d\s]')
    _FILENAME_SEP = '-'
    _TIMESTAMP_FORMAT = '%Y%m%dT%H%M%S'

    def __init__(self, filepath):
        self.filename = os.path.basename(filepath)

        # error tracking
        self.valid = True
        self.error = None

        # metadata from the file name
        self.timestamp: datetime | None = None
        self.fiber: int | None = None
        self.integration_time_us: int | None = None

        # metadata from the spectrometer
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
        self._parse_filename()
        self._parse_file(filepath)

    def _parse_filename(self):
        filename_parts = os.path.splitext(self.filename)[0].split(self._FILENAME_SEP)

        if len(filename_parts) < 1:
            return

        self.timestamp = datetime.strptime(filename_parts[0], self._TIMESTAMP_FORMAT)

        for part in filename_parts[1:]:
            if part.startswith('F'):
                self.fiber = int(part[1:])
            elif part.startswith('i'):
                self.integration_time_us = int(part[1:])

    def _parse_file(self, filepath: str):
        try:
            with open(filepath, mode='r', encoding='utf8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            self.valid = False
            self.error = str(e)
            return

        # clean the file content from all characters that aren't digits or spaces
        clean = re.sub(self._CLEAN_PATTERN, '', content)

        # split by whitespace and convert values to integers
        arr = np.fromstring(clean, sep=' ', dtype=np.int32)

        # too few values means the file is invalid
        if arr.size < 10:
            self.valid = False
            self.error = "Too few values"
            return

        self.start_of_spectrum = int(arr[0])
        self.data_size_flag = int(arr[1])
        self.nr_of_scans = int(arr[2])
        self.integration_time_ms = int(arr[3])
        self.baseline_I = int(arr[4])
        self.baseline_II = int(arr[5])
        self.pixel_mode = int(arr[6])
        # if pixel mode is 1 then things work kinda differently, idk I haven't seen it yet
        self.data = arr[7:-1] if self.pixel_mode == 0 else []
        self.end_of_spectrum = int(arr[-1])

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
        print(f"{self.filename}")
        if self.error:
            print(f"\tError: {self.error}")
        else:
            print(f"\tTimestamp: {self.timestamp}")
            print(f"\tPixels: {len(self.data)}\tMin: {min(self.data)}\tMax: {max(self.data)}")
