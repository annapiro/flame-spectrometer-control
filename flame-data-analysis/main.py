import argparse
import csv
import os

from core import Spectrum


# TODO: rewrite for OOP later but right now I don't need it
def save_to_csv(measurements: list, save_as: str):
    if not save_as.endswith('.csv'):
        save_as += '.csv'
    data = [{'Integration time': m['File'].split('-')[-1][:-4],
             'Filename': m['File'],
             'Data length': len(m['Spectral data']),
             } for m in measurements]
    fieldnames = ['Experiment nr', 'Baud rate', 'Integration time', 'Filename', 'Data length']
    with open(save_as, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print('Saved ' + save_as)


def get_measurements_from_folder(dirpath: str) -> list[Spectrum]:
    measurements = []
    for entry in os.scandir(dirpath):
        if entry.is_file():
            measurements.append(Spectrum(entry.path))
    return measurements


def main():
    measurements = get_measurements_from_folder("data/2026-01-21")
    well_formed = 0
    for m in measurements:
        if len(m.data) != 3669:
            m.pretty_print()
        else:
            well_formed += 1
    print(f"\n{well_formed}/{len(measurements)} files are well-formed.")


if __name__ == "__main__":
    # takes arguments either file name or folder name or current folder by default
    main()
