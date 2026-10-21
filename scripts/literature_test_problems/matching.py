"""This module gives each row its automatic status by comparing it with every earlier row.

A row's test functions are its cases: each pair of 1 instance of its function, 1 per combination of its parameter
values, and 1 of its intervals that fits that instance (`intervals.Interval.fits`). A parsed row's instances are
compared with all earlier rows' instances in 3 ways:

- **structure:** they are equal after an equation `lhs = rhs` becomes `lhs - rhs`, and a constant factor and the sign
  are removed;
- **value:** they agree, up to a constant factor, at the fixed x-values of `parsing.SAMPLE_POINTS`, in 40-digit
  arithmetic;
- **family:** the row's expression is equal with its parameters left as symbols.

Every row with code in its f or f_description is also compared by its text: its f or f_description and its
parameters, without whitespace and backticks. A row's cases count as found when an earlier complete row has the
same instance, by structure or by text, on the same interval.
"""

import re

import sympy as sp

from .data_files import UNDECIDED, AutomaticStatus, SourceRow, join_row_ids
from .intervals import ParsedIntervals
from .parsing import ParsedRow, ParseError, ParseTimeoutError


def compute_automatic_statuses(rows: list[SourceRow], incomplete_row_ids: set[str]) -> dict[str, AutomaticStatus]:
    """Return the automatic status of each row, keyed by row id, for rows given in time order.

    `incomplete_row_ids` holds the rows that a decision makes `incomplete`; their test functions are not complete, so
    no later row is a duplicate of them.
    """
    earlier_row_index = EarlierRowIndex()
    return {row.row_id: earlier_row_index.match_and_add(row, row.row_id in incomplete_row_ids) for row in rows}


# ==================================================================================================
#  EarlierRowIndex
# ==================================================================================================
class EarlierRowIndex:
    """An `EarlierRowIndex` holds the rows compared so far, indexed by their functions and by their cases.

    For each row it is given, it finds the earliest matching rows among those compared so far. A function key is a
    pair of the comparison and the form that it compares, and a case key is a pair of a function key and an
    interval's key.
    """

    def __init__(self) -> None:
        """Start with no rows."""
        # _first_row maps each function key to the earliest row with that function, complete or not.
        self._first_row: dict[tuple, str] = {}
        # _first_complete_row maps each case key to the earliest complete row with that case.
        self._first_complete_row: dict[tuple, str] = {}
        # _unpaired_rows holds the complete rows whose cases can be more than their source gives: rows with several
        # instances and several intervals that no parameter ties to their instances, whose cases are every pair, and
        # rows whose instances combine several sets of parameter values (`ParsedRow.has_value_sets`).
        self._unpaired_rows: set[str] = set()

    def match_and_add(self, row: SourceRow, is_decided_incomplete: bool) -> AutomaticStatus:
        """Return the automatic status of a row, then add the row to the index.

        The status is the first of these that applies:

        - `incomplete` when the row gives no usable interval, or no function (an f_description without code);
        - `undecided` when its interval does not parse;
        - `duplicate` when every case of a row whose f does not parse is found by its text, and otherwise
          `undecided`;
        - `undecided` when an instance keeps a parameter without values;
        - `duplicate` when every case is found by structure, unless a case is found only in a row whose instances
          and intervals are not paired, which leaves the row `undecided`;
        - `undecided` when every case is found by structure or by value, but not every one by structure, or when no
          interval fits any instance;
        - `new` otherwise, naming the earlier rows that share an instance, its family or its text on other cases.

        `is_decided_incomplete` keeps the row's cases out of the index.
        """
        try:
            parsed = ParsedRow.from_source_row(row)
        except (ParseError, ParseTimeoutError) as error:
            parsed, function_note = None, str(error) or "timeout"
        else:
            function_note = ""
        try:
            intervals = ParsedIntervals.from_source_row(row)
        except (ParseError, ParseTimeoutError) as error:
            intervals, interval_note = None, str(error) or "interval: timeout"
        else:
            interval_note = f"interval: {intervals.n_unusable} left out" if intervals.n_unusable else ""
        parse_note = "; ".join(note for note in (function_note, interval_note) if note)
        n_instances = len(parsed.instances) if parsed else 0
        function_keys = self._function_keys(row, parsed)
        derived = self._derived_matches(function_keys)
        cases = self._cases(row, parsed, intervals)
        if intervals and intervals.incomplete_case:
            status = AutomaticStatus("incomplete", intervals.incomplete_case, derived[1], parse_note, n_instances)
        elif not function_keys:
            status = AutomaticStatus("incomplete", "no function", "", parse_note, n_instances)
        elif intervals is None:
            status = AutomaticStatus(UNDECIDED, "interval does not parse", derived[1], parse_note, n_instances)
        elif parsed is None:
            status = self._match_by_text(cases["text"], derived, parse_note)
        elif parsed.has_free_parameters:
            status = AutomaticStatus(UNDECIDED, "parameters without values", derived[1], parse_note, n_instances)
        else:
            status = self._match_parsed(cases, derived, parse_note, n_instances)
        self._add(row.row_id, function_keys, cases, parsed, intervals, is_decided_incomplete)
        return status

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _derived_matches(self, function_keys: list[tuple]) -> tuple[str, str]:
        """Return the comparisons that find earlier rows with any of the function keys, and those rows, as 2 fields."""
        kinds, row_ids = [], []
        for key in function_keys:
            if key in self._first_row:
                kinds.append(key[0])
                row_ids.append(self._first_row[key])
        return ", ".join(dict.fromkeys(kinds)), join_row_ids(row_ids)

    def _match_by_text(self, text_cases: list[tuple], derived: tuple[str, str], parse_note: str) -> AutomaticStatus:
        """Return the status of a row whose f does not parse: a duplicate if every case is found by its text."""
        found = [self._first_complete_row.get(case) for case in text_cases]
        if text_cases and all(found):
            return AutomaticStatus("duplicate", "same text", join_row_ids(found), parse_note, n_instances=0)
        else:
            return AutomaticStatus(UNDECIDED, "unparsed", derived[1], parse_note, n_instances=0)

    def _match_parsed(
        self, cases: dict[str, list[tuple]], derived: tuple[str, str], parse_note: str, n_instances: int
    ) -> AutomaticStatus:
        """Return the status of a row whose f and intervals parse, from its cases by structure and by value.

        `cases["value"]` holds each structure case's value case, or None where the instance has no scaled values.
        """
        by_structure = [self._first_complete_row.get(case) for case in cases["structure"]]
        by_structure_or_value = [
            found or (value_case and self._first_complete_row.get(value_case))
            for found, value_case in zip(by_structure, cases["value"], strict=True)
        ]
        if not cases["structure"]:
            return AutomaticStatus(UNDECIDED, "no case", derived[1], parse_note, n_instances)
        elif all(by_structure) and self._unpaired_rows.isdisjoint(by_structure):
            return AutomaticStatus("duplicate", "structure", join_row_ids(by_structure), parse_note, n_instances)
        elif all(by_structure):
            return AutomaticStatus(UNDECIDED, "unpaired", join_row_ids(by_structure), parse_note, n_instances)
        elif all(by_structure_or_value):
            return AutomaticStatus(UNDECIDED, "value", join_row_ids(by_structure_or_value), parse_note, n_instances)
        else:
            return AutomaticStatus("new", derived[0], derived[1], parse_note, n_instances)

    def _add(
        self,
        row_id: str,
        function_keys: list[tuple],
        cases: dict[str, list[tuple]],
        parsed: ParsedRow | None,
        intervals: ParsedIntervals | None,
        is_decided_incomplete: bool,
    ) -> None:
        """Add a row's function keys to the index, and its cases where it has usable intervals and is complete."""
        for key in function_keys:
            self._first_row.setdefault(key, row_id)
        if is_decided_incomplete or not intervals or intervals.incomplete_case:
            return
        for case in [*cases["structure"], *cases["value"], *cases["text"]]:
            if case:
                self._first_complete_row.setdefault(case, row_id)
        if parsed and len(parsed.instances) > 1:
            has_unpaired_intervals = len({i.key for i in intervals.intervals}) > 1 and all(
                interval.fits(values) for interval in intervals.intervals for values in parsed.instance_parameter_values
            )
            if has_unpaired_intervals or parsed.has_value_sets:
                self._unpaired_rows.add(row_id)

    @staticmethod
    def _function_keys(row: SourceRow, parsed: ParsedRow | None) -> list[tuple]:
        """Return the keys of a row's function: per instance by structure and by value, its family, and its text.

        A row with neither a parsed f nor code in its f_description, such as "not given", has no keys.
        """
        keys = []
        if parsed:
            for instance, values in zip(parsed.instances, parsed.scaled_values, strict=True):
                keys.append(("structure", sp.srepr(instance)))
                if values is not None:
                    keys.append(("value", values))
            keys.append(("family", sp.srepr(parsed.family)))
        text_key = EarlierRowIndex._text_key(row)
        if text_key:
            keys.append(text_key)
        return keys

    @staticmethod
    def _cases(row: SourceRow, parsed: ParsedRow | None, intervals: ParsedIntervals | None) -> dict[str, list[tuple]]:
        """Return a row's case keys by structure, by value (aligned with those by structure) and by text.

        A parsed instance takes every interval that fits its parameter values; the text takes every interval.
        """
        cases: dict[str, list[tuple]] = {"structure": [], "value": [], "text": []}
        if not intervals:
            return cases
        if parsed:
            for instance, values, parameter_values in zip(
                parsed.instances, parsed.scaled_values, parsed.instance_parameter_values, strict=True
            ):
                for interval in intervals.intervals:
                    if interval.fits(parameter_values):
                        cases["structure"].append((("structure", sp.srepr(instance)), interval.key))
                        cases["value"].append((("value", values), interval.key) if values is not None else None)
        text_key = EarlierRowIndex._text_key(row)
        if text_key:
            cases["text"] = [(text_key, interval.key) for interval in intervals.intervals]
        return cases

    @staticmethod
    def _text_key(row: SourceRow) -> tuple | None:
        """Return the key of a row's text: its f or f_description and its parameters, without whitespace and backticks.

        A row whose f_description holds no code, such as "not given", has no text key.
        """
        if row.f or "`" in row.f_description:
            text = re.sub(r"[\s`]", "", row.f or row.f_description)
            return ("text", text + "|" + re.sub(r"[\s`]", "", row.parameters))
        else:
            return None
