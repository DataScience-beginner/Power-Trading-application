# Data Quality Memory

## AI-1 baseline

- The initial engine evaluates V0 DailyFile and Transaction records through a dynamic QualityPolicy.
- Default expectations mirror the current six report types and 96 blocks but are explicitly overrideable.
- V0 files are not yet automatically linked to AI-0 SourceArtifact records; responses disclose this limitation.
- Findings are persisted, but automatic correction is forbidden.
