# avro-resolution-witness

Explain bounded Avro writer-to-reader resolution with field paths, promotions, defaults and union branch evidence.

For data engineers reviewing an inline Avro writer/reader schema change.

## Quickstart

Python3.10+; no external service or runtime dependencies. Linux shell:

```sh
git clone https://github.com/nripankadas07/avro-resolution-witness.git
cd avro-resolution-witness
python -m venv .venv
. .venv/bin/activate
python -m pip install .
avro-resolution-witness example.json
```

The invented example promotes id to long and supplies the new note default. [Expected JSON](example-output.json).

## Input and interpretation

Use the exact object in [example.json](example.json). Unknown keys, duplicate JSON keys and nonfinite numbers reject. The JSON file is read only, <=1MiB. Identifiers are nonempty strings <=128 characters; booleans are not integers.

Inline unqualified schemas only. Primitives, records, enums, fixed, arrays, maps and nonnested unions; <=300 schema nodes, depth24, <=100 fields/symbols and16 union branches. Named definitions must be unique per schema. Reject named references, namespaces/dotted names, aliases, logical types, unknown attributes and record/array/map defaults. Scalar/enum/fixed defaults and union defaults matching one supported branch are checked. All possible writer branches must resolve. First matching reader union branch is selected, then nested resolution checked. No binary decoding, registry access or full Avro validator. Compatibility is one direction only.

Exit0: completed result without a finding/conflict; exit1: documented schema/shared-formula/stockout finding or merge conflict; exit2: malformed/unsupported input, stderr and no partial JSON report. Event-time drops are normal policy decisions and use exit0. A completed report is evidence only about the supplied model and supported subset. No automatic live-system changes.

## Verification

```sh
python -m unittest -v
python -m compileall -q avro_resolution_witness.py
python -m pip wheel --no-deps . -w dist
```

64 primitive pairs, missing defaults, ignored fields, union selection/all branches, enums, fixed sizes, nested array/map promotion and unsupported schema rejection. [Validation record](VALIDATION.md). CI checks Python3.10/3.12/3.14 and a wheel-installed console from outside the checkout. Windows/macOS and production-size workloads are not verified. No benchmark or superiority claim.

## Scope and provenance

Alpha utility, original AI-assisted implementation and invented fixtures. Standard algorithms were reimplemented; no third-party implementation/prose copied. MIT. [Candidate brief](BRIEF.json), [dated research and alternatives](RESEARCH.md), [support](SUPPORT.md), [contribution guide](CONTRIBUTING.md), [security](SECURITY.md).

schema-gen generates JSON models and npm/export tools inspect packages. This traces actual Avro reader/writer evolution rules; it is separate from spreadsheet, streaming, stock and text-merge contracts.
