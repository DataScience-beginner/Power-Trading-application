# Conversational Assistant Memory

## AI-1.5 baseline

- Database-backed users support platform_admin and client_user roles.
- Client users are bound to one client and may have portfolio restrictions.
- Conversations are fixed to an authorized scope and owned by one user.
- Groq llama-3.1-8b-instant is optional; deterministic fallback is mandatory.
- Prompt/system/credential/SQL and consequential-action requests are blocked before tool routing.
