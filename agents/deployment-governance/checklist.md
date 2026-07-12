# Deployment Governance Checklist

- [ ] Target environment explicitly identified.
- [ ] Branch and commit SHA verified.
- [ ] Database service is environment-specific.
- [ ] Secrets are environment-specific and not printed.
- [ ] Required golden gate selected and passed.
- [ ] Railway deployment reached `SUCCESS`.
- [ ] Health and API smoke checks passed.
- [ ] Test evidence retained.
- [ ] Production backup confirmed.
- [ ] Cofounder approval recorded for production.
- [ ] Rollback target recorded.
