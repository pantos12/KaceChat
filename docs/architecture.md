# Architecture Overview

## Data Flow
1. **Extract** tickets from KACE via API or CSV exports.
2. **Process** tickets to filter resolved items, classify categories, and compute confidence scores.
3. **Cluster** similar issues to deduplicate KB articles.
4. **Generate** KB articles with normalized schema.
5. **Export** to SharePoint list for Copilot Studio knowledge source.

## Security
- Store credentials in environment variables.
- Prefer app registrations for unattended jobs (service principal).
- If SSO with Duo 2FA is required, use delegated auth for manual runs.
