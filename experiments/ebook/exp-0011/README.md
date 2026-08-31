# EXP-0011 execution evidence

This directory contains the product-code-free execution contract for
`EXP-0011`. The experiment projects the current identity report for exactly
five TEST-0001 pairs, eight conforming EXP-0010 quality pairs, and two separate
invalid controls into the three variants accepted in the planning contract.

The runner reads versioned synthetic inputs only. EXP-0010 payloads are
rematerialized deterministically in memory by the already-bound EXP-0010
generator; no media files are created. It uses neither network nor containers,
does not write product state, and writes only `result.json` after the complete
preimage has been committed.

Profile validation and tests:

    python tools/experiments/run_exp_0011.py --validate-profile
    python -m unittest tests.experiments.test_exp_0011 -v

Execution from the clean committed preimage:

    python tools/experiments/run_exp_0011.py

Result validation without rerunning the experiment:

    python tools/experiments/run_exp_0011.py --validate-result

After integration, `tools/experiments/validate_exp_0011_result.py` validates
the evidence against the exact historical preimage even if product code later
changes.
