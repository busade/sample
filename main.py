import tkinter as tk
from tkinter import messagebox
import sqlite3

print(tk.TkVersion)
# intialize database connection
db = sqlite3.connect("port.db")
c = db.cursor()

# create tables

c.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    class TEXT NOT NULL
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    score REAL,
    UNIQUE(student_id, name),
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

db.commit()



# functions

def add_student():
    name = student_name_entry.get()
    class_name = student_class_entry.get()
    if name.strip():
        messagebox.showerror("Error","Student name cannot be empty")
        return
    try: 
        c.execute("INSERT INTO students(name ,class) VALUES (?)", (name, class_name,))
        db.commit()
        messagebox.showinfo("Success",f"student '{name}' added.")
        update_menus()

    except sqlite3.IntergrityError :
        messagebox.showerror("Error","Student already exists!")
    student_name_entry.delete(0,tk.END)
    student_class_entry.delete(0,tk.END)


def add_subject():
    student_name = student_select.get()
    subject = subject_name_entry.get()

    if student_name == "":
        messagebox.showerror("Error", "Please select a valid student.")
        return
    if subject.strip() == "":
        messagebox.showerror("Error", "Subject name cannot be empty!")
        return

    try:
        c.execute("SELECT id FROM students WHERE name = ?", (student_name,))
        student_id = c.fetchone()[0]
        c.execute("INSERT INTO subjects (student_id, name) VALUES (?, ?)", (student_id, subject))
        db.commit()
        messagebox.showinfo("Success", f"Subject '{subject}' added for {student_name}.")
        update_menus()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Subject already exists for this student!")
    subject_name_entry.delete(0, tk.END)



def add_score():
    student_name = student_select.get()
    subject = subject_select.get()
    try:
        score = float(score_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid score.")
        return

    if student_name == "":
        messagebox.showerror("Error", "Please select a valid student.")
        return
    if subject == "":
        messagebox.showerror("Error", "Please select a valid subject.")
        return

    try:
        c.execute("""
        UPDATE subjects SET score = ?
        WHERE id = (SELECT s.id FROM subjects s
                    JOIN students st ON s.student_id = st.id
                    WHERE st.name = ? AND s.name = ?)
        """, (score, student_name, subject))
        if c.rowcount == 0:
            messagebox.showerror("Error", "Failed to update score.")
        else:
            db.commit()
            messagebox.showinfo("Success", f"Score {score} added for {student_name} in {subject}.")
    except Exception as e:
        messagebox.showerror("Error", f"Error adding score: {e}")
    score_entry.delete(0, tk.END)



def get_scores():
    student_name = student_select.get()
    if student_name == "":
        messagebox.showerror("Error", "Please select a valid student.")
        return

    c.execute("""
    SELECT s.name, sb.name, sb.score
    FROM students s
    LEFT JOIN subjects sb ON s.id = sb.student_id
    WHERE s.name = ?
    """, (student_name,))
    rows = c.fetchall()

    if not rows:
        messagebox.showinfo("Student Scores", f"No data available for {student_name}.")
    else:
        result = f"Scores for {student_name}:\n"
        for row in rows:
            subject, score = row[1], row[2]
            result += f"{subject}: {score if score is not None else 'No score assigned'}\n"
        messagebox.showinfo("Student Scores", result)



# Create main window
root = tk.Tk()
root.title("Student Score Manager")
root.geometry("400x500")

# Widgets
# Add student frame
student_frame = tk.LabelFrame(root, text="Add Student")
student_frame.pack(fill="both", padx=10, pady=5)

student_name_label = tk.Label(student_frame, text="Student Name:")
student_name_label.pack(pady=5)
student_name_entry = tk.Entry(student_frame)
student_name_entry.pack(pady=5)
student_class_label = tk.Label(student_frame, text="Student Name:")
student_class_label.pack(pady=5)
student_class_entry = tk.Entry(student_frame)
student_class_entry.pack(pady=5)
add_student_button = tk.Button(student_frame, text="Add Student", command=add_student)
add_student_button.pack(pady=5)


# Add subject frame
subject_frame = tk.LabelFrame(root, text="Add Subject")
subject_frame.pack(fill="both", padx=10, pady=5)

student_select_label = tk.Label(subject_frame, text="Select Student:")
student_select_label.pack(pady=5)
student_select = tk.StringVar()
student_select_menu = tk.OptionMenu(subject_frame, student_select, "")
student_select_menu.pack(pady=5)

subject_name_label = tk.Label(subject_frame, text="Subject Name:")
subject_name_label.pack(pady=5)
subject_name_entry = tk.Entry(subject_frame)
subject_name_entry.pack(pady=5)
add_subject_button = tk.Button(subject_frame, text="Add Subject", command=add_subject)
add_subject_button.pack(pady=5)


# Add score frame
score_frame = tk.LabelFrame(root, text="Add Score")
score_frame.pack(fill="both", padx=10, pady=5)

subject_select_label = tk.Label(score_frame, text="Select Subject:")
subject_select_label.pack(pady=5)
subject_select = tk.StringVar()
subject_select_menu = tk.OptionMenu(score_frame, subject_select, "")
subject_select_menu.pack(pady=5)

score_label = tk.Label(score_frame, text="Score:")
score_label.pack(pady=5)
score_entry = tk.Entry(score_frame)
score_entry.pack(pady=5)
add_score_button = tk.Button(score_frame, text="Add Score", command=add_score)
add_score_button.pack(pady=5)


# Get scores frame
get_scores_button = tk.Button(root, text="Get Scores", command=get_scores)
get_scores_button.pack(pady=10)

# Update menus dynamically
def update_menus():
    student_select_menu['menu'].delete(0, 'end')
    c.execute("SELECT name FROM students")
    students = [row[0] for row in c.fetchall()]
    for student in students:
        student_select_menu['menu'].add_command(label=student, command=tk._setit(student_select, student))

    if student_select.get() != "":
        subject_select_menu['menu'].delete(0, 'end')
        c.execute("""
        SELECT sb.name
        FROM subjects sb
        JOIN students s ON sb.student_id = s.id
        WHERE s.name = ?
        """, (student_select.get(),))
        subjects = [row[0] for row in c.fetchall()]
        for subject in subjects:
            subject_select_menu['menu'].add_command(label=subject, command=tk._setit(subject_select, subject))


update_menus()
root.mainloop()

# Close database connection on exit
db.close()
