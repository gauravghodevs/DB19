# Trivy finding: pip embedded SBOM

## Summary

During scanning of secureops-payment-api:0.1.1, Trivy
reported six Python vulnerability findings for msgpack,
setuptools, and urllib3.

## Investigation

The image contains:
`/usr/local/lib/python3.11/site-packages/pip/_vendor/bom.cdx.json`

This embedded CycloneDX SBOM lists:

- msgpack 1.1.2

- setuptools 70.3.0

- urllib3 2.7.0

Runtime package checks showed setuptools 84.0.0 installed,
while msgpack and urllib3 were not installed as separate
Python distributions.

A diagnostic scan using --skip-files
"**/pip/_vendor/bom.cdx.json" removed all six findings.

## Interpretation

The findings originate from pip's vendored dependency
inventory, not the active top-level Python distributions.
Vendored code is still physically present in the image, so
the findings must not be automatically classified as harmless.

## Handling

- Preserve the original Trivy report.

- Keep the diagnostic report separate.

- Review the vendored code and each vulnerability's applicability.

- Document any accepted risk or exception with evidence.

- Continue scanning the complete image, including OS packages.
