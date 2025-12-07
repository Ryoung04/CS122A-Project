import sys
import os
import csv
import mysql.connector

# ------------------------------------------------------------
# Database Connection Helper
# ------------------------------------------------------------

#use when submitting

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="test",
        password="password",
        database="cs122a_project",
        allow_local_infile=True
    )
"""

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="password", #Change this for ur own device
        database="cs122a_project",
        allow_local_infile=True
    )
"""
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
                            print(row)
                            print(table_name)
                            placeholders = ",".join(["%s"] * len(row))
                            sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                            print(sql)
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

#Function 2: Inseret Agent Client

#NOTE FROM EDWARD:
#TO CHECK ERRORS FROM SQL - PRINT E WHEN ERROR OCCURS!

def insert_ac(values):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()

        #first gotta insert as a user
        user_ph = ",".join(["%s"] * len(values[:3]))
        user_sql = f"INSERT INTO User VALUES ({user_ph})"
        cursor.execute(user_sql, values[:3])
        #then we can insert as AC
        placeholders = ",".join(["%s"] * (len(values[3:]) + 1))
        sql = f"INSERT INTO AgentClient VALUES ({placeholders})"
        user_val = values[0:1] + values[3:]
        cursor.execute(sql, user_val)
        
        conn.commit()

        print("Success")
    except mysql.connector.Error as e:
        print("Fail")
        if conn:
            conn.rollback()  
    except Exception as e:
        print("Fail")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_customized_model(values):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()

        placeholders = ",".join(["%s"] * len(values))
        sql = f"INSERT INTO CustomizedModel VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()
        print("Success")
    except mysql.connector.Error as e:
        print("Fail")
        if conn:
            conn.rollback()  
    except Exception as e:
        print(f"Fail: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#Functino to delete basemodels 9BM

def delete_BM(value):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()

        sql = "DELETE FROM BaseModel WHERE BMID = (%s)"
        cursor.execute(sql, (value,))
        conn.commit()
        print("Success")
    except mysql.connector.Error as e:
        print("Fail")
        if conn:
            conn.rollback()  
    except Exception as e:
        print("Fail")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def listIS(value):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()

        sql = "SELECT S.sid, S.provider, S.endpoint From InternetService AS S JOIN Utilize U ON U.sid = S.sid WHERE U.bmid = (%s) ORDER BY S.provider ASC"
        print(sql)
        cursor.execute(sql, (value,))
        results = cursor.fetchall()
        
        for record in results:
            output_line = ",".join(map(str, record))
            print(output_line)

    except mysql.connector.Error as e:
        print(f"Fail {e}")
        if conn:
            conn.rollback()  
    except Exception as e:
        print("Fail")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def countCM(values):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()

        placeholders = placeholders = ",".join(["%s"] * len(values))

        sql = f"SELECT BM.bmid, BM.description, COUNT(CM.mid) FROM BaseModel AS BM LEFT JOIN CustomizedModel AS CM ON BM.bmid = CM.bmid WHERE BM.bmid IN ({placeholders}) GROUP BY BM.bmid, BM.description ORDER BY BM.bmid ASC"
        cursor.execute(sql, values)
        results = cursor.fetchall()
        
        for record in results:
            output_line = ",".join(map(str, record))
            print(output_line)

    except mysql.connector.Error as e:
        print(f"Fail {e}")
        if conn:
            conn.rollback()  
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
    if len(sys.argv) < 3:
        print("Fail")
        return

    cmd = sys.argv[1]

    if cmd == "import":
        folder = sys.argv[2]
        import_data(folder)
    elif cmd == "insertAgentClient":
        values = sys.argv[2:]
        insert_ac(values)
    elif cmd == "addCustomizedModel":
        values = sys.argv[2:]
        add_customized_model(values)
    elif cmd == "deleteBaseModel":
        value = sys.argv[2]
        delete_BM(value)
    elif cmd == "listInternetService":
        value = sys.argv[2]
        listIS(value)
    elif cmd == "countCustomizedModel":
        values = sys.argv[2:]
        countCM(values)
    else:
        print("Fail")

if __name__ == "__main__":
    main()
