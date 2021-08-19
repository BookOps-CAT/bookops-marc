from typing import BinaryIO, Union

from pymarc import MARCReader
from pymarc.constants import END_OF_RECORD
from pymarc import exceptions

from bookops_marc import Bib


class SierraBibReader(MARCReader):
    """
    An interator class for reading file of local Sierra MARC records.
    """

    def __init__(
        self,
        marc_target: Union[BinaryIO, bytes],
        library: str = "",
        to_unicode: bool = True,
        force_utf8: bool = False,
        hide_utf8_warnings: bool = False,
        utf8_handling: str = "strict",
        file_encoding: str = "iso8859-1",
        permissive: bool = False,
    ) -> None:
        super().__init__(
            marc_target,
            to_unicode,
            force_utf8,
            hide_utf8_warnings,
            utf8_handling,
            file_encoding,
            permissive,
        )

        self.library = library

    def __next__(self):
        """Read and parse the next record."""
        if self._current_exception:
            if isinstance(self._current_exception, exceptions.FatalReaderEror):
                raise StopIteration

        self._current_chunk = None
        self._current_exception = None

        self._current_chunk = first5 = self.file_handle.read(5)
        if not first5:
            raise StopIteration

        if len(first5) < 5:
            self._current_exception = exceptions.TruncatedRecord()
            return

        try:
            length = int(first5)
        except ValueError:
            self._current_exception = exceptions.RecordLengthInvalid()
            return

        chunk = self.file_handle.read(length - 5)
        chunk = first5 + chunk
        self._current_chunk = chunk

        if len(self._current_chunk) < length:
            self._current_exception = exceptions.TruncatedRecord()
            return

        if self._current_chunk[-1] != ord(END_OF_RECORD):
            self._current_exception = exceptions.EndOfRecordNotFound()
            return

        try:
            return Bib(
                chunk,
                library=self.library,
                to_unicode=self.to_unicode,
                force_utf8=self.force_utf8,
                hide_utf8_warnings=self.hide_utf8_warnings,
                utf8_handling=self.utf8_handling,
                file_encoding=self.file_encoding,
            )
        except Exception as ex:
            self._current_exception = ex
