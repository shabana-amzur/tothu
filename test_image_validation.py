"""
Test script for Image Rule Validation & Data Extraction API
Run this after starting the backend server.
"""
import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/image-validation"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def test_get_document_types():
    """Test getting available document types."""
    print_section("Test 1: Get Available Document Types")
    
    url = f"{BASE_URL}{API_PREFIX}/document-types"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_get_rules(document_type="invoice"):
    """Test getting rules for a specific document type."""
    print_section(f"Test 2: Get Rules for '{document_type}'")
    
    url = f"{BASE_URL}{API_PREFIX}/rules/{document_type}"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_extract_only(image_path=None, document_type="invoice"):
    """Test data extraction without validation."""
    print_section("Test 3: Extract Data Only")
    
    if image_path and Path(image_path).exists():
        url = f"{BASE_URL}{API_PREFIX}/extract"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'document_type': document_type}
            response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    else:
        print("⚠️  No test image provided. Skipping extraction test.")
        print("To test extraction, provide an image path:")
        print("  python test_image_validation.py --image path/to/invoice.jpg")
        return None


def test_validate_image(image_path=None, document_type="invoice"):
    """Test full validation with rules."""
    print_section("Test 4: Validate Image with Rules")
    
    if image_path and Path(image_path).exists():
        url = f"{BASE_URL}{API_PREFIX}/validate"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'document_type': document_type,
                'expected_fields': json.dumps([
                    'invoice_number',
                    'invoice_date',
                    'total_amount',
                    'currency',
                    'vendor_name'
                ])
            }
            response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2)}")
        
        # Print summary
        if response.status_code == 200:
            print(f"\n📊 Validation Summary:")
            print(f"  Overall Status: {result.get('overall_status')}")
            print(f"  Confidence Score: {result.get('confidence_score')}")
            print(f"  Fields Extracted: {len(result.get('extracted_data', {}))}")
            print(f"  Rules Checked: {len(result.get('validation_results', []))}")
            
            # Show pass/fail counts
            passed = sum(1 for r in result.get('validation_results', []) if r['status'] == 'PASS')
            failed = len(result.get('validation_results', [])) - passed
            print(f"  Passed: {passed}, Failed: {failed}")
        
        return response.status_code == 200
    else:
        print("⚠️  No test image provided. Skipping validation test.")
        print("To test validation, provide an image path:")
        print("  python test_image_validation.py --image path/to/invoice.jpg")
        return None


def test_invalid_document_type():
    """Test with an invalid document type."""
    print_section("Test 5: Invalid Document Type")
    
    url = f"{BASE_URL}{API_PREFIX}/rules/invalid_type"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 404


def test_health_check():
    """Test if the server is running."""
    print_section("Health Check")
    
    try:
        url = f"{BASE_URL}/health"
        response = requests.get(url, timeout=5)
        print(f"✅ Server is running")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running or not responding")
        print(f"Error: {str(e)}")
        return False


def create_sample_test_data():
    """Create sample test data structure."""
    print_section("Sample Test Data")
    
    sample_data = {
        "invoice": {
            "invoice_number": "INV-2024-001",
            "invoice_date": "2024-01-15",
            "total_amount": 1500.00,
            "currency": "USD",
            "vendor_name": "ABC Corp",
            "email": "contact@abccorp.com"
        },
        "receipt": {
            "receipt_number": "RCP-123456",
            "date": "2024-01-20",
            "total": 45.50,
            "merchant_name": "Coffee Shop",
            "payment_method": "CARD"
        },
        "id_card": {
            "id_number": "AB12345678",
            "full_name": "John Doe",
            "date_of_birth": "1990-05-15",
            "expiry_date": "2030-05-15"
        }
    }
    
    print("Sample data that should pass validation:")
    print(json.dumps(sample_data, indent=2))
    
    return sample_data


def run_all_tests(image_path=None, document_type="invoice"):
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("  IMAGE RULE VALIDATION API TESTS")
    print("🧪" * 30 + "\n")
    
    results = []
    
    # Health check first
    if not test_health_check():
        print("\n❌ Server is not running. Please start the backend first:")
        print("   cd backend && python main.py")
        return
    
    # Run tests
    results.append(("Get Document Types", test_get_document_types()))
    results.append(("Get Rules", test_get_rules(document_type)))
    results.append(("Extract Data", test_extract_only(image_path, document_type)))
    results.append(("Validate Image", test_validate_image(image_path, document_type)))
    results.append(("Invalid Document Type", test_invalid_document_type()))
    
    # Show sample test data
    create_sample_test_data()
    
    # Print summary
    print_section("Test Summary")
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n✨ All tests passed! ✨")
    
    # Instructions for full testing
    if skipped > 0:
        print("\n" + "ℹ️ " * 20)
        print("\nTo run full tests with an actual image:")
        print("1. Prepare a test image (invoice, receipt, or ID card)")
        print("2. Run: python test_image_validation.py --image path/to/image.jpg --type invoice")
        print("\nOr use the interactive test below:")
        print("=" * 60)


def interactive_test():
    """Interactive test mode."""
    print_section("Interactive Test Mode")
    
    print("Choose a test:")
    print("1. Get available document types")
    print("2. Get rules for a document type")
    print("3. Upload and validate an image")
    print("4. Run all tests")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        test_get_document_types()
    elif choice == "2":
        doc_type = input("Enter document type (invoice/receipt/id_card): ").strip()
        test_get_rules(doc_type)
    elif choice == "3":
        image_path = input("Enter image path: ").strip()
        doc_type = input("Enter document type (invoice/receipt/id_card): ").strip()
        test_validate_image(image_path, doc_type)
    elif choice == "4":
        image_path = input("Enter image path (optional, press Enter to skip): ").strip()
        doc_type = input("Enter document type (invoice/receipt/id_card): ").strip() or "invoice"
        run_all_tests(image_path if image_path else None, doc_type)
    elif choice == "5":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print("Usage:")
            print("  python test_image_validation.py                    # Run basic tests")
            print("  python test_image_validation.py --image PATH       # Test with image")
            print("  python test_image_validation.py --image PATH --type TYPE")
            print("  python test_image_validation.py --interactive      # Interactive mode")
            print("\nDocument types: invoice, receipt, id_card")
            sys.exit(0)
        
        if "--interactive" in sys.argv:
            interactive_test()
        else:
            image_path = None
            document_type = "invoice"
            
            if "--image" in sys.argv:
                idx = sys.argv.index("--image")
                if idx + 1 < len(sys.argv):
                    image_path = sys.argv[idx + 1]
            
            if "--type" in sys.argv:
                idx = sys.argv.index("--type")
                if idx + 1 < len(sys.argv):
                    document_type = sys.argv[idx + 1]
            
            run_all_tests(image_path, document_type)
    else:
        # Run basic tests without image
        run_all_tests()
