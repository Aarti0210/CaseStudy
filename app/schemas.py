from marshmallow import Schema, fields, ValidationError, validates, validates_schema

class ExplainOrderSchema(Schema):
    text = fields.Str(required=True, validate=lambda s: 0 < len(s) <= 2000)
    language = fields.Str(load_default="en", validate=lambda s: len(s) <= 5)

class CaseDataSchema(Schema):
    case_type = fields.Str(required=True)
    number_of_hearings = fields.Int(required=True, validate=lambda n: n >= 0)
    judge_workload = fields.Int(required=True, validate=lambda n: n >= 0)
    document_count = fields.Int(required=True, validate=lambda n: n >= 0)
    case_priority = fields.Str(required=True)
    filing_to_first_hearing_days = fields.Int(required=True, validate=lambda n: n >= 0)
    court_level = fields.Str(required=True)
    previous_adjournments = fields.Int(required=True, validate=lambda n: n >= 0)

class CaseSummarySchema(Schema):
    case_data = fields.Dict(required=True)
    language = fields.Str(load_default="en", validate=lambda s: len(s) <= 5)

class BasicTextSchema(Schema):
    text = fields.Str(required=True, validate=lambda s: 0 < len(s) <= 2000)
    language = fields.Str(load_default="en", validate=lambda s: len(s) <= 5)

class DraftNoticeSchema(Schema):
    client_name = fields.Str(required=True, validate=lambda s: len(s) <= 100)
    case_type = fields.Str(required=True)
    facts = fields.Str(required=True, validate=lambda s: len(s) <= 2000)

class EvidenceSummarySchema(Schema):
    text = fields.Str(required=True, validate=lambda s: 0 < len(s) <= 2000)

class StrategySuggestionSchema(Schema):
    case_summary = fields.Str(required=True, validate=lambda s: len(s) <= 2000)
    opponent_claims = fields.Str(load_default="", validate=lambda s: len(s) <= 2000)

class PredictDelaySchema(Schema):
    case_data = fields.Nested(CaseDataSchema, required=True)

# custom validator decorator

def validate_schema(schema_cls):
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            try:
                data = request.get_json() or {}
            except Exception:
                return jsonify({"success": False, "error": "Invalid JSON"}), 400
            try:
                schema = schema_cls()
                schema.load(data)
            except ValidationError as err:
                return jsonify({"success": False, "error": "validation error", "details": err.messages}), 400
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
