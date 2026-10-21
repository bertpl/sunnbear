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

from .data_files import UNDECIDED, AutomaticStatus, SourceRow, join_row_ids
from .parsing import ParsedRow, ParseError, ParseTimeoutError

# PARSE_TIMEOUT_SECONDS limits the time that parsing a row and computing its scaled values may take.
PARSE_TIMEOUT_SECONDS = 10


def compute_automatic_statuses(rows: list[SourceRow]) -> dict[str, AutomaticStatus]:
    """Return the automatic status of each row, keyed by row id, for rows given in time order."""
    earlier_row_index = EarlierRowIndex()
    return {row.row_id: earlier_row_index.match_and_add(row) for row in rows}


# ==================================================================================================
#  EarlierRowIndex
# ==================================================================================================
class EarlierRowIndex:
    """An `EarlierRowIndex` holds the rows compared so far, indexed by each kind of comparison.

    It finds the earliest matches of each next row.
    """

    def __init__(self) -> None:
        """Start with no rows, and make SIGALRM raise `ParseTimeoutError`, which ends a parse that takes too long.

        Python installs a SIGALRM handler only on Unix and in the main thread, so the index works only there.
        """
        signal.signal(signal.SIGALRM, self._on_alarm)
        self._by_structure: dict[str, str] = {}
        self._by_value: dict[tuple, str] = {}
        self._by_text: dict[str, str] = {}
        self._by_family: dict[str, str] = {}

    def match_and_add(self, row: SourceRow) -> AutomaticStatus:
        """Return the automatic status of a row, then add the row to the index.

        The status is `duplicate` when every instance of the row matches an earlier row by structure, `extended`
        when the row only adds parameter values to an earlier family, `new` when the row parses and matches
        nothing, and `judge` when a person must decide: a match by value only, a match of only some of its
        instances, or a row that does not parse.
        """
        text_form = self._text_form(row)
        same_text = self._by_text.get(text_form)
        signal.alarm(PARSE_TIMEOUT_SECONDS)
        try:
            parsed = ParsedRow.from_source_row(row)
            scaled_values = parsed.scaled_values()
            signal.alarm(0)
        except (ParseError, ParseTimeoutError) as error:
            signal.alarm(0)
            parse_note = str(error) or "timeout"
            if same_text:
                status = AutomaticStatus("duplicate", "same text", same_text, parse_note, n_instances=0)
            else:
                status = AutomaticStatus(UNDECIDED, "unparsed", "", parse_note, n_instances=0)
        else:
            instance_keys = [sp.srepr(instance) for instance in parsed.instances]
            status = self._match_parsed(parsed, instance_keys, scaled_values, same_text)
            self._add_parsed(row.row_id, parsed, instance_keys, scaled_values)
        self._by_text.setdefault(text_form, row.row_id)
        return status

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _match_parsed(
        self, parsed: ParsedRow, instance_keys: list[str], scaled_values: list, same_text: str | None
    ) -> AutomaticStatus:
        """Return the status of a parsed row against the earlier rows.

        `same_text` is the earlier row with the same text form, which matches only when no other comparison does.
        """
        n = len(instance_keys)
        structural = [self._by_structure.get(key) for key in instance_keys]
        family = self._by_family.get(sp.srepr(parsed.family))
        by_structure_or_value = []
        for instance_values, match in zip(scaled_values, structural, strict=True):
            if instance_values is not None and not match:
                by_structure_or_value.append(self._by_value.get(instance_values))
            else:
                by_structure_or_value.append(match)
        if all(structural):
            return AutomaticStatus("duplicate", "structure", join_row_ids(structural), "", n)
        elif family and parsed.has_values:
            return AutomaticStatus("extended", "family, new parameter values", family, "", n)
        elif family:
            return AutomaticStatus(UNDECIDED, "family, no parsed values", family, "", n)
        elif all(by_structure_or_value):
            return AutomaticStatus(UNDECIDED, "value", join_row_ids(by_structure_or_value), "", n)
        elif any(by_structure_or_value):
            return AutomaticStatus(UNDECIDED, "partial", join_row_ids(by_structure_or_value), "", n)
        elif same_text:
            return AutomaticStatus("duplicate", "same text", same_text, "", n)
        else:
            return AutomaticStatus("new", "", "", "", n)

    def _add_parsed(self, row_id: str, parsed: ParsedRow, instance_keys: list[str], scaled_values: list) -> None:
        """Add a parsed row's instances, scaled values and family form to the indexes, where no earlier row has them."""
        for key, instance_values in zip(instance_keys, scaled_values, strict=True):
            self._by_structure.setdefault(key, row_id)
            if instance_values is not None:
                self._by_value.setdefault(instance_values, row_id)
        self._by_family.setdefault(sp.srepr(parsed.family), row_id)

    @staticmethod
    def _text_form(row: SourceRow) -> str:
        """Return the text by which a row matches when nothing else does.

        The text is the row's f or f_description and its parameters, without whitespace and backticks. A row whose
        f_description holds no code, such as "not given", matches nothing by its text.
        """
        if row.f or "`" in row.f_description:
            return re.sub(r"[\s`]", "", row.f or row.f_description) + "|" + re.sub(r"[\s`]", "", row.parameters)
        else:
            return f"no expression: {row.row_id}"

    @staticmethod
    def _on_alarm(signum: int, frame: object) -> None:
        """Stop a parse that takes too long."""
        raise ParseTimeoutError
