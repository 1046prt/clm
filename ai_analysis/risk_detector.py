import json
import time
import logging

from django.conf import settings
from django.utils import timezone

from ai_analysis.extractor import extract_text_from_file

logger = logging.getLogger(__name__)

RISK_DETECTION_PROMPT = """You are a legal risk analysis AI. Analyze the following contract text and identify ALL risky, unusual, or potentially harmful clauses.

For each risk found, provide:
{
    "risks": [
        {
            "severity": "low|medium|high|critical",
            "category": "Risk category name",
            "title": "Short title of the risk",
            "description": "Detailed explanation of why this is risky",
            "clause_reference": "The specific text from the contract that triggers this risk",
            "recommendation": "What the user should do about this risk"
        }
    ]
}

Common risk patterns to look for:
- Auto-renewal clauses without adequate notice periods
- One-sided indemnification (only one party indemnifies)
- Unlimited liability caps
- Unfavorable termination terms
- Missing force majeure provisions
- Overly broad non-compete or non-solicitation clauses
- Unreasonable penalty/liquidated damages clauses
- One-sided governing law/jurisdiction
- Missing data protection/privacy provisions
- Ambiguous payment terms
- Excessive warranty periods
- Unilateral amendment rights
- Missing dispute resolution mechanisms

Only return the JSON object, no additional text.

Contract text:
---
{contract_text}
---"""


def detect_risks(analysis, user=None):
    from ai_analysis.models import RiskFlag

    contract = analysis.contract
    start_time = time.time()

    try:
        contract_text = extract_text_from_file(contract)
        if not contract_text.strip():
            raise ValueError("No text content found in the contract")

        prompt = RISK_DETECTION_PROMPT.format(contract_text=contract_text[:50000])

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

        data = json.loads(response_text)
        risks = data.get("risks", [])

        created_flags = []
        for risk in risks:
            flag = RiskFlag.objects.create(
                analysis=analysis,
                severity=risk.get("severity", "medium"),
                category=risk.get("category", "General"),
                title=risk.get("title", "Unnamed Risk"),
                description=risk.get("description", ""),
                clause_reference=risk.get("clause_reference", ""),
                recommendation=risk.get("recommendation", ""),
            )
            created_flags.append(flag)

        analysis.raw_response = {
            **analysis.raw_response,
            "risk_analysis": risks,
        }
        analysis.processing_time_seconds = (analysis.processing_time_seconds or 0) + (time.time() - start_time)
        analysis.save()

        return created_flags

    except Exception as e:
        logger.error(f"Risk detection failed: {e}")
        return []
