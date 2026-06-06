import getpass
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from pyfiglet import Figlet
from fpdf import FPDF
import time

console = Console()

# ====== DATA FILES ======
DATA_FILE = "school_data.json"
RESULTS_FOLDER = "result_cards"

# Create results folder if it doesn't exist
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

# ====== SCHOOL CONSTANTS ======
SCHOOL_NAME = "UHD-Schools"
SCHOOL_ADDRESS = "Wahadat Road, Lahore"
SCHOOL_PHONE = "+1 234 567 890"
SCHOOL_EMAIL = "UHD@uhd-schools.edu"
PRINCIPAL_NAME = "Dr. Muhammad Daniyal"

# ====== HEADER ======
def show_header(text):
    f = Figlet(font="rounded")
    console.print(f"[bold cyan]{f.renderText(text)}[/bold cyan]")
    
    console.print(f"[bold yellow]{SCHOOL_NAME}[/bold yellow]")
    console.print(f"[dim]{SCHOOL_ADDRESS}[/dim]")

def show_subheader(text):
    console.print(f"\n[bold magenta]▶ {text}[/bold magenta]")

# ================== DATA MANAGEMENT ==================
def load_data():
    """Load data from JSON file"""
    default_data = {
        "students": [
            {"roll": 1, "name": "Hassan", "attendance": [], "Physics": [], "Maths": [], "Chemistry": [], "Computer": [], "email": "hassan@uhd-schools.edu", "parent_contact": "1234567890", "address": "Student Housing, UHD Campus", "password": "student123"},
            {"roll": 2, "name": "Ubaid", "attendance": [], "Physics": [], "Maths": [], "Chemistry": [], "Computer": [], "email": "ubaid@uhd-schools.edu", "parent_contact": "1234567891", "address": "Student Housing, UHD Campus", "password": "student123"},
            {"roll": 3, "name": "Daniyal", "attendance": [], "Physics": [], "Maths": [], "Chemistry": [], "Computer": [], "email": "daniyal@uhd-schools.edu", "parent_contact": "1234567892", "address": "Student Housing, UHD Campus", "password": "student123"}
        ],
        "teachers": [],
        "next_roll": 4,
        "next_teacher_id": 1,
        "school_info": {
            "name": SCHOOL_NAME,
            "address": SCHOOL_ADDRESS,
            "phone": SCHOOL_PHONE,
            "email": SCHOOL_EMAIL,
            "principal": PRINCIPAL_NAME
        }
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                for student in data.get('students', []):
                    if 'password' not in student:
                        student['password'] = 'student123'
                    if 'attendance' not in student:
                        student['attendance'] = []
                    for subject in ['Physics', 'Maths', 'Chemistry', 'Computer']:
                        if subject not in student:
                            student[subject] = []
                return data
        except:
            console.print("[bold red]Error loading data. Using default data.[/bold red]")
            return default_data
    return default_data

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[bold red]Error saving data: {e}[/bold red]")
        return False

# ================== UTILITIES ==================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
    input()

def input_int(msg, lo, hi):
    while True:
        try:
            v = int(input(msg))
            if lo <= v <= hi:
                return v
            else:
                console.print(f"[bold red]Enter between {lo}-{hi}![/bold red]")
        except ValueError:
            console.print("[bold red]Invalid number![/bold red]")

def input_string(msg, allow_empty=False, min_len=2, max_len=50):
    while True:
        v = input(msg).strip()
        
        if not v and not allow_empty:
            console.print("[bold red]This field cannot be empty![/bold red]")
            continue
        
        if v and (len(v) < min_len or len(v) > max_len):
            console.print(f"[bold red]Input must be between {min_len}-{max_len} characters[/bold red]")
            continue
        
        if any(char.isdigit() for char in v) and "name" in msg.lower():
            console.print("[bold red]Name cannot contain numbers![/bold red]")
            continue
        
        return v
   
def input_email(msg):
    while True:
        email = input(msg).strip()
        if "@" in email and "." in email and len(email) >= 5:
            return email
        console.print("[bold red]Invalid email format![/bold red]")

def calculate_grade(marks):
    if marks is None or marks == []:
        return "-"
    if isinstance(marks, list):
        if not marks:
            return "-"
        marks = marks[-1]
    
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B+"
    elif marks >= 60:
        return "B"
    elif marks >= 50:
        return "C"
    else:
        return "F"

def calculate_percentage(student):
    subjects = ['Physics', 'Maths', 'Chemistry', 'Computer']
    total = 0
    count = 0
    
    for subject in subjects:
        marks = student.get(subject, [])
        if marks and marks[-1] is not None:
            total += marks[-1]
            count += 1
    
    if count == 0:
        return 0
    return total / count

def calculate_total_marks(student):
    subjects = ['Physics', 'Maths', 'Chemistry', 'Computer']
    total = 0
    for subject in subjects:
        marks = student.get(subject, [])
        if marks and marks[-1] is not None:
            total += marks[-1]
    return total

def get_student_status(percentage):
    if percentage >= 80:
        return "Excellent", "green"
    elif percentage >= 70:
        return "Very Good", "cyan"
    elif percentage >= 60:
        return "Good", "blue"
    elif percentage >= 50:
        return "Satisfactory", "yellow"
    elif percentage >= 40:
        return "Needs Improvement", "orange"
    else:
        return "Needs Attention", "red"

def show_pie_chart(student):
    subjects = ['Physics', 'Maths', 'Chemistry', 'Computer']
    marks = []
    labels = []
    
    for subject in subjects:
        sub_marks = student.get(subject, [])
        if sub_marks and sub_marks[-1] is not None:
            marks.append(sub_marks[-1])
            labels.append(f"{subject}\n({sub_marks[-1]})")
    
    if not marks:
        console.print("[yellow]No marks available to display chart[/yellow]")
        return
    
    plt.figure(figsize=(8, 6))
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    plt.pie(marks, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title(f"{student['name']}'s Performance Distribution\n{SCHOOL_NAME}", fontsize=14, fontweight='bold')
    plt.axis('equal')
    
    attendance = len(student.get('attendance', []))
    plt.figtext(0.02, 0.02, f"Total Attendance: {attendance} days", fontsize=10)
    plt.figtext(0.02, 0.05, f"Generated: {datetime.now().strftime('%d-%b-%Y')}", fontsize=8, style='italic')
    
    plt.show()

def show_attendance_chart(student):
    """Display attendance trend chart with absent shown in red - FIXED VERSION"""
    attendance_records = student.get('attendance', [])
    
    if not attendance_records:
        console.print("[yellow]No attendance records available. Please mark attendance first.[/yellow]")
        return
    
    # Parse attendance records to get present dates
    present_dates = []
    for record in attendance_records:
        if isinstance(record, str):
            if record.startswith('ABSENT_'):
                continue
            else:
                # Regular date string
                present_dates.append(record)
        elif isinstance(record, dict):
            if record.get('status') == 'Present':
                present_dates.append(record.get('date'))
    
    if not present_dates:
        console.print("[yellow]No attendance records available. Please mark attendance first.[/yellow]")
        return
    
    # Get the earliest and latest dates
    try:
        # Convert present dates to datetime
        present_datetimes = []
        for date_str in present_dates:
            try:
                present_datetimes.append(datetime.strptime(date_str, "%Y-%m-%d"))
            except:
                continue
        
        if not present_datetimes:
            console.print("[yellow]Invalid date format in attendance records[/yellow]")
            return
        
        start_date = min(present_datetimes)
        end_date = datetime.now()
        
        # Generate all dates between start and end
        date_range = []
        current = start_date
        while current <= end_date:
            date_range.append(current)
            current = current + timedelta(days=1)
        
        # Create attendance status for each date
        dates_str = []
        attendance_status = []  # 1 for present, 0 for absent
        colors_list = []
        
        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")
            dates_str.append(date.strftime("%d-%b"))
            
            if date_str in present_dates:
                attendance_status.append(1)
                colors_list.append('green')
            else:
                attendance_status.append(0)
                colors_list.append('red')
        
        # Create bar chart
        plt.figure(figsize=(14, 6))
        plt.bar(range(len(dates_str)), attendance_status, color=colors_list, edgecolor='black', linewidth=0.5)
        
        plt.title(f"{student['name']}'s Daily Attendance\n{SCHOOL_NAME}", fontsize=14, fontweight='bold')
        plt.xlabel("Date")
        plt.ylabel("Attendance Status")
        plt.xticks(range(len(dates_str)), dates_str, rotation=45, ha='right', fontsize=8)
        plt.yticks([0, 1], ['Absent', 'Present'])
        plt.ylim(-0.1, 1.1)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='green', label='Present'),
                           Patch(facecolor='red', label='Absent')]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Add statistics
        total_days = len(date_range)
        present_count = sum(attendance_status)
        absent_count = total_days - present_count
        attendance_percentage = (present_count / total_days) * 100 if total_days > 0 else 0
        
        plt.figtext(0.02, 0.02, f"Total Days: {total_days} | Present: {present_count} | Absent: {absent_count} | Attendance: {attendance_percentage:.1f}%", fontsize=9)
        plt.figtext(0.02, 0.05, f"Generated: {datetime.now().strftime('%d-%b-%Y')}", fontsize=8, style='italic')
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        console.print(f"[red]Error creating chart: {e}[/red]")
        console.print("[yellow]Please ensure attendance records are in correct format[/yellow]")

# ================== PDF RESULT CARD GENERATION ==================
class ResultCardPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 24)
        self.set_text_color(0, 51, 102)
        self.cell(0, 15, SCHOOL_NAME, 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, SCHOOL_ADDRESS, 0, 1, 'C')
        self.cell(0, 5, f'Phone: {SCHOOL_PHONE} | Email: {SCHOOL_EMAIL}', 0, 1, 'C')
        
        self.set_draw_color(0, 51, 102)
        self.set_line_width(1.5)
        self.line(10, 40, 200, 40)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} - {SCHOOL_NAME} - Generated on {datetime.now().strftime("%d-%m-%Y %H:%M")}', 0, 0, 'C')

def generate_result_card(data, student):
    percentage = calculate_percentage(student)
    total_marks = calculate_total_marks(student)
    status, color = get_student_status(percentage)
    attendance = len(student.get('attendance', []))
    
    pdf = ResultCardPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'STUDENT RESULT CARD', 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'STUDENT INFORMATION', 0, 1, 'L')
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_x(15)
    pdf.cell(50, 8, f'Name:', 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, f'{student["name"]}', 0, 0)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(30, 8, f'Roll No:', 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f'{student["roll"]}', 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.set_x(15)
    pdf.cell(50, 8, f'Parent Contact:', 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, f'{student.get("parent_contact", "N/A")}', 0, 0)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(30, 8, f'Email:', 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f'{student.get("email", "N/A")}', 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.set_x(15)
    pdf.cell(50, 8, f'Address:', 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f'{student.get("address", "N/A")}', 0, 1)
    
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'EXAMINATION RESULTS', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(230, 240, 255)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(60, 12, 'Subject', 1, 0, 'C', 1)
    pdf.cell(40, 12, 'Marks Obtained', 1, 0, 'C', 1)
    pdf.cell(40, 12, 'Max Marks', 1, 0, 'C', 1)
    pdf.cell(50, 12, 'Grade', 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 11)
    subjects = ['Physics', 'Maths', 'Chemistry', 'Computer']
    fill = False
    
    for subject in subjects:
        marks = student.get(subject, [])
        latest_marks = marks[-1] if marks else '-'
        
        pdf.cell(60, 10, subject, 1, 0, 'L', fill)
        
        if latest_marks == '-':
            pdf.cell(40, 10, '-', 1, 0, 'C', fill)
            pdf.cell(40, 10, '100', 1, 0, 'C', fill)
            pdf.cell(50, 10, '-', 1, 1, 'C', fill)
        else:
            pdf.cell(40, 10, str(latest_marks), 1, 0, 'C', fill)
            pdf.cell(40, 10, '100', 1, 0, 'C', fill)
            pdf.cell(50, 10, calculate_grade(marks), 1, 1, 'C', fill)
        
        fill = not fill
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'PERFORMANCE SUMMARY', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Arial', '', 11)
    
    pdf.set_x(20)
    pdf.cell(50, 8, 'Total Marks:', 0, 0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(40, 8, f'{total_marks}/400', 0, 0)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(50, 8, 'Percentage:', 0, 0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, f'{percentage:.2f}%', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_x(20)
    pdf.cell(50, 8, 'Attendance:', 0, 0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(40, 8, f'{attendance} days', 0, 0)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(50, 8, 'Status:', 0, 0)
    pdf.set_font('Arial', 'B', 11)
    
    if status == "Excellent":
        pdf.set_text_color(0, 128, 0)
    elif status == "Needs Attention":
        pdf.set_text_color(255, 0, 0)
    else:
        pdf.set_text_color(0, 0, 0)
    
    pdf.cell(0, 8, status, 0, 1)
    
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, '_________________________', 0, 1, 'R')
    pdf.cell(0, 5, f'Principal\'s Signature', 0, 1, 'R')
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 5, f'({PRINCIPAL_NAME})', 0, 1, 'R')
    pdf.cell(0, 5, SCHOOL_NAME, 0, 1, 'R')
    
    clean_name = student['name'].replace(" ", "_")
    filename = f"{RESULTS_FOLDER}/{clean_name}_Result_Card.pdf"
    pdf.output(filename)
    
    return filename

# ================== DISPLAY TABLES ==================
def show_students_table(data, filter_name=None):
    table = Table(title=f"{SCHOOL_NAME} - Student Records", style="bold cyan", show_lines=True)
    table.add_column("Roll", justify="center", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Attendance\n(Days)", justify="center")
    table.add_column("Avg %", justify="center")
    table.add_column("Status", justify="center")
    for subject in ["Physics", "Maths", "Chemistry", "Computer"]:
        table.add_column(f"{subject}\nMarks", justify="center")
        table.add_column(f"{subject}\nGrade", justify="center")
    
    students = data['students']
    if filter_name:
        students = [s for s in students if filter_name.lower() in s['name'].lower()]
    
    for s in students:
        attendance = len(s.get('attendance', []))
        percentage = calculate_percentage(s)
        status, color = get_student_status(percentage)
        
        if percentage >= 80:
            perc_str = f"[green]{percentage:.1f}%[/green]"
        elif percentage >= 60:
            perc_str = f"[yellow]{percentage:.1f}%[/yellow]"
        else:
            perc_str = f"[red]{percentage:.1f}%[/red]"
        
        status_str = f"[{color}]{status}[/{color}]"
        
        table.add_row(
            str(s['roll']), 
            s['name'], 
            str(attendance),
            perc_str,
            status_str,
            str(s['Physics'][-1] if s['Physics'] else "-"), 
            calculate_grade(s['Physics']),
            str(s['Maths'][-1] if s['Maths'] else "-"), 
            calculate_grade(s['Maths']),
            str(s['Chemistry'][-1] if s['Chemistry'] else "-"), 
            calculate_grade(s['Chemistry']),
            str(s['Computer'][-1] if s['Computer'] else "-"), 
            calculate_grade(s['Computer'])
        )
    console.print(table)

def show_teachers_table(data):
    if not data['teachers']:
        console.print("[yellow]No teachers registered yet.[/yellow]")
        return
    
    table = Table(title=f"{SCHOOL_NAME} - Teacher Records", style="bold magenta", show_lines=True)
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Subject", style="yellow")
    table.add_column("Attendance\n(Days)", justify="center")
    table.add_column("Email", style="blue")
    table.add_column("Contact", style="blue")
    
    for t in data['teachers']:
        table.add_row(
            str(t['id']),
            t['name'],
            t['subject'],
            str(len(t.get('attendance', []))),
            t.get('email', 'N/A'),
            t.get('contact', 'N/A')
        )
    console.print(table)

def show_teacher_students(data, teacher):
    subject = teacher['subject']
    
    table = Table(title=f"{SCHOOL_NAME} - All Students - {subject} Results", style="bold cyan", show_lines=True)
    table.add_column("Roll", justify="center", style="cyan")
    table.add_column("Name", style="green")
    table.add_column(f"{subject}\nMarks", justify="center")
    table.add_column(f"{subject}\nGrade", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Attendance\n(Days)", justify="center")
    
    for student in data['students']:
        marks = student.get(subject, [])
        latest_marks = marks[-1] if marks else "-"
        grade = calculate_grade(marks)
        attendance = len(student.get('attendance', []))
        
        if latest_marks != "-":
            if latest_marks >= 80:
                status = "[green]Excellent[/green]"
            elif latest_marks >= 60:
                status = "[yellow]Good[/yellow]"
            else:
                status = "[red]Needs Work[/red]"
        else:
            status = "[dim]Not Graded[/dim]"
        
        table.add_row(
            str(student['roll']),
            student['name'],
            str(latest_marks),
            grade,
            status,
            str(attendance)
        )
    
    console.print(table)

# ================== STUDENT MANAGEMENT ==================
def add_student(data):
    show_subheader(f"{SCHOOL_NAME} - Add New Student")
    console.print("[cyan]Enter student details:[/cyan]")
    
    name = input_string("Name: ")
    roll = data['next_roll']
    
    new_student = {
        "roll": roll,
        "name": name,
        "attendance": [],
        "Physics": [],
        "Maths": [],
        "Chemistry": [],
        "Computer": [],
        "email": f"{name.lower()}@uhd-schools.edu",
        "parent_contact": input_string("Parent Contact: "),
        "address": input_string("Address: "),
        "password": "student123"
    }
    
    data['students'].append(new_student)
    data['next_roll'] += 1
    
    console.print(f"\n[green]✓ Student added successfully to {SCHOOL_NAME}![/green]")
    console.print(f"Roll Number: [bold]{roll}[/bold]")
    console.print(f"Login Email: [bold]{new_student['email']}[/bold]")
    console.print(f"Default Password: [bold]student123[/bold]")
    
    save_data(data)

def remove_student(data):
    show_subheader(f"{SCHOOL_NAME} - Remove Student")
    roll = input_int("Enter roll number to remove: ", 1, 1000)
    
    student = next((s for s in data['students'] if s['roll'] == roll), None)
    if student:
        console.print(f"[yellow]Are you sure you want to remove {student['name']} from {SCHOOL_NAME}?[/yellow]")
        confirm = input("Type 'YES' to confirm: ")
        if confirm == "YES":
            data['students'] = [s for s in data['students'] if s['roll'] != roll]
            console.print("[green]✓ Student removed successfully![/green]")
            save_data(data)
        else:
            console.print("[yellow]Removal cancelled.[/yellow]")
    else:
        console.print("[red]Student not found![/red]")

def search_student(data):
    show_subheader(f"{SCHOOL_NAME} - Search Student")
    name = input_string("Enter student name to search: ")
    show_students_table(data, name)

# ================== TEACHER MANAGEMENT ==================
def add_teacher(data):
    show_subheader(f"{SCHOOL_NAME} - Add New Teacher")
    
    name = input_string("Name: ")
    
    console.print("Assign Subject:")
    console.print("1. Physics\n2. Maths\n3. Chemistry\n4. Computer")
    
    subject_choice = input_int("Select subject (1-4): ", 1, 4)
    subjects = ["Physics", "Maths", "Chemistry", "Computer"]
    subject = subjects[subject_choice - 1]
    
    email = input_email("Email: ")
    contact = input_string("Contact: ", allow_empty=True)
    
    is_class_teacher = True if subject == "Physics" else False
    
    new_teacher = {
        "id": data['next_teacher_id'],
        "name": name,
        "subject": subject,
        "email": email,
        "contact": contact,
        "attendance": [],
        "password": "teacher123",
        "class_teacher": is_class_teacher
    }
    
    data['teachers'].append(new_teacher)
    data['next_teacher_id'] += 1
    
    console.print("[green]✓ Teacher added successfully![/green]")
    save_data(data)

def remove_teacher(data):
    show_subheader(f"{SCHOOL_NAME} - Remove Teacher")
    teacher_id = input_int("Enter teacher ID to remove: ", 1, 1000)
    
    teacher = next((t for t in data['teachers'] if t['id'] == teacher_id), None)
    if teacher:
        console.print(f"[yellow]Are you sure you want to remove {teacher['name']} from {SCHOOL_NAME}?[/yellow]")
        confirm = input("Type 'YES' to confirm: ")
        if confirm == "YES":
            data['teachers'] = [t for t in data['teachers'] if t['id'] != teacher_id]
            console.print("[green]✓ Teacher removed successfully![/green]")
            save_data(data)
        else:
            console.print("[yellow]Removal cancelled.[/yellow]")
    else:
        console.print("[red]Teacher not found![/red]")

def modify_teacher_attendance(data):
    show_subheader(f"{SCHOOL_NAME} - Mark Teacher Attendance")
    
    if not data['teachers']:
        console.print("[yellow]No teachers registered.[/yellow]")
        return
    
    teachers_table = Table(title=f"{SCHOOL_NAME} - Select Teacher")
    teachers_table.add_column("ID", justify="center")
    teachers_table.add_column("Name")
    teachers_table.add_column("Subject")
    teachers_table.add_column("Current Attendance")
    
    for t in data['teachers']:
        teachers_table.add_row(str(t['id']), t['name'], t['subject'], str(len(t.get('attendance', []))))
    
    console.print(teachers_table)
    
    teacher_id = input_int("\nEnter teacher ID to mark attendance: ", 1, 1000)
    teacher = next((t for t in data['teachers'] if t['id'] == teacher_id), None)
    
    if teacher:
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in teacher['attendance']:
            teacher['attendance'].append(today)
            console.print(f"[green]✓ Attendance marked for {teacher['name']} at {SCHOOL_NAME}[/green]")
            save_data(data)
        else:
            console.print("[yellow]Attendance already marked for today![/yellow]")
    else:
        console.print("[red]Teacher not found![/red]")

# ================== SYSTEM FUNCTIONS ==================
def mark_student_attendance(data):
    show_subheader(f"{SCHOOL_NAME} - Mark Attendance (P/A)")
    today = datetime.now().strftime("%Y-%m-%d")
    
    for s in data['students']:
        console.print(f"\n[cyan]{s['name']} (Roll: {s['roll']})[/cyan]")
        
        status = input("Present or Absent? (P/A, default=P): ").strip().upper()
        
        # Remove any existing record for today
        s['attendance'] = [a for a in s['attendance'] if a != today and not (isinstance(a, str) and a.startswith('ABSENT_'))]
        
        if status == "A":
            # Record absence
            s['attendance'].append(f"ABSENT_{today}")
        else:
            # Record presence
            s['attendance'].append(today)
    
    console.print("[bold green]✓ Attendance marked successfully![/bold green]")
    save_data(data)

def add_student_results(data, teacher):
    show_subheader(f"{SCHOOL_NAME} - Add Results ({teacher['subject']})")
    
    subject = teacher['subject']
    
    for s in data['students']:
        console.print(f"\n[bold cyan]{s['name']} (Roll: {s['roll']})[/bold cyan]")
        
        marks = input_int(f"{subject} (0-100): ", 0, 100)
        s[subject].append(marks)
    
    console.print("[bold green]✓ Results updated successfully![/bold green]")
    save_data(data)

def update_student_marks(data):
    """Allow teacher to update existing marks"""
    show_subheader(f"{SCHOOL_NAME} - Update Student Marks")
    
    if not data['teachers']:
        console.print("[red]No teachers available![/red]")
        return
    
    show_teachers_table(data)
    tid = input_int("Enter Teacher ID: ", 1, 1000)
    teacher = next((t for t in data['teachers'] if t['id'] == tid), None)
    
    if not teacher:
        console.print("[red]Invalid Teacher ID![/red]")
        return
    
    subject = teacher['subject']
    
    roll = input_int("Enter Student Roll Number: ", 1, 1000)
    student = next((s for s in data['students'] if s['roll'] == roll), None)
    
    if not student:
        console.print("[red]Student not found![/red]")
        return
    
    console.print(f"\n[cyan]Student: {student['name']}[/cyan]")
    console.print(f"Current {subject} marks: {student[subject][-1] if student[subject] else 'No marks'}")
    
    exam_num = input_int(f"Which exam to update? (1-{len(student[subject])+1}): ", 1, len(student[subject])+1)
    
    if exam_num <= len(student[subject]):
        # Update existing exam
        new_marks = input_int(f"New marks for {subject}: ", 0, 100)
        student[subject][exam_num - 1] = new_marks
        console.print(f"[green]✓ Updated exam {exam_num} marks to {new_marks}[/green]")
    else:
        # Add new exam
        new_marks = input_int(f"New marks for {subject}: ", 0, 100)
        student[subject].append(new_marks)
        console.print(f"[green]✓ Added new exam with {new_marks} marks[/green]")
    
    save_data(data)

def clear_all_data(data):
    """Clear all results and attendance for a fresh start"""
    show_subheader(f"{SCHOOL_NAME} - Clear All Data")
    
    console.print("[bold red]⚠️ WARNING: This will delete ALL results and attendance records![/bold red]")
    console.print("[yellow]Student accounts and teacher accounts will remain.[/yellow]")
    
    confirm = input("Type 'CONFIRM' to proceed: ")
    
    if confirm == "CONFIRM":
        # Clear student results and attendance
        for student in data['students']:
            student['attendance'] = []
            student['Physics'] = []
            student['Maths'] = []
            student['Chemistry'] = []
            student['Computer'] = []
        
        # Clear teacher attendance
        for teacher in data['teachers']:
            teacher['attendance'] = []
        
        save_data(data)
        console.print("[green]✓ All results and attendance cleared successfully![/green]")
    else:
        console.print("[yellow]Operation cancelled.[/yellow]")
    
    pause()

def clear_student_data(data):
    """Clear data for a specific student"""
    show_subheader(f"{SCHOOL_NAME} - Clear Student Data")
    
    roll = input_int("Enter Student Roll Number: ", 1, 1000)
    student = next((s for s in data['students'] if s['roll'] == roll), None)
    
    if not student:
        console.print("[red]Student not found![/red]")
        return
    
    console.print(f"[yellow]Clear data for {student['name']}?[/yellow]")
    console.print("1. Clear Attendance Only")
    console.print("2. Clear Results Only")
    console.print("3. Clear Both")
    console.print("0. Cancel")
    
    choice = input_int("Choice: ", 0, 3)
    
    if choice == 1:
        student['attendance'] = []
        console.print("[green]✓ Attendance cleared![/green]")
    elif choice == 2:
        student['Physics'] = []
        student['Maths'] = []
        student['Chemistry'] = []
        student['Computer'] = []
        console.print("[green]✓ Results cleared![/green]")
    elif choice == 3:
        student['attendance'] = []
        student['Physics'] = []
        student['Maths'] = []
        student['Chemistry'] = []
        student['Computer'] = []
        console.print("[green]✓ All data cleared![/green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")
        return
    
    save_data(data)
    pause()

# ================== STUDENT PORTAL ==================
def student_portal(data, roll):
    s = next((x for x in data['students'] if x["roll"] == roll), None)
    if not s:
        console.print("[bold red]Student not found.[/bold red]")
        pause()
        return
    
    while True:
        clear()
        show_header(f"{s['name']}'s PORTAL")
        
        attendance = len(s.get('attendance', []))
        percentage = calculate_percentage(s)
        status, color = get_student_status(percentage)
        
        stats_text = Text()
        stats_text.append(f"{SCHOOL_NAME}\n", style="bold yellow")
        stats_text.append(f"Roll Number: {s['roll']}\n", style="cyan")
        stats_text.append(f"Attendance: {attendance} days\n", style="green")
        stats_text.append(f"Average Percentage: {percentage:.1f}%\n", style="yellow")
        stats_text.append(f"Status: ", style="white")
        stats_text.append(f"{status}\n", style=color)
        
        console.print(Panel(stats_text, title="📊 Student Statistics", border_style="blue"))
        
        console.print("\n[bold cyan]1.[/bold cyan] View Results Table")
        console.print("[bold cyan]2.[/bold cyan] View Performance Pie Chart")
        console.print("[bold cyan]3.[/bold cyan] View Attendance Chart")
        console.print("[bold cyan]4.[/bold cyan] View All Records")
        console.print("[bold cyan]5.[/bold cyan] 📄 Download Result Card (PDF)")
        console.print("[bold cyan]0.[/bold cyan] Logout")
        
        choice = input_int("\nChoice: ", 0, 5)
        
        if choice == 0:
            break
        elif choice == 1:
            clear()
            show_subheader(f"{SCHOOL_NAME} - Your Results")
            table = Table(title=f"{s['name']}'s Latest Results", style="bold cyan")
            table.add_column("Subject", style="cyan")
            table.add_column("Marks", justify="center")
            table.add_column("Grade", justify="center")
            table.add_column("Status", justify="center")
            
            subjects = ['Physics', 'Maths', 'Chemistry', 'Computer']
            for subject in subjects:
                marks = s.get(subject, [])
                latest = marks[-1] if marks else "-"
                grade = calculate_grade(marks)
                
                if latest != "-":
                    if latest >= 80:
                        sub_status = "[green]Excellent[/green]"
                    elif latest >= 60:
                        sub_status = "[yellow]Good[/yellow]"
                    else:
                        sub_status = "[red]Needs Work[/red]"
                else:
                    sub_status = "-"
                
                table.add_row(subject, str(latest), grade, sub_status)
            
            console.print(table)
            
            total = calculate_total_marks(s)
            percentage = calculate_percentage(s)
            console.print(f"\n[bold]Total:[/bold] {total}/400 | [bold]Percentage:[/bold] {percentage:.1f}%")
            
            pause()
            
        elif choice == 2:
            clear()
            show_subheader(f"{SCHOOL_NAME} - Performance Chart")
            console.print("[yellow]Closing the chart window to continue...[/yellow]")
            show_pie_chart(s)
            
        elif choice == 3:
            clear()
            show_subheader(f"{SCHOOL_NAME} - Attendance Chart")
            console.print("[yellow]Generating attendance chart...[/yellow]")
            show_attendance_chart(s)
            
        elif choice == 4:
            clear()
            show_subheader(f"{SCHOOL_NAME} - Complete Record")
            table = Table(title=f"{s['name']}'s Exam History", style="bold cyan")
            table.add_column("Exam", style="cyan")
            table.add_column("Date", style="cyan")
            table.add_column("Physics", justify="center")
            table.add_column("Maths", justify="center")
            table.add_column("Chemistry", justify="center")
            table.add_column("Computer", justify="center")
            table.add_column("Total", justify="center")
            
            subjects = ['Physics', 'Maths', 'Chemistry', 'Computer']
            max_exams = max(len(s.get(sub, [])) for sub in subjects) if any(s.get(sub, []) for sub in subjects) else 0
            
            for i in range(max_exams):
                exam_total = 0
                row = [f"Exam {i+1}", datetime.now().strftime("%d-%b-%Y")]
                
                for subject in subjects:
                    marks = s.get(subject, [])
                    if i < len(marks):
                        mark = marks[i]
                        exam_total += mark
                        row.append(str(mark))
                    else:
                        row.append("-")
                
                row.append(str(exam_total))
                table.add_row(*row)
            
            console.print(table)
            pause()
            
        elif choice == 5:
            clear()
            show_subheader(f"{SCHOOL_NAME} - Download Result Card")
            
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description=f"Generating {SCHOOL_NAME} result card...", total=None)
                
                filename = generate_result_card(data, s)
                time.sleep(1)
            
            console.print(f"[green]✓ Result card downloaded successfully![/green]")
            console.print(f"[cyan]Saved to:[/cyan] {filename}")
            console.print("[yellow]Check the 'result_cards' folder in your project directory.[/yellow]")
            
            pause()

# ================== TEACHER PORTAL ==================
def teacher_portal(data, teacher):
    while True:
        clear()
        show_header("TEACHER MENU")
        
        console.print(f"[yellow]Welcome {teacher['name']}[/yellow]")
        console.print(f"[cyan]Subject: {teacher['subject']}[/cyan]")
        
        console.print("\n[bold cyan]1.[/bold cyan] Add Subject Results")
        console.print("[bold cyan]2.[/bold cyan] View All Students Results")
        console.print("[bold cyan]3.[/bold cyan] Update Student Marks")
        
        if teacher.get("class_teacher"):
            console.print("[bold cyan]4.[/bold cyan] Mark Student Attendance")
        
        console.print("[bold cyan]0.[/bold cyan] Logout")
        
        choice = input_int("\nChoice: ", 0, 4)
        
        if choice == 0:
            return
        
        elif choice == 1:
            add_student_results(data, teacher)
        
        elif choice == 2:
            clear()
            show_subheader(f"{SCHOOL_NAME} - All Students - {teacher['subject']} Results")
            show_teacher_students(data, teacher)
            pause()
        
        elif choice == 3:
            update_student_marks(data)
        
        elif choice == 4 and teacher.get("class_teacher"):
            mark_student_attendance(data)
        
        else:
            console.print("[red]Invalid choice![/red]")
        
        pause()

# ================== ADMIN PORTAL ==================

def edit_student(data):
    show_subheader(f"{SCHOOL_NAME} - Edit Student Info")
    
    roll = input_int("Enter Roll Number: ", 1, 1000)
    student = next((s for s in data['students'] if s['roll'] == roll), None)
    
    if not student:
        console.print("[red]Student not found![/red]")
        return
    
    console.print(f"\n[cyan]Editing {student['name']}[/cyan]")
    
    console.print(f"1. Name: {student['name']}")
    console.print(f"2. Email: {student.get('email', 'N/A')}")
    console.print(f"3. Parent Contact: {student.get('parent_contact', 'N/A')}")
    console.print(f"4. Address: {student.get('address', 'N/A')}")
    console.print("5. Change Password")
    console.print("0. Back")
    
    choice = input_int("Select field to edit: ", 0, 5)
    
    if choice == 1:
        student['name'] = input_string("New Name: ")
    elif choice == 2:
        student['email'] = input_email("New Email: ")
    elif choice == 3:
        student['parent_contact'] = input_string("New Contact: ")
    elif choice == 4:
        student['address'] = input_string("New Address: ")
    elif choice == 5:
        student['password'] = input_string("New Password: ", min_len=4)
    
    console.print("[green]✓ Student info updated successfully![/green]")
    save_data(data)

def edit_teacher(data):
    show_subheader(f"{SCHOOL_NAME} - Edit Teacher Info")
    
    teacher_id = input_int("Enter Teacher ID: ", 1, 1000)
    teacher = next((t for t in data['teachers'] if t['id'] == teacher_id), None)
    
    if not teacher:
        console.print("[red]Teacher not found![/red]")
        return
    
    console.print(f"\n[cyan]Editing {teacher['name']}[/cyan]")
    
    console.print(f"1. Name: {teacher['name']}")
    console.print(f"2. Email: {teacher.get('email', 'N/A')}")
    console.print(f"3. Contact: {teacher.get('contact', 'N/A')}")
    console.print(f"4. Subject: {teacher.get('subject', 'N/A')}")
    console.print("5. Change Password")
    console.print("0. Back")
    
    choice = input_int("Select field to edit: ", 0, 5)
    
    if choice == 1:
        teacher['name'] = input_string("New Name: ")
    elif choice == 2:
        teacher['email'] = input_email("New Email: ")
    elif choice == 3:
        teacher['contact'] = input_string("New Contact: ", allow_empty=True)
    elif choice == 4:
        console.print("1. Physics\n2. Maths\n3. Chemistry\n4. Computer")
        subject_choice = input_int("Choice: ", 1, 4)
        subjects = ["Physics", "Maths", "Chemistry", "Computer"]
        teacher['subject'] = subjects[subject_choice - 1]
        teacher['class_teacher'] = True if teacher['subject'] == "Physics" else False
    elif choice == 5:
        teacher['password'] = input_string("New Password: ", min_len=4)
    
    console.print("[green]✓ Teacher info updated successfully![/green]")
    save_data(data)

def admin_portal(data):
    while True:
        clear()
        show_header("ADMIN MENU")
        
        console.print(Panel(
            f"[cyan]{SCHOOL_NAME}[/cyan]\n"
            f"[green]Students: {len(data['students'])} | Teachers: {len(data['teachers'])}[/green]",
            border_style="blue"
        ))
        
        console.print("\n[bold cyan]📊 VIEW SECTION[/bold cyan]")
        console.print("1. View Student Records")
        console.print("2. View Teacher Records")
        console.print("3. Search Student")
        
        console.print("\n[bold cyan]👥 STUDENT MANAGEMENT[/bold cyan]")
        console.print("4. Add New Student")
        console.print("5. Remove Student")
        
        console.print("\n[bold cyan]👨‍🏫 TEACHER MANAGEMENT[/bold cyan]")
        console.print("6. Add New Teacher")
        console.print("7. Remove Teacher")
        console.print("8. Mark Teacher Attendance")
        
        console.print("\n[bold cyan]📝 ACADEMICS[/bold cyan]")
        console.print("9. Add/Update Student Results")
        console.print("10. Update Student Marks (Teacher)")
        
        console.print("\n[bold cyan]✏️ EDIT SECTION[/bold cyan]")
        console.print("11. Edit Student Info")
        console.print("12. Edit Teacher Info")
        
        console.print("\n[bold cyan]🗑️ RESET SECTION[/bold cyan]")
        console.print("13. Clear All Data (Results & Attendance)")
        console.print("14. Clear Specific Student Data")
        
        console.print("\n[bold cyan]0.[/bold cyan] Logout")
        
        choice = input_int("\nChoice: ", 0, 14)
        
        if choice == 0:
            save_data(data)
            return
        elif choice == 1:
            show_students_table(data)
        elif choice == 2:
            show_teachers_table(data)
        elif choice == 3:
            search_student(data)
        elif choice == 4:
            add_student(data)
        elif choice == 5:
            remove_student(data)
        elif choice == 6:
            add_teacher(data)
        elif choice == 7:
            remove_teacher(data)
        elif choice == 8:
            modify_teacher_attendance(data)
        elif choice == 9:
            if not data['teachers']:
                console.print("[red]No teachers available![/red]")
            else:
                show_teachers_table(data)
                tid = input_int("Enter Teacher ID to assign result entry: ", 1, 1000)
                teacher = next((t for t in data['teachers'] if t['id'] == tid), None)
                if teacher:
                    add_student_results(data, teacher)
                else:
                    console.print("[red]Invalid Teacher ID![/red]")
        elif choice == 10:
            update_student_marks(data)
        elif choice == 11:
            edit_student(data)
        elif choice == 12:
            edit_teacher(data)
        elif choice == 13:
            clear_all_data(data)
        elif choice == 14:
            clear_student_data(data)
        
        pause()

# ================== MAIN ==================
def main():
    data = load_data()
    
    while True:
        clear()
        show_header("SCHOOL ERP SYSTEM")
        
        console.print(Panel(
            f"[bold cyan]{SCHOOL_NAME}[/bold cyan]\n"
            f"[dim]{SCHOOL_ADDRESS}[/dim]\n"
            "[yellow]Welcome to School Management System[/yellow]\n\n"
            "[dim]Admin: admin@gmail.com \n"
            "Student: [name]@uhd-schools.edu \n"
            "Teacher: Use email provided during registration \n Passwords Default[/dim]",
            border_style="green"
        ))
        
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        
        if email == "admin@gmail.com" and password == "admin123":
            admin_portal(data)
        
        elif any(t['email'] == email and password == t.get('password', 'teacher123') for t in data['teachers']):
            teacher = next(t for t in data['teachers'] if t['email'] == email)
            teacher_portal(data, teacher)
        
        elif any(s.get('email') == email and password == s.get("password", "student123") for s in data['students']):
            student = next(s for s in data['students'] if s.get('email') == email)
            student_portal(data, student['roll'])
        
        elif email == "break":
            save_data(data)
            console.print(f"[green]Data saved. Goodbye from {SCHOOL_NAME}![/green]")
            break
        
        else:
            console.print("[bold red]Invalid email or password![/bold red]")
            pause()

if __name__ == "__main__":
    main()