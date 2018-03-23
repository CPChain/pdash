#!/usr/bin/env python3


import hashlib, os

def validate_file_md5_hash(file, original_hash):
    """ Returns true if file MD5 hash matches with the provided one, false otherwise. """

    if get_file_md5_hash(file) == original_hash:
        return True

    return False

def get_file_md5_hash(file):
    """ Returns file MD5 hash"""

    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)

    return md5_hash.hexdigest()

def read_bytes_from_file(file, chunk_size = 8100):
    """ Read bytes from a file in chunks. """

    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)

            if chunk:
                    yield chunk
            else:
                break

    file.close()

def list_all_files(path):
    file_list = []
    for r, d ,f in os.walk(path):
        for file in f:
            file_list.append(os.path.join(r, file))

    return file_list

def clean_and_split_input(input):
    """ Removes carriage return and line feed characters and splits input on a single whitespace. """
    input = input.decode()
    input = input.strip()
    input = input.split(':')

    return input
