"""
Startup Optimization Script for Transport Management System
Analyzes and optimizes application startup time

Usage:
    python optimize_startup.py
"""

import time
import sys
import importlib
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def measure_import_time(module_name):
    """Measure time to import a module"""
    start = time.time()
    try:
        importlib.import_module(module_name)
        elapsed = time.time() - start
        return elapsed, None
    except Exception as e:
        elapsed = time.time() - start
        return elapsed, str(e)


def analyze_imports():
    """Analyze import times for key modules"""
    print_header("Analyzing Import Times")
    
    modules = [
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pandas',
        'openpyxl',
        'pydantic',
        'sqlite3',
    ]
    
    results = []
    
    for module in modules:
        elapsed, error = measure_import_time(module)
        results.append((module, elapsed, error))
        
        if error:
            print(f"✗ {module}: {elapsed:.3f}s (ERROR: {error})")
        elif elapsed > 1.0:
            print(f"⚠ {module}: {elapsed:.3f}s (SLOW)")
        else:
            print(f"✓ {module}: {elapsed:.3f}s")
    
    total_time = sum(r[1] for r in results)
    print(f"\nTotal import time: {total_time:.3f}s")
    
    return results


def check_database_initialization():
    """Check database initialization time"""
    print_header("Checking Database Initialization")
    
    try:
        from src.database.enhanced_db_manager import EnhancedDatabaseManager
        import config
        
        start = time.time()
        db_manager = EnhancedDatabaseManager(config.DATABASE_PATH)
        elapsed = time.time() - start
        
        print(f"Database initialization: {elapsed:.3f}s")
        
        if elapsed > 2.0:
            print("⚠ Database initialization is slow")
            print("Recommendations:")
            print("  - Check if database file is on slow storage")
            print("  - Reduce connection pool size")
            print("  - Optimize schema indexes")
        else:
            print("✓ Database initialization is fast")
        
        return elapsed
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return None


def check_gui_initialization():
    """Check GUI initialization time"""
    print_header("Checking GUI Initialization")
    
    print("Note: This will open the application window briefly.")
    print("Press Enter to continue or Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n⚠ GUI initialization test skipped")
        return None
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        import config
        from src.database.enhanced_db_manager import EnhancedDatabaseManager
        from src.gui.integrated_main_window import IntegratedMainWindow
        
        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        
        db_manager = EnhancedDatabaseManager(config.DATABASE_PATH)
        
        start = time.time()
        main_window = IntegratedMainWindow(db_manager)
        main_window.show()
        elapsed = time.time() - start
        
        print(f"GUI initialization: {elapsed:.3f}s")
        
        if elapsed > 3.0:
            print("⚠ GUI initialization is slow")
            print("Recommendations:")
            print("  - Use lazy loading for widgets")
            print("  - Defer loading of non-critical components")
            print("  - Optimize widget creation")
        else:
            print("✓ GUI initialization is fast")
        
        # Close the window
        main_window.close()
        app.quit()
        
        return elapsed
        
    except Exception as e:
        print(f"✗ Error initializing GUI: {e}")
        return None


def analyze_file_sizes():
    """Analyze file sizes in the build"""
    print_header("Analyzing Build File Sizes")
    
    dist_dir = Path('dist/TransportManagementSystem')
    
    if not dist_dir.exists():
        print("⚠ Build directory not found. Run build.py first.")
        return
    
    # Get all files
    files = []
    for file_path in dist_dir.rglob('*'):
        if file_path.is_file():
            size = file_path.stat().st_size
            files.append((file_path.relative_to(dist_dir), size))
    
    # Sort by size
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Show top 10 largest files
    print("Top 10 largest files:")
    for i, (file_path, size) in enumerate(files[:10], 1):
        size_mb = size / (1024 * 1024)
        print(f"{i:2d}. {file_path} - {size_mb:.2f} MB")
    
    # Calculate total size
    total_size = sum(size for _, size in files)
    print(f"\nTotal build size: {total_size / (1024 * 1024):.2f} MB")
    
    # Recommendations
    if total_size > 300 * 1024 * 1024:  # > 300 MB
        print("\n⚠ Build size is large")
        print("Recommendations:")
        print("  - Enable UPX compression (already enabled)")
        print("  - Exclude unnecessary modules")
        print("  - Consider using --onefile mode")
    else:
        print("\n✓ Build size is reasonable")


def generate_optimization_report():
    """Generate optimization recommendations"""
    print_header("Optimization Recommendations")
    
    recommendations = []
    
    # Check if lazy loading is used
    print("Checking for optimization opportunities...")
    
    # Check main.py for optimization opportunities
    main_py = Path('main.py')
    if main_py.exists():
        content = main_py.read_text(encoding='utf-8')
        
        if 'import *' in content:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Wildcard imports found in main.py',
                'solution': 'Use specific imports instead of wildcard imports'
            })
        
        if 'from src' in content and content.count('from src') > 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': 'Many imports at startup',
                'solution': 'Consider lazy loading for non-critical modules'
            })
    
    # Check for large dependencies
    recommendations.append({
        'priority': 'LOW',
        'issue': 'PyQt6 and pandas are large dependencies',
        'solution': 'These are necessary, but ensure only required modules are imported'
    })
    
    # Print recommendations
    if recommendations:
        print("\nOptimization Opportunities:\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. [{rec['priority']}] {rec['issue']}")
            print(f"   Solution: {rec['solution']}\n")
    else:
        print("✓ No obvious optimization opportunities found")
    
    # General recommendations
    print("\nGeneral Optimization Tips:")
    print("1. Use lazy loading for heavy modules")
    print("2. Defer initialization of non-critical components")
    print("3. Use connection pooling for database (already implemented)")
    print("4. Cache frequently accessed data")
    print("5. Use background threads for heavy operations")
    print("6. Optimize database queries with indexes")
    print("7. Use debouncing for real-time operations")


def main():
    """Main optimization analysis"""
    print("=" * 60)
    print("  STARTUP OPTIMIZATION ANALYSIS")
    print("  Transport Management System")
    print("=" * 60)
    
    # Analyze imports
    import_results = analyze_imports()
    
    # Check database initialization
    db_time = check_database_initialization()
    
    # Check GUI initialization
    gui_time = check_gui_initialization()
    
    # Analyze file sizes
    analyze_file_sizes()
    
    # Generate recommendations
    generate_optimization_report()
    
    # Summary
    print_header("Summary")
    
    total_startup = 0
    if import_results:
        total_startup += sum(r[1] for r in import_results)
    if db_time:
        total_startup += db_time
    if gui_time:
        total_startup += gui_time
    
    print(f"Estimated total startup time: {total_startup:.3f}s")
    
    if total_startup < 5.0:
        print("✓ Startup time is excellent (< 5s)")
    elif total_startup < 10.0:
        print("✓ Startup time is good (< 10s)")
    elif total_startup < 15.0:
        print("⚠ Startup time is acceptable (< 15s)")
    else:
        print("✗ Startup time is slow (> 15s)")
        print("Consider implementing the optimization recommendations above")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
