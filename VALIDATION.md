# Validation — 21 October 2026

64 primitive pairs, missing defaults, ignored fields, union selection/all branches, enums, fixed sizes, nested array/map promotion and unsupported schema rejection.

All behavior tests passed locally on Python3.12/Linux. Local compile, offline wheel build, new isolated venv installation and installed console from outside checkout passed; failure cases and input preservation passed. Local runtime: Python3.12.14, Linux x86_64. Remote Python3.10/3.12/3.14 matrix and public heads must be verified before LIVE. No competitor benchmark.
