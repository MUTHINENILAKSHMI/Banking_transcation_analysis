
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from auth import register_user, login_user
from database import get_connection


# ====================================================
# PAGE CONFIGURATION
# ====================================================

st.set_page_config(
    page_title="Banking Transaction Analysis",
    page_icon="🏦",
    layout="wide"
)


# ====================================================
# CUSTOM DARK BLUE THEME
# ====================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #080F1E;
    color: #F8FAFC;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0D192B 0%,
        #111F35 100%
    );
    border-right: 1px solid #263B56;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #EAF2FC;
}

/* Main headings */
h1 {
    color: #38BDF8 !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #60A5FA !important;
    font-weight: 700 !important;
}

/* Normal text */
p, label {
    color: #E2E8F0;
}

/* Sidebar menu */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 8px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    background-color: #14243A;
    border: 1px solid #263B56;
    border-radius: 9px;
    padding: 9px 12px;
    margin: 2px 0;
    transition: background-color 0.2s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background-color: #1E3A5F;
}

[data-testid="stSidebar"] [role="radiogroup"]
label:has(input:checked) {
    background-color: #075985;
    border: 1px solid #38BDF8;
    border-left: 4px solid #7DD3FC;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    color: #F8FAFC !important;
    font-weight: 600;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        #142742,
        #1D3B60
    );
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #38BDF8;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #BAE6FD !important;
    font-size: 15px !important;
}

/* Metric numbers */
[data-testid="stMetricValue"] {
    color: #FACC15 !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    border: 1px solid #334E68;
    border-radius: 10px;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: #172A45 !important;
    color: #FFFFFF !important;
    border: 1px solid #38BDF8 !important;
}

/* Select boxes */
.stSelectbox [data-baseweb="select"] {
    background-color: #172A45;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background-color: #0284C7;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: bold;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #0369A1;
    color: white;
    border: 1px solid #7DD3FC;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #334E68;
}

</style>
""", unsafe_allow_html=True)

# ====================================================
# LOGIN AND REGISTER
# ====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.logged_in:
    st.title("🏦 Banking Transaction Analysis")
    st.subheader("Bank Staff Portal")

    auth_option = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True
    )
    st.markdown("---")

    if auth_option == "Register":
        st.subheader("📝 Create New Account")
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button(
                "Create Account", use_container_width=True
            )

            if register_button:
                if not full_name.strip() or not email.strip():
                    st.error("Please enter your name and email address.")
                elif "@" not in email or "." not in email.split("@")[-1]:
                    st.error("Please enter a valid email address.")
                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(
                        full_name.strip(), email.strip().lower(), password
                    )
                    if success:
                        st.success("Registration successful!")
                        st.info("Please select Login to continue.")
                    else:
                        st.error(message)
    else:
        st.subheader("🔐 Bank Staff Login")
        with st.form("login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button(
                "Login", use_container_width=True
            )
            if login_button:
                success, result = login_user(email.strip().lower(), password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = result
                    st.rerun()
                else:
                    st.error(result)

    st.stop()



# ====================================================
# DATABASE FUNCTION
# ====================================================

def load_data(query, params=None):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()

        return pd.DataFrame(result)

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ====================================================
# SQL QUERIES
# ====================================================

CUSTOMERS_QUERY = """
SELECT
    customer_id,
    customer_name,
    email,
    phone
FROM customers
ORDER BY customer_name;
"""


HISTORY_QUERY = """
SELECT
    t.transaction_id,
    t.customer_id,
    c.customer_name,
    t.transaction_type,
    t.amount,
    t.transaction_date
FROM transactions t
JOIN customers c
ON t.customer_id = c.customer_id
ORDER BY t.transaction_date DESC;
"""


CUSTOMER_BALANCE_QUERY = """
SELECT
    c.customer_id,
    c.customer_name,
    COALESCE(SUM(
        CASE
            WHEN t.transaction_type = 'Deposit'
                THEN t.amount
            WHEN t.transaction_type = 'Withdrawal'
                THEN -t.amount
            ELSE 0
        END
    ), 0) AS account_balance
FROM customers c
LEFT JOIN transactions t
ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY account_balance DESC;
"""


LARGE_TRANSACTIONS_QUERY = """
SELECT
    t.transaction_id,
    c.customer_name,
    t.transaction_type,
    t.amount,
    t.transaction_date
FROM transactions t
JOIN customers c
ON t.customer_id = c.customer_id
WHERE t.amount >= %s
ORDER BY t.amount DESC;
"""


REPEATED_TRANSACTIONS_QUERY = """
SELECT
    c.customer_name,
    t1.transaction_id AS transaction_1,
    t2.transaction_id AS transaction_2,
    t1.amount AS amount_1,
    t2.amount AS amount_2,
    t1.transaction_date AS time_1,
    t2.transaction_date AS time_2
FROM transactions t1
JOIN transactions t2
ON t1.customer_id = t2.customer_id
AND t1.transaction_id < t2.transaction_id
AND t2.transaction_date >= t1.transaction_date
AND TIMESTAMPDIFF(
    MINUTE,
    t1.transaction_date,
    t2.transaction_date
) <= 5
JOIN customers c
ON t1.customer_id = c.customer_id;
"""


# ====================================================
# HELPER FUNCTIONS
# ====================================================

def money(value):
    return f"₹{float(value):,.2f}"


def style_chart(fig):

    fig.update_layout(
        paper_bgcolor="#080F1E",
        plot_bgcolor="#080F1E",
        font=dict(
            color="#F1F5F9",
            size=13
        ),
        legend_title_font_color="#38BDF8",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    fig.update_xaxes(
        showgrid=False,
        color="#E2E8F0"
    )

    fig.update_yaxes(
        gridcolor="#263B56",
        color="#E2E8F0"
    )

    return fig


def excel_file(dataframe):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Transactions"
        )

    return output.getvalue()


# ====================================================
# LOAD DATABASE DATA
# ====================================================

try:

    customers = load_data(CUSTOMERS_QUERY)

    history = load_data(HISTORY_QUERY)

    balances = load_data(CUSTOMER_BALANCE_QUERY)

    summary = load_data("""
        SELECT
            COUNT(*) AS total_transactions,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'Deposit'
                    THEN amount
                    ELSE 0
                END
            ), 0) AS total_deposits,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'Withdrawal'
                    THEN amount
                    ELSE 0
                END
            ), 0) AS total_withdrawals

        FROM transactions;
    """)

except Exception as error:

    st.error("Unable to connect to MySQL database.")
    st.error(str(error))

    st.info(
        "Check your database.py password "
        "and MySQL server."
    )

    st.stop()


# Convert data types

if not history.empty:

    history["transaction_date"] = pd.to_datetime(
        history["transaction_date"],
        errors="coerce"
    )

    history["amount"] = pd.to_numeric(
        history["amount"],
        errors="coerce"
    )


if not balances.empty:

    balances["account_balance"] = pd.to_numeric(
        balances["account_balance"]
    )


# ====================================================
# SIDEBAR NAVIGATION
# ====================================================


# ====================================================
# SIDEBAR NAVIGATION
# ====================================================

menu_options = {
    "🏠 Dashboard": "Dashboard",
    "💳 Transactions": "Transactions",
    "📊 Monthly Analysis": "Monthly Analysis",
    "👥 Customer Analysis": "Customer Analysis",
    "🔍 Customer Profile": "Customer Profile",
    "🚨 Fraud Detection": "Fraud Detection"
}

selected_menu = st.sidebar.radio(
    "Select Page",
    list(menu_options.keys()),
    label_visibility="collapsed"
)

page = menu_options[selected_menu]

st.sidebar.markdown("---")
st.sidebar.write(f"Welcome, {st.session_state.user['full_name']}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()





# ====================================================
# DASHBOARD
# ====================================================

if page == "Dashboard":

    st.title("🏦 Banking Transaction Dashboard")

    st.write(
        "Monitor deposits, withdrawals and customer transactions."
    )

    if summary.empty:

        st.warning("No transaction data available.")

        st.stop()


    total_customers = len(customers)

    total_transactions = int(
        summary.iloc[0]["total_transactions"]
    )

    deposits = float(
        summary.iloc[0]["total_deposits"]
    )

    withdrawals = float(
        summary.iloc[0]["total_withdrawals"]
    )

    net_balance = deposits - withdrawals


    # Summary cards

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        total_customers
    )

    col2.metric(
        "Total Transactions",
        total_transactions
    )

    col3.metric(
        "Total Deposits",
        money(deposits)
    )

    col4.metric(
        "Total Withdrawals",
        money(withdrawals)
    )


    st.markdown("---")

    st.subheader("Overall Net Transaction Amount")

    st.metric(
        "Net Amount",
        money(net_balance)
    )


    # Charts

    col1, col2 = st.columns(2)


    with col1:

        st.subheader("Deposit vs Withdrawal")

        chart_data = pd.DataFrame({

            "Transaction Type": [
                "Deposit",
                "Withdrawal"
            ],

            "Amount": [
                deposits,
                withdrawals
            ]

        })


        fig = px.pie(
            chart_data,
            names="Transaction Type",
            values="Amount",
            hole=0.5,
            color="Transaction Type",
            color_discrete_map={
                "Deposit": "#38BDF8",
                "Withdrawal": "#A78BFA"
            }
        )


        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )


    with col2:

        st.subheader("Top 10 Customers")

        if not balances.empty:

            top_customers = balances.head(10)

            fig = px.bar(
                top_customers,
                x="customer_name",
                y="account_balance",
                color="account_balance",
                color_continuous_scale="Blues",
                labels={
                    "customer_name": "Customer",
                    "account_balance": "Balance"
                }
            )

            fig.update_yaxes(
                rangemode="tozero",
                tickformat=",.0f"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )


    st.subheader("Recent Transactions")

    st.dataframe(
        history.head(10),
        use_container_width=True,
        hide_index=True
    )


# ====================================================
# TRANSACTIONS
# ====================================================

elif page == "Transactions":

    st.title("💳 Transaction Management")

    st.write(
        "Search, filter and download banking transactions."
    )


    if history.empty:

        st.warning("No transactions found.")

    else:

        # Search

        search = st.text_input(
            "🔍 Search by customer name or transaction ID"
        )


        col1, col2 = st.columns(2)


        with col1:

            transaction_type = st.selectbox(
                "Transaction Type",
                [
                    "All",
                    "Deposit",
                    "Withdrawal"
                ]
            )


        with col2:

            min_date = history["transaction_date"].min().date()

            max_date = history["transaction_date"].max().date()

            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date)
            )


        filtered = history.copy()


        # Transaction type filter

        if transaction_type != "All":

            filtered = filtered[
                filtered["transaction_type"]
                == transaction_type
            ]


        # Date filter

        if len(date_range) == 2:

            start_date, end_date = date_range

            filtered = filtered[
                (
                    filtered["transaction_date"].dt.date
                    >= start_date
                )
                &
                (
                    filtered["transaction_date"].dt.date
                    <= end_date
                )
            ]


        # Search filter

        if search.strip():

            search_text = search.strip()

            filtered = filtered[
                filtered["customer_name"].str.contains(
                    search_text,
                    case=False,
                    na=False
                )
                |
                filtered["transaction_id"].astype(str).str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]


        st.subheader("Filtered Transaction Records")

        st.write(
            "Total Records:",
            len(filtered)
        )


        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )


        # CSV and Excel downloads

        col1, col2 = st.columns(2)


        with col1:

            st.download_button(
                "⬇️ Download CSV",

                data=filtered.to_csv(
                    index=False
                ).encode("utf-8"),

                file_name="banking_transactions.csv",

                mime="text/csv"
            )


        with col2:

            st.download_button(
                "⬇️ Download Excel",

                data=excel_file(filtered),

                file_name="banking_transactions.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# ====================================================
# MONTHLY ANALYSIS
# ====================================================

elif page == "Monthly Analysis":

    st.title("📊 Monthly Transaction Analysis")


    if history.empty:

        st.warning("No transaction data available.")

    else:

        monthly_data = history.copy()


        monthly_data["transaction_date"] = pd.to_datetime(
            monthly_data["transaction_date"],
            errors="coerce"
        )


        monthly_data = monthly_data.dropna(
            subset=["transaction_date"]
        )


        # Extract month and year

        monthly_data["Month"] = (
            monthly_data["transaction_date"]
            .dt.strftime("%Y-%m")
        )


        # Monthly deposits and withdrawals

        monthly_summary = (
            monthly_data.groupby(
                ["Month", "transaction_type"],
                as_index=False
            )["amount"]
            .sum()
            .sort_values("Month")
        )


        st.subheader(
            "Monthly Deposits and Withdrawals"
        )


        fig = px.bar(
            monthly_summary,
            x="Month",
            y="amount",
            color="transaction_type",
            barmode="group",

            color_discrete_map={
                "Deposit": "#38BDF8",
                "Withdrawal": "#A78BFA"
            },

            labels={
                "Month": "Month",
                "amount": "Transaction Amount (₹)",
                "transaction_type": "Transaction Type"
            }
        )


        fig.update_xaxes(
            type="category",
            categoryorder="category ascending"
        )

        fig.update_yaxes(
            rangemode="tozero",
            tickformat=",.0f",
            title="Transaction Amount (₹)"
        )


        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )


        st.markdown("---")

        st.subheader(
            "Monthly Transaction Trend"
        )


        monthly_total = (
            monthly_data.groupby(
                "Month",
                as_index=False
            )["amount"]
            .sum()
            .sort_values("Month")
        )


        fig = px.line(
            monthly_total,
            x="Month",
            y="amount",
            markers=True,

            color_discrete_sequence=[
                "#38BDF8"
            ],

            labels={
                "Month": "Month",
                "amount": "Total Transaction Amount (₹)"
            }
        )


        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=10)
        )


        fig.update_xaxes(
            type="category",
            categoryorder="category ascending"
        )

        fig.update_yaxes(
            rangemode="tozero",
            tickformat=",.0f",
            title="Total Transaction Amount (₹)"
        )


        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )


        st.subheader("Monthly Summary")

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True
        )


# ====================================================
# CUSTOMER ANALYSIS
# ====================================================

elif page == "Customer Analysis":

    st.title("👥 Customer Analysis")


    if history.empty:

        st.warning("No transaction data available.")

    else:

        col1, col2 = st.columns(2)


        with col1:

            st.subheader(
                "Customer Transaction Totals"
            )


            customer_totals = (
                history.groupby("customer_name")["amount"]
                .sum()
                .reset_index()
                .sort_values(
                    "amount",
                    ascending=False
                )
            )


            st.dataframe(
                customer_totals,
                use_container_width=True,
                hide_index=True
            )


        with col2:

            st.subheader(
                "Customer Account Balances"
            )


            st.dataframe(
                balances,
                use_container_width=True,
                hide_index=True
            )


        if not customer_totals.empty:

            fig = px.bar(
                customer_totals.head(10),
                x="customer_name",
                y="amount",

                color="amount",
                color_continuous_scale="Blues",

                labels={
                    "customer_name": "Customer",
                    "amount": "Total Transaction Amount"
                }
            )


            fig.update_yaxes(
                rangemode="tozero",
                tickformat=",.0f"
            )


            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )


# ====================================================
# CUSTOMER PROFILE
# ====================================================

elif page == "Customer Profile":

    st.title("🔍 Customer Profile")


    if customers.empty:

        st.warning("No customer records available.")

    else:

        selected_name = st.selectbox(
            "Select Customer",
            customers["customer_name"].tolist()
        )


        selected_customer = customers[
            customers["customer_name"] == selected_name
        ].iloc[0]


        customer_id = int(
            selected_customer["customer_id"]
        )


        st.subheader("Customer Information")


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Customer ID",
            customer_id
        )

        col2.metric(
            "Email",
            selected_customer["email"]
        )

        col3.metric(
            "Phone",
            selected_customer["phone"]
        )


        if not history.empty:

            customer_history = history[
                history["customer_id"] == customer_id
            ].copy()

        else:

            customer_history = pd.DataFrame()


        customer_balance = balances[
            balances["customer_id"] == customer_id
        ]


        balance = (

            float(
                customer_balance.iloc[0]["account_balance"]
            )

            if not customer_balance.empty

            else 0

        )


        if not customer_history.empty:

            deposits = customer_history.loc[
                customer_history["transaction_type"] == "Deposit",
                "amount"
            ].sum()


            withdrawals = customer_history.loc[
                customer_history["transaction_type"] == "Withdrawal",
                "amount"
            ].sum()

        else:

            deposits = 0

            withdrawals = 0


        st.markdown("---")

        st.subheader(
            "Customer Account Summary"
        )


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Total Deposits",
            money(deposits)
        )

        col2.metric(
            "Total Withdrawals",
            money(withdrawals)
        )

        col3.metric(
            "Account Balance",
            money(balance)
        )


        st.subheader("Transaction History")


        if customer_history.empty:

            st.info(
                "No transactions found for this customer."
            )

        else:

            st.dataframe(
                customer_history,
                use_container_width=True,
                hide_index=True
            )


            profile_chart = (
                customer_history.groupby(
                    "transaction_type"
                )["amount"]
                .sum()
                .reset_index()
            )


            fig = px.pie(
                profile_chart,
                names="transaction_type",
                values="amount",
                hole=0.5,

                color="transaction_type",

                color_discrete_map={
                    "Deposit": "#38BDF8",
                    "Withdrawal": "#A78BFA"
                }
            )


            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )


# ====================================================
# FRAUD DETECTION
# ====================================================

elif page == "Fraud Detection":

    st.title("🚨 Fraud Detection and Alerts")


    st.write(
        "Identify unusually large transactions and repeated "
        "transactions within a short time interval."
    )


    # Large transaction threshold

    threshold = st.number_input(
        "Set Large Transaction Alert Threshold (₹)",

        min_value=1.0,

        value=50000.0,

        step=5000.0
    )


    large_transactions = load_data(
        LARGE_TRANSACTIONS_QUERY,
        (threshold,)
    )


    st.subheader(
        "⚠️ Large Transaction Alerts"
    )


    if large_transactions.empty:

        st.success(
            "No transactions found above the selected threshold."
        )

    else:

        st.warning(
            f"{len(large_transactions)} potentially unusual "
            "transaction(s) found."
        )


        st.dataframe(
            large_transactions,
            use_container_width=True,
            hide_index=True
        )


    st.markdown("---")


    st.subheader(
        "Repeated Transactions Within 5 Minutes"
    )


    repeated_transactions = load_data(
        REPEATED_TRANSACTIONS_QUERY
    )


    if repeated_transactions.empty:

        st.success(
            "No repeated transactions found within 5 minutes."
        )

    else:

        st.warning(
            f"{len(repeated_transactions)} possible repeated "
            "transaction pair(s) found."
        )


        st.dataframe(
            repeated_transactions,
            use_container_width=True,
            hide_index=True
        )


    st.caption(
        "Note: These are potential fraud indicators, "
        "not confirmation of fraud."
    )


# ====================================================
# FOOTER
# ====================================================

st.markdown("---")


st.markdown(
    """
    <div style="
        text-align:center;
        color:#94A3B8;
        padding:10px;
    ">
        Banking Transaction Analysis System
        <br>
        Developed using Python, MySQL and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
