import argparse
import csv
import os

from tqdm import tqdm

from config import *
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
    for entry in tqdm(list(os.scandir(dirpath)), desc="Parsing txt files"):
        if entry.is_file():
            measurements.append(Spectrum(entry.path))
    return measurements


def main(dirpath: str):
    measurements = get_measurements_from_folder(dirpath)

    # TODO: implement control loop for processing user commands

    errors = [x for x in measurements if len(x.data) != NR_PIXELS]

    if errors:
        print(f"{len(errors)} files contain an error:\n")
        for f in errors:
            f.pretty_print()

    print(f"\n{len(measurements) - len(errors)}/{len(measurements)} files are well-formed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    args = parser.parse_args()
    # TODO: take arguments either file name or folder name
    main(args.dir)
