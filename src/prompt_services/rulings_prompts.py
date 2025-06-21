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
You are a senior legal expert specializing in Kenyan law, tasked with extracting comprehensive trial court decision details. Your analysis must be extremely detailed, accurate, and relevant to the specific case at hand.

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED COMPREHENSIVE ANALYSIS:

1. **TRIAL COURT INFORMATION**:
   - Court name: [Exact court name and location]
   - Judge(s): [Full names of presiding judge(s) with titles]
   - Case number: [Trial court case number]
   - Date of decision: [Exact date of judgment/ruling]
   - Location: [Court location if mentioned]
   - Court level: [Magistrate's Court, High Court, etc.]
   - Type of proceeding: [Trial, hearing, application, etc.]

2. **DETAILED FINDINGS OF FACT**:
   - Background facts: [All factual findings, even minor details]
   - Evidence evaluation: [How court evaluated each piece of evidence with specific reasoning]
   - Witness credibility: [Any credibility assessments with specific reasons]
   - Documentary evidence: [How documents were treated and evaluated]
   - Expert evidence: [If any expert evidence was considered and how]
   - Any factual disputes resolved: [Specific factual determinations with reasoning]
   - Key factual findings: [Main factual conclusions with supporting evidence]
   - Contested facts: [Facts that were in dispute and how resolved]
   - Undisputed facts: [Facts that were agreed upon]

3. **LEGAL ANALYSIS AND REASONING**:
   - Legal principles applied: [All legal principles cited with specific applications]
   - Statute interpretation: [How statutes were interpreted with specific sections]
   - Case law references: [All precedent cases cited with specific holdings]
   - Legal reasoning: [Step-by-step legal analysis with logical progression]
   - Burden of proof: [How burden was applied and to which party]
   - Standard of proof: [Standard applied (balance of probabilities, beyond reasonable doubt, etc.)]
   - Legal conclusions: [Main legal conclusions reached with reasoning]
   - Constitutional analysis: [If any constitutional issues were considered]
   - Policy considerations: [Any policy reasons mentioned in the decision]

4. **DETAILED DECISION AND ORDERS**:
   - Primary decision: [Main outcome with specific details]
   - Specific orders made: [All orders, even minor ones, with exact wording]
   - Relief granted/denied: [Exact relief awarded with specific amounts]
   - Costs awarded: [If any costs were awarded with specific amounts]
   - Time limits: [Any time-related orders with specific dates]
   - Conditions imposed: [Any conditions attached to orders]
   - Interest awarded: [If any interest was awarded with rates]
   - Damages: [If any damages were awarded with breakdown]
   - Declaratory relief: [Any declaratory orders made]
   - Injunctive relief: [Any injunctions granted or denied]

5. **PROCEDURAL ASPECTS AND HISTORY**:
   - Procedural history: [All procedural steps taken with dates]
   - Adjournments: [Any adjournments and specific reasons]
   - Applications made: [Any interlocutory applications with outcomes]
   - Rulings on objections: [How objections were handled with specific rulings]
   - Any procedural irregularities: [If any were noted and how addressed]
   - Specific dates mentioned: [All relevant dates throughout proceedings]
   - Evidence rulings: [Any rulings on admissibility of evidence]
   - Amendment applications: [Any applications to amend pleadings]

6. **REASONS FOR DECISION**:
   - Primary reasons: [Main reasons for the decision with detailed explanation]
   - Alternative grounds: [If decision could have been based on other grounds]
   - Dissenting opinions: [If any judge disagreed with specific reasons]
   - Concurring opinions: [If any judge agreed for different reasons]
   - Policy considerations: [Any policy reasons mentioned]
   - Public interest factors: [If any public interest considerations]
   - Legal precedent considerations: [How precedent influenced the decision]
   - Factual basis for each conclusion: [Specific facts supporting each conclusion]

7. **LEGAL PRINCIPLES ESTABLISHED**:
   - New legal principles: [If any new principles established]
   - Interpretation of statutes: [How statutes were interpreted with specific sections]
   - Application of precedent: [How precedent cases were applied or distinguished]
   - Legal doctrines applied: [Any legal doctrines used with specific applications]
   - Constitutional principles: [If any constitutional principles were applied]
   - Common law principles: [Any common law principles applied]

8. **SPECIFIC LEGAL ISSUES ADDRESSED**:
   - Contract law issues: [If contract dispute, specific contract law principles]
   - Tort law issues: [If tort claim, specific tort elements and analysis]
   - Property law issues: [If property dispute, specific property law principles]
   - Constitutional issues: [If constitutional issues, specific constitutional analysis]
   - Administrative law issues: [If administrative action, specific administrative law]
   - Employment law issues: [If employment dispute, specific employment law]
   - Family law issues: [If family dispute, specific family law principles]

9. **EVIDENCE ANALYSIS**:
   - Documentary evidence: [How each document was evaluated]
   - Witness evidence: [How each witness was assessed]
   - Expert evidence: [How expert evidence was treated]
   - Physical evidence: [How physical evidence was evaluated]
   - Electronic evidence: [How electronic evidence was handled]
   - Circumstantial evidence: [How circumstantial evidence was weighed]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor - accuracy is paramount
- Include specific legal citations and references with exact section numbers
- Preserve exact language where possible, especially for legal terms and orders
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on the trial court's reasoning and findings
- Include all procedural aspects and orders
- Pay special attention to amounts, dates, and specific factual details
- Ensure all legal citations are accurate and complete
- Highlight any novel or unusual legal reasoning
- Note any procedural irregularities or unusual aspects
- Provide specific factual basis for each legal conclusion

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE. BE EXTREMELY THOROUGH AND ACCURATE:
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
You are a senior legal expert specializing in Kenyan law, tasked with extracting comprehensive appellate court ruling details. Your analysis must be extremely detailed, accurate, and relevant to the specific case at hand.

CASE TITLE: {case_title}

PDF CONTENT:
{pdf_content[:8000]}  # Limit content length for API

REQUIRED COMPREHENSIVE ANALYSIS:

1. **APPELLATE COURT INFORMATION**:
   - Court name: [Exact court name (Court of Appeal, Supreme Court, etc.)]
   - Judge(s): [Full names of all appellate judges with titles]
   - Case number: [Appellate court case number]
   - Date of decision: [Exact date of appellate decision]
   - Location: [Court location if mentioned]
   - Court level: [Appellate court level]
   - Type of appeal: [Civil appeal, criminal appeal, constitutional petition, etc.]

2. **GROUNDS OF APPEAL**:
   - Primary grounds: [All grounds of appeal raised with specific details]
   - Legal basis for each ground: [Specific legal principles and statutory provisions]
   - Arguments presented: [Complete arguments for each ground with specific reasoning]
   - Evidence relied upon: [Evidence cited in support of each ground]
   - Any new evidence: [If any new evidence was introduced with details]
   - Procedural grounds: [Any procedural challenges with specific allegations]
   - Constitutional grounds: [If any constitutional issues with specific articles]
   - Factual grounds: [Any challenges to factual findings]
   - Legal grounds: [Any challenges to legal conclusions]

3. **APPELLATE COURT'S ANALYSIS**:
   - Standard of review: [Standard applied by appellate court with specific details]
   - Deference to trial court: [How much deference given to trial findings with reasoning]
   - Legal principles applied: [All legal principles cited with specific applications]
   - Statute interpretation: [How statutes were interpreted with specific sections]
   - Case law references: [All precedent cases cited with specific holdings]
   - Legal reasoning: [Step-by-step appellate analysis with logical progression]
   - Constitutional analysis: [If any constitutional issues with specific analysis]
   - Policy considerations: [Any policy reasons mentioned in appellate decision]
   - Public interest factors: [If any public interest considerations]

4. **DETAILED RULING**:
   - Primary decision: [Main outcome (allowed/dismissed) with specific details]
   - Specific orders made: [All orders, even minor ones, with exact wording]
   - Relief granted/denied: [Exact relief awarded with specific amounts]
   - Costs awarded: [If any costs were awarded with specific amounts]
   - Remittal: [If case was remitted to trial court with specific directions]
   - Conditions imposed: [Any conditions attached to orders]
   - Interest awarded: [If any interest was awarded with rates]
   - Damages: [If any damages were awarded with breakdown]
   - Declaratory relief: [Any declaratory orders made]
   - Injunctive relief: [Any injunctions granted or denied]

5. **REASONING AND JUSTIFICATION**:
   - Primary reasons: [Main reasons for the decision with detailed explanation]
   - Analysis of trial court decision: [How appellate court viewed trial decision]
   - Errors found: [Any errors identified in trial decision with specific details]
   - Correct application of law: [How law should have been applied with specific reasoning]
   - Policy considerations: [Any policy reasons mentioned]
   - Precedent setting: [If decision sets new precedent with specific details]
   - Public interest factors: [If any public interest considerations]
   - Factual basis for appellate conclusions: [Specific facts supporting appellate conclusions]
   - Legal precedent considerations: [How precedent influenced appellate decision]

6. **COMPARISON WITH TRIAL COURT DECISION**:
   - Areas of agreement: [Where appellate court agreed with trial court]
   - Areas of disagreement: [Where appellate court disagreed with trial court]
   - Specific errors corrected: [Specific errors identified and corrected]
   - Legal principles clarified: [Any legal principles clarified or corrected]
   - Factual findings upheld: [Which factual findings were upheld]
   - Factual findings overturned: [Which factual findings were overturned]
   - Relief modified: [How relief was modified from trial court]

7. **PROCEDURAL ASPECTS**:
   - Procedural history: [All appellate procedural steps with dates]
   - Applications made: [Any interlocutory applications with outcomes]
   - Rulings on objections: [How objections were handled with specific rulings]
   - Specific dates mentioned: [All relevant dates throughout appellate proceedings]
   - Any procedural irregularities: [If any were noted and how addressed]
   - Evidence rulings: [Any rulings on admissibility of evidence on appeal]
   - Amendment applications: [Any applications to amend grounds of appeal]

8. **JUDGMENT STYLE**:
   - Unanimous decision: [If all judges agreed with specific details]
   - Majority opinion: [If there was a majority with specific details]
   - Dissenting opinions: [If any judge disagreed with specific reasons]
   - Concurring opinions: [If any judge agreed for different reasons]
   - Separate judgments: [If judges wrote separate judgments with details]
   - Lead judgment: [Who wrote the lead judgment with specific details]
   - Ratio decidendi: [The main legal principle established]

9. **LEGAL PRINCIPLES ESTABLISHED**:
   - New legal principles: [If any new principles established with specific details]
   - Interpretation of statutes: [How statutes were interpreted with specific sections]
   - Application of precedent: [How precedent cases were applied or distinguished]
   - Legal doctrines applied: [Any legal doctrines used with specific applications]
   - Constitutional principles: [If any constitutional principles established]
   - Common law principles: [Any common law principles applied or developed]

10. **SPECIFIC LEGAL ISSUES ADDRESSED**:
    - Contract law issues: [If contract dispute, specific contract law principles]
    - Tort law issues: [If tort claim, specific tort elements and analysis]
    - Property law issues: [If property dispute, specific property law principles]
    - Constitutional issues: [If constitutional issues, specific constitutional analysis]
    - Administrative law issues: [If administrative action, specific administrative law]
    - Employment law issues: [If employment dispute, specific employment law]
    - Family law issues: [If family dispute, specific family law principles]

11. **EVIDENCE ANALYSIS ON APPEAL**:
    - Documentary evidence: [How documentary evidence was evaluated on appeal]
    - Witness evidence: [How witness evidence was assessed on appeal]
    - Expert evidence: [How expert evidence was treated on appeal]
    - Physical evidence: [How physical evidence was evaluated on appeal]
    - Electronic evidence: [How electronic evidence was handled on appeal]
    - Circumstantial evidence: [How circumstantial evidence was weighed on appeal]

IMPORTANT INSTRUCTIONS:
- Extract EVERY detail, no matter how minor - accuracy is paramount
- Include specific legal citations and references with exact section numbers
- Preserve exact language where possible, especially for legal terms and orders
- Do not summarize - provide comprehensive details
- If information is not available, state "Not mentioned in document"
- Focus on the appellate court's reasoning and findings
- Include all procedural aspects and orders
- Pay special attention to amounts, dates, and specific factual details
- Ensure all legal citations are accurate and complete
- Highlight any novel or unusual legal reasoning
- Note any procedural irregularities or unusual aspects
- Provide specific factual basis for each legal conclusion
- Emphasize the appellate court's analysis of the trial court decision
- Highlight any new legal principles established

RESPOND WITH A DETAILED STRUCTURED ANALYSIS COVERING ALL SECTIONS ABOVE. BE EXTREMELY THOROUGH AND ACCURATE:
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