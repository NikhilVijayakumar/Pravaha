"""
Robust Configuration Validator

Adapted from Nibandha's RobustConfigValidator.
Recursively validates input data against Pydantic models,
sanitizing invalid fields and maintaining a detailed audit log.
"""

import logging
from typing import Type, Any, Dict, List
from pydantic import BaseModel, TypeAdapter

logger = logging.getLogger(__name__)


class PravahaRobustConfigValidator:
    """
    Validator that recursively checks input data against a Pydantic model.
    It sanitizes the data by keeping valid fields and discarding invalid ones
    (triggering fallback to defaults), while maintaining a detailed audit log.
    """

    def __init__(self):
        self.audit_log: List[str] = []

    def validate_and_sanitize(
        self,
        model_class: Type[BaseModel],
        input_data: Dict[str, Any],
        parent_path: str = "",
    ) -> Dict[str, Any]:
        """
        Recursively validates input_data against model_class.
        Returns a dictionary containing ONLY valid fields.
        Invalid fields are omitted, allowing Pydantic to fall back
        to their default values during instantiation.

        Args:
            model_class: The Pydantic model class to validate against.
            input_data: The raw configuration dictionary.
            parent_path: Dot-separated path for audit log (internal use).

        Returns:
            Sanitized dictionary with only valid fields.
        """
        clean_data = {}

        if input_data is None:
            return {}

        if not isinstance(input_data, dict):
            self.audit_log.append(
                f"[WARNING] {parent_path or 'Root'}: "
                f"Input is not a dictionary ({type(input_data).__name__}). Using defaults."
            )
            return {}

        for field_name, field_info in model_class.model_fields.items():
            full_path = (
                f"{parent_path}.{field_name}" if parent_path else field_name
            )

            # 1. Missing fields — skip (defaults used later)
            if field_name not in input_data:
                continue

            value = input_data[field_name]
            field_type = field_info.annotation

            # 2. Check for Pydantic Model (Direct or Optional/Union wrapped)
            is_model = False
            target_model = field_type

            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                is_model = True

            # Special handling: If value is a dict and target is a model, recurse
            if is_model and isinstance(value, dict):
                sub_validator = PravahaRobustConfigValidator()
                sub_clean = sub_validator.validate_and_sanitize(
                    target_model, value, full_path
                )
                clean_data[field_name] = sub_clean
                self.audit_log.extend(sub_validator.audit_log)
                continue

            # 3. Standard Validation for primitives or mismatch types
            try:
                adapter = TypeAdapter(field_type)
                valid_value = adapter.validate_python(value)
                clean_data[field_name] = valid_value
                self.audit_log.append(f"[VALID]   {full_path}: Accepted.")
            except Exception as e:
                # REJECT invalid field, do NOT include in clean_data
                # This triggers fallback to default value defined in the Model
                msg = (
                    f"[INVALID] {full_path}: Rejected value '{value}' "
                    f"({type(e).__name__}). Using Default."
                )
                self.audit_log.append(msg)
                logger.warning(msg)

        return clean_data
