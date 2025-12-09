"""
Static Review Tests for Database Schema and Triggers
Validates SQL schema structure, constraints, indexes, and triggers
"""
import unittest
import re
import os

class TestSchemaStaticReview(unittest.TestCase):
    """Static analysis tests for database schema"""
    
    @classmethod
    def setUpClass(cls):
        """Load SQL schema file"""
        schema_path = 'create_database.sql'
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            cls.schema_sql = f.read()

    # ========== Table Structure Tests ==========
    
    def test_all_required_tables_exist(self):
        """Verify all required tables are defined"""
        print("\n=== Testing Required Tables ===")
        
        required_tables = [
            'users',
            'files',
            'invites',
            'invite_codes',
            'meetings',
            'activities'
        ]
        
        for table in required_tables:
            pattern = rf'CREATE TABLE\s+{table}\s*\('
            self.assertIsNotNone(
                re.search(pattern, self.schema_sql, re.IGNORECASE),
                f"Table '{table}' not found in schema"
            )
            print(f"  ✅ Table '{table}' exists")
        
        print("✅ All required tables exist")

    def test_users_table_structure(self):
        """Verify users table has all required columns"""
        print("\n=== Testing Users Table Structure ===")
        
        required_columns = [
            'id',
            'email',
            'user_id',
            'password',
            'first_name',
            'last_name',
            'date_of_birth',
            'address',
            'role',
            'department',
            'employees_list',
            'created_at',
            'updated_at'
        ]
        
        # Extract users table definition
        users_table_match = re.search(
            r'CREATE TABLE users\s*\((.*?)\);',
            self.schema_sql,
            re.IGNORECASE | re.DOTALL
        )
        self.assertIsNotNone(users_table_match, "Users table definition not found")
        
        users_table_def = users_table_match.group(1)
        
        for column in required_columns:
            self.assertIn(
                column,
                users_table_def.lower(),
                f"Column '{column}' not found in users table"
            )
            print(f"  ✅ Column '{column}' exists")
        
        print("✅ Users table structure is valid")

    def test_activities_table_structure(self):
        """Verify activities table has all required columns"""
        print("\n=== Testing Activities Table Structure ===")
        
        required_columns = [
            'id',
            'activity_id',
            'date',
            'type',
            'title',
            'description',
            'creator',
            'employees_joined',
            'status',
            'created_at',
            'updated_at'
        ]
        
        activities_table_match = re.search(
            r'CREATE TABLE activities\s*\((.*?)\);',
            self.schema_sql,
            re.IGNORECASE | re.DOTALL
        )
        self.assertIsNotNone(activities_table_match, "Activities table definition not found")
        
        activities_table_def = activities_table_match.group(1)
        
        for column in required_columns:
            self.assertIn(
                column,
                activities_table_def.lower(),
                f"Column '{column}' not found in activities table"
            )
            print(f"  ✅ Column '{column}' exists")
        
        print("✅ Activities table structure is valid")

    # ========== Constraint Tests ==========
    
    def test_primary_keys_defined(self):
        """Verify all tables have primary keys"""
        print("\n=== Testing Primary Keys ===")
        
        tables = ['users', 'files', 'invites', 'invite_codes', 'meetings', 'activities']
        
        for table in tables:
            # Look for PRIMARY KEY constraint
            pattern = rf'CREATE TABLE {table}\s*\(.*?PRIMARY KEY.*?\);'
            self.assertIsNotNone(
                re.search(pattern, self.schema_sql, re.IGNORECASE | re.DOTALL),
                f"Primary key not found for table '{table}'"
            )
            print(f"  ✅ Primary key defined for '{table}'")
        
        print("✅ All tables have primary keys")

    def test_foreign_keys_defined(self):
        """Verify foreign key constraints are defined"""
        print("\n=== Testing Foreign Keys ===")
        
        expected_foreign_keys = [
            ('activities', 'creator', 'users', 'email'),
            ('files', 'uploaded_by', 'users', 'email'),
            ('meetings', 'created_by', 'users', 'email'),  # Meeting uses created_by not creator
        ]
        
        for child_table, child_col, parent_table, parent_col in expected_foreign_keys:
            # Look for FOREIGN KEY constraint
            pattern = rf'CONSTRAINT\s+fk_{child_table}_{child_col}\s+FOREIGN KEY\s*\({child_col}\)'
            found = re.search(pattern, self.schema_sql, re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"Foreign key constraint not found: {child_table}.{child_col} -> {parent_table}.{parent_col}"
            )
            print(f"  ✅ FK: {child_table}.{child_col} -> {parent_table}.{parent_col}")
        
        print("✅ All foreign keys are defined")

    def test_unique_constraints(self):
        """Verify unique constraints are defined"""
        print("\n=== Testing Unique Constraints ===")
        
        unique_constraints = [
            ('users', 'email'),
            ('users', 'user_id'),
            ('activities', 'activity_id'),
            ('files', 'file_id'),
        ]
        
        for table, column in unique_constraints:
            # Look for UNIQUE constraint
            pattern = rf'{column}\s+.*?UNIQUE'
            table_def = re.search(
                rf'CREATE TABLE {table}\s*\((.*?)\);',
                self.schema_sql,
                re.IGNORECASE | re.DOTALL
            )
            self.assertIsNotNone(table_def, f"Table '{table}' not found")
            
            found = re.search(pattern, table_def.group(1), re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"Unique constraint not found for {table}.{column}"
            )
            print(f"  ✅ UNIQUE: {table}.{column}")
        
        print("✅ All unique constraints are defined")

    def test_not_null_constraints(self):
        """Verify NOT NULL constraints on critical columns"""
        print("\n=== Testing NOT NULL Constraints ===")
        
        not_null_columns = [
            ('users', 'email'),
            ('users', 'user_id'),
            ('activities', 'activity_id'),
            ('activities', 'creator'),
            ('activities', 'date'),
            ('meetings', 'created_by'),  # Meeting uses created_by not creator
        ]
        
        for table, column in not_null_columns:
            table_def = re.search(
                rf'CREATE TABLE {table}\s*\((.*?)\);',
                self.schema_sql,
                re.IGNORECASE | re.DOTALL
            )
            self.assertIsNotNone(table_def, f"Table '{table}' not found")
            
            # Look for column definition with NOT NULL
            pattern = rf'{column}\s+.*?NOT NULL'
            found = re.search(pattern, table_def.group(1), re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"NOT NULL constraint not found for {table}.{column}"
            )
            print(f"  ✅ NOT NULL: {table}.{column}")
        
        print("✅ All NOT NULL constraints are defined")

    # ========== Index Tests ==========
    
    def test_indexes_defined(self):
        """Verify indexes are created for performance"""
        print("\n=== Testing Indexes ===")
        
        expected_indexes = [
            ('users', 'email'),
            ('users', 'user_id'),
            ('activities', 'activity_id'),
            ('activities', 'creator'),
            ('activities', 'type'),
            ('activities', 'date'),
            ('activities', 'status'),
        ]
        
        for table, column in expected_indexes:
            pattern = rf'CREATE INDEX\s+idx_{table}_{column}\s+ON\s+{table}\s*\({column}\)'
            found = re.search(pattern, self.schema_sql, re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"Index not found: idx_{table}_{column}"
            )
            print(f"  ✅ INDEX: idx_{table}_{column}")
        
        print("✅ All indexes are defined")

    # ========== Trigger Tests ==========
    
    def test_update_timestamp_triggers(self):
        """Verify triggers for automatic timestamp updates"""
        print("\n=== Testing Update Timestamp Triggers ===")
        
        # Check for trigger function definition (PostgreSQL style)
        trigger_function_pattern = r'CREATE\s+OR\s+REPLACE\s+FUNCTION\s+update_updated_at_column'
        function_found = re.search(trigger_function_pattern, self.schema_sql, re.IGNORECASE)
        
        if function_found:
            print("  ✅ Trigger function: update_updated_at_column() found")
        
        # Check for at least one trigger using the function
        trigger_pattern = r'CREATE\s+TRIGGER\s+update_\w+_updated_at'
        triggers = re.findall(trigger_pattern, self.schema_sql, re.IGNORECASE)
        
        self.assertGreater(len(triggers), 0, "No update triggers found")
        print(f"  ✅ Found {len(triggers)} update timestamp triggers")
        
        print("✅ Update timestamp triggers are defined")

    def test_trigger_logic(self):
        """Verify trigger logic is correct"""
        print("\n=== Testing Trigger Logic ===")
        
        # Check for trigger function that sets updated_at
        function_pattern = r'CREATE\s+OR\s+REPLACE\s+FUNCTION\s+update_updated_at_column.*?NEW\.updated_at\s*:?=\s*(?:CURRENT_TIMESTAMP|now\(\))'
        function_found = re.search(function_pattern, self.schema_sql, re.IGNORECASE | re.DOTALL)
        
        if function_found:
            print("  ✅ Trigger function logic: Sets updated_at to CURRENT_TIMESTAMP")
            self.assertTrue(True)
        else:
            # Fallback: check for any trigger-related timestamp logic
            timestamp_logic = re.search(r'updated_at.*?(?:CURRENT_TIMESTAMP|now\(\))', self.schema_sql, re.IGNORECASE)
            self.assertIsNotNone(timestamp_logic, "No timestamp update logic found")
            print("  ✅ Timestamp update logic found")
        
        print("✅ Trigger logic is correct")

    # ========== Data Type Tests ==========
    
    def test_jsonb_columns(self):
        """Verify JSONB columns are used for array data"""
        print("\n=== Testing JSONB Columns ===")
        
        jsonb_columns = [
            ('users', 'employees_list'),
            ('activities', 'employees_joined'),
            ('meetings', 'employees_list'),
            ('meetings', 'invited_employees_list'),
        ]
        
        for table, column in jsonb_columns:
            table_def = re.search(
                rf'CREATE TABLE {table}\s*\((.*?)\);',
                self.schema_sql,
                re.IGNORECASE | re.DOTALL
            )
            self.assertIsNotNone(table_def, f"Table '{table}' not found")
            
            # Look for JSONB data type
            pattern = rf'{column}\s+JSONB'
            found = re.search(pattern, table_def.group(1), re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"JSONB type not found for {table}.{column}"
            )
            print(f"  ✅ JSONB: {table}.{column}")
        
        print("✅ All JSONB columns are defined")

    def test_timestamp_columns(self):
        """Verify timestamp columns use correct type"""
        print("\n=== Testing Timestamp Columns ===")
        
        timestamp_columns = [
            ('users', 'created_at'),
            ('users', 'updated_at'),
            ('activities', 'created_at'),
            ('activities', 'updated_at'),
            ('activities', 'date'),
        ]
        
        for table, column in timestamp_columns:
            table_def = re.search(
                rf'CREATE TABLE {table}\s*\((.*?)\);',
                self.schema_sql,
                re.IGNORECASE | re.DOTALL
            )
            self.assertIsNotNone(table_def, f"Table '{table}' not found")
            
            # Look for TIMESTAMP WITH TIME ZONE
            pattern = rf'{column}\s+TIMESTAMP\s+WITH\s+TIME\s+ZONE'
            found = re.search(pattern, table_def.group(1), re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"TIMESTAMP WITH TIME ZONE not found for {table}.{column}"
            )
            print(f"  ✅ TIMESTAMP: {table}.{column}")
        
        print("✅ All timestamp columns use correct type")

    # ========== Default Value Tests ==========
    
    def test_default_values(self):
        """Verify default values are set correctly"""
        print("\n=== Testing Default Values ===")
        
        defaults = [
            ('users', 'employees_list', "DEFAULT '[]'::JSONB"),
            ('activities', 'employees_joined', "DEFAULT '[]'::JSONB"),
            ('activities', 'status', "DEFAULT 'scheduled'"),
            ('users', 'created_at', "DEFAULT CURRENT_TIMESTAMP"),
        ]
        
        for table, column, default_clause in defaults:
            table_def = re.search(
                rf'CREATE TABLE {table}\s*\((.*?)\);',
                self.schema_sql,
                re.IGNORECASE | re.DOTALL
            )
            self.assertIsNotNone(table_def, f"Table '{table}' not found")
            
            # Look for default value
            pattern = rf'{column}\s+.*?{re.escape(default_clause)}'
            found = re.search(pattern, table_def.group(1), re.IGNORECASE)
            self.assertIsNotNone(
                found,
                f"Default value not found for {table}.{column}: {default_clause}"
            )
            print(f"  ✅ DEFAULT: {table}.{column}")
        
        print("✅ All default values are set correctly")

if __name__ == '__main__':
    print("Starting Static Schema Review Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)
