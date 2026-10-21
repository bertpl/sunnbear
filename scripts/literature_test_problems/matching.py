"""This module gives each row its automatic status by comparing it with every earlier row.

A row's function has 1 instance per combination of its parameter values. A row's test functions are the pairs of 1
instance and 1 of the row's intervals that matches that instance's parameter values
(`intervals.Interval.matches_parameter_values`). A parsed row's instances are compared with all earlier rows'
instances in 3 ways:

- **structure:** they are equal after an equation `lhs = rhs` becomes `lhs - rhs`, and a constant factor and the sign
  are removed;
- **value:** they agree, up to a constant factor, at the fixed x-values of `functions.SAMPLE_POINTS`, in 40-digit
  arithmetic;
- **family:** the row's expression is equal with its parameters left as symbols.

Every row with code in its f or f_description is also compared by its text: its f or f_description and its
parameters, without whitespace and backticks. A row's test functions count as found when an earlier complete row has
the same instance, by structure or by text, on the same interval.
"""

import re
from dataclasses import dataclass

import sympy as sp

from .data_files import UNDECIDED, AutomaticStatus, FinalStatus, SourceRow, join_row_ids
from .functions import ParsedFunction, X
from .helpers import ParseError, ParseTimeoutError
from .intervals import ParsedIntervals


# ==================================================================================================
#  EarlierRowIndex
# ==================================================================================================
class EarlierRowIndex:
    """An `EarlierRowIndex` holds the rows compared so far, indexed by their functions and by their test functions.

    For each row that the index is given, it finds the earliest matching rows among those compared so far. A function
    key is a pair of a comparison's name and the form of the function that it compares, such as
    `("structure", srepr(instance))`, and a test function key is a pair of a function key and an interval's key.
    """

    def __init__(self) -> None:
        """Start with no rows."""
        # _first_row_by_function maps each function key to the earliest row with that function, complete or not.
        self._first_row_by_function: dict[tuple, str] = {}
        # _first_complete_row_by_test_function maps each test function key to the earliest complete row with it.
        self._first_complete_row_by_test_function: dict[tuple, str] = {}
        # _unpaired_rows holds the complete rows for which the index may hold test functions that their source does
        # not give: rows with several instances and several intervals that no parameter ties to an instance, so that
        # every instance is paired with every interval, and rows whose instances combine several sets of parameter
        # values (`ParsedFunction.has_value_sets`).
        self._unpaired_rows: set[str] = set()

    @classmethod
    def compute_automatic_statuses(
        cls, rows: list[SourceRow], decisions: dict[str, FinalStatus]
    ) -> dict[str, AutomaticStatus]:
        """Return the automatic status of each row, keyed by row id, for rows given in time order.

        A row that `decisions` makes `incomplete` gives no test function, so no later row is a duplicate of it.
        """
        earlier_row_index = cls()
        statuses = {}
        for row in rows:
            is_decided_incomplete = row.row_id in decisions and decisions[row.row_id].status == "incomplete"
            statuses[row.row_id] = earlier_row_index.match_and_add(row, is_decided_incomplete)
        return statuses

    def match_and_add(self, row: SourceRow, is_decided_incomplete: bool) -> AutomaticStatus:
        """Return the automatic status of a row, then add the row to the index.

        The status is the first of these that applies:

        - `incomplete` when the row gives no usable interval, or no function (an f_description without code);
        - `undecided` when its interval does not parse;
        - `duplicate` when every test function of a row whose f does not parse is found by its text, and otherwise
          `undecided`;
        - `undecided` when an instance keeps a parameter without values, or when no interval matches any instance;
        - `duplicate` when every test function is found by structure, unless one is found only in a row whose
          instances and intervals are not paired, which leaves the row `undecided`;
        - `undecided` when every test function is found by structure or by value, but not every one by structure;
        - `new` otherwise, naming the earlier rows that share an instance, the family or the text, whatever their
          intervals.

        `is_decided_incomplete` keeps the row's test functions out of the index.
        """
        try:
            parsed_function = ParsedFunction.from_source_row(row)
        except (ParseError, ParseTimeoutError) as error:
            parsed_function, function_note = None, str(error) or "timeout"
        else:
            function_note = ""
        try:
            intervals = ParsedIntervals.from_source_row(row)
        except (ParseError, ParseTimeoutError) as error:
            intervals, interval_note = None, str(error) or "interval: timeout"
        else:
            interval_note = f"interval: {intervals.n_unusable} left out" if intervals.n_unusable else ""
        parse_note = "; ".join(note for note in (function_note, interval_note) if note)
        n_instances = len(parsed_function.instances) if parsed_function else 0
        function_keys = self._function_keys(row, parsed_function)
        derived_matches = self._derived_matches(function_keys)
        test_function_keys = TestFunctionKeys.from_row(row, parsed_function, intervals)
        if intervals and intervals.incomplete_reason:
            status = AutomaticStatus(
                "incomplete", intervals.incomplete_reason, derived_matches[1], parse_note, n_instances
            )
        elif not function_keys:
            status = AutomaticStatus("incomplete", "no function", "", parse_note, n_instances)
        elif intervals is None:
            status = AutomaticStatus(UNDECIDED, "interval does not parse", derived_matches[1], parse_note, n_instances)
        elif parsed_function is None:
            status = self._match_by_text(test_function_keys.text, derived_matches, parse_note)
        elif any(instance.free_symbols - {X} for instance in parsed_function.instances):
            status = AutomaticStatus(
                UNDECIDED, "parameters without values", derived_matches[1], parse_note, n_instances
            )
        else:
            status = self._match_parsed(test_function_keys, derived_matches, parse_note, n_instances)
        self._add(row.row_id, function_keys, test_function_keys, parsed_function, intervals, is_decided_incomplete)
        return status

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _derived_matches(self, function_keys: list[tuple]) -> tuple[str, str]:
        """Return the comparisons that find earlier rows with any of the function keys, and those rows, as 2 fields."""
        kinds, row_ids = [], []
        for key in function_keys:
            if key in self._first_row_by_function:
                kinds.append(key[0])
                row_ids.append(self._first_row_by_function[key])
        return ", ".join(dict.fromkeys(kinds)), join_row_ids(row_ids)

    def _match_by_text(
        self, text_keys: list[tuple], derived_matches: tuple[str, str], parse_note: str
    ) -> AutomaticStatus:
        """Return the status of a row whose f does not parse: a duplicate if each test function is found by its text."""
        found = [self._first_complete_row_by_test_function.get(key) for key in text_keys]
        if text_keys and all(found):
            return AutomaticStatus("duplicate", "same text", join_row_ids(found), parse_note, n_instances=0)
        else:
            return AutomaticStatus(UNDECIDED, "unparsed", derived_matches[1], parse_note, n_instances=0)

    def _match_parsed(
        self,
        test_function_keys: "TestFunctionKeys",
        derived_matches: tuple[str, str],
        parse_note: str,
        n_instances: int,
    ) -> AutomaticStatus:
        """Return the status of a row whose f and intervals parse, from its test functions by structure and by value."""
        by_structure = [self._first_complete_row_by_test_function.get(key) for key in test_function_keys.structure]
        by_structure_or_value = []
        for found, value_key in zip(by_structure, test_function_keys.value, strict=True):
            if found or value_key is None:
                by_structure_or_value.append(found)
            else:
                by_structure_or_value.append(self._first_complete_row_by_test_function.get(value_key))
        if not test_function_keys.structure:
            return AutomaticStatus(UNDECIDED, "no test function", derived_matches[1], parse_note, n_instances)
        elif all(by_structure) and self._unpaired_rows.isdisjoint(by_structure):
            return AutomaticStatus("duplicate", "structure", join_row_ids(by_structure), parse_note, n_instances)
        elif all(by_structure):
            return AutomaticStatus(UNDECIDED, "unpaired", join_row_ids(by_structure), parse_note, n_instances)
        elif all(by_structure_or_value):
            return AutomaticStatus(UNDECIDED, "value", join_row_ids(by_structure_or_value), parse_note, n_instances)
        else:
            return AutomaticStatus("new", derived_matches[0], derived_matches[1], parse_note, n_instances)

    def _add(
        self,
        row_id: str,
        function_keys: list[tuple],
        test_function_keys: "TestFunctionKeys",
        parsed_function: ParsedFunction | None,
        intervals: ParsedIntervals | None,
        is_decided_incomplete: bool,
    ) -> None:
        """Add a row's function keys to the index, and its test functions where it has usable intervals and is complete.

        The row also joins `_unpaired_rows` where its test functions can be more than its source gives.
        """
        for key in function_keys:
            self._first_row_by_function.setdefault(key, row_id)
        if is_decided_incomplete or not intervals or intervals.incomplete_reason:
            return
        for key in [*test_function_keys.structure, *test_function_keys.value, *test_function_keys.text]:
            if key:
                self._first_complete_row_by_test_function.setdefault(key, row_id)
        if parsed_function and len(parsed_function.instances) > 1:
            is_every_pair_a_test_function = len({interval.key for interval in intervals.intervals}) > 1
            for interval in intervals.intervals:
                for values in parsed_function.instance_parameter_values:
                    if not interval.matches_parameter_values(values):
                        is_every_pair_a_test_function = False
            if is_every_pair_a_test_function or parsed_function.has_value_sets:
                self._unpaired_rows.add(row_id)

    @staticmethod
    def _function_keys(row: SourceRow, parsed_function: ParsedFunction | None) -> list[tuple]:
        """Return the keys of a row's function: per instance by structure and by value, its family, and its text.

        A row with neither a parsed f nor code in its f_description, such as "not given", has no keys.
        """
        keys = []
        if parsed_function:
            for instance, values in zip(parsed_function.instances, parsed_function.scaled_values, strict=True):
                keys.append(("structure", sp.srepr(instance)))
                if values is not None:
                    keys.append(("value", values))
            keys.append(("family", sp.srepr(parsed_function.family)))
        text_key = _text_key(row)
        if text_key:
            keys.append(text_key)
        return keys


# ==================================================================================================
#  TestFunctionKeys
# ==================================================================================================
@dataclass(frozen=True)
class TestFunctionKeys:
    """A `TestFunctionKeys` holds the keys of a row's test functions by structure, by value and by text.

    `value` is aligned with `structure`: it holds, at the position of each key in `structure`, the same test function
    keyed by the instance's scaled values, or None where the instance has no scaled values.
    """

    structure: list[tuple]
    value: list[tuple | None]
    text: list[tuple]

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_row(
        cls, row: SourceRow, parsed_function: ParsedFunction | None, intervals: ParsedIntervals | None
    ) -> "TestFunctionKeys":
        """Return the keys of a row's test functions by structure, by value and by text.

        A parsed instance takes every interval that matches its parameter values; the text takes every interval.
        """
        structure, value, text = [], [], []
        if intervals and parsed_function:
            for instance, values, parameter_values in zip(
                parsed_function.instances,
                parsed_function.scaled_values,
                parsed_function.instance_parameter_values,
                strict=True,
            ):
                for interval in intervals.intervals:
                    if interval.matches_parameter_values(parameter_values):
                        structure.append((("structure", sp.srepr(instance)), interval.key))
                        value.append((("value", values), interval.key) if values is not None else None)
        text_key = _text_key(row)
        if intervals and text_key:
            text = [(text_key, interval.key) for interval in intervals.intervals]
        return cls(structure, value, text)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _text_key(row: SourceRow) -> tuple | None:
    """Return the key of a row's text: its f or f_description and its parameters, without whitespace and backticks.

    A row whose f_description holds no code, such as "not given", has no text key.
    """
    if row.f or "`" in row.f_description:
        text = re.sub(r"[\s`]", "", row.f or row.f_description)
        return ("text", text + "|" + re.sub(r"[\s`]", "", row.parameters))
    else:
        return None
