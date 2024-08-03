from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import mysql.connector
from tkcalendar import Calendar
from tkinter import ttk

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password = "Your_password",
    port = "3306", #your port number which is used for mysql
    database="employee_management"
)
cursor = conn.cursor()

# Create employees table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        position VARCHAR(255) NOT NULL,
        salary FLOAT
    )
''')

# Create attendance table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT,
        date DATE NOT NULL,
        status VARCHAR(255) NOT NULL
    )
''')


#functions
def adminwin():
    root = tk.Tk()
    root.title("Employee Management System")

    # Create Notebook widget for different pages
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Page 1: Employee Details
    page1 = ttk.Frame(notebook)
    notebook.add(page1, text='Employee Details')

    # Employee Entry Fields
    name_label = tk.Label(page1, text="Name:")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(page1)
    name_entry.grid(row=0, column=1)

    position_label = tk.Label(page1, text="Position:")
    position_label.grid(row=1, column=0)
    position_entry = tk.Entry(page1)
    position_entry.grid(row=1, column=1)

    salary_label = tk.Label(page1, text="Salary:")
    salary_label.grid(row=2, column=0)
    salary_entry = tk.Entry(page1)
    salary_entry.grid(row=2, column=1)

    #function
    def add_employee():
        # Function to add a new employee
        name = name_entry.get()
        position = position_entry.get()
        salary = salary_entry.get()
        
        cursor.execute("INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)", (name, position, salary))
        conn.commit()
        messagebox.showinfo("Success", "Employee added successfully")
        
        name_entry.delete(0, tk.END)
        position_entry.delete(0, tk.END)
        salary_entry.delete(0, tk.END)


    add_employee_button = tk.Button(page1, text="Add Employee", command=add_employee)
    add_employee_button.grid(row=3, column=0, columnspan=2)

    # Page 2: Update and Delete Employees
    page2 = ttk.Frame(notebook)
    notebook.add(page2, text='Update/Delete Employees')

    tree = ttk.Treeview(page2, columns=("ID", "Name", "Position", "Salary"))
    tree.heading("#1", text="ID")
    tree.heading("#2", text="Name")
    tree.heading("#3", text="Position")
    tree.heading("#4", text="Salary")
    #function 
    def delete_employee():
        # Function to delete an employee
        selected_item = tree.selection()
        if selected_item:
            employee_id = tree.item(selected_item, "values")[0]
            cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
            conn.commit()
            messagebox.showinfo("Success", "Employee deleted successfully")
            view_employee_records()
        else:
            messagebox.showerror("Error", "Please select an employee to delete.")

    def update_employee():
        # Function to update an employee
        selected_item = tree.selection()
        if selected_item:
            employee_id = tree.item(selected_item, "values")[0]
            new_name = updated_name_entry.get()
            new_position = updated_position_entry.get()
            new_salary = updated_salary_entry.get()
            
            cursor.execute("UPDATE employees SET name = %s, position = %s, salary = %s WHERE id = %s",
                        (new_name, new_position, new_salary, employee_id))
            conn.commit()
            messagebox.showinfo("Success", "Employee updated successfully")
            view_employee_records()
        else:
            messagebox.showerror("Error", "Please select an employee to update.")
    
    def view_employee_records():
        # Function to view employee records
        for row in tree.get_children():
            tree.delete(row)

        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

        for employee in employees:
            tree.insert("", "end", values=employee)

    # Fetch records from the database and populate the treeview
    view_employee_records()

    tree.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    delete_employee_button = tk.Button(page2, text="Delete Employee", command=delete_employee)
    delete_employee_button.grid(row=1, column=0)

    update_employee_button = tk.Button(page2, text="Update Employee", command=update_employee)
    update_employee_button.grid(row=1, column=1)

    updated_name_label = tk.Label(page2, text="New Name:")
    updated_name_label.grid(row=2, column=0)
    updated_name_entry = tk.Entry(page2)
    updated_name_entry.grid(row=2, column=1)

    updated_position_label = tk.Label(page2, text="New Position:")
    updated_position_label.grid(row=3, column=0)
    updated_position_entry = tk.Entry(page2)
    updated_position_entry.grid(row=3, column=1)

    updated_salary_label = tk.Label(page2, text="New Salary:")
    updated_salary_label.grid(row=4, column=0)
    updated_salary_entry = tk.Entry(page2)
    updated_salary_entry.grid(row=4, column=1)

    # Page 3: Attendance
    # page3 = ttk.Frame(notebook)
    # notebook.add(page3, text='Attendance')

    # employee_id_label = tk.Label(page3, text="Employee ID:")
    # employee_id_label.grid(row=0, column=0)
    # employee_id_entry = tk.Entry(page3)
    # employee_id_entry.grid(row=0, column=1)

    # date_label = tk.Label(page3, text="Date:")
    # date_label.grid(row=1, column=0)
    # cal = Calendar(page3, selectmode="day",date_pattern="y-mm-dd")
    # cal.grid(row=1, column=1)

    # status_label = tk.Label(page3, text="Status:")
    # status_label.grid(row=2, column=0)
    # status_var = tk.StringVar()
    # status_var.set("Present")
    # status_menu = tk.OptionMenu(page3, status_var, "Present", "Absent")
    # status_menu.grid(row=2, column=1)
    
    #function
    

    def view_attendance_records():
        # Function to view attendance records and calculate salary deduction for absent days
        for row in attendance_tree.get_children():
            attendance_tree.delete(row)

        cursor.execute("SELECT employees.id, employees.name, attendance.date, attendance.status, employees.salary FROM employees LEFT JOIN attendance ON employees.id = attendance.employee_id")
        records = cursor.fetchall()

        for record in records:
            employee_id, employee_name, date, status, salary = record

            
            # Calculate salary deduction for absent days (assuming 100 Rs per absent day)
            absent_days=0
            if status == "Absent":
                cursor.execute("SELECT COUNT(*) FROM attendance WHERE employee_id = %s AND status = 'Absent'", (employee_id,))
                absent_days =cursor.fetchone()[0]
                
            deduction=absent_days *100
            # Calculate total salary after deduction
            total_salary = salary - deduction

            attendance_tree.insert("", "end", values=(employee_id, employee_name, date, status, salary, deduction, total_salary))


        # mark_attendance_button = tk.Button(page3, text="Mark Attendance", command=mark_attendance)
        # mark_attendance_button.grid(row=3, column=0, columnspan=2)

    # Page 4: View Attendance Records with Salary Deduction
    page4 = ttk.Frame(notebook)
    notebook.add(page4, text='View Attendance Records')

    attendance_tree = ttk.Treeview(page4, columns=("ID", "Name", "Date", "Status", "Salary", "Deduction", "Total Salary"))
    attendance_tree.heading("#1", text="ID")
    attendance_tree.heading("#2", text="Name")
    attendance_tree.heading("#3", text="Date")
    attendance_tree.heading("#4", text="Status")
    attendance_tree.heading("#5", text="Salary")
    attendance_tree.heading("#6", text="Deduction")
    attendance_tree.heading("#7", text="Total Salary")

    attendance_tree.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    # Fetch attendance records and calculate salary deduction
    view_attendance_records()

    root.mainloop()
def nxtpge():
    x=a.get()
    print("Name: ",x)
    y=b.get()
    # #create Cursor
    c= conn.cursor()

    #Query the database
    accesschecker = f"SELECT position from employees WHERE name = '{x}'"     
    c.execute(accesschecker)
    record=c.fetchall()   
    # print(record) 
    if (((len(record) != 0) and str.lower(record[0][0]) =='admin') or x =='temp') and y == 'admin':
        messagebox.showinfo("information","Sucess")
        #exitform()
        window.destroy()
        adminwin()        
    else:
        messagebox.showinfo("information","wrong")
    #commit Changes
    conn.commit()

def userpage():
    def mark_attendance():
        # Function to mark attendance
        employee_id = employee_id_entry.get()
        date = cal.get_date()
        status = status_var.get()
        
        cursor.execute("INSERT INTO attendance (employee_id, date, status) VALUES (%s, %s, %s)", (employee_id, date, status))
        conn.commit()
        messagebox.showinfo("Success", "Attendance marked successfully")
        
        employee_id_entry.delete(0, tk.END)
        status_var.set("Present")
    up = tk.Tk()
    up.title("Attendance")
    up.geometry("700x500")
    up.resizable(False, False)
    page3 = LabelFrame(up)
    page3.pack(padx=150,pady=50)
    employee_id_label = tk.Label(page3, text="Employee ID:")
    employee_id_label.grid(row=0, column=0)
    employee_id_entry = tk.Entry(page3)
    employee_id_entry.grid(row=0, column=1)

    date_label = tk.Label(page3, text="Date:")
    date_label.grid(row=1, column=0)
    cal = Calendar(page3, selectmode="day",date_pattern="y-mm-dd")
    cal.grid(row=1, column=1)

    status_label = tk.Label(page3, text="Status:")
    status_label.grid(row=2, column=0)
    status_var = tk.StringVar()
    status_var.set("Present")
    status_menu = tk.OptionMenu(page3, status_var, "Present", "Absent")
    status_menu.grid(row=2, column=1)

    mark_attendance_button = tk.Button(page3, text="Mark Attendance", command=mark_attendance)
    mark_attendance_button.grid(row=3, column=0, columnspan=2)

    for widget in page3.winfo_children():
        widget.grid_configure(padx=15,pady=15)
   
window = tk.Tk()
window.title("Emp_management")
window.geometry("800x500")
window.resizable(False, False)
window.iconbitmap('C:\\Users\\SABARI RAJ\\Downloads\\suitcase.png')
canvas = tk.Canvas(
        window, 
        width = 800, 
        height = 500
        )  
canvas.pack()  
img = tk.PhotoImage(file=('C:\\Users\\SABARI RAJ\\Downloads\\OIP.png'))  
canvas.create_image(
        0, 
        0, 
        anchor="nw", 
        image=img
        ) 

lable = tk.Label(window,text="Admin",font=('Arial',25)).place(x=420,y=80,anchor='center')
#username
l=  tk.Label(window,text='User Name :').place(x=350,y=210,anchor='center')
#l.grid(row=1,column=1)
a=tk.StringVar()
e= tk.Entry(window,text=a).place(x=450,y=210,anchor='center')
#e.grid(row=1,column=2)

#password 
l2=  Label(window,text='Password :').place(x=355,y=240,anchor='center')
#l2.grid(row=2,column=1,sticky=W)
b=tk.StringVar()
e2= tk.Entry(window,show="*",text=b).place(x=450,y=240,anchor='center')
#e2.grid(row=2,column=2)

bt=tk.Button(window,text="submit",command=nxtpge,font=('helvetica')).place(x=350,y=350,anchor='center')

userbt=tk.Button(window,text="User Panel",command=userpage,font=('helvetica')).place(x=550,y=350,anchor='center') 

window.mainloop()

# Create the main GUI window
