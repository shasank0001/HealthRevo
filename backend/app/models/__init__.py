"""SQLAlchemy models package.

Import all model modules here so that SQLAlchemy's mapper registry
knows about every mapped class (resolves string-based relationships).
"""

# flake8: noqa

from .user import User, UserRole  # noqa: F401
from .patient import Patient  # noqa: F401
from .vitals import Vitals  # noqa: F401
from .prescription import Prescription  # noqa: F401
from .risk_score import RiskScore  # noqa: F401
from .alert import Alert  # noqa: F401
from .lifestyle_log import LifestyleLog  # noqa: F401
from .drug_interaction import DrugInteraction  # noqa: F401
