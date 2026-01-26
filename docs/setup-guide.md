# Setup Guide

## Requirements
- Python 3.9+
- Access to KACE ticket exports or API
- SharePoint site and list for knowledge base

## Configure
1. Copy `config/kace_config.template.json` to `config/kace_config.json`.
2. Copy `config/sharepoint_config.template.json` to `config/sharepoint_config.json`.
3. Set environment variables for credentials.

## Run the Pipeline
```bash
python -m data_pipeline.extractors.kace_connector --config config/kace_config.json
python -m data_pipeline.processors.ticket_processor --input /path/to/export.csv --output knowledge_base/processed.json
python -m data_pipeline.processors.kb_generator --input knowledge_base/processed.json --output knowledge_base/articles.json
python -m data_pipeline.exporters.sharepoint_exporter --input knowledge_base/articles.json --config config/sharepoint_config.json --output knowledge_base/sharepoint_payload.json
```

## Scheduled Runs
```bash
python -m data_pipeline.scheduler \
  --kace-config config/kace_config.json \
  --processor-config config/processor_config.json \
  --output-dir knowledge_base
```
