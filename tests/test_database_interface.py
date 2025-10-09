#!/usr/bin/env python3
"""
Test Database Interface Implementation
Tests both TextDatabase and interface compliance
"""

import sys
import os
from pathlib import Path
import tempfile
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.interface import DatabaseInterface, get_database, UserRole
from database.text_db import TextDatabase


class TestDatabaseInterface:
    """Test suite for database interface implementations"""
    
    def __init__(self):
        """Initialize test environment"""
        self.test_data_dir = None
        self.database = None
        
    def setup_test_data(self):
        """Create temporary test data directory and files"""
        self.test_data_dir = tempfile.mkdtemp()
        tables_dir = os.path.join(self.test_data_dir, 'txt_tables')
        os.makedirs(tables_dir, exist_ok=True)
        
        # Create test data files
        test_data = {
            'users.txt': [
                'user_id|password|role|name|school_id|reports_to',
                'U001|pass123|R|Test Resident|SCH001|DM001',
                'DM001|pass456|DM|Test Manager||RM001',
                'RM001|pass789|RM|Regional Manager||',
                'HO001|passabc|HO|Head Office||'
            ],
            'timetables.txt': [
                'school_id|class|section|period_number|time_slot|subject|is_pe_period',
                'SCH001|V|A|1|9:00-10:00|Math|false',
                'SCH001|V|A|2|10:00-11:00|PE|true',
                'SCH001|V|B|1|9:00-10:00|Science|false'
            ],
            'lesson_plans.txt': [
                'lesson_plan_id|school_id|session|lessons',
                'LP001|SCH001|2024-25|L001,L002',
                'LP002|SCH001|2024-25|L003'
            ],
            'lessons.txt': [
                'lesson_id|name|description|duration|required_props',
                'L001|Basic Football|Introduction to football|60|football,cones',
                'L002|Basketball Drills|Basic basketball skills|45|basketball',
                'L003|Athletics|Running and jumping|30|stopwatch'
            ],
            'props.txt': [
                'prop_id|type|school_id|quantity|available|status',
                'P001|football|SCH001|10|8|good',
                'P002|basketball|SCH001|5|5|excellent',
                'P003|cones|SCH001|20|18|fair'
            ]
        }
        
        # Write test data files
        for filename, lines in test_data.items():
            with open(os.path.join(tables_dir, filename), 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
        
        print(f"[OK] Test data created in: {tables_dir}")
        return tables_dir
    
    def test_database_factory(self):
        """Test database factory function"""
        print("[TEST] Testing database factory...")
        
        # Test text database (default)
        os.environ['DB_TYPE'] = 'text'
        db = get_database()
        assert isinstance(db, TextDatabase), "Should return TextDatabase instance"
        
        # Test invalid type
        os.environ['DB_TYPE'] = 'invalid'
        try:
            db = get_database()
            assert False, "Should raise ValueError for invalid DB_TYPE"
        except ValueError:
            pass  # Expected
        
        print("[OK] Database factory tests passed")
    
    def test_interface_compliance(self):
        """Test that TextDatabase implements all interface methods"""
        print("[TEST] Testing interface compliance...")
        
        # Temporarily override data directory
        original_init = TextDatabase.__init__
        test_tables_dir = self.setup_test_data()
        
        def patched_init(self):
            self.data_dir = test_tables_dir
            self.lesson_completions = []
            self.prop_updates = []
            self.vector_store = None  # Skip vector store for tests
            
        TextDatabase.__init__ = patched_init
        
        try:
            db = TextDatabase()
            
            # Test all interface methods exist and are callable
            interface_methods = [
                'get_user', 'authenticate_user', 'get_timetable', 
                'get_lesson_plans', 'get_lessons', 'get_props', 
                'get_events', 'log_lesson_completion', 'update_prop_status',
                'get_residents_under_manager', 'semantic_search', 'refresh_vector_cache'
            ]
            
            for method_name in interface_methods:
                assert hasattr(db, method_name), f"Missing method: {method_name}"
                assert callable(getattr(db, method_name)), f"Method not callable: {method_name}"
            
            print("[OK] All interface methods present and callable")
            self.database = db
            
        finally:
            # Restore original init
            TextDatabase.__init__ = original_init
    
    def test_user_operations(self):
        """Test user-related operations"""
        print("[TEST] Testing user operations...")
        
        if not self.database:
            print("[FAIL] Database not initialized for testing")
            return
        
        # Test get_user
        user = self.database.get_user('U001')
        assert user is not None, "Should find test user"
        assert user['name'] == 'Test Resident', "Should return correct user data"
        assert user['role'] == 'R', "Should return correct role"
        
        # Test authenticate_user (simplified for text db)
        auth_user = self.database.authenticate_user('U001', 'any_password')
        assert auth_user is not None, "Text DB should authenticate any password"
        
        # Test non-existent user
        no_user = self.database.get_user('INVALID')
        assert no_user is None, "Should return None for non-existent user"
        
        print("[OK] User operations tests passed")
    
    def test_timetable_operations(self):
        """Test timetable operations"""
        print("[TEST] Testing timetable operations...")
        
        if not self.database:
            print("[FAIL] Database not initialized for testing")
            return
        
        # Test get all timetables for school
        timetables = self.database.get_timetable('SCH001')
        assert len(timetables) >= 2, "Should return multiple timetable entries"
        
        # Test filtered by class
        class_timetables = self.database.get_timetable('SCH001', class_name='V')
        assert len(class_timetables) >= 2, "Should return class V timetables"
        
        # Test filtered by class and section
        section_timetables = self.database.get_timetable('SCH001', class_name='V', section='A')
        assert len(section_timetables) == 2, "Should return exactly 2 entries for V-A"
        
        # Check PE period detection
        pe_periods = [tt for tt in section_timetables if tt.get('is_pe_period')]
        assert len(pe_periods) == 1, "Should find exactly one PE period"
        
        print("[OK] Timetable operations tests passed")
    
    def test_lesson_operations(self):
        """Test lesson and lesson plan operations"""
        print("[TEST] Testing lesson operations...")
        
        if not self.database:
            print("[FAIL] Database not initialized for testing")
            return
        
        # Test get lesson plans
        lesson_plans = self.database.get_lesson_plans('SCH001')
        assert len(lesson_plans) >= 2, "Should return multiple lesson plans"
        
        # Test get lessons with lesson_plan_id
        lessons = self.database.get_lessons('LP001')
        assert len(lessons) >= 2, "Should return lessons for LP001"
        
        # Test get all lessons (no lesson_plan_id)
        all_lessons = self.database.get_lessons()
        assert len(all_lessons) >= 3, "Should return all lessons"
        
        # Test lesson completion logging
        completion_data = {
            'school_id': 'SCH001',
            'class': 'V',
            'section': 'A',
            'period_number': 2,
            'lesson_id': 'L001',
            'resident_id': 'U001',
            'completion_status': 'completed',
            'notes': 'Test completion'
        }
        
        result = self.database.log_lesson_completion(completion_data)
        assert result is True, "Should successfully log lesson completion"
        assert len(self.database.lesson_completions) >= 1, "Should store completion data"
        
        print("[OK] Lesson operations tests passed")
    
    def test_props_operations(self):
        """Test props operations"""
        print("[TEST] Testing props operations...")
        
        if not self.database:
            print("[FAIL] Database not initialized for testing")
            return
        
        # Test get props for school
        props = self.database.get_props('SCH001')
        assert len(props) >= 3, "Should return multiple props"
        
        # Test get all props
        all_props = self.database.get_props()
        assert len(all_props) >= 3, "Should return all props"
        
        # Test prop status update
        result = self.database.update_prop_status('P001', 'maintenance', 'U001')
        assert result is True, "Should successfully update prop status"
        assert len(self.database.prop_updates) >= 1, "Should store update data"
        
        print("[OK] Props operations tests passed")
    
    def test_management_operations(self):
        """Test management operations"""
        print("[TEST] Testing management operations...")
        
        if not self.database:
            print("[FAIL] Database not initialized for testing")
            return
        
        # Test get residents under manager
        residents = self.database.get_residents_under_manager('DM001')
        assert len(residents) >= 1, "Should find residents under DM001"
        
        resident = residents[0]
        assert resident['role'] == 'R', "Should return resident role"
        assert resident['reports_to'] == 'DM001', "Should report to correct manager"
        
        print("[OK] Management operations tests passed")
    
    def test_vector_operations(self):
        """Test vector store operations (with graceful degradation)"""
        print("[TEST] Testing vector operations...")
        
        if not self.database:
            print("[FAIL] Database not initialized for testing")
            return
        
        # Test semantic search (should gracefully handle missing vector store)
        result = self.database.semantic_search("football training")
        assert isinstance(result, str), "Should return string result"
        
        # Test refresh vector cache
        refresh_result = self.database.refresh_vector_cache()
        # Should return False since vector store is disabled for tests
        assert refresh_result is False, "Should return False when vector store disabled"
        
        print("[OK] Vector operations tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("[START] Starting Database Interface Tests\n")
        
        try:
            self.test_database_factory()
            self.test_interface_compliance()
            self.test_user_operations()
            self.test_timetable_operations()
            self.test_lesson_operations()
            self.test_props_operations()
            self.test_management_operations()
            self.test_vector_operations()
            
            print("\n[SUCCESS] All database interface tests passed!")
            return True
            
        except Exception as e:
            print(f"\n[FAIL] Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Cleanup
            if self.test_data_dir:
                import shutil
                shutil.rmtree(self.test_data_dir)
                print(f"[CLEANUP] Cleaned up test data: {self.test_data_dir}")


def test_database_consistency():
    """Test that both database implementations are consistent"""
    print("[CONSISTENCY] Testing database implementation consistency...")
    
    # Test method signatures match
    from database.interface import DatabaseInterface
    from database.text_db import TextDatabase
    
    # Get interface methods
    interface_methods = [method for method in dir(DatabaseInterface) 
                        if not method.startswith('_') and callable(getattr(DatabaseInterface, method, None))]
    
    # Get TextDatabase methods
    text_db_methods = [method for method in dir(TextDatabase) 
                      if not method.startswith('_') and callable(getattr(TextDatabase, method, None))]
    
    # Check all interface methods are implemented
    missing_methods = []
    for method in interface_methods:
        if method not in text_db_methods:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"[ERROR] TextDatabase missing methods: {missing_methods}")
        return False
    else:
        print("[OK] All interface methods implemented in TextDatabase")
    
    print("[OK] Database consistency tests passed")
    return True


if __name__ == "__main__":
    print("[TEST] SportzVillage Database Interface Test Suite\n")
    
    # Run consistency tests
    consistency_ok = test_database_consistency()
    
    if consistency_ok:
        # Run full test suite
        test_suite = TestDatabaseInterface()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n[SUCCESS] All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n[FAILED] Some tests failed!")
            sys.exit(1)
    else:
        print("\n[FAILED] Consistency tests failed!")
        sys.exit(1)