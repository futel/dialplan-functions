"""
Download recordings stored by Twilio Programmable Voice.
"""


import argparse
import os
import re

import dotenv
import requests

dotenv.load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        '..', 'app-dialplan', 'chalicelib', 'environment', '.env'))

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']


def extract_urls(log_filename, recording_type):
    """Yield recording URLs of recording_type found in the log file."""
    pattern = re.compile(
        r'Recording: ' + re.escape(recording_type) + r': (\S+)')
    seen = set()
    with open(log_filename) as log_file:
        for line in log_file:
            match = pattern.search(line)
            if match:
                url = match.group(1)
                if url not in seen:
                    seen.add(url)
                    yield url


def download_recording(url):
    """Download the recording at url into the current directory.

    Returns True if the recording was downloaded, False if it was missing.
    """
    filename = url.rsplit('/', 1)[-1]
    response = requests.get(url, auth=(account_sid, auth_token))
    if response.status_code == 404:
        print('missing', filename)
        return False
    response.raise_for_status()
    with open(filename, 'wb') as recording_file:
        recording_file.write(response.content)
    print(filename)
    return True


def delete_recording(url):
    """Delete the recording at url."""
    response = requests.delete(url, auth=(account_sid, auth_token))
    response.raise_for_status()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument(
        'log_filename', help='Path to the log file to search.')
    parser.add_argument(
        'recording_type',
        help="Recording type to download, e.g. 'operator' or "
             "'mother-foucaults'.")
    parser.add_argument(
        '-d', '--delete', action='store_true',
        help='Delete each recording after it is downloaded.')
    args = parser.parse_args()

    for url in extract_urls(args.log_filename, args.recording_type):
        downloaded = download_recording(url + '.wav')
        if downloaded and args.delete:
            delete_recording(url)
