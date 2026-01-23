"""
Utility script to create and manage validation rules.
"""
import json
from pathlib import Path
from typing import List, Dict, Any


def create_rule(
    field: str,
    rule_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a validation rule.
    
    Args:
        field: Field name to validate
        rule_type: Type of rule (REQUIRED_FIELD, REGEX_MATCH, etc.)
        **kwargs: Additional rule parameters
    
    Returns:
        Rule dictionary
    """
    rule = {
        "field": field,
        "type": rule_type
    }
    
    # Add optional parameters
    if "condition" in kwargs:
        rule["condition"] = kwargs["condition"]
    if "min" in kwargs:
        rule["min"] = kwargs["min"]
    if "max" in kwargs:
        rule["max"] = kwargs["max"]
    if "pattern" in kwargs:
        rule["pattern"] = kwargs["pattern"]
    if "values" in kwargs:
        rule["values"] = kwargs["values"]
    
    return rule


def create_ruleset(
    document_type: str,
    rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create a complete rule set.
    
    Args:
        document_type: Type of document
        rules: List of rule dictionaries
    
    Returns:
        Complete ruleset dictionary
    """
    return {
        "document_type": document_type,
        "rules": rules
    }


def save_ruleset(
    ruleset: Dict[str, Any],
    output_path: str = None
):
    """
    Save a ruleset to a JSON file.
    
    Args:
        ruleset: Ruleset dictionary
        output_path: Output file path (optional)
    """
    if output_path is None:
        # Save to default location
        rules_dir = Path(__file__).parent / "backend" / "app" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        output_path = rules_dir / f"{ruleset['document_type']}_rules.json"
    
    with open(output_path, 'w') as f:
        json.dump(ruleset, f, indent=2)
    
    print(f"✅ Ruleset saved to: {output_path}")


def create_invoice_rules():
    """Create invoice validation rules."""
    rules = [
        create_rule("invoice_number", "REQUIRED_FIELD"),
        create_rule("invoice_date", "DATE_CHECK", condition="PAST"),
        create_rule("total_amount", "RANGE_CHECK", min=1),
        create_rule("currency", "ENUM_CHECK", values=["INR", "USD", "EUR", "GBP"]),
        create_rule("vendor_name", "REQUIRED_FIELD"),
        create_rule("email", "REGEX_MATCH", 
                   pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    ]
    
    return create_ruleset("invoice", rules)


def create_purchase_order_rules():
    """Create purchase order validation rules."""
    rules = [
        create_rule("po_number", "REQUIRED_FIELD"),
        create_rule("po_date", "DATE_CHECK", condition="ANY"),
        create_rule("vendor_name", "REQUIRED_FIELD"),
        create_rule("total", "RANGE_CHECK", min=0),
        create_rule("status", "ENUM_CHECK", values=["PENDING", "APPROVED", "REJECTED"]),
        create_rule("delivery_date", "DATE_CHECK", condition="FUTURE")
    ]
    
    return create_ruleset("purchase_order", rules)


def create_bill_of_lading_rules():
    """Create bill of lading validation rules."""
    rules = [
        create_rule("bl_number", "REQUIRED_FIELD"),
        create_rule("vessel_name", "REQUIRED_FIELD"),
        create_rule("port_of_loading", "REQUIRED_FIELD"),
        create_rule("port_of_discharge", "REQUIRED_FIELD"),
        create_rule("container_number", "REGEX_MATCH",
                   pattern=r"^[A-Z]{4}[0-9]{7}$"),
        create_rule("date_of_shipment", "DATE_CHECK", condition="ANY")
    ]
    
    return create_ruleset("bill_of_lading", rules)


def create_bank_statement_rules():
    """Create bank statement validation rules."""
    rules = [
        create_rule("account_number", "REQUIRED_FIELD"),
        create_rule("account_holder_name", "REQUIRED_FIELD"),
        create_rule("statement_period", "REQUIRED_FIELD"),
        create_rule("opening_balance", "RANGE_CHECK", min=0),
        create_rule("closing_balance", "RANGE_CHECK", min=0),
        create_rule("bank_name", "REQUIRED_FIELD")
    ]
    
    return create_ruleset("bank_statement", rules)


def create_passport_rules():
    """Create passport validation rules."""
    rules = [
        create_rule("passport_number", "REQUIRED_FIELD"),
        create_rule("full_name", "REQUIRED_FIELD"),
        create_rule("date_of_birth", "DATE_CHECK", condition="PAST"),
        create_rule("date_of_issue", "DATE_CHECK", condition="PAST"),
        create_rule("date_of_expiry", "DATE_CHECK", condition="FUTURE"),
        create_rule("nationality", "REQUIRED_FIELD"),
        create_rule("passport_number", "REGEX_MATCH",
                   pattern=r"^[A-Z]{1,2}[0-9]{6,9}$")
    ]
    
    return create_ruleset("passport", rules)


def interactive_rule_creator():
    """Interactive rule creation tool."""
    print("\n" + "=" * 60)
    print("  RULE CREATION WIZARD")
    print("=" * 60 + "\n")
    
    document_type = input("Enter document type (e.g., invoice, receipt): ").strip()
    
    rules = []
    
    print("\nAdd validation rules (press Enter without input to finish):")
    
    while True:
        print("\n" + "-" * 40)
        field = input("Field name: ").strip()
        
        if not field:
            break
        
        print("\nRule types:")
        print("1. REQUIRED_FIELD")
        print("2. REGEX_MATCH")
        print("3. RANGE_CHECK")
        print("4. DATE_CHECK")
        print("5. ENUM_CHECK")
        
        choice = input("Choose rule type (1-5): ").strip()
        
        if choice == "1":
            rules.append(create_rule(field, "REQUIRED_FIELD"))
        
        elif choice == "2":
            pattern = input("Enter regex pattern: ").strip()
            rules.append(create_rule(field, "REGEX_MATCH", pattern=pattern))
        
        elif choice == "3":
            min_val = input("Enter minimum value (optional): ").strip()
            max_val = input("Enter maximum value (optional): ").strip()
            kwargs = {}
            if min_val:
                kwargs["min"] = float(min_val)
            if max_val:
                kwargs["max"] = float(max_val)
            rules.append(create_rule(field, "RANGE_CHECK", **kwargs))
        
        elif choice == "4":
            print("Condition: PAST, FUTURE, or ANY")
            condition = input("Enter condition: ").strip().upper()
            rules.append(create_rule(field, "DATE_CHECK", condition=condition))
        
        elif choice == "5":
            values = input("Enter allowed values (comma-separated): ").strip()
            values_list = [v.strip() for v in values.split(",")]
            rules.append(create_rule(field, "ENUM_CHECK", values=values_list))
        
        else:
            print("Invalid choice!")
            continue
        
        print(f"✅ Rule added for field '{field}'")
    
    if not rules:
        print("No rules added. Exiting.")
        return
    
    ruleset = create_ruleset(document_type, rules)
    
    print("\n" + "=" * 60)
    print("  RULESET PREVIEW")
    print("=" * 60)
    print(json.dumps(ruleset, indent=2))
    
    save = input("\nSave this ruleset? (y/n): ").strip().lower()
    
    if save == "y":
        save_ruleset(ruleset)
        print("\n✨ Ruleset created successfully!")
    else:
        print("\nRuleset not saved.")


def generate_all_sample_rules():
    """Generate all sample rule files."""
    print("Generating sample rule files...")
    
    rules_dir = Path(__file__).parent / "backend" / "app" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample rules
    samples = [
        ("Invoice", create_invoice_rules),
        ("Purchase Order", create_purchase_order_rules),
        ("Bill of Lading", create_bill_of_lading_rules),
        ("Bank Statement", create_bank_statement_rules),
        ("Passport", create_passport_rules),
    ]
    
    for name, creator_func in samples:
        try:
            ruleset = creator_func()
            save_ruleset(ruleset)
            print(f"✅ Created {name} rules")
        except Exception as e:
            print(f"❌ Failed to create {name} rules: {str(e)}")
    
    print(f"\n✨ Generated {len(samples)} sample rule files")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--generate-samples":
            generate_all_sample_rules()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python create_rules.py                  # Interactive mode")
            print("  python create_rules.py --generate-samples  # Generate all samples")
            print("  python create_rules.py --help           # Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        interactive_rule_creator()
