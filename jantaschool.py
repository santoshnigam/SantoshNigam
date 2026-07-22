
import streamlit as st
import sqlite3
import uuid
import hashlib
import base64
from datetime import date
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="School Management System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "school.db",
    check_same_thread=False
)

cursor = conn.cursor()


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =========================================================
# CREATE TABLES
# =========================================================

# ADMIN
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")


# STUDENTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    father_name TEXT,
    mother_name TEXT,
    dob TEXT,
    gender TEXT,
    class_name TEXT,
    section TEXT,
    roll_no TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    admission_date TEXT
)
""")


# STUDENT ACCOUNTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT
)
""")


# TEACHERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    subject TEXT,
    qualification TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    joining_date TEXT,
    salary REAL DEFAULT 0
)
""")


# FACULTY
cursor.execute("""
CREATE TABLE IF NOT EXISTS faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT,
    designation TEXT,
    qualification TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    joining_date TEXT,
    salary REAL DEFAULT 0
)
""")


# FEES
cursor.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_no TEXT UNIQUE NOT NULL,
    admission_no TEXT,
    student_name TEXT,
    class_name TEXT,
    fee_type TEXT,
    total_fee REAL DEFAULT 0,
    paid_amount REAL DEFAULT 0,
    due_amount REAL DEFAULT 0,
    payment_method TEXT,
    payment_date TEXT,
    remarks TEXT
)
""")


# PAYMENT REQUEST
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT UNIQUE NOT NULL,
    admission_no TEXT NOT NULL,
    student_name TEXT,
    amount REAL DEFAULT 0,
    payment_method TEXT,
    transaction_id TEXT,
    payment_date TEXT,
    status TEXT DEFAULT 'Pending',
    remarks TEXT
)
""")


# FINANCIAL
cursor.execute("""
CREATE TABLE IF NOT EXISTS finances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL,
    category TEXT,
    amount REAL DEFAULT 0,
    description TEXT,
    transaction_date TEXT
)
""")


# STUDENT ATTENDANCE
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT,
    student_name TEXT,
    class_name TEXT,
    attendance_date TEXT,
    status TEXT,
    remarks TEXT
)
""")


# TEACHER ATTENDANCE
cursor.execute("""
CREATE TABLE IF NOT EXISTS teacher_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT,
    teacher_name TEXT,
    attendance_date TEXT,
    status TEXT,
    remarks TEXT
)
""")


# MARKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT,
    student_name TEXT,
    class_name TEXT,
    exam_name TEXT,
    subject TEXT,
    full_marks REAL,
    pass_marks REAL,
    obtained_marks REAL,
    grade TEXT,
    remarks TEXT
)
""")


# SCHOOL INFORMATION
cursor.execute("""
CREATE TABLE IF NOT EXISTS school_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    principal_name TEXT,
    about TEXT
)
""")


# DEFAULT ADMIN
cursor.execute("""
INSERT OR IGNORE INTO admin_users
(id, username, password)
VALUES (?, ?, ?)
""", (
    1,
    "admin",
    hash_password("admin123")
))


conn.commit()


# =========================================================
# DARK UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #000000 !important;
    color: white !important;
}

.main {
    background-color: #000000 !important;
}

[data-testid="stSidebar"] {
    background: #050505 !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.stApp p,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    color: white !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input {
    background-color: #151515 !important;
    color: white !important;
    border: 1px solid #444 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #151515 !important;
    color: white !important;
}

[data-testid="stForm"] {
    background-color: #0d0d0d !important;
    border: 1px solid #333 !important;
    border-radius: 12px;
    padding: 20px;
}

.stButton > button {
    background-color: #1e3a8a;
    color: white;
    border-radius: 8px;
    border: none;
}

.stButton > button:hover {
    background-color: #2563eb;
}

[data-testid="stMetric"] {
    background-color: #111111;
    padding: 15px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "admission_no" not in st.session_state:
    st.session_state.admission_no = ""


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.title("🏫 School Management System")

    st.write(
        "Admin और Student दोनों के लिए Login Portal"
    )

    tab1, tab2, tab3 = st.tabs([
        "🔐 Admin Login",
        "👨‍🎓 Student Login",
        "📝 Student Register"
    ])


    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    with tab1:

        st.subheader(
            "🔐 Admin Login"
        )

        username = st.text_input(
            "Username",
            key="admin_user"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="admin_pass"
        )

        if st.button(
            "🔐 Login as Admin",
            use_container_width=True
        ):

            cursor.execute("""
            SELECT *
            FROM admin_users
            WHERE username = ?
            AND password = ?
            """, (
                username,
                hash_password(password)
            ))

            user = cursor.fetchone()

            if user:

                st.session_state.logged_in = True

                st.session_state.user_type = "admin"

                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    "Invalid Admin Username or Password"
                )


    # =====================================================
    # STUDENT LOGIN
    # =====================================================

    with tab2:

        st.subheader(
            "👨‍🎓 Student Login"
        )

        username = st.text_input(
            "Student Username",
            key="student_user"
        )

        password = st.text_input(
            "Student Password",
            type="password",
            key="student_pass"
        )

        if st.button(
            "👨‍🎓 Login as Student",
            use_container_width=True
        ):

            cursor.execute("""
            SELECT admission_no
            FROM student_accounts
            WHERE username = ?
            AND password = ?
            """, (
                username,
                hash_password(password)
            ))

            student = cursor.fetchone()

            if student:

                st.session_state.logged_in = True

                st.session_state.user_type = "student"

                st.session_state.username = username

                st.session_state.admission_no = student[0]

                st.rerun()

            else:

                st.error(
                    "Invalid Student Login"
                )


    # =====================================================
    # STUDENT REGISTER
    # =====================================================

    with tab3:

        st.subheader(
            "📝 Student Registration"
        )

        st.info(
            "Registration के लिए पहले Admin द्वारा "
            "Student Record बनाया होना जरूरी है।"
        )

        admission_no = st.text_input(
            "Admission Number",
            key="reg_admission"
        )

        username = st.text_input(
            "Create Username",
            key="reg_username"
        )

        password = st.text_input(
            "Create Password",
            type="password",
            key="reg_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="reg_confirm"
        )

        if st.button(
            "📝 Register",
            use_container_width=True
        ):

            if not admission_no:

                st.error(
                    "Admission Number required."
                )

            elif not username:

                st.error(
                    "Username required."
                )

            elif not password:

                st.error(
                    "Password required."
                )

            elif password != confirm_password:

                st.error(
                    "Password और Confirm Password अलग हैं."
                )

            else:

                cursor.execute("""
                SELECT *
                FROM students
                WHERE admission_no = ?
                """, (
                    admission_no,
                ))

                student = cursor.fetchone()

                if not student:

                    st.error(
                        "Admission Number नहीं मिला. "
                        "पहले Admin से Student Add करवाएं."
                    )

                else:

                    try:

                        cursor.execute("""
                        INSERT INTO student_accounts (
                            admission_no,
                            username,
                            password,
                            created_at
                        )
                        VALUES (?, ?, ?, ?)
                        """, (

                            admission_no,
                            username,
                            hash_password(password),
                            str(date.today())

                        ))

                        conn.commit()

                        st.success(
                            "Registration Successful! "
                            "अब Student Login करें."
                        )

                    except sqlite3.IntegrityError:

                        st.error(
                            "Username या Admission Number "
                            "पहले से registered है."
                        )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    admission_no = st.session_state.admission_no


    cursor.execute("""
    SELECT *
    FROM students
    WHERE admission_no = ?
    """, (
        admission_no,
    ))

    student = cursor.fetchone()


    if not student:

        st.error(
            "Student Record Not Found"
        )

        return


    student_name = student[2]


    # SIDEBAR

    st.sidebar.title(
        "👨‍🎓 Student Portal"
    )

    st.sidebar.write(
        f"Welcome, {student_name}"
    )

    st.sidebar.divider()


    menu = st.sidebar.radio(
        "Student Menu",
        [
            "🏠 Dashboard",
            "👤 My Profile",
            "💰 My Fees",
            "💳 Pay Fee",
            "🧾 My Receipts",
            "📊 My Marks",
            "📅 My Attendance",
            "🔑 My Account"
        ]
    )


    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_type = ""

        st.session_state.username = ""

        st.session_state.admission_no = ""

        st.rerun()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "🏠 Dashboard":

        st.title(
            "🏠 Student Dashboard"
        )

        cursor.execute("""
        SELECT
        COALESCE(SUM(total_fee),0),
        COALESCE(SUM(paid_amount),0),
        COALESCE(SUM(due_amount),0)
        FROM fees
        WHERE admission_no = ?
        """, (
            admission_no,
        ))

        total_fee, paid, due = cursor.fetchone()


        c1, c2, c3 = st.columns(3)

        c1.metric(
            "💰 Total Fee",
            f"Rs. {total_fee:,.2f}"
        )

        c2.metric(
            "✅ Paid",
            f"Rs. {paid:,.2f}"
        )

        c3.metric(
            "📌 Due",
            f"Rs. {due:,.2f}"
        )


        st.divider()

        st.success(
            f"Welcome {student_name}! 👋"
        )


    # =====================================================
    # PROFILE
    # =====================================================

    elif menu == "👤 My Profile":

        st.title(
            "👤 My Profile"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.write(
                f"**Admission No:** {student[1]}"
            )

            st.write(
                f"**Name:** {student[2]}"
            )

            st.write(
                f"**Father Name:** {student[3]}"
            )

            st.write(
                f"**Mother Name:** {student[4]}"
            )

            st.write(
                f"**Date of Birth:** {student[5]}"
            )

            st.write(
                f"**Gender:** {student[6]}"
            )

        with c2:

            st.write(
                f"**Class:** {student[7]}"
            )

            st.write(
                f"**Section:** {student[8]}"
            )

            st.write(
                f"**Roll No:** {student[9]}"
            )

            st.write(
                f"**Phone:** {student[10]}"
            )

            st.write(
                f"**Email:** {student[11]}"
            )

            st.write(
                f"**Address:** {student[12]}"
            )


    # =====================================================
    # FEES
    # =====================================================

    elif menu == "💰 My Fees":

        st.title(
            "💰 My Fee Details"
        )

        cursor.execute("""
        SELECT
        receipt_no,
        fee_type,
        total_fee,
        paid_amount,
        due_amount,
        payment_method,
        payment_date
        FROM fees
        WHERE admission_no = ?
        ORDER BY id DESC
        """, (
            admission_no,
        ))

        data = cursor.fetchall()


        if data:

            st.dataframe(
                data,
                use_container_width=True
            )

        else:

            st.info(
                "Fee Record नहीं मिला."
            )


    # =====================================================
    # PAY FEE
    # =====================================================

    elif menu == "💳 Pay Fee":

        st.title(
            "💳 Pay School Fee"
        )

        cursor.execute("""
        SELECT
        COALESCE(SUM(due_amount),0)
        FROM fees
        WHERE admission_no = ?
        """, (
            admission_no,
        ))

        due = cursor.fetchone()[0]


        st.metric(
            "Current Due",
            f"Rs. {due:,.2f}"
        )


        if due <= 0:

            st.success(
                "🎉 आपकी कोई Fee Due नहीं है."
            )

        else:

            amount = st.number_input(
                "Payment Amount",
                min_value=1.0,
                max_value=float(due),
                value=min(
                    1.0,
                    float(due)
                )
            )


            method = st.selectbox(
                "Payment Method",
                [
                    "eSewa",
                    "Khalti",
                    "Bank Transfer",
                    "Cash"
                ]
            )


            transaction_id = st.text_input(
                "Transaction ID / Reference No."
            )


            remarks = st.text_area(
                "Remarks"
            )


            if st.button(
                "💳 Submit Payment Request",
                use_container_width=True
            ):

                if method != "Cash" and not transaction_id:

                    st.error(
                        "Transaction ID required."
                    )

                else:

                    payment_id = (
                        "PAY-" +
                        str(uuid.uuid4())[:8].upper()
                    )


                    cursor.execute("""
                    INSERT INTO student_payments (
                        payment_id,
                        admission_no,
                        student_name,
                        amount,
                        payment_method,
                        transaction_id,
                        payment_date,
                        status,
                        remarks
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (

                        payment_id,
                        admission_no,
                        student_name,
                        amount,
                        method,
                        transaction_id,
                        str(date.today()),
                        "Pending",
                        remarks

                    ))


                    conn.commit()


                    st.success(
                        f"Payment Request Submitted!"
                    )

                    st.info(
                        f"Payment ID: {payment_id}"
                    )

                    st.warning(
                        "Admin verification के बाद "
                        "Fee account update होगा."
                    )


    # =====================================================
    # RECEIPTS
    # =====================================================

    elif menu == "🧾 My Receipts":

        st.title(
            "🧾 My Fee Receipts"
        )


        cursor.execute("""
        SELECT *
        FROM fees
        WHERE admission_no = ?
        ORDER BY id DESC
        """, (
            admission_no,
        ))


        receipts = cursor.fetchall()


        if not receipts:

            st.info(
                "No receipts found."
            )

        else:

            receipt_options = {
                x[1]: x
                for x in receipts
            }


            selected = st.selectbox(
                "Select Receipt",
                list(
                    receipt_options.keys()
                )
            )


            r = receipt_options[selected]


            receipt_no = r[1]

            student_name = r[3]

            class_name = r[4]

            fee_type = r[5]

            total_fee = r[6]

            paid_amount = r[7]

            due_amount = r[8]

            payment_method = r[9]

            payment_date = r[10]

            remarks = r[11]


            st.subheader(
                "🏫 SCHOOL FEE RECEIPT"
            )


            st.write(
                f"**Receipt:** {receipt_no}"
            )

            st.write(
                f"**Student:** {student_name}"
            )

            st.write(
                f"**Class:** {class_name}"
            )

            st.write(
                f"**Fee Type:** {fee_type}"
            )

            st.write(
                f"**Total:** Rs. {total_fee:,.2f}"
            )

            st.write(
                f"**Paid:** Rs. {paid_amount:,.2f}"
            )

            st.write(
                f"**Due:** Rs. {due_amount:,.2f}"
            )


            # PDF

            pdf_buffer = BytesIO()

            pdf = canvas.Canvas(
                pdf_buffer,
                pagesize=A4
            )

            width, height = A4


            pdf.setFont(
                "Helvetica-Bold",
                20
            )


            pdf.drawCentredString(
                width / 2,
                height - 60,
                "SCHOOL FEE RECEIPT"
            )


            pdf.line(
                50,
                height - 100,
                width - 50,
                height - 100
            )


            y = height - 140


            pdf.setFont(
                "Helvetica",
                12
            )


            lines = [

                f"Receipt No: {receipt_no}",

                f"Student Name: {student_name}",

                f"Class: {class_name}",

                f"Fee Type: {fee_type}",

                f"Total Fee: Rs. {total_fee}",

                f"Paid Amount: Rs. {paid_amount}",

                f"Due Amount: Rs. {due_amount}",

                f"Payment Method: {payment_method}",

                f"Payment Date: {payment_date}",

                f"Remarks: {remarks}"

            ]


            for line in lines:

                pdf.drawString(
                    70,
                    y,
                    line
                )

                y -= 30


            pdf.drawString(
                70,
                y - 40,
                "Authorized Signature"
            )


            pdf.drawString(
                width - 200,
                y - 40,
                "School Stamp"
            )


            pdf.save()


            pdf_buffer.seek(0)

            pdf_data = (
                pdf_buffer.getvalue()
            )


            c1, c2 = st.columns(2)


            with c1:

                st.download_button(
                    "📄 Download PDF",
                    data=pdf_data,
                    file_name=f"{receipt_no}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


            with c2:

                pdf_base64 = base64.b64encode(
                    pdf_data
                ).decode()


                print_html = f"""
                <html>

                <body>

                <embed
                src="data:application/pdf;base64,{pdf_base64}"
                type="application/pdf"
                width="100%"
                height="700px"
                >

                <script>

                window.onload = function() {{

                    setTimeout(
                        function() {{
                            window.print();
                        }},
                        1000
                    );

                }};

                </script>

                </body>

                </html>
                """


                print_data = base64.b64encode(
                    print_html.encode()
                ).decode()


                print_url = (
                    "data:text/html;base64,"
                    + print_data
                )


                st.markdown(
                    f"""
                    <a
                    href="{print_url}"
                    target="_blank"
                    style="
                    display:block;
                    text-align:center;
                    padding:10px;
                    background:#1e3a8a;
                    color:white;
                    text-decoration:none;
                    border-radius:8px;
                    font-weight:bold;
                    "
                    >
                    🖨️ Print Receipt
                    </a>
                    """,
                    unsafe_allow_html=True
                )


    # =====================================================
    # MARKS
    # =====================================================

    elif menu == "📊 My Marks":

        st.title(
            "📊 My Marks"
        )


        cursor.execute("""
        SELECT
        exam_name,
        subject,
        full_marks,
        pass_marks,
        obtained_marks,
        grade,
        remarks
        FROM student_marks
        WHERE admission_no = ?
        ORDER BY id DESC
        """, (
            admission_no,
        ))


        marks = cursor.fetchall()


        if marks:

            st.dataframe(
                marks,
                use_container_width=True
            )

        else:

            st.info(
                "Marks अभी available नहीं हैं."
            )


    # =====================================================
    # ATTENDANCE
    # =====================================================

    elif menu == "📅 My Attendance":

        st.title(
            "📅 My Attendance"
        )


        cursor.execute("""
        SELECT
        attendance_date,
        status,
        remarks
        FROM student_attendance
        WHERE admission_no = ?
        ORDER BY id DESC
        """, (
            admission_no,
        ))


        attendance = cursor.fetchall()


        if attendance:

            st.dataframe(
                attendance,
                use_container_width=True
            )


            total = len(
                attendance
            )


            present = sum(
                1
                for x in attendance
                if x[1] == "Present"
            )


            percentage = (

                present /
                total *
                100

                if total > 0

                else 0

            )


            st.metric(
                "Attendance",
                f"{percentage:.2f}%"
            )


        else:

            st.info(
                "Attendance Record नहीं मिला."
            )


    # =====================================================
    # ACCOUNT
    # =====================================================

    elif menu == "🔑 My Account":

        st.title(
            "🔑 My Account"
        )


        st.write(
            f"Username: **{st.session_state.username}**"
        )


        st.write(
            f"Admission No: **{admission_no}**"
        )


        st.divider()


        st.subheader(
            "🔐 Change Password"
        )


        old_password = st.text_input(
            "Old Password",
            type="password"
        )


        new_password = st.text_input(
            "New Password",
            type="password"
        )


        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )


        if st.button(
            "🔐 Change Password"
        ):


            cursor.execute("""
            SELECT password
            FROM student_accounts
            WHERE admission_no = ?
            """, (
                admission_no,
            ))


            current = cursor.fetchone()


            if hash_password(
                old_password
            ) != current[0]:

                st.error(
                    "Old Password गलत है."
                )


            elif new_password != confirm_password:

                st.error(
                    "New Password match नहीं करता."
                )


            else:

                cursor.execute("""
                UPDATE student_accounts
                SET password = ?
                WHERE admission_no = ?
                """, (

                    hash_password(
                        new_password
                    ),

                    admission_no

                ))


                conn.commit()


                st.success(
                    "Password Changed Successfully!"
                )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard():

    st.sidebar.title(
        "🏫 Admin Panel"
    )


    menu = st.sidebar.radio(
        "Admin Menu",
        [

            "🏠 Dashboard",

            "👨‍🎓 Students",

            "👨‍🏫 Teachers",

            "👥 Faculty",

            "💰 Fees",

            "💳 Payment Approval",

            "🧾 Fee Receipts",

            "📅 Student Attendance",

            "📅 Teacher Attendance",

            "📝 Student Marks",

            "📊 Financial",

            "🏫 About School"

        ]
    )


    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_type = ""

        st.session_state.username = ""

        st.session_state.admission_no = ""

        st.rerun()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "🏠 Dashboard":

        st.title(
            "🏠 Admin Dashboard"
        )


        cursor.execute(
            "SELECT COUNT(*) FROM students"
        )

        students = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(*) FROM teachers"
        )

        teachers = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(*) FROM faculty"
        )

        faculty = cursor.fetchone()[0]


        cursor.execute("""
        SELECT COALESCE(SUM(paid_amount),0)
        FROM fees
        """)

        paid = cursor.fetchone()[0]


        cursor.execute("""
        SELECT COALESCE(SUM(due_amount),0)
        FROM fees
        """)

        due = cursor.fetchone()[0]


        cursor.execute("""
        SELECT COUNT(*)
        FROM student_payments
        WHERE status = 'Pending'
        """)

        pending = cursor.fetchone()[0]


        c1, c2, c3 = st.columns(3)


        c1.metric(
            "👨‍🎓 Students",
            students
        )


        c2.metric(
            "👨‍🏫 Teachers",
            teachers
        )


        c3.metric(
            "👥 Faculty",
            faculty
        )


        c4, c5, c6 = st.columns(3)


        c4.metric(
            "💰 Fees Paid",
            f"Rs. {paid:,.2f}"
        )


        c5.metric(
            "📌 Fees Due",
            f"Rs. {due:,.2f}"
        )


        c6.metric(
            "💳 Pending Payments",
            pending
        )


    # =====================================================
    # STUDENTS
    # =====================================================

    elif menu == "👨‍🎓 Students":

        st.title(
            "👨‍🎓 Student Management"
        )


        tab1, tab2 = st.tabs([
            "➕ Add Student",
            "📋 Records"
        ])


        with tab1:

            with st.form(
                "add_student"
            ):


                c1, c2 = st.columns(2)


                with c1:

                    admission_no = st.text_input(
                        "Admission No *"
                    )

                    name = st.text_input(
                        "Student Name *"
                    )

                    father = st.text_input(
                        "Father Name"
                    )

                    mother = st.text_input(
                        "Mother Name"
                    )

                    dob = st.date_input(
                        "Date of Birth"
                    )

                    gender = st.selectbox(
                        "Gender",
                        [
                            "Male",
                            "Female",
                            "Other"
                        ]
                    )


                with c2:

                    class_name = st.text_input(
                        "Class"
                    )

                    section = st.text_input(
                        "Section"
                    )

                    roll = st.text_input(
                        "Roll No"
                    )

                    phone = st.text_input(
                        "Phone"
                    )

                    email = st.text_input(
                        "Email"
                    )

                    address = st.text_area(
                        "Address"
                    )


                submit = st.form_submit_button(
                    "💾 Save Student",
                    use_container_width=True
                )


                if submit:


                    if not admission_no or not name:

                        st.error(
                            "Admission No और Name required हैं."
                        )


                    else:

                        try:

                            cursor.execute("""
                            INSERT INTO students (
                                admission_no,
                                name,
                                father_name,
                                mother_name,
                                dob,
                                gender,
                                class_name,
                                section,
                                roll_no,
                                phone,
                                email,
                                address,
                                admission_date
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (

                                admission_no,
                                name,
                                father,
                                mother,
                                str(dob),
                                gender,
                                class_name,
                                section,
                                roll,
                                phone,
                                email,
                                address,
                                str(date.today())

                            ))


                            conn.commit()


                            st.success(
                                "Student Added Successfully!"
                            )


                        except sqlite3.IntegrityError:

                            st.error(
                                "Admission No already exists."
                            )


        with tab2:

            cursor.execute("""
            SELECT
            admission_no,
            name,
            class_name,
            section,
            roll_no,
            phone,
            email
            FROM students
            ORDER BY id DESC
            """)


            data = cursor.fetchall()


            st.dataframe(
                data,
                use_container_width=True
            )


    # =====================================================
    # TEACHERS
    # =====================================================

    elif menu == "👨‍🏫 Teachers":

        st.title(
            "👨‍🏫 Teacher Management"
        )


        with st.form(
            "teacher_form"
        ):


            c1, c2 = st.columns(2)


            with c1:

                teacher_id = st.text_input(
                    "Teacher ID *"
                )

                name = st.text_input(
                    "Teacher Name *"
                )

                subject = st.text_input(
                    "Subject"
                )

                qualification = st.text_input(
                    "Qualification"
                )


            with c2:

                phone = st.text_input(
                    "Phone"
                )

                email = st.text_input(
                    "Email"
                )

                address = st.text_area(
                    "Address"
                )

                joining_date = st.date_input(
                    "Joining Date"
                )

                salary = st.number_input(
                    "Salary",
                    min_value=0.0
                )


            submit = st.form_submit_button(
                "💾 Save Teacher",
                use_container_width=True
            )


            if submit:


                if not teacher_id or not name:

                    st.error(
                        "Teacher ID और Name required हैं."
                    )


                else:

                    try:

                        cursor.execute("""
                        INSERT INTO teachers (
                            teacher_id,
                            name,
                            subject,
                            qualification,
                            phone,
                            email,
                            address,
                            joining_date,
                            salary
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (

                            teacher_id,
                            name,
                            subject,
                            qualification,
                            phone,
                            email,
                            address,
                            str(joining_date),
                            salary

                        ))


                        conn.commit()


                        st.success(
                            "Teacher Added!"
                        )


                    except sqlite3.IntegrityError:

                        st.error(
                            "Teacher ID already exists."
                        )


        st.subheader(
            "📋 Teacher Records"
        )


        cursor.execute("""
        SELECT *
        FROM teachers
        ORDER BY id DESC
        """)


        st.dataframe(
            cursor.fetchall(),
            use_container_width=True
        )


    # =====================================================
    # FACULTY
    # =====================================================

    elif menu == "👥 Faculty":

        st.title(
            "👥 Faculty Management"
        )


        with st.form(
            "faculty_form"
        ):


            faculty_id = st.text_input(
                "Faculty ID *"
            )


            name = st.text_input(
                "Name *"
            )


            department = st.text_input(
                "Department"
            )


            designation = st.text_input(
                "Designation"
            )


            qualification = st.text_input(
                "Qualification"
            )


            phone = st.text_input(
                "Phone"
            )


            email = st.text_input(
                "Email"
            )


            salary = st.number_input(
                "Salary",
                min_value=0.0
            )


            submit = st.form_submit_button(
                "💾 Save Faculty"
            )


            if submit:


                try:

                    cursor.execute("""
                    INSERT INTO faculty (
                        faculty_id,
                        name,
                        department,
                        designation,
                        qualification,
                        phone,
                        email,
                        salary
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (

                        faculty_id,
                        name,
                        department,
                        designation,
                        qualification,
                        phone,
                        email,
                        salary

                    ))


                    conn.commit()


                    st.success(
                        "Faculty Added!"
                    )


                except sqlite3.IntegrityError:

                    st.error(
                        "Faculty ID already exists."
                    )


        cursor.execute("""
        SELECT *
        FROM faculty
        ORDER BY id DESC
        """)


        st.dataframe(
            cursor.fetchall(),
            use_container_width=True
        )


    # =====================================================
    # FEES
    # =====================================================

    elif menu == "💰 Fees":

        st.title(
            "💰 Fee Management"
        )


        cursor.execute("""
        SELECT admission_no, name, class_name
        FROM students
        ORDER BY name
        """)


        students = cursor.fetchall()


        if not students:

            st.warning(
                "पहले Student Add करें."
            )


        else:


            student_map = {

                f"{x[0]} - {x[1]} - {x[2]}":
                x

                for x in students

            }


            selected = st.selectbox(
                "Select Student",
                list(
                    student_map.keys()
                )
            )


            student = student_map[selected]


            fee_type = st.selectbox(
                "Fee Type",
                [
                    "Admission Fee",
                    "Monthly Fee",
                    "Exam Fee",
                    "Transport Fee",
                    "Hostel Fee",
                    "Library Fee",
                    "Computer Fee",
                    "Other"
                ]
            )


            total = st.number_input(
                "Total Fee",
                min_value=0.0
            )


            paid = st.number_input(
                "Paid Amount",
                min_value=0.0
            )


            due = max(
                total - paid,
                0
            )


            st.info(
                f"Due: Rs. {due:,.2f}"
            )


            method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "eSewa",
                    "Khalti",
                    "Bank Transfer",
                    "Cheque"
                ]
            )


            remarks = st.text_area(
                "Remarks"
            )


            if st.button(
                "💾 Save Fee"
            ):


                if paid > total:

                    st.error(
                        "Paid amount Total Fee से अधिक नहीं हो सकता."
                    )


                else:


                    receipt_no = (
                        "REC-" +
                        str(uuid.uuid4())[:8].upper()
                    )


                    cursor.execute("""
                    INSERT INTO fees (
                        receipt_no,
                        admission_no,
                        student_name,
                        class_name,
                        fee_type,
                        total_fee,
                        paid_amount,
                        due_amount,
                        payment_method,
                        payment_date,
                        remarks
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (

                        receipt_no,
                        student[0],
                        student[1],
                        student[2],
                        fee_type,
                        total,
                        paid,
                        due,
                        method,
                        str(date.today()),
                        remarks

                    ))


                    if paid > 0:

                        cursor.execute("""
                        INSERT INTO finances (
                            transaction_type,
                            category,
                            amount,
                            description,
                            transaction_date
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """, (

                            "Income",
                            fee_type,
                            paid,
                            f"Fee from {student[1]}",
                            str(date.today())

                        ))


                    conn.commit()


                    st.success(
                        f"Fee Saved! Receipt: {receipt_no}"
                    )


    # =====================================================
    # PAYMENT APPROVAL
    # =====================================================

    elif menu == "💳 Payment Approval":

        st.title(
            "💳 Student Payment Approval"
        )


        cursor.execute("""
        SELECT *
        FROM student_payments
        WHERE status = 'Pending'
        ORDER BY id DESC
        """)


        payments = cursor.fetchall()


        if not payments:

            st.success(
                "No Pending Payments."
            )


        for payment in payments:


            payment_id = payment[1]

            admission_no = payment[2]

            student_name = payment[3]

            amount = payment[4]

            method = payment[5]

            transaction_id = payment[6]

            payment_date = payment[7]

            remarks = payment[9]


            with st.expander(
                f"{payment_id} | "
                f"{student_name} | "
                f"Rs. {amount}"
            ):


                st.write(
                    f"Admission: {admission_no}"
                )


                st.write(
                    f"Payment Method: {method}"
                )


                st.write(
                    f"Transaction ID: {transaction_id}"
                )


                c1, c2 = st.columns(2)


                with c1:


                    if st.button(
                        "✅ Approve",
                        key=f"approve_{payment_id}"
                    ):


                        cursor.execute("""
                        SELECT
                        id,
                        total_fee,
                        paid_amount,
                        due_amount
                        FROM fees
                        WHERE admission_no = ?
                        AND due_amount > 0
                        ORDER BY id ASC
                        LIMIT 1
                        """, (
                            admission_no,
                        ))


                        fee = cursor.fetchone()


                        if fee:


                            fee_id = fee[0]

                            total_fee = fee[1]

                            old_paid = fee[2]


                            new_paid = (
                                old_paid +
                                amount
                            )


                            new_due = max(
                                total_fee -
                                new_paid,
                                0
                            )


                            cursor.execute("""
                            UPDATE fees
                            SET
                            paid_amount = ?,
                            due_amount = ?,
                            payment_method = ?,
                            payment_date = ?
                            WHERE id = ?
                            """, (

                                new_paid,
                                new_due,
                                method,
                                payment_date,
                                fee_id

                            ))


                            cursor.execute("""
                            UPDATE student_payments
                            SET status = 'Approved'
                            WHERE payment_id = ?
                            """, (
                                payment_id,
                            ))


                            cursor.execute("""
                            INSERT INTO finances (
                                transaction_type,
                                category,
                                amount,
                                description,
                                transaction_date
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """, (

                                "Income",
                                "Student Payment",
                                amount,
                                f"Online Fee - {student_name}",
                                payment_date

                            ))


                            conn.commit()


                            st.success(
                                "Payment Approved!"
                            )


                            st.rerun()


                        else:


                            st.error(
                                "Student का Due Fee Record नहीं मिला."
                            )


                with c2:


                    if st.button(
                        "❌ Reject",
                        key=f"reject_{payment_id}"
                    ):


                        cursor.execute("""
                        UPDATE student_payments
                        SET status = 'Rejected'
                        WHERE payment_id = ?
                        """, (
                            payment_id,
                        ))


                        conn.commit()


                        st.warning(
                            "Payment Rejected."
                        )


                        st.rerun()


    # =====================================================
    # FEE RECEIPTS
    # =====================================================

    elif menu == "🧾 Fee Receipts":

        st.title(
            "🧾 Fee Receipts"
        )


        cursor.execute("""
        SELECT
        receipt_no,
        student_name,
        fee_type,
        paid_amount,
        payment_method,
        payment_date
        FROM fees
        ORDER BY id DESC
        """)


        st.dataframe(
            cursor.fetchall(),
            use_container_width=True
        )


    # =====================================================
    # STUDENT ATTENDANCE
    # =====================================================

    elif menu == "📅 Student Attendance":

        st.title(
            "📅 Student Attendance"
        )


        cursor.execute("""
        SELECT admission_no, name, class_name
        FROM students
        ORDER BY name
        """)


        students = cursor.fetchall()


        if students:


            student_map = {

                f"{x[0]} - {x[1]}":
                x

                for x in students

            }


            selected = st.selectbox(
                "Student",
                list(
                    student_map.keys()
                )
            )


            student = student_map[selected]


            attendance_date = st.date_input(
                "Date"
            )


            status = st.selectbox(
                "Status",
                [
                    "Present",
                    "Absent",
                    "Late",
                    "Leave"
                ]
            )


            remarks = st.text_input(
                "Remarks"
            )


            if st.button(
                "💾 Save Attendance"
            ):


                cursor.execute("""
                INSERT INTO student_attendance (
                    admission_no,
                    student_name,
                    class_name,
                    attendance_date,
                    status,
                    remarks
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """, (

                    student[0],
                    student[1],
                    student[2],
                    str(attendance_date),
                    status,
                    remarks

                ))


                conn.commit()


                st.success(
                    "Attendance Saved!"
                )


    # =====================================================
    # TEACHER ATTENDANCE
    # =====================================================

    elif menu == "📅 Teacher Attendance":

        st.title(
            "📅 Teacher Attendance"
        )


        cursor.execute("""
        SELECT teacher_id, name
        FROM teachers
        ORDER BY name
        """)


        teachers = cursor.fetchall()


        if teachers:


            teacher_map = {

                f"{x[0]} - {x[1]}":
                x

                for x in teachers

            }


            selected = st.selectbox(
                "Teacher",
                list(
                    teacher_map.keys()
                )
            )


            teacher = teacher_map[selected]


            attendance_date = st.date_input(
                "Date"
            )


            status = st.selectbox(
                "Status",
                [
                    "Present",
                    "Absent",
                    "Late",
                    "Leave"
                ]
            )


            remarks = st.text_input(
                "Remarks"
            )


            if st.button(
                "💾 Save Teacher Attendance"
            ):


                cursor.execute("""
                INSERT INTO teacher_attendance (
                    teacher_id,
                    teacher_name,
                    attendance_date,
                    status,
                    remarks
                )
                VALUES (?, ?, ?, ?, ?)
                """, (

                    teacher[0],
                    teacher[1],
                    str(attendance_date),
                    status,
                    remarks

                ))


                conn.commit()


                st.success(
                    "Teacher Attendance Saved!"
                )


    # =====================================================
    # MARKS
    # =====================================================

    elif menu == "📝 Student Marks":

        st.title(
            "📝 Student Marks"
        )


        cursor.execute("""
        SELECT admission_no, name, class_name
        FROM students
        ORDER BY name
        """)


        students = cursor.fetchall()


        if students:


            student_map = {

                f"{x[0]} - {x[1]}":
                x

                for x in students

            }


            selected = st.selectbox(
                "Student",
                list(
                    student_map.keys()
                )
            )


            student = student_map[selected]


            exam = st.text_input(
                "Exam Name"
            )


            subject = st.text_input(
                "Subject"
            )


            c1, c2, c3 = st.columns(3)


            with c1:

                full_marks = st.number_input(
                    "Full Marks",
                    min_value=1.0,
                    value=100.0
                )


            with c2:

                pass_marks = st.number_input(
                    "Pass Marks",
                    min_value=0.0,
                    value=40.0
                )


            with c3:

                obtained = st.number_input(
                    "Obtained Marks",
                    min_value=0.0,
                    max_value=float(
                        full_marks
                    )
                )


            percentage = (
                obtained /
                full_marks *
                100
            )


            if percentage >= 80:

                grade = "A+"

            elif percentage >= 70:

                grade = "A"

            elif percentage >= 60:

                grade = "B+"

            elif percentage >= 50:

                grade = "B"

            elif percentage >= 40:

                grade = "C"

            else:

                grade = "F"


            st.info(
                f"Percentage: {percentage:.2f}% | Grade: {grade}"
            )


            remarks = st.text_input(
                "Remarks"
            )


            if st.button(
                "💾 Save Marks"
            ):


                cursor.execute("""
                INSERT INTO student_marks (
                    admission_no,
                    student_name,
                    class_name,
                    exam_name,
                    subject,
                    full_marks,
                    pass_marks,
                    obtained_marks,
                    grade,
                    remarks
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (

                    student[0],
                    student[1],
                    student[2],
                    exam,
                    subject,
                    full_marks,
                    pass_marks,
                    obtained,
                    grade,
                    remarks

                ))


                conn.commit()


                st.success(
                    "Marks Saved!"
                )


    # =====================================================
    # FINANCIAL
    # =====================================================

    elif menu == "📊 Financial":

        st.title(
            "📊 Financial Management"
        )


        c1, c2 = st.columns(2)


        with c1:

            income = st.number_input(
                "Income",
                min_value=0.0
            )


        with c2:

            expense = st.number_input(
                "Expense",
                min_value=0.0
            )


        category = st.text_input(
            "Category"
        )


        description = st.text_input(
            "Description"
        )


        if st.button(
            "💾 Save Transaction"
        ):


            if income > 0:

                cursor.execute("""
                INSERT INTO finances (
                    transaction_type,
                    category,
                    amount,
                    description,
                    transaction_date
                )
                VALUES (?, ?, ?, ?, ?)
                """, (

                    "Income",
                    category,
                    income,
                    description,
                    str(date.today())

                ))


            elif expense > 0:

                cursor.execute("""
                INSERT INTO finances (
                    transaction_type,
                    category,
                    amount,
                    description,
                    transaction_date
                )
                VALUES (?, ?, ?, ?, ?)
                """, (

                    "Expense",
                    category,
                    expense,
                    description,
                    str(date.today())

                ))


            conn.commit()


            st.success(
                "Transaction Saved!"
            )


        cursor.execute("""
        SELECT
        COALESCE(
            SUM(
                CASE
                WHEN transaction_type = 'Income'
                THEN amount
                ELSE 0
                END
            ),0
        ),
        COALESCE(
            SUM(
                CASE
                WHEN transaction_type = 'Expense'
                THEN amount
                ELSE 0
                END
            ),0
        )
        FROM finances
        """)


        total_income, total_expense = (
            cursor.fetchone()
        )


        c1, c2, c3 = st.columns(3)


        c1.metric(
            "Income",
            f"Rs. {total_income:,.2f}"
        )


        c2.metric(
            "Expense",
            f"Rs. {total_expense:,.2f}"
        )


        c3.metric(
            "Balance",
            f"Rs. {total_income - total_expense:,.2f}"
        )


    # =====================================================
    # ABOUT SCHOOL
    # =====================================================

    elif menu == "🏫 About School":

        st.title(
            "🏫 School Information"
        )


        cursor.execute("""
        SELECT *
        FROM school_settings
        ORDER BY id DESC
        LIMIT 1
        """)


        school = cursor.fetchone()


        old = school or (
            0,
            "",
            "",
            "",
            "",
            "",
            ""
        )


        school_name = st.text_input(
            "School Name",
            value=old[1]
        )


        address = st.text_input(
            "Address",
            value=old[2]
        )


        phone = st.text_input(
            "Phone",
            value=old[3]
        )


        email = st.text_input(
            "Email",
            value=old[4]
        )


        principal = st.text_input(
            "Principal",
            value=old[5]
        )


        about = st.text_area(
            "About School",
            value=old[6]
        )


        if st.button(
            "💾 Save School Information"
        ):


            if school:

                cursor.execute("""
                UPDATE school_settings
                SET
                school_name = ?,
                address = ?,
                phone = ?,
                email = ?,
                principal_name = ?,
                about = ?
                WHERE id = ?
                """, (

                    school_name,
                    address,
                    phone,
                    email,
                    principal,
                    about,
                    school[0]

                ))


            else:

                cursor.execute("""
                INSERT INTO school_settings (
                    school_name,
                    address,
                    phone,
                    email,
                    principal_name,
                    about
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """, (

                    school_name,
                    address,
                    phone,
                    email,
                    principal,
                    about

                ))


            conn.commit()


            st.success(
                "School Information Saved!"
            )


# =========================================================
# MAIN ROUTING
# =========================================================

if not st.session_state.logged_in:

    login_page()

    st.stop()


if st.session_state.user_type == "admin":

    admin_dashboard()

elif st.session_state.user_type == "student":

    student_dashboard()


# =========================================================
# CLOSE
# =========================================================

conn.commit()

