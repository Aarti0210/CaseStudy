def case_summary_prompt(case_details):
    return f"""
    Summarize the following legal case professionally:

    {case_details}
    """


def legal_risk_prompt(case_details):
    return f"""
    Analyze the following case and give risk assessment:

    {case_details}
    """
