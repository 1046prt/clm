# Contract Lifecycle Management Platform

> An enterprise-grade, AI-augmented contract management system that orchestrates the full lifecycle of commercial agreements — from inception through execution, performance, and termination.

## Overview

Built to address the operational inefficiencies inherent in conventional contract management workflows, this platform eliminates fragmented email-based approval chains, manual clause review, and missed renewal windows. It serves as a centralized, auditable system of record for all contractual obligations and institutional commitments.

---

## Core Capabilities

### 1. Contract Repository & Version Control

- Centralized contract storage with full-text search across metadata, parties, and clause content
- Immutable version history tracking every redline and editorial modification through negotiation cycles
- Confidential access controls with designated contract ownership
- Automated text extraction from uploaded PDF and DOCX artifacts via PyPDF2 and python-docx

### 2. Clause Library & Template Engine

- Pre-approved clause repository with risk-level classifications (Low, Medium, High, Critical)
- Reusable contract templates with parameterized `{{variable}}` placeholder blocks
- Category-driven organization enabling rapid assembly of bespoke agreements from vetted components

### 3. Configurable Approval Workflow Engine

- Multi-stage, condition-based approval chains triggered automatically by contract category, value thresholds, or organizational rules
- Role-gated approver assignment (Legal, Finance, Executive) with granular approve/reject/change-request controls
- Complete audit trail capturing actor identity, timestamp, and decision rationale for every governance action
- Configurable escalation paths with sequential and parallel review stages

### 4. Automated Contract Intelligence

- **Automated Metadata Extraction**: LLM-driven parsing of uploaded contracts to extract parties, effective dates, expiry, payment terms, liability caps, governing law, and jurisdiction
- **Risk Flagging Engine**: Pattern-matching analysis identifying anomalous clauses — auto-renewal without notice, one-sided indemnification, unlimited liability, missing force majeure provisions
- **Severity Classification**: Risk flags categorized as Low, Medium, High, or Critical with actionable remediation recommendations
- Powered by Claude via the Anthropic API with token usage tracking and processing latency metrics

### 5. Obligation & Renewal Lifecycle Management

- Proactive renewal monitoring with 30/60/90-day advance notification windows
- Recurring obligation scheduling (Weekly, Monthly, Quarterly, Annual) with automated due-date tracking
- Overdue detection with real-time dashboard visibility into compliance gaps
- Dismissible alert system for expiring contracts and pending deliverables

### 6. Cryptographic E-Signature Integration

- Dual-mode signature capture: typed name rendering and freehand canvas-based drawing with touch support
- SHA-256 cryptographic hash generation for signature integrity verification
- Complete signing audit log capturing actor email, IP address, user agent, and timestamp
- Sequential signing workflow with configurable signer ordering

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/clm.git
cd clm

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL, ANTHROPIC_API_KEY, and SECRET_KEY

# Run migrations
python manage.py migrate

# Seed sample data (creates users, contracts, parties, approval chains)
python manage.py seed_data

# Create admin superuser
python manage.py createsuperuser

# Launch development server
python manage.py runserver
```

## API Configuration

### Anthropic (Required for AI Analysis)

```env
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL=claude-sonnet-4-20250514
```

### Database (Production)

```env
DATABASE_URL=postgres://user:password@localhost:5432/clm_db
```

### Background Processing

```env
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## Data Model

```model
Party ──────────┐
                 ├──▶ Contract ──▶ ContractVersion
ContractCategory─┘       │
                         ├──▶ ApprovalRequest ──▶ ApprovalAction
                         │         └──▶ ApprovalChain ──▶ ApprovalStep
                         │
                         ├──▶ Obligation ──▶ ObligationCategory
                         ├──▶ RenewalAlert
                         │
                         ├──▶ AnalysisResult ──▶ ExtractedMetadata
                         │         └──▶ RiskFlag
                         │
                         ├──▶ SignatureRequest ──▶ Signature
                         │         └──▶ SigningAuditLog
                         │
                         └──▶ ContractComment

ContractTemplate ──▶ Clause (M2M)
                └──▶ ContractCategory
Clause ──▶ ClauseCategory
```

---

## Security Considerations

- Environment-based secret management via `python-dotenv`
- CSRF protection on all state-mutating endpoints
- `@login_required` enforcement across all views
- `.env`, `db.sqlite3`, and `media/` excluded from version control via `.gitignore`
- No hardcoded credentials, API keys, or secrets in source code
- SHA-256 signature hashing for tamper-evident audit records

---

## Production Deployment Notes

1. Set `DEBUG=False` and configure `ALLOWED_HOSTS`
2. Generate a cryptographically secure `DJANGO_SECRET_KEY`
3. Switch from SQLite to PostgreSQL
4. Configure static file serving via WhiteNoise or CDN
5. Implement Celery workers for background task processing
6. Add rate limiting to AI analysis endpoints
7. Implement object-level authorization checks
8. Configure TLS termination and security headers

---
