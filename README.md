# KACE Chatbot Knowledge Base Pipeline

This repository contains a Python-based data pipeline that extracts resolved KACE Quest tickets (via API or file exports), transforms them into knowledge base (KB) articles, and prepares them for SharePoint ingestion for Microsoft Copilot Studio.

## Features
- **Extraction**: Pull from KACE API (placeholder) or parse file exports (CSV).
- **Processing**: Filter for resolved tickets, categorize issues, and score resolution quality and time-to-resolution.
- **Similarity**: Cluster similar issues to deduplicate KB articles.
- **KB Generation**: Normalize tickets into a structured KB schema.
- **Export**: Prepare SharePoint-friendly JSON payloads (placeholder for upload).
- **Automation-ready**: Designed for GitHub Actions or Azure Functions.

## Repository Layout
```
/data_pipeline
  /extractors
  /processors
  /exporters
/config
/knowledge_base
/tests
/scripts
/docs
/copilot-config
/power-automate-flows
```

## Quick Start
1. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r data_pipeline/requirements.txt
   ```

3. **Configure credentials**
   - Copy `config/kace_config.template.json` to `config/kace_config.json`
   - Copy `config/sharepoint_config.template.json` to `config/sharepoint_config.json`
   - Set environment variables referenced in the templates

4. **Run extraction and processing**
   ```bash
   python -m data_pipeline.extractors.kace_connector --config config/kace_config.json
   python -m data_pipeline.processors.ticket_processor --input /path/to/export.csv --output knowledge_base/processed.json
   python -m data_pipeline.processors.kb_generator --input knowledge_base/processed.json --output knowledge_base/articles.json
   ```

5. **Export KB payloads**
   ```bash
   python -m data_pipeline.exporters.sharepoint_exporter --input knowledge_base/articles.json --config config/sharepoint_config.json --output knowledge_base/sharepoint_payload.json
   python -m data_pipeline.exporters.dataverse_exporter --input knowledge_base/articles.json --config config/dataverse_config.json --output knowledge_base/dataverse_payload.json
   ```

6. **Run the scheduled pipeline**
   ```bash
   python -m data_pipeline.scheduler \
     --kace-config config/kace_config.json \
     --processor-config config/processor_config.json \
     --output-dir knowledge_base
   ```

## Authentication Notes
- For **SSO with 2FA**, automated pipelines typically use **app registrations** with delegated permissions or app-only access in SharePoint. The `sharepoint_config.template.json` assumes a service principal for unattended runs; adjust if your security policy requires delegated tokens.

## Copilot Studio Setup
- Topic definitions: `copilot-config/topics/topic_definitions.json`
- Generative answers config: `copilot-config/generative-answers-config.json`
- Power Automate flow templates: `power-automate-flows/*.json`

## Git Branch Initialization
If your hosting UI reports that the feature branch has no history in common with `main`, you can create a local `main` branch from your current history and set it as the default branch before pushing:

```bash
./scripts/init-main-branch.sh
```

After running the script, set the remote default branch to `main` and push your branches again.
If a remote named `origin` exists, the script also updates `origin/HEAD` to point to `origin/main`.

## Free / Low-Cost AI Options
If you want AI-assisted answers without paid APIs, consider local inference:
- **Ollama**: Run models locally (no API fees) and integrate via a local HTTP endpoint.
- **Local LLM servers** (e.g., LM Studio): Provide OpenAI-compatible endpoints on your network.

These options work best for internal users when you can host the model behind your firewall. You can combine them with the KB pipeline by adding a “semantic answer” layer that uses the generated KB articles as context.

## Next Steps
- Confirm KACE API availability and field mappings.
- Provide a real SharePoint upload flow (Power Automate or Graph API).
- Add classification/similarity models to improve KB clustering.

## License
Internal use only.
