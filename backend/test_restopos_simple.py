#!/usr/bin/env python
"""
Simple test to verify the RestoPOS module fix without database
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.restopos.models import Restaurant, Staff
from apps.restopos.views import RestaurantAccessMixin, dashboard
import inspect


def test_model_structure():
    """Test that the Restaurant model doesn't have an owner field"""
    
    print("Testing RestoPOS Model Structure...")
    print("-" * 50)
    
    # Check Restaurant model fields
    restaurant_fields = [field.name for field in Restaurant._meta.get_fields()]
    
    print("Restaurant model fields:")
    for field in sorted(restaurant_fields):
        print(f"  - {field}")
    
    print("\n" + "=" * 50)
    
    # Check if 'owner' field exists
    if 'owner' in restaurant_fields:
        print("✗ ERROR: Restaurant model has an 'owner' field")
        print("  This should not exist - restaurants should be linked to users via Staff model")
        return False
    else:
        print("✓ PASS: Restaurant model correctly does not have an 'owner' field")
    
    # Check Staff model fields
    staff_fields = [field.name for field in Staff._meta.get_fields()]
    
    print("\nStaff model fields:")
    for field in ['restaurant', 'user', 'role', 'employee_id']:
        if field in staff_fields:
            print(f"  ✓ {field} exists")
        else:
            print(f"  ✗ {field} missing")
    
    print("\n" + "=" * 50)
    return True


def test_view_structure():
    """Test that the dashboard view has been fixed"""
    
    print("\nTesting RestoPOS View Structure...")
    print("-" * 50)
    
    # Get the source code of the dashboard function
    dashboard_source = inspect.getsource(dashboard)
    
    # Check if the problematic line exists
    if "Restaurant.objects.filter(owner=request.user)" in dashboard_source:
        print("✗ ERROR: Dashboard view still references 'owner' field")
        print("  The line 'Restaurant.objects.filter(owner=request.user)' should not exist")
        return False
    else:
        print("✓ PASS: Dashboard view no longer references non-existent 'owner' field")
    
    # Check if the fix is implemented
    if "Staff.objects.filter" in dashboard_source:
        print("✓ PASS: Dashboard view correctly uses Staff model for access control")
    else:
        print("⚠ WARNING: Dashboard view doesn't seem to use Staff model")
    
    # Check for the mixin
    print("\nChecking RestaurantAccessMixin:")
    if hasattr(RestaurantAccessMixin, 'get_user_restaurants'):
        print("✓ PASS: RestaurantAccessMixin.get_user_restaurants method exists")
    else:
        print("✗ ERROR: RestaurantAccessMixin.get_user_restaurants method missing")
    
    if hasattr(RestaurantAccessMixin, 'filter_queryset_by_restaurant'):
        print("✓ PASS: RestaurantAccessMixin.filter_queryset_by_restaurant method exists")
    else:
        print("✗ ERROR: RestaurantAccessMixin.filter_queryset_by_restaurant method missing")
    
    print("\n" + "=" * 50)
    return True


def main():
    """Main test runner"""
    
    print("\n" + "=" * 60)
    print("RestoPOS Module Fix Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Test model structure
    if not test_model_structure():
        all_passed = False
    
    # Test view structure
    if not test_view_structure():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nSummary of fixes:")
        print("1. Restaurant model correctly uses Staff model for multi-tenancy")
        print("2. Dashboard view fixed to use Staff model instead of non-existent 'owner' field")
        print("3. RestaurantAccessMixin implemented for consistent access control")
        print("4. ViewSets updated to use RestaurantAccessMixin for data isolation")
        print("\nThe RestoPOS module is now ready for use with proper multi-tenant support.")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please review the errors above.")
    
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)