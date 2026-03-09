def explain_order_prompt(text, language="en"):
    return f"Explain the following court order in {language} in simple terms. Avoid legal jargon. Include important dates and next steps.\n\n{text}"


def case_summary_prompt(case_data, language="en"):
    return f"Provide a concise case summary in {language}. Include parties, key facts, case status, next hearing, and suggested preparations.\n\n{case_data}"


def voice_search_prompt(transcript):
    return f"Convert the following spoken input into a structured case search query:\n\n{transcript}"


def draft_notice_prompt(client_name, case_type, facts, language="en"):
    return f"Draft a formal legal notice in {language} for client {client_name} regarding {case_type}. Include sections: heading, parties, facts, claim, relief sought, and signature. Facts: {facts}"


def evidence_summary_prompt(text, language="en"):
    return f"Summarize the key points, important dates, and timeline from the evidence below in {language}:\n\n{text}"


def strategy_suggestion_prompt(case_summary, opponent_claims, language="en"):
    return f"Provide advisory strategy suggestions (not legal advice) in {language} based on the case summary and opponent claims. Highlight risks and possible arguments.\n\nSummary: {case_summary}\n\nOpponent: {opponent_claims}"


def draft_judgment_prompt(
    case_summary, plaintiff_args, defendant_args, evidence_summary, language="en"
):
    return f"Provide a structured draft judgment in {language} with sections: background, framed issues, analysis structure, suggested reasoning and orders. Do NOT decide final verdict.\n\nCase Summary: {case_summary}\n\nPlaintiff: {plaintiff_args}\n\nDefendant: {defendant_args}\n\nEvidence: {evidence_summary}"


def contradictions_prompt(plaintiff, defendant, language="en"):
    return f"Detect logical contradictions, missing evidence, or inconsistent claims between plaintiff and defendant in {language}.\n\nPlaintiff: {plaintiff}\n\nDefendant: {defendant}"


def timeline_prompt(events, language="en"):
    return f"Generate a chronological timeline from the following events with dates and short descriptions in {language}:\n\n{events}"


def system_summary_prompt(stats, language="en"):
    return f"Provide an executive system analytics summary in {language}: include total cases, delayed cases, judge workload insights, and pending hearings overview. Use data: {stats}"


def delay_prediction_prompt(case_data, language="en"):
    return (
        f"Estimate how long the following case is likely to take from filing to final order in {language}.\n"
        f"Provide risk levels (low/medium/high) and contributing factors.\nCase data:\n{case_data}"
    )


def judicial_intelligence_prompt(case_data, language="en"):
    return (
        f"You are an intelligent judicial assistant. For the case described below, generate a comprehensive report in {language} consisting of:\n"
        f"1. A concise case summary\n"
        f"2. A delay prediction (duration, risk, confidence)\n"
        f"3. Strategic suggestions for parties\n"
        f"4. A simple timeline of key events\n\nCase data:\n{case_data}"
    )
