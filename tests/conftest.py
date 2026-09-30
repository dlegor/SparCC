"""
Shared pytest setup.

Importing ``sparcc`` first sets OPENSSL_CONF before any test module imports
pandas (see sparcc/__init__.py), independent of test collection order.
"""
import sparcc  # noqa: F401
