"""
Pleadings Prompts Service

This module contains specialized prompts for extracting pleadings and claims
from Kenyan court case documents.
"""

from typing import Dict, Any


class PleadingsPrompts:
    """
    Service for generating prompts to extract detailed pleadings and claims.

    This service provides templated prompts focused on extracting comprehensive
    information about pleadings, claims, defenses, and procedural aspects.
    """

    @staticmethod
    def get_comprehensive_pleadings_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate comprehensive prompt for extracting ALL pleadings and claims.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for comprehensive pleadings extraction
        """
        return f"""
You are a legal expert analyzing a Kenyan court case. Please extract ALL pleadings and claims raised by each party in the following case:

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED COMPREHENSIVE ANALYSIS:

1. **PARTIES IDENTIFICATION**:
   - Plaintiff/Appellant: [Full name and details]
   - Defendant/Respondent: [Full name and details]
   - Any other parties involved: [Names and roles]
   - Legal representatives: [Lawyers/advocates involved]

2. **DETAILED PLEADINGS BY PLAINTIFF/APPELLANT**:
   - Primary claims: [List ALL claims with specific details]
   - Legal grounds: [Specific legal principles and statutes cited]
   - Relief sought: [Exact relief requested]
   - Evidence presented: [All evidence mentioned, even minor details]
   - Arguments made: [Complete arguments, including procedural points]
   - Any counter-arguments to defendant's position: [If any]
   - Specific amounts claimed: [Exact monetary amounts if any]
   - Time periods involved: [Any relevant time periods]

3. **DETAILED PLEADINGS BY DEFENDANT/RESPONDENT**:
   - Primary defenses: [List ALL defenses with specific details]
   - Legal grounds: [Specific legal principles and statutes cited]
   - Counter-claims: [If any counter-claims were made]
   - Evidence presented: [All evidence mentioned, even minor details]
   - Arguments made: [Complete arguments, including procedural points]
   - Any challenges to plaintiff's position: [If any]
   - Specific amounts disputed: [Exact amounts if any]
   - Alternative relief sought: [If any]

4. **PROCEDURAL PLEADINGS**:
   - Preliminary objections: [Any procedural objections raised]
   - Jurisdictional issues: [If any jurisdiction challenges]
   - Admissibility of evidence: [Any evidence admissibility challenges]
   - Service of process: [Any service-related issues]
   - Time limitations: [Any statute of limitations arguments]
   - Venue challenges: [If any venue-related issues]
   - Joinder applications: [If any party joinder issues]

5. **MINOR DETAILS AND NUANCES**:
   - Specific dates mentioned: [All relevant dates]
   - Amounts claimed: [Exact monetary amounts if any]
   - Specific documents referenced: [All documents mentioned]
   - Witness statements: [Any witness evidence]
   - Expert opinions: [If any expert evidence]
   - Affidavits filed: [Any affidavits mentioned]
   - Exhibits attached: [Any exhibits referenced]
   - Any other minor pleadings or claims: [Catch-all for anything missed]

6. **LEGAL CITATIONS AND REFERENCES**:
   - Statutes cited: [All statutory provisions]
   - Case law references: [All precedent cases]
   - Constitutional provisions: [If any constitutional issues]
   - International law: [If any international law references]
   - Legal principles: [All legal doctrines mentioned]

7. **EVIDENCE AND DOCUMENTATION**:
   - Documentary evidence: [All documents mentioned]
   - Physical evidence: [Any physical evidence]
   - Electronic evidence: [Any digital evidence]
   - Expert reports: [Any expert reports]
   - Witness statements: [All witness evidence]
   - Affidavits: [All affidavits mentioned]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor
- Include specific legal citations and references
- Preserve exact language where possible
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on factual pleadings rather than legal conclusions
- Include all procedural aspects mentioned
- Capture all evidence and documentation referenced

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_claims_extraction_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate prompt specifically for extracting claims and relief sought.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for claims extraction
        """
        return f"""
You are a legal expert extracting specific claims and relief sought from a Kenyan court case.

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:6000]}  # Limit content length for API

REQUIRED ANALYSIS:

1. **PLAINTIFF/APPELLANT CLAIMS**:
   - Primary claim: [Main claim being made]
   - Secondary claims: [Any additional claims]
   - Legal basis: [Legal grounds for each claim]
   - Relief sought: [Specific relief requested]
   - Amount claimed: [Monetary amounts if any]
   - Declaratory relief: [Any declaratory orders sought]
   - Injunctive relief: [Any injunctions sought]
   - Specific performance: [If specific performance sought]

2. **DEFENDANT/RESPONDENT DEFENSES**:
   - Primary defense: [Main defense raised]
   - Alternative defenses: [Any alternative defenses]
   - Counter-claims: [If any counter-claims made]
   - Set-off claims: [If any set-off pleaded]
   - Contributory negligence: [If applicable]
   - Limitation defenses: [Any time limitation defenses]

3. **SPECIFIC DETAILS**:
   - Exact amounts: [All monetary amounts mentioned]
   - Time periods: [All relevant time periods]
   - Specific dates: [All important dates]
   - Property details: [If property involved]
   - Contract terms: [If contract dispute]
   - Employment details: [If employment dispute]

RESPOND WITH DETAILED STRUCTURED ANALYSIS:
"""

    @staticmethod
    def get_evidence_extraction_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate prompt for extracting evidence and documentation details.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for evidence extraction
        """
        return f"""
You are a legal expert extracting evidence and documentation details from a Kenyan court case.

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:6000]}  # Limit content length for API

REQUIRED ANALYSIS:

1. **DOCUMENTARY EVIDENCE**:
   - Contracts: [All contracts mentioned]
   - Letters: [All correspondence]
   - Reports: [Any reports filed]
   - Certificates: [Any certificates]
   - Receipts: [Any receipts or invoices]
   - Photographs: [Any photographs]
   - Maps/Plans: [Any maps or plans]
   - Medical reports: [If any medical evidence]

2. **WITNESS EVIDENCE**:
   - Witness names: [All witnesses mentioned]
   - Witness statements: [Summary of statements]
   - Expert witnesses: [Any expert witnesses]
   - Expert reports: [Any expert reports]
   - Cross-examination: [Any cross-examination details]

3. **PHYSICAL EVIDENCE**:
   - Items produced: [Any physical items]
   - Forensic evidence: [Any forensic analysis]
   - Site visits: [Any site inspections]
   - Demonstrative evidence: [Any demonstrative evidence]

4. **ELECTRONIC EVIDENCE**:
   - Emails: [Any email evidence]
   - Text messages: [Any SMS evidence]
   - Social media: [Any social media evidence]
   - Digital records: [Any digital documentation]

RESPOND WITH DETAILED STRUCTURED ANALYSIS:
"""

    @staticmethod
    def get_procedural_pleadings_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate prompt for extracting procedural pleadings and objections.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for procedural pleadings extraction
        """
        return f"""
You are a legal expert extracting procedural pleadings and objections from a Kenyan court case.

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:6000]}  # Limit content length for API

REQUIRED ANALYSIS:

1. **PRELIMINARY OBJECTIONS**:
   - Jurisdiction: [Any jurisdiction challenges]
   - Limitation: [Any time limitation objections]
   - Service: [Any service of process issues]
   - Parties: [Any party-related objections]
   - Cause of action: [Any cause of action objections]
   - Res judicata: [If res judicata pleaded]
   - Estoppel: [If estoppel pleaded]

2. **PROCEDURAL APPLICATIONS**:
   - Amendment applications: [Any amendment requests]
   - Joinder applications: [Any joinder requests]
   - Consolidation: [If cases consolidated]
   - Stay applications: [Any stay requests]
   - Security for costs: [If security sought]
   - Discovery applications: [Any discovery requests]

3. **EVIDENCE OBJECTIONS**:
   - Admissibility: [Any admissibility challenges]
   - Hearsay: [Any hearsay objections]
   - Privilege: [Any privilege claims]
   - Relevance: [Any relevance objections]
   - Best evidence: [Any best evidence rule issues]

4. **PROCEDURAL IRREGULARITIES**:
   - Non-compliance: [Any non-compliance issues]
   - Delay: [Any delay-related issues]
   - Abuse of process: [If abuse of process alleged]
   - Vexatious litigation: [If vexatious litigation alleged]

RESPOND WITH DETAILED STRUCTURED ANALYSIS:
"""