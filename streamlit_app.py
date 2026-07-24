import sqlite3
from datetime import datetime
from pathlib import Path
import html

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

MILL_TYPES = [
    "FFM",
    "FIM",
    "FRM",
    "CM",
    "HM",
    "Other",
]

MATERIAL_TYPES = [
    "Steel",
    "Aluminium",
]

COOLANT_MEDIA = [
    "Kerosene",
    "Emulsion",
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

SPRAYBAR_ARRANGEMENTS = [
    "Top + bottom bar",
    "Top bar + remote bar",
]

ROW_CONFIGURATIONS = [
    "Single row",
    "Dual row",
]

SPRAYBAR_MATERIALS = [
    "Aluminium",
    "Stainless steel",
]

BAR_CONNECTIONS = [
    "G1/2",
    "G3/4",
    "G1",
    "G1 1/4",
    "G1 1/2",
    "G2",
    "Other",
]

JUNCTION_BOX_TYPES = [
    "J001",
    "J002",
    "J003",
    "J004",
    "J005",
    "J006",
]

CABLE_ENTRY_ANGLES = [
    "0°",
    "90°",
]

YES_NO = [
    "No",
    "Yes",
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

PROJECT_REQUIREMENT_TEMPLATES = {
    "Operating condition": {
        "category": "Operating Condition",
        "help": (
            "Use this when equipment must operate under a particular "
            "environmental or process condition."
        ),
    },
    "Capacity or quantity": {
        "category": "Capacity",
        "help": (
            "Use this when a minimum number, quantity or capacity "
            "must be provided."
        ),
    },
    "Performance level": {
        "category": "Performance",
        "help": (
            "Use this when a measurable level of performance "
            "must be achieved."
        ),
    },
    "Response time": {
        "category": "Performance",
        "help": (
            "Use this when something must happen within a defined time."
        ),
    },
    "Compatibility or interface": {
        "category": "Interface",
        "help": (
            "Use this when the ISV system must connect to or work "
            "with another item."
        ),
    },
    "Product type or standard": {
        "category": "Product",
        "help": (
            "Use this when a particular product, material, standard "
            "or specification must be used."
        ),
    },
    "Reliability or maintenance": {
        "category": "Maintenance",
        "help": (
            "Use this for maintenance, access, replacement or "
            "reliability requirements."
        ),
    },
    "Other requirement": {
        "category": "Other",
        "help": (
            "Use this when none of the guided templates are suitable."
        ),
    },
}

ENGINEERING_DELIVERABLES = [
    "Project Data baseline committed",
    "Project-specific requirements reviewed",
    "Initial layout complete",
    "Layout issued internally",
    "Layout sent to customer",
    "Layout approved",
    "Detailed design complete",
    "Manufacturing drawings issued",
    "Detailing sent to manufacture",
]


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --orange: #f47b20;
    --orange2: #ffb16f;
    --amber: #ffd7ad;
    --bg: #f7f4ef;
    --panel: #ffffff;
    --panel2: #fffaf5;
    --border: rgba(9, 37, 70, 0.10);
    --text: #0b2547;
    --muted: #6f7f92;
    --green: #3fa66a;
}

html,
body,
[class*="css"] {
    font-family: Inter, "Segoe UI", Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 82% 8%,
            rgba(244, 123, 32, 0.08),
            transparent 25%
        ),
        radial-gradient(
            circle at 8% 4%,
            rgba(11, 37, 71, 0.05),
            transparent 22%
        ),
        linear-gradient(
            145deg,
            #fbfaf8 0%,
            #f7f4ef 50%,
            #f4f7fb 100%
        );
    color: var(--text);
}

.block-container {
    max-width: 1600px;
    padding-top: 1.35rem;
    padding-left: 1.8rem;
    padding-right: 1.8rem;
    padding-bottom: 4rem;
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

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0a2342,
            #0d315b
        );
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 0.25rem 0 2rem 0;
}

.sidebar-logo {
    width: 48px;
    height: 48px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(
            145deg,
            #f47b20,
            #ffb16f
        );
    font-size: 1.55rem;
    color: white;
    box-shadow:
        0 0 18px rgba(244, 123, 32, 0.18);
}

.sidebar-title {
    color: white;
    font-size: 1.55rem;
    font-weight: 800;
}

.sidebar-subtitle {
    color: #c6d0dc;
    font-size: 0.82rem;
    margin-top: 0.15rem;
}

section[data-testid="stSidebar"]
div[data-testid="stRadio"] > label {
    display: none;
}

section[data-testid="stSidebar"]
div[data-testid="stRadio"] label {
    border-radius: 12px;
    padding: 0.7rem 0.75rem;
    margin: 0.15rem 0;
    border: 1px solid transparent;
}

section[data-testid="stSidebar"]
div[data-testid="stRadio"] label:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.08);
}

section[data-testid="stSidebar"]
div[data-testid="stRadio"]
label:has(input:checked) {
    background:
        linear-gradient(
            135deg,
            rgba(244, 123, 32, 0.22),
            rgba(255, 177, 111, 0.12)
        );
    border-color: rgba(255, 177, 111, 0.28);
}

.sidebar-footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    color: #b8c3d0;
    font-size: 0.82rem;
}

/* PAGE HEADER */

.page-header {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 1.35rem;
}

.page-icon {
    width: 50px;
    height: 50px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(
            145deg,
            #fff0e4,
            #ffe0c7
        );
    color: #f47b20;
    font-size: 1.5rem;
    box-shadow:
        0 0 16px rgba(244, 123, 32, 0.10);
}

.page-title {
    color: #0b2547;
    font-size: 2.05rem;
    font-weight: 790;
    letter-spacing: -0.035em;
    line-height: 1.05;
}

.page-subtitle {
    color: #6f7f92;
    font-size: 0.95rem;
    margin-top: 0.32rem;
}

/* CONTAINERS */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        linear-gradient(
            145deg,
            #ffffff,
            #fffaf5
        ) !important;
    border:
        1px solid
        rgba(9, 37, 70, 0.10) !important;
    border-radius: 16px !important;
    box-shadow:
        0 15px 34px rgba(11, 37, 71, 0.07);
}

/* SECTION HEADERS */

.section-heading {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.8rem;
}

.section-number {
    min-width: 31px;
    height: 31px;
    padding: 0 0.3rem;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #f47b20;
    font-weight: 800;
    background:
        linear-gradient(
            145deg,
            #fff1e5,
            #ffe2ca
        );
    box-shadow:
        0 0 12px rgba(244, 123, 32, 0.08);
}

.section-title {
    color: #0b2547;
    font-size: 1.13rem;
    font-weight: 740;
}

.subsection-title {
    color: #123762;
    font-size: 1rem;
    font-weight: 720;
    margin-bottom: 0.45rem;
}

/* FORM CONTROLS */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background:
        #ffffff !important;
    border:
        1px solid
        rgba(9, 37, 70, 0.18) !important;
    border-radius:
        10px !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color:
        rgba(244, 123, 32, 0.70) !important;
    box-shadow:
        0 0 0 2px rgba(244, 123, 32, 0.08);
}

input,
textarea {
    color: #0b2547 !important;
}

label {
    color: #0b2547 !important;
    font-weight: 590 !important;
}

/* BUTTONS */

.stButton > button {
    width: 100%;
    min-height: 3rem;
    border-radius: 11px;
    border:
        1px solid
        rgba(244, 123, 32, 0.40);
    background:
        linear-gradient(
            105deg,
            #f47b20,
            #ff9b52,
            #ffb16f
        );
    color: white;
    font-weight: 750;
    box-shadow:
        0 0 16px rgba(244, 123, 32, 0.12);
}

.stButton > button:hover {
    color: white;
    border-color: #ffb16f;
    box-shadow:
        0 0 22px rgba(244, 123, 32, 0.18);
}

/* METRIC CARDS */

.metric-card {
    min-height: 125px;
    padding: 1.1rem;
    border-radius: 15px;
    background:
        linear-gradient(
            145deg,
            #ffffff,
            #fffaf5
        );
    border:
        1px solid rgba(9, 37, 70, 0.10);
    box-shadow:
        0 14px 30px rgba(11, 37, 71, 0.07);
}

.metric-label {
    color: #6f7f92;
    font-size: 0.91rem;
}

.metric-value {
    color: #0b2547;
    font-size: 2.25rem;
    font-weight: 800;
    margin-top: 0.7rem;
    line-height: 1;
}

.metric-orange {
    border-color: rgba(244, 123, 32, 0.34);
}

.metric-green {
    border-color: rgba(63, 166, 106, 0.30);
}

.metric-blue {
    border-color: rgba(18, 55, 98, 0.24);
}

.metric-amber {
    border-color: rgba(255, 177, 111, 0.34);
}

/* INFO STRIP */

.info-strip {
    border:
        1px solid rgba(244, 123, 32, 0.18);
    border-left:
        4px solid #f47b20;
    background:
        #fff7f0;
    padding:
        0.85rem 1rem;
    border-radius:
        10px;
    color:
        #0b2547;
    margin-bottom:
        1rem;
}

/* PREVIEW */

.preview-panel {
    min-height: 250px;
    padding: 1rem;
    border:
        1px solid rgba(9, 37, 70, 0.14);
    border-radius:
        12px;
    background:
        #fbfcfe;
    color:
        #0b2547;
    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;
    line-height:
        1.65;
    white-space:
        pre-wrap;
}

/* TABLES */

div[data-testid="stDataFrame"] {
    border:
        1px solid rgba(9, 37, 70, 0.12);
    border-radius:
        13px;
    overflow:
        hidden;
}

/* EXPANDERS */

details[data-testid="stExpander"] {
    background:
        #ffffff;
    border:
        1px solid rgba(9, 37, 70, 0.10);
    border-radius:
        12px;
    margin-bottom:
        0.6rem;
}

/* PROGRESS */

div[data-testid="stProgress"] > div > div {
    background:
        linear-gradient(
            90deg,
            #123762,
            #1c4d82,
            #f47b20
        );
}

h1,
h2,
h3 {
    color: #0b2547;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_database_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_existing_columns(connection, table_name):
    rows = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [row[1] for row in rows]


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

    # Project-specific requirements
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

    # Locked Project Data revisions
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

    # Items contained in each locked Project Data revision
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

    # Completion status
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

    # Engineering deliverables
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
# GENERAL HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    text = str(value)

    if text.lower() in ["none", "nan"]:
        return ""

    return text


def get_text_value(
    values,
    question_id,
    default="",
):
    value = values.get(
        question_id,
        default,
    )

    value = safe_text(value)

    if not value:
        return default

    return value


def get_float_value(
    values,
    question_id,
    default=0.0,
):
    try:
        value = values.get(
            question_id,
            default,
        )

        if safe_text(value).lower() == "not applicable":
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def get_integer_value(
    values,
    question_id,
    default=0,
):
    try:
        value = values.get(
            question_id,
            default,
        )

        if safe_text(value).lower() == "not applicable":
            return default

        return int(float(value))

    except (TypeError, ValueError):
        return default


def option_index(
    options,
    saved_value,
    default=0,
):
    if saved_value in options:
        return options.index(saved_value)

    return default


def format_number(value):
    try:
        number = float(value)

        if number.is_integer():
            return str(int(number))

        return f"{number:g}"

    except (TypeError, ValueError):
        return str(value)


def escape(value):
    return html.escape(str(value))


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
        <div class="page-header">
            <div class="page-icon">{icon}</div>
            <div>
                <div class="page-title">{escape(title)}</div>
                <div class="page-subtitle">{escape(subtitle)}</div>
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
        <div class="section-heading">
            <div class="section-number">{escape(number)}</div>
            <div class="section-title">{escape(title)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_subsection(title):
    st.markdown(
        f"""
        <div class="subsection-title">
            {escape(title)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label,
    value,
    style_class="metric-orange",
):
    st.markdown(
        f"""
        <div class="metric-card {style_class}">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_strip(text):
    st.markdown(
        f"""
        <div class="info-strip">
            {escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT DATA DATABASE FUNCTIONS
# ============================================================

def load_project_data_revisions(project_name):
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
        params=(project_name,),
    )

    connection.close()
    return dataframe


def load_revision_items(revision_id):
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
        params=(revision_id,),
    )

    connection.close()
    return dataframe


def get_latest_revision_id(project_name):
    revisions = load_project_data_revisions(
        project_name
    )

    if revisions.empty:
        return None

    return int(
        revisions.iloc[-1]["id"]
    )


def get_latest_revision_number(project_name):
    revisions = load_project_data_revisions(
        project_name
    )

    if revisions.empty:
        return "None"

    return str(
        revisions.iloc[-1]["revision_number"]
    )


def get_next_revision_number(project_name):
    revisions = load_project_data_revisions(
        project_name
    )

    if revisions.empty:
        return "00"

    latest = (
        revisions["revision_number"]
        .astype(int)
        .max()
    )

    return f"{latest + 1:02d}"


def load_latest_project_data_values(project_name):
    latest_revision_id = get_latest_revision_id(
        project_name
    )

    if latest_revision_id is None:
        return {}

    items = load_revision_items(
        latest_revision_id
    )

    values = {}

    for _, row in items.iterrows():
        values[
            str(row["requirement_id"])
        ] = safe_text(
            row["required_value"]
        )

    return values


def commit_project_data_revision(
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
                str(row["Question ID"]),
                str(row["Requirement Area"]),
                str(row["Requirement"]),
                str(row["Required Value"]),
                str(row["Unit / Limit"]),
                str(row["V&V Point"]),
                str(row["V&V Method"]),
                str(row["Notes"]),
                "Yes",
            ),
        )

    connection.commit()
    connection.close()


def revision_items_to_dictionary(dataframe):
    result = {}

    for _, row in dataframe.iterrows():
        question_id = str(
            row["requirement_id"]
        )

        result[question_id] = {
            "requirement_area": safe_text(
                row["requirement_area"]
            ),
            "requirement_text": safe_text(
                row["requirement_text"]
            ),
            "required_value": safe_text(
                row["required_value"]
            ),
            "unit_or_limit": safe_text(
                row["unit_or_limit"]
            ),
            "verification_point": safe_text(
                row["verification_point"]
            ),
            "verification_method": safe_text(
                row["verification_method"]
            ),
            "notes": safe_text(
                row["notes"]
            ),
        }

    return result


def find_changed_question_ids(
    previous_items,
    current_items,
):
    previous_dictionary = (
        revision_items_to_dictionary(
            previous_items
        )
    )

    current_dictionary = (
        revision_items_to_dictionary(
            current_items
        )
    )

    all_ids = sorted(
        set(previous_dictionary.keys())
        |
        set(current_dictionary.keys())
    )

    changed_ids = []

    for question_id in all_ids:
        if (
            previous_dictionary.get(question_id)
            !=
            current_dictionary.get(question_id)
        ):
            changed_ids.append(
                question_id
            )

    return changed_ids


def build_revision_history_summary(project_name):
    revisions = load_project_data_revisions(
        project_name
    )

    if revisions.empty:
        return pd.DataFrame()

    rows = []
    previous_items = None

    for _, revision in revisions.iterrows():
        current_items = load_revision_items(
            int(revision["id"])
        )

        if previous_items is None:
            changed_text = "Initial issue"

        else:
            changed_ids = (
                find_changed_question_ids(
                    previous_items,
                    current_items,
                )
            )

            changed_text = (
                ", ".join(changed_ids)
                if changed_ids
                else "No changes"
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
                    safe_text(
                        revision[
                            "committed_by"
                        ]
                    ),
                "Comment":
                    safe_text(
                        revision[
                            "revision_comment"
                        ]
                    ),
            }
        )

        previous_items = current_items

    return pd.DataFrame(rows)


# ============================================================
# PROJECT-SPECIFIC REQUIREMENT DATABASE FUNCTIONS
# ============================================================

def save_project_requirement(
    project_name,
    requirement_title,
    requirement_text,
    category,
    source_department,
    submitted_by,
    boilerplate_name,
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
            boilerplate_name,
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


# ============================================================
# DASHBOARD DATABASE FUNCTIONS
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

    return bool(row[0]), safe_text(row[1])


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
            int(is_complete),
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

    return bool(row[0])


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
            int(is_complete),
        ),
    )

    connection.commit()
    connection.close()


# ============================================================
# PROJECT DATA REQUIREMENT GENERATOR
# ============================================================

def requirement_row(
    question_id,
    area,
    requirement,
    value,
    unit="",
    vv_point="Detailed design review",
    vv_method="Design review",
    notes="",
):
    return {
        "Question ID": question_id,
        "Requirement Area": area,
        "Requirement": requirement,
        "Required Value": value,
        "Unit / Limit": unit,
        "V&V Point": vv_point,
        "V&V Method": vv_method,
        "Notes": notes,
    }


def build_project_data_requirements(data):
    rows = []

    # --------------------------------------------------------
    # PROJECT INFORMATION
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-001",
            "Project Information",
            (
                "The ISV system shall be supplied "
                "for the specified project."
            ),
            data["project_name"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    rows.append(
        requirement_row(
            "STD-002",
            "Project Information",
            (
                "The ISV system shall be supplied "
                "to the specified customer."
            ),
            data["customer_name"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    rows.append(
        requirement_row(
            "STD-003",
            "Project Information",
            (
                "The project destination country "
                "shall be recorded as specified."
            ),
            data["country"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    rows.append(
        requirement_row(
            "STD-004",
            "Project Information",
            (
                "The project shall identify the "
                "responsible Lead Engineer."
            ),
            data["lead_engineer"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    rows.append(
        requirement_row(
            "STD-005",
            "Project Information",
            (
                "The project shall identify the "
                "responsible Project Manager."
            ),
            data["project_manager"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    # --------------------------------------------------------
    # MATERIAL
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-010",
            "Mill Process Data - Material",
            (
                "The ISV system shall be suitable "
                "for processing the specified material type."
            ),
            data["material_type"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    rows.append(
        requirement_row(
            "STD-011",
            "Mill Process Data - Material",
            (
                "The ISV system shall be suitable "
                "for the specified alloy range."
            ),
            data["alloy_range"],
            vv_point="Requirements review",
            vv_method="Document review",
        )
    )

    # --------------------------------------------------------
    # STRIP DATA
    # --------------------------------------------------------

    strip_fields = [
        (
            "STD-020",
            "maximum entry thickness",
            data["max_entry_thickness"],
        ),
        (
            "STD-021",
            "minimum entry thickness",
            data["min_entry_thickness"],
        ),
        (
            "STD-022",
            "maximum exit thickness",
            data["max_exit_thickness"],
        ),
        (
            "STD-023",
            "minimum exit thickness",
            data["min_exit_thickness"],
        ),
        (
            "STD-024",
            "maximum strip width",
            data["max_strip_width"],
        ),
        (
            "STD-025",
            "minimum strip width",
            data["min_strip_width"],
        ),
    ]

    for question_id, description, value in strip_fields:
        rows.append(
            requirement_row(
                question_id,
                "Mill Process Data - Strip Data",
                (
                    "The ISV system shall be designed "
                    f"for the specified {description}."
                ),
                format_number(value),
                "mm",
                vv_point="Concept design review",
                vv_method="Design review",
            )
        )

    # --------------------------------------------------------
    # ROLLING DATA
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-030",
            "Mill Process Data - Rolling Data",
            (
                "The ISV system shall be designed "
                "for the specified mill type."
            ),
            data["mill_type"],
            vv_point="Concept design review",
            vv_method="Design review",
        )
    )

    rows.append(
        requirement_row(
            "STD-031",
            "Mill Process Data - Rolling Data",
            (
                "The ISV system interface shall be "
                "compatible with the specified mill supplier."
            ),
            data["mill_supplier"],
            vv_point="Concept design review",
            vv_method="Document review",
        )
    )

    rolling_numeric = [
        (
            "STD-032",
            "maximum rolling speed",
            data["max_rolling_speed"],
            "m/min",
        ),
        (
            "STD-033",
            "maximum mill force",
            data["max_mill_force"],
            "kN",
        ),
        (
            "STD-034",
            "maximum strip stress",
            data["max_strip_stress"],
            "MPa",
        ),
        (
            "STD-035",
            "minimum strip stress",
            data["min_strip_stress"],
            "MPa",
        ),
        (
            "STD-036",
            "main drive power",
            data["main_drive_power"],
            "kW",
        ),
        (
            "STD-037",
            "maximum reduction",
            data["max_reduction"],
            "%",
        ),
        (
            "STD-038",
            "minimum reduction",
            data["min_reduction"],
            "%",
        ),
    ]

    for (
        question_id,
        description,
        value,
        unit,
    ) in rolling_numeric:
        rows.append(
            requirement_row(
                question_id,
                "Mill Process Data - Rolling Data",
                (
                    "The ISV system shall be designed "
                    f"for the specified {description}."
                ),
                format_number(value),
                unit,
                vv_point="Concept design review",
                vv_method="Design review",
            )
        )

    # --------------------------------------------------------
    # ROLL DATA
    # --------------------------------------------------------

    roll_fields = [
        (
            "STD-040",
            "minimum work roll diameter",
            data["min_work_roll_diameter"],
        ),
        (
            "STD-041",
            "maximum work roll diameter",
            data["max_work_roll_diameter"],
        ),
        (
            "STD-042",
            "minimum backup roll diameter",
            data["min_backup_roll_diameter"],
        ),
        (
            "STD-043",
            "maximum backup roll diameter",
            data["max_backup_roll_diameter"],
        ),
    ]

    for (
        question_id,
        description,
        value,
    ) in roll_fields:
        rows.append(
            requirement_row(
                question_id,
                "Mill Process Data - Roll Data",
                (
                    "The ISV system shall be designed "
                    f"for the specified {description}."
                ),
                format_number(value),
                "mm",
                vv_point="Concept design review",
                vv_method="Design review",
            )
        )

    # --------------------------------------------------------
    # COOLING SYSTEM
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-050",
            "Cooling System Requirements",
            (
                "The cooling system shall provide "
                "the specified required cooling capacity."
            ),
            format_number(
                data["required_cooling_capacity"]
            ),
            "L/min",
            vv_point="Detailed design review",
            vv_method="Calculation",
        )
    )

    rows.append(
        requirement_row(
            "STD-051",
            "Cooling System Requirements",
            (
                "The ISV system shall be designed "
                "for the specified available coolant pressure."
            ),
            format_number(
                data["available_coolant_pressure"]
            ),
            "bar",
            vv_point="Detailed design review",
            vv_method="Design review",
        )
    )

    rows.append(
        requirement_row(
            "STD-052",
            "Cooling System Requirements",
            (
                "The ISV system shall be suitable "
                "for the specified coolant temperature."
            ),
            format_number(
                data["coolant_temperature"]
            ),
            "°C",
            vv_point="Detailed design review",
            vv_method="Design review",
        )
    )

    rows.append(
        requirement_row(
            "STD-053",
            "Cooling System Requirements",
            (
                "The ISV system shall be compatible "
                "with the specified coolant medium."
            ),
            data["coolant_medium"],
            vv_point="Detailed design review",
            vv_method="Design review",
        )
    )

    # --------------------------------------------------------
    # SPRAYBAR BASIC ARRANGEMENT
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-060",
            "Spraybar Configuration - Basic Arrangement",
            (
                "The ISV system shall use the "
                "specified spraybar arrangement."
            ),
            data["spraybar_arrangement"],
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-061",
            "Spraybar Configuration - Basic Arrangement",
            (
                "The spraybar shall use the "
                "specified row configuration."
            ),
            data["row_configuration"],
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-062",
            "Spraybar Configuration - Basic Arrangement",
            (
                "The spraybar shall be manufactured "
                "from the specified material."
            ),
            data["spraybar_material"],
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    # --------------------------------------------------------
    # VALVES
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-063",
            "Spraybar Configuration - Valve Configuration",
            (
                "The ISV system shall use the "
                "specified ISV product variant."
            ),
            data["product_variant"],
            vv_point="Concept design review",
            vv_method="Design review",
        )
    )

    rows.append(
        requirement_row(
            "STD-064",
            "Spraybar Configuration - Valve Configuration",
            (
                "The ISV MK3 valve configuration "
                "shall use the specified configuration."
            ),
            (
                data["mk3_configuration"]
                if data["product_variant"]
                == "ISV - MK3"
                else "Not applicable"
            ),
            vv_point="Concept design review",
            vv_method="Design review",
            notes=(
                "Applicable only when ISV - MK3 "
                "is selected."
            ),
        )
    )

    # --------------------------------------------------------
    # NOZZLES
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-070",
            "Spraybar Configuration - Nozzle Configuration",
            (
                "The spraybar nozzle arrangement shall "
                "use the specified nozzle pitch."
            ),
            format_number(
                data["nozzle_pitch"]
            ),
            "mm",
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-071",
            "Spraybar Configuration - Nozzle Configuration",
            (
                "Each top valve shall supply the "
                "specified number of nozzles."
            ),
            str(
                data["nozzles_per_valve_top"]
            ),
            "nozzles / valve",
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-072",
            "Spraybar Configuration - Nozzle Configuration",
            (
                "Each bottom valve shall supply the "
                "specified number of nozzles."
            ),
            (
                str(
                    data[
                        "nozzles_per_valve_bottom"
                    ]
                )
                if data["spraybar_arrangement"]
                == "Top + bottom bar"
                else "Not applicable"
            ),
            (
                "nozzles / valve"
                if data["spraybar_arrangement"]
                == "Top + bottom bar"
                else ""
            ),
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-073",
            "Spraybar Configuration - Nozzle Configuration",
            (
                "The spraybar configuration shall include "
                "a top backup nozzle as specified."
            ),
            data["top_backup_nozzle"],
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-074",
            "Spraybar Configuration - Bite Lube Spray",
            (
                "The bite lubrication spray shall use "
                "the specified nozzle pitch."
            ),
            format_number(
                data["bite_lube_pitch"]
            ),
            "mm",
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-075",
            "Spraybar Configuration - Bite Lube Spray",
            (
                "The bite lubrication spray shall contain "
                "the specified number of nozzles."
            ),
            str(
                data["bite_lube_nozzles"]
            ),
            "nozzles",
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-076",
            "Spraybar Configuration - Bite Lube Spray",
            (
                "The bite lubrication system shall use "
                "a remote valve as specified."
            ),
            data["bite_lube_remote_valve"],
            vv_point="Detailed design review",
            vv_method="Design review",
        )
    )

    # --------------------------------------------------------
    # COOLANT CONNECTIONS
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-080",
            "Coolant Connections",
            (
                "The coolant connection to the spraybar "
                "shall use the specified connection size."
            ),
            data["connection_to_bar"],
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-081",
            "Coolant Connections",
            (
                "The coolant hose connection shall use "
                "the specified thread size."
            ),
            data["hose_thread_size"],
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-082",
            "Coolant Connections",
            (
                "The coolant hose connection shall use "
                "the specified cone configuration."
            ),
            data["hose_cone"],
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-083",
            "Coolant Connections",
            (
                "The coolant block shall use the "
                "specified connection angle."
            ),
            format_number(
                data["coolant_block_angle"]
            ),
            "degrees",
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-084",
            "Coolant Connections",
            (
                "The ISV system shall provide the "
                "specified number of coolant connections."
            ),
            str(
                data["number_coolant_connections"]
            ),
            "connections",
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    # --------------------------------------------------------
    # PNEUMATICS
    # --------------------------------------------------------

    mk3_selected = (
        data["product_variant"]
        == "ISV - MK3"
    )

    rows.append(
        requirement_row(
            "STD-090",
            "Pneumatic Requirements",
            (
                "The MK3 pneumatic system shall provide "
                "the specified number of air connections."
            ),
            (
                str(
                    data["number_air_connections"]
                )
                if mk3_selected
                else "Not applicable"
            ),
            (
                "connections"
                if mk3_selected
                else ""
            ),
            vv_point="Detailed design review",
            vv_method="Drawing review",
            notes=(
                "Applicable only when ISV - MK3 "
                "is selected."
            ),
        )
    )

    rows.append(
        requirement_row(
            "STD-091",
            "Pneumatic Requirements",
            (
                "An air intensifier shall be supplied "
                "as specified for the MK3 system."
            ),
            (
                data["air_intensifier_supplied"]
                if mk3_selected
                else "Not applicable"
            ),
            vv_point="Detailed design review",
            vv_method="Document review",
            notes=(
                "Applicable only when ISV - MK3 "
                "is selected."
            ),
        )
    )

    rows.append(
        requirement_row(
            "STD-092",
            "Pneumatic Requirements",
            (
                "An air control panel shall be supplied "
                "as specified for the MK3 system."
            ),
            (
                data["air_control_panel_supplied"]
                if mk3_selected
                else "Not applicable"
            ),
            vv_point="Detailed design review",
            vv_method="Document review",
            notes=(
                "Applicable only when ISV - MK3 "
                "is selected."
            ),
        )
    )

    # --------------------------------------------------------
    # ELECTRICAL
    # --------------------------------------------------------

    rows.append(
        requirement_row(
            "STD-100",
            "Electrical Requirements",
            (
                "Each signal cable shall have the "
                "specified cable length."
            ),
            format_number(
                data["signal_cable_length"]
            ),
            "m",
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-101",
            "Electrical Requirements",
            (
                "The ISV electrical system shall provide "
                "the specified quantity of signal cables."
            ),
            str(
                data["signal_cable_quantity"]
            ),
            "cables",
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-102",
            "Electrical Requirements",
            (
                "The signal cable entry shall use the "
                "specified entry angle."
            ),
            data["cable_entry_angle"],
            vv_point="Approval drawing review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-103",
            "Electrical Requirements",
            (
                "The ISV electrical system shall provide "
                "the specified quantity of junction boxes."
            ),
            str(
                data["junction_box_quantity"]
            ),
            "junction boxes",
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    rows.append(
        requirement_row(
            "STD-104",
            "Electrical Requirements",
            (
                "The ISV electrical system shall use "
                "the specified junction box type."
            ),
            data["junction_box_type"],
            vv_point="Detailed design review",
            vv_method="Drawing review",
        )
    )

    return pd.DataFrame(rows)


# ============================================================
# INITIALISE DATABASE
# ============================================================

create_or_update_database()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">⬢</div>
            <div>
                <div class="sidebar-title">ISV</div>
                <div class="sidebar-subtitle">
                    Requirements Management
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        [
            "1. Project Data",
            "2. Project-Specific Requirements",
            "3. Engineering Dashboard",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="sidebar-footer">
            <strong>Engineering Team</strong>
            <br>
            Internal ISV engineering tool
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE 1 — PROJECT DATA
# ============================================================

if selected_page == "1. Project Data":

    render_page_heading(
        "▤",
        "Project Data",
        (
            "Define the controlled engineering baseline "
            "for an ISV project and commit locked revisions."
        ),
    )

    # --------------------------------------------------------
    # PROJECT SELECTOR / REVISION STATUS
    # --------------------------------------------------------

    project_selector_column, revision_column = (
        st.columns([3, 1])
    )

    with project_selector_column:
        selected_project = st.selectbox(
            "Project",
            ALLOWED_PROJECTS,
            key="project_data_project",
        )

    latest_revision_number = (
        get_latest_revision_number(
            selected_project
        )
    )

    next_revision_number = (
        get_next_revision_number(
            selected_project
        )
    )

    with revision_column:
        render_metric_card(
            "Next Revision",
            next_revision_number,
            "metric-orange",
        )

    latest_values = (
        load_latest_project_data_values(
            selected_project
        )
    )

    if latest_revision_number == "None":
        render_info_strip(
            (
                "No locked Project Data revision exists for this project. "
                "The first committed baseline will be Revision 00."
            )
        )
    else:
        render_info_strip(
            (
                f"Latest locked revision: {latest_revision_number}. "
                f"Any new committed changes will create Revision "
                f"{next_revision_number}."
            )
        )

    # --------------------------------------------------------
    # 1. PROJECT INFORMATION
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "1",
            "Project Information",
        )

        project_info_col1, project_info_col2 = (
            st.columns(2)
        )

        with project_info_col1:

            st.text_input(
                "Project reference",
                value=selected_project,
                disabled=True,
            )

            customer_name = st.text_input(
                "Customer name *",
                value=get_text_value(
                    latest_values,
                    "STD-002",
                    "",
                ),
                key=f"customer_{selected_project}",
            )

            country = st.text_input(
                "Country *",
                value=get_text_value(
                    latest_values,
                    "STD-003",
                    "",
                ),
                key=f"country_{selected_project}",
            )

        with project_info_col2:

            lead_engineer = st.text_input(
                "Lead Engineer *",
                value=get_text_value(
                    latest_values,
                    "STD-004",
                    "",
                ),
                key=f"lead_engineer_{selected_project}",
            )

            project_manager = st.text_input(
                "Project Manager *",
                value=get_text_value(
                    latest_values,
                    "STD-005",
                    "",
                ),
                key=f"project_manager_{selected_project}",
            )

            st.caption(
                "These fields identify the responsible "
                "project engineering team."
            )

    # --------------------------------------------------------
    # 2. MILL PROCESS DATA
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "2",
            "Mill Process Data",
        )

        # MATERIAL

        render_subsection(
            "Material"
        )

        material_col1, material_col2 = (
            st.columns(2)
        )

        with material_col1:

            saved_material = get_text_value(
                latest_values,
                "STD-010",
                "Steel",
            )

            material_type = st.selectbox(
                "Material type *",
                MATERIAL_TYPES,
                index=option_index(
                    MATERIAL_TYPES,
                    saved_material,
                    0,
                ),
                key=f"material_{selected_project}",
            )

        with material_col2:

            alloy_range = st.text_input(
                "Alloy range *",
                value=get_text_value(
                    latest_values,
                    "STD-011",
                    "",
                ),
                placeholder=(
                    "Example: Carbon steel, stainless grades 304–316"
                ),
                key=f"alloy_{selected_project}",
            )

        st.divider()

        # STRIP DATA

        render_subsection(
            "Strip Data"
        )

        strip_col1, strip_col2, strip_col3 = (
            st.columns(3)
        )

        with strip_col1:

            max_entry_thickness = st.number_input(
                "Maximum entry thickness (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-020",
                    0.0,
                ),
                step=0.1,
                key=f"max_entry_{selected_project}",
            )

            min_entry_thickness = st.number_input(
                "Minimum entry thickness (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-021",
                    0.0,
                ),
                step=0.1,
                key=f"min_entry_{selected_project}",
            )

        with strip_col2:

            max_exit_thickness = st.number_input(
                "Maximum exit thickness (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-022",
                    0.0,
                ),
                step=0.1,
                key=f"max_exit_{selected_project}",
            )

            min_exit_thickness = st.number_input(
                "Minimum exit thickness (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-023",
                    0.0,
                ),
                step=0.1,
                key=f"min_exit_{selected_project}",
            )

        with strip_col3:

            max_strip_width = st.number_input(
                "Maximum strip width (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-024",
                    0.0,
                ),
                step=1.0,
                key=f"max_width_{selected_project}",
            )

            min_strip_width = st.number_input(
                "Minimum strip width (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-025",
                    0.0,
                ),
                step=1.0,
                key=f"min_width_{selected_project}",
            )

        st.divider()

        # ROLLING DATA

        render_subsection(
            "Rolling Data"
        )

        rolling_col1, rolling_col2, rolling_col3 = (
            st.columns(3)
        )

        saved_mill_type = get_text_value(
            latest_values,
            "STD-030",
            "FFM",
        )

        with rolling_col1:

            mill_type_selection = st.selectbox(
                "Mill type *",
                MILL_TYPES,
                index=option_index(
                    MILL_TYPES,
                    (
                        saved_mill_type
                        if saved_mill_type
                        in MILL_TYPES
                        else "Other"
                    ),
                    0,
                ),
                key=f"mill_type_{selected_project}",
            )

            if mill_type_selection == "Other":

                mill_type = st.text_input(
                    "Specify mill type *",
                    value=(
                        saved_mill_type
                        if saved_mill_type
                        not in MILL_TYPES
                        else ""
                    ),
                    key=f"mill_other_{selected_project}",
                )

            else:
                mill_type = mill_type_selection

            mill_supplier = st.text_input(
                "Mill supplier *",
                value=get_text_value(
                    latest_values,
                    "STD-031",
                    "",
                ),
                key=f"mill_supplier_{selected_project}",
            )

            max_rolling_speed = st.number_input(
                "Maximum rolling speed (m/min) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-032",
                    0.0,
                ),
                step=10.0,
                key=f"rolling_speed_{selected_project}",
            )

        with rolling_col2:

            max_mill_force = st.number_input(
                "Maximum mill force (kN) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-033",
                    0.0,
                ),
                step=100.0,
                key=f"mill_force_{selected_project}",
            )

            max_strip_stress = st.number_input(
                "Maximum strip stress (MPa) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-034",
                    0.0,
                ),
                step=1.0,
                key=f"max_stress_{selected_project}",
            )

            min_strip_stress = st.number_input(
                "Minimum strip stress (MPa) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-035",
                    0.0,
                ),
                step=1.0,
                key=f"min_stress_{selected_project}",
            )

        with rolling_col3:

            main_drive_power = st.number_input(
                "Main drive power (kW) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-036",
                    0.0,
                ),
                step=10.0,
                key=f"drive_power_{selected_project}",
            )

            max_reduction = st.number_input(
                "Maximum reduction (%) *",
                min_value=0.0,
                max_value=100.0,
                value=min(
                    100.0,
                    get_float_value(
                        latest_values,
                        "STD-037",
                        0.0,
                    ),
                ),
                step=1.0,
                key=f"max_reduction_{selected_project}",
            )

            min_reduction = st.number_input(
                "Minimum reduction (%) *",
                min_value=0.0,
                max_value=100.0,
                value=min(
                    100.0,
                    get_float_value(
                        latest_values,
                        "STD-038",
                        0.0,
                    ),
                ),
                step=1.0,
                key=f"min_reduction_{selected_project}",
            )

        st.divider()

        # ROLL DATA

        render_subsection(
            "Roll Data"
        )

        roll_col1, roll_col2 = (
            st.columns(2)
        )

        with roll_col1:

            min_work_roll_diameter = (
                st.number_input(
                    "Minimum work roll diameter (mm) *",
                    min_value=0.0,
                    value=get_float_value(
                        latest_values,
                        "STD-040",
                        0.0,
                    ),
                    step=1.0,
                    key=f"min_work_roll_{selected_project}",
                )
            )

            max_work_roll_diameter = (
                st.number_input(
                    "Maximum work roll diameter (mm) *",
                    min_value=0.0,
                    value=get_float_value(
                        latest_values,
                        "STD-041",
                        0.0,
                    ),
                    step=1.0,
                    key=f"max_work_roll_{selected_project}",
                )
            )

        with roll_col2:

            min_backup_roll_diameter = (
                st.number_input(
                    "Minimum backup roll diameter (mm) *",
                    min_value=0.0,
                    value=get_float_value(
                        latest_values,
                        "STD-042",
                        0.0,
                    ),
                    step=1.0,
                    key=f"min_backup_roll_{selected_project}",
                )
            )

            max_backup_roll_diameter = (
                st.number_input(
                    "Maximum backup roll diameter (mm) *",
                    min_value=0.0,
                    value=get_float_value(
                        latest_values,
                        "STD-043",
                        0.0,
                    ),
                    step=1.0,
                    key=f"max_backup_roll_{selected_project}",
                )
            )

    # --------------------------------------------------------
    # 3. COOLING SYSTEM REQUIREMENTS
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "3",
            "Cooling System Requirements",
        )

        cooling_col1, cooling_col2 = (
            st.columns(2)
        )

        with cooling_col1:

            required_cooling_capacity = (
                st.number_input(
                    "Required cooling capacity (L/min) *",
                    min_value=0.0,
                    value=get_float_value(
                        latest_values,
                        "STD-050",
                        0.0,
                    ),
                    step=10.0,
                    key=f"cooling_capacity_{selected_project}",
                )
            )

            available_coolant_pressure = (
                st.number_input(
                    "Available coolant pressure (bar) *",
                    min_value=0.0,
                    value=get_float_value(
                        latest_values,
                        "STD-051",
                        0.0,
                    ),
                    step=0.1,
                    key=f"coolant_pressure_{selected_project}",
                )
            )

        with cooling_col2:

            coolant_temperature = st.number_input(
                "Coolant temperature (°C) *",
                value=get_float_value(
                    latest_values,
                    "STD-052",
                    20.0,
                ),
                step=1.0,
                key=f"coolant_temp_{selected_project}",
            )

            saved_coolant = get_text_value(
                latest_values,
                "STD-053",
                "Emulsion",
            )

            coolant_selection = st.selectbox(
                "Coolant medium *",
                COOLANT_MEDIA,
                index=option_index(
                    COOLANT_MEDIA,
                    (
                        saved_coolant
                        if saved_coolant
                        in COOLANT_MEDIA
                        else "Other"
                    ),
                    1,
                ),
                key=f"coolant_medium_{selected_project}",
            )

            if coolant_selection == "Other":

                coolant_medium = st.text_input(
                    "Specify coolant medium *",
                    value=(
                        saved_coolant
                        if saved_coolant
                        not in COOLANT_MEDIA
                        else ""
                    ),
                    key=f"other_coolant_{selected_project}",
                )

            else:
                coolant_medium = coolant_selection

    # --------------------------------------------------------
    # 4. SPRAYBAR CONFIGURATION
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "4",
            "Spraybar Configuration",
        )

        # BASIC ARRANGEMENT

        render_subsection(
            "Basic Arrangement"
        )

        arrangement_col1, arrangement_col2, arrangement_col3 = (
            st.columns(3)
        )

        saved_arrangement = get_text_value(
            latest_values,
            "STD-060",
            "Top + bottom bar",
        )

        with arrangement_col1:

            spraybar_arrangement = st.selectbox(
                "Arrangement *",
                SPRAYBAR_ARRANGEMENTS,
                index=option_index(
                    SPRAYBAR_ARRANGEMENTS,
                    saved_arrangement,
                    0,
                ),
                key=f"arrangement_{selected_project}",
            )

        saved_row_configuration = get_text_value(
            latest_values,
            "STD-061",
            "Single row",
        )

        with arrangement_col2:

            row_configuration = st.selectbox(
                "Row configuration *",
                ROW_CONFIGURATIONS,
                index=option_index(
                    ROW_CONFIGURATIONS,
                    saved_row_configuration,
                    0,
                ),
                key=f"row_config_{selected_project}",
            )

        saved_spraybar_material = get_text_value(
            latest_values,
            "STD-062",
            "Stainless steel",
        )

        with arrangement_col3:

            spraybar_material = st.selectbox(
                "Spraybar material *",
                SPRAYBAR_MATERIALS,
                index=option_index(
                    SPRAYBAR_MATERIALS,
                    saved_spraybar_material,
                    1,
                ),
                key=f"bar_material_{selected_project}",
            )

        st.divider()

        # VALVE CONFIGURATION

        render_subsection(
            "Valve Configuration"
        )

        valve_col1, valve_col2 = (
            st.columns(2)
        )

        saved_variant = get_text_value(
            latest_values,
            "STD-063",
            "ISV - MK3",
        )

        with valve_col1:

            product_variant = st.selectbox(
                "ISV product variant *",
                ISV_PRODUCT_VARIANTS,
                index=option_index(
                    ISV_PRODUCT_VARIANTS,
                    saved_variant,
                    0,
                ),
                key=f"variant_{selected_project}",
            )

        with valve_col2:

            if product_variant == "ISV - MK3":

                saved_mk3 = get_text_value(
                    latest_values,
                    "STD-064",
                    "Standard",
                )

                mk3_configuration = st.selectbox(
                    "MK3 configuration *",
                    MK3_CONFIGURATIONS,
                    index=option_index(
                        MK3_CONFIGURATIONS,
                        saved_mk3,
                        0,
                    ),
                    key=f"mk3_config_{selected_project}",
                )

            else:

                mk3_configuration = (
                    "Not applicable"
                )

                st.info(
                    "MK3 configuration is not applicable "
                    "to the selected valve variant."
                )

        st.divider()

        # NOZZLE CONFIGURATION

        render_subsection(
            "Nozzle Configuration"
        )

        nozzle_col1, nozzle_col2 = (
            st.columns(2)
        )

        with nozzle_col1:

            nozzle_pitch = st.number_input(
                "Nozzle pitch (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-070",
                    0.0,
                ),
                step=1.0,
                key=f"nozzle_pitch_{selected_project}",
            )

            nozzles_per_valve_top = (
                st.number_input(
                    "Nozzles per valve - top *",
                    min_value=0,
                    value=get_integer_value(
                        latest_values,
                        "STD-071",
                        0,
                    ),
                    step=1,
                    key=f"top_nozzles_{selected_project}",
                )
            )

            nozzles_per_valve_bottom = (
                st.number_input(
                    "Nozzles per valve - bottom *",
                    min_value=0,
                    value=get_integer_value(
                        latest_values,
                        "STD-072",
                        0,
                    ),
                    step=1,
                    disabled=(
                        spraybar_arrangement
                        != "Top + bottom bar"
                    ),
                    key=f"bottom_nozzles_{selected_project}",
                )
            )

        with nozzle_col2:

            saved_backup_nozzle = get_text_value(
                latest_values,
                "STD-073",
                "No",
            )

            top_backup_nozzle = st.selectbox(
                "Top backup nozzle *",
                YES_NO,
                index=option_index(
                    YES_NO,
                    saved_backup_nozzle,
                    0,
                ),
                key=f"backup_nozzle_{selected_project}",
            )

        st.divider()

        # BITE LUBE

        render_subsection(
            "Bite Lube Spray"
        )

        bite_col1, bite_col2, bite_col3 = (
            st.columns(3)
        )

        with bite_col1:

            bite_lube_pitch = st.number_input(
                "Pitching (mm) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-074",
                    0.0,
                ),
                step=1.0,
                key=f"bite_pitch_{selected_project}",
            )

        with bite_col2:

            bite_lube_nozzles = st.number_input(
                "Number of nozzles *",
                min_value=0,
                value=get_integer_value(
                    latest_values,
                    "STD-075",
                    0,
                ),
                step=1,
                key=f"bite_nozzles_{selected_project}",
            )

        with bite_col3:

            saved_remote_valve = get_text_value(
                latest_values,
                "STD-076",
                "No",
            )

            bite_lube_remote_valve = (
                st.selectbox(
                    "Remote valve *",
                    YES_NO,
                    index=option_index(
                        YES_NO,
                        saved_remote_valve,
                        0,
                    ),
                    key=f"remote_valve_{selected_project}",
                )
            )

    # --------------------------------------------------------
    # 5. COOLANT CONNECTIONS
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "5",
            "Coolant Connections",
        )

        connection_col1, connection_col2 = (
            st.columns(2)
        )

        saved_bar_connection = get_text_value(
            latest_values,
            "STD-080",
            "G1",
        )

        with connection_col1:

            bar_connection_selection = (
                st.selectbox(
                    "Connection to bar *",
                    BAR_CONNECTIONS,
                    index=option_index(
                        BAR_CONNECTIONS,
                        (
                            saved_bar_connection
                            if saved_bar_connection
                            in BAR_CONNECTIONS
                            else "Other"
                        ),
                        2,
                    ),
                    key=f"bar_connection_{selected_project}",
                )
            )

            if bar_connection_selection == "Other":

                connection_to_bar = st.text_input(
                    "Specify connection to bar *",
                    value=(
                        saved_bar_connection
                        if saved_bar_connection
                        not in BAR_CONNECTIONS
                        else ""
                    ),
                    key=f"bar_connection_other_{selected_project}",
                )

            else:
                connection_to_bar = (
                    bar_connection_selection
                )

            hose_thread_size = st.text_input(
                "Connection to hose - thread size *",
                value=get_text_value(
                    latest_values,
                    "STD-081",
                    "",
                ),
                placeholder="Example: G1",
                key=f"hose_thread_{selected_project}",
            )

            hose_cone = st.text_input(
                "Connection to hose - cone *",
                value=get_text_value(
                    latest_values,
                    "STD-082",
                    "",
                ),
                placeholder="Enter cone specification",
                key=f"hose_cone_{selected_project}",
            )

        with connection_col2:

            coolant_block_angle = st.number_input(
                "Coolant block angle (degrees) *",
                min_value=0.0,
                max_value=360.0,
                value=min(
                    360.0,
                    get_float_value(
                        latest_values,
                        "STD-083",
                        0.0,
                    ),
                ),
                step=1.0,
                key=f"block_angle_{selected_project}",
            )

            number_coolant_connections = (
                st.number_input(
                    "Number of coolant connections *",
                    min_value=1,
                    value=max(
                        1,
                        get_integer_value(
                            latest_values,
                            "STD-084",
                            1,
                        ),
                    ),
                    step=1,
                    key=f"coolant_connections_{selected_project}",
                )
            )

    # --------------------------------------------------------
    # 6. PNEUMATIC REQUIREMENTS
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "6",
            "Pneumatic Requirements",
        )

        if product_variant == "ISV - MK3":

            render_info_strip(
                (
                    "Pneumatic requirements are shown because "
                    "ISV - MK3 is selected."
                )
            )

            pneumatic_col1, pneumatic_col2, pneumatic_col3 = (
                st.columns(3)
            )

            with pneumatic_col1:

                number_air_connections = (
                    st.number_input(
                        "Number of air connections *",
                        min_value=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_values,
                                "STD-090",
                                1,
                            ),
                        ),
                        step=1,
                        key=f"air_connections_{selected_project}",
                    )
                )

            with pneumatic_col2:

                saved_intensifier = get_text_value(
                    latest_values,
                    "STD-091",
                    "No",
                )

                air_intensifier_supplied = (
                    st.selectbox(
                        "Air intensifier supplied *",
                        YES_NO,
                        index=option_index(
                            YES_NO,
                            saved_intensifier,
                            0,
                        ),
                        key=f"intensifier_{selected_project}",
                    )
                )

            with pneumatic_col3:

                saved_air_panel = get_text_value(
                    latest_values,
                    "STD-092",
                    "No",
                )

                air_control_panel_supplied = (
                    st.selectbox(
                        "Air control panel supplied *",
                        YES_NO,
                        index=option_index(
                            YES_NO,
                            saved_air_panel,
                            0,
                        ),
                        key=f"air_panel_{selected_project}",
                    )
                )

        else:

            number_air_connections = 0
            air_intensifier_supplied = (
                "Not applicable"
            )
            air_control_panel_supplied = (
                "Not applicable"
            )

            st.info(
                "Pneumatic requirements are only applicable "
                "when ISV - MK3 is selected."
            )

    # --------------------------------------------------------
    # 7. ELECTRICAL REQUIREMENTS
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "7",
            "Electrical Requirements",
        )

        electrical_col1, electrical_col2 = (
            st.columns(2)
        )

        with electrical_col1:

            signal_cable_length = st.number_input(
                "Signal cable length (m) *",
                min_value=0.0,
                value=get_float_value(
                    latest_values,
                    "STD-100",
                    0.0,
                ),
                step=1.0,
                key=f"signal_length_{selected_project}",
            )

            signal_cable_quantity = st.number_input(
                "Quantity of signal cables *",
                min_value=1,
                value=max(
                    1,
                    get_integer_value(
                        latest_values,
                        "STD-101",
                        1,
                    ),
                ),
                step=1,
                key=f"signal_quantity_{selected_project}",
            )

            saved_cable_angle = get_text_value(
                latest_values,
                "STD-102",
                "0°",
            )

            cable_entry_angle = st.selectbox(
                "Cable entry angle *",
                CABLE_ENTRY_ANGLES,
                index=option_index(
                    CABLE_ENTRY_ANGLES,
                    saved_cable_angle,
                    0,
                ),
                key=f"cable_angle_{selected_project}",
            )

        with electrical_col2:

            junction_box_quantity = st.number_input(
                "Junction box quantity *",
                min_value=0,
                value=get_integer_value(
                    latest_values,
                    "STD-103",
                    0,
                ),
                step=1,
                key=f"junction_quantity_{selected_project}",
            )

            saved_junction_type = get_text_value(
                latest_values,
                "STD-104",
                "J001",
            )

            junction_box_type = st.selectbox(
                "Junction box type *",
                JUNCTION_BOX_TYPES,
                index=option_index(
                    JUNCTION_BOX_TYPES,
                    saved_junction_type,
                    0,
                ),
                key=f"junction_type_{selected_project}",
            )

    # --------------------------------------------------------
    # BUILD CURRENT PROJECT DATA
    # --------------------------------------------------------

    project_data = {
        "project_name":
            selected_project,
        "customer_name":
            customer_name.strip(),
        "country":
            country.strip(),
        "lead_engineer":
            lead_engineer.strip(),
        "project_manager":
            project_manager.strip(),
        "material_type":
            material_type,
        "alloy_range":
            alloy_range.strip(),
        "max_entry_thickness":
            max_entry_thickness,
        "min_entry_thickness":
            min_entry_thickness,
        "max_exit_thickness":
            max_exit_thickness,
        "min_exit_thickness":
            min_exit_thickness,
        "max_strip_width":
            max_strip_width,
        "min_strip_width":
            min_strip_width,
        "mill_type":
            str(mill_type).strip(),
        "mill_supplier":
            mill_supplier.strip(),
        "max_rolling_speed":
            max_rolling_speed,
        "max_mill_force":
            max_mill_force,
        "max_strip_stress":
            max_strip_stress,
        "min_strip_stress":
            min_strip_stress,
        "main_drive_power":
            main_drive_power,
        "max_reduction":
            max_reduction,
        "min_reduction":
            min_reduction,
        "min_work_roll_diameter":
            min_work_roll_diameter,
        "max_work_roll_diameter":
            max_work_roll_diameter,
        "min_backup_roll_diameter":
            min_backup_roll_diameter,
        "max_backup_roll_diameter":
            max_backup_roll_diameter,
        "required_cooling_capacity":
            required_cooling_capacity,
        "available_coolant_pressure":
            available_coolant_pressure,
        "coolant_temperature":
            coolant_temperature,
        "coolant_medium":
            str(coolant_medium).strip(),
        "spraybar_arrangement":
            spraybar_arrangement,
        "row_configuration":
            row_configuration,
        "spraybar_material":
            spraybar_material,
        "product_variant":
            product_variant,
        "mk3_configuration":
            mk3_configuration,
        "nozzle_pitch":
            nozzle_pitch,
        "nozzles_per_valve_top":
            nozzles_per_valve_top,
        "nozzles_per_valve_bottom":
            nozzles_per_valve_bottom,
        "top_backup_nozzle":
            top_backup_nozzle,
        "bite_lube_pitch":
            bite_lube_pitch,
        "bite_lube_nozzles":
            bite_lube_nozzles,
        "bite_lube_remote_valve":
            bite_lube_remote_valve,
        "connection_to_bar":
            str(connection_to_bar).strip(),
        "hose_thread_size":
            hose_thread_size.strip(),
        "hose_cone":
            hose_cone.strip(),
        "coolant_block_angle":
            coolant_block_angle,
        "number_coolant_connections":
            number_coolant_connections,
        "number_air_connections":
            number_air_connections,
        "air_intensifier_supplied":
            air_intensifier_supplied,
        "air_control_panel_supplied":
            air_control_panel_supplied,
        "signal_cable_length":
            signal_cable_length,
        "signal_cable_quantity":
            signal_cable_quantity,
        "cable_entry_angle":
            cable_entry_angle,
        "junction_box_quantity":
            junction_box_quantity,
        "junction_box_type":
            junction_box_type,
    }

    generated_requirements = (
        build_project_data_requirements(
            project_data
        )
    )

    # --------------------------------------------------------
    # 8. REVIEW GENERATED REQUIREMENTS
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "8",
            "Review Generated Requirements",
        )

        st.caption(
            (
                "These requirements will form the locked "
                f"Revision {next_revision_number} baseline "
                "when committed."
            )
        )

        review_filter = st.selectbox(
            "Show requirement area",
            [
                "All areas",
                *sorted(
                    generated_requirements[
                        "Requirement Area"
                    ]
                    .unique()
                    .tolist()
                ),
            ],
            key=f"review_filter_{selected_project}",
        )

        if review_filter == "All areas":
            review_dataframe = (
                generated_requirements.copy()
            )
        else:
            review_dataframe = (
                generated_requirements[
                    generated_requirements[
                        "Requirement Area"
                    ]
                    == review_filter
                ]
            )

        st.dataframe(
            review_dataframe[
                [
                    "Question ID",
                    "Requirement Area",
                    "Requirement",
                    "Required Value",
                    "Unit / Limit",
                    "V&V Point",
                    "V&V Method",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation_errors = []

    required_text_fields = {
        "Customer name":
            customer_name,
        "Country":
            country,
        "Lead Engineer":
            lead_engineer,
        "Project Manager":
            project_manager,
        "Alloy range":
            alloy_range,
        "Mill type":
            mill_type,
        "Mill supplier":
            mill_supplier,
        "Coolant medium":
            coolant_medium,
        "Connection to bar":
            connection_to_bar,
        "Hose thread size":
            hose_thread_size,
        "Hose cone":
            hose_cone,
    }

    for field_name, field_value in (
        required_text_fields.items()
    ):
        if not str(field_value).strip():
            validation_errors.append(
                f"{field_name} is required."
            )

    # Logical range validation

    if (
        max_entry_thickness
        < min_entry_thickness
    ):
        validation_errors.append(
            (
                "Maximum entry thickness cannot be "
                "less than minimum entry thickness."
            )
        )

    if (
        max_exit_thickness
        < min_exit_thickness
    ):
        validation_errors.append(
            (
                "Maximum exit thickness cannot be "
                "less than minimum exit thickness."
            )
        )

    if (
        max_strip_width
        < min_strip_width
    ):
        validation_errors.append(
            (
                "Maximum strip width cannot be "
                "less than minimum strip width."
            )
        )

    if (
        max_strip_stress
        < min_strip_stress
    ):
        validation_errors.append(
            (
                "Maximum strip stress cannot be "
                "less than minimum strip stress."
            )
        )

    if (
        max_reduction
        < min_reduction
    ):
        validation_errors.append(
            (
                "Maximum reduction cannot be "
                "less than minimum reduction."
            )
        )

    if (
        max_work_roll_diameter
        < min_work_roll_diameter
    ):
        validation_errors.append(
            (
                "Maximum work roll diameter cannot be "
                "less than minimum work roll diameter."
            )
        )

    if (
        max_backup_roll_diameter
        < min_backup_roll_diameter
    ):
        validation_errors.append(
            (
                "Maximum backup roll diameter cannot be "
                "less than minimum backup roll diameter."
            )
        )

    # --------------------------------------------------------
    # 9. COMMIT REVISION
    # --------------------------------------------------------

    commit_left, commit_right = (
        st.columns([1.4, 1])
    )

    with commit_left:

        with st.container(border=True):

            render_section_heading(
                "9",
                "Commit Locked Revision",
            )

            committed_by = st.text_input(
                "Committed by *",
                value=lead_engineer,
                key=f"commit_by_{selected_project}",
            )

            revision_comment = st.text_area(
                "Revision comment",
                placeholder=(
                    "Example: Initial project baseline "
                    "or updated cooling system data."
                ),
                key=f"revision_comment_{selected_project}",
            )

            if validation_errors:

                st.warning(
                    (
                        "The Project Data currently contains "
                        f"{len(validation_errors)} validation issue(s)."
                    )
                )

                with st.expander(
                    "Show validation issues"
                ):
                    for error in validation_errors:
                        st.write(
                            f"• {error}"
                        )

            commit_button = st.button(
                (
                    f"🔒 Commit Locked Revision "
                    f"{next_revision_number}"
                ),
                type="primary",
                use_container_width=True,
            )

            if commit_button:

                if validation_errors:

                    st.error(
                        (
                            "Resolve the validation issues "
                            "before committing this revision."
                        )
                    )

                elif not committed_by.strip():

                    st.error(
                        "Committed by is required."
                    )

                else:

                    try:

                        commit_project_data_revision(
                            project_name=
                                selected_project,
                            revision_number=
                                next_revision_number,
                            committed_by=
                                committed_by.strip(),
                            revision_comment=
                                revision_comment.strip(),
                            requirements_dataframe=
                                generated_requirements,
                        )

                        st.success(
                            (
                                f"Revision "
                                f"{next_revision_number} "
                                "has been committed and locked."
                            )
                        )

                        st.rerun()

                    except sqlite3.IntegrityError:

                        st.error(
                            (
                                "This revision number already exists. "
                                "Refresh the page and try again."
                            )
                        )

    with commit_right:

        with st.container(border=True):

            st.subheader(
                "Revision History"
            )

            revision_history = (
                build_revision_history_summary(
                    selected_project
                )
            )

            if revision_history.empty:

                st.info(
                    (
                        "No revisions have been "
                        "committed for this project."
                    )
                )

            else:

                st.dataframe(
                    revision_history[
                        [
                            "Revision",
                            "Changed Question IDs",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

                with st.expander(
                    "Show revision details"
                ):

                    st.dataframe(
                        revision_history,
                        use_container_width=True,
                        hide_index=True,
                    )


# ============================================================
# PAGE 2 — PROJECT-SPECIFIC REQUIREMENTS
# ============================================================

elif (
    selected_page
    == "2. Project-Specific Requirements"
):

    render_page_heading(
        "◇",
        "Project-Specific Requirements",
        (
            "Capture additional customer and stakeholder "
            "requirements using simple guided templates."
        ),
    )

    # --------------------------------------------------------
    # 1. REQUIREMENT DETAILS
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "1",
            "Requirement Details",
        )

        detail_col1, detail_col2 = (
            st.columns(2)
        )

        with detail_col1:

            requirement_project = st.selectbox(
                "Project *",
                ALLOWED_PROJECTS,
                key="specific_project",
            )

            source_department = st.selectbox(
                "Source / department *",
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
                key="specific_source",
            )

        with detail_col2:

            requirement_title = st.text_input(
                "Requirement title *",
                placeholder=(
                    "Enter a short descriptive title"
                ),
                key="specific_title",
            )

            submitted_by = st.text_input(
                "Submitted by *",
                placeholder="Enter your name",
                key="specific_submitter",
            )

    # --------------------------------------------------------
    # 2. CHOOSE TEMPLATE
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "2",
            "Choose a Requirement Template",
        )

        template_name = st.selectbox(
            "What kind of requirement do you want to add? *",
            list(
                PROJECT_REQUIREMENT_TEMPLATES.keys()
            ),
            key="specific_template",
        )

        template_details = (
            PROJECT_REQUIREMENT_TEMPLATES[
                template_name
            ]
        )

        render_info_strip(
            template_details["help"]
        )

    # --------------------------------------------------------
    # 3. GUIDED INPUTS
    # --------------------------------------------------------

    input_column, preview_column = (
        st.columns([1.5, 1])
    )

    generated_requirement = ""
    stakeholder_input = ""
    requirement_complete = False

    with input_column:

        with st.container(border=True):

            render_section_heading(
                "3",
                "Fill In the Requirement",
            )

            if template_name == "Operating condition":

                equipment = st.text_input(
                    "What equipment or system? *",
                    value="ISV system",
                    key="specific_operating_equipment",
                )

                action = st.text_input(
                    "What must it do? *",
                    placeholder=(
                        "Example: operate continuously"
                    ),
                    key="specific_operating_action",
                )

                condition = st.text_area(
                    "Under what condition? *",
                    placeholder=(
                        "Example: at ambient temperatures "
                        "between 5°C and 45°C"
                    ),
                    key="specific_operating_condition",
                )

                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall "
                    f"{action.strip() or '[required action]'} "
                    f"{condition.strip() or '[condition]'}."
                )

                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Action: {action}\n"
                    f"Condition: {condition}"
                )

                requirement_complete = all(
                    [
                        equipment.strip(),
                        action.strip(),
                        condition.strip(),
                    ]
                )

            elif template_name == "Capacity or quantity":

                equipment = st.text_input(
                    "What equipment or system? *",
                    value="ISV system",
                    key="specific_capacity_equipment",
                )

                action = st.text_input(
                    "What must it provide or control? *",
                    placeholder=(
                        "Example: independently control"
                    ),
                    key="specific_capacity_action",
                )

                quantity = st.number_input(
                    "Minimum quantity *",
                    min_value=0,
                    step=1,
                    key="specific_capacity_quantity",
                )

                item = st.text_input(
                    "What is being counted? *",
                    placeholder=(
                        "Example: spray zones"
                    ),
                    key="specific_capacity_item",
                )

                quantity_text = (
                    str(quantity)
                    if quantity > 0
                    else "[quantity]"
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

                requirement_complete = all(
                    [
                        equipment.strip(),
                        action.strip(),
                        quantity > 0,
                        item.strip(),
                    ]
                )

            elif template_name == "Performance level":

                equipment = st.text_input(
                    "What equipment or system? *",
                    value="ISV system",
                    key="specific_performance_equipment",
                )

                action = st.text_input(
                    "What performance is required? *",
                    placeholder=(
                        "Example: deliver cooling fluid"
                    ),
                    key="specific_performance_action",
                )

                value = st.number_input(
                    "Required value *",
                    min_value=0.0,
                    step=1.0,
                    key="specific_performance_value",
                )

                unit = st.text_input(
                    "Unit *",
                    placeholder=(
                        "Example: L/min"
                    ),
                    key="specific_performance_unit",
                )

                value_text = (
                    format_number(value)
                    if value > 0
                    else "[value]"
                )

                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall "
                    f"{action.strip() or '[required action]'} "
                    f"at a minimum value of "
                    f"{value_text} "
                    f"{unit.strip() or '[unit]'}."
                )

                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Action: {action}\n"
                    f"Value: {value}\n"
                    f"Unit: {unit}"
                )

                requirement_complete = all(
                    [
                        equipment.strip(),
                        action.strip(),
                        value > 0,
                        unit.strip(),
                    ]
                )

            elif template_name == "Response time":

                equipment = st.text_input(
                    "What equipment or system? *",
                    value="ISV system",
                    key="specific_response_equipment",
                )

                action = st.text_input(
                    "What must happen? *",
                    placeholder=(
                        "Example: begin coolant delivery"
                    ),
                    key="specific_response_action",
                )

                trigger = st.text_input(
                    "What triggers the action? *",
                    placeholder=(
                        "Example: receiving a control signal"
                    ),
                    key="specific_response_trigger",
                )

                response_time = st.number_input(
                    "Maximum time *",
                    min_value=0.0,
                    step=0.1,
                    key="specific_response_time",
                )

                time_unit = st.selectbox(
                    "Time unit *",
                    [
                        "milliseconds",
                        "seconds",
                        "minutes",
                    ],
                    key="specific_response_unit",
                )

                time_text = (
                    format_number(
                        response_time
                    )
                    if response_time > 0
                    else "[time]"
                )

                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall "
                    f"{action.strip() or '[required action]'} "
                    f"within "
                    f"{time_text} "
                    f"{time_unit} of "
                    f"{trigger.strip() or '[trigger]'}."
                )

                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Action: {action}\n"
                    f"Trigger: {trigger}\n"
                    f"Time: {response_time} {time_unit}"
                )

                requirement_complete = all(
                    [
                        equipment.strip(),
                        action.strip(),
                        trigger.strip(),
                        response_time > 0,
                    ]
                )

            elif template_name == "Compatibility or interface":

                equipment = st.text_input(
                    "What ISV equipment or system? *",
                    value="ISV system",
                    key="specific_interface_equipment",
                )

                interface_item = st.text_input(
                    "What must it connect to or work with? *",
                    placeholder=(
                        "Example: customer's PLC"
                    ),
                    key="specific_interface_item",
                )

                interface_requirement = st.text_area(
                    "Describe the required connection or compatibility *",
                    placeholder=(
                        "Example: exchange operating status "
                        "and alarm signals"
                    ),
                    key="specific_interface_requirement",
                )

                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall interface with "
                    f"{interface_item.strip() or '[external system]'} "
                    f"to "
                    f"{interface_requirement.strip() or '[required interface behaviour]'}."
                )

                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Interface: {interface_item}\n"
                    f"Requirement: {interface_requirement}"
                )

                requirement_complete = all(
                    [
                        equipment.strip(),
                        interface_item.strip(),
                        interface_requirement.strip(),
                    ]
                )

            elif template_name == "Product type or standard":

                equipment = st.text_input(
                    "What equipment or item? *",
                    value="ISV system",
                    key="specific_product_equipment",
                )

                specification = st.text_input(
                    "Required product, material or standard *",
                    placeholder=(
                        "Example: stainless steel construction"
                    ),
                    key="specific_product_specification",
                )

                reason = st.text_area(
                    "Where or why is this required? *",
                    placeholder=(
                        "Example: for all wetted components"
                    ),
                    key="specific_product_reason",
                )

                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall use "
                    f"{specification.strip() or '[required specification]'} "
                    f"{reason.strip() or '[application]'}."
                )

                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Specification: {specification}\n"
                    f"Application: {reason}"
                )

                requirement_complete = all(
                    [
                        equipment.strip(),
                        specification.strip(),
                        reason.strip(),
                    ]
                )

            elif template_name == "Reliability or maintenance":

                equipment = st.text_input(
                    "What equipment or component? *",
                    value="ISV system",
                    key="specific_maintenance_equipment",
                )

                maintenance_need = st.text_area(
                    "What must be possible? *",
                    placeholder=(
                        "Example: valves must be replaceable "
                        "without removing the complete spraybar"
                    ),
                    key="specific_maintenance_need",
                )

                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall be designed such that "
                    f"{maintenance_need.strip() or '[maintenance requirement]'}."
                )

                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Requirement: {maintenance_need}"
                )

                requirement_complete = all(
                    [
                        equipment.strip(),
                        maintenance_need.strip(),
                    ]
                )

            else:

                free_requirement = st.text_area(
                    "Describe the requirement *",
                    placeholder=(
                        "Describe what the project needs "
                        "in clear, simple language."
                    ),
                    height=180,
                    key="specific_other_requirement",
                )

                generated_requirement = (
                    free_requirement.strip()
                    or "[Describe the requirement]"
                )

                stakeholder_input = (
                    free_requirement.strip()
                )

                requirement_complete = bool(
                    free_requirement.strip()
                )

    # --------------------------------------------------------
    # 4. LIVE PREVIEW
    # --------------------------------------------------------

    with preview_column:

        with st.container(border=True):

            render_section_heading(
                "4",
                "Live Requirement Preview",
            )

            preview_text = (
                f"Project: {requirement_project}\n\n"
                f"Title: "
                f"{requirement_title or '[Requirement title]'}"
                f"\n\n"
                f"Template: {template_name}\n\n"
                f"Requirement:\n"
                f"{generated_requirement}"
            )

            st.markdown(
                f"""
                <div class="preview-panel">
                {escape(preview_text)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # 5. V&V
    # --------------------------------------------------------

    with st.container(border=True):

        render_section_heading(
            "5",
            "Verification and Validation",
        )

        vv_col1, vv_col2 = (
            st.columns(2)
        )

        with vv_col1:

            verification_point = st.selectbox(
                "V&V point *",
                VERIFICATION_POINTS,
                key="specific_vv_point",
            )

            st.caption(
                (
                    "The project stage where the "
                    "requirement will be checked."
                )
            )

        with vv_col2:

            verification_method = st.selectbox(
                "V&V method *",
                VERIFICATION_METHODS,
                key="specific_vv_method",
            )

            st.caption(
                (
                    "How engineering will demonstrate "
                    "that the requirement has been met."
                )
            )

    submit_requirement = st.button(
        "Submit Project-Specific Requirement",
        type="primary",
        use_container_width=True,
    )

    if submit_requirement:

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
                (
                    "Please complete: "
                    + ", ".join(errors)
                )
            )

        else:

            save_project_requirement(
                project_name=
                    requirement_project,
                requirement_title=
                    requirement_title.strip(),
                requirement_text=
                    generated_requirement,
                category=
                    template_details[
                        "category"
                    ],
                source_department=
                    source_department,
                submitted_by=
                    submitted_by.strip(),
                boilerplate_name=
                    template_name,
                stakeholder_input=
                    stakeholder_input,
                verification_point=
                    verification_point,
                verification_method=
                    verification_method,
            )

            st.success(
                (
                    "Requirement submitted successfully "
                    "and set to Pending."
                )
            )

            st.rerun()

    # --------------------------------------------------------
    # EXISTING PROJECT REQUIREMENTS
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Project-Specific Requirements"
        )

        project_requirements = (
            load_project_requirements(
                requirement_project
            )
        )

        if project_requirements.empty:

            st.info(
                (
                    "No project-specific requirements "
                    "have been submitted for this project."
                )
            )

        else:

            display_requirements = (
                project_requirements.rename(
                    columns={
                        "id": "ID",
                        "requirement_title": "Title",
                        "requirement_text": "Requirement",
                        "boilerplate_name": "Template",
                        "verification_point": "V&V Point",
                        "verification_method": "V&V Method",
                        "status": "Status",
                    }
                )
            )

            st.dataframe(
                display_requirements[
                    [
                        "ID",
                        "Title",
                        "Requirement",
                        "Template",
                        "V&V Point",
                        "V&V Method",
                        "Status",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# PAGE 3 — ENGINEERING DASHBOARD
# ============================================================

else:

    render_page_heading(
        "⌁",
        "Engineering Dashboard",
        (
            "Review the complete project requirement set, "
            "track compliance and view V&V progress."
        ),
    )

    dashboard_project_col, dashboard_revision_col = (
        st.columns([3, 1])
    )

    with dashboard_project_col:

        dashboard_project = st.selectbox(
            "Project",
            ALLOWED_PROJECTS,
            key="dashboard_project",
        )

    dashboard_latest_revision = (
        get_latest_revision_number(
            dashboard_project
        )
    )

    with dashboard_revision_col:

        render_metric_card(
            "Project Data Revision",
            dashboard_latest_revision,
            "metric-orange",
        )

    latest_revision_id = (
        get_latest_revision_id(
            dashboard_project
        )
    )

    if latest_revision_id is None:

        standard_items = pd.DataFrame()

    else:

        standard_items = load_revision_items(
            latest_revision_id
        )

    project_specific_items = (
        load_project_requirements(
            dashboard_project
        )
    )

    combined_rows = []

    # Latest Project Data requirements

    for _, row in standard_items.iterrows():

        reference = safe_text(
            row["requirement_id"]
        )

        complete, comment = (
            get_requirement_completion(
                dashboard_project,
                "Project Data",
                reference,
            )
        )

        value_text = safe_text(
            row["required_value"]
        )

        unit_text = safe_text(
            row["unit_or_limit"]
        )

        if unit_text:
            value_display = (
                f"{value_text} {unit_text}"
            )
        else:
            value_display = value_text

        combined_rows.append(
            {
                "Source":
                    "Project Data",
                "Reference":
                    reference,
                "Requirement":
                    safe_text(
                        row[
                            "requirement_text"
                        ]
                    ),
                "Required Value":
                    value_display,
                "V&V Point":
                    safe_text(
                        row[
                            "verification_point"
                        ]
                    ),
                "V&V Method":
                    safe_text(
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

    # Project-specific requirements

    for _, row in (
        project_specific_items.iterrows()
    ):

        reference = (
            f"REQ-{int(row['id']):04d}"
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
                    safe_text(
                        row[
                            "requirement_text"
                        ]
                    ),
                "Required Value":
                    "",
                "V&V Point":
                    safe_text(
                        row[
                            "verification_point"
                        ]
                    ),
                "V&V Method":
                    safe_text(
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

    combined_requirements = pd.DataFrame(
        combined_rows
    )

    total_requirements = len(
        combined_requirements
    )

    if total_requirements > 0:

        completed_requirements = int(
            combined_requirements[
                "Complete"
            ].sum()
        )

    else:

        completed_requirements = 0

    open_requirements = (
        total_requirements
        - completed_requirements
    )

    completion_percentage = (
        int(
            round(
                completed_requirements
                / total_requirements
                * 100
            )
        )
        if total_requirements > 0
        else 0
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:

        render_metric_card(
            "Total Requirements",
            total_requirements,
            "metric-blue",
        )

    with metric_col2:

        render_metric_card(
            "Requirements Met",
            completed_requirements,
            "metric-green",
        )

    with metric_col3:

        render_metric_card(
            "Requirements Open",
            open_requirements,
            "metric-amber",
        )

    with metric_col4:

        render_metric_card(
            "Overall Completion",
            f"{completion_percentage}%",
            "metric-orange",
        )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Requirement Filters"
        )

        filter_col1, filter_col2, filter_col3 = (
            st.columns(3)
        )

        with filter_col1:

            source_filter = st.selectbox(
                "Requirement source",
                [
                    "All requirements",
                    "Project Data",
                    "Project specific",
                ],
            )

        if combined_requirements.empty:

            available_vv_points = []

        else:

            available_vv_points = sorted(
                [
                    point
                    for point in
                    combined_requirements[
                        "V&V Point"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                    if point.strip()
                ]
            )

        with filter_col2:

            vv_filter = st.selectbox(
                "V&V point",
                [
                    "All V&V points",
                    *available_vv_points,
                ],
            )

        with filter_col3:

            completion_filter = st.selectbox(
                "Completion",
                [
                    "All",
                    "Open only",
                    "Complete only",
                ],
            )

    filtered_requirements = (
        combined_requirements.copy()
    )

    if not filtered_requirements.empty:

        if (
            source_filter
            != "All requirements"
        ):

            filtered_requirements = (
                filtered_requirements[
                    filtered_requirements[
                        "Source"
                    ]
                    == source_filter
                ]
            )

        if vv_filter != "All V&V points":

            filtered_requirements = (
                filtered_requirements[
                    filtered_requirements[
                        "V&V Point"
                    ]
                    == vv_filter
                ]
            )

        if completion_filter == "Open only":

            filtered_requirements = (
                filtered_requirements[
                    ~filtered_requirements[
                        "Complete"
                    ]
                ]
            )

        elif (
            completion_filter
            == "Complete only"
        ):

            filtered_requirements = (
                filtered_requirements[
                    filtered_requirements[
                        "Complete"
                    ]
                ]
            )

    # --------------------------------------------------------
    # REQUIREMENT CHECKLIST
    # --------------------------------------------------------

    checklist_col, vv_col = (
        st.columns([1.7, 1])
    )

    with checklist_col:

        with st.container(border=True):

            st.subheader(
                "Requirements Checklist"
            )

            if filtered_requirements.empty:

                st.info(
                    (
                        "No requirements match "
                        "the selected filters."
                    )
                )

            else:

                for _, row in (
                    filtered_requirements
                    .reset_index(drop=True)
                    .iterrows()
                ):

                    reference = row["Reference"]
                    source = row["Source"]

                    key_prefix = (
                        f"{dashboard_project}_"
                        f"{source}_"
                        f"{reference}"
                    )

                    expander_title = (
                        f"{reference} — "
                        f"{row['Requirement']}"
                    )

                    with st.expander(
                        expander_title,
                        expanded=False,
                    ):

                        if (
                            row[
                                "Required Value"
                            ]
                        ):

                            st.markdown(
                                (
                                    "**Required value:** "
                                    f"{row['Required Value']}"
                                )
                            )

                        details_col1, details_col2 = (
                            st.columns(2)
                        )

                        with details_col1:

                            st.caption(
                                (
                                    "V&V Point: "
                                    f"{row['V&V Point']}"
                                )
                            )

                        with details_col2:

                            st.caption(
                                (
                                    "V&V Method: "
                                    f"{row['V&V Method']}"
                                )
                            )

                        complete_value = (
                            st.checkbox(
                                "Requirement met",
                                value=bool(
                                    row[
                                        "Complete"
                                    ]
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
                                value=safe_text(
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
                                project_name=
                                    dashboard_project,
                                source=
                                    source,
                                reference=
                                    reference,
                                is_complete=
                                    complete_value,
                                evidence_comment=
                                    comment_value,
                            )

                            st.success(
                                (
                                    f"{reference} "
                                    "has been updated."
                                )
                            )

                            st.rerun()

    # --------------------------------------------------------
    # V&V PROGRESS
    # --------------------------------------------------------

    with vv_col:

        with st.container(border=True):

            st.subheader(
                "V&V Progress"
            )

            if combined_requirements.empty:

                st.info(
                    "No V&V data is available."
                )

            else:

                grouped = (
                    combined_requirements
                    .groupby("V&V Point")
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
                    - grouped["Met"]
                )

                grouped["Completion"] = (
                    (
                        grouped["Met"]
                        /
                        grouped[
                            "Requirements"
                        ]
                        * 100
                    )
                    .round()
                    .astype(int)
                )

                for _, row in grouped.iterrows():

                    point_name = (
                        row["V&V Point"]
                        or "Unassigned"
                    )

                    st.markdown(
                        (
                            f"**{point_name}** "
                            f"— "
                            f"{int(row['Completion'])}%"
                        )
                    )

                    st.progress(
                        int(
                            row["Completion"]
                        )
                        / 100
                    )

                    st.caption(
                        (
                            f"{int(row['Met'])} met · "
                            f"{int(row['Open'])} open"
                        )
                    )

    # --------------------------------------------------------
    # ENGINEERING DELIVERABLES / OVERALL
    # --------------------------------------------------------

    deliverables_col, overall_col = (
        st.columns([1.3, 1])
    )

    with deliverables_col:

        with st.container(border=True):

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

                updated_value = st.checkbox(
                    deliverable,
                    value=stored_value,
                    key=(
                        f"deliverable_"
                        f"{dashboard_project}_"
                        f"{deliverable}"
                    ),
                )

                if updated_value:
                    completed_deliverables += 1

                if updated_value != stored_value:

                    save_deliverable_status(
                        project_name=
                            dashboard_project,
                        deliverable_name=
                            deliverable,
                        is_complete=
                            updated_value,
                    )

            deliverable_percentage = int(
                round(
                    completed_deliverables
                    /
                    len(
                        ENGINEERING_DELIVERABLES
                    )
                    * 100
                )
            )

            st.progress(
                deliverable_percentage / 100
            )

            st.caption(
                (
                    f"{completed_deliverables} of "
                    f"{len(ENGINEERING_DELIVERABLES)} "
                    "engineering deliverables complete"
                )
            )

    with overall_col:

        with st.container(border=True):

            st.subheader(
                "Requirement Completion"
            )

            st.markdown(
                f"""
                <div style="
                    min-height:290px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    flex-direction:column;
                ">
                    <div style="
                        width:190px;
                        height:190px;
                        border-radius:50%;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        flex-direction:column;
                        background:
                            radial-gradient(
                                circle,
                                #0b1526 55%,
                                transparent 57%
                            ),
                            conic-gradient(
                                #ff9a35 0% {completion_percentage}%,
                                #1c2a3d {completion_percentage}% 100%
                            );
                        box-shadow:
                            0 0 34px
                            rgba(255,154,67,0.18);
                    ">
                        <div style="
                            color:white;
                            font-size:2.7rem;
                            font-weight:800;
                        ">
                            {completion_percentage}%
                        </div>
                        <div style="
                            color:#c9b18c;
                        ">
                            Complete
                        </div>
                    </div>

                    <div style="
                        margin-top:1.2rem;
                        color:#9eacc7;
                    ">
                        {completed_requirements} met
                        &nbsp;·&nbsp;
                        {open_requirements} open
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            ) 