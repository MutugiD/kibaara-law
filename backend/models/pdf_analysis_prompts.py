"""
Templated prompts for detailed PDF analysis of legal documents.

This module contains specialized prompts for extracting detailed information
from Kenyan court case PDFs, focusing on pleadings, trial decisions, and appellate rulings.
"""

from typing import Dict, Any


class PDFAnalysisPrompts:
    """
    Collection of templated prompts for detailed PDF analysis.

    These prompts are designed to extract comprehensive legal information
    from Kenyan court case documents with focus on 2-hop litigation.
    """

    @staticmethod
    def get_pleadings_extraction_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate prompt for extracting detailed pleadings and claims.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for pleadings extraction
        """
        return f"""
You are a legal expert analyzing a Kenyan court case. Please extract ALL pleadings and claims raised by each party in the following case:

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED ANALYSIS:

1. **PARTIES IDENTIFICATION**:
   - Plaintiff/Appellant: [Full name and details]
   - Defendant/Respondent: [Full name and details]
   - Any other parties involved: [Names and roles]

2. **DETAILED PLEADINGS BY PLAINTIFF/APPELLANT**:
   - Primary claims: [List ALL claims with specific details]
   - Legal grounds: [Specific legal principles and statutes cited]
   - Relief sought: [Exact relief requested]
   - Evidence presented: [All evidence mentioned, even minor details]
   - Arguments made: [Complete arguments, including procedural points]
   - Any counter-arguments to defendant's position: [If any]

3. **DETAILED PLEADINGS BY DEFENDANT/RESPONDENT**:
   - Primary defenses: [List ALL defenses with specific details]
   - Legal grounds: [Specific legal principles and statutes cited]
   - Counter-claims: [If any counter-claims were made]
   - Evidence presented: [All evidence mentioned, even minor details]
   - Arguments made: [Complete arguments, including procedural points]
   - Any challenges to plaintiff's position: [If any]

4. **PROCEDURAL PLEADINGS**:
   - Preliminary objections: [Any procedural objections raised]
   - Jurisdictional issues: [If any jurisdiction challenges]
   - Admissibility of evidence: [Any evidence admissibility challenges]
   - Service of process: [Any service-related issues]
   - Time limitations: [Any statute of limitations arguments]

5. **MINOR DETAILS AND NUANCES**:
   - Specific dates mentioned: [All relevant dates]
   - Amounts claimed: [Exact monetary amounts if any]
   - Specific documents referenced: [All documents mentioned]
   - Witness statements: [Any witness evidence]
   - Expert opinions: [If any expert evidence]
   - Any other minor pleadings or claims: [Catch-all for anything missed]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor
- Include specific legal citations and references
- Preserve exact language where possible
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on factual pleadings rather than legal conclusions

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_trial_court_decision_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate prompt for extracting trial court decision details.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for trial court decision extraction
        """
        return f"""
You are a legal expert analyzing a Kenyan trial court decision. Please extract ALL details about the trial court's decision in the following case:

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED ANALYSIS:

1. **TRIAL COURT INFORMATION**:
   - Court name: [Exact court name]
   - Judge(s): [Full names of presiding judge(s)]
   - Case number: [Trial court case number]
   - Date of decision: [Exact date]
   - Location: [Court location if mentioned]

2. **DETAILED FINDINGS OF FACT**:
   - Background facts: [All factual findings, even minor details]
   - Evidence evaluation: [How court evaluated each piece of evidence]
   - Witness credibility: [Any credibility assessments]
   - Documentary evidence: [How documents were treated]
   - Expert evidence: [If any expert evidence was considered]
   - Any factual disputes resolved: [Specific factual determinations]

3. **LEGAL ANALYSIS AND REASONING**:
   - Legal principles applied: [All legal principles cited]
   - Statute interpretation: [How statutes were interpreted]
   - Case law references: [All precedent cases cited]
   - Legal reasoning: [Step-by-step legal analysis]
   - Burden of proof: [How burden was applied]
   - Standard of proof: [Standard applied (balance of probabilities, beyond reasonable doubt, etc.)]

4. **DETAILED DECISION AND ORDERS**:
   - Primary decision: [Main outcome]
   - Specific orders made: [All orders, even minor ones]
   - Relief granted/denied: [Exact relief awarded]
   - Costs awarded: [If any costs were awarded]
   - Time limits: [Any time-related orders]
   - Conditions imposed: [Any conditions attached to orders]

5. **MINOR DETAILS AND PROCEDURAL ASPECTS**:
   - Procedural history: [All procedural steps taken]
   - Adjournments: [Any adjournments and reasons]
   - Applications made: [Any interlocutory applications]
   - Rulings on objections: [How objections were handled]
   - Any procedural irregularities: [If any were noted]
   - Specific dates mentioned: [All relevant dates]
   - Any other minor details: [Catch-all for anything missed]

6. **REASONS FOR DECISION**:
   - Primary reasons: [Main reasons for the decision]
   - Alternative grounds: [If decision could have been based on other grounds]
   - Dissenting opinions: [If any judge disagreed]
   - Concurring opinions: [If any judge agreed for different reasons]
   - Policy considerations: [Any policy reasons mentioned]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor
- Include specific legal citations and references
- Preserve exact language where possible
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on the trial court's reasoning and findings

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_appellate_court_ruling_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate prompt for extracting appellate court ruling details.

        Args:
            case_title: Title of the case
            pdf_content: Content of the PDF document

        Returns:
            Formatted prompt for appellate court ruling extraction
        """
        return f"""
You are a legal expert analyzing a Kenyan appellate court ruling. Please extract ALL details about the appellate court's decision in the following case:

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED ANALYSIS:

1. **APPELLATE COURT INFORMATION**:
   - Court name: [Exact court name (Court of Appeal, Supreme Court, etc.)]
   - Judge(s): [Full names of all appellate judges]
   - Case number: [Appellate court case number]
   - Date of decision: [Exact date]
   - Location: [Court location if mentioned]

2. **GROUNDS OF APPEAL**:
   - Primary grounds: [All grounds of appeal raised]
   - Legal basis for each ground: [Specific legal principles]
   - Arguments presented: [Complete arguments for each ground]
   - Evidence relied upon: [Evidence cited in support]
   - Any new evidence: [If any new evidence was introduced]
   - Procedural grounds: [Any procedural challenges]

3. **APPELLATE COURT'S ANALYSIS**:
   - Standard of review: [Standard applied by appellate court]
   - Deference to trial court: [How much deference given to trial findings]
   - Legal principles applied: [All legal principles cited]
   - Statute interpretation: [How statutes were interpreted]
   - Case law references: [All precedent cases cited]
   - Legal reasoning: [Step-by-step appellate analysis]

4. **DETAILED RULING**:
   - Primary decision: [Main outcome (allowed/dismissed)]
   - Specific orders made: [All orders, even minor ones]
   - Relief granted/denied: [Exact relief awarded]
   - Costs awarded: [If any costs were awarded]
   - Remittal: [If case was remitted to trial court]
   - Conditions imposed: [Any conditions attached to orders]

5. **REASONING AND JUSTIFICATION**:
   - Primary reasons: [Main reasons for the decision]
   - Analysis of trial court decision: [How appellate court viewed trial decision]
   - Errors found: [Any errors identified in trial decision]
   - Correct application of law: [How law should have been applied]
   - Policy considerations: [Any policy reasons mentioned]
   - Precedent setting: [If decision sets new precedent]

6. **MINOR DETAILS AND PROCEDURAL ASPECTS**:
   - Procedural history: [All appellate procedural steps]
   - Applications made: [Any interlocutory applications]
   - Rulings on objections: [How objections were handled]
   - Specific dates mentioned: [All relevant dates]
   - Any procedural irregularities: [If any were noted]
   - Any other minor details: [Catch-all for anything missed]

7. **JUDGMENT STYLE**:
   - Unanimous decision: [If all judges agreed]
   - Majority opinion: [If there was a majority]
   - Dissenting opinions: [If any judge disagreed and why]
   - Concurring opinions: [If any judge agreed for different reasons]
   - Separate judgments: [If judges wrote separate judgments]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor
- Include specific legal citations and references
- Preserve exact language where possible
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on the appellate court's reasoning and how it differed from trial court

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_comprehensive_case_summary_prompt(case_title: str, pleadings_analysis: str,
                                            trial_decision: str, appellate_ruling: str) -> str:
        """
        Generate prompt for creating comprehensive case summary.

        Args:
            case_title: Title of the case
            pleadings_analysis: Analysis of pleadings
            trial_decision: Analysis of trial court decision
            appellate_ruling: Analysis of appellate court ruling

        Returns:
            Formatted prompt for comprehensive case summary
        """
        return f"""
You are a legal expert creating a comprehensive summary of a Kenyan court case with 2-hop litigation. Please create a detailed case summary based on the following analyses:

CASE TITLE: {case_title}

PLEADINGS ANALYSIS:
{pleadings_analysis}

TRIAL COURT DECISION:
{trial_decision}

APPELLATE COURT RULING:
{appellate_ruling}

REQUIRED COMPREHENSIVE SUMMARY:

1. **CASE OVERVIEW**:
   - Full case title and citation
   - Subject matter and legal area
   - Key legal issues involved
   - Significance of the case

2. **PARTIES AND PROCEDURAL HISTORY**:
   - All parties involved with their roles
   - Complete procedural timeline
   - Key procedural events
   - Any procedural irregularities

3. **DETAILED PLEADINGS SUMMARY**:
   - Plaintiff/Appellant's complete claims
   - Defendant/Respondent's complete defenses
   - All legal grounds raised
   - Evidence presented by each party
   - Relief sought by each party

4. **TRIAL COURT DECISION SUMMARY**:
   - Court and judge(s) involved
   - Complete findings of fact
   - Legal analysis and reasoning
   - Specific decision and orders
   - Key legal principles established

5. **APPELLATE COURT RULING SUMMARY**:
   - Court and judge(s) involved
   - Grounds of appeal raised
   - Appellate court's analysis
   - Complete ruling and orders
   - Key legal principles established

6. **LITIGATION PROGRESSION ANALYSIS**:
   - How case progressed from trial to appellate court
   - Key differences between trial and appellate reasoning
   - What changed between the two decisions
   - Procedural lessons learned

7. **LEGAL PRINCIPLES AND PRECEDENT**:
   - Key legal principles established
   - Precedent value of the case
   - Impact on Kenyan jurisprudence
   - Relationship to existing case law

8. **CASE METADATA**:
   - Case numbers (trial and appellate)
   - Decision dates
   - Courts involved
   - Judges involved
   - Legal areas covered
   - Citation information

IMPORTANT INSTRUCTIONS:
- Create a comprehensive, detailed summary
- Include ALL important details from the analyses
- Maintain accuracy and completeness
- Structure the summary logically
- Include specific legal citations and references
- Focus on the 2-hop litigation progression

RESPOND WITH A COMPREHENSIVE STRUCTURED SUMMARY COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_case_metadata_extraction_prompt(case_title: str, comprehensive_summary: str) -> Dict[str, Any]:
        """
        Generate structured metadata from comprehensive case summary.

        Args:
            case_title: Title of the case
            comprehensive_summary: Comprehensive case summary

        Returns:
            Structured metadata dictionary
        """
        return {
            "case_title": case_title,
            "comprehensive_summary": comprehensive_summary,
            "metadata_fields": {
                "trial_court": "Court name and location",
                "appellate_court": "Court name and location",
                "trial_judges": "Names of trial court judges",
                "appellate_judges": "Names of appellate court judges",
                "trial_case_number": "Trial court case number",
                "appellate_case_number": "Appellate court case number",
                "trial_date": "Date of trial court decision",
                "appellate_date": "Date of appellate court decision",
                "legal_area": "Primary legal area (civil, criminal, constitutional, etc.)",
                "subject_matter": "Specific subject matter of the case",
                "key_legal_issues": "Main legal issues involved",
                "trial_outcome": "Outcome at trial court level",
                "appellate_outcome": "Outcome at appellate court level",
                "precedent_value": "Whether case sets new precedent",
                "citation": "Legal citation if available",
                "pdf_files": "List of downloaded PDF files",
                "analysis_complete": True,
                "analysis_timestamp": "Timestamp of analysis"
            }
        }