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
You are a senior legal expert specializing in Kenyan law, tasked with extracting comprehensive pleadings and claims from a court case. Your analysis must be extremely detailed, accurate, and relevant to the specific case at hand.

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED COMPREHENSIVE ANALYSIS:

1. **PARTIES IDENTIFICATION**:
   - Plaintiff/Appellant: [Full name, capacity, and any relevant details]
   - Defendant/Respondent: [Full name, capacity, and any relevant details]
   - Any other parties involved: [Names, roles, and relationships]
   - Legal representatives: [Lawyers/advocates with their specific roles]
   - Any corporate entities: [Company details if applicable]

2. **DETAILED PLEADINGS BY PLAINTIFF/APPELLANT**:
   - Primary claims: [List ALL claims with specific factual details]
   - Legal grounds: [Specific legal principles, statutes, and constitutional provisions cited]
   - Relief sought: [Exact relief requested with specific amounts if applicable]
   - Evidence presented: [All evidence mentioned with specific details]
   - Arguments made: [Complete arguments including procedural and substantive points]
   - Any counter-arguments to defendant's position: [If any]
   - Specific amounts claimed: [Exact monetary amounts with breakdown if any]
   - Time periods involved: [Any relevant time periods and dates]
   - Contract terms: [If contract dispute, specific terms in issue]
   - Property details: [If property involved, specific property details]

3. **DETAILED PLEADINGS BY DEFENDANT/RESPONDENT**:
   - Primary defenses: [List ALL defenses with specific factual details]
   - Legal grounds: [Specific legal principles, statutes, and constitutional provisions cited]
   - Counter-claims: [If any counter-claims were made with details]
   - Evidence presented: [All evidence mentioned with specific details]
   - Arguments made: [Complete arguments including procedural and substantive points]
   - Any challenges to plaintiff's position: [If any]
   - Specific amounts disputed: [Exact amounts if any]
   - Alternative relief sought: [If any]
   - Contract terms: [If contract dispute, specific terms in issue]
   - Property details: [If property involved, specific property details]

4. **PROCEDURAL PLEADINGS**:
   - Preliminary objections: [Any procedural objections raised with specific grounds]
   - Jurisdictional issues: [If any jurisdiction challenges with legal basis]
   - Admissibility of evidence: [Any evidence admissibility challenges with specific reasons]
   - Service of process: [Any service-related issues with specific details]
   - Time limitations: [Any statute of limitations arguments with specific dates]
   - Venue challenges: [If any venue-related issues]
   - Joinder applications: [If any party joinder issues]
   - Amendment applications: [Any applications to amend pleadings]
   - Discovery issues: [Any discovery-related pleadings]

5. **FACTUAL BACKGROUND AND CONTEXT**:
   - Chronological sequence of events: [Detailed timeline of relevant events]
   - Key factual disputes: [Specific factual issues in contention]
   - Background circumstances: [Context that led to the dispute]
   - Any prior proceedings: [Previous court actions if any]
   - Settlement attempts: [Any settlement negotiations mentioned]
   - Expert opinions: [If any expert evidence or opinions]
   - Witness statements: [Any witness evidence with specific details]

6. **LEGAL CITATIONS AND REFERENCES**:
   - Statutes cited: [All statutory provisions with section numbers]
   - Case law references: [All precedent cases with citations]
   - Constitutional provisions: [If any constitutional issues with specific articles]
   - International law: [If any international law references]
   - Legal principles: [All legal doctrines mentioned]
   - Regulatory provisions: [Any regulations or rules cited]

7. **EVIDENCE AND DOCUMENTATION**:
   - Documentary evidence: [All documents mentioned with specific details]
   - Physical evidence: [Any physical evidence with descriptions]
   - Electronic evidence: [Any digital evidence with details]
   - Expert reports: [Any expert reports with specific findings]
   - Witness statements: [All witness evidence with specific content]
   - Affidavits: [All affidavits mentioned with key points]
   - Exhibits: [All exhibits with specific descriptions]
   - Photographs: [Any photographs with descriptions]
   - Financial records: [Any financial documentation]

8. **SPECIFIC LEGAL ISSUES**:
   - Constitutional issues: [Any constitutional rights or violations alleged]
   - Human rights issues: [Any human rights violations claimed]
   - Administrative law issues: [If administrative action challenged]
   - Contract law issues: [Specific contract terms and breaches]
   - Tort law issues: [Specific tort claims and elements]
   - Property law issues: [Specific property rights and disputes]
   - Employment law issues: [If employment dispute, specific employment terms]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor - accuracy is paramount
- Include specific legal citations and references with exact section numbers
- Preserve exact language where possible, especially for legal terms
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on factual pleadings rather than legal conclusions
- Include all procedural aspects mentioned
- Capture all evidence and documentation referenced
- Pay special attention to amounts, dates, and specific factual details
- Ensure all legal citations are accurate and complete
- Highlight any novel or unusual legal arguments
- Note any procedural irregularities or unusual aspects

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE. BE EXTREMELY THOROUGH AND ACCURATE:
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