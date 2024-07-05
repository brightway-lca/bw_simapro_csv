class WasteModelMismatch(Exception):
    """Our understanding of SimaPro waste models doesn't agree with this data"""

    pass


class IndeterminateBlockEnd(Exception):
    pass


class FormulaReservedWord(Exception):
    pass
