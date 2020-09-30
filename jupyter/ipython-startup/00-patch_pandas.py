"""
IPython startup file
See https://ipython.org/ipython-doc/1/config/overview.html#startup-files

This file used to provide a patch to pandas.read_csv() so that it accepted the "s3:bucket-path" form (as returned by
the "copy path" feature in Jupyterlab) in addition to the canonical "s3://bucket-path" form.
We removed the patch because 1. it wasn't not bulletproof (reloading pandas will cancel it for example) and 2. it was
confusing, as other function calls still required the canonical form.

This file has been deliberately kept, but empty: our config copies the directory content to the user home directory
every time its server starts. If we remove this file from the repository and the resulting image, users would just
keep a copy of the previous version of the file containing the problematic patch.
"""
