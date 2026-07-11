import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ISV Requirements Management",
    page_icon="⬢",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION SETTINGS
# ============================================================

DATABASE_FILE = Path("isv_requirements.db")

ALLOWED_PROJECTS = [
    "S.TM10735",
    "S.TM11089",
    "S.TM11113",
]

PROJECT_REQUIREMENT_CATEGORIES = [
    "Operating condition",
    "Capacity or quantity",
    "Performance level",
    "Response time",
    "Compatibility or interface",
    "Product type or standard",
    "Reliability or maintenance",
    "Other requirement",
]

VERIFICATION_POINTS = [
    "Requirements review",
    "Concept design review",
    "Approval drawing review",
    "Detailed design review",
    "Manufacturing inspection",
    "Assembly / Factory Acceptance Test",
    "Site commissioning",
    "Final project acceptance",
]

VERIFICATION_METHODS = [
    "Document review",
    "Drawing review",
    "Design review",
    "Calculation",
    "Simulation",
    "Inspection",
    "Functional test",
    "Factory Acceptance Test",
    "Site Acceptance Test",
    "Demonstration",
]

MILL_TYPES = [
    "FFM",
    "FIM",
    "FRM",
    "CM",
    "HM",
    "Other",
]

ISV_PRODUCT_VARIANTS = [
    "ISV - MK3",
    "ISV - E",
    "ISV - EC",
    "ISV - EX",
]

MK3_CONFIGURATIONS = [
    "Standard",
    "Narrow",
    "Narrow reduced outlet",
]

PITCHING_TYPES = [
    "Uniform pitching",
    "Hybrid pitching",
]

OPERATING_FLUIDS = [
    "Water",
    "Emulsion",
    "Kerosene",
    "Other",
]

ENGINEERING_DELIVERABLES = [
    "Requirements baseline committed",
    "Initial layout complete",
    "Layout issued internally",
    "Layout sent to customer",
    "Layout approved",
    "Detailed design complete",
    "Manufacturing drawings issued",
    "Detailing sent to manufacture",
]


# ============================================================
# CUSTOM DARK DASHBOARD THEME
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    :root {
        --page-bg: #050b18;
        --panel-bg: rgba(12, 25, 52, 0.88);
        --panel-bg-soft: rgba(16, 31, 63, 0.72);
        --panel-border: rgba(115, 151, 220, 0.22);
        --text-main: #f5f7ff;
        --text-soft: #aeb9d2;
        --purple: #8d55ff;
        --purple-light: #b96cff;
        --cyan: #18d9ff;
        --blue: #2586ff;
        --green: #36e4a0;
        --orange: #ff9d32;
    }

    html,
    body,
    [class*="css"] {
        font-family:
            Inter,
            "Segoe UI",
            Arial,
            sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 82% 8%,
                rgba(0, 198, 255, 0.11),
                transparent 25%
            ),
            radial-gradient(
                circle at 8% 12%,
                rgba(130, 70, 255, 0.14),
                transparent 24%
            ),
            linear-gradient(
                145deg,
                #050a15 0%,
                #071328 50%,
                #061022 100%
            );
        color: var(--text-main);
    }

    .block-container {
        max-width: 1550px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(10, 24, 55, 0.98) 0%,
                rgba(7, 17, 38, 0.98) 100%
            );
        border-right:
            1px solid rgba(106, 133, 197, 0.24);
        box-shadow:
            18px 0 45px rgba(0, 0, 0, 0.28);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label {
        border:
            1px solid transparent;
        border-radius:
            14px;
        padding:
            0.8rem 0.9rem;
        margin:
            0.18rem 0;
        color:
            #cbd5ea;
        transition:
            all 0.2s ease;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label:hover {
        background:
            rgba(79, 116, 255, 0.13);
        border-color:
            rgba(79, 116, 255, 0.28);
    }

    section[data-testid="stSidebar"]
    div[data-testid="stRadio"]
    label:has(input:checked) {
        background:
            linear-gradient(
                135deg,
                rgba(126, 70, 255, 0.72),
                rgba(34, 112, 255, 0.50)
            );
        border-color:
            rgba(160, 108, 255, 0.65);
        box-shadow:
            0 0 24px rgba(125, 74, 255, 0.22);
        color:
            white;
    }


    /* --------------------------------------------------------
       HEADINGS
    -------------------------------------------------------- */

    h1 {
        color:
            #ffffff;
        letter-spacing:
            -0.04em;
        font-weight:
            760;
    }

    h2,
    h3 {
        color:
            #f5f7ff;
        letter-spacing:
            -0.02em;
    }

    p,
    span,
    label {
        color:
            #d8e0f2;
    }


    /* --------------------------------------------------------
       FORM CONTROLS
    -------------------------------------------------------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        background:
            rgba(6, 17, 39, 0.78) !important;
        border:
            1px solid rgba(108, 139, 201, 0.38) !important;
        border-radius:
            11px !important;
        box-shadow:
            inset 0 0 0 1px rgba(255, 255, 255, 0.015);
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color:
            rgba(72, 211, 255, 0.85) !important;
        box-shadow:
            0 0 0 2px rgba(35, 196, 255, 0.10),
            0 0 18px rgba(35, 196, 255, 0.10);
    }

    input,
    textarea {
        color:
            white !important;
    }

    input::placeholder,
    textarea::placeholder {
        color:
            #76839f !important;
    }

    div[data-baseweb="select"] span {
        color:
            #ecf2ff !important;
    }

    div[data-testid="stNumberInput"] input {
        color:
            white !important;
    }


    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button {
        width:
            100%;
        min-height:
            3rem;
        border:
            1px solid rgba(121, 91, 255, 0.60);
        border-radius:
            12px;
        background:
            linear-gradient(
                105deg,
                #7a35f6 0%,
                #6956ff 42%,
                #169ff6 72%,
                #05d6d6 100%
            );
        color:
            white;
        font-weight:
            720;
        box-shadow:
            0 0 20px rgba(101, 62, 255, 0.24),
            0 0 20px rgba(0, 202, 255, 0.12);
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        transform:
            translateY(-1px);
        color:
            white;
        border-color:
            rgba(80, 225, 255, 0.82);
        box-shadow:
            0 0 28px rgba(111, 70, 255, 0.33),
            0 0 22px rgba(0, 216, 255, 0.21);
    }


    /* --------------------------------------------------------
       EXPANDERS
    -------------------------------------------------------- */

    details[data-testid="stExpander"] {
        background:
            linear-gradient(
                145deg,
                rgba(14, 28, 58, 0.90),
                rgba(7, 20, 44, 0.86)
            );
        border:
            1px solid rgba(96, 132, 205, 0.26);
        border-radius:
            14px;
        margin-bottom:
            0.85rem;
        box-shadow:
            0 12px 30px rgba(0, 0, 0, 0.16);
    }

    details[data-testid="stExpander"] summary {
        font-weight:
            700;
        color:
            #f4f7ff;
    }


    /* --------------------------------------------------------
       DATAFRAMES
    -------------------------------------------------------- */

    div[data-testid="stDataFrame"] {
        border:
            1px solid rgba(92, 128, 202, 0.28);
        border-radius:
            14px;
        overflow:
            hidden;
        background:
            rgba(7, 18, 40, 0.74);
        box-shadow:
            0 12px 28px rgba(0, 0, 0, 0.18);
    }


    /* --------------------------------------------------------
       TABS
    -------------------------------------------------------- */

    button[data-baseweb="tab"] {
        border-radius:
            10px;
        color:
            #9ba9c5;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color:
            white;
        background:
            rgba(94, 67, 255, 0.28);
    }


    /* --------------------------------------------------------
       STREAMLIT METRICS
    -------------------------------------------------------- */

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(20, 38, 77, 0.94),
                rgba(11, 25, 55, 0.88)
            );
        border:
            1px solid rgba(103, 137, 210, 0.28);
        border-radius:
            15px;
        padding:
            1.05rem;
        min-height:
            125px;
        box-shadow:
            0 16px 30px rgba(0, 0, 0, 0.18);
    }

    div[data-testid="stMetricLabel"] {
        color:
            #bac6dc;
    }

    div[data-testid="stMetricValue"] {
        color:
            white;
        font-size:
            2rem;
        font-weight:
            760;
    }


    /* --------------------------------------------------------
       PROGRESS
    -------------------------------------------------------- */

    div[data-testid="stProgress"] > div > div {
        background:
            linear-gradient(
                90deg,
                #7c46ff,
                #1fb3ff,
                #1be8cf
            );
    }


    /* --------------------------------------------------------
       CUSTOM PANELS
    -------------------------------------------------------- */

    .app-shell-title {
        display:
            flex;
        align-items:
            center;
        gap:
            0.9rem;
        margin-bottom:
            1.1rem;
    }

    .app-icon {
        width:
            48px;
        height:
            48px;
        border-radius:
            14px;
        display:
            flex;
        align-items:
            center;
        justify-content:
            center;
        font-size:
            1.55rem;
        background:
            linear-gradient(
                145deg,
                #9a49ff,
                #315cff,
                #10d9f3
            );
        box-shadow:
            0 0 28px rgba(92, 92, 255, 0.40);
    }

    .app-shell-title h1 {
        margin:
            0;
        font-size:
            2.05rem;
    }

    .page-subtitle {
        color:
            #95a5c3;
        margin-top:
            -0.5rem;
        margin-bottom:
            1.3rem;
    }

    .glass-card {
        background:
            linear-gradient(
                145deg,
                rgba(16, 32, 68, 0.92),
                rgba(7, 20, 45, 0.84)
            );
        border:
            1px solid rgba(102, 139, 210, 0.26);
        border-radius:
            15px;
        padding:
            1rem 1.1rem;
        margin-bottom:
            0.9rem;
        box-shadow:
            0 16px 34px rgba(0, 0, 0, 0.18);
    }

    .glass-card-purple {
        background:
            linear-gradient(
                145deg,
                rgba(42, 29, 85, 0.88),
                rgba(14, 27, 59, 0.88)
            );
        border:
            1px solid rgba(145, 93, 255, 0.46);
        border-radius:
            15px;
        padding:
            1rem 1.1rem;
        margin-bottom:
            0.9rem;
        box-shadow:
            0 0 28px rgba(117, 67, 255, 0.10);
    }

    .glass-card-cyan {
        background:
            linear-gradient(
                145deg,
                rgba(4, 38, 68, 0.86),
                rgba(7, 21, 47, 0.90)
            );
        border:
            1px solid rgba(28, 209, 255, 0.46);
        border-radius:
            15px;
        padding:
            1rem 1.1rem;
        margin-bottom:
            0.9rem;
        box-shadow:
            0 0 28px rgba(20, 199, 255, 0.09);
    }

    .card-heading {
        display:
            flex;
        align-items:
            center;
        gap:
            0.6rem;
        color:
            white;
        font-size:
            1.02rem;
        font-weight:
            730;
        margin-bottom:
            0.65rem;
    }

    .section-number {
        display:
            inline-flex;
        align-items:
            center;
        justify-content:
            center;
        width:
            27px;
        height:
            27px;
        border-radius:
            8px;
        color:
            white;
        font-weight:
            800;
        background:
            linear-gradient(
                145deg,
                #8c49ff,
                #4f55ff
            );
        box-shadow:
            0 0 14px rgba(126, 70, 255, 0.28);
    }

    .metric-card {
        min-height:
            138px;
        border-radius:
            16px;
        padding:
            1.2rem;
        border:
            1px solid rgba(109, 145, 217, 0.28);
        background:
            linear-gradient(
                145deg,
                rgba(21, 40, 80, 0.96),
                rgba(10, 24, 52, 0.90)
            );
        box-shadow:
            0 15px 34px rgba(0, 0, 0, 0.20);
    }

    .metric-label {
        color:
            #b7c3db;
        font-size:
            0.93rem;
    }

    .metric-value {
        color:
            white;
        font-size:
            2.55rem;
        font-weight:
            780;
        line-height:
            1.1;
        margin-top:
            0.65rem;
    }

    .metric-purple {
        border-color:
            rgba(151, 86, 255, 0.48);
        box-shadow:
            0 0 30px rgba(130, 73, 255, 0.09);
    }

    .metric-green {
        border-color:
            rgba(57, 227, 166, 0.40);
        box-shadow:
            0 0 30px rgba(57, 227, 166, 0.06);
    }

    .metric-orange {
        border-color:
            rgba(255, 158, 50, 0.42);
        box-shadow:
            0 0 30px rgba(255, 158, 50, 0.06);
    }

    .metric-blue {
        border-color:
            rgba(37, 142, 255, 0.48);
        box-shadow:
            0 0 30px rgba(37, 142, 255, 0.08);
    }

    .small-badge {
        display:
            inline-block;
        border:
            1px solid rgba(92, 190, 255, 0.36);
        border-radius:
            9px;
        padding:
            0.32rem 0.65rem;
        color:
            #8bdbff;
        background:
            rgba(19, 84, 134, 0.18);
        font-size:
            0.82rem;
        font-weight:
            700;
    }

    .preview-panel {
        background:
            #061329;
        border:
            1px solid rgba(24, 217, 255, 0.58);
        border-radius:
            13px;
        padding:
            1.1rem;
        color:
            #8de6ff;
        font-family:
            "SFMono-Regular",
            Consolas,
            monospace;
        line-height:
            1.75;
        box-shadow:
            inset 0 0 20px rgba(0, 184, 255, 0.04),
            0 0 25px rgba(0, 190, 255, 0.08);
        white-space:
            pre-wrap;
    }

    .sidebar-brand {
        margin:
            0.2rem 0 2.2rem 0;
    }

    .sidebar-logo-row {
        display:
            flex;
        align-items:
            center;
        gap:
            0.8rem;
    }

    .sidebar-logo {
        width:
            43px;
        height:
            43px;
        border-radius:
            12px;
        display:
            flex;
        align-items:
            center;
        justify-content:
            center;
        font-size:
            1.5rem;
        background:
            linear-gradient(
                145deg,
                #a044ff,
                #315cff,
                #04d9ff
            );
        box-shadow:
            0 0 24px rgba(82, 89, 255, 0.42);
    }

    .sidebar-brand-name {
        color:
            white;
        font-size:
            1.65rem;
        font-weight:
            800;
        line-height:
            1;
    }

    .sidebar-brand-sub {
        color:
            #abb8d2;
        font-size:
            0.86rem;
        line-height:
            1.2;
        margin-top:
            0.25rem;
    }

    .sidebar-footer {
        margin-top:
            3rem;
        padding-top:
            1rem;
        border-top:
            1px solid rgba(104, 133, 193, 0.20);
        color:
            #aebad1;
        font-size:
            0.84rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

def get_database_connection():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def get_existing_columns(
    connection,
    table_name,
):
    rows = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [
        row[1]
        for row in rows
    ]


def add_column_if_missing(
    connection,
    table_name,
    column_name,
    definition,
):
    existing_columns = get_existing_columns(
        connection,
        table_name,
    )

    if column_name not in existing_columns:

        connection.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {definition}
            """
        )


def create_or_update_database():
    connection = get_database_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            requirement_title TEXT NOT NULL,
            requirement_text TEXT NOT NULL,
            requirement_type TEXT NOT NULL,
            category TEXT NOT NULL,
            source_department TEXT NOT NULL,
            submitted_by TEXT NOT NULL,
            date_submitted TEXT NOT NULL,
            status TEXT NOT NULL,
            boilerplate_name TEXT,
            stakeholder_input TEXT,
            verification_point TEXT,
            verification_method TEXT
        )
        """
    )

    add_column_if_missing(
        connection,
        "requirements",
        "boilerplate_name",
        "TEXT",
    )

    add_column_if_missing(
        connection,
        "requirements",
        "stakeholder_input",
        "TEXT",
    )

    add_column_if_missing(
        connection,
        "requirements",
        "verification_point",
        "TEXT",
    )

    add_column_if_missing(
        connection,
        "requirements",
        "verification_method",
        "TEXT",
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS standard_requirement_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            revision_number TEXT NOT NULL,
            committed_by TEXT NOT NULL,
            committed_date TEXT NOT NULL,
            revision_status TEXT NOT NULL,
            revision_comment TEXT,
            UNIQUE(project_name, revision_number)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS standard_requirement_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            revision_id INTEGER NOT NULL,
            requirement_id TEXT NOT NULL,
            requirement_area TEXT NOT NULL,
            requirement_text TEXT NOT NULL,
            required_value TEXT,
            unit_or_limit TEXT,
            verification_point TEXT,
            verification_method TEXT,
            notes TEXT,
            locked TEXT NOT NULL,
            FOREIGN KEY(revision_id)
                REFERENCES standard_requirement_revisions(id)
        )
        """
    )

    add_column_if_missing(
        connection,
        "standard_requirement_items",
        "verification_point",
        "TEXT",
    )

    add_column_if_missing(
        connection,
        "standard_requirement_items",
        "verification_method",
        "TEXT",
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS requirement_completion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            requirement_source TEXT NOT NULL,
            requirement_reference TEXT NOT NULL,
            is_complete INTEGER NOT NULL DEFAULT 0,
            evidence_comment TEXT,
            UNIQUE(
                project_name,
                requirement_source,
                requirement_reference
            )
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS engineering_deliverables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            deliverable_name TEXT NOT NULL,
            is_complete INTEGER NOT NULL DEFAULT 0,
            UNIQUE(
                project_name,
                deliverable_name
            )
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# DATABASE QUERIES
# ============================================================

def save_project_requirement(
    project_name,
    requirement_title,
    requirement_text,
    category,
    source_department,
    submitted_by,
    requirement_category,
    stakeholder_input,
    verification_point,
    verification_method,
):
    connection = get_database_connection()

    connection.execute(
        """
        INSERT INTO requirements (
            project_name,
            requirement_title,
            requirement_text,
            requirement_type,
            category,
            source_department,
            submitted_by,
            date_submitted,
            status,
            boilerplate_name,
            stakeholder_input,
            verification_point,
            verification_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_name,
            requirement_title,
            requirement_text,
            "Customer specific",
            category,
            source_department,
            submitted_by,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "Pending",
            requirement_category,
            stakeholder_input,
            verification_point,
            verification_method,
        ),
    )

    connection.commit()
    connection.close()


def load_project_requirements(
    project_name=None,
):
    connection = get_database_connection()

    query = """
        SELECT
            id,
            project_name,
            requirement_title,
            requirement_text,
            category,
            source_department,
            submitted_by,
            date_submitted,
            status,
            boilerplate_name,
            stakeholder_input,
            verification_point,
            verification_method
        FROM requirements
        WHERE requirement_type = 'Customer specific'
    """

    parameters = ()

    if project_name:

        query += """
            AND project_name = ?
        """

        parameters = (
            project_name,
        )

    query += """
        ORDER BY id DESC
    """

    dataframe = pd.read_sql_query(
        query,
        connection,
        params=parameters,
    )

    connection.close()

    return dataframe


def load_standard_revisions(
    project_name,
):
    connection = get_database_connection()

    dataframe = pd.read_sql_query(
        """
        SELECT
            id,
            project_name,
            revision_number,
            committed_by,
            committed_date,
            revision_status,
            revision_comment
        FROM standard_requirement_revisions
        WHERE project_name = ?
        ORDER BY CAST(revision_number AS INTEGER) ASC
        """,
        connection,
        params=(
            project_name,
        ),
    )

    connection.close()

    return dataframe


def load_standard_revision_items(
    revision_id,
):
    connection = get_database_connection()

    dataframe = pd.read_sql_query(
        """
        SELECT
            requirement_id,
            requirement_area,
            requirement_text,
            required_value,
            unit_or_limit,
            verification_point,
            verification_method,
            notes
        FROM standard_requirement_items
        WHERE revision_id = ?
        ORDER BY requirement_id ASC
        """,
        connection,
        params=(
            revision_id,
        ),
    )

    connection.close()

    return dataframe


def get_latest_revision_id(
    project_name,
):
    revisions = load_standard_revisions(
        project_name
    )

    if revisions.empty:

        return None

    return int(
        revisions.iloc[-1]["id"]
    )


def get_latest_revision_number(
    project_name,
):
    revisions = load_standard_revisions(
        project_name
    )

    if revisions.empty:

        return "None"

    return str(
        revisions.iloc[-1][
            "revision_number"
        ]
    )


def get_next_revision_number(
    project_name,
):
    revisions = load_standard_revisions(
        project_name
    )

    if revisions.empty:

        return "00"

    latest_number = (
        revisions[
            "revision_number"
        ]
        .astype(int)
        .max()
    )

    return f"{latest_number + 1:02d}"


def load_latest_standard_values(
    project_name,
):
    revision_id = get_latest_revision_id(
        project_name
    )

    if revision_id is None:

        return {}

    items = load_standard_revision_items(
        revision_id
    )

    values = {}

    for _, row in items.iterrows():

        values[
            str(
                row[
                    "requirement_id"
                ]
            )
        ] = str(
            row[
                "required_value"
            ]
        )

    return values


def commit_standard_revision(
    project_name,
    revision_number,
    committed_by,
    revision_comment,
    requirements_dataframe,
):
    connection = get_database_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO standard_requirement_revisions (
            project_name,
            revision_number,
            committed_by,
            committed_date,
            revision_status,
            revision_comment
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            project_name,
            revision_number,
            committed_by,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "Locked",
            revision_comment,
        ),
    )

    revision_id = cursor.lastrowid

    for _, row in requirements_dataframe.iterrows():

        cursor.execute(
            """
            INSERT INTO standard_requirement_items (
                revision_id,
                requirement_id,
                requirement_area,
                requirement_text,
                required_value,
                unit_or_limit,
                verification_point,
                verification_method,
                notes,
                locked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                revision_id,
                str(
                    row["Question ID"]
                ),
                str(
                    row[
                        "Requirement Area"
                    ]
                ),
                str(
                    row["Requirement"]
                ),
                str(
                    row[
                        "Required Value"
                    ]
                ),
                str(
                    row[
                        "Unit / Limit"
                    ]
                ),
                str(
                    row["V&V Point"]
                ),
                str(
                    row["V&V Method"]
                ),
                str(
                    row["Notes"]
                ),
                "Yes",
            ),
        )

    connection.commit()
    connection.close()


# ============================================================
# REVISION HISTORY
# ============================================================

def revision_items_to_dictionary(
    dataframe,
):
    result = {}

    for _, row in dataframe.iterrows():

        question_id = str(
            row[
                "requirement_id"
            ]
        )

        result[
            question_id
        ] = {

            "requirement_area":
                str(
                    row[
                        "requirement_area"
                    ]
                ),

            "requirement_text":
                str(
                    row[
                        "requirement_text"
                    ]
                ),

            "required_value":
                str(
                    row[
                        "required_value"
                    ]
                ),

            "unit_or_limit":
                str(
                    row[
                        "unit_or_limit"
                    ]
                ),

            "verification_point":
                str(
                    row[
                        "verification_point"
                    ]
                ),

            "verification_method":
                str(
                    row[
                        "verification_method"
                    ]
                ),

            "notes":
                str(
                    row["notes"]
                ),
        }

    return result


def find_changed_question_ids(
    previous_items,
    current_items,
):
    previous = (
        revision_items_to_dictionary(
            previous_items
        )
    )

    current = (
        revision_items_to_dictionary(
            current_items
        )
    )

    all_ids = sorted(
        set(
            previous.keys()
        )
        |
        set(
            current.keys()
        )
    )

    changed = []

    for question_id in all_ids:

        if (
            previous.get(
                question_id
            )
            !=
            current.get(
                question_id
            )
        ):

            changed.append(
                question_id
            )

    return changed


def build_revision_history_summary(
    project_name,
):
    revisions = load_standard_revisions(
        project_name
    )

    if revisions.empty:

        return pd.DataFrame()

    rows = []

    previous_items = None

    for _, revision in revisions.iterrows():

        current_items = (
            load_standard_revision_items(
                int(
                    revision["id"]
                )
            )
        )

        if previous_items is None:

            changed_text = (
                "Initial issue"
            )

        else:

            changed_ids = (
                find_changed_question_ids(
                    previous_items,
                    current_items,
                )
            )

            changed_text = (
                ", ".join(
                    changed_ids
                )
                if changed_ids
                else
                "No requirement changes"
            )

        rows.append(
            {
                "Revision":
                    str(
                        revision[
                            "revision_number"
                        ]
                    ),

                "Changed Question IDs":
                    changed_text,

                "Committed By":
                    revision[
                        "committed_by"
                    ],

                "Comment":
                    revision[
                        "revision_comment"
                    ],
            }
        )

        previous_items = (
            current_items
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# DASHBOARD STORAGE
# ============================================================

def get_requirement_completion(
    project_name,
    source,
    reference,
):
    connection = get_database_connection()

    row = connection.execute(
        """
        SELECT
            is_complete,
            evidence_comment
        FROM requirement_completion
        WHERE project_name = ?
        AND requirement_source = ?
        AND requirement_reference = ?
        """,
        (
            project_name,
            source,
            reference,
        ),
    ).fetchone()

    connection.close()

    if row is None:

        return False, ""

    return bool(
        row[0]
    ), row[1] or ""


def save_requirement_completion(
    project_name,
    source,
    reference,
    is_complete,
    evidence_comment,
):
    connection = get_database_connection()

    connection.execute(
        """
        INSERT INTO requirement_completion (
            project_name,
            requirement_source,
            requirement_reference,
            is_complete,
            evidence_comment
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(
            project_name,
            requirement_source,
            requirement_reference
        )
        DO UPDATE SET
            is_complete = excluded.is_complete,
            evidence_comment = excluded.evidence_comment
        """,
        (
            project_name,
            source,
            reference,
            int(
                is_complete
            ),
            evidence_comment,
        ),
    )

    connection.commit()
    connection.close()


def get_deliverable_status(
    project_name,
    deliverable_name,
):
    connection = get_database_connection()

    row = connection.execute(
        """
        SELECT is_complete
        FROM engineering_deliverables
        WHERE project_name = ?
        AND deliverable_name = ?
        """,
        (
            project_name,
            deliverable_name,
        ),
    ).fetchone()

    connection.close()

    if row is None:

        return False

    return bool(
        row[0]
    )


def save_deliverable_status(
    project_name,
    deliverable_name,
    is_complete,
):
    connection = get_database_connection()

    connection.execute(
        """
        INSERT INTO engineering_deliverables (
            project_name,
            deliverable_name,
            is_complete
        )
        VALUES (?, ?, ?)
        ON CONFLICT(
            project_name,
            deliverable_name
        )
        DO UPDATE SET
            is_complete = excluded.is_complete
        """,
        (
            project_name,
            deliverable_name,
            int(
                is_complete
            ),
        ),
    )

    connection.commit()
    connection.close()


# ============================================================
# VALUE HELPERS
# ============================================================

def get_text_value(
    values,
    question_id,
    default="",
):
    value = values.get(
        question_id,
        default,
    )

    if value in [
        "None",
        "nan",
    ]:

        return default

    return str(
        value
    )


def get_integer_value(
    values,
    question_id,
    default=0,
):
    try:

        return int(
            float(
                values.get(
                    question_id,
                    default,
                )
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def get_float_value(
    values,
    question_id,
    default=0.0,
):
    try:

        return float(
            values.get(
                question_id,
                default,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def selectbox_index(
    options,
    value,
    default_index=0,
):
    if value in options:

        return options.index(
            value
        )

    return default_index


# ============================================================
# STANDARD REQUIREMENT GENERATOR
# ============================================================

def get_electrical_requirement(
    product_variant,
):
    mapping = {

        "ISV - MK3":
            (
                "Electrical requirements applicable "
                "to the ISV - MK3 valve configuration"
            ),

        "ISV - E":
            (
                "Electrical requirements applicable "
                "to the ISV - E valve configuration"
            ),

        "ISV - EC":
            (
                "Electrical requirements applicable "
                "to the ISV - EC valve configuration"
            ),

        "ISV - EX":
            (
                "Electrical requirements applicable "
                "to the ISV - EX valve configuration"
            ),
    }

    return mapping.get(
        product_variant,
        "Valve-specific electrical requirements",
    )


def build_standard_requirement_table(
    project_name,
    customer_name,
    mill_type,
    product_variant,
    mk3_configuration,
    pitching_type,
    total_valves,
    uniform_pitch,
    edge_valves_per_side,
    edge_pitch,
    centre_valves,
    centre_pitch,
    operating_fluid,
):
    electrical_requirement = (
        get_electrical_requirement(
            product_variant
        )
    )

    requirements = [

        {
            "Question ID":
                "STD-001",

            "Requirement Area":
                "Project Information",

            "Requirement":
                (
                    "The project shall use "
                    "the selected project reference."
                ),

            "Required Value":
                project_name,

            "Unit / Limit":
                "",

            "V&V Point":
                "Requirements review",

            "V&V Method":
                "Document review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-002",

            "Requirement Area":
                "Project Information",

            "Requirement":
                (
                    "The ISV system shall be supplied "
                    "to the identified customer."
                ),

            "Required Value":
                customer_name,

            "Unit / Limit":
                "",

            "V&V Point":
                "Requirements review",

            "V&V Method":
                "Document review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-003",

            "Requirement Area":
                "Project Information",

            "Requirement":
                (
                    "The ISV system shall be designed "
                    "for the selected mill type."
                ),

            "Required Value":
                mill_type,

            "Unit / Limit":
                "",

            "V&V Point":
                "Concept design review",

            "V&V Method":
                "Design review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-004",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV system shall use "
                    "the selected ISV product variant."
                ),

            "Required Value":
                product_variant,

            "Unit / Limit":
                "",

            "V&V Point":
                "Concept design review",

            "V&V Method":
                "Design review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-005",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV - MK3 valve configuration "
                    "shall use the selected configuration."
                ),

            "Required Value":
                mk3_configuration,

            "Unit / Limit":
                "",

            "V&V Point":
                "Concept design review",

            "V&V Method":
                "Design review",

            "Notes":
                (
                    "Not applicable when "
                    "a non-MK3 variant is selected."
                ),
        },

        {
            "Question ID":
                "STD-006",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar shall use "
                    "the selected valve pitching configuration."
                ),

            "Required Value":
                pitching_type,

            "Unit / Limit":
                "",

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-007",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar shall contain "
                    "the specified total number of valves."
                ),

            "Required Value":
                str(
                    total_valves
                ),

            "Unit / Limit":
                "valves",

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-008",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar shall use "
                    "the specified uniform valve pitch."
                ),

            "Required Value":
                (
                    f"{uniform_pitch:g}"
                    if pitching_type
                    == "Uniform pitching"
                    else
                    "Not applicable"
                ),

            "Unit / Limit":
                (
                    "mm"
                    if pitching_type
                    == "Uniform pitching"
                    else
                    ""
                ),

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-009",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar shall contain "
                    "the specified number of edge valves "
                    "on each side."
                ),

            "Required Value":
                (
                    str(
                        edge_valves_per_side
                    )
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    "Not applicable"
                ),

            "Unit / Limit":
                (
                    "valves per side"
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    ""
                ),

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-010",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar edge valves "
                    "shall use the specified pitch."
                ),

            "Required Value":
                (
                    f"{edge_pitch:g}"
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    "Not applicable"
                ),

            "Unit / Limit":
                (
                    "mm"
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    ""
                ),

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-011",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar shall contain "
                    "the specified number of centre valves."
                ),

            "Required Value":
                (
                    str(
                        centre_valves
                    )
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    "Not applicable"
                ),

            "Unit / Limit":
                (
                    "valves"
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    ""
                ),

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-012",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar centre valves "
                    "shall use the specified pitch."
                ),

            "Required Value":
                (
                    f"{centre_pitch:g}"
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    "Not applicable"
                ),

            "Unit / Limit":
                (
                    "mm"
                    if pitching_type
                    == "Hybrid pitching"
                    else
                    ""
                ),

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Drawing review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-013",

            "Requirement Area":
                "Operating Fluid",

            "Requirement":
                (
                    "The ISV system shall be designed "
                    "for operation using the specified fluid."
                ),

            "Required Value":
                operating_fluid,

            "Unit / Limit":
                "",

            "V&V Point":
                "Detailed design review",

            "V&V Method":
                "Design review",

            "Notes":
                "",
        },

        {
            "Question ID":
                "STD-014",

            "Requirement Area":
                "Electrical",

            "Requirement":
                (
                    "The ISV electrical configuration "
                    "shall comply with the requirements "
                    "applicable to the selected valve variant."
                ),

            "Required Value":
                electrical_requirement,

            "Unit / Limit":
                "",

            "V&V Point":
                "Detailed design review",

            "V&V Method":
                "Design review",

            "Notes":
                (
                    "Automatically generated from "
                    "the selected valve variant."
                ),
        },

        {
            "Question ID":
                "STD-015",

            "Requirement Area":
                "Documentation",

            "Requirement":
                (
                    "The project shall provide "
                    "customer approval drawings."
                ),

            "Required Value":
                "Required",

            "Unit / Limit":
                "",

            "V&V Point":
                "Approval drawing review",

            "V&V Method":
                "Document review",

            "Notes":
                (
                    "Automatically applicable "
                    "to all projects."
                ),
        },

        {
            "Question ID":
                "STD-016",

            "Requirement Area":
                "Documentation",

            "Requirement":
                (
                    "The project shall provide "
                    "manufacturing drawings."
                ),

            "Required Value":
                "Required",

            "Unit / Limit":
                "",

            "V&V Point":
                "Detailed design review",

            "V&V Method":
                "Document review",

            "Notes":
                (
                    "Automatically applicable "
                    "to all projects."
                ),
        },
    ]

    return pd.DataFrame(
        requirements
    )


# ============================================================
# UI HELPERS
# ============================================================

def render_page_heading(
    icon,
    title,
    subtitle,
):
    st.markdown(
        f"""
        <div class="app-shell-title">
            <div class="app-icon">
                {icon}
            </div>

            <div>
                <h1>
                    {title}
                </h1>

                <div class="page-subtitle">
                    {subtitle}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(
    number,
    title,
):
    st.markdown(
        f"""
        <div class="card-heading">
            <span class="section-number">
                {number}
            </span>

            <span>
                {title}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label,
    value,
    style_class,
):
    st.markdown(
        f"""
        <div class="
            metric-card
            {style_class}
        ">
            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CREATE DATABASE
# ============================================================

create_or_update_database()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo-row">

                <div class="sidebar-logo">
                    ⬢
                </div>

                <div>

                    <div class="sidebar-brand-name">
                        ISV
                    </div>

                    <div class="sidebar-brand-sub">
                        Requirements<br>
                        Management
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        options=[
            "Project-Specific Requirements",
            "Standard Requirements",
            "Engineering Dashboard",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="sidebar-footer">

            <strong>
                Engineering Team
            </strong>

            <br>

            Internal engineering tool

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT-SPECIFIC REQUIREMENTS PAGE
# ============================================================

if (
    selected_page
    == "Project-Specific Requirements"
):

    render_page_heading(
        "▤",
        "Project-Specific Requirements",
        (
            "Capture customer and project-specific "
            "requirements using guided engineering inputs."
        ),
    )

    top_left, top_right = st.columns(
        [
            1.85,
            1,
        ]
    )

    with top_left:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        render_section_heading(
            "1",
            "Requirement Details",
        )

        detail_1, detail_2 = st.columns(2)

        with detail_1:

            selected_project = (
                st.selectbox(
                    "Project *",
                    ALLOWED_PROJECTS,
                    key="project_project",
                )
            )

            source_department = (
                st.selectbox(
                    "Source department *",
                    [
                        "Customer",
                        "Sales",
                        "Engineering",
                        "Project Management",
                        "Operations / Production",
                        "Supply Chain Management",
                        "Site and Service",
                        "Research and Development",
                        "Quality",
                        "Other",
                    ],
                    key="project_source",
                )
            )

        with detail_2:

            requirement_title = (
                st.text_input(
                    "Requirement title *",
                    placeholder=(
                        "Enter a short, descriptive title"
                    ),
                    key="project_title",
                )
            )

            submitted_by = (
                st.text_input(
                    "Submitted by *",
                    placeholder=(
                        "Enter your name"
                    ),
                    key="project_submitter",
                )
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with top_right:

        st.markdown(
            """
            <div class="glass-card-purple">
            """,
            unsafe_allow_html=True,
        )

        render_section_heading(
            "2",
            "Requirement Type",
        )

        requirement_category = (
            st.selectbox(
                "Select requirement type *",
                PROJECT_REQUIREMENT_CATEGORIES,
                key="project_category",
            )
        )

        st.caption(
            (
                "Choose the category that best "
                "matches the requirement."
            )
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    input_left, preview_right = st.columns(
        [
            1.65,
            1,
        ]
    )

    generated_requirement = ""

    stakeholder_input = ""

    requirement_complete = False

    internal_category = "Other"

    with input_left:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        render_section_heading(
            "3",
            "Tell Us What Is Needed",
        )

        if (
            requirement_category
            == "Operating condition"
        ):

            internal_category = (
                "Environmental"
            )

            equipment = st.text_input(
                "Equipment or system *",
                value="ISV spraybar",
                key="operating_equipment",
            )

            action = st.text_input(
                "What must it do? *",
                placeholder=(
                    "Example: operate continuously"
                ),
                key="operating_action",
            )

            condition = st.text_area(
                "Operating condition *",
                placeholder=(
                    "Example: at an ambient "
                    "temperature between 5°C and 45°C"
                ),
                key="operating_condition",
            )

            requirement_complete = all(
                [
                    equipment.strip(),
                    action.strip(),
                    condition.strip(),
                ]
            )

            generated_requirement = (
                f"The "
                f"{equipment.strip() or '[equipment]'} "
                f"shall "
                f"{action.strip() or '[required action]'} "
                f"{condition.strip() or '[operating condition]'}."
            )

            stakeholder_input = (
                f"Equipment: {equipment}\n"
                f"Action: {action}\n"
                f"Condition: {condition}"
            )

        elif (
            requirement_category
            == "Capacity or quantity"
        ):

            internal_category = (
                "Capacity"
            )

            equipment = st.text_input(
                "Equipment or system *",
                value="ISV spraybar",
                key="capacity_equipment",
            )

            action = st.text_input(
                "What must it do? *",
                placeholder="Example: control",
                key="capacity_action",
            )

            quantity = st.number_input(
                "Minimum quantity *",
                min_value=0,
                step=1,
                key="capacity_quantity",
            )

            item = st.text_input(
                "What is being counted? *",
                placeholder=(
                    "Example: spray zones"
                ),
                key="capacity_item",
            )

            requirement_complete = all(
                [
                    equipment.strip(),
                    action.strip(),
                    quantity > 0,
                    item.strip(),
                ]
            )

            quantity_text = (
                str(
                    quantity
                )
                if quantity > 0
                else
                "[minimum quantity]"
            )

            generated_requirement = (
                f"The "
                f"{equipment.strip() or '[equipment]'} "
                f"shall "
                f"{action.strip() or '[required action]'} "
                f"a minimum of "
                f"{quantity_text} "
                f"{item.strip() or '[item]'}."
            )

            stakeholder_input = (
                f"Equipment: {equipment}\n"
                f"Action: {action}\n"
                f"Quantity: {quantity}\n"
                f"Item: {item}"
            )

        elif (
            requirement_category
            == "Response time"
        ):

            internal_category = (
                "Performance"
            )

            equipment = st.text_input(
                "Equipment or system *",
                value="ISV spraybar",
                key="response_equipment",
            )

            action = st.text_input(
                "Required action *",
                placeholder=(
                    "Example: begin coolant delivery"
                ),
                key="response_action",
            )

            trigger = st.text_input(
                "Trigger event *",
                placeholder=(
                    "Example: receiving "
                    "a control signal"
                ),
                key="response_trigger",
            )

            response_time = st.number_input(
                "Maximum permitted time *",
                min_value=0.0,
                step=0.1,
                key="response_time",
            )

            response_unit = (
                st.selectbox(
                    "Time unit *",
                    [
                        "milliseconds",
                        "seconds",
                        "minutes",
                    ],
                    key="response_unit",
                )
            )

            requirement_complete = all(
                [
                    equipment.strip(),
                    action.strip(),
                    trigger.strip(),
                    response_time > 0,
                ]
            )

            time_text = (
                f"{response_time:g}"
                if response_time > 0
                else
                "[maximum time]"
            )

            generated_requirement = (
                f"The "
                f"{equipment.strip() or '[equipment]'} "
                f"shall "
                f"{action.strip() or '[required action]'} "
                f"within "
                f"{time_text} "
                f"{response_unit} of "
                f"{trigger.strip() or '[trigger event]'}."
            )

            stakeholder_input = (
                f"Equipment: {equipment}\n"
                f"Action: {action}\n"
                f"Trigger: {trigger}\n"
                f"Time: {response_time} "
                f"{response_unit}"
            )

        else:

            description = st.text_area(
                "Describe the requirement *",
                placeholder=(
                    "Describe the need, constraint, "
                    "performance expectation, interface, "
                    "or customer requirement."
                ),
                height=180,
                key="generic_description",
            )

            requirement_complete = bool(
                description.strip()
            )

            generated_requirement = (
                description.strip()
                or
                "[Describe the requirement]"
            )

            stakeholder_input = (
                description.strip()
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with preview_right:

        st.markdown(
            """
            <div class="glass-card-cyan">
            """,
            unsafe_allow_html=True,
        )

        render_section_heading(
            "4",
            "Live Requirement Preview",
        )

        preview_text = (
            f"Project: "
            f"{selected_project}\n\n"

            f"Title: "
            f"{requirement_title or '[Requirement title]'}\n\n"

            f"Type: "
            f"{requirement_category}\n\n"

            f"Requirement:\n"
            f"{generated_requirement}\n\n"

            f"Status: Draft"
        )

        st.markdown(
            f"""
            <div class="preview-panel">
            {preview_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="glass-card-purple">
        """,
        unsafe_allow_html=True,
    )

    render_section_heading(
        "5",
        "Verification and Validation",
    )

    v_and_v_1, v_and_v_2 = st.columns(2)

    with v_and_v_1:

        verification_point = (
            st.selectbox(
                "V&V point *",
                VERIFICATION_POINTS,
                key="project_vv_point",
            )
        )

        st.caption(
            (
                "Where in the engineering lifecycle "
                "will this be checked?"
            )
        )

    with v_and_v_2:

        verification_method = (
            st.selectbox(
                "V&V method *",
                VERIFICATION_METHODS,
                key="project_vv_method",
            )
        )

        st.caption(
            (
                "How will compliance "
                "be demonstrated?"
            )
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    submit_button = st.button(
        "✈  Submit Requirement",
        type="primary",
        use_container_width=True,
    )

    if submit_button:

        errors = []

        if not requirement_title.strip():

            errors.append(
                "Requirement title"
            )

        if not submitted_by.strip():

            errors.append(
                "Submitted by"
            )

        if not requirement_complete:

            errors.append(
                "Requirement information"
            )

        if errors:

            st.error(
                "Please complete: "
                +
                ", ".join(
                    errors
                )
            )

        else:

            save_project_requirement(
                project_name=(
                    selected_project
                ),
                requirement_title=(
                    requirement_title.strip()
                ),
                requirement_text=(
                    generated_requirement
                ),
                category=(
                    internal_category
                ),
                source_department=(
                    source_department
                ),
                submitted_by=(
                    submitted_by.strip()
                ),
                requirement_category=(
                    requirement_category
                ),
                stakeholder_input=(
                    stakeholder_input
                ),
                verification_point=(
                    verification_point
                ),
                verification_method=(
                    verification_method
                ),
            )

            st.success(
                (
                    "Requirement submitted successfully "
                    "and set to Pending."
                )
            )

            st.rerun()

    st.markdown(
        """
        <div class="glass-card">
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        "Project Requirements Dashboard"
    )

    recent_requirements = (
        load_project_requirements(
            selected_project
        )
    )

    if recent_requirements.empty:

        st.info(
            (
                "No project-specific requirements "
                "have been submitted for this project."
            )
        )

    else:

        display_requirements = (
            recent_requirements.rename(
                columns={

                    "id":
                        "ID",

                    "project_name":
                        "Project",

                    "requirement_title":
                        "Title",

                    "boilerplate_name":
                        "Requirement Type",

                    "verification_point":
                        "V&V Point",

                    "verification_method":
                        "V&V Method",

                    "status":
                        "Status",
                }
            )
        )

        st.dataframe(
            display_requirements[
                [
                    "ID",
                    "Project",
                    "Title",
                    "Requirement Type",
                    "V&V Point",
                    "V&V Method",
                    "Status",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# STANDARD REQUIREMENTS PAGE
# ============================================================

elif (
    selected_page
    == "Standard Requirements"
):

    render_page_heading(
        "◇",
        "Standard Requirements",
        (
            "Create controlled project baselines "
            "using guided ISV configuration questions."
        ),
    )

    project_header_1, project_header_2 = (
        st.columns(
            [
                3,
                1,
            ]
        )
    )

    with project_header_1:

        standard_project = (
            st.selectbox(
                "Project",
                ALLOWED_PROJECTS,
                key="standard_project",
            )
        )

    next_revision = (
        get_next_revision_number(
            standard_project
        )
    )

    with project_header_2:

        st.markdown(
            f"""
            <div
                class="glass-card-purple"
                style="
                    margin-top: 1.75rem;
                    text-align: center;
                "
            >
                <div
                    style="
                        color: #aebbd4;
                        font-size: 0.82rem;
                    "
                >
                    Next Revision
                </div>

                <div
                    style="
                        color: #7cd8ff;
                        font-size: 1.75rem;
                        font-weight: 800;
                    "
                >
                    {next_revision}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    latest_values = (
        load_latest_standard_values(
            standard_project
        )
    )

    top_1, top_2 = st.columns(
        [
            1.4,
            1,
        ]
    )

    with top_1:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Revision History"
        )

        revision_history = (
            build_revision_history_summary(
                standard_project
            )
        )

        if revision_history.empty:

            st.info(
                (
                    "No locked revisions "
                    "exist for this project."
                )
            )

        else:

            st.dataframe(
                revision_history,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with top_2:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Project Information"
        )

        customer_name = st.text_input(
            "Customer name *",
            value=get_text_value(
                latest_values,
                "STD-002",
            ),
            key=(
                f"customer_"
                f"{standard_project}"
            ),
        )

        saved_mill = get_text_value(
            latest_values,
            "STD-003",
            "FFM",
        )

        mill_selection = st.selectbox(
            "Mill type *",
            MILL_TYPES,
            index=selectbox_index(
                MILL_TYPES,
                (
                    saved_mill
                    if saved_mill
                    in MILL_TYPES
                    else
                    "Other"
                ),
                0,
            ),
            key=(
                f"mill_"
                f"{standard_project}"
            ),
        )

        if mill_selection == "Other":

            final_mill = st.text_input(
                "Specify mill type *",
                value=(
                    saved_mill
                    if saved_mill
                    not in MILL_TYPES
                    else
                    ""
                ),
                key=(
                    f"other_mill_"
                    f"{standard_project}"
                ),
            )

        else:

            final_mill = (
                mill_selection
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    valve_1, valve_2 = st.columns(
        [
            0.82,
            1.8,
        ]
    )

    with valve_1:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Valve Configuration"
        )

        saved_variant = (
            get_text_value(
                latest_values,
                "STD-004",
                "ISV - MK3",
            )
        )

        product_variant = (
            st.selectbox(
                "ISV product variant *",
                ISV_PRODUCT_VARIANTS,
                index=selectbox_index(
                    ISV_PRODUCT_VARIANTS,
                    saved_variant,
                    0,
                ),
                key=(
                    f"variant_"
                    f"{standard_project}"
                ),
            )
        )

        if (
            product_variant
            == "ISV - MK3"
        ):

            saved_mk3 = get_text_value(
                latest_values,
                "STD-005",
                "Standard",
            )

            mk3_configuration = (
                st.selectbox(
                    "MK3 configuration *",
                    MK3_CONFIGURATIONS,
                    index=selectbox_index(
                        MK3_CONFIGURATIONS,
                        saved_mk3,
                        0,
                    ),
                    key=(
                        f"mk3_"
                        f"{standard_project}"
                    ),
                )
            )

        else:

            mk3_configuration = (
                "Not applicable"
            )

        st.caption(
            (
                "Electrical requirements are "
                "generated from the selected variant."
            )
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with valve_2:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Valve Pitching"
        )

        saved_pitching = (
            get_text_value(
                latest_values,
                "STD-006",
                "Uniform pitching",
            )
        )

        pitching_type = (
            st.radio(
                "Pitch configuration *",
                PITCHING_TYPES,
                horizontal=True,
                index=selectbox_index(
                    PITCHING_TYPES,
                    saved_pitching,
                    0,
                ),
                key=(
                    f"pitching_"
                    f"{standard_project}"
                ),
            )
        )

        if (
            pitching_type
            == "Uniform pitching"
        ):

            uniform_1, uniform_2 = (
                st.columns(2)
            )

            with uniform_1:

                total_valves = (
                    st.number_input(
                        "Total number of valves *",
                        min_value=1,
                        step=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_values,
                                "STD-007",
                                64,
                            ),
                        ),
                        key=(
                            f"total_valves_"
                            f"{standard_project}"
                        ),
                    )
                )

            with uniform_2:

                uniform_pitch = (
                    st.number_input(
                        "Uniform valve pitch (mm) *",
                        min_value=0.0,
                        step=1.0,
                        value=get_float_value(
                            latest_values,
                            "STD-008",
                            52.0,
                        ),
                        key=(
                            f"uniform_pitch_"
                            f"{standard_project}"
                        ),
                    )
                )

            edge_valves = 0
            edge_pitch = 0.0
            centre_valves = 0
            centre_pitch = 0.0

        else:

            hybrid_1, hybrid_2 = (
                st.columns(2)
            )

            with hybrid_1:

                edge_valves = (
                    st.number_input(
                        "Edge valves per side *",
                        min_value=1,
                        step=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_values,
                                "STD-009",
                                12,
                            ),
                        ),
                        key=(
                            f"edge_valves_"
                            f"{standard_project}"
                        ),
                    )
                )

                edge_pitch = (
                    st.number_input(
                        "Edge valve pitch (mm) *",
                        min_value=0.0,
                        step=1.0,
                        value=get_float_value(
                            latest_values,
                            "STD-010",
                            26.0,
                        ),
                        key=(
                            f"edge_pitch_"
                            f"{standard_project}"
                        ),
                    )
                )

            with hybrid_2:

                centre_valves = (
                    st.number_input(
                        "Centre valves *",
                        min_value=1,
                        step=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_values,
                                "STD-011",
                                20,
                            ),
                        ),
                        key=(
                            f"centre_valves_"
                            f"{standard_project}"
                        ),
                    )
                )

                centre_pitch = (
                    st.number_input(
                        "Centre valve pitch (mm) *",
                        min_value=0.0,
                        step=1.0,
                        value=get_float_value(
                            latest_values,
                            "STD-012",
                            52.0,
                        ),
                        key=(
                            f"centre_pitch_"
                            f"{standard_project}"
                        ),
                    )
                )

            total_valves = (
                edge_valves
                * 2
                +
                centre_valves
            )

            uniform_pitch = 0.0

            st.metric(
                "Calculated total valves",
                total_valves,
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="glass-card">
        """,
        unsafe_allow_html=True,
    )

    fluid_options = (
        OPERATING_FLUIDS
    )

    saved_fluid = get_text_value(
        latest_values,
        "STD-013",
        "Water",
    )

    fluid_selection = st.selectbox(
        "Operating fluid *",
        fluid_options,
        index=selectbox_index(
            fluid_options,
            (
                saved_fluid
                if saved_fluid
                in fluid_options
                else
                "Other"
            ),
            0,
        ),
        key=(
            f"fluid_"
            f"{standard_project}"
        ),
    )

    if fluid_selection == "Other":

        final_fluid = st.text_input(
            "Specify operating fluid *",
            value=(
                saved_fluid
                if saved_fluid
                not in fluid_options
                else
                ""
            ),
            key=(
                f"other_fluid_"
                f"{standard_project}"
            ),
        )

    else:

        final_fluid = (
            fluid_selection
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    generated_standard_requirements = (
        build_standard_requirement_table(

            project_name=(
                standard_project
            ),

            customer_name=(
                customer_name.strip()
            ),

            mill_type=(
                final_mill
            ),

            product_variant=(
                product_variant
            ),

            mk3_configuration=(
                mk3_configuration
            ),

            pitching_type=(
                pitching_type
            ),

            total_valves=(
                total_valves
            ),

            uniform_pitch=(
                uniform_pitch
            ),

            edge_valves_per_side=(
                edge_valves
            ),

            edge_pitch=(
                edge_pitch
            ),

            centre_valves=(
                centre_valves
            ),

            centre_pitch=(
                centre_pitch
            ),

            operating_fluid=(
                final_fluid
            ),
        )
    )

    review_1, commit_1 = st.columns(
        [
            1.7,
            0.8,
        ]
    )

    with review_1:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Review Generated Standard Requirements"
        )

        st.dataframe(
            generated_standard_requirements[
                [
                    "Question ID",
                    "Requirement Area",
                    "Required Value",
                    "V&V Point",
                    "V&V Method",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with commit_1:

        st.markdown(
            """
            <div class="glass-card-purple">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Commit Locked Revision"
        )

        committed_by = st.text_input(
            "Committed by *",
            key=(
                f"committed_by_"
                f"{standard_project}"
            ),
        )

        revision_comment = st.text_area(
            "Revision comment",
            placeholder=(
                "Describe the reason "
                "for this revision."
            ),
            key=(
                f"revision_comment_"
                f"{standard_project}"
            ),
        )

        commit_revision = st.button(
            (
                f"🔒 Commit Locked "
                f"Revision {next_revision}"
            ),
            type="primary",
            use_container_width=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    if commit_revision:

        errors = []

        if not customer_name.strip():

            errors.append(
                "Customer name"
            )

        if not str(
            final_mill
        ).strip():

            errors.append(
                "Mill type"
            )

        if not str(
            final_fluid
        ).strip():

            errors.append(
                "Operating fluid"
            )

        if not committed_by.strip():

            errors.append(
                "Committed by"
            )

        if (
            pitching_type
            == "Uniform pitching"
            and
            uniform_pitch <= 0
        ):

            errors.append(
                "Uniform pitch"
            )

        if (
            pitching_type
            == "Hybrid pitching"
            and
            (
                edge_pitch <= 0
                or
                centre_pitch <= 0
            )
        ):

            errors.append(
                "Hybrid pitch values"
            )

        if errors:

            st.error(
                (
                    "Please complete: "
                    +
                    ", ".join(
                        errors
                    )
                )
            )

        else:

            try:

                commit_standard_revision(
                    project_name=(
                        standard_project
                    ),
                    revision_number=(
                        next_revision
                    ),
                    committed_by=(
                        committed_by.strip()
                    ),
                    revision_comment=(
                        revision_comment.strip()
                    ),
                    requirements_dataframe=(
                        generated_standard_requirements
                    ),
                )

                st.success(
                    (
                        f"Revision "
                        f"{next_revision} "
                        f"has been committed "
                        f"and locked."
                    )
                )

                st.rerun()

            except sqlite3.IntegrityError:

                st.error(
                    (
                        "This revision number "
                        "already exists."
                    )
                )


# ============================================================
# ENGINEERING DASHBOARD PAGE
# ============================================================

else:

    render_page_heading(
        "⌁",
        "Engineering Dashboard",
        (
            "Track requirement compliance, V&V completion, "
            "and engineering deliverables."
        ),
    )

    dashboard_header_1, dashboard_header_2 = (
        st.columns(
            [
                3,
                1,
            ]
        )
    )

    with dashboard_header_1:

        dashboard_project = (
            st.selectbox(
                "Project",
                ALLOWED_PROJECTS,
                key="dashboard_project",
            )
        )

    latest_revision = (
        get_latest_revision_number(
            dashboard_project
        )
    )

    with dashboard_header_2:

        st.markdown(
            f"""
            <div
                class="glass-card"
                style="
                    margin-top: 1.75rem;
                    text-align: center;
                "
            >

                <div
                    style="
                        color: #aebbd4;
                        font-size: 0.82rem;
                    "
                >
                    Current Standard Revision
                </div>

                <div
                    style="
                        color: #65d8ff;
                        font-size: 1.65rem;
                        font-weight: 800;
                    "
                >
                    {latest_revision}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    standard_revision_id = (
        get_latest_revision_id(
            dashboard_project
        )
    )

    if standard_revision_id is None:

        standard_items = (
            pd.DataFrame()
        )

    else:

        standard_items = (
            load_standard_revision_items(
                standard_revision_id
            )
        )

    project_items = (
        load_project_requirements(
            dashboard_project
        )
    )

    combined_rows = []

    for _, row in standard_items.iterrows():

        complete, comment = (
            get_requirement_completion(
                dashboard_project,
                "Standard",
                str(
                    row[
                        "requirement_id"
                    ]
                ),
            )
        )

        combined_rows.append(
            {

                "Source":
                    "Standard",

                "Reference":
                    str(
                        row[
                            "requirement_id"
                        ]
                    ),

                "Requirement":
                    str(
                        row[
                            "requirement_text"
                        ]
                    ),

                "V&V Point":
                    str(
                        row[
                            "verification_point"
                        ]
                    ),

                "V&V Method":
                    str(
                        row[
                            "verification_method"
                        ]
                    ),

                "Complete":
                    complete,

                "Evidence / Comment":
                    comment,
            }
        )

    for _, row in project_items.iterrows():

        reference = (
            f"REQ-"
            f"{int(row['id']):04d}"
        )

        complete, comment = (
            get_requirement_completion(
                dashboard_project,
                "Project specific",
                reference,
            )
        )

        combined_rows.append(
            {

                "Source":
                    "Project specific",

                "Reference":
                    reference,

                "Requirement":
                    str(
                        row[
                            "requirement_text"
                        ]
                    ),

                "V&V Point":
                    str(
                        row[
                            "verification_point"
                        ]
                    ),

                "V&V Method":
                    str(
                        row[
                            "verification_method"
                        ]
                    ),

                "Complete":
                    complete,

                "Evidence / Comment":
                    comment,
            }
        )

    combined_requirements = (
        pd.DataFrame(
            combined_rows
        )
    )

    total_requirements = len(
        combined_requirements
    )

    if total_requirements:

        completed_requirements = int(
            combined_requirements[
                "Complete"
            ].sum()
        )

    else:

        completed_requirements = 0

    open_requirements = (
        total_requirements
        -
        completed_requirements
    )

    completion_percentage = (
        int(
            round(
                (
                    completed_requirements
                    /
                    total_requirements
                    *
                    100
                )
            )
        )
        if total_requirements
        else
        0
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    with metric_1:

        render_metric_card(
            "Total Requirements",
            total_requirements,
            "metric-purple",
        )

    with metric_2:

        render_metric_card(
            "Requirements Met",
            completed_requirements,
            "metric-green",
        )

    with metric_3:

        render_metric_card(
            "Requirements Open",
            open_requirements,
            "metric-orange",
        )

    with metric_4:

        render_metric_card(
            "Overall Completion",
            f"{completion_percentage}%",
            "metric-blue",
        )

    checklist_1, progress_1 = st.columns(
        [
            1.7,
            1,
        ]
    )

    with checklist_1:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Requirements Checklist"
        )

        if combined_requirements.empty:

            st.info(
                (
                    "No requirements are available "
                    "for this project."
                )
            )

        else:

            selected_vv_point = (
                st.selectbox(
                    "Filter by V&V point",
                    [
                        "All V&V points"
                    ]
                    +
                    sorted(
                        combined_requirements[
                            "V&V Point"
                        ]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                )
            )

            filtered_requirements = (
                combined_requirements.copy()
            )

            if (
                selected_vv_point
                !=
                "All V&V points"
            ):

                filtered_requirements = (
                    filtered_requirements[
                        filtered_requirements[
                            "V&V Point"
                        ]
                        ==
                        selected_vv_point
                    ]
                )

            for row_index, row in (
                filtered_requirements
                .reset_index(
                    drop=True
                )
                .iterrows()
            ):

                reference = (
                    row["Reference"]
                )

                source = (
                    row["Source"]
                )

                key_prefix = (
                    f"{dashboard_project}_"
                    f"{source}_"
                    f"{reference}"
                )

                with st.expander(
                    (
                        f"{reference} — "
                        f"{row['Requirement']}"
                    ),
                    expanded=False,
                ):

                    detail_1, detail_2 = (
                        st.columns(2)
                    )

                    with detail_1:

                        st.caption(
                            (
                                f"V&V Point: "
                                f"{row['V&V Point']}"
                            )
                        )

                    with detail_2:

                        st.caption(
                            (
                                f"V&V Method: "
                                f"{row['V&V Method']}"
                            )
                        )

                    complete_value = (
                        st.checkbox(
                            "Requirement met",
                            value=bool(
                                row["Complete"]
                            ),
                            key=(
                                f"complete_"
                                f"{key_prefix}"
                            ),
                        )
                    )

                    comment_value = (
                        st.text_input(
                            "Evidence / comment",
                            value=str(
                                row[
                                    "Evidence / Comment"
                                ]
                            ),
                            key=(
                                f"comment_"
                                f"{key_prefix}"
                            ),
                        )
                    )

                    if st.button(
                        "Save requirement status",
                        key=(
                            f"save_"
                            f"{key_prefix}"
                        ),
                    ):

                        save_requirement_completion(
                            project_name=(
                                dashboard_project
                            ),
                            source=(
                                source
                            ),
                            reference=(
                                reference
                            ),
                            is_complete=(
                                complete_value
                            ),
                            evidence_comment=(
                                comment_value
                            ),
                        )

                        st.success(
                            (
                                f"{reference} "
                                f"updated."
                            )
                        )

                        st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with progress_1:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "V&V Progress by Point"
        )

        if combined_requirements.empty:

            st.info(
                (
                    "No V&V data available."
                )
            )

        else:

            grouped = (
                combined_requirements
                .groupby(
                    "V&V Point"
                )
                .agg(
                    Requirements=(
                        "Reference",
                        "count",
                    ),
                    Met=(
                        "Complete",
                        "sum",
                    ),
                )
                .reset_index()
            )

            grouped["Open"] = (
                grouped[
                    "Requirements"
                ]
                -
                grouped["Met"]
            )

            grouped[
                "Completion"
            ] = (
                (
                    grouped["Met"]
                    /
                    grouped[
                        "Requirements"
                    ]
                    *
                    100
                )
                .round()
                .astype(int)
            )

            for _, row in (
                grouped.iterrows()
            ):

                st.markdown(
                    f"""
                    <div
                        style="
                            display:flex;
                            justify-content:space-between;
                            gap:0.7rem;
                            margin-top:0.8rem;
                        "
                    >

                        <span>
                            {row['V&V Point']}
                        </span>

                        <span
                            style="
                                color:#76ddff;
                                font-weight:700;
                            "
                        >
                            {int(row['Completion'])}%
                        </span>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.progress(
                    int(
                        row[
                            "Completion"
                        ]
                    )
                    /
                    100
                )

                st.caption(
                    (
                        f"{int(row['Met'])} met · "
                        f"{int(row['Open'])} open"
                    )
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    lower_1, lower_2 = st.columns(
        [
            1.25,
            1,
        ]
    )

    with lower_1:

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Engineering Deliverables"
        )

        completed_deliverables = 0

        for deliverable in (
            ENGINEERING_DELIVERABLES
        ):

            stored_value = (
                get_deliverable_status(
                    dashboard_project,
                    deliverable,
                )
            )

            updated_value = (
                st.checkbox(
                    deliverable,
                    value=stored_value,
                    key=(
                        f"deliverable_"
                        f"{dashboard_project}_"
                        f"{deliverable}"
                    ),
                )
            )

            if updated_value:

                completed_deliverables += 1

            if (
                updated_value
                !=
                stored_value
            ):

                save_deliverable_status(
                    project_name=(
                        dashboard_project
                    ),
                    deliverable_name=(
                        deliverable
                    ),
                    is_complete=(
                        updated_value
                    ),
                )

        deliverable_percentage = int(
            round(
                (
                    completed_deliverables
                    /
                    len(
                        ENGINEERING_DELIVERABLES
                    )
                    *
                    100
                )
            )
        )

        st.progress(
            deliverable_percentage
            /
            100
        )

        st.caption(
            (
                f"{completed_deliverables} of "
                f"{len(ENGINEERING_DELIVERABLES)} "
                f"deliverables complete"
            )
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with lower_2:

        st.markdown(
            """
            <div class="glass-card-cyan">
            """,
            unsafe_allow_html=True,
        )

        st.subheader(
            "Overall Completion"
        )

        st.markdown(
            f"""
            <div
                style="
                    min-height:260px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    flex-direction:column;
                "
            >

                <div
                    style="
                        width:180px;
                        height:180px;
                        border-radius:50%;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        flex-direction:column;
                        background:
                            radial-gradient(
                                circle,
                                #07152d 55%,
                                transparent 57%
                            ),
                            conic-gradient(
                                #16d8ff
                                0%
                                {completion_percentage}%,
                                #192b4d
                                {completion_percentage}%
                                100%
                            );
                        box-shadow:
                            0 0 34px
                            rgba(29, 190, 255, 0.18);
                    "
                >

                    <div
                        style="
                            color:white;
                            font-size:2.65rem;
                            font-weight:800;
                        "
                    >
                        {completion_percentage}%
                    </div>

                    <div
                        style="
                            color:#aebbd5;
                        "
                    >
                        Complete
                    </div>

                </div>

                <div
                    style="
                        margin-top:1.2rem;
                        color:#9eacc7;
                    "
                >
                    {completed_requirements}
                    met
                    &nbsp;·&nbsp;
                    {open_requirements}
                    open
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )