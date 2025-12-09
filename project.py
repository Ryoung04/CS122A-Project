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
        database="cs122a",
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
#  Import Data 
def import_data(folder):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        drop_order = [
            "Configuration_Uses_CustomizedModel", "Utilize", "LLMService", "DataStorageService", 
            "InternetService", "Configuration", "CustomizedModel", "BaseModel", 
            "AgentClient", "AgentCreator", "User"
        ]
        for table in drop_order:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        with open("ddl.sql", "r") as ddl_file:
            sql_content = ddl_file.read()
        
        # DDL parsing (kept for completeness)
        lines = sql_content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('--'):
                cleaned_lines.append(line)
        cleaned_sql = '\n'.join(cleaned_lines)
        
        statements = cleaned_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.upper().startswith('USE') and not stmt.upper().startswith('DROP'):
                cursor.execute(stmt)

        # Load CSV
        load_order = [
            "User", "AgentCreator", "AgentClient", "BaseModel", "CustomizedModel", 
            "Configuration", "InternetService", "LLMService", "DataStorageService", 
            "Utilize", "Configuration_Uses_CustomizedModel"
        ]
        
        for table_name in load_order:
            csv_path = os.path.join(folder, f"{table_name}.csv")
            if os.path.exists(csv_path):
                with open(csv_path, "r") as f:
                    reader = csv.reader(f)
                    
                    header = next(reader) # Skip header
                    
                    for row in reader:
                        if not row:
                            continue
                        # --- AgentClient Transformation ---
                        if table_name == "AgentClient":
                            # Existing logic to reorder and format AgentClient data
                            try:
                                csv_uid = row[0]
                                csv_interests = row[1]
                                csv_cardholder = row[2]
                                csv_expire = row[3]
                                csv_cardno = row[4]
                                csv_cvv = row[5]
                                csv_zip = row[6]
                                month_year = f"{csv_expire[5:7]}/{csv_expire[2:4]}"
                                padded_cardno = str(csv_cardno).zfill(16)
                                padded_cvv = str(csv_cvv).zfill(4)
                                row = [
                                    csv_uid, padded_cardno, csv_cardholder, 
                                    month_year, padded_cvv, csv_zip, csv_interests
                                ]
                            except IndexError as ie:
                                print(f"Fail: Missing data in AgentClient row: {row}")
                                raise ie 
                        
                        # --- BaseModel Transformation ---
                        elif table_name == "BaseModel":
                            # Logic to truncate and reorder BaseModel data
                            try:
                                csv_bmid = row[0]
                                csv_creator_uid = row[1]
                                csv_description = row[2]
                                # DDL Order: [bmid, description, creator_uid]
                                row = [csv_bmid, csv_description, csv_creator_uid]
                            except IndexError as ie:
                                print(f"Fail: Missing data in BaseModel row: {row}")
                                raise ie

                        # --- Configuration Transformation (NEW FIX) ---
                        elif table_name == "Configuration":
                            # DDL Order (inferred): [cid, content, labels, client_uid]
                            # CSV Order: [cid, client_uid, content, labels]
                            try:
                                # Extract fields
                                csv_cid = row[0]
                                csv_client_uid = row[1]
                                csv_content = row[2]
                                csv_labels = row[3]
                                
                                # Reorder to DDL: [cid, content, labels, client_uid]
                                row = [csv_cid, csv_content, csv_labels, csv_client_uid]
                            except IndexError as ie:
                                # This handles case where Configuration.csv has less than 4 fields
                                print(f"Fail: Missing data in Configuration row: {row}")
                                raise ie
                            
                        # --- Insertion Logic with Debugging ---
                        try:
                            placeholders = ",".join(["%s"] * len(row))
                            sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                            cursor.execute(sql, row)
                        except Exception as insert_e:
                            # Debugging print statement
                            print(f"!!! INSERTION FAILURE !!! Table: {table_name}, Data Fields: {len(row)}, Row Content: {row}")
                            raise insert_e
                        # --- End Insertion Logic ---

        conn.commit()
        print("Success")

    except Exception as e:
        print("Fail")
        print(f"Error Details: {e}") 
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
#Function 2: Inseret Agent Client

#NOTE FROM EDWARD:
#TO CHECK ERRORS FROM SQL - PRINT E WHEN ERROR OCCURS!
def get_user_insert_sql():
    return "INSERT INTO User (uid, email, username) VALUES (%s, %s, %s)"

def get_ac_insert_sql():
    return (
        "INSERT INTO AgentClient "
        "(uid, card_number, card_holder_name, expiration_date, cvv, zip, interests) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
def insert_ac(values):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()
        #move things from one value to a dedicated nnumber 
        uid = int(values[0])
        username = values[1]
        email = values[2]
        cardnum = values[3]
        card_holder = values[4]
        expirationdate = values[5]
        ccv_num = values[6]
        zipcode = int(values[7])
        interests = values[8]

        cardnumber = str(cardnum).zfill(16)
        cvvnumber = str(ccv_num).zfill(4)
        year, month, _ = expirationdate.split('-')
        month_year = f"{month}/{year[2:]}"
        cursor.execute(
            get_user_insert_sql(),
            (uid, email, username)
        )
        #now for agent client: 
        cursor.execute(
            get_ac_insert_sql(),
            (uid, cardnumber, card_holder, month_year, cvvnumber, zipcode, interests)
        )
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
        print(f"Fail")
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
        cursor.execute(sql, (int(value),))
        if cursor.rowcount >0:
            conn.commit()
            print("Success")
        else: 
            print("Fail")
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
        bmid = int(value)
        sql = "SELECT S.sid, S.provider, S.endpoint From InternetService AS S JOIN Utilize U ON U.sid = S.sid WHERE U.bmid = (%s) ORDER BY S.provider ASC"
        cursor.execute(sql, (value,))
        results = cursor.fetchall()
        
        for record in results:
            output_line = ",".join(map(str, record))
            print(output_line)

    except mysql.connector.Error as e:
        print(f"Fail")
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
        print(f"Fail")
        if conn:
            conn.rollback()  
    except Exception as e:
        print("Fail")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
#now for part 7 
def topNdurationconfig(values):
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()
        uid = int(values[0])
        N= int(values[1])
        
        sql = """
            SELECT
                C.client_uid AS uid,
                C.cid,
                C.labels AS label,
                C.content,
                SUM(CUCM.usage_minutes) AS total_duration
            FROM Configuration AS C
            JOIN Configuration_Uses_CustomizedModel AS CUCM ON C.cid = CUCM.cid
            WHERE C.client_uid = %s
            GROUP BY C.client_uid, C.cid, C.labels, C.content
            ORDER BY total_duration DESC
            LIMIT %s;
        """        
        cursor.execute(sql,(uid, N))
        results = cursor.fetchall()

        for record in results:
            # Output will be uid,cid,label,content,duration
            output_line = ",".join(map(str, record))
            print(output_line)

    except mysql.connector.Error as e:
         print("Fail") #trouble shoot
    except Exception as e:
         print("Fail") #trouble shoot
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
#part 8 Keyword search List 5 base models that are utilizing
#def listBaseModelKeyWords(keyword_value):

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
        bmid_values = sys.argv[2:] 
        countCM(bmid_values)
    elif cmd == "topNdurationconfig": 
        topNdurationconfig(values)
    else:
        print("Fail")

if __name__ == "__main__":
    main()
