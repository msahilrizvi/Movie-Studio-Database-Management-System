import mysql.connector
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpass",
    database="dbms"
)

cursor = db.cursor(buffered=True)


def execute_query(query, data=None):
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        db.commit()
        messagebox.showinfo("Success", "Query executed successfully")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error executing query: {err}")


def get_primary_key(table_name):
    query = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'"
    cursor.execute(query)
    return cursor.fetchone()[4]


# Display tables
def display_table(table_name):
    def insert_data():
        data = {}
        for col in column_names:
            data[col] = entry_vars[col].get()
        if data:
            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            execute_query(query, tuple(data.values()))
            refresh_table()

    def edit_data():
        row_id = tree.focus()
        if row_id:
            data = {}
            for col in column_names:
                value = entry_vars[col].get()
                if value:
                    data[col] = value
            if data:
                updates = ', '.join([f"{col}=%s" for col in data.keys()])
                query = f"UPDATE {table_name} SET {updates} WHERE {get_primary_key(table_name)}=%s"
                execute_query(query, tuple(data.values()) + (tree.item(row_id)['values'][0],))
                refresh_table()
        else:
            messagebox.showinfo("Info", "Select a row to edit")

    def search_data():
        data = {}
        for col in column_names:
            value = entry_vars[col].get()
            if value:
                data[col] = value
        if data:
            conditions = ' AND '.join([f"{col} LIKE %s" for col in data.keys()])
            values = ['%' + v + '%' for v in data.values()]
            query = f"SELECT * FROM {table_name} WHERE {conditions}"
            cursor.execute(query, tuple(values))
            rows = cursor.fetchall()
            refresh_table_with_rows(rows)
        else:
            refresh_table()

    def delete_data():
        row_id = tree.focus()
        if row_id:
            # Get the values of the selected row
            selected_row_values = tree.item(row_id)['values']
            conditions = ' AND '.join([f"{col}=%s" for col in column_names])
            query = f"DELETE FROM {table_name} WHERE {conditions}"
            execute_query(query, tuple(selected_row_values))
            refresh_table()
        else:
            messagebox.showinfo("Info", "Select a row to delete")

    def refresh_table_with_rows(rows):
        for row in tree.get_children():
            tree.delete(row)
        for row in rows:
            tree.insert("", "end", values=row)

    def refresh_table():
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)
        db.commit()

    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    column_names = [col[0] for col in cursor.fetchall()]

    table_frame = Frame(main_frame)
    table_frame.grid(row=0, column=1, sticky="nsew")

    tree = Treeview(table_frame, columns=column_names, show="headings")
    for col in column_names:
        tree.heading(col, text=col)
    tree.pack(side=LEFT, fill=BOTH, expand=1)

    input_frame = Frame(main_frame)
    input_frame.grid(row=1, column=1, sticky="nsew")

    entry_vars = {}
    for i, col in enumerate(column_names):
        label = Label(input_frame, text=col)
        label.grid(row=i, column=0, sticky="e")
        entry_vars[col] = StringVar()
        entry = Entry(input_frame, textvariable=entry_vars[col])
        entry.grid(row=i, column=1, sticky="ew")

    btn_frame = Frame(main_frame)
    btn_frame.grid(row=2, column=1, sticky="nsew")

    insert_btn = Button(btn_frame, text="Insert Data", command=insert_data)
    insert_btn.pack(side=LEFT, padx=5, pady=5)

    edit_btn = Button(btn_frame, text="Edit Data", command=edit_data)
    edit_btn.pack(side=LEFT, padx=5, pady=5)

    search_btn = Button(btn_frame, text="Search Data", command=search_data)
    search_btn.pack(side=LEFT, padx=5, pady=5)

    delete_btn = Button(btn_frame, text="Delete Data", command=delete_data)
    delete_btn.pack(side=LEFT, padx=5, pady=5)

    refresh_btn = Button(btn_frame, text="Refresh Table", command=refresh_table)
    refresh_btn.pack(side=LEFT, padx=5, pady=5)

    refresh_table()


def display_table_names():
    query = "SHOW TABLES"
    cursor.execute(query)
    tables = [table[0] for table in cursor.fetchall()]
    for table_name in tables:
        label = Label(left_frame, text=table_name, relief=RIDGE, width=20)
        label.pack()
        label.bind("<Button-1>", lambda event, name=table_name: display_table(name))


# main window
root = Tk()
root.title("DBMS Project")

root.state('zoomed')

main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

left_frame = Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="ns")

display_table_names()

root.mainloop()
