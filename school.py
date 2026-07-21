import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import os
import uuid
from datetime import date

# =========================================================
# CONFIG
# =========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

st.set_page_config(
    page_title="School Management System",
    page_icon="🏫",
    layout="wide"
)

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SUPABASE_URL और SUPABASE_KEY .env file में डालें")
    st.stop()

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#111827,#1e3a8a);
}

[data-testid="stSidebar"] * {
    color: white;
}

.dashboard-card {
    padding: 20px;
    border-radius: 15px;
    background: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    text-align: center;
}

.dashboard-card h2 {
    color: #1e3a8a;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================================================
# LOGIN
# =========================================================

def login_page():

    st.title("🏫 School Management System")

    st.subheader("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login", type="primary"):

        result = supabase.table(
            "admin_users"
        ).select("*").eq(
            "username",
            username
        ).eq(
            "password",
            password
        ).execute()

        if result.data:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success("Login Successful")
            st.rerun()

        else:

            st.error(
                "Invalid Username or Password"
            )


if not st.session_state.logged_in:

    login_page()
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏫 SCHOOL SYSTEM")

st.sidebar.write(
    f"Welcome, {st.session_state.username}"
)

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👨‍🎓 Students",
        "👨‍🏫 Teachers",
        "💰 Fees",
        "🧾 Fee Receipt",
        "📊 Financial",
        "🏫 About School"
    ]
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

if menu == "🏠 Dashboard":

    st.title("🏠 School Dashboard")

    students = supabase.table(
        "students"
    ).select("*").execute().data

    teachers = supabase.table(
        "teachers"
    ).select("*").execute().data

    fees = supabase.table(
        "fees"
    ).select("*").execute().data

    finances = supabase.table(
        "finances"
    ).select("*").execute().data

    total_students = len(students)
    total_teachers = len(teachers)

    total_paid = sum(
        float(x["paid_amount"] or 0)
        for x in fees
    )

    total_due = sum(
        float(x["due_amount"] or 0)
        for x in fees
    )

    income = sum(
        float(x["amount"] or 0)
        for x in finances
        if x["transaction_type"] == "Income"
    )

    expense = sum(
        float(x["amount"] or 0)
        for x in finances
        if x["transaction_type"] == "Expense"
    )

    balance = income - expense

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "👨‍🎓 Students",
            total_students
        )

    with c2:
        st.metric(
            "👨‍🏫 Teachers",
            total_teachers
        )

    with c3:
        st.metric(
            "💰 Fees Collected",
            f"Rs. {total_paid:,.2f}"
        )

    with c4:
        st.metric(
            "📌 Fee Due",
            f"Rs. {total_due:,.2f}"
        )

    st.divider()

    c5, c6, c7 = st.columns(3)

    with c5:
        st.metric(
            "📈 Total Income",
            f"Rs. {income:,.2f}"
        )

    with c6:
        st.metric(
            "📉 Total Expense",
            f"Rs. {expense:,.2f}"
        )

    with c7:
        st.metric(
            "💵 Balance",
            f"Rs. {balance:,.2f}"
        )


# =========================================================
# STUDENTS
# =========================================================

elif menu == "👨‍🎓 Students":

    st.title("👨‍🎓 Student Management")

    tab1, tab2 = st.tabs(
        [
            "➕ Add Student",
            "📋 Student Records"
        ]
    )

    with tab1:

        with st.form("student_form"):

            c1, c2 = st.columns(2)

            with c1:

                admission_no = st.text_input(
                    "Admission No *"
                )

                name = st.text_input(
                    "Student Name *"
                )

                father_name = st.text_input(
                    "Father Name"
                )

                mother_name = st.text_input(
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

                roll_no = st.text_input(
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
                "Save Student"
            )

            if submit:

                if not admission_no or not name:

                    st.error(
                        "Admission No और Name required हैं"
                    )

                else:

                    try:

                        supabase.table(
                            "students"
                        ).insert({

                            "admission_no":
                                admission_no,

                            "name":
                                name,

                            "father_name":
                                father_name,

                            "mother_name":
                                mother_name,

                            "dob":
                                str(dob),

                            "gender":
                                gender,

                            "class_name":
                                class_name,

                            "section":
                                section,

                            "roll_no":
                                roll_no,

                            "phone":
                                phone,

                            "email":
                                email,

                            "address":
                                address

                        }).execute()

                        st.success(
                            "Student saved successfully"
                        )

                    except Exception as e:

                        st.error(str(e))


    with tab2:

        search = st.text_input(
            "🔍 Search Student"
        )

        data = supabase.table(
            "students"
        ).select("*").execute().data

        if search:

            data = [

                x for x in data

                if search.lower()
                in str(x).lower()

            ]

        if data:

            st.dataframe(
                data,
                use_container_width=True
            )

        else:

            st.info(
                "No student records found"
            )


# =========================================================
# TEACHERS
# =========================================================

elif menu == "👨‍🏫 Teachers":

    st.title("👨‍🏫 Teacher Management")

    tab1, tab2 = st.tabs(
        [
            "➕ Add Teacher",
            "📋 Teacher Records"
        ]
    )

    with tab1:

        with st.form("teacher_form"):

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
                "Monthly Salary",
                min_value=0.0
            )

            submit = st.form_submit_button(
                "Save Teacher"
            )

            if submit:

                if not teacher_id or not name:

                    st.error(
                        "Teacher ID और Name required हैं"
                    )

                else:

                    try:

                        supabase.table(
                            "teachers"
                        ).insert({

                            "teacher_id":
                                teacher_id,

                            "name":
                                name,

                            "subject":
                                subject,

                            "qualification":
                                qualification,

                            "phone":
                                phone,

                            "email":
                                email,

                            "address":
                                address,

                            "joining_date":
                                str(joining_date),

                            "salary":
                                salary

                        }).execute()

                        st.success(
                            "Teacher saved successfully"
                        )

                    except Exception as e:

                        st.error(str(e))


    with tab2:

        teachers = supabase.table(
            "teachers"
        ).select("*").execute().data

        st.dataframe(
            teachers,
            use_container_width=True
        )


# =========================================================
# FEES
# =========================================================

elif menu == "💰 Fees":

    st.title("💰 Fee Management")

    students = supabase.table(
        "students"
    ).select("*").execute().data

    if not students:

        st.warning(
            "पहले Student add करें"
        )

    else:

        student_options = {

            f"{x['admission_no']} - {x['name']}":
            x

            for x in students

        }

        selected = st.selectbox(
            "Select Student",
            list(student_options.keys())
        )

        student = student_options[selected]

        with st.form("fee_form"):

            fee_type = st.selectbox(
                "Fee Type",
                [
                    "Admission Fee",
                    "Monthly Fee",
                    "Exam Fee",
                    "Transport Fee",
                    "Library Fee",
                    "Computer Fee",
                    "Other"
                ]
            )

            total_fee = st.number_input(
                "Total Fee",
                min_value=0.0
            )

            paid_amount = st.number_input(
                "Paid Amount",
                min_value=0.0
            )

            due_amount = max(
                total_fee - paid_amount,
                0
            )

            st.info(
                f"Due Amount: Rs. {due_amount:,.2f}"
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "Bank Transfer",
                    "eSewa",
                    "Khalti",
                    "Cheque"
                ]
            )

            remarks = st.text_area(
                "Remarks"
            )

            submit = st.form_submit_button(
                "💾 Save Fee"
            )

            if submit:

                receipt_no = (
                    "REC-" +
                    str(uuid.uuid4())[:8].upper()
                )

                supabase.table(
                    "fees"
                ).insert({

                    "receipt_no":
                        receipt_no,

                    "admission_no":
                        student["admission_no"],

                    "student_name":
                        student["name"],

                    "class_name":
                        student["class_name"],

                    "fee_type":
                        fee_type,

                    "total_fee":
                        total_fee,

                    "paid_amount":
                        paid_amount,

                    "due_amount":
                        due_amount,

                    "payment_method":
                        payment_method,

                    "remarks":
                        remarks

                }).execute()

                # Financial Income

                if paid_amount > 0:

                    supabase.table(
                        "finances"
                    ).insert({

                        "transaction_type":
                            "Income",

                        "category":
                            fee_type,

                        "amount":
                            paid_amount,

                        "description":
                            f"Fee from {student['name']}"

                    }).execute()

                st.success(
                    f"Fee saved. Receipt No: {receipt_no}"
                )


# =========================================================
# RECEIPT
# =========================================================

elif menu == "🧾 Fee Receipt":

    st.title("🧾 Fee Receipt")

    fees = supabase.table(
        "fees"
    ).select("*").order(
        "created_at",
        desc=True
    ).execute().data

    if not fees:

        st.info(
            "No fee receipt found"
        )

    else:

        receipt_options = {

            x["receipt_no"]: x

            for x in fees

        }

        receipt_no = st.selectbox(
            "Select Receipt",
            list(receipt_options.keys())
        )

        r = receipt_options[receipt_no]

        st.subheader(
            "🏫 SCHOOL FEE RECEIPT"
        )

        st.write(
            f"**Receipt No:** {r['receipt_no']}"
        )

        st.write(
            f"**Student:** {r['student_name']}"
        )

        st.write(
            f"**Admission No:** {r['admission_no']}"
        )

        st.write(
            f"**Class:** {r['class_name']}"
        )

        st.write(
            f"**Fee Type:** {r['fee_type']}"
        )

        st.write(
            f"**Total Fee:** Rs. {r['total_fee']}"
        )

        st.write(
            f"**Paid:** Rs. {r['paid_amount']}"
        )

        st.write(
            f"**Due:** Rs. {r['due_amount']}"
        )

        st.write(
            f"**Payment:** {r['payment_method']}"
        )

        # PDF

        pdf_buffer = BytesIO()

        pdf = canvas.Canvas(
            pdf_buffer,
            pagesize=A4
        )

        pdf.setFont(
            "Helvetica-Bold",
            18
        )

        pdf.drawCentredString(
            300,
            800,
            "SCHOOL FEE RECEIPT"
        )

        pdf.setFont(
            "Helvetica",
            12
        )

        y = 750

        lines = [

            f"Receipt No: {r['receipt_no']}",

            f"Student Name: {r['student_name']}",

            f"Admission No: {r['admission_no']}",

            f"Class: {r['class_name']}",

            f"Fee Type: {r['fee_type']}",

            f"Total Fee: Rs. {r['total_fee']}",

            f"Paid Amount: Rs. {r['paid_amount']}",

            f"Due Amount: Rs. {r['due_amount']}",

            f"Payment Method: {r['payment_method']}",

            f"Date: {r['payment_date']}"

        ]

        for line in lines:

            pdf.drawString(
                80,
                y,
                line
            )

            y -= 30

        pdf.drawString(
            80,
            y - 30,
            "Authorized Signature"
        )

        pdf.save()

        pdf_buffer.seek(0)

        st.download_button(

            label="📄 Download PDF Receipt",

            data=pdf_buffer,

            file_name=
                f"{r['receipt_no']}.pdf",

            mime="application/pdf"

        )


# =========================================================
# FINANCIAL
# =========================================================

elif menu == "📊 Financial":

    st.title("📊 Financial Management")

    tab1, tab2 = st.tabs(
        [
            "➕ Add Transaction",
            "📈 Financial Report"
        ]
    )

    with tab1:

        with st.form("finance_form"):

            transaction_type = st.selectbox(
                "Transaction Type",
                [
                    "Income",
                    "Expense"
                ]
            )

            category = st.text_input(
                "Category"
            )

            amount = st.number_input(
                "Amount",
                min_value=0.0
            )

            description = st.text_area(
                "Description"
            )

            submit = st.form_submit_button(
                "Save Transaction"
            )

            if submit:

                supabase.table(
                    "finances"
                ).insert({

                    "transaction_type":
                        transaction_type,

                    "category":
                        category,

                    "amount":
                        amount,

                    "description":
                        description

                }).execute()

                st.success(
                    "Transaction saved"
                )


    with tab2:

        finances = supabase.table(
            "finances"
        ).select("*").execute().data

        income = sum(

            float(x["amount"])

            for x in finances

            if x["transaction_type"]
            == "Income"

        )

        expense = sum(

            float(x["amount"])

            for x in finances

            if x["transaction_type"]
            == "Expense"

        )

        balance = income - expense

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Income",
            f"Rs. {income:,.2f}"
        )

        c2.metric(
            "Total Expense",
            f"Rs. {expense:,.2f}"
        )

        c3.metric(
            "Balance",
            f"Rs. {balance:,.2f}"
        )

        st.dataframe(
            finances,
            use_container_width=True
        )


# =========================================================
# ABOUT SCHOOL
# =========================================================

elif menu == "🏫 About School":

    st.title("🏫 About School")

    result = supabase.table(
        "school_settings"
    ).select("*").limit(
        1
    ).execute()

    current = (
        result.data[0]
        if result.data
        else {}
    )

    with st.form("school_form"):

        school_name = st.text_input(
            "School Name",
            value=current.get(
                "school_name",
                ""
            )
        )

        address = st.text_input(
            "Address",
            value=current.get(
                "address",
                ""
            )
        )

        phone = st.text_input(
            "Phone",
            value=current.get(
                "phone",
                ""
            )
        )

        email = st.text_input(
            "Email",
            value=current.get(
                "email",
                ""
            )
        )

        principal = st.text_input(
            "Principal Name",
            value=current.get(
                "principal_name",
                ""
            )
        )

        about = st.text_area(
            "About School",
            value=current.get(
                "about",
                ""
            )
        )

        submit = st.form_submit_button(
            "Save School Information"
        )

        if submit:

            data = {

                "school_name":
                    school_name,

                "address":
                    address,

                "phone":
                    phone,

                "email":
                    email,

                "principal_name":
                    principal,

                "about":
                    about

            }

            if current:

                supabase.table(
                    "school_settings"
                ).update(
                    data
                ).eq(
                    "id",
                    current["id"]
                ).execute()

            else:

                supabase.table(
                    "school_settings"
                ).insert(
                    data
                ).execute()

            st.success(
                "School information updated"
            )