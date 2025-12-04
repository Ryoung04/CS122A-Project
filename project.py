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
        password="Your Password Here",   # <-- change this
        database="cs122a_project"
    )

# ------------------------------------------------------------
# Function 1: Import Data
# ------------------------------------------------------------
def import_data(folder):
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
            ddl_text = ddl_file.read()
        for stmt in ddl_text.split(";"):
            if stmt.strip():
                cursor.execute(stmt + ";")

        # Load all CSV files
        for filename in os.listdir(folder):
            if filename.endswith(".csv"):
                table_name = filename[:-4]
                path = os.path.join(folder, filename)

                with open(path, "r") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        placeholders = ",".join(["%s"] * len(row))
                        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                        cursor.execute(sql, row)

        conn.commit()
        print("Success")

    except Exception as e:
        print("Fail")
    finally:
        cursor.close()
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
