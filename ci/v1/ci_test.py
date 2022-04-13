"""
Integration test of the CMPT 756 sample applicaton.

Result of test in program return code:
0: Test succeeded
1: Test failed
"""

# Standard library modules
import argparse
import os
import sys

from sqlalchemy import true

# Installed packages

# Local modules
import create_tables
import book

# The services check only that we pass an authorization,
# not whether it's valid
DUMMY_AUTH = 'Bearer A'


def parse_args():
    """Parse the command-line arguments.

    Returns
    -------
    namespace
        A namespace of all the arguments, augmented with names
        'user_url' and 'book_url'.
    """
    argp = argparse.ArgumentParser(
        'ci_test',
        description='Integration test of CMPT 756 sample application'
        )
    argp.add_argument(
        'user_address',
        help="DNS name or IP address of user service."
        )
    argp.add_argument(
        'user_port',
        type=int,
        help="Port number of user service."
        )
    argp.add_argument(
        'book_address',
        help="DNS name or IP address of book service."
        )
    argp.add_argument(
        'book_port',
        type=int,
        help="Port number of book service."
        )
    argp.add_argument(
        'table_suffix',
        help="Suffix to add to table names (not including leading "
             "'-').  If suffix is 'scp756-2022', the book table "
             "will be 'Book-scp756-2022'."
    )
    args = argp.parse_args()
    args.user_url = "http://{}:{}/api/v1/user/".format(
        args.user_address, args.user_port)
    args.book_url = "http://{}:{}/api/v1/book/".format(
        args.book_address, args.book_port)
    return args


def get_env_vars(args):
    """Augment the arguments with environment variable values.

    Parameters
    ----------
    args: namespace
        The command-line argument values.

    Environment variables
    ---------------------
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
        SVC_LOADER_TOKEN, DYNAMODB_URL: string
        Environment variables specifying these AWS access parameters.

    Modifies
    -------
    args
        The args namespace augmented with the following names:
        dynamodb_region, access_key_id, secret_access_key, loader_token,
        dynamodb_url

        These names contain the string values passed in the corresponding
        environment variables.

    Returns
    -------
    Nothing
    """
    # These are required to be present
    args.dynamodb_region = os.getenv('AWS_REGION')
    args.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    args.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    args.loader_token = os.getenv('SVC_LOADER_TOKEN')
    args.dynamodb_url = os.getenv('DYNAMODB_URL')


def setup(args):
    """Create the DynamoDB tables.

    Parameters
    ----------
    args: namespace
        The arguments specifying the tables. Uses dynamodb_url,
        dynamodb_region, access_key_id, secret_access_key, table_suffix.
    """
    create_tables.create_tables(
        args.dynamodb_url,
        args.dynamodb_region,
        args.access_key_id,
        args.secret_access_key,
        'Book-' + args.table_suffix,
        'User-' + args.table_suffix
    )


def run_test(args):
    """Run the tests.

    Parameters
    ----------
    args: namespace
        The arguments for the test. Uses book_url.

    Prerequisites
    -------------
    The DyamoDB tables must already exist.

    Returns
    -------
    number
        An HTTP status code representing the test result.
        Some "pseudo-HTTP" codes are defined in the 600 range
        to indicate conditions that are not included in the HTTP
        specification.

    Notes
    -----
    This test is highly incomplete and needs substantial extension.
    """
    mserv = book.Book(args.book_url, DUMMY_AUTH)
    author, book, datepublished, availability = ('Dan Brown', 'Inferno', '06-05-2004', True)
    trc, b_id = mserv.create(author, book, datepublished, availability)
    if trc != 200:
        sys.exit(1)
    trc, rauthor, rbook = mserv.read(b_id)
    if trc == 200:
        if author != rauthor or book != rbook:
            # Fake HTTP code to indicate error
            trc = 601
        mserv.delete(b_id)
    return trc


if __name__ == '__main__':
    args = parse_args()
    get_env_vars(args)
    setup(args)
    trc = run_test(args)
    if trc != 200:
        sys.exit(1)
