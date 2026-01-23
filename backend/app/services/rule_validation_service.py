"""
Rule validation engine for extracted data.
"""
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.schemas.image_validation import (
    Rule,
    RuleSet,
    RuleType,
    DateCondition,
    ValidationResult
)


class RuleValidationService:
    """Service for validating extracted data against defined rules."""
    
    def __init__(self):
        """Initialize the validation service."""
        self.rules_dir = Path(__file__).parent.parent / "rules"
        self._rule_cache: Dict[str, RuleSet] = {}
    
    def load_rules(self, document_type: str) -> Optional[RuleSet]:
        """
        Load rules for a specific document type.
        
        Args:
            document_type: Type of document (invoice, receipt, etc.)
            
        Returns:
            RuleSet object or None if not found
        """
        # Check cache first
        if document_type in self._rule_cache:
            return self._rule_cache[document_type]
        
        # Try to load from file
        rule_file = self.rules_dir / f"{document_type}_rules.json"
        if not rule_file.exists():
            return None
        
        try:
            with open(rule_file, 'r') as f:
                rule_data = json.load(f)
            
            rule_set = RuleSet(**rule_data)
            self._rule_cache[document_type] = rule_set
            return rule_set
        except Exception as e:
            print(f"Error loading rules for {document_type}: {str(e)}")
            return None
    
    def validate_required_field(
        self,
        field: str,
        data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate that a required field exists and is not empty.
        
        Args:
            field: Field name to check
            data: Extracted data dictionary
            
        Returns:
            ValidationResult object
        """
        if field not in data:
            return ValidationResult(
                field=field,
                rule_type=RuleType.REQUIRED_FIELD,
                status="FAIL",
                reason=f"Required field '{field}' is missing"
            )
        
        value = data[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult(
                field=field,
                rule_type=RuleType.REQUIRED_FIELD,
                status="FAIL",
                reason=f"Required field '{field}' is empty"
            )
        
        return ValidationResult(
            field=field,
            rule_type=RuleType.REQUIRED_FIELD,
            status="PASS"
        )
    
    def validate_regex_match(
        self,
        field: str,
        data: Dict[str, Any],
        pattern: str
    ) -> ValidationResult:
        """
        Validate that a field matches a regex pattern.
        
        Args:
            field: Field name to check
            data: Extracted data dictionary
            pattern: Regex pattern to match
            
        Returns:
            ValidationResult object
        """
        if field not in data:
            return ValidationResult(
                field=field,
                rule_type=RuleType.REGEX_MATCH,
                status="FAIL",
                reason=f"Field '{field}' not found in extracted data"
            )
        
        value = str(data[field])
        
        try:
            if not re.match(pattern, value):
                return ValidationResult(
                    field=field,
                    rule_type=RuleType.REGEX_MATCH,
                    status="FAIL",
                    reason=f"Field '{field}' does not match pattern '{pattern}'. Value: '{value}'"
                )
            
            return ValidationResult(
                field=field,
                rule_type=RuleType.REGEX_MATCH,
                status="PASS"
            )
        except re.error as e:
            return ValidationResult(
                field=field,
                rule_type=RuleType.REGEX_MATCH,
                status="FAIL",
                reason=f"Invalid regex pattern: {str(e)}"
            )
    
    def validate_range_check(
        self,
        field: str,
        data: Dict[str, Any],
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate that a numeric field is within a specified range.
        
        Args:
            field: Field name to check
            data: Extracted data dictionary
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            ValidationResult object
        """
        if field not in data:
            return ValidationResult(
                field=field,
                rule_type=RuleType.RANGE_CHECK,
                status="FAIL",
                reason=f"Field '{field}' not found in extracted data"
            )
        
        try:
            value = float(data[field])
        except (ValueError, TypeError):
            return ValidationResult(
                field=field,
                rule_type=RuleType.RANGE_CHECK,
                status="FAIL",
                reason=f"Field '{field}' is not a valid number. Value: '{data[field]}'"
            )
        
        # Check minimum
        if min_val is not None and value < min_val:
            return ValidationResult(
                field=field,
                rule_type=RuleType.RANGE_CHECK,
                status="FAIL",
                reason=f"Value {value} is below minimum {min_val}"
            )
        
        # Check maximum
        if max_val is not None and value > max_val:
            return ValidationResult(
                field=field,
                rule_type=RuleType.RANGE_CHECK,
                status="FAIL",
                reason=f"Value {value} exceeds maximum {max_val}"
            )
        
        return ValidationResult(
            field=field,
            rule_type=RuleType.RANGE_CHECK,
            status="PASS"
        )
    
    def validate_date_check(
        self,
        field: str,
        data: Dict[str, Any],
        condition: DateCondition
    ) -> ValidationResult:
        """
        Validate that a date field meets the specified condition.
        
        Args:
            field: Field name to check
            data: Extracted data dictionary
            condition: Date condition (PAST, FUTURE, ANY)
            
        Returns:
            ValidationResult object
        """
        if field not in data:
            return ValidationResult(
                field=field,
                rule_type=RuleType.DATE_CHECK,
                status="FAIL",
                reason=f"Field '{field}' not found in extracted data"
            )
        
        date_str = str(data[field])
        
        # Try multiple date formats
        date_formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d %b %Y',
            '%d %B %Y',
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            return ValidationResult(
                field=field,
                rule_type=RuleType.DATE_CHECK,
                status="FAIL",
                reason=f"Field '{field}' is not a valid date. Value: '{date_str}'"
            )
        
        # Check condition
        now = datetime.now()
        
        if condition == DateCondition.PAST:
            if parsed_date > now:
                return ValidationResult(
                    field=field,
                    rule_type=RuleType.DATE_CHECK,
                    status="FAIL",
                    reason=f"Date {date_str} is in the future, but should be in the past"
                )
        elif condition == DateCondition.FUTURE:
            if parsed_date < now:
                return ValidationResult(
                    field=field,
                    rule_type=RuleType.DATE_CHECK,
                    status="FAIL",
                    reason=f"Date {date_str} is in the past, but should be in the future"
                )
        
        return ValidationResult(
            field=field,
            rule_type=RuleType.DATE_CHECK,
            status="PASS"
        )
    
    def validate_enum_check(
        self,
        field: str,
        data: Dict[str, Any],
        allowed_values: List[str]
    ) -> ValidationResult:
        """
        Validate that a field value is one of the allowed values.
        
        Args:
            field: Field name to check
            data: Extracted data dictionary
            allowed_values: List of allowed values
            
        Returns:
            ValidationResult object
        """
        if field not in data:
            return ValidationResult(
                field=field,
                rule_type=RuleType.ENUM_CHECK,
                status="FAIL",
                reason=f"Field '{field}' not found in extracted data"
            )
        
        value = str(data[field]).strip().upper()
        allowed_upper = [v.upper() for v in allowed_values]
        
        if value not in allowed_upper:
            return ValidationResult(
                field=field,
                rule_type=RuleType.ENUM_CHECK,
                status="FAIL",
                reason=f"Value '{data[field]}' is not in allowed values: {allowed_values}"
            )
        
        return ValidationResult(
            field=field,
            rule_type=RuleType.ENUM_CHECK,
            status="PASS"
        )
    
    def validate_single_rule(
        self,
        rule: Rule,
        data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a single rule against extracted data.
        
        Args:
            rule: Rule to validate
            data: Extracted data dictionary
            
        Returns:
            ValidationResult object
        """
        if rule.type == RuleType.REQUIRED_FIELD:
            return self.validate_required_field(rule.field, data)
        
        elif rule.type == RuleType.REGEX_MATCH:
            if not rule.pattern:
                return ValidationResult(
                    field=rule.field,
                    rule_type=rule.type,
                    status="FAIL",
                    reason="Regex pattern not specified in rule"
                )
            return self.validate_regex_match(rule.field, data, rule.pattern)
        
        elif rule.type == RuleType.RANGE_CHECK:
            return self.validate_range_check(rule.field, data, rule.min, rule.max)
        
        elif rule.type == RuleType.DATE_CHECK:
            if not rule.condition:
                return ValidationResult(
                    field=rule.field,
                    rule_type=rule.type,
                    status="FAIL",
                    reason="Date condition not specified in rule"
                )
            return self.validate_date_check(rule.field, data, rule.condition)
        
        elif rule.type == RuleType.ENUM_CHECK:
            if not rule.values:
                return ValidationResult(
                    field=rule.field,
                    rule_type=rule.type,
                    status="FAIL",
                    reason="Allowed values not specified in rule"
                )
            return self.validate_enum_check(rule.field, data, rule.values)
        
        else:
            return ValidationResult(
                field=rule.field,
                rule_type=rule.type,
                status="FAIL",
                reason=f"Unknown rule type: {rule.type}"
            )
    
    def validate_data(
        self,
        data: Dict[str, Any],
        document_type: str
    ) -> tuple[List[ValidationResult], str]:
        """
        Validate extracted data against all rules for a document type.
        
        Args:
            data: Extracted data dictionary
            document_type: Type of document
            
        Returns:
            Tuple of (validation_results, overall_status)
        """
        # Load rules
        rule_set = self.load_rules(document_type)
        if not rule_set:
            raise ValueError(f"No rules found for document type: {document_type}")
        
        # Validate each rule
        results = []
        for rule in rule_set.rules:
            result = self.validate_single_rule(rule, data)
            results.append(result)
        
        # Determine overall status
        has_failures = any(r.status == "FAIL" for r in results)
        overall_status = "INVALID" if has_failures else "VALID"
        
        return results, overall_status
    
    def get_available_document_types(self) -> List[str]:
        """
        Get list of available document types with rules.
        
        Returns:
            List of document type names
        """
        if not self.rules_dir.exists():
            return []
        
        types = []
        for rule_file in self.rules_dir.glob("*_rules.json"):
            # Extract document type from filename
            doc_type = rule_file.stem.replace("_rules", "")
            types.append(doc_type)
        
        return sorted(types)


# Singleton instance
_validation_service = None


def get_validation_service() -> RuleValidationService:
    """Get or create singleton validation service instance."""
    global _validation_service
    if _validation_service is None:
        _validation_service = RuleValidationService()
    return _validation_service
