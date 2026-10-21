"""This module gives each row its automatic status by comparing it with every earlier row.

A parsed row is compared with all earlier parsed rows in 3 ways:

- **structure:** its instances, 1 per combination of its parameter values, are equal after an equation `lhs = rhs`
  becomes `lhs - rhs`, and a constant factor and the sign are removed;
- **family:** its expression is equal with its parameters left as symbols;
- **value:** its instances agree, up to a constant factor, at the fixed x-values of `parsing.SAMPLE_POINTS`, in
  40-digit arithmetic.

A row that does not parse is compared by its text only, and a parsed row by its text when the 3 comparisons find no
match: its f or f_description and its parameters, without whitespace and backticks.
"""

import re

import sympy as sp

from .data_files import UNDECIDED, AutomaticStatus, SourceRow, join_row_ids
from .parsing import ParsedRow, ParseError, ParseTimeoutError


def compute_automatic_statuses(rows: list[SourceRow]) -> dict[str, AutomaticStatus]:
    """Return the automatic status of each row, keyed by row id, for rows given in time order."""
    earlier_row_index = EarlierRowIndex()
    return {row.row_id: earlier_row_index.match_and_add(row) for row in rows}


# ==================================================================================================
#  EarlierRowIndex
# ==================================================================================================
class EarlierRowIndex:
    """An `EarlierRowIndex` holds the rows compared so far, indexed by each kind of comparison.

    For each row it is given, it finds the earliest matching rows among those compared so far.
    """

    def __init__(self) -> None:
        """Start with no rows."""
        self._by_structure: dict[str, str] = {}
        self._by_value: dict[tuple, str] = {}
        self._by_text: dict[str, str] = {}
        self._by_family: dict[str, str] = {}

    def match_and_add(self, row: SourceRow) -> AutomaticStatus:
        """Return the automatic status of a row, then add the row to the index.

        The status is:

        - `duplicate` when every instance of the row matches an earlier row by structure, or when the row matches an
          earlier row only by its text;
        - `extended` when the row adds parameter values to an earlier family;
        - `new` when the row parses and matches nothing;
        - `undecided` when a person must decide: a match by value only, a match of only some of its instances, a
          family match of a row without parameter values, or a row that does not parse and matches no earlier text.
        """
        text_form = self._text_form(row)
        same_text_row_id = self._by_text.get(text_form)
        try:
            parsed = ParsedRow.from_source_row(row)
        except (ParseError, ParseTimeoutError) as error:
            parse_note = str(error) or "timeout"
            if same_text_row_id:
                status = AutomaticStatus("duplicate", "same text", same_text_row_id, parse_note, n_instances=0)
            else:
                status = AutomaticStatus(UNDECIDED, "unparsed", "", parse_note, n_instances=0)
        else:
            instance_keys = [sp.srepr(instance) for instance in parsed.instances]
            status = self._match_parsed(parsed, instance_keys, same_text_row_id)
            self._add_parsed(row.row_id, parsed, instance_keys)
        self._by_text.setdefault(text_form, row.row_id)
        return status

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _match_parsed(
        self, parsed: ParsedRow, instance_keys: list[str], same_text_row_id: str | None
    ) -> AutomaticStatus:
        """Return the status of a parsed row against the earlier rows.

        `same_text_row_id` is the id of the earlier row with the same text form; that row counts as a match only when
        no other comparison finds one.
        """
        n = len(instance_keys)
        structure_matches = [self._by_structure.get(key) for key in instance_keys]
        family_match = self._by_family.get(sp.srepr(parsed.family))
        structure_or_value_matches = []
        for instance_values, match in zip(parsed.scaled_values, structure_matches, strict=True):
            if instance_values is not None and not match:
                structure_or_value_matches.append(self._by_value.get(instance_values))
            else:
                structure_or_value_matches.append(match)
        if all(structure_matches):
            return AutomaticStatus("duplicate", "structure", join_row_ids(structure_matches), "", n)
        elif family_match and parsed.has_values:
            return AutomaticStatus("extended", "family, new parameter values", family_match, "", n)
        elif family_match:
            return AutomaticStatus(UNDECIDED, "family, no parsed values", family_match, "", n)
        elif all(structure_or_value_matches):
            return AutomaticStatus(UNDECIDED, "value", join_row_ids(structure_or_value_matches), "", n)
        elif any(structure_or_value_matches):
            return AutomaticStatus(UNDECIDED, "partial", join_row_ids(structure_or_value_matches), "", n)
        elif same_text_row_id:
            return AutomaticStatus("duplicate", "same text", same_text_row_id, "", n)
        else:
            return AutomaticStatus("new", "", "", "", n)

    def _add_parsed(self, row_id: str, parsed: ParsedRow, instance_keys: list[str]) -> None:
        """Add a parsed row's instances, scaled values and family form to the indexes, where no earlier row has them."""
        for key, instance_values in zip(instance_keys, parsed.scaled_values, strict=True):
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
