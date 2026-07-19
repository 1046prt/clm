import json
import time
import logging
from datetime import date

from django.conf import settings
from django.utils import timezone

from contracts.models import Contract

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a legal contract analysis AI. Extract the following metadata from the contract text below.
Return a JSON object with exactly these fields:

{
    "parties_involved": [{"name": "...", "role": "..."}],
    "effective_date": "YYYY-MM-DD or null",
    "expiry_date": "YYYY-MM-DD or null",
    "renewal_terms": "...",
    "payment_terms": "...",
    "termination_clauses": "...",
    "liability_cap": "...",
    "governing_law": "...",
    "jurisdiction": "...",
    "non_compete_clause": true/false,
    "confidentiality_clause": true/false,
    "indemnification_clause": true/false,
    "auto_renewal": true/false,
    "force_majeure": true/false,
    "summary": "Brief 2-3 sentence summary of the contract"
}

Only return the JSON object, no additional text.

Contract text:
---
{contract_text}
---"""


def extract_text_from_file(contract):
    text = contract.content or ""
    if contract.uploaded_file:
        try:
            file_path = contract.uploaded_file.path
            if file_path.endswith(".pdf"):
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text() or ""
                text = pdf_text or text
            elif file_path.endswith(".docx"):
                from docx import Document
                doc = Document(file_path)
                docx_text = "\n".join([para.text for para in doc.paragraphs])
                text = docx_text or text
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
    return text


def analyze_contract(contract, user=None):
    from ai_analysis.models import AnalysisResult, ExtractedMetadata

    analysis = AnalysisResult.objects.create(
        contract=contract,
        initiated_by=user,
        status="processing",
        model_used=settings.AI_MODEL,
    )

    start_time = time.time()

    try:
        contract_text = extract_text_from_file(contract)
        if not contract_text.strip():
            raise ValueError("No text content found in the contract")

        prompt = EXTRACTION_PROMPT.format(contract_text=contract_text[:50000])

        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        metadata = json.loads(response_text)

        analysis.raw_response = metadata
        analysis.tokens_used = message.usage.input_tokens + message.usage.output_tokens
        analysis.processing_time_seconds = time.time() - start_time
        analysis.status = "completed"
        analysis.completed_at = timezone.now()
        analysis.save()

        ExtractedMetadata.objects.create(
            analysis=analysis,
            parties_involved=metadata.get("parties_involved", []),
            effective_date=_parse_date(metadata.get("effective_date")),
            expiry_date=_parse_date(metadata.get("expiry_date")),
            renewal_terms=metadata.get("renewal_terms", ""),
            payment_terms=metadata.get("payment_terms", ""),
            termination_clauses=metadata.get("termination_clauses", ""),
            liability_cap=metadata.get("liability_cap", ""),
            governing_law=metadata.get("governing_law", ""),
            jurisdiction=metadata.get("jurisdiction", ""),
            non_compete_clause=metadata.get("non_compete_clause", False),
            confidentiality_clause=metadata.get("confidentiality_clause", False),
            indemnification_clause=metadata.get("indemnification_clause", False),
            auto_renewal=metadata.get("auto_renewal", False),
            force_majeure=metadata.get("force_majeure", False),
            extracted_text_summary=metadata.get("summary", ""),
        )

        return analysis

    except Exception as e:
        logger.error(f"Contract analysis failed: {e}")
        analysis.status = "failed"
        analysis.error_message = str(e)
        analysis.processing_time_seconds = time.time() - start_time
        analysis.save()
        return analysis


def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
