"""
Simple verification that IntegratedMainWindow can be imported and has required attributes
"""

import sys

print("=" * 60)
print("Simple Integrated Main Window Verification")
print("=" * 60)
print()

try:
    print("1. Testing imports...")
    from src.gui.integrated_main_window import IntegratedMainWindow
    print("   ✓ IntegratedMainWindow imported successfully")
    
    print("\n2. Checking class attributes...")
    
    # Check if class has required methods
    required_methods = [
        '_setup_ui',
        '_create_menu_bar',
        '_create_toolbar',
        '_create_status_bar',
        '_setup_connections',
        '_load_departments',
        '_restore_window_state',
        '_save_window_state',
    ]
    
    for method in required_methods:
        assert hasattr(IntegratedMainWindow, method), f"Missing method: {method}"
        print(f"   ✓ Has method: {method}")
    
    print("\n3. Checking menu action handlers...")
    
    action_handlers = [
        '_on_new_record',
        '_on_import_excel',
        '_on_export_excel',
        '_on_copy',
        '_on_paste',
        '_on_delete',
        '_on_refresh',
        '_on_field_manager',
        '_on_formula_builder',
        '_on_push_conditions',
        '_on_about',
    ]
    
    for handler in action_handlers:
        assert hasattr(IntegratedMainWindow, handler), f"Missing handler: {handler}"
        print(f"   ✓ Has handler: {handler}")
    
    print("\n" + "=" * 60)
    print("✓ All verification checks passed!")
    print("=" * 60)
    
    sys.exit(0)
    
except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ Verification failed: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
