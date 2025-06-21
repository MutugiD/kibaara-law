"""
Summary Prompts Service

This module contains specialized prompts for creating comprehensive case summaries
and extracting structured metadata from legal documents.
"""

from typing import Dict, Any


class SummaryPrompts:
    """
    Service for generating prompts to create comprehensive case summaries and metadata.

    This service provides templated prompts focused on creating structured summaries
    and extracting metadata from legal analysis results.
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
   - Type of litigation (civil, criminal, constitutional, etc.)

2. **PARTIES AND PROCEDURAL HISTORY**:
   - All parties involved with their roles
   - Complete procedural timeline
   - Key procedural events
   - Any procedural irregularities
   - Legal representatives involved

3. **DETAILED PLEADINGS SUMMARY**:
   - Plaintiff/Appellant's complete claims
   - Defendant/Respondent's complete defenses
   - All legal grounds raised
   - Evidence presented by each party
   - Relief sought by each party
   - Key arguments made by each side

4. **TRIAL COURT DECISION SUMMARY**:
   - Court and judge(s) involved
   - Complete findings of fact
   - Legal analysis and reasoning
   - Specific decision and orders
   - Key legal principles established
   - Relief granted or denied

5. **APPELLATE COURT RULING SUMMARY**:
   - Court and judge(s) involved
   - Grounds of appeal raised
   - Appellate court's analysis
   - Complete ruling and orders
   - Key legal principles established
   - Relief granted or denied on appeal

6. **LITIGATION PROGRESSION ANALYSIS**:
   - How case progressed from trial to appellate court
   - Key differences between trial and appellate reasoning
   - What changed between the two decisions
   - Procedural lessons learned
   - Impact of appellate decision on trial decision

7. **LEGAL PRINCIPLES AND PRECEDENT**:
   - Key legal principles established
   - Precedent value of the case
   - Impact on Kenyan jurisprudence
   - Relationship to existing case law
   - Novel legal interpretations

8. **CASE METADATA**:
   - Case numbers (trial and appellate)
   - Decision dates
   - Courts involved
   - Judges involved
   - Legal areas covered
   - Citation information
   - File references

IMPORTANT INSTRUCTIONS:
- Create a comprehensive, detailed summary
- Include ALL important details from the analyses
- Maintain accuracy and completeness
- Structure the summary logically
- Include specific legal citations and references
- Focus on the 2-hop litigation progression
- Highlight key legal developments

RESPOND WITH A COMPREHENSIVE STRUCTURED SUMMARY COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_case_metadata_extraction_prompt(case_title: str, comprehensive_summary: str) -> str:
        """
        Generate prompt for extracting structured metadata from case summary.

        Args:
            case_title: Title of the case
            comprehensive_summary: Comprehensive case summary

        Returns:
            Formatted prompt for metadata extraction
        """
        return f"""
You are a legal expert extracting structured metadata from a comprehensive case summary.

CASE TITLE: {case_title}

COMPREHENSIVE SUMMARY:
{comprehensive_summary}

REQUIRED METADATA EXTRACTION:

Please extract the following structured metadata in JSON format:

1. **BASIC CASE INFORMATION**:
   - case_title: [Full case title]
   - citation: [Legal citation if available]
   - subject_matter: [Primary subject matter]
   - legal_area: [Primary legal area (civil, criminal, constitutional, etc.)]
   - case_type: [Type of case (appeal, judicial review, etc.)]

2. **COURT INFORMATION**:
   - trial_court: [Trial court name and location]
   - appellate_court: [Appellate court name and location]
   - trial_judges: [Names of trial court judges]
   - appellate_judges: [Names of appellate court judges]

3. **CASE NUMBERS AND DATES**:
   - trial_case_number: [Trial court case number]
   - appellate_case_number: [Appellate court case number]
   - trial_date: [Date of trial court decision]
   - appellate_date: [Date of appellate court decision]
   - filing_date: [Date case was filed if mentioned]

4. **PARTIES**:
   - plaintiff_appellant: [Name of plaintiff/appellant]
   - defendant_respondent: [Name of defendant/respondent]
   - other_parties: [Any other parties involved]

5. **LEGAL ISSUES**:
   - key_legal_issues: [Main legal issues involved]
   - grounds_of_appeal: [Grounds of appeal raised]
   - constitutional_issues: [Any constitutional issues]

6. **OUTCOMES**:
   - trial_outcome: [Outcome at trial court level]
   - appellate_outcome: [Outcome at appellate court level]
   - relief_granted: [Relief granted at each level]
   - costs_awarded: [Costs awarded if any]

7. **LEGAL PRINCIPLES**:
   - legal_principles_established: [Key legal principles established]
   - precedent_value: [Whether case sets new precedent]
   - statutes_interpreted: [Statutes interpreted]
   - case_law_cited: [Important case law cited]

8. **PROCEDURAL ASPECTS**:
   - procedural_history: [Key procedural events]
   - procedural_irregularities: [Any procedural irregularities]
   - applications_made: [Key applications made]

9. **EVIDENCE AND DOCUMENTATION**:
   - key_evidence: [Key evidence presented]
   - expert_evidence: [Any expert evidence]
   - documents_referenced: [Key documents referenced]

10. **ANALYSIS INFORMATION**:
    - analysis_complete: true
    - analysis_timestamp: [Current timestamp]
    - pdf_files: [List of related PDF files]
    - analysis_quality: [Quality assessment of analysis]

IMPORTANT INSTRUCTIONS:
- Extract all available information from the summary
- Use "Not mentioned" for missing information
- Maintain accuracy and completeness
- Structure the metadata logically
- Include all relevant details

RESPOND WITH STRUCTURED JSON METADATA:
"""

    @staticmethod
    def get_case_comparison_prompt(case1_summary: str, case2_summary: str) -> str:
        """
        Generate prompt for comparing two cases.

        Args:
            case1_summary: Summary of first case
            case2_summary: Summary of second case

        Returns:
            Formatted prompt for case comparison
        """
        return f"""
You are a legal expert comparing two Kenyan court cases.

CASE 1 SUMMARY:
{case1_summary}

CASE 2 SUMMARY:
{case2_summary}

REQUIRED COMPARISON ANALYSIS:

1. **SIMILARITIES**:
   - Legal issues: [Similar legal issues]
   - Procedural aspects: [Similar procedural elements]
   - Legal principles: [Similar legal principles applied]
   - Outcomes: [Similar outcomes if any]

2. **DIFFERENCES**:
   - Legal issues: [Different legal issues]
   - Procedural aspects: [Different procedural elements]
   - Legal principles: [Different legal principles applied]
   - Outcomes: [Different outcomes]

3. **LEGAL DEVELOPMENT**:
   - How cases relate: [How cases relate to each other]
   - Legal progression: [Legal development between cases]
   - Precedent relationship: [Precedent relationship if any]

4. **PRACTICAL IMPLICATIONS**:
   - Impact on practice: [Impact on legal practice]
   - Lessons learned: [Key lessons from comparison]
   - Future implications: [Future implications]

RESPOND WITH DETAILED COMPARISON ANALYSIS:
"""

    @staticmethod
    def get_legal_trends_prompt(case_summaries: str) -> str:
        """
        Generate prompt for analyzing legal trends across multiple cases.

        Args:
            case_summaries: Summaries of multiple cases

        Returns:
            Formatted prompt for trend analysis
        """
        return f"""
You are a legal expert analyzing trends across multiple Kenyan court cases.

CASE SUMMARIES:
{case_summaries}

REQUIRED TREND ANALYSIS:

1. **LEGAL TRENDS**:
   - Common legal issues: [Most common legal issues]
   - Emerging principles: [New legal principles emerging]
   - Statutory interpretations: [Trends in statutory interpretation]
   - Procedural developments: [Procedural trends]

2. **JUDICIAL APPROACHES**:
   - Judicial reasoning: [Trends in judicial reasoning]
   - Standard of review: [Trends in standard of review]
   - Deference patterns: [Patterns in judicial deference]
   - Policy considerations: [Policy considerations trends]

3. **PRACTICAL IMPLICATIONS**:
   - Impact on litigation: [Impact on future litigation]
   - Practice recommendations: [Recommendations for practice]
   - Risk assessment: [Risk assessment for similar cases]

4. **FUTURE DEVELOPMENTS**:
   - Predicted trends: [Predicted future trends]
   - Areas of concern: [Areas requiring attention]
   - Recommendations: [Recommendations for stakeholders]

RESPOND WITH DETAILED TREND ANALYSIS:
"""