import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from contracts.models import (
    Party, ContractCategory, ClauseCategory, Clause,
    ContractTemplate, Contract
)
from approvals.models import ApprovalChain, ApprovalStep
from obligations.models import ObligationCategory, Obligation


class Command(BaseCommand):
    help = "Seed the database with sample CLM data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Users
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@clm.com", "is_staff": True, "is_superuser": True, "first_name": "Admin", "last_name": "User"},
        )
        admin.set_password("admin")
        admin.save()

        legal, _ = User.objects.get_or_create(
            username="legal",
            defaults={"email": "legal@clm.com", "first_name": "Sarah", "last_name": "Chen"},
        )
        legal.set_password("legal123")
        legal.save()

        finance, _ = User.objects.get_or_create(
            username="finance",
            defaults={"email": "finance@clm.com", "first_name": "James", "last_name": "Wilson"},
        )
        finance.set_password("finance123")
        finance.save()

        manager, _ = User.objects.get_or_create(
            username="manager",
            defaults={"email": "manager@clm.com", "first_name": "Mike", "last_name": "Johnson"},
        )
        manager.set_password("manager123")
        manager.save()

        # Categories
        cat_nda, _ = ContractCategory.objects.get_or_create(name="NDA", description="Non-Disclosure Agreements")
        cat_vendor, _ = ContractCategory.objects.get_or_create(name="Vendor Agreement", description="Vendor/Supplier contracts")
        cat_employment, _ = ContractCategory.objects.get_or_create(name="Employment", description="Employment contracts")
        cat_saas, _ = ContractCategory.objects.get_or_create(name="SaaS", description="Software-as-a-Service agreements")
        cat_partnership, _ = ContractCategory.objects.get_or_create(name="Partnership", description="Partnership agreements")

        # Parties
        party_data = [
            ("Acme Corp", "company", "contracts@acme.com", "John Smith"),
            ("TechStart Inc", "company", "legal@techstart.io", "Lisa Park"),
            ("Global Services LLC", "company", "deals@globalservices.com", "David Brown"),
            ("CloudFirst Solutions", "company", "partnerships@cloudfirst.dev", "Emma Davis"),
            ("DataShield Security", "company", "enterprise@datashield.io", "Robert Kim"),
            ("Pacific Trading Co", "company", "contracts@pacifictrading.com", "Maria Garcia"),
            ("Vertex Analytics", "company", "legal@vertexanalytics.com", "Alex Turner"),
            ("Meridian Healthcare", "company", "contracts@meridianhealth.org", "Dr. Patel"),
        ]
        parties = []
        for name, ptype, email, contact in party_data:
            p, _ = Party.objects.get_or_create(
                name=name, defaults={"party_type": ptype, "email": email, "contact_person": contact}
            )
            parties.append(p)

        # Clause Categories
        cl_cat_conf, _ = ClauseCategory.objects.get_or_create(name="Confidentiality")
        cl_cat_liability, _ = ClauseCategory.objects.get_or_create(name="Liability")
        cl_cat_term, _ = ClauseCategory.objects.get_or_create(name="Termination")
        cl_cat_indemnity, _ = ClauseCategory.objects.get_or_create(name="Indemnification")
        cl_cat_ip, _ = ClauseCategory.objects.get_or_create(name="Intellectual Property")

        # Clauses
        clauses = [
            ("Standard Confidentiality", cl_cat_conf, "low", True, "Each party agrees to maintain the confidentiality of all proprietary information disclosed during the term of this agreement."),
            ("Mutual NDA", cl_cat_conf, "low", True, "Both parties agree not to disclose any confidential information to third parties without prior written consent."),
            ("Limited Liability", cl_cat_liability, "low", True, "In no event shall either party's total liability exceed the total amount paid under this agreement."),
            ("Unlimited Liability", cl_cat_liability, "critical", False, "Each party shall be liable for all damages arising from breach of this agreement without limitation."),
            ("Mutual Indemnification", cl_cat_indemnity, "low", True, "Each party shall indemnify and hold harmless the other party from any claims arising from their breach."),
            ("One-Sided Indemnification", cl_cat_indemnity, "high", False, "Client shall indemnify and hold harmless Provider from all claims arising from this agreement."),
            ("IP Ownership", cl_cat_ip, "medium", True, "All intellectual property created under this agreement shall be owned by the commissioning party."),
            ("Convenient Termination", cl_cat_term, "low", True, "Either party may terminate this agreement with 30 days written notice."),
            ("Lock-In Termination", cl_cat_term, "high", False, "Client may not terminate this agreement for a period of 36 months from the effective date."),
            ("Auto-Renewal with 90-Day Notice", cl_cat_term, "medium", True, "This agreement shall automatically renew for successive 1-year terms unless either party provides 90 days written notice."),
        ]
        clause_objs = []
        for title, cat, risk, approved, content in clauses:
            c, _ = Clause.objects.get_or_create(
                title=title, defaults={
                    "category": cat, "risk_level": risk, "is_pre_approved": approved,
                    "content": content, "created_by": admin
                }
            )
            clause_objs.append(c)

        # Templates
        nda_template, _ = ContractTemplate.objects.get_or_create(
            name="Standard NDA Template",
            defaults={
                "category": cat_nda,
                "description": "Mutual non-disclosure agreement template",
                "content": "This Non-Disclosure Agreement is entered into between {{party_a}} and {{party_b}}...\n\n1. Confidential Information\n{{confidentiality_clause}}\n\n2. Term\nThis agreement shall remain in effect for {{term}} months.\n\n3. Governing Law\nThis agreement shall be governed by the laws of {{governing_law}}.",
                "created_by": admin,
            }
        )
        nda_template.clauses.add(clause_objs[0], clause_objs[1])

        vendor_template, _ = ContractTemplate.objects.get_or_create(
            name="Vendor Service Agreement",
            defaults={
                "category": cat_vendor,
                "description": "Standard vendor service agreement",
                "content": "This Vendor Agreement is between {{client}} and {{vendor}}...\n\n1. Services\n{{vendor}} shall provide the following services: {{service_description}}\n\n2. Payment Terms\n{{payment_terms}}\n\n3. Term and Termination\n{{termination_clause}}",
                "created_by": admin,
            }
        )

        saas_template, _ = ContractTemplate.objects.get_or_create(
            name="SaaS Subscription Agreement",
            defaults={
                "category": cat_saas,
                "description": "SaaS subscription terms",
                "content": "This SaaS Subscription Agreement is between {{customer}} and {{provider}}...\n\n1. Service Description\n{{service_description}}\n\n2. Subscription Fee\n{{subscription_fee}} per {{billing_period}}\n\n3. Data Protection\n{{data_protection_clause}}",
                "created_by": admin,
            }
        )

        # Approval Chains
        chain_standard, _ = ApprovalChain.objects.get_or_create(
            name="Standard Approval",
            defaults={
                "description": "Legal -> Finance -> Manager for standard contracts",
                "min_value": 10000,
                "max_value": 100000,
            }
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_standard, step_number=1,
            defaults={"name": "Legal Review", "approver": legal, "role_required": "legal"}
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_standard, step_number=2,
            defaults={"name": "Finance Review", "approver": finance, "role_required": "finance"}
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_standard, step_number=3,
            defaults={"name": "Manager Approval", "approver": manager, "role_required": "manager"}
        )

        chain_high, _ = ApprovalChain.objects.get_or_create(
            name="High Value Approval",
            defaults={
                "description": "Extended approval for high-value contracts",
                "min_value": 100000,
            }
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_high, step_number=1,
            defaults={"name": "Legal Review", "approver": legal, "role_required": "legal"}
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_high, step_number=2,
            defaults={"name": "Finance Review", "approver": finance, "role_required": "finance"}
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_high, step_number=3,
            defaults={"name": "VP Approval", "approver": admin, "role_required": "executive"}
        )

        chain_low, _ = ApprovalChain.objects.get_or_create(
            name="Quick Approval",
            defaults={
                "description": "Manager-only for low-value contracts",
                "max_value": 10000,
            }
        )
        ApprovalStep.objects.get_or_create(
            chain=chain_low, step_number=1,
            defaults={"name": "Manager Approval", "approver": manager, "role_required": "manager"}
        )

        # Contracts
        today = timezone.now().date()
        contract_data = [
            ("NDA with Acme Corp", "NDA-2024-001", cat_nda, "active", "medium", [parties[0]], 15000, 0),
            ("Vendor Agreement - TechStart", "VND-2024-001", cat_vendor, "active", "medium", [parties[1]], 45000, 30),
            ("SaaS License - CloudFirst", "SAAS-2024-001", cat_saas, "pending_approval", "high", [parties[3]], 120000, 90),
            ("Employment Contract - New Hire", "EMP-2024-001", cat_employment, "active", "low", [parties[5]], 75000, 0),
            ("Partnership Agreement - Vertex", "PTR-2024-001", cat_partnership, "draft", "urgent", [parties[6]], 250000, 0),
            ("Data Processing Agreement - DataShield", "DPA-2024-001", cat_saas, "active", "medium", [parties[4]], 35000, 45),
            ("Vendor Agreement - Global Services", "VND-2024-002", cat_vendor, "expired", "low", [parties[2]], 28000, 0),
            ("NDA - Meridian Healthcare", "NDA-2024-002", cat_nda, "active", "medium", [parties[7]], 12000, 15),
            ("SaaS Enterprise License - CloudFirst", "SAAS-2024-002", cat_saas, "approved", "high", [parties[3]], 180000, 60),
            ("Consulting Agreement - Vertex Analytics", "CON-2024-001", cat_vendor, "draft", "medium", [parties[6]], 55000, 0),
        ]

        for title, number, category, status, priority, contract_parties, value, days_offset in contract_data:
            effective = today - timedelta(days=random.randint(30, 365))
            expiry = effective + timedelta(days=365)
            if days_offset > 0:
                expiry = today + timedelta(days=days_offset)

            contract, created = Contract.objects.get_or_create(
                contract_number=number,
                defaults={
                    "title": title,
                    "category": category,
                    "status": status,
                    "priority": priority,
                    "effective_date": effective,
                    "expiry_date": expiry,
                    "renewal_date": expiry - timedelta(days=30),
                    "auto_renew": random.choice([True, False]),
                    "renewal_notice_days": random.choice([30, 60, 90]),
                    "total_value": value,
                    "content": f"Contract content for {title}.\n\nThis agreement is made between the undersigned parties...",
                    "created_by": admin,
                    "internal_owner": random.choice([admin, legal, manager]),
                    "version": "1.0",
                },
            )
            if created:
                contract.parties.set(contract_parties)

        # Obligations
        ob_cat_compliance, _ = ObligationCategory.objects.get_or_create(name="Compliance")
        ob_cat_delivery, _ = ObligationCategory.objects.get_or_create(name="Deliverables")
        ob_cat_reporting, _ = ObligationCategory.objects.get_or_create(name="Reporting")

        contracts = Contract.objects.all()
        for contract in contracts[:5]:
            Obligation.objects.get_or_create(
                contract=contract,
                title=f"Quarterly compliance report for {contract.title}",
                defaults={
                    "description": "Vendor must submit quarterly compliance report",
                    "category": ob_cat_compliance,
                    "frequency": "quarterly",
                    "status": "pending",
                    "due_date": today + timedelta(days=30),
                    "assigned_to": manager,
                }
            )
            Obligation.objects.get_or_create(
                contract=contract,
                title=f"Annual review for {contract.title}",
                defaults={
                    "description": "Conduct annual contract review",
                    "category": ob_cat_reporting,
                    "frequency": "annual",
                    "status": "pending",
                    "due_date": today + timedelta(days=90),
                    "assigned_to": legal,
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {User.objects.count()} users, {Party.objects.count()} parties, "
            f"{Contract.objects.count()} contracts, {Clause.objects.count()} clauses, "
            f"{ApprovalChain.objects.count()} approval chains, {Obligation.objects.count()} obligations"
        ))
