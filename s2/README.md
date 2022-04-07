# CMPT 756 Music service

The book service maintains a list of books and the author that wrote
them.

This is a public Flask server written in Python.

There are several versions, each in its own subdirectory:

v1: A version that relies upon the DB service to store its values persistently.

v2: This version is configurable to return errors for a specified
  percentage (`PERCENT_ERROR`) of calls to `read`. It does not
  include the "bug" in in Assignment 4.  The `test` call
  will always return Success.

  This version is typically used with some form of
  traffic shaping to demonstrate "canary" deployments and
  rollbacks. See `cluster/s2-vs-canary.yaml` for setting
  up the services for such a deployment.
