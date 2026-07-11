# AI Governance Checklist

- Client scope is required and portfolio ownership is validated.
- Actual and synthetic data are explicitly distinguished.
- Source, parser, contract, rule, model, and prompt versions are recorded where applicable.
- Capabilities use Pydantic request/response contracts and endpoint registry metadata.
- Authentication fails closed when required configuration is absent.
- Output includes evidence, confidence, limitations, and review policy.
- Hidden chain-of-thought is not stored.
- LLM text is not used as an authoritative schedule or calculation.
- Controlled writes are idempotent or carry a version key.
- Consequential actions require explicit approval and audit.
- Tests are deterministic, tenant-isolated, and production-safe.
