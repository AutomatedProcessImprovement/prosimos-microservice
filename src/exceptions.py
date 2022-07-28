# user-defined exceptions

class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyFilename(Error):
    """Raised when the provided filename is empty"""
    def __str__(self):
        return "Cannot parse empty filename"
