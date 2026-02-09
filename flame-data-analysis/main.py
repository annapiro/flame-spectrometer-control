import csv
import os

from tqdm import tqdm

from config import *
from core import Spectrum


# TODO: rewrite for OOP later but right now I don't need it
def save_to_csv(measurements: list, save_as: str):
    if not save_as.endswith('.csv'):
        save_as += '.csv'
    # TODO: this can and should be extracted from the Spectrum object
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


def calc_auto_integration_success_rate(measurements: list[Spectrum], to_csv=True):
    # sort measurements chronologically
    sorted_by_time = sorted(measurements, key=lambda x: x.timestamp)

    # collect measurements that were done after integration time changed
    after_int_change = [curr for prev, curr in zip(sorted_by_time, sorted_by_time[1:])
                        # current integration time is different from previous -> it changed
                        if curr.integration_time_us != prev.integration_time_us
                        # consider only same-fiber consecutive measurements
                        and curr.fiber == prev.fiber
                        # exclude measurements that hit the integration time cap - we can't expect them to be in range
                        and curr.integration_time_us < INTEGRATION_TIME_LIMIT]

    # build lookup: filename -> success status
    results = {}
    for m in after_int_change:
        max_val = max(m.data)
        results[m.filename] = LOWER_BOUNDARY <= max_val < UPPER_BOUNDARY

    # optionally write a summary to csv
    if to_csv:
        with open('out.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['filename', 'max_pixel', 'success'])

            for m in measurements:
                max_val = max(m.data)
                success = results.get(m.filename, None)  # None if not evaluated
                writer.writerow([m.filename, max_val, success])

    success_count = sum(results.values())
    print(f"Success rate: {success_count / len(results):.2%}")


def get_measurements_from_folder(dirpath: str) -> list[Spectrum]:
    measurements = []
    for entry in tqdm(list(os.scandir(dirpath)), desc="Parsing txt files"):
        if entry.is_file():
            measurements.append(Spectrum(entry.path))
    return measurements


def main():
    user_path = None

    # get the measurements path from the user
    while not user_path:
        user_input = input("Enter a valid path to a spectrometer measurement file "
                           "or a directory containing measurement files: \n")
        if os.path.exists(user_input):
            user_path = user_input
        else:
            print("File or directory not recognized!")

    if os.path.isdir(user_path):
        measurements = get_measurements_from_folder(user_path)
    elif os.path.isfile(user_path):
        measurements = [Spectrum(user_path)]
    # TODO: not very elegant is it
    else:
        print("File access error, please restart the script")

    # main control loop
    while True:
        command = input(f"Enter command for '{user_path}': ").strip().lower()
        print(f"===== {command} =====")
        if command == 'exit':
            break
        elif command == 'count pixels':
            errors = [x for x in measurements if len(x.data) != NR_PIXELS]
            print(f"{len(measurements) - len(errors)}/{len(measurements)} files are well-formed.")
            if errors:
                print(f"{len(errors)} files contain an error: \n")
                for f in errors:
                    f.pretty_print()
        elif command == 'show stats':
            for m in measurements:
                m.pretty_print()
        # TODO: really weird command naming
        elif command == 'auto integration success':
            calc_auto_integration_success_rate(measurements)
        # TODO: add command to change the path
        else:
            print("Unknown command!")


if __name__ == "__main__":
    main()
