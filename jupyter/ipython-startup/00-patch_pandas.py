"""
IPython startup file
See https://ipython.org/ipython-doc/1/config/overview.html#startup-files

Patch pandas so that our s3 paths in the file browser, that cannot start with s3:// for jupyter-related reasons,
can be used by pandas.read_csv()
"""

import pandas

original_read_csv = pandas.read_csv


def patched_read_csv(filepath_or_buffer, *args, **kwargs):
    if filepath_or_buffer[:3] == "s3:":
        filepath_or_buffer = "s3://" + filepath_or_buffer[3:]

    return original_read_csv(filepath_or_buffer, *args, **kwargs)


pandas.read_csv = patched_read_csv
