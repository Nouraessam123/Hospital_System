import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import pyodbc
from datetime import datetime

conn =pyodbc.connect(

    'DRIVER={ODBC Driver 17 for SQL SERVER};'
    'SERVER=.;'
    'DataBase=Hospital3;'
    'Trusted_Connection=yes;'
)
cursor=conn.cursor()
import streamlit as st
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

class Patients:
    def __init__(self):
        """Establish connection with SQL Server."""
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL SERVER};'
            'SERVER=.;'
            'DATABASE=Hospital3;'
            'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Create the Patients table if it doesn't exist."""
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Patients' AND xtype='U')
        CREATE TABLE Patients (
            National_ID NVARCHAR(14) PRIMARY KEY,
            Name NVARCHAR(100),
            Age INT,
            Gender NVARCHAR(10),
            Contact NVARCHAR(20),
            Medical_History NVARCHAR(MAX),
            BMI FLOAT,
            Blood_Pressure NVARCHAR(20),
            Sugar_Level FLOAT
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add_patient(self, national_id, name, age, gender, contact, medical_history, bmi=None, bp=None, sugar=None):
        """Add a new patient to the database."""
        query = """
        INSERT INTO Patients (National_ID, Name, Age, Gender, Contact, Medical_History, BMI, Blood_Pressure, Sugar_Level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, (national_id, name, age, gender, contact, medical_history, bmi, bp, sugar))
        self.conn.commit()
        st.success(f"Patient {name} with National ID {national_id} added successfully!")

    def get_patient_by_id(self, national_id):
        """Retrieve a patient by their National ID."""
        query = "SELECT * FROM Patients WHERE National_ID = ?;"
        self.cursor.execute(query, (national_id,))
        row = self.cursor.fetchone()
        if row:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, row))
        else:
            st.warning("No patient found with the given National ID.")
            return None

    def update_patient(self, national_id, **updates):
        """Update patient details dynamically."""
        if updates:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [national_id]
            query = f"UPDATE Patients SET {set_clause} WHERE National_ID = ?;"
            self.cursor.execute(query, values)
            self.conn.commit()
        else:
            st.warning("No updates provided.")

    def delete_patient(self, national_id):
        """Delete a patient by their National ID."""
        query = "DELETE FROM Patients WHERE National_ID = ?;"
        self.cursor.execute(query, (national_id,))
        self.conn.commit()
        st.success(f"Patient with National ID {national_id} removed successfully!")

    def search_patients(self, search_term):
        """Search for patients by name, contact number, or National ID."""
        query = """
            SELECT * FROM Patients
            WHERE Name LIKE ?
            OR Contact LIKE ?
            OR National_ID LIKE ?;
        """
        # Execute the query with the search term for all three fields
        self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return None  # Return None if no results are found
    def view_patients(self):
        """View all patients."""
        query = "SELECT * FROM Patients;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            
            # Use st.dataframe for a wider and more flexible table
            st.dataframe(
                results,
                use_container_width=True,  # Make the table use the full container width
                height=400,  # Set a fixed height for the table (optional)
                column_config={
                    "National_ID": "National ID",
                    "Name": "Name",
                    "Age": "Age",
                    "Gender": "Gender",
                    "Contact": "Contact",
                    "Medical_History": "Medical History",
                    "BMI": "BMI",
                    "Blood_Pressure": "Blood Pressure",
                    "Sugar_Level": "Sugar Level"
                }
            )
        else:
            st.warning("No patients found.")
    def patients_info(self):
        """Visualize patient data."""
        df = pd.read_sql("SELECT * FROM Patients", self.conn)

        if df.empty or 'Age' not in df.columns:
            st.warning("No data available to plot.")
            return

        st.header("Patient Data Visualization")

        # Age Distribution
        st.subheader("Patient Age Distribution")
        fig, ax = plt.subplots()
        ax.hist(df['Age'].dropna(), bins=10, color='skyblue', edgecolor='black')
        ax.set_xlabel("Age")
        ax.set_ylabel("Number of Patients")
        st.pyplot(fig)

        # Gender Distribution
        st.subheader("Patient Gender Distribution")
        fig, ax = plt.subplots()
        gender_counts = df['Gender'].value_counts()
        sns.barplot(x=gender_counts.index, y=gender_counts.values, palette='Set2', ax=ax)
        ax.set_xlabel("Gender")
        ax.set_ylabel("Number of Patients")
        st.pyplot(fig)

        # BMI vs Age
        if 'BMI' in df.columns:
            st.subheader("BMI vs Age")
            fig, ax = plt.subplots()
            sns.scatterplot(data=df, x='Age', y='BMI', hue='Gender', palette='Set1', ax=ax)
            ax.set_xlabel("Age")
            ax.set_ylabel("BMI")
            st.pyplot(fig)

        # Sugar Level Distribution
        if 'Sugar_Level' in df.columns and not df['Sugar_Level'].isnull().all():
            st.subheader("Sugar Level Distribution")
            fig, ax = plt.subplots()
            sns.histplot(df['Sugar_Level'].dropna(), kde=True, color='green', ax=ax)
            ax.set_xlabel("Sugar Level")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
    def get_patient_name_by_id(self, national_id):
        """
        Fetch a patient's name by their National ID.
        """
        query = "SELECT Name FROM Patients WHERE National_ID = ?;"
        self.cursor.execute(query, (national_id,))
        row = self.cursor.fetchone()
        return row[0] if row else "Unknown Patient"
    def close_connection(self):
        """Close the database connection."""
        self.cursor.close()
        self.conn.close()   
class Departments:
    def __init__(self):
        """Establish connection with SQL Server."""
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL SERVER};'
            'SERVER=.;'
            'DATABASE=Hospital3;'
            'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Create the Departments table if it doesn't exist."""
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Departments' AND xtype='U')
        CREATE TABLE Departments (
            Department_ID INT PRIMARY KEY IDENTITY(1,1),
            Name NVARCHAR(100)
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add_department(self, name):
        """Add a new department to the database."""
        query = """
        INSERT INTO Departments (Name)
        VALUES (?);
        """
        self.cursor.execute(query, (name,))
        self.conn.commit()
        st.success(f"Department {name} added successfully.")

    def get_department_by_id(self, department_id):
        """Retrieve a department by its ID."""
        query = "SELECT * FROM Departments WHERE Department_ID = ?;"
        self.cursor.execute(query, (department_id,))
        row = self.cursor.fetchone()
        if row:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, row))
        else:
            st.warning("No department found with the given ID.")
            return None

    def search_Departments(self, search_term):
        """Search for Departments by name."""
        query = """
        SELECT * FROM Departments
        WHERE Name LIKE ?;
        """
        self.cursor.execute(query, (f"%{search_term}%",))
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results  # Return the results instead of displaying them here
        else:
            return None  # Return None if no results are found

    def update_department(self, department_id, **updates):
        """Update department details."""
        if not updates:
            st.warning("No updates provided.")
            return

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE Departments SET {set_clause} WHERE Department_ID = ?;"
        values = list(updates.values()) + [department_id]

        self.cursor.execute(query, values)
        self.conn.commit()
        st.success(f"Department {department_id} updated successfully!")

    def delete_department(self, department_id):
        """Delete a department by its ID."""
        query = "DELETE FROM Departments WHERE Department_ID = ?;"
        self.cursor.execute(query, (department_id,))
        self.conn.commit()
        st.success(f"Department {department_id} removed successfully!")

    def view_Departments(self):
        """View all Departments."""
        query = "SELECT * FROM Departments;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            st.table(results)  # Display results in a table
        else:
            st.warning("No Departments found.")
    def view_Departments_List(self):
        """Fetch and return all departments from the database."""
        query = "SELECT Department_ID, Name FROM Departments"
        self.cursor.execute(query)
        departments = self.cursor.fetchall()

        # Convert the result into a list of dictionaries for easier use
        department_list = []
        for dept in departments:
            department_list.append({
                "Department_ID": dept[0],  # Department ID
                "Name": dept[1]            # Department Name
            })

        return department_list

    def department_stats(self):
        """Visualize department count."""
        query = "SELECT Name, COUNT(*) as Count FROM Departments GROUP BY Name;"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        if data:
            labels, sizes = zip(*data)
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2", len(labels)))
            ax.set_title("Department Distribution")
            st.pyplot(fig)
        else:
            st.warning("No Departments available for visualization.")
class Nurses:
    def __init__(self, conn):
        """Initialize the Nurses class with a database connection."""
        self.conn = conn
        self.cursor = conn.cursor()
        self.create_table()

    def create_table(self):
        """Ensure the 'Nurses' table exists in the database."""
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Nurses' AND xtype='U')
        CREATE TABLE Nurses (
            Nurse_National_Id NVARCHAR(20) PRIMARY KEY,
            Name NVARCHAR(255) NOT NULL,
            Department_ID INT FOREIGN KEY REFERENCES Departments(Department_ID),
            Contact NVARCHAR(20),
            Gender NVARCHAR(10),
            Salary FLOAT
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add_nurse(self, nurse_national_id, name, department_id, contact, gender, salary):
        """Add a new nurse to the database."""
        query = """
        INSERT INTO Nurses (Nurse_National_ID, Name, Department_ID, Contact, Gender, Salary)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            self.cursor.execute(query, (nurse_national_id, name, department_id, contact, gender, salary))
            self.conn.commit()  # Commit the transaction to save changes
            print("Nurse added successfully!")  # Debug: Confirm insertion
        except Exception as e:
            print("Error adding nurse:", e)  # Debug: Print any errors
            raise e
    def get_nurse_by_name(self, nurse_name):
        """Retrieve nurse details using the name."""
        query = "SELECT * FROM Nurses WHERE Name = ?;"
        self.cursor.execute(query, (nurse_name,))
        row = self.cursor.fetchone()
        if row:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, row))
        else:
            st.warning(f"No nurse found with the name '{nurse_name}'.")
            return None

    def get_nurse_by_id(self, nurse_national_id):
        """Retrieve nurse details using the national ID."""
        query = "SELECT * FROM Nurses WHERE Nurse_National_Id = ?;"
        self.cursor.execute(query, (nurse_national_id,))
        row = self.cursor.fetchone()
        if row:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, row))

    def update_nurse(self, nurse_national_id, **updates):
        """Update nurse details dynamically."""
        if updates:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [nurse_national_id]
            query = f"UPDATE Nurses SET {set_clause} WHERE Nurse_National_Id = ?;"
            self.cursor.execute(query, values)
            self.conn.commit()
            st.success(f"Nurse {nurse_national_id} updated successfully.")
        else:
            st.warning("No updates provided.")

    def delete_nurse(self, nurse_national_id):
        """Delete a nurse from the database."""
        query = "DELETE FROM Nurses WHERE Nurse_National_Id = ?;"
        self.cursor.execute(query, (nurse_national_id,))
        self.conn.commit()


    def search_nurse(self, search_term):
        """Search for nurses by nurse_national_id, department name, or name."""
        query = """
            SELECT Nurses.*, Departments.Name AS DepartmentName 
            FROM Nurses
            LEFT JOIN Departments ON Nurses.Department_ID = Departments.Department_ID
            WHERE Nurses.Nurse_National_Id LIKE ? 
            OR Departments.Name LIKE ? 
            OR Nurses.Name LIKE ?;
        """
        # Execute the query with the search term for all three fields
        self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return None
           
      
    def view_nurses(self):
        """View all nurses in the database."""
        query = "SELECT * FROM Nurses;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            st.table(results)  # Display results in a table
        else:
            st.warning("No nurses found.")

    def get_nurses_by_department(self, department_id):
        """Fetch all nurses in a specific department."""
        query = "SELECT Nurse_National_Id, Name FROM Nurses WHERE Department_ID = ?"
        self.cursor.execute(query, (department_id,))
        return self.cursor.fetchall()

    def get_nurses_by_department_list(self, department_id):
        """Fetch all nurses in a specific department."""
        query = """
        SELECT Nurse_National_Id, Name 
        FROM Nurses 
        WHERE Department_ID = ?
        """
        self.cursor.execute(query, (department_id,))
        nurses = self.cursor.fetchall()

        # Convert the result into a list of dictionaries for easier use
        nurse_list = []
        for nurse in nurses:
            nurse_list.append({
                "Nurse_National_Id": nurse[0],  # Nurse's National ID
                "Name": nurse[1]               # Nurse's Name
            })

        return nurse_list

    def visualize_nurses(self):
        """Visualize nurse data."""
        # Gender Distribution
        query = "SELECT Gender, COUNT(*) FROM Nurses GROUP BY Gender;"
        self.cursor.execute(query)
        gender_data = self.cursor.fetchall()

        # Salary Distribution
        query = "SELECT Salary FROM Nurses;"
        self.cursor.execute(query)
        salary_data = [row[0] for row in self.cursor.fetchall()]

        # Average Salary by Department
        query = "SELECT Department_ID, AVG(Salary) FROM Nurses GROUP BY Department_ID;"
        self.cursor.execute(query)
        salary_by_dept = self.cursor.fetchall()

        # Number of Nurses per Department
        query = "SELECT Department_ID, COUNT(*) FROM Nurses GROUP BY Department_ID;"
        self.cursor.execute(query)
        nurses_by_dept = self.cursor.fetchall()

        if not gender_data and not salary_data and not salary_by_dept and not nurses_by_dept:
            st.warning("No nurse data available for visualization.")
            return

        st.header("Nurse Data Visualization")

        # Subplot 1: Gender Distribution
        if gender_data:
            st.subheader("Gender Distribution of Nurses")
            labels, sizes = zip(*gender_data)
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2", len(labels)))
            st.pyplot(fig)

        # Subplot 2: Salary Distribution
        if salary_data:
            st.subheader("Salary Distribution of Nurses")
            fig, ax = plt.subplots()
            sns.histplot(salary_data, kde=True, bins=20, color='skyblue', ax=ax)
            ax.set_xlabel("Salary")
            ax.set_ylabel("Number of Nurses")
            st.pyplot(fig)

        # Subplot 3: Average Salary by Department
        if salary_by_dept:
            st.subheader("Average Salary by Department")
            dept_ids, avg_salaries = zip(*salary_by_dept)
            fig, ax = plt.subplots()
            ax.bar(dept_ids, avg_salaries, color='teal')
            ax.set_xlabel("Department ID")
            ax.set_ylabel("Average Salary")
            ax.set_xticks(dept_ids)
            ax.set_xticklabels(dept_ids, rotation=45)
            st.pyplot(fig)

        # Subplot 4: Number of Nurses per Department
        if nurses_by_dept:
            st.subheader("Number of Nurses per Department")
            dept_ids, counts = zip(*nurses_by_dept)
            fig, ax = plt.subplots()
            ax.bar(dept_ids, counts, color='skyblue', edgecolor='black')
            ax.set_xlabel("Department ID")
            ax.set_ylabel("Number of Nurses")
            ax.set_xticks(dept_ids)
            ax.set_xticklabels(dept_ids, rotation=45)
            st.pyplot(fig)
class Doctors:
    def __init__(self):
        """Establish connection with SQL Server."""
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL SERVER};'
            'SERVER=.;'
            'DATABASE=Hospital3;'
            'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()
        self.create_tables_if_not_exists()

    def create_tables_if_not_exists(self):
        """Create the Doctors and Doctor_Availability tables if they don't exist."""
        try:
            # Create Doctors table
            query = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Doctors' AND xtype='U')
            CREATE TABLE Doctors (
                Dr_National_ID NVARCHAR(14) PRIMARY KEY,  -- Changed to Dr_National_ID
                Name NVARCHAR(100),
                Specialization NVARCHAR(100),
                Department_ID INT,
                Contact NVARCHAR(20),
                Date_of_Birth DATE,
                Email NVARCHAR(100),
                Qualification NVARCHAR(100),
                Years_of_Experience INT,
                Status NVARCHAR(20),
                CONSTRAINT FK_Department FOREIGN KEY (Department_ID) REFERENCES Departments(Department_ID)
            );
            """
            self.cursor.execute(query)

            # Create Doctor_Availability table
            query = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Doctor_Availability' AND xtype='U')
            CREATE TABLE Doctor_Availability (
                Availbilty_ID int PRIMARY KEY identity(1,1),  -- Added comma here
                Dr_National_ID NVARCHAR(14),  -- Changed to Dr_National_ID
                Day NVARCHAR(20),
                Start_Time TIME,
                End_Time TIME,
                FOREIGN KEY (Dr_National_ID) REFERENCES Doctors(Dr_National_ID)
            );
            """
            self.cursor.execute(query)
            self.conn.commit()
        except pyodbc.Error as e:
            st.error(f"Database error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    def add_doctor_availability(self, dr_national_id, day, start_time, end_time):
        """Add availability for a doctor."""
        query = """
        INSERT INTO Doctor_Availability (Dr_National_ID, Day, Start_Time, End_Time)
        VALUES (?, ?, ?, ?);
        """
        self.cursor.execute(query, (dr_national_id, day, start_time, end_time))
        self.conn.commit()
        st.success(f"Availability added for Doctor with National ID {dr_national_id} on {day} from {start_time} to {end_time}.")

    def check_doctor_exists(self, dr_national_id):
        """Check if a doctor with the given National ID exists in the database."""
        query = "SELECT * FROM Doctors WHERE Dr_National_ID = ?;"
        self.cursor.execute(query, (dr_national_id,))
        row = self.cursor.fetchone()
        return row is not None  # Return True if the doctor exists, False otherwise
    
    def get_doctor_name_by_id(self, dr_national_id):
        """
        Fetch a doctor's name by their National ID.
        """
        query = "SELECT Name FROM Doctors WHERE Dr_National_ID = ?;"
        self.cursor.execute(query, (dr_national_id,))
        row = self.cursor.fetchone()
        return row[0] if row else "Unknown Doctor"
    def get_doctor_availability_by_name_or_id(self, search_term):
        """Fetch a doctor's availability by name or National ID."""
        query = """
        SELECT Doctor_Availability.*, Doctors.Name 
        FROM Doctor_Availability
        JOIN Doctors ON Doctor_Availability.Dr_National_ID = Doctors.Dr_National_ID
        WHERE Doctors.Dr_National_ID = ? OR Doctors.Name LIKE ?;
        """
        self.cursor.execute(query, (search_term, f"%{search_term}%"))
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return None  # Return None if no availability is found
    def delete_doctor_availability_by_day(self, dr_national_id, day):
        """Delete all availabilities for a doctor on a given day."""
        query = """
        DELETE FROM Doctor_Availability 
        WHERE Dr_National_ID = ? AND Day = ?;
        """
        self.cursor.execute(query, (dr_national_id, day))
        self.conn.commit()
        st.success(f"All availabilities deleted for Doctor with National ID {dr_national_id} on {day}.")

    def update_doctor_availability(self, dr_national_id, old_day, old_start_time, old_end_time, new_day, new_start_time, new_end_time):
        """Update availability for a doctor."""
        query = """
        UPDATE Doctor_Availability 
        SET Day = ?, Start_Time = ?, End_Time = ? 
        WHERE Dr_National_ID = ? AND Day = ? AND Start_Time = ? AND End_Time = ?;
        """
        self.cursor.execute(query, (new_day, new_start_time, new_end_time, dr_national_id, old_day, old_start_time, old_end_time))
        self.conn.commit()
        st.success(f"Availability updated for Doctor with National ID {dr_national_id}: {old_day} {old_start_time}-{old_end_time} → {new_day} {new_start_time}-{new_end_time}.")

    def get_doctor_availability(self, dr_national_id):
        """Retrieve and display availability for a specific doctor, including the doctor's name."""
        query = """
        SELECT d.Name AS Doctor_Name, da.Dr_National_ID, da.Day, da.Start_Time, da.End_Time
        FROM Doctor_Availability da
        JOIN Doctors d ON da.Dr_National_ID = d.Dr_National_ID
        WHERE da.Dr_National_ID = ?;
        """
        self.cursor.execute(query, (dr_national_id,))
        rows = self.cursor.fetchall()
        
        if not rows:
            st.warning(f"No availability found for Doctor with National ID {dr_national_id}.")
            return []
        
        # Extract column names
        columns = [column[0] for column in self.cursor.description]
        
        # Display the results in a table
        results = [dict(zip(columns, row)) for row in rows]
        st.table(results)
        return results

    def view_doctor_availability(self):
        """Display availability for all doctors."""
        query = """
        SELECT 
            Doctors.Dr_National_ID,
            Doctors.Name AS Doctor_Name,
            Doctor_Availability.Day,
            Doctor_Availability.Start_Time,
            Doctor_Availability.End_Time
        FROM Doctor_Availability
        JOIN Doctors ON Doctor_Availability.Dr_National_ID = Doctors.Dr_National_ID;
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            st.table(results)
        else:
            st.warning("No availability records found.")

    def add_doctor(self, dr_national_id, name, specialization, department_id, contact, date_of_birth, email, qualification, years_of_experience, status):
        """Add a new doctor to the database."""
        # Check if the Department_ID exists in the Departments table
        department_query = "SELECT Department_ID FROM Departments WHERE Department_ID = ?;"
        self.cursor.execute(department_query, (department_id,))
        if not self.cursor.fetchone():
            st.error(f"Department ID {department_id} does not exist.")
            return

        query = """
        INSERT INTO Doctors (Dr_National_ID, Name, Specialization, Department_ID, Contact, Date_of_Birth, Email, Qualification, Years_of_Experience, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, (dr_national_id, name, specialization, int(department_id), contact, date_of_birth, email, qualification, years_of_experience, status))
        self.conn.commit()
        st.success(f"Doctor {name} added successfully.")

    def get_doctor_by_id(self, dr_national_id):
        """Retrieve a doctor by their National ID."""
        query = "SELECT * FROM Doctors WHERE Dr_National_ID = ?;"
        self.cursor.execute(query, (dr_national_id,))
        row = self.cursor.fetchone()
        if row:
            columns = [column[0] for column in self.cursor.description]
            doctor = dict(zip(columns, row))
            doctor["Department_ID"] = int(doctor["Department_ID"])  # Ensuring Department_ID is an integer
            return doctor
        return None

    def search_doctors(self, search_term):
        """
        Search for doctors by Dr_National_ID, name, or department name.
        """
        query = """
        SELECT Doctors.*, Departments.Name AS DepartmentName
        FROM Doctors
        LEFT JOIN Departments ON Doctors.Department_ID = Departments.Department_ID
        WHERE Doctors.Dr_National_ID LIKE ? 
        OR Doctors.Name LIKE ? 
        OR Departments.Name LIKE ?;
        """
        self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results  # Return the results instead of displaying them here
        else:
            return None  # Return None if no results are found
    def check_doctor_availability(self, doctor_id, date, time):
        """
        Check if the doctor is available at the specified date and time.
        """
        # Convert date to day of the week
        from datetime import datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = date_obj.strftime("%A")  # e.g., "Monday"

        # Convert time to HH:MM:SS format
        time = time + ":00" if len(time) == 5 else time

        query = """
        SELECT * FROM Doctor_Availability
        WHERE Dr_National_ID = ? AND Day = ? AND Start_Time <= ? AND End_Time >= ?;
        """
        self.cursor.execute(query, (doctor_id, day_of_week, time, time))
        row = self.cursor.fetchone()
        
        return row is not None  # Return True if the doctor is available, False otherwise
    def update_doctor(self, dr_national_id, **updates):
        """Update doctor details dynamically."""
        if updates:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [dr_national_id]
            query = f"UPDATE Doctors SET {set_clause} WHERE Dr_National_ID = ?;"
            self.cursor.execute(query, values)
            self.conn.commit()
        else:
            st.warning("No updates provided.")
    def delete_doctor(self, dr_national_id):
        """Delete a doctor by their National ID."""
        query = "DELETE FROM Doctors WHERE Dr_National_ID = ?;"
        self.cursor.execute(query, (dr_national_id,))
        self.conn.commit()

    def view_doctors(self):
        """Fetch and return all doctors from the database."""
        query = "SELECT * FROM Doctors;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if rows:
            # Get column names from the cursor description
            columns = [column[0] for column in self.cursor.description]
            
            # Convert rows to a list of dictionaries
            doctors = [dict(zip(columns, row)) for row in rows]
            return doctors
        else:
            return []  

    def doctor_specialization_stats(self):
        """Visualize doctor specialization distribution."""
        df = pd.read_sql("SELECT Specialization FROM Doctors", self.conn)
        if df.empty:
            st.warning("No data available to visualize.")
            return

        st.header("Doctor Specialization Distribution")
        specialization_counts = df['Specialization'].value_counts()
        fig, ax = plt.subplots()
        specialization_counts.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_xlabel("Specialization")
        ax.set_ylabel("Number of Doctors")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
    def get_doctors_by_department(self, department_id):
        """Fetch all doctors in a specific department."""
        query = "SELECT Dr_National_ID, Name FROM Doctors WHERE Department_ID = ?"
        self.cursor.execute(query, (department_id,))
        return self.cursor.fetchall()
    def get_doctors_by_department_list(self, department_id):
        """Fetch all doctors in a specific department."""
        query = """
        SELECT Dr_National_ID, Name 
        FROM Doctors 
        WHERE Department_ID = ?
        """
        self.cursor.execute(query, (department_id,))
        doctors = self.cursor.fetchall()

        # Convert the result into a list of dictionaries for easier use
        doctor_list = []
        for doc in doctors:
            doctor_list.append({
                "Dr_National_ID": doc[0],  # Doctor's National ID
                "Name": doc[1]            # Doctor's Name
            })

        return doctor_list
    def close_connection(self):
            """Close the database connection."""
            self.cursor.close()
            self.conn.close()
class Appointments:
    def __init__(self, conn, doctor_manager=None, nurse_manager=None, department_manager=None, patient_manager=None):
        """
        Initialize the Appointments class with the specified managers and database connection.
        """
        self.conn = conn
        self.cursor = conn.cursor()
        # Initialize manager classes if not passed
        self.doctor_manager = doctor_manager if doctor_manager else Doctors()
        self.nurse_manager = nurse_manager if nurse_manager else Nurses(conn)
        self.department_manager = department_manager if department_manager else Departments()
        self.patient_manager = patient_manager if patient_manager else Patients()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Create the Appointments table if it doesn't exist."""
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Appointments' AND xtype='U')
        CREATE TABLE Appointments (
            Appointment_ID INT PRIMARY KEY IDENTITY(1,1),
            National_ID NVARCHAR(14),
            dr_national_id NVARCHAR(14),  -- Changed from Doctor_ID to dr_national_id
            Nurse_National_Id NVARCHAR(20),  -- Changed from Nurse_ID to Nurse_National_Id
            Department_ID INT,
            Date DATE,
            Time TIME,
            Reason NVARCHAR(255),
            FOREIGN KEY (National_ID) REFERENCES Patients(National_ID),
            FOREIGN KEY (dr_national_id) REFERENCES Doctors(dr_national_id),  -- Updated foreign key
            FOREIGN KEY (Nurse_National_Id) REFERENCES Nurses(Nurse_National_Id),  -- Updated foreign key
            FOREIGN KEY (Department_ID) REFERENCES Departments(Department_ID)
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def get_appointments_by_patient(self, national_id):
        """Retrieve all appointments for a specific patient using National_ID."""
        query = "SELECT * FROM Appointments WHERE National_ID = ?"
        self.cursor.execute(query, (national_id,))
        rows = self.cursor.fetchall()
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            st.table(results)
        else:
            st.write(f"No appointments found for Patient with National ID {national_id}.")

    def get_appointments_by_department(self, department_id):
        """Retrieve all appointments for a specific department."""
        query = "SELECT * FROM Appointments WHERE Department_ID = ?"
        self.cursor.execute(query, (department_id,))
        rows = self.cursor.fetchall()
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            st.table(results)
        else:
            st.write(f"No appointments found for Department ID {department_id}.")

    def delete_appointment(self, appointment_id):
        """Delete an appointment by its ID."""
        query = "DELETE FROM Appointments WHERE Appointment_ID = ?"
        self.cursor.execute(query, (appointment_id,))
        self.conn.commit()
        st.write(f"Appointment with ID {appointment_id} removed successfully.")

    def view_appointments(self):
        """Fetch all appointments with names instead of IDs."""
        query = """
        SELECT 
            Appointments.Appointment_ID,
            Patients.Name AS Patient_Name,
            Doctors.Name AS Doctor_Name,
            Nurses.Name AS Nurse_Name,
            Departments.Name AS Department_Name,
            Appointments.Date,
            Appointments.Time,
            Appointments.Reason
        FROM Appointments
        LEFT JOIN Patients ON Appointments.National_ID = Patients.National_ID
        LEFT JOIN Doctors ON Appointments.dr_national_id = Doctors.dr_national_id
        LEFT JOIN Nurses ON Appointments.Nurse_National_Id = Nurses.Nurse_National_Id
        LEFT JOIN Departments ON Appointments.Department_ID = Departments.Department_ID;
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return None  # Return None if no appointments are found

    def view_doctor_appointments(self, dr_national_id):
        """
        View all appointments for a specific doctor, including their time, date, and patient's National_ID.
        """
        query = """
        SELECT 
            Appointments.Appointment_ID,
            Patients.National_ID,  -- Include National_ID
            Patients.Name AS Patient_Name,
            Appointments.Date,
            Appointments.Time,
            Appointments.Reason
        FROM Appointments
        JOIN Patients ON Appointments.National_ID = Patients.National_ID
        WHERE Appointments.dr_national_id = ?  -- Updated condition
        ORDER BY Appointments.Date, Appointments.Time;
        """
        self.cursor.execute(query, (dr_national_id,))
        rows = self.cursor.fetchall()
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            st.table(results)
        else:
            st.write(f"No appointments found for Doctor with National ID {dr_national_id}.")

    def search_appointment(self, appointment_id=None, national_id=None, dr_national_id=None, date=None, reason=None):
        """
        Search for appointments based on one or more criteria.
        """
        # Base query
        query = """
        SELECT 
            Appointments.Appointment_ID,
            Patients.National_ID,
            Patients.Name AS Patient_Name,
            Doctors.Name AS Doctor_Name,
            Nurses.Name AS Nurse_Name,
            Departments.Name AS Department_Name,
            Appointments.Date,
            Appointments.Time,
            Appointments.Reason
        FROM Appointments
        JOIN Patients ON Appointments.National_ID = Patients.National_ID
        JOIN Doctors ON Appointments.dr_national_id = Doctors.dr_national_id  -- Updated JOIN condition
        JOIN Nurses ON Appointments.Nurse_National_Id = Nurses.Nurse_National_Id  -- Updated JOIN condition
        JOIN Departments ON Appointments.Department_ID = Departments.Department_ID
        WHERE 1=1
        """

        # Add conditions based on provided criteria
        conditions = []
        params = []

        if appointment_id:
            conditions.append("Appointments.Appointment_ID = ?")
            params.append(appointment_id)
        if national_id:
            conditions.append("Appointments.National_ID = ?")
            params.append(national_id)
        if dr_national_id:  # Updated condition
            conditions.append("Appointments.dr_national_id = ?")
            params.append(dr_national_id)
        if date:
            conditions.append("Appointments.Date = ?")
            params.append(date)
        if reason:
            conditions.append("Appointments.Reason LIKE ?")
            params.append(f"%{reason}%")

        # Combine conditions into the query
        if conditions:
            query += " AND " + " AND ".join(conditions)

        # Execute the query
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # Return results as a list of dictionaries
        if rows:
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return None  # Return None if no appointments are found
    def get_appointment_by_id(self, appointment_id):
        """
        Fetch an appointment by its ID.
        """
        query = """
        SELECT 
            Appointments.Appointment_ID,
            Appointments.National_ID,
            Appointments.dr_national_id,
            Appointments.Nurse_National_Id,
            Appointments.Department_ID,
            Appointments.Date,
            Appointments.Time,
            Appointments.Reason
        FROM Appointments
        WHERE Appointments.Appointment_ID = ?;
        """
        self.cursor.execute(query, (appointment_id,))
        row = self.cursor.fetchone()
        
        if row:
            # Fetch column names and map row to a dictionary
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, row))
        else:
            return None  # Return None if no appointment is found

    def update_appointment(self, appointment_id, **updates):
        """
        Update appointment details dynamically.
        """
        if not updates:
            st.warning("No updates provided.")
            return

        # Validate appointment ID
        query = "SELECT * FROM Appointments WHERE Appointment_ID = ?;"
        self.cursor.execute(query, (appointment_id,))
        if not self.cursor.fetchone():
            st.error(f"Error: Appointment with ID {appointment_id} does not exist.")
            return

        # Build the SET clause for the update query
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE Appointments SET {set_clause} WHERE Appointment_ID = ?;"
        values = list(updates.values()) + [appointment_id]

        # Execute the update query
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            st.success(f"Appointment {appointment_id} updated successfully.")
        except Exception as e:
            st.error(f"Error updating appointment: {e}")
    
    def check_doctor_availability(self,search_term, date):
        """Check a doctor's availability by name or National ID on a specific date."""
        query = """
        SELECT Doctor_Availability.*, Doctors.Name 
        FROM Doctor_Availability
        JOIN Doctors ON Doctor_Availability.Dr_National_ID = Doctors.Dr_National_ID
        WHERE (Doctors.Dr_National_ID = ? OR Doctors.Name LIKE ?)
        AND Doctor_Availability.Day = ?;
        """
        self.cursor.execute(query, (search_term, f"%{search_term}%", date))
        rows = self.cursor.fetchall()
        
        if rows:
            # Fetch column names and map rows to dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return None  # Return None if no availability is found
    def cancel_appointment(self, appointment_id):
        """
        Cancel an appointment by its ID.
        """
        query = "DELETE FROM Appointments WHERE Appointment_ID = ?;"
        self.cursor.execute(query, (appointment_id,))
        self.conn.commit()
        st.write(f"Appointment {appointment_id} canceled successfully.")

    def add_appointment(self, national_id, dr_national_id, nurse_national_id, department_id, date, time, reason):
        """
        Add a new appointment using National_ID, ensuring a 15-minute gap between appointments.
        """
        # Validate inputs (existing code)
        if not self.patient_manager.get_patient_by_id(national_id):
            st.write(f"Error: Patient with National ID {national_id} does not exist.")
            return
        if not self.doctor_manager.get_doctor_by_id(dr_national_id):
            st.write(f"Error: Doctor with National ID {dr_national_id} does not exist.")
            return
        if not self.nurse_manager.get_nurse_by_id(nurse_national_id):
            st.write(f"Error: Nurse with National ID {nurse_national_id} does not exist.")
            return
        if not self.department_manager.get_department_by_id(department_id):
            st.write(f"Error: Department with ID {department_id} does not exist.")
            return

        # Convert date to a date object
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()  # Ensure it's a date object
        except Exception as e:
            st.write(f"Error parsing date: {e}")
            return

        # Check if the appointment date and time are in the future
        appointment_datetime = datetime.combine(date_obj, time)
        if appointment_datetime <= datetime.now():
            st.write("Error: Appointment date and time must be in the future.")
            return

        # Extract day of the week from the appointment date
        day_of_week = date_obj.strftime("%A")  # e.g., "Monday"

        # Check if the doctor is available on the specified day and time
        availability = self.doctor_manager.get_doctor_availability(dr_national_id)
        if not availability:
            st.write(f"Error: Doctor with National ID {dr_national_id} has no availability records.")
            return

        is_available = False
        for slot in availability:
            if slot['Day'] == day_of_week:
                start_time = slot['Start_Time']
                end_time = slot['End_Time']
                if start_time <= time <= end_time:
                    is_available = True
                    break

        if not is_available:
            st.write(f"Error: Doctor with National ID {dr_national_id} is not available at {time} on {day_of_week}.")
            return

        # Check for 15-minute gap between appointments (existing code)
        query = """
        SELECT Time FROM Appointments
        WHERE dr_national_id = ? AND Date = ?
        AND DATEDIFF(MINUTE, Time, ?) BETWEEN -15 AND 15;
        """
        self.cursor.execute(query, (dr_national_id, date_obj, time))
        conflicting_appointments = self.cursor.fetchall()
        if conflicting_appointments:
            st.write(f"Error: Cannot schedule appointment at {time}. Conflicting appointments exist.")
            return

        # Save the appointment (existing code)
        query = """
        INSERT INTO Appointments (National_ID, dr_national_id, Nurse_National_Id, Department_ID, Date, Time, Reason)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, (national_id, dr_national_id, nurse_national_id, department_id, date_obj, time, reason))
        self.conn.commit()
        st.write(f"Appointment added successfully.")

    def check_doctor_availability_date(self, doctor_id, date, time):
        """
        Check if a doctor is available on a specific date and time.
        
        Args:
            doctor_id (str): The doctor's national ID.
            date (str): The date to check (YYYY-MM-DD).
            time (str): The time to check (HH:MM).
        
        Returns:
            bool: True if the doctor is available, False otherwise.
        """
        try:
            # Convert the input date to a day of the week (e.g., "Monday")
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = date_obj.strftime("%A")  # e.g., "Monday"

            # Ensure the time is in HH:MM:SS format
            time_obj = datetime.strptime(time, "%H:%M").time()

            query = """
            SELECT * FROM Doctor_Availability
            WHERE Dr_National_ID = ?
            AND Day = ?
            AND ? BETWEEN Start_Time AND End_Time;
            """
            self.cursor.execute(query, (doctor_id, day_of_week, time_obj))
            result = self.cursor.fetchone()
            
            return result is not None  # Return True if the doctor is available
        except Exception as e:
            st.error(f"Error checking doctor availability: {e}")
            return False

import decimal

class Billing:
    def __init__(self, conn, appointment_manager):
        """
        Initialize the Billing class with a database connection and an Appointments instance.
        """
        self.conn = conn
        self.cursor = conn.cursor()
        self.appointment_manager = appointment_manager
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """
        Create the Bills table if it doesn't exist.
        """
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Bills' AND xtype='U')
        CREATE TABLE Bills (
            Invoice_ID INT PRIMARY KEY IDENTITY(1,1),  -- Auto-generated ID
            Appointment_ID INT,
            Patient_Name NVARCHAR(100),
            National_ID NVARCHAR(14),  -- Add National_ID column
            Doctor_Name NVARCHAR(100),
            Total_Amount DECIMAL(10, 2),
            Date_Issued DATE,
            Payment_Status NVARCHAR(50),
            FOREIGN KEY (Appointment_ID) REFERENCES Appointments(Appointment_ID)
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def generate_bill(self, appointment_id, total_amount, payment_status="Unpaid"):
        """
        Generate a bill for a given appointment using Appointments.
        """
        # Retrieve appointment details from the database
        query = """
        SELECT 
            Appointments.Appointment_ID,
            Patients.Name AS Patient_Name,
            Patients.National_ID AS National_ID,  -- Include National_ID
            Doctors.Name AS Doctor_Name
        FROM Appointments
        JOIN Patients ON Appointments.National_ID = Patients.National_ID
        JOIN Doctors ON Appointments.dr_national_id = Doctors.dr_national_id  -- Updated JOIN condition
        WHERE Appointments.Appointment_ID = ?;
        """
        self.cursor.execute(query, (appointment_id,))
        
        # Get column names
        columns = [column[0] for column in self.cursor.description]
        
        # Fetch appointment data
        appointment = self.cursor.fetchone()

        if not appointment:
            st.error(f"Error: Appointment with ID {appointment_id} does not exist.")
            return

        # Convert tuple to dictionary
        appointment = dict(zip(columns, appointment))
        
        # Extract relevant details
        patient_name = appointment['Patient_Name']
        national_id = appointment['National_ID']  # Extract National_ID
        doctor_name = appointment['Doctor_Name']
        date_issued = pd.Timestamp.now().strftime('%Y-%m-%d')

        # Insert the bill record into the database
        query = """
        INSERT INTO Bills (Appointment_ID, Patient_Name, National_ID, Doctor_Name, Total_Amount, Date_Issued, Payment_Status)
        OUTPUT INSERTED.Invoice_ID  -- Retrieve the auto-generated Invoice_ID
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, (appointment_id, patient_name, national_id, doctor_name, total_amount, date_issued, payment_status))
        
        # Fetch the auto-generated Invoice_ID
        invoice_id = self.cursor.fetchone()[0]  # Fix: Access tuple element by index
        self.conn.commit()
        st.success(f"Bill generated successfully with Invoice ID {invoice_id}.")

    def calculate_doctor_salary(self, dr_national_id):
        """
        Calculate the total earnings for a doctor based on bills where Payment_Status is 'Paid'.
        Uses dr_national_id instead of doctor_name.
        """
        # First, get the doctor's name using dr_national_id
        query = """
        SELECT Name FROM Doctors WHERE dr_national_id = ?;
        """
        self.cursor.execute(query, (dr_national_id,))
        doctor = self.cursor.fetchone()

        if not doctor:
            st.warning(f"No doctor found with National ID {dr_national_id}.")
            return 0.0

        doctor_name = doctor[0]  # Extract the doctor's name

        # Calculate total earnings for the doctor
        query = """
        SELECT SUM(Total_Amount) AS total_earnings
        FROM Bills
        WHERE Doctor_Name = ? AND Payment_Status = 'Paid';
        """
        self.cursor.execute(query, (doctor_name,))
        result = self.cursor.fetchone()
    
        if not result or result[0] is None:
            st.warning(f"No earnings found for Dr. {doctor_name} with 'Paid' status.")
            return 0.0
    
        # Convert Decimal to float
        total_earnings = float(result[0]) * 0.6  
        st.success(f"Total earnings for Dr. {doctor_name} (Paid bills only): ${total_earnings:.2f}")
        return total_earnings

    def update_payment_status(self, invoice_id, new_status):
        """
        Update the payment status for a specific invoice.
        """
        query = """
        UPDATE Bills
        SET Payment_Status = ?
        WHERE Invoice_ID = ?;
        """
        self.cursor.execute(query, (new_status, invoice_id))
        self.conn.commit()
        st.success(f"Payment status for Invoice ID {invoice_id} updated to '{new_status}'.")

    def search_bills(self, search_term):
        """
        Search for bills by patient name, doctor name, invoice ID, or National ID.
        Returns a list of dictionaries containing the search results.
        """
        query = """
        SELECT 
            Bills.Invoice_ID,
            Bills.Appointment_ID,
            Appointments.National_ID AS Patient_National_ID,  -- Include National_ID
            Bills.Patient_Name,
            Bills.Doctor_Name,
            Bills.Total_Amount,
            Bills.Date_Issued,
            Bills.Payment_Status
        FROM Bills
        JOIN Appointments ON Bills.Appointment_ID = Appointments.Appointment_ID
        WHERE Invoice_ID LIKE ? OR Patient_Name LIKE ? OR Doctor_Name LIKE ? OR Appointments.National_ID LIKE ?;
        """
        self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = self.cursor.fetchall()

        if not rows:
            return None  # Return None if no results are found
        else:
            # Convert rows to a list of dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
    def view_bills(self):
        """
        Fetch all billing records, including Patient National ID.
        Returns a list of dictionaries containing the billing records.
        """
        query = """
        SELECT 
            Bills.Invoice_ID,
            Bills.Appointment_ID,
            Appointments.National_ID AS Patient_National_ID,  -- Include National_ID
            Bills.Patient_Name,
            Bills.Doctor_Name,
            Bills.Total_Amount,
            Bills.Date_Issued,
            Bills.Payment_Status
        FROM Bills
        JOIN Appointments ON Bills.Appointment_ID = Appointments.Appointment_ID;
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if not rows:
            return None  # Return None if no billing records are found
        else:
            # Convert rows to a list of dictionaries
            columns = [column[0] for column in self.cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
    def delete_bill(self, invoice_id):
        """
        Delete a specific bill by its invoice ID.
        """
        query = "DELETE FROM Bills WHERE Invoice_ID = ?;"
        self.cursor.execute(query, (invoice_id,))
        self.conn.commit()
        st.success(f"Invoice {invoice_id} deleted successfully.")

# app.py
import streamlit as st
CORRECT_PASSWORD = "123"
class Employee:
    def __init__(self):
        """Initialize all managers."""
        self.patient_manager = Patients()
        self.doctor_manager = Doctors()
        self.department_manager = Departments()
        self.nurse_manager = Nurses(conn)
        self.appointment_manager = Appointments(conn, doctor_manager=self.doctor_manager)
        self.billing_manager = Billing(conn, self.appointment_manager)
    # ==================== Patient Operations ====================
    def input_add_patient(self):
        """Take input for adding a new patient using Streamlit widgets."""
        st.header("Add Patient")
        national_id = st.text_input("National ID")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        gender = st.selectbox("Gender", ["Male", "Female"])
        contact = st.text_input("Contact")
        medical_history = st.text_input("Medical History")
        bmi = st.text_input("BMI (optional)") or None
        bp = st.text_input("Blood Pressure (optional)") or None
        sugar = st.text_input("Sugar Level (optional)") or None

        if st.button("Add Patient"):
            self.patient_manager.add_patient(national_id, name, age, gender, contact, medical_history, bmi, bp, sugar)
            

    def input_update_patient(self):
        """Take input for updating a patient's details using Streamlit widgets."""
        st.header("Update Patient")
        
        # Input for the National ID of the patient to update
        national_id = st.text_input("Enter patient's National ID to update:")
        
        if national_id:  # Only proceed if a National ID is provided
            # Fetch the existing patient data
            patient = self.patient_manager.get_patient_by_id(national_id)
            
            if patient:
                # Input fields for updating all attributes (pre-filled with current data)
                st.subheader("Update Patient Details (leave blank to keep the same)")
                new_name = st.text_input("New Name", value=patient.get("Name", "")) or None
                new_age = st.text_input("New Age", value=str(patient.get("Age", ""))) or None
                new_gender = st.text_input("New Gender", value=patient.get("Gender", "")) or None
                new_contact = st.text_input("New Contact", value=patient.get("Contact", "")) or None
                new_medical_history = st.text_input("New Medical History", value=patient.get("Medical_History", "")) or None
                new_bmi = st.text_input("New BMI", value=str(patient.get("BMI", ""))) or None
                new_bp = st.text_input("New Blood Pressure", value=patient.get("Blood_Pressure", "")) or None
                new_sugar = st.text_input("New Sugar Level", value=str(patient.get("Sugar_Level", ""))) or None

                # Create a dictionary of updates
                updates = {}
                if new_name is not None:
                    updates["Name"] = new_name
                if new_age is not None:
                    updates["Age"] = int(new_age)  # Convert to integer
                if new_gender is not None:
                    updates["Gender"] = new_gender
                if new_contact is not None:
                    updates["Contact"] = new_contact
                if new_medical_history is not None:
                    updates["Medical_History"] = new_medical_history
                if new_bmi is not None:
                    updates["BMI"] = float(new_bmi)  # Convert to float
                if new_bp is not None:
                    updates["Blood_Pressure"] = new_bp
                if new_sugar is not None:
                    updates["Sugar_Level"] = float(new_sugar)  # Convert to float

                if st.button("Update Patient"):
                    if updates:
                        # Call the update method with the updates dictionary
                        self.patient_manager.update_patient(national_id, **updates)
                        st.success(f"Patient with National ID {national_id} updated successfully!")
                    else:
                        st.warning("No updates provided.")
            else:
                st.error(f"No patient found with National ID {national_id}.")
        else:
            st.warning("Please enter a National ID to update a patient.")
    def input_delete_patient(self):
        """Take input for deleting a patient using Streamlit widgets."""
        st.header("Delete Patient")
        national_id = st.text_input("Enter patient's National ID to delete:")

        if st.button("Delete Patient"):
            self.patient_manager.delete_patient(national_id)
            

    def input_search_patient(self):
        """Search for patients using Streamlit widgets."""
        st.header("Search Patient")
        search_term = st.text_input("Enter patient's name, contact number, or National ID to search:")

        if st.button("Search"):
            if search_term:  # Only proceed if a search term is provided
                results = self.patient_manager.search_patients(search_term)
                if results:
                    st.write("Search Results:")
                    
                    # Inject custom CSS to make the table wider
                    st.markdown(
                        """
                        <style>
                        .stDataFrame {
                            width: 100% !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display the results in a dataframe
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("No patients are found.")
            else:
                st.warning("Please enter a search term.")
    def input_view_patients(self):
        """View all patients using Streamlit widgets."""
        st.header("View Patients")
        self.patient_manager.view_patients()  # Call the view_patients method directly

    def input_patients_info(self):
        """Visualize patient data using Streamlit widgets."""
        st.header("Patient Data Visualization")
        self.patient_manager.patients_info()

    # ==================== Doctor Operations ====================
    def input_add_doctor(self):
        """Take input for adding a new doctor using Streamlit widgets."""
        st.header("Add Doctor")
        dr_national_id = st.text_input("Doctor's National ID")  # Updated to Dr_National_ID
        name = st.text_input("Doctor's Name")
        specialization = st.text_input("Specialization")
        
        # Replace department_id with a dropdown of department names
        departments = self.department_manager.view_Departments_List()
        if departments:
            department_names = [dept["Name"] for dept in departments]
            selected_department_name = st.selectbox("Department Name", department_names)
            selected_department_id = [dept["Department_ID"] for dept in departments if dept["Name"] == selected_department_name][0]
        else:
            st.warning("No departments found. Please add departments first.")
            return
        
        contact = st.text_input("Contact")
        
        # Convert date_of_birth to a date-time input
        date_of_birth= st.text_input(
            "Date of Birth (YYYY-MM-DD)",
            placeholder="YYYY-MM-DD"
        )
    
        email = st.text_input("Email")
        qualification = st.text_input("Qualification")
        years_of_experience = st.number_input("Years of Experience", min_value=0)
        
        # Replace status with a dropdown containing "Active" and "Not Active"
        status = st.selectbox("Status", ["Active", "Not Active"])

        if st.button("Add Doctor"):
            self.doctor_manager.add_doctor(
                dr_national_id, name, specialization, selected_department_id, contact, 
                date_of_birth, email, qualification, years_of_experience, status
            )
           
    def input_update_doctor(self):
        """Take input for updating a doctor's details using Streamlit widgets."""
        st.header("Update Doctor")
        dr_national_id = st.text_input("Enter doctor's National ID to update:")

        # Fetch the current doctor details
        current_doctor = self.doctor_manager.get_doctor_by_id(dr_national_id)
        if not current_doctor:
            st.warning(f"No doctor found with National ID {dr_national_id}.")
            return

        # Input fields for updating doctor details (optional)
        st.subheader("Update Doctor Details (leave blank to keep the same)")
        new_name = st.text_input("New Name", value=current_doctor.get("Name", "")) or None
        new_specialization = st.text_input("New Specialization", value=current_doctor.get("Specialization", "")) or None
        new_contact = st.text_input("New Contact", value=current_doctor.get("Contact", "")) or None
        new_date_of_birth = st.text_input("New Date of Birth (YYYY-MM-DD)", value=current_doctor.get("Date_of_Birth", "")) or None
        new_email = st.text_input("New Email", value=current_doctor.get("Email", "")) or None
        new_qualification = st.text_input("New Qualification", value=current_doctor.get("Qualification", "")) or None
        new_years_of_experience = st.text_input("New Years of Experience", value=current_doctor.get("Years_of_Experience", "")) or None
        new_status = st.text_input("New Status", value=current_doctor.get("Status", "")) or None

        # Fetch departments and create a dropdown for department names
        departments = self.department_manager.view_Departments_List()
        if departments:
            department_names = [dept["Name"] for dept in departments]
            current_department_name = next(
                (dept["Name"] for dept in departments if dept["Department_ID"] == current_doctor.get("Department_ID")),
                None
            )
            selected_department_name = st.selectbox(
                "New Department",
                department_names,
                index=department_names.index(current_department_name) if current_department_name else 0
            )
            new_department_id = [dept["Department_ID"] for dept in departments if dept["Name"] == selected_department_name][0]
        else:
            st.warning("No departments found. Please add departments first.")
            return

        if st.button("Update Doctor"):
            # Prepare updates dictionary
            updates = {}
            if new_name is not None:
                updates["Name"] = new_name
            if new_specialization is not None:
                updates["Specialization"] = new_specialization
            if new_contact is not None:
                updates["Contact"] = new_contact
            if new_date_of_birth is not None:
                updates["Date_of_Birth"] = new_date_of_birth
            if new_email is not None:
                updates["Email"] = new_email
            if new_qualification is not None:
                updates["Qualification"] = new_qualification
            if new_years_of_experience is not None:
                updates["Years_of_Experience"] = new_years_of_experience
            if new_status is not None:
                updates["Status"] = new_status
            if new_department_id is not None:
                updates["Department_ID"] = new_department_id

            # Update doctor details
            if updates:
                self.doctor_manager.update_doctor(dr_national_id, **updates)
                st.success(f"Doctor with National ID {dr_national_id} updated successfully!")
            else:
                st.warning("No updates provided.")
    def input_delete_doctor(self):
        """Take input for deleting a doctor using Streamlit widgets."""
        st.header("Delete Doctor")
        dr_national_id = st.text_input("Enter doctor's National ID to delete:")  # Updated to Dr_National_ID

        if st.button("Delete Doctor"):
            self.doctor_manager.delete_doctor(dr_national_id)
            st.success(f"Doctor with National ID {dr_national_id} deleted successfully!")

    def input_search_doctor(self):
        """Search for doctors using Streamlit widgets."""
        st.header("Search Doctor")
        search_term = st.text_input("Enter doctor's National_ID, name, or department name to search:")

        if st.button("Search"):
            results = self.doctor_manager.search_doctors(search_term)  # Call search_doctors method
            if results:
                st.write("Search Results:")
                st.dataframe(
                    results,
                    use_container_width=True,  # Make the table use the full container width
                    column_config={
                        "Dr_National_ID": "National ID",
                        "Name": "Name",
                        "Specialization": "Specialization",
                        "Contact": "Contact",
                        "Availability": "Availability",
                        "DepartmentName": "Department Name"  # Add DepartmentName to the table
                    }
                )
            else:
                st.warning("No doctors found.")
    def input_view_doctors(self):
        """View all doctors using Streamlit widgets."""
        st.header("View Doctors")
        doctors = self.doctor_manager.view_doctors()
        if doctors:
            # Use st.dataframe to display the table with a wider layout
            st.dataframe(
                doctors,
                use_container_width=True,  # Expands the table to the width of the container
                
            )
        else:
            st.warning("No doctors found.")
    def input_doctor_specialization_stats(self):
        """Visualize doctor specialization distribution using Streamlit widgets."""
        st.header("Doctor Specialization Stats")
        self.doctor_manager.doctor_specialization_stats()

    def input_add_doctor_availability(self):
        """Take input for adding a doctor's availability using Streamlit widgets."""
        st.header("Add Doctor Availability")
        dr_national_id = st.text_input("Doctor's National ID")  # Updated to Dr_National_ID
        day = st.text_input("Day (e.g., Monday)")
        start_time = st.text_input("Start Time (HH:MM)")
        end_time = st.text_input("End Time (HH:MM)")

        if st.button("Add Availability"):
            # Check if the doctor's National ID exists in the database
            if self.doctor_manager.check_doctor_exists(dr_national_id):
                # If the doctor exists, add availability
                self.doctor_manager.add_doctor_availability(dr_national_id, day, start_time, end_time)
               
            else:
                # If the doctor does not exist, show an error message
                st.error("Doctor with the provided National ID not found. Please try again.")

    def input_delete_doctor_availability_by_day(self):
        """Take input for deleting a doctor's availability by day using Streamlit widgets."""
        st.header("Delete Doctor Availability by Day")
        dr_national_id = st.text_input("Doctor's National ID")  # Updated to Dr_National_ID
        day = st.text_input("Day (e.g., Monday)")

        if st.button("Delete Availability"):
            # Check if the doctor's National ID exists in the database
            if self.doctor_manager.check_doctor_exists(dr_national_id):
                # If the doctor exists, delete availability
                self.doctor_manager.delete_doctor_availability_by_day(dr_national_id, day)
                st.success(f"All availabilities deleted for Doctor with National ID {dr_national_id} on {day}.")
            else:
                # If the doctor does not exist, show an error message
                st.error("Doctor with the provided National ID not found. Please try again.")

    def input_update_doctor_availability(self):
        """Take input for updating a doctor's availability using Streamlit widgets."""
        st.header("Update Doctor Availability")
        doctor_id = st.number_input("Doctor ID", min_value=1)
        old_day = st.text_input("Current Day (e.g., Monday)")
        old_start_time = st.text_input("Current Start Time (HH:MM)")
        old_end_time = st.text_input("Current End Time (HH:MM)")
        new_day = st.text_input("New Day (e.g., Tuesday)")
        new_start_time = st.text_input("New Start Time (HH:MM)")
        new_end_time = st.text_input("New End Time (HH:MM)")

        if st.button("Update Availability"):
            self.doctor_manager.update_doctor_availability(doctor_id, old_day, old_start_time, old_end_time, new_day, new_start_time, new_end_time)
            st.success(f"Availability updated for Doctor ID {doctor_id}: {old_day} {old_start_time}-{old_end_time} → {new_day} {new_start_time}-{new_end_time}.")


    def input_view_doctor_availability(self):
        """View a doctor's availability using Streamlit widgets."""
        st.header("View Doctor Availability")
        
        # Input for doctor's name or National ID
        search_term = st.text_input("Enter Doctor's Name or National ID:")

        if st.button("View Availability"):
            if search_term:  # Only proceed if a search term is provided
                # Fetch availability by name or National ID
                availability = self.doctor_manager.get_doctor_availability_by_name_or_id(search_term)
                
                if availability:
                    st.write("Doctor Availability:")
                    
                    # Use st.dataframe to display the table with a wider layout
                    st.dataframe(
                        availability,
                        use_container_width=True,  # Expands the table to the width of the container
                        column_config={
                            "Dr_National_ID": "National ID",
                            "Name": "Name",
                            "Day": "Day",
                            "Start_Time": "Start Time",
                            "End_Time": "End Time"
                        }
                    )
                else:
                    st.warning("No availability found for this doctor.")
            else:
                st.warning("Please enter a Doctor's Name or National ID.")
    # ==================== Department Operations ====================
    def input_add_department(self):
        """Take input for adding a new department using Streamlit widgets."""
        st.header("Add Department")
        name = st.text_input("Department Name")

        if st.button("Add Department"):
            self.department_manager.add_department(name)
          


    def input_update_department(self):
        """Take input for updating a department using Streamlit widgets."""
        st.header("Update Department")
        department_id = st.text_input("Enter department ID to update:")
        new_name = st.text_input("Enter new department name (leave blank to keep the same):") or None

        if st.button("Update Department"):
            self.department_manager.update_department(department_id, Name=new_name)

    def input_delete_department(self):
        """Take input for deleting a department using Streamlit widgets."""
        st.header("Delete Department")
        department_id = st.text_input("Enter department ID to delete:")

        if st.button("Delete Department"):
            self.department_manager.delete_department(department_id)
        

    def input_search_department(self):
        """Search for Departments using Streamlit widgets."""
        st.header("Search Department")
        search_term = st.text_input("Enter department name to search:")

        if st.button("Search"):
            results = self.department_manager.search_Departments(search_term)  # Call search_Departments method
            if results:
                st.write("Search Results:")
                st.dataframe(
                    results,
                    use_container_width=True,  # Make the table use the full container width
                    column_config={
                        "Department_ID": "Department ID",
                        "Name": "Name",
                        "Description": "Description",
                        "Head": "Head",
                        "Contact": "Contact"
                    }
                )
            else:
                st.warning("No Departments found.")
    def input_view_Departments(self):
        """View all Departments using Streamlit widgets."""
        st.header("View Departments")
        Departments = self.department_manager.view_Departments()
        if Departments:
            st.table(Departments)  # Display Departments in a table


    def input_department_stats(self):
        """Visualize department count using Streamlit widgets."""
        st.header("Department Stats")
        self.department_manager.department_stats()

    # ==================== Nurse Operations ====================
    def input_add_nurse(self):
        """Take input for adding a new nurse using Streamlit widgets."""
        st.header("Add Nurse")
        nurse_national_id = st.text_input("Nurse's National ID")  # Added Nurse_National_Id input
        name = st.text_input("Nurse's Name")
        
        # Fetch departments and create a dropdown for department names
        departments = self.department_manager.view_Departments_List()
        if departments:
            department_names = [dept["Name"] for dept in departments]
            selected_department_name = st.selectbox("Department Name", department_names)
            
            # Debug: Print the departments list
            print("Departments:", departments)
            
            # Get the selected department ID
            selected_department_id = [dept["Department_ID"] for dept in departments if dept["Name"] == selected_department_name][0]
            
            # Debug: Print the selected department ID
            print("Selected Department ID:", selected_department_id)
        else:
            st.warning("No departments found. Please add departments first.")
            return
        
        contact = st.text_input("Contact")
        gender = st.text_input("Gender")
        salary = st.number_input("Salary", min_value=0.0)

        if st.button("Add Nurse"):
            # Debug: Print all inputs before adding the nurse
            print(f"Adding Nurse: National ID={nurse_national_id}, Name={name}, Department ID={selected_department_id}, Contact={contact}, Gender={gender}, Salary={salary}")
            
            # Add the nurse to the database
            self.nurse_manager.add_nurse(nurse_national_id, name, selected_department_id, contact, gender, salary)
            st.success("Nurse added successfully!")        

    def input_update_nurse(self):
        """Take input for updating a nurse's details using Streamlit widgets."""
        st.header("Update Nurse")
        nurse_national_id = st.text_input("Enter nurse's National ID to update:")

        # Fetch the current nurse details
        current_nurse = self.nurse_manager.get_nurse_by_id(nurse_national_id)
        if not current_nurse:
            st.warning(f"No nurse found with National ID {nurse_national_id}.")
            return

        # Input fields for updating nurse details (optional)
        st.subheader("Update Nurse Details (leave blank to keep the same)")
        new_name = st.text_input("New Name", value=current_nurse.get("Name", "")) or None
        new_contact = st.text_input("New Contact", value=current_nurse.get("Contact", "")) or None
        new_gender = st.text_input("New Gender", value=current_nurse.get("Gender", "")) or None
        new_salary = st.number_input("New Salary", value=current_nurse.get("Salary", 0.0), min_value=0.0) or None

        # Fetch departments and create a dropdown for department names
        departments = self.department_manager.view_Departments_List()
        if departments:
            department_names = [dept["Name"] for dept in departments]
            current_department_name = next(
                (dept["Name"] for dept in departments if dept["Department_ID"] == current_nurse.get("Department_ID")),
                None
            )
            selected_department_name = st.selectbox(
                "New Department",
                department_names,
                index=department_names.index(current_department_name) if current_department_name else 0
            )
            new_department_id = [dept["Department_ID"] for dept in departments if dept["Name"] == selected_department_name][0]
        else:
            st.warning("No departments found. Please add departments first.")
            return

        if st.button("Update Nurse"):
            # Prepare updates dictionary
            updates = {}
            if new_name is not None:
                updates["Name"] = new_name
            if new_contact is not None:
                updates["Contact"] = new_contact
            if new_gender is not None:
                updates["Gender"] = new_gender
            if new_salary is not None:
                updates["Salary"] = new_salary
            if new_department_id is not None:
                updates["Department_ID"] = new_department_id

            # Update nurse details
            if updates:
                self.nurse_manager.update_nurse(nurse_national_id, **updates)
            else:
                st.warning("No updates provided.")
    def input_delete_nurse(self):
        """Take input for deleting a nurse using Streamlit widgets."""
        st.header("Delete Nurse")
        nurse_national_id = st.text_input("Enter nurse's National ID to delete:")  # Updated to Nurse_National_Id

        if st.button("Delete Nurse"):
            self.nurse_manager.delete_nurse(nurse_national_id)
            st.success(f"Nurse with National ID {nurse_national_id} deleted successfully!")
    def input_search_nurse(self):
        """Search for nurses by NurseNationalID, Department Name, or Nurse Name using Streamlit widgets."""
        st.header("Search Nurse")
        
        # Input for the search term
        search_term = st.text_input("Enter Nurse National ID, Department Name, or Nurse Name to search:")
        if st.button("Search"):
            if search_term:  # Only proceed if a search term is provided
                results = self.nurse_manager.search_nurse(search_term)
                if results:
                    st.write("Search Results:")
                    
                    # Use st.dataframe for a wider and more flexible table
                    st.dataframe(results, 
                        use_container_width=True,
                        column_config={
                            "Nurse_National_Id":"Nurse_National_Id",
                            "Name":"Name",
                            "Department_ID":"Department_ID",
                            "Contact":"Contact",
                            "Gender":"Gender",
                            "Salary":"Salary",
                            "DepartmentName":"DepartmentName" })  # Adjust width to container
                else:
                    st.warning("No nurses found.")
            else:
                st.warning("Please enter a search term.")

    def input_view_nurses(self):
        """View all nurses using Streamlit widgets."""
        st.header("View Nurses")
        nurses = self.nurse_manager.view_nurses()
        if nurses:
            st.table(nurses)  # Display nurses in a table


    def input_visualize_nurses(self):
        """Visualize nurse data using Streamlit widgets."""
        st.header("Nurse Data Visualization")
        self.nurse_manager.visualize_nurses()

    # ==================== Appointment Operations ====================
    def input_add_appointment(self):
        """Take input for adding a new appointment using Streamlit widgets."""
        st.header("Add Appointment")

        # Step 1: Select Department
        Departments = self.department_manager.view_Departments_List()  # Fetch all Departments

        department_names = [dept["Name"] for dept in Departments]  # Extract department names
        selected_dept_name = st.selectbox("Select Department", department_names, key="dept_select")  # Unique key
        selected_dept_id = [dept["Department_ID"] for dept in Departments if dept["Name"] == selected_dept_name][0]

        # Step 2: Select Doctor (based on selected department)
        doctors = self.doctor_manager.get_doctors_by_department_list(selected_dept_id)  # Fetch doctors in the selected department
        if doctors:
            doctor_names = [doc["Name"] for doc in doctors]  # Extract doctor names
            selected_doc_name = st.selectbox("Select Doctor", doctor_names, key="doc_select")  # Unique key
            selected_dr_national_id = [doc["Dr_National_ID"] for doc in doctors if doc["Name"] == selected_doc_name][0]
        else:
            st.warning("No doctors found in this department. Please add doctors first.")
            return

        # Step 3: Select Nurse (based on selected department)
        nurses = self.nurse_manager.get_nurses_by_department_list(selected_dept_id)  # Fetch nurses in the selected department
        if nurses:
            nurse_names = [nurse["Name"] for nurse in nurses]  # Extract nurse names
            selected_nurse_name = st.selectbox("Select Nurse", nurse_names, key="nurse_select")  # Unique key
            selected_nurse_national_id = [nurse["Nurse_National_Id"] for nurse in nurses if nurse["Name"] == selected_nurse_name][0]
        else:
            st.warning("No nurses found in this department. Please add nurses first.")
            return

        # Step 4: Input Patient National ID
        national_id = st.text_input("Patient's National ID", key="national_id_input")  # Unique key

        # Step 5: Input Date and Time
        appointment_date = st.date_input("Appointment Date", key="appt_date_input")  # Returns a datetime.date object
        appointment_time = st.time_input("Appointment Time", key="appt_time_input")  # Returns a datetime.time object

        # Convert date to string in the correct format
        date_str = appointment_date.strftime("%Y-%m-%d")  # Convert date to "YYYY-MM-DD" format

        # Step 6: Input Reason for Appointment
        reason = st.text_input("Reason for Appointment", key="reason_input")  # Unique key

        # Step 7: Add Appointment
        if st.button("Add Appointment", key="add_appt_button"):  # Unique key
            self.appointment_manager.add_appointment(
                national_id=national_id,
                dr_national_id=selected_dr_national_id,
                nurse_national_id=selected_nurse_national_id,
                department_id=selected_dept_id,
                date=date_str,  # Pass date as a string
                time=appointment_time,  # Pass time as a datetime.time object
                reason=reason
            )
    def input_search_appointment(self):
        """Search for appointments using Streamlit widgets."""
        st.header("Search Appointment")
        appointment_id = st.text_input("Enter appointment ID (leave blank to skip):") or None
        national_id = st.text_input("Enter patient's National ID (leave blank to skip):") or None
        dr_national_id = st.text_input("Enter doctor's National ID (leave blank to skip):") or None
        date = st.text_input("Enter appointment date (YYYY-MM-DD, leave blank to skip):") or None
        reason = st.text_input("Enter reason (leave blank to skip):") or None

        if st.button("Search"):
            results = self.appointment_manager.search_appointment(appointment_id, national_id, dr_national_id, date, reason)
            if results:
                st.write("Search Results:")
                
                # Use st.dataframe to display the table with a wider layout
                st.dataframe(
                    results,
                    use_container_width=True,  # Expands the table to the width of the container
                    column_config={
                        "Appointment_ID": "Appointment ID",
                        "National_ID": "Patient National ID",
                        "Patient_Name": "Patient Name",
                        "Doctor_Name": "Doctor Name",
                        "Nurse_Name": "Nurse Name",
                        "Department_Name": "Department Name",
                        "Date": "Date",
                        "Time": "Time",
                        "Reason": "Reason"
                    }
                )
            else:
                st.warning("No appointments found.")
    def input_view_appointments(self):
        """View all appointments using Streamlit widgets."""
        st.header("View Appointments")
        appointments = self.appointment_manager.view_appointments()
        
        if appointments:
            # Use st.dataframe to display the table with a wider layout
            st.dataframe(
                appointments,
                use_container_width=True,  # Expands the table to the width of the container
                column_config={
                    "Appointment_ID": "Appointment ID",
                    "Patient_Name": "Patient Name",
                    "Doctor_Name": "Doctor Name",
                    "Nurse_Name": "Nurse Name",
                    "Department_Name": "Department Name",
                    "Date": "Date",
                    "Time": "Time",
                    "Reason": "Reason"
                }
            )
        else:
            st.warning("No appointments found.")

    def input_cancel_appointment(self):
        """Cancel an appointment using Streamlit widgets."""
        st.header("Cancel Appointment")
        appointment_id = st.text_input("Enter appointment ID to cancel:")

        if st.button("Cancel Appointment"):
            self.appointment_manager.cancel_appointment(appointment_id)
            st.success(f"Appointment with ID {appointment_id} canceled successfully!")


    def input_update_appointment(self):
        """
        Update an appointment's date and time using Streamlit widgets.
        """
        st.header("Update Appointment Date and Time")
        
        # Input for appointment ID
        appointment_id = st.text_input("Enter appointment ID to update:")
        
        if appointment_id:  # Only proceed if an appointment ID is provided
            current_appointment = self.appointment_manager.get_appointment_by_id(appointment_id)
            
            if current_appointment:
                # Fetch patient and doctor names
                patient_name = self.patient_manager.get_patient_name_by_id(current_appointment["National_ID"])
                doctor_name = self.doctor_manager.get_doctor_name_by_id(current_appointment["dr_national_id"])

                # Display current appointment details
                st.subheader("Current Appointment Details")
                st.write(f"**Appointment ID:** {current_appointment['Appointment_ID']}")
                st.write(f"**Patient Name:** {patient_name}")
                st.write(f"**Doctor Name:** {doctor_name}")
                st.write(f"**Current Date:** {current_appointment['Date']}")
                st.write(f"**Current Time:** {current_appointment['Time']}")

                # Input fields for updating date and time
                st.subheader("Update Date and Time")
                new_date = st.text_input("New Date (YYYY-MM-DD)", value=current_appointment.get("Date", "")) or None
                new_time = st.text_input("New Time (HH:MM)", value=current_appointment.get("Time", "")) or None

                if st.button("Update Appointment"):
                    if new_date and new_time:
                        # Check if the doctor is available at the new date and time
                        doctor_id = current_appointment["dr_national_id"]
                        is_available = self.appointment_manager.check_doctor_availability_date(doctor_id, new_date, new_time)
                        
                        if is_available:
                            # Prepare updates dictionary
                            updates = {
                                "Date": new_date,
                                "Time": new_time
                            }

                            # Update appointment details
                            self.appointment_manager.update_appointment(appointment_id, **updates)
                        else:
                            st.error(f"Doctor {doctor_name} is not available on {new_date} at {new_time}.")
                    else:
                        st.warning("Please provide both a new date and time.")
            else:
                st.error(f"No appointment found with ID {appointment_id}.")
        else:
            st.warning("Please enter an appointment ID to update.")
    def input_check_doctor_availability(self):
        """Check a doctor's availability using Streamlit widgets."""
        st.header("Check Doctor Availability")
        doctor_id = st.text_input("Enter doctor's ID:")
        date = st.text_input("Enter date to check availability (YYYY-MM-DD):")

        if st.button("Check Availability"):
            availability = self.appointment_manager.check_doctor_availability(doctor_id, date)
            if availability:
                st.write("Doctor Availability:")
                st.table(availability)  # Display availability in a table
            else:
                st.warning("No availability found.")
   # ==================== Billing Operations ====================
    def input_generate_bill(self):
        """Take input for generating a bill using Streamlit widgets."""
        st.header("Generate Bill")
        appointment_id = st.number_input("Appointment ID", min_value=1)
        total_amount = st.number_input("Total Amount", min_value=0.0)
        payment_status = st.text_input("Payment Status (default: Unpaid):") or "Unpaid"

        if st.button("Generate Bill"):
            self.billing_manager.generate_bill(appointment_id, total_amount, payment_status)
            

    def input_calculate_doctor_salary(self):
        """Take input for calculating a doctor's salary using Streamlit widgets."""
        st.header("Calculate Doctor Salary")
        dr_national_id = st.text_input("Enter doctor's national ID:")

        if st.button("Calculate Salary"):
             self.billing_manager.calculate_doctor_salary(dr_national_id)

    def input_update_payment_status(self):
        """Take input for updating a bill's payment status using Streamlit widgets."""
        st.header("Update Payment Status")
        invoice_id = st.number_input("Invoice ID", min_value=1)
        new_status = st.text_input("Enter new payment status:")

        if st.button("Update Payment Status"):
            self.billing_manager.update_payment_status(invoice_id, new_status)

    def input_search_bills(self):
        """Search for bills using Streamlit widgets."""
        st.header("Search Bills")
        search_term = st.text_input("Enter patient Id, doctor Id, or invoice ID to search:")

        if st.button("Search"):
            results = self.billing_manager.search_bills(search_term)
            if results:
                st.write("Search Results:")
                # Use st.dataframe to display the table with a wider layout
                st.dataframe(
                    results,
                    use_container_width=True,  # Expands the table to the width of the container
                    column_config={
                        "Invoice_ID": "Invoice ID",
                        "Appointment_ID": "Appointment ID",
                        "Patient_National_ID": "Patient National ID",
                        "Patient_Name": "Patient Name",
                        "Doctor_Name": "Doctor Name",
                        "Total_Amount": "Total Amount",
                        "Date_Issued": "Date Issued",
                        "Payment_Status": "Payment Status"
                    }
                )
            else:
                st.warning(f"No results found for '{search_term}'.")
    def input_view_bills(self):
        """View all bills using Streamlit widgets."""
        st.header("View Bills")
        bills = self.billing_manager.view_bills()
        if bills:
            # Use st.dataframe to display the table with a wider layout
            st.dataframe(
                bills,
                use_container_width=True,  # Expands the table to the width of the container
                column_config={
                    "Invoice_ID": "Invoice ID",
                    "Appointment_ID": "Appointment ID",
                    "Patient_National_ID": "Patient National ID",
                    "Patient_Name": "Patient Name",
                    "Doctor_Name": "Doctor Name",
                    "Total_Amount": "Total Amount",
                    "Date_Issued": "Date Issued",
                    "Payment_Status": "Payment Status"
                }
            )
        else:
            st.warning("No billing records to display.")
    def input_delete_bill(self):
        """Take input for deleting a bill using Streamlit widgets."""
        st.header("Delete Bill")
        invoice_id = st.number_input("Enter invoice ID to delete:", min_value=1)

        if st.button("Delete Bill"):
            self.billing_manager.delete_bill(invoice_id)
            st.success(f"Bill with invoice ID {invoice_id} deleted successfully!")


    # ==================== Start the App ====================
    def start(self):

        """Start the Streamlit-driven system for employee operations."""
        st.title("Hospital Management System")
        # Sidebar for navigation
        if not self.authenticate():
            return  # Stop further execution if authentication fails

        operation = st.sidebar.selectbox(
            "Select Operation",
            [
                "Patient Operations", "Doctor Operations", "Department Operations",
                "Nurse Operations", "Appointment Operations", "Billing Operations"
            ]
        )

        if operation == "Patient Operations":
            self.patient_operations()
        elif operation == "Doctor Operations":
            self.doctor_operations()
        elif operation == "Department Operations":
            self.department_operations()
        elif operation == "Nurse Operations":
            self.nurse_operations()
        elif operation == "Appointment Operations":
            self.appointment_operations()
        elif operation == "Billing Operations":
            self.billing_operations()
    
    def authenticate(self):
        """Authenticate the user with a password."""
        if 'authenticated' not in st.session_state:
            st.session_state['authenticated'] = False

        if st.session_state['authenticated']:
            return True

        st.title("Login")
        password = st.text_input("Enter Password", type="password")

        if st.button("Login"):
            if password == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.success("Logged in successfully!")
                return True
            else:
                st.error("Incorrect password. Please try again.")
                return False

    def patient_operations(self):
        """Handles all patient-related operations."""
        action = st.sidebar.selectbox(
            "Select Action",
            [
                "Add Patient", "Update Patient", "Delete Patient",
                "Search Patient", "View Patients", "Visualize Patient Data"
            ]
        )

        if action == "Add Patient":
            self.input_add_patient()
        elif action == "Update Patient":
            self.input_update_patient()
        elif action == "Delete Patient":
            self.input_delete_patient()
        elif action == "Search Patient":
            self.input_search_patient()
        elif action == "View Patients":
            self.input_view_patients()
        elif action == "Visualize Patient Data":
            self.input_patients_info()

    def doctor_operations(self):
        """Handles all doctor-related operations."""
        action = st.sidebar.selectbox(
            "Select Action",
            [
                "Add Doctor", "Update Doctor", "Delete Doctor",
                "Search Doctor", "View Doctors", "Doctor Specialization Stats",
                "Add Doctor Availability", "Delete Doctor Availability by Day",
                "Update Doctor Availability", "View Doctor Availability"
            ]
        )

        if action == "Add Doctor":
            self.input_add_doctor()
        elif action == "Update Doctor":
            self.input_update_doctor()
        elif action == "Delete Doctor":
            self.input_delete_doctor()
        elif action == "Search Doctor":
            self.input_search_doctor()
        elif action == "View Doctors":
            self.input_view_doctors()
        elif action == "Doctor Specialization Stats":
            self.input_doctor_specialization_stats()
        elif action == "Add Doctor Availability":
            self.input_add_doctor_availability()
        elif action == "Delete Doctor Availability by Day":
            self.input_delete_doctor_availability_by_day()
        elif action == "Update Doctor Availability":
            self.input_update_doctor_availability()
        elif action == "View Doctor Availability":
            self.input_view_doctor_availability()


    def department_operations(self):
        """Handles all department-related operations."""
        action = st.sidebar.selectbox(
            "Select Action",
            [
                "Add Department", "Update Department", "Delete Department",
                "Search Department", "View Departments", "Department Stats"
            ]
        )

        if action == "Add Department":
            self.input_add_department()
        elif action == "Update Department":
            self.input_update_department()
        elif action == "Delete Department":
            self.input_delete_department()
        elif action == "Search Department":
            self.input_search_department()
        elif action == "View Departments":
            self.input_view_Departments()
        elif action == "Department Stats":
            self.input_department_stats()

    def nurse_operations(self):
        """Handles all nurse-related operations."""
        action = st.sidebar.selectbox(
            "Select Action",
            [
                "Add Nurse", "Update Nurse", "Delete Nurse",
                "Search Nurse", "View Nurses", "Visualize Nurse Data"
            ]
        )

        if action == "Add Nurse":
            self.input_add_nurse()
        elif action == "Update Nurse":
            self.input_update_nurse()
        elif action == "Delete Nurse":
            self.input_delete_nurse()
        elif action == "Search Nurse":
            self.input_search_nurse()
        elif action == "View Nurses":
            self.input_view_nurses()
        elif action == "Visualize Nurse Data":
            self.input_visualize_nurses()

    def appointment_operations(self):
        """Handles all appointment-related operations."""
        action = st.sidebar.selectbox(
            "Select Action",
            [
                "Add Appointment", "Search Appointment", "View Appointments",
                "Cancel Appointment", "Update Appointment",
                "Check Doctor Availability" 
            ]
        )

        if action == "Add Appointment":
            self.input_add_appointment()
        elif action == "Search Appointment":
            self.input_search_appointment()
        elif action == "View Appointments":
            self.input_view_appointments()
        elif action == "Cancel Appointment":
            self.input_cancel_appointment()
        elif action == "Update Appointment":
            self.input_update_appointment()
        elif action == "Check Doctor Availability":
            self.input_check_doctor_availability()


    def billing_operations(self):
        """Handles all billing-related operations."""
        action = st.sidebar.selectbox(
            "Select Action",
            [
                "Generate Bill", "Update Payment Status", "View Bills",
                "Search Bills", "Delete Bill", 
                "Calculate Doctor Salary"
            ]
        )

        if action == "Generate Bill":
            self.input_generate_bill()
        elif action == "Update Payment Status":
            self.input_update_payment_status()
        elif action == "View Bills":
            self.input_view_bills()
        elif action == "Search Bills":
            self.input_search_bills()
        elif action == "Delete Bill":
            self.input_delete_bill()
        elif action == "Calculate Doctor Salary":
            self.input_calculate_doctor_salary()

# Run the app
if __name__ == "__main__":
    employee = Employee()
    employee.start()