import os

# PyArrow (pulled in transitively by pandas/dask[dataframe]) statically links
# its own OpenSSL. On systems whose openssl.cnf configures the pkcs11 engine
# (e.g. Ubuntu with opensc installed), that vendored OpenSSL segfaults while
# dlopen-ing the system's engines-3/libpkcs11.so, whose ABI doesn't match.
# SparCC never touches TLS/engines, so blank out the config PyArrow's OpenSSL
# reads, before anything in this package can trigger a pandas/pyarrow import.
os.environ.setdefault('OPENSSL_CONF', '')
