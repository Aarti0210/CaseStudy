DISCLAIMER = "AI-generated content. Not legal advice."


def standard_response(feature, data):
    return {"success": True, "feature": feature, "data": data, "disclaimer": DISCLAIMER}


def error_response(feature, message, code=400):
    return {
        "success": False,
        "feature": feature,
        "error": message,
        "disclaimer": DISCLAIMER,
        "code": code,
    }
