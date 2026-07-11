# V0 to AI Foundation V1 Mapping

## Decision

The current database, parsers, mock generator, calculations, and dashboards remain operational as V0. They are not the final domain model. AI Foundation V1 is an additive compatibility and governance layer; it does not destructively rewrite V0.

## Current-to-future map

| V0 concept | Current use | AI Foundation V1 treatment | Longer-term direction |
|---|---|---|---|
| `Client` | SaaS customer and generation defaults | Required tenant/client scope | Separate tenant, legal entity, and organization profile after identity design |
| `Portfolio` | Groups client files and schedules | Required optional portfolio scope | Keep as stable business grouping with explicit membership/effective dates |
| Client `lat/lon/capacity/farm_type` | First-cut forecast inputs | Do not copy as canonical truth | Register one or more versioned site/asset entities and effective configurations |
| `DailyFile` | Parsed report metadata | Existing operational record | Link future uploads to immutable `SourceArtifact` and parser/contract versions |
| `Transaction` | 15-minute DOR/SCH values | Existing dashboard fact | Evolve toward normalized interval observations with metric, unit, source, and quality status |
| DOR/SCH + DAM/RTM/GDAM strings | Current report classification | Accepted V0 source values | Configure report/market product definitions; avoid permanent database enums |
| `summary`, `charges`, metadata JSON | Flexible parser payloads | Preserve for compatibility | Validate each payload against a named source/canonical schema version |
| Monthly calculations | First-cut derived results | Existing calculation output | Add calculation-run lineage, rule version, input references, and reproducibility |
| Energy schedule month/day | Current schedule presentation | Existing operational read model | Build future schedules from versioned interval facts and effective rules |
| Workbook rows | Internal solar/IEX/TNEB result view | Existing V0 result | Replace hardcoded source columns only after stable procurement domain review |
| Synthetic mock reports | Dashboard/demo baseline | Register as `is_synthetic=true` | Maintain versioned defect, forecasting, and optimization evaluation datasets |

## New AI Foundation V1 records

### CanonicalEntity

Represents evolving entities such as site, connection point, meter, solar asset, battery, contract, tariff account, market account, or future types. `entity_type` and versioned `attributes` prevent early schema lock-in.

### SourceArtifact

Registers immutable source identity, checksum, schema, parser, version, lineage, storage reference, and synthetic status. It does not duplicate the source payload or store credentials.

### ProcessingRun

Records which agent/service version classified, parsed, validated, or normalized a source, including correlation ID, inputs, outputs, errors, and timestamps.

### BusinessRuleVersion

Stores effective-dated tariffs, market rules, solar-bank policies, losses, charges, constraints, and configuration. Active rules require named human approval.

### AIExecutionAudit

Records actor, capability, contract/model/prompt/tool versions, evidence references, output, confidence, limitations, scope, and outcome. Hidden chain-of-thought is explicitly excluded.

### DecisionRecord

Stores title, summary, rationale, evidence, alternatives, limitations, confidence, status, and human-review policy. A deterministic narrative makes the same facts understandable to specialists without changing the structured agent contract.

## Compatibility workflow

```text
V0 source/upload
  -> register SourceArtifact
  -> record parser/validation ProcessingRun
  -> map stable business objects to CanonicalEntity
  -> resolve effective BusinessRuleVersion
  -> existing V0 calculation/API remains authoritative
  -> record AIExecutionAudit for explanation
  -> create proposed DecisionRecord for human review
```

## Promotion rules

A flexible attribute should become a dedicated normalized table/column only when:

- its meaning is stable and approved by a domain specialist;
- it is used frequently for filtering, joining, constraints, or reporting;
- units and effective-date behavior are defined;
- migration and backward compatibility are planned;
- deterministic tests exist.

## Known gaps after AI-0

- Full SaaS JWT/RBAC must replace or complement the initial service credential.
- Object storage is not yet provisioned; `storage_uri` is a reference contract.
- Source-to-V0 upload integration will be built with the AI-1 Data Quality workflow.
- Rule payload schemas need domain-specific validators as each rule family is approved.
- No forecast, optimization, or market execution is authorized in AI-0.
