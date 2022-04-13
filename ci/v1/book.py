"""
Python  API for the book service.
"""

# Standard library modules

# Installed packages
import requests


class Book():
    """Python API for the book service.

    Handles the details of formatting HTTP requests and decoding
    the results.

    Parameters
    ----------
    url: string
        The URL for accessing the book service. Often
        'http://cmpt756s2:30001/'. Note the trailing slash.
    auth: string
        Authorization code to pass to the book service. For many
        implementations, the code is required but its content is
        ignored.
    """
    def __init__(self, url, auth):
        self._url = url
        self._auth = auth

    def create(self, author, book, datepublished, availability):
        """Create an author, book pair.

        Parameters
        ----------
        author: string
            The author performing book.
        book: string
            The name of the book.

        Returns
        -------
        (number, string)
            The number is the HTTP status code returned by book.
            The string is the UUID of this book in the book database.
        """
        r = requests.post(
            self._url,
            json={'author': author,
                  'bookTitle': book,
                  'datepublished':datepublished,
                  'availability':availability},
            headers={'Authorization': self._auth}
        )
        return r.status_code, r.json()['book_id']

    def read(self, b_id):
        """Read an author, book pair.

        Parameters
        ----------
        b_id: string
            The UUID of this book in the book database.

        Returns
        -------
        status, author, title, datepublished, availability

        status: number
            The HTTP status code returned by book.
        author: If status is 200, the author performing the book.
          If status is not 200, None.
        title: If status is 200, the title of the book.
          If status is not 200, None.
        """
        r = requests.get(
            self._url + b_id,
            headers={'Authorization': self._auth}
            )
        if r.status_code != 200:
            return r.status_code, None, None

        item = r.json()['Items'][0]
        return r.status_code, item['author'], item['booktitle'], item['datepublished'], item['availability']

    def delete(self, b_id):
        """Delete an author, book pair.

        Parameters
        ----------
        b_id: string
            The UUID of this book in the book database.

        Returns
        -------
        Does not return anything. The book delete operation
        always returns 200, HTTP success.
        """
        requests.delete(
            self._url + b_id,
            headers={'Authorization': self._auth}
        )
