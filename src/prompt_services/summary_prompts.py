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
You are a senior legal expert specializing in Kenyan law, tasked with creating a comprehensive summary of a Kenyan court case with 2-hop litigation. You must provide extremely detailed, accurate, and relevant analysis that differentiates between trial court and appellate court arguments and rulings.

CASE TITLE: {case_title}

PLEADINGS ANALYSIS:
{pleadings_analysis}

TRIAL COURT DECISION:
{trial_decision}

APPELLATE COURT RULING:
{appellate_ruling}

REQUIRED COMPREHENSIVE SUMMARY IN JSON FORMAT:

You must respond with a JSON object that has the following structure:

{{
  "success": true,
  "case_title": "[Full case title]",
  "analysis_type": "comprehensive_summary",
  "trial_court_ruling": {{
    "court_info": {{
      "court_name": "[Exact court name and location]",
      "judges": "[Full names of presiding judge(s) with titles]",
      "case_number": "[Trial court case number]",
      "decision_date": "[Exact date of trial court decision]"
    }},
    "key_arguments": {{
      "plaintiff_arguments": "[Detailed summary of plaintiff's key arguments]",
      "defendant_arguments": "[Detailed summary of defendant's key arguments]",
      "legal_grounds": "[Specific legal principles and statutes cited]",
      "evidence_presented": "[Key evidence presented by each party]"
    }},
    "findings": {{
      "factual_findings": "[Detailed factual findings with specific details]",
      "legal_findings": "[Legal conclusions reached with reasoning]",
      "evidence_evaluation": "[How court evaluated evidence]",
      "witness_credibility": "[Any credibility assessments]"
    }},
    "decision": {{
      "primary_outcome": "[Main outcome with specific details]",
      "orders_made": "[All specific orders with exact wording]",
      "relief_granted": "[Exact relief awarded with amounts]",
      "costs_awarded": "[If any costs were awarded]",
      "reasoning": "[Detailed reasoning for the decision]"
    }},
    "legal_principles": {{
      "statutes_interpreted": "[How statutes were interpreted]",
      "case_law_applied": "[Precedent cases cited and applied]",
      "new_principles": "[Any new legal principles established]",
      "legal_doctrines": "[Legal doctrines applied]"
    }}
  }},
  "appellate_court_ruling": {{
    "court_info": {{
      "court_name": "[Exact appellate court name]",
      "judges": "[Full names of all appellate judges with titles]",
      "case_number": "[Appellate court case number]",
      "decision_date": "[Exact date of appellate decision]"
    }},
    "grounds_of_appeal": {{
      "primary_grounds": "[All grounds of appeal raised with details]",
      "legal_basis": "[Specific legal principles and statutory provisions]",
      "arguments_presented": "[Complete arguments for each ground]",
      "evidence_relied_upon": "[Evidence cited in support]"
    }},
    "appellate_analysis": {{
      "standard_of_review": "[Standard applied by appellate court]",
      "deference_to_trial": "[How much deference given to trial findings]",
      "legal_reasoning": "[Step-by-step appellate analysis]",
      "constitutional_analysis": "[If any constitutional issues]"
    }},
    "appellate_decision": {{
      "primary_outcome": "[Main outcome (allowed/dismissed) with details]",
      "orders_made": "[All specific orders with exact wording]",
      "relief_granted": "[Exact relief awarded with amounts]",
      "costs_awarded": "[If any costs were awarded]",
      "remittal": "[If case was remitted with directions]"
    }},
    "comparison_with_trial": {{
      "areas_of_agreement": "[Where appellate court agreed with trial court]",
      "areas_of_disagreement": "[Where appellate court disagreed with trial court]",
      "errors_corrected": "[Specific errors identified and corrected]",
      "legal_principles_clarified": "[Any legal principles clarified]",
      "factual_findings_upheld": "[Which factual findings were upheld]",
      "factual_findings_overturned": "[Which factual findings were overturned]",
      "relief_modified": "[How relief was modified from trial court]"
    }},
    "legal_principles": {{
      "new_principles": "[Any new legal principles established]",
      "statutes_interpreted": "[How statutes were interpreted]",
      "precedent_setting": "[If decision sets new precedent]",
      "constitutional_principles": "[Any constitutional principles established]"
    }}
  }},
  "summary": {{
    "case_overview": {{
      "subject_matter": "[Primary subject matter and legal area]",
      "key_legal_issues": "[Main legal issues involved]",
      "significance": "[Significance of the case]",
      "litigation_type": "[Type of litigation (civil, criminal, constitutional)]"
    }},
    "parties_and_procedure": {{
      "parties": "[All parties involved with their roles]",
      "procedural_timeline": "[Complete procedural timeline]",
      "legal_representatives": "[Legal representatives involved]"
    }},
    "factual_background": {{
      "chronological_events": "[Detailed timeline of relevant events]",
      "key_factual_disputes": "[Specific factual issues in contention]",
      "background_circumstances": "[Context that led to the dispute]"
    }},
    "legal_analysis": {{
      "key_legal_principles": "[Key legal principles established]",
      "precedent_value": "[Precedent value of the case]",
      "impact_on_jurisprudence": "[Impact on Kenyan jurisprudence]",
      "novel_interpretations": "[Any novel legal interpretations]"
    }},
    "comparative_analysis": {{
      "alignment_departure": "[Whether rulings in two courts align or depart from each other]",
      "key_differences": "[Key differences between trial and appellate reasoning]",
      "procedural_lessons": "[Procedural lessons learned]",
      "impact_of_appellate": "[Impact of appellate decision on trial decision]"
    }},
    "case_metadata": {{
      "trial_case_number": "[Trial court case number]",
      "appellate_case_number": "[Appellate court case number]",
      "trial_date": "[Date of trial court decision]",
      "appellate_date": "[Date of appellate court decision]",
      "courts_involved": "[All courts involved]",
      "judges_involved": "[All judges involved]",
      "legal_areas": "[Legal areas covered]",
      "citation": "[Legal citation if available]"
    }}
  }},
  "timestamp": "[Current timestamp]"
}}

IMPORTANT INSTRUCTIONS:
- Create a comprehensive, detailed summary that is extremely accurate and relevant
- Include ALL important details from the analyses
- Maintain accuracy and completeness in all sections
- Structure the summary logically with clear differentiation between trial and appellate courts
- Include specific legal citations and references
- Focus on the 2-hop litigation progression
- Highlight key legal developments and differences between courts
- Ensure the JSON structure is valid and complete
- Pay special attention to the comparative analysis section
- Emphasize whether the rulings align or depart from each other
- Provide detailed factual and legal analysis
- Include specific amounts, dates, and factual details
- Ensure all legal citations are accurate and complete

RESPOND WITH A COMPLETE JSON OBJECT FOLLOWING THE EXACT STRUCTURE ABOVE. BE EXTREMELY THOROUGH AND ACCURATE:
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