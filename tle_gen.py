#!/usr/bin/env python3

__author__ = "Van Graham"
__version__ = "1.0"

from argparse import ArgumentParser
import requests
from os import path
from re import match
import logging

NORAD_URL = 'https://celestrak.com/NORAD/elements/gp.php'

def read_satellites_file(file_path: str) -> list:
    satellites = []
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r') as input:
        for line in input:
            if line.startswith('#'):
                continue
            matched = match(r"([0-9]{5}).*", line)
            if matched:
                catalog_number = matched.group(1)
                logging.debug(f'Found catalog number: {catalog_number}.')
                satellites.append(catalog_number)

    return satellites


def download_tle(catalog_number: str) -> list:
    data = []
    url = f'{NORAD_URL}?CATNR={catalog_number}'

    response = requests.get(url)

    if response.status_code == 200:
        raw = response.content.split(b'\r\n')
        data = [x for x in raw if x.strip()]
    else:
        logging.error(response.reason)

    return data


if __name__== "__main__":

    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    parser = ArgumentParser(description='Custom TLE file generator.', prog='tle_gen')
    parser.add_argument('-i','--input', help='Download TLE for the specified catalog numbers.')
    parser.add_argument('-o','--output', help='Output file path.')
    parser.add_argument('-v','--version', help='Show version.', action='version', version='%(prog)s v' + __version__)

    args = vars(parser.parse_args())

    # Tracked satellites file
    tr_file = 'satellites.txt'

    # Output default file paths
    out_files = [path.join('C:/WXtoImg', 'custom.tle'), 
                 path.join('C:/Program Files (x86)/Orbitron/Tle', 'custom.tle')]

    if args['output']:
        out_files = [args['output']]  # If specific output is given, use it

    if args['input']:
        input_list = args['input'].replace(" ", "").split(',')
    else:
        try:
            input_list = read_satellites_file(tr_file)
        except FileNotFoundError as err:
            logging.error(err)
            exit(1)

    if len(input_list) == 0:
        logging.info('Invalid satellite list.')
        exit(1)

    for out_file in out_files:
        with open(out_file, 'wb') as output:
            for elem in input_list:
                data = download_tle(elem)
                if not len(data) == 3:
                    logging.warning('Could not get TLE for: {0}'.format(elem))
                    continue
                for line in data:
                    output.write(line + b'\r\n')
                logging.info('Saved TLE for {0} in {1}.'.format((data[0].decode()).strip(), out_file))

        logging.info('Custom TLE file saved in \"{0}\".'.format(path.abspath(out_file)))
