# Durable evidence verification

1. Retain the trusted anchor independently of this export.
2. Run verify_export(export_root, trusted_anchor).
3. Reject missing objects, altered bytes, truncation, or anchor mismatch.
4. Do not infer success from report generation or cleanup.
