class ScaffoldError(Exception):
    """Base error with a user-actionable message."""
class ConfigError(ScaffoldError): pass
class GenerationError(ScaffoldError): pass
class GitError(ScaffoldError): pass
class VerificationError(ScaffoldError): pass
