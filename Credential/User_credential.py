import csv


def get_keys(csv_file_addr):

    keys = list()
    with open(csv_file_addr) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='=')
        for key_line in csv_reader:
            keys.append(key_line[1])

    return keys
