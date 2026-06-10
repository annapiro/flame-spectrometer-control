import os
import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from flamelib.config import *
from flamelib import Spectrum


class SpectrumViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flame Spectrum Viewer")
        self.geometry("1200x700")
        self.file_paths = {}
        self._build_ui()

    def _build_ui(self):
        # top bar
        top = tk.Frame(self, pady=4, padx=8)
        top.pack(side=tk.TOP, fill=tk.X)
        tk.Button(top, text="Open folder", command=self._open_folder).pack(side=tk.LEFT)
        self.path_label = tk.Label(top, text="No folder selected", anchor='w', fg='gray')
        self.path_label.pack(side=tk.LEFT, padx=8)

        # main area: left list + right plot
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # left panel
        left = tk.Frame(pane, width=300)
        pane.add(left, minsize=200)
        tk.Label(left, text="Spectrum files", anchor='w', font=('', 9, 'bold')).pack(fill=tk.X)
        scrollbar = tk.Scrollbar(left)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(left, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set, font=('Courier', 8))
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)

        # right panel
        right = tk.Frame(pane)
        pane.add(right, minsize=500)
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # status bar
        self.status = tk.Label(self, text="", anchor='w', fg='gray', font=('', 8))
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=2)

    def _open_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.path_label.config(text=path, fg='black')
        self._load_folder(path)

    def _load_folder(self, path):
        self.listbox.delete(0, tk.END)
        self.file_paths.clear()
        files = sorted([
            e for e in os.scandir(path)
            if e.is_file() and e.name.endswith('.txt') and not e.name.startswith('LOG')
        ], key=lambda e: e.name)
        for entry in files:
            self.listbox.insert(tk.END, entry.name)
            self.file_paths[entry.name] = entry.path
        self.status.config(text=f"{len(files)} spectrum files found")

    def _on_select(self, event):
        selected = [self.listbox.get(i) for i in self.listbox.curselection()]
        if not selected:
            return

        self.ax.clear()
        self.ax.axhline(SATURATION_VALUE, color='red', linestyle='--', linewidth=0.8, alpha=0.6, label='Saturation')

        errors = []
        for name in selected:
            spectrum = Spectrum(self.file_paths[name])
            # not a valid Spectrum object
            if spectrum.error:
                errors.append(f"{name}: {spectrum.error}")
                continue
            # doesn't match the expected number of pixels, so cannot be plotted
            if len(spectrum.data) != NR_PIXELS:
                errors.append(f"{name}: Unexpected pixel count: {len(spectrum.data)}")
                continue
            self.ax.plot(WAVELENGTHS, spectrum.data, linewidth=0.8, label=name)

        self.ax.set_xlabel("Wavelength [nm]")
        self.ax.set_ylabel("Counts")
        self.ax.set_ylim(bottom=0)
        self.ax.legend(fontsize=7)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()

        if errors:
            self.status.config(text=" | ".join(errors), fg='red')
        else:
            self.status.config(text=f"{len(selected)} {'spectrum' if len(selected) == 1 else 'spectra'} plotted", fg='gray')


if __name__ == '__main__':
    app = SpectrumViewer()
    app.mainloop()
