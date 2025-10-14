# SPDX-License-Identifier: MIT
"""
Validation service module for Pydantic models.
"""

from pydantic import BaseModel, ValidationError


class ValidateService:
    """A service class providing validation utilities for Pydantic models."""

    @staticmethod
    def validate(obj: BaseModel) -> str | None:
        """Validate a Pydantic model instance.

        Args:
            obj: The Pydantic BaseModel instance to validate.

        Returns:
            Optional[str]: None if validation passes, otherwise a comma-separated string
            of validation error messages.
        """
        try:
            # Call Pydantic's validation logic (for Pydantic v2.x)
            obj.model_validate()  # For v2.x Pydantic
            return None
        except ValidationError as e:
            # Concatenate error messages
            errors = ", ".join(
                [
                    f"{'->'.join(map(str, error['loc']))}: {error['msg']}"
                    for error in e.errors()
                ]
            )
            return errors

    @staticmethod
    def get_validate_err_msg(e: ValidationError) -> str | None:
        """Format validation error messages from a ValidationError exception.

        Args:
            e: The ValidationError exception containing validation errors.

        Returns:
            Optional[str]: A comma-separated string of formatted error messages,
            or None if no errors exist.
        """
        err_msg = []
        for error in e.errors():
            field = " -> ".join(map(str, error["loc"]))  # Field path
            message = error["message"]  # Error description
            err_msg.append(f"Error in field '{field}': {message}")
        return ",".join(err_msg)
