import sys
import os
import csv
import mysql.connector

# ------------------------------------------------------------
# Database Connection Helper
# ------------------------------------------------------------
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="143Rjma!",   # <-- change this
        database="cs122a_project",
        allow_local_infile=True
    )

# ------------------------------------------------------------
# Function 1: Import Data
# ------------------------------------------------------------
def import_data(folder):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Drop tables in correct foreign-key order
        drop_order = [
            "Configuration_Uses_CustomizedModel",
            "Utilize",
            "LLMService",
            "DataStorageService",
            "InternetService",
            "Configuration",
            "CustomizedModel",
            "BaseModel",
            "AgentClient",
            "AgentCreator",
            "User"
        ]
        for table in drop_order:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")

        # Recreate tables by reading ddl.sql
        with open("ddl.sql", "r") as ddl_file:
            sql_content = ddl_file.read()
        
        # Remove comment lines
        lines = sql_content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that are pure comments or empty
            stripped = line.strip()
            if stripped and not stripped.startswith('--'):
                cleaned_lines.append(line)
        
        cleaned_sql = '\n'.join(cleaned_lines)
        
        # Split by semicolon and execute each statement
        statements = cleaned_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            # Skip empty, USE, and DROP statements
            if stmt and not stmt.upper().startswith('USE') and not stmt.upper().startswith('DROP'):
                cursor.execute(stmt)

        # Load CSV files in correct foreign-key order
        load_order = [
            "User",
            "AgentCreator",
            "AgentClient",
            "BaseModel",
            "CustomizedModel",
            "Configuration",
            "InternetService",
            "LLMService",
            "DataStorageService",
            "Utilize",
            "Configuration_Uses_CustomizedModel"
        ]
        
        for table_name in load_order:
            csv_path = os.path.join(folder, f"{table_name}.csv")
            if os.path.exists(csv_path):
                with open(csv_path, "r") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:  # Skip empty rows
                            placeholders = ",".join(["%s"] * len(row))
                            sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                            cursor.execute(sql, row)

        conn.commit()
        print("Success")

    except Exception as e:
        print("Fail")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ------------------------------------------------------------
# MAIN ROUTER
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Fail")
        return

    cmd = sys.argv[1]

    if cmd == "import":
        folder = sys.argv[2]
        import_data(folder)
    else:
        print("Fail")

if __name__ == "__main__":
    main()
