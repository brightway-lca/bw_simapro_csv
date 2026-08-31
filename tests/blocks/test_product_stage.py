from io import StringIO

from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Process, ProductStage

# A minimal `{product stages}` export: one ordinary process plus one assembly
# product stage that references the process (by name) and a sub-assembly.
STAGES_CSV = """{SimaPro 10.2.0.1}
{product stages}
{Project: Demo}
{CSV Format version: 9.0.0}
{CSV separator: Semicolon}
{Decimal separator: .}
{Date separator: /}
{Short date format: M/d/yyyy}

Process

Category type
material

Process identifier
FOO000000000000000001

Products
Widget;kg;1;100;not defined;Cat\\Sub;a comment

Materials/fuels

End

Product stage

Category type
assembly

Status


Products
My Assembly (Top);p;1;Cat\\Path;1234 units;

Materials/assemblies
Sub Assembly X;p;1234;Undefined;0;0;0;;

Processes
Widget;kg;7120/1234;Undefined;0;0;0;a note;

Input parameters

Calculated parameters

End
"""


def _parse():
    return SimaProCSV(StringIO(STAGES_CSV), write_logs=False, stderr_logs=False)


def test_product_stage_is_parsed_not_dropped():
    sp = _parse()
    stages = [b for b in sp.blocks if isinstance(b, ProductStage)]
    assert len(stages) == 1
    # A product stage must not be mistaken for a process.
    assert not any(isinstance(b, ProductStage) and isinstance(b, Process) for b in sp.blocks)


def test_product_stage_metadata_and_sections():
    sp = _parse()
    stage = next(b for b in sp.blocks if isinstance(b, ProductStage))
    assert stage.parsed["metadata"]["Category type"] == "assembly"
    # Blank-valued metadata (Status) is dropped, like a process.
    assert "Status" not in stage.parsed["metadata"]
    assert set(stage.blocks) == {"Products", "Materials/assemblies", "Processes"}


def test_product_stage_reference_row():
    sp = _parse()
    stage = next(b for b in sp.blocks if isinstance(b, ProductStage))
    ref = stage.blocks["Products"].parsed[0]
    # Product-stage reference layout is name;unit;amount;category;comment - no
    # allocation/waste-type columns, so the category lands in column 3.
    assert ref["name"] == "My Assembly (Top)"
    assert ref["unit"] == "p"
    assert ref["amount"] == 1.0
    assert ref["category"] == "Cat\\Path"
    assert ref["comment"] == "1234 units"


def test_product_stage_components_reference_by_name():
    sp = _parse()
    stage = next(b for b in sp.blocks if isinstance(b, ProductStage))
    sub = stage.blocks["Materials/assemblies"].parsed[0]
    assert sub["name"] == "Sub Assembly X"
    assert sub["amount"] == 1234.0
    proc = stage.blocks["Processes"].parsed[0]
    # An expression amount is kept as a formula, not evaluated.
    assert proc["name"] == "Widget"
    assert proc["formula"] == "7120/1234"
