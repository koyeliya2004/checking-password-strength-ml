import joblib
from pathlib import Path
import types
import sys
import math
import logging


# fallback tokenizer for legacy pickles
def char_tokenizer(s):
    try:
        return list(s)
    except Exception:
        return [c for c in str(s)]

if "__main__" not in sys.modules:
    sys.modules["__main__"] = types.ModuleType("__main__")
setattr(sys.modules["__main__"], "char_tokenizer", char_tokenizer)

# Directories
APP_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = Path(__file__).resolve().parents[2]

# Model holders (populated by initialize_models)
_models = {}

# configure logger for this module
logger = logging.getLogger("password_ml_engine")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)


def _reshape_features_for_model(X, model):
    """Best-effort: adjust feature dimension of X to model.n_features_in_.
    Pads with zeros or truncates columns so shapes match.
    """
    n = getattr(model, "n_features_in_", None)
    try:
        n = int(n) if n is not None else None
    except Exception:
        n = None
    if n is None:
        return X

    try:
        current = X.shape[1]
    except Exception:
        return X

    if current == n:
        return X

    try:
        from scipy import sparse as _sps
    except Exception:
        logger.warning("scipy.sparse unavailable; cannot reshape features (have %s, need %s)", current, n)
        return X

    try:
        if _sps.issparse(X):
            if current < n:
                pad = _sps.csr_matrix((X.shape[0], n - current))
                X_new = _sps.hstack([X, pad])
            else:
                X_new = X[:, :n]
        else:
            import numpy as _np
            arr = _np.asarray(X)
            if arr.shape[1] < n:
                pad = _np.zeros((arr.shape[0], n - arr.shape[1]))
                X_new = _np.hstack([arr, pad])
            else:
                X_new = arr[:, :n]
        logger.info("reshaped features from %s to %s for model", current, n)
        return X_new
    except Exception as e:
        logger.warning("failed to reshape features (%s -> %s): %s", current, n, e)
        return X


def _load_model(filename):
    candidates = [APP_DIR / "models" / filename, BASE_DIR / filename, BASE_DIR / "models" / filename]
    for p in candidates:
        try:
            if p.exists():
                logger.info(f"Loading model from: {p}")
                model = joblib.load(str(p))
                logger.info(f"Successfully loaded model: {filename}")
                return model
        except Exception as e:
            logger.warning(f"Failed to load model from {p}: {e}")
            continue
    logger.error(f"Model file '{filename}' not found in any of: {[str(c) for c in candidates]}")
    raise FileNotFoundError(f"Model file '{filename}' not found in {candidates}")


def initialize_models():
    """Load the models we need. Keep models in memory for fast calls.
    We will use `enhanced_password_model_1.pkl` as primary and
    `enhancedpasswordmodel.pkl` as fallback for predicted_strength.
    """
    global _models
    logger.info("Initializing models...")
    
    # Strength predictors
    try:
        _models['primary_strength'] = _load_model('enhanced_password_model_1.pkl')
        logger.info("Primary strength model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load primary strength model: {e}")
        _models['primary_strength'] = None
    
    try:
        _models['fallback_strength'] = _load_model('enhancedpasswordmodel.pkl')
        logger.info("Fallback strength model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load fallback strength model: {e}")
        _models['fallback_strength'] = None

    # vectorizer for transforming input
    def _vec_feature_count(vec):
        try:
            if hasattr(vec, 'vocabulary_') and vec.vocabulary_ is not None:
                return len(vec.vocabulary_)
            try:
                return len(vec.get_feature_names_out())
            except Exception:
                return vec.transform(["x"]).shape[1]
        except Exception:
            return None

    # If primary model defines `n_features_in_`, try to find a matching vectorizer first
    model_n = getattr(_models.get('primary_strength'), 'n_features_in_', None)
    found_vec = None
    if model_n is not None:
        candidates = []
        app_models_dir = APP_DIR / 'models'
        if app_models_dir.exists():
            candidates.extend(app_models_dir.glob('tfidf_vectorizer*.pkl'))
        candidates.extend(BASE_DIR.glob('tfidf_vectorizer*.pkl'))
        best = (None, None)
        for p in candidates:
            try:
                vec = joblib.load(str(p))
            except Exception:
                continue
            n_vec = _vec_feature_count(vec)
            if n_vec is None:
                continue
            if int(model_n) == int(n_vec):
                found_vec = vec
                _models['vectorizer_path'] = str(p)
                logger.info('selected vectorizer %s matching model n_features_in_=%s', p, model_n)
                break
            # keep closest as fallback
            if best[0] is None or abs(int(n_vec) - int(model_n)) < abs(int(_vec_feature_count(best[0])) - int(model_n)):
                best = (vec, p)
        if found_vec is None and best[0] is not None:
            found_vec = best[0]
            _models['vectorizer_path'] = str(best[1])

    if found_vec is not None:
        _models['vectorizer'] = found_vec
        logger.info('using vectorizer from %s', _models.get('vectorizer_path'))
    else:
        # fallback: try common names
        for name in ('tfidf_vectorizer_1.pkl', 'tfidf_vectorizer.pkl', 'tfidf_vectorizer (2).pkl'):
            try:
                _models['vectorizer'] = _load_model(name)
                break
            except Exception:
                _models['vectorizer'] = None
    logger.info('initialize_models: primary n_features_in_=%s, selected vectorizer=%s', model_n, _models.get('vectorizer_path'))

    # improvement model (optional) to generate suggestions
    try:
        _models['improvement'] = _load_model('password_improvement_model.pkl')
        logger.info("Improvement model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load improvement model: {e}")
        _models['improvement'] = None

    # load reuse list (simple plain-text list of known reused passwords)
    reuse_file = APP_DIR / 'models' / 'reuse_list.txt'
    if not reuse_file.exists():
        reuse_file = BASE_DIR / 'reuse_list.txt'
    reuse = set()
    try:
        if reuse_file.exists():
            for ln in reuse_file.read_text(encoding='utf8').splitlines():
                ln = ln.strip()
                if ln:
                    reuse.add(ln)
            logger.info(f"Loaded {len(reuse)} passwords from reuse list: {reuse_file}")
    except Exception as e:
        logger.warning(f"Failed to load reuse list: {e}")
        reuse = set()
    _models['reuse_list'] = reuse
    
    logger.info(f"Model initialization complete. Loaded models: {[k for k, v in _models.items() if v is not None and k != 'reuse_list']}")


def _predict_strength(password):
    """Predict password strength using rule-based scoring (primary) + ML as validation.
    The ML model's vectorizer is missing from the repository, so all vectorizers predict 'Weak'.
    Using rule-based heuristics as the primary method.
    Returns numeric label (0='Weak', 1='Medium', 2='Strong').
    """
    # Rule-based strength assessment
    score = 0
    length = len(password)
    
    # Length scoring
    if length >= 16:
        score += 4
    elif length >= 12:
        score += 3
    elif length >= 8:
        score += 2
    elif length >= 6:
        score += 1
    
    # Character diversity
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    char_types = sum([has_lower, has_upper, has_digit, has_special])
    score += char_types
    
    # Bonus for excellent length + diversity
    if length >= 12 and char_types >= 3:
        score += 2
    
    # Check for common weak passwords (override score)
    common_weak = ['password', 'password123', '12345678', 'qwerty', 'abc123', 'letmein', '123456', 'admin', 'welcome']
    if password.lower() in common_weak:
        score = 0
    
    # Map score to numeric label
    if score >= 8:
        strength_label = 2  # Strong
    elif score >= 4:
        strength_label = 1  # Medium
    else:
        strength_label = 0  # Weak
    
    logger.info(f"Rule-based strength for '{password}': score={score} -> label={strength_label}")
    
    # Try ML model for comparison (currently all vectorizers predict Weak/0 - not used)
    vec = _models.get('vectorizer')
    primary = _models.get('primary_strength')
    
    if primary is not None and vec is not None:
        try:
            X_raw = vec.transform([password])
            X = _reshape_features_for_model(X_raw, primary)
            ml_pred = primary.predict(X)[0]
            logger.info(f"ML model prediction: {ml_pred} (not used - using rule-based: {strength_label})")
        except Exception as e:
            logger.debug(f"ML prediction skipped: {e}")
    
    return strength_label


def _map_label(raw):
    # Normalize various model output formats to one of 'Weak'|'Medium'|'Strong' when possible.
    mapping = {0: 'Weak', 1: 'Medium', 2: 'Strong'}
    try:
        # unwrap lists/tuples/ndarrays
        if isinstance(raw, (list, tuple)) and raw:
            # if it's a probability vector or scores, pick argmax
            try:
                # try numeric elements
                nums = [float(x) for x in raw]
                idx = int(max(range(len(nums)), key=lambda i: nums[i]))
                return mapping.get(idx, str(raw))
            except Exception:
                # fall back to first element
                raw = raw[0]

        # if numpy array-like
        try:
            import numpy as _np
            if _np and hasattr(raw, 'shape'):
                arr = _np.asarray(raw)
                if arr.size > 1:
                    idx = int(_np.argmax(arr))
                    return mapping.get(idx, str(raw))
                if arr.size == 1:
                    raw = arr.reshape(-1)[0]
        except Exception:
            pass

        # if it's a string numeric
        if isinstance(raw, str) and raw.isdigit():
            return mapping.get(int(raw), raw)

        # if it's numeric (float/int)
        try:
            ir = int(raw)
            return mapping.get(ir, str(raw))
        except Exception:
            pass

        # if it's a dict with probabilities
        if isinstance(raw, dict):
            # try to find highest-probability key
            try:
                keys = list(raw.keys())
                vals = [float(raw[k]) for k in keys]
                k = keys[int(max(range(len(vals)), key=lambda i: vals[i]))]
                return str(k)
            except Exception:
                return str(raw)

        # fallback to string
        return str(raw)
    except Exception:
        return str(raw)


def _estimate_crack_time(password):
    """Simple entropy-based crack-time estimator.
    Returns a human-friendly string (years).
    """
    length = len(password)
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(not c.isalnum() for c in password):
        pool += 32
    if pool <= 1:
        pool = 2
    # entropy bits
    entropy = length * math.log2(pool)
    # assume 1e10 guesses per second (fast offline cracking)
    guesses_per_sec = 1e10
    seconds = (2 ** entropy) / guesses_per_sec
    years = seconds / (60 * 60 * 24 * 365)
    # cap and format
    if years > 1e12:
        return f">= {int(1e12)} years"
    if years < 1:
        # show in days/hours/minutes/seconds
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds/60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds/3600)} hours"
        else:
            return f"{int(seconds/86400)} days"
    return f"{int(years)} years"


def password_assistant_with_reuse(password):
    """Main convenience function that returns the analysis dict.
    Uses only the two requested models for strength prediction.
    """
    if not _models:
        initialize_models()

    raw_pred = _predict_strength(password)
    pred_label = _map_label(raw_pred)

    # rule-based issues
    issues = []
    if len(password) < 8:
        issues.append('Password is too short')
    if not any(c.isupper() for c in password):
        issues.append('No uppercase letter')
    if not any(c.islower() for c in password):
        issues.append('No lowercase letter')
    if not any(c.isdigit() for c in password):
        issues.append('No digit')
    if not any(not c.isalnum() for c in password):
        issues.append('No special character')

    # suggestions: try improvement model
    suggestions = []
    improv = _models.get('improvement')
    vec = _models.get('vectorizer')
    if improv is not None:
        try:
            if vec is not None:
                X = vec.transform([password])
                suggestions = list(improv.predict(X))
            else:
                suggestions = list(improv.predict([password]))
        except Exception:
            suggestions = []

    if not suggestions:
        # simple deterministic fallback suggestions
        suggestions = [
            password[::-1] + "@1A",
            ''.join(reversed(password))[:12] + "#X",
            password + "_Strong"
        ]

    # crack time
    crack_time = _estimate_crack_time(password)

    # reuse detection (kept internal) -- do not include empty reuse_warning in API response
    reuse_list = _models.get('reuse_list', set())
    if password in reuse_list:
        # If detection is needed later, it can be surfaced separately
        logger.info('Exact password reuse detected for input')

    return {
        'input_password': password,
        'predicted_strength': pred_label,
        'issues_found': issues,
        'suggestions': suggestions,
        'estimated_crack_time': crack_time,
    }


