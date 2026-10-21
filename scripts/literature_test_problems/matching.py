"""This module gives each row its automatic status by comparing it with every earlier row.

A parsed row is compared with all earlier parsed rows in 3 ways:

- **structure:** its instances are equal after an equation `lhs = rhs` becomes `lhs - rhs`, and a constant factor
  and the sign are removed;
- **family:** its expression is equal with its parameters left as symbols;
- **value:** its instances agree, up to a constant factor, at 12 fixed x-values, in 40-digit arithmetic.

A row that does not parse is compared by its text only: its f or f_description and its parameters, without
whitespace and backticks.
"""

import re
import signal

import sympy as sp

from .data_files import ROW_ID_SEPARATOR, UNDECIDED, AutomaticStatus, SourceRow
from .parsing import ParsedRow, ParseError, ParseTimeoutError

# the time that parsing a row and computing its fingerprints may take, in seconds
PARSE_SECONDS = 10


def compute_automatic_statuses(rows: list[SourceRow]) -> dict[str, AutomaticStatus]:
    """Return the automatic status of each row, keyed by row id, for rows given in time order."""
    signal.signal(signal.SIGALRM, _on_alarm)
    earlier_rows = EarlierRows()
    return {row.row_id: earlier_rows.match(row) for row in rows}


# ==================================================================================================
#  EarlierRows
# ==================================================================================================
class EarlierRows:
    """The rows matched so far, indexed by each kind of match, to find the earliest matches of the next row."""

    def __init__(self) -> None:
        """Start with no rows."""
        self._by_structure: dict[str, str] = {}
        self._by_value: dict[tuple, str] = {}
        self._by_text: dict[str, str] = {}
        self._by_family: dict[str, str] = {}

    def match(self, row: SourceRow) -> AutomaticStatus:
        """Return the automatic status of a row, then add the row to the index.

        The status is `duplicate` when every instance of the row matches an earlier row by structure, `extended`
        when the row only adds parameter values to an earlier family, `new` when the row parses and matches
        nothing, and `judge` when a person must decide: a match by value only, a partial match, or a row that does
        not parse.
        """
        text_form = self._text_form(row)
        signal.alarm(PARSE_SECONDS)
        try:
            parsed = ParsedRow.from_source_row(row)
            fingerprints = parsed.fingerprints()
            signal.alarm(0)
        except (ParseError, ParseTimeoutError) as error:
            signal.alarm(0)
            status = self._match_unparsed(text_form, str(error) or "timeout")
        else:
            instance_keys = [sp.srepr(instance) for instance in parsed.instances]
            status = self._match_parsed(parsed, instance_keys, fingerprints, self._by_text.get(text_form))
            self._add_parsed(row.row_id, parsed, instance_keys, fingerprints)
        self._by_text.setdefault(text_form, row.row_id)
        return status

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _match_unparsed(self, text_form: str, parse_note: str) -> AutomaticStatus:
        """Return the status of a row that does not parse: a duplicate of an earlier row with the same text."""
        earlier = self._by_text.get(text_form)
        if earlier:
            return AutomaticStatus("duplicate", "same text", earlier, parse_note, instances=0)
        else:
            return AutomaticStatus(UNDECIDED, "unparsed", "", parse_note, instances=0)

    def _match_parsed(
        self, parsed: ParsedRow, instance_keys: list[str], fingerprints: list, same_text: str | None
    ) -> AutomaticStatus:
        """Return the status of a parsed row against the earlier rows."""
        n = len(instance_keys)
        structural = [self._by_structure.get(key) for key in instance_keys]
        family = self._by_family.get(sp.srepr(parsed.family))
        by_values = [
            self._by_value.get(fingerprint) if fingerprint is not None and not match else match
            for fingerprint, match in zip(fingerprints, structural, strict=True)
        ]
        if all(structural):
            return AutomaticStatus("duplicate", "structure", _join(structural), "", n)
        elif family and parsed.has_values:
            return AutomaticStatus("extended", "family, new parameter values", family, "", n)
        elif family:
            return AutomaticStatus(UNDECIDED, "family, no parsed values", family, "", n)
        elif all(by_values):
            return AutomaticStatus(UNDECIDED, "value", _join(by_values), "", n)
        elif any(by_values):
            return AutomaticStatus(UNDECIDED, "partial", _join(by_values), "", n)
        elif same_text:
            return AutomaticStatus("duplicate", "same text", same_text, "", n)
        else:
            return AutomaticStatus("new", "", "", "", n)

    def _add_parsed(self, row_id: str, parsed: ParsedRow, instance_keys: list[str], fingerprints: list) -> None:
        """Add a parsed row to the indexes, where no earlier row holds its forms already."""
        for key, fingerprint in zip(instance_keys, fingerprints, strict=True):
            self._by_structure.setdefault(key, row_id)
            if fingerprint is not None:
                self._by_value.setdefault(fingerprint, row_id)
        self._by_family.setdefault(sp.srepr(parsed.family), row_id)

    @staticmethod
    def _text_form(row: SourceRow) -> str:
        """Return the text by which an unparsed row matches: its f and parameters without whitespace and backticks.

        A row whose f_description holds no code, such as "not given", matches nothing by its text.
        """
        if row.f or "`" in row.f_description:
            return re.sub(r"[\s`]", "", row.f or row.f_description) + "|" + re.sub(r"[\s`]", "", row.parameters)
        else:
            return f"no expression: {row.row_id}"


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _on_alarm(signum: int, frame: object) -> None:
    """Stop a parse that takes too long."""
    raise ParseTimeoutError


def _join(row_ids: list[str | None]) -> str:
    """Join the distinct row ids, in their first order."""
    return ROW_ID_SEPARATOR.join(dict.fromkeys(r for r in row_ids if r))
