from typing import Dict, List, Any
import numpy as np

# Simple feature engineering helpers. Encoders/mappings saved in metadata.

def build_feature_vector(sample: Dict[str, Any], feature_list: List[str], mappings: Dict[str, Dict[str, int]]):
    """Return feature vector (1D numpy array) for given sample according to feature_list and mappings.

    sample: dictionary with keys like case_type, number_of_hearings, judge_workload, document_count,
            case_priority, filing_to_first_hearing_days, court_level, previous_adjournments
    feature_list: ordered list of features used by model
    mappings: dict mapping categorical fields to integer encodings
    """
    vec = []
    for f in feature_list:
        v = sample.get(f)
        if v is None:
            # missing numeric -> use 0
            vec.append(0.0)
            continue
        # categorical mapping
        if f in mappings:
            m = mappings[f]
            vec.append(float(m.get(str(v), m.get("__default", 0))))
        else:
            # numeric
            try:
                vec.append(float(v))
            except Exception:
                vec.append(0.0)
    return np.array(vec).reshape(1, -1)
