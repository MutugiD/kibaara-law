"""
Rulings Prompts Service

This module contains specialized prompts for extracting detailed trial court decisions
and appellate court rulings from Kenyan court case documents.
"""

from typing import Dict, Any


class RulingsPrompts:
    """
    Service for generating prompts to extract detailed court rulings and decisions.

    This service provides templated prompts focused on extracting comprehensive
    information about trial court decisions and appellate court rulings.
    """

    @staticmethod
    def get_trial_court_decision_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate comprehensive prompt for extracting trial court decision details.

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

REQUIRED COMPREHENSIVE ANALYSIS:

1. **TRIAL COURT INFORMATION**:
   - Court name: [Exact court name]
   - Judge(s): [Full names of presiding judge(s)]
   - Case number: [Trial court case number]
   - Date of decision: [Exact date]
   - Location: [Court location if mentioned]
   - Court level: [Magistrate's Court, High Court, etc.]

2. **DETAILED FINDINGS OF FACT**:
   - Background facts: [All factual findings, even minor details]
   - Evidence evaluation: [How court evaluated each piece of evidence]
   - Witness credibility: [Any credibility assessments]
   - Documentary evidence: [How documents were treated]
   - Expert evidence: [If any expert evidence was considered]
   - Any factual disputes resolved: [Specific factual determinations]
   - Key factual findings: [Main factual conclusions]

3. **LEGAL ANALYSIS AND REASONING**:
   - Legal principles applied: [All legal principles cited]
   - Statute interpretation: [How statutes were interpreted]
   - Case law references: [All precedent cases cited]
   - Legal reasoning: [Step-by-step legal analysis]
   - Burden of proof: [How burden was applied]
   - Standard of proof: [Standard applied (balance of probabilities, beyond reasonable doubt, etc.)]
   - Legal conclusions: [Main legal conclusions reached]

4. **DETAILED DECISION AND ORDERS**:
   - Primary decision: [Main outcome]
   - Specific orders made: [All orders, even minor ones]
   - Relief granted/denied: [Exact relief awarded]
   - Costs awarded: [If any costs were awarded]
   - Time limits: [Any time-related orders]
   - Conditions imposed: [Any conditions attached to orders]
   - Interest awarded: [If any interest was awarded]
   - Damages: [If any damages were awarded]

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
   - Public interest factors: [If any public interest considerations]

7. **LEGAL PRINCIPLES ESTABLISHED**:
   - New legal principles: [If any new principles established]
   - Interpretation of statutes: [How statutes were interpreted]
   - Application of precedent: [How precedent cases were applied]
   - Legal doctrines applied: [Any legal doctrines used]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor
- Include specific legal citations and references
- Preserve exact language where possible
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on the trial court's reasoning and findings
- Include all procedural aspects and orders

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_appellate_court_ruling_prompt(case_title: str, pdf_content: str) -> str:
        """
        Generate comprehensive prompt for extracting appellate court ruling details.

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

REQUIRED COMPREHENSIVE ANALYSIS:

1. **APPELLATE COURT INFORMATION**:
   - Court name: [Exact court name (Court of Appeal, Supreme Court, etc.)]
   - Judge(s): [Full names of all appellate judges]
   - Case number: [Appellate court case number]
   - Date of decision: [Exact date]
   - Location: [Court location if mentioned]
   - Court level: [Appellate court level]

2. **GROUNDS OF APPEAL**:
   - Primary grounds: [All grounds of appeal raised]
   - Legal basis for each ground: [Specific legal principles]
   - Arguments presented: [Complete arguments for each ground]
   - Evidence relied upon: [Evidence cited in support]
   - Any new evidence: [If any new evidence was introduced]
   - Procedural grounds: [Any procedural challenges]
   - Constitutional grounds: [If any constitutional issues]

3. **APPELLATE COURT'S ANALYSIS**:
   - Standard of review: [Standard applied by appellate court]
   - Deference to trial court: [How much deference given to trial findings]
   - Legal principles applied: [All legal principles cited]
   - Statute interpretation: [How statutes were interpreted]
   - Case law references: [All precedent cases cited]
   - Legal reasoning: [Step-by-step appellate analysis]
   - Constitutional analysis: [If any constitutional issues]

4. **DETAILED RULING**:
   - Primary decision: [Main outcome (allowed/dismissed)]
   - Specific orders made: [All orders, even minor ones]
   - Relief granted/denied: [Exact relief awarded]
   - Costs awarded: [If any costs were awarded]
   - Remittal: [If case was remitted to trial court]
   - Conditions imposed: [Any conditions attached to orders]
   - Interest awarded: [If any interest was awarded]
   - Damages: [If any damages were awarded]

5. **REASONING AND JUSTIFICATION**:
   - Primary reasons: [Main reasons for the decision]
   - Analysis of trial court decision: [How appellate court viewed trial decision]
   - Errors found: [Any errors identified in trial decision]
   - Correct application of law: [How law should have been applied]
   - Policy considerations: [Any policy reasons mentioned]
   - Precedent setting: [If decision sets new precedent]
   - Public interest factors: [If any public interest considerations]

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
   - Lead judgment: [Who wrote the lead judgment]

8. **LEGAL PRINCIPLES ESTABLISHED**:
   - New legal principles: [If any new principles established]
   - Interpretation of statutes: [How statutes were interpreted]
   - Application of precedent: [How precedent cases were applied]
   - Legal doctrines applied: [Any legal doctrines used]
   - Constitutional principles: [If any constitutional principles established]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor
- Include specific legal citations and references
- Preserve exact language where possible
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on the appellate court's reasoning and how it differed from trial court
- Include all procedural aspects and orders

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE:
"""

    @staticmethod
    def get_decision_summary_prompt(case_title: str, trial_decision: str, appellate_ruling: str) -> str:
        """
        Generate prompt for creating a summary comparing trial and appellate decisions.

        Args:
            case_title: Title of the case
            trial_decision: Analysis of trial court decision
            appellate_ruling: Analysis of appellate court ruling

        Returns:
            Formatted prompt for decision comparison
        """
        return f"""
You are a legal expert creating a comprehensive comparison of trial and appellate court decisions.

CASE TITLE: {case_title}

TRIAL COURT DECISION:
{trial_decision}

APPELLATE COURT RULING:
{appellate_ruling}

REQUIRED COMPARISON ANALYSIS:

1. **DECISION COMPARISON**:
   - Trial court outcome: [What trial court decided]
   - Appellate court outcome: [What appellate court decided]
   - Key differences: [Main differences between decisions]
   - What changed: [What specifically changed on appeal]

2. **REASONING COMPARISON**:
   - Trial court reasoning: [Main reasoning of trial court]
   - Appellate court reasoning: [Main reasoning of appellate court]
   - Legal analysis differences: [How legal analysis differed]
   - Factual findings: [How factual findings were treated]

3. **RELIEF COMPARISON**:
   - Trial court relief: [Relief granted by trial court]
   - Appellate court relief: [Relief granted by appellate court]
   - Changes in relief: [How relief changed on appeal]
   - Costs comparison: [How costs were treated]

4. **LEGAL PRINCIPLES**:
   - Trial court principles: [Legal principles applied by trial court]
   - Appellate court principles: [Legal principles applied by appellate court]
   - New principles established: [Any new principles on appeal]
   - Precedent value: [Precedent value of appellate decision]

5. **PROCEDURAL ASPECTS**:
   - Trial court procedure: [Procedural aspects at trial]
   - Appellate procedure: [Procedural aspects on appeal]
   - Procedural lessons: [Procedural lessons learned]

RESPOND WITH DETAILED COMPARISON ANALYSIS:
"""

    @staticmethod
    def get_legal_principles_prompt(case_title: str, trial_decision: str, appellate_ruling: str) -> str:
        """
        Generate prompt for extracting legal principles from both decisions.

        Args:
            case_title: Title of the case
            trial_decision: Analysis of trial court decision
            appellate_ruling: Analysis of appellate court ruling

        Returns:
            Formatted prompt for legal principles extraction
        """
        return f"""
You are a legal expert extracting legal principles from trial and appellate court decisions.

CASE TITLE: {case_title}

TRIAL COURT DECISION:
{trial_decision}

APPELLATE COURT RULING:
{appellate_ruling}

REQUIRED LEGAL PRINCIPLES ANALYSIS:

1. **TRIAL COURT LEGAL PRINCIPLES**:
   - Statutes interpreted: [All statutes interpreted]
   - Case law applied: [All precedent cases applied]
   - Legal doctrines used: [All legal doctrines applied]
   - Legal reasoning: [Legal reasoning employed]

2. **APPELLATE COURT LEGAL PRINCIPLES**:
   - Statutes interpreted: [All statutes interpreted]
   - Case law applied: [All precedent cases applied]
   - Legal doctrines used: [All legal doctrines applied]
   - Legal reasoning: [Legal reasoning employed]

3. **NEW LEGAL PRINCIPLES ESTABLISHED**:
   - Novel interpretations: [Any novel statutory interpretations]
   - New precedent: [If new precedent established]
   - Legal developments: [Any legal developments]
   - Constitutional principles: [If any constitutional principles]

4. **PRECEDENT VALUE**:
   - Binding precedent: [If decision creates binding precedent]
   - Persuasive value: [Persuasive value of decision]
   - Impact on jurisprudence: [Impact on Kenyan jurisprudence]
   - Future application: [How decision may be applied in future]

RESPOND WITH DETAILED LEGAL PRINCIPLES ANALYSIS:
"""