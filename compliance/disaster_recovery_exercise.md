# Disaster Recovery Exercise

Run quarterly and before major production architecture changes.

1. Record release commit, database identifier, backup timestamp, checksum, and operator.
2. Restore the encrypted logical backup into an isolated TEST database.
3. Run migrations and the rigorous golden gate.
4. Verify tenant counts, portfolio relationships, authentication, health, and critical reports.
5. Record recovery-point objective, recovery-time objective, failures, owner, and due date.
6. Destroy the temporary restore only after evidence is retained.

Never restore production data into DEV. TEST restores require approved access and masking where applicable.
