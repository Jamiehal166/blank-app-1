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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --background-primary: #050b18;
    --background-secondary: #071329;
    --background-card: rgba(12, 27, 58, 0.92);
    --background-card-soft: rgba(15, 31, 66, 0.84);
    --border-soft: rgba(103, 139, 207, 0.30);
    --text-primary: #f5f7ff;
    --text-secondary: #aab7d1;
    --purple: #8b4cff;
    --cyan: #18d9ff;
    --blue: #3185ff;
    --green: #35e49f;
    --orange: #ff9f35;
}


/* ==========================================================
   GLOBAL
========================================================== */

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
            rgba(0, 196, 255, 0.12),
            transparent 26%
        ),
        radial-gradient(
            circle at 10% 8%,
            rgba(133, 68, 255, 0.16),
            transparent 23%
        ),
        linear-gradient(
            145deg,
            #050914 0%,
            #061126 48%,
            #06172b 100%
        );

    color:
        var(--text-primary);
}


.block-container {
    max-width:
        1550px;

    padding-top:
        1.4rem;

    padding-left:
        1.8rem;

    padding-right:
        1.8rem;

    padding-bottom:
        4rem;
}


#MainMenu {
    visibility:
        hidden;
}


footer {
    visibility:
        hidden;
}


header {
    background:
        transparent !important;
}


/* ==========================================================
   SIDEBAR
========================================================== */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(9, 24, 55, 0.99),
            rgba(6, 17, 39, 0.99)
        );

    border-right:
        1px solid
        rgba(99, 132, 195, 0.24);

    box-shadow:
        18px 0 45px
        rgba(0, 0, 0, 0.28);
}


section[data-testid="stSidebar"] > div {
    padding-top:
        1rem;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] > label {
    display:
        none;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label {
    border:
        1px solid transparent;

    border-radius:
        14px;

    padding:
        0.75rem 0.8rem;

    margin:
        0.18rem 0;

    transition:
        all 0.2s ease;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label:hover {
    background:
        rgba(77, 107, 228, 0.14);

    border-color:
        rgba(85, 123, 227, 0.26);
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"]
label:has(input:checked) {
    background:
        linear-gradient(
            135deg,
            rgba(129, 67, 255, 0.77),
            rgba(31, 108, 255, 0.55)
        );

    border-color:
        rgba(151, 96, 255, 0.68);

    box-shadow:
        0 0 25px
        rgba(120, 69, 255, 0.22);
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] p {
    color:
        #dfe7fa;

    font-weight:
        620;
}


.sidebar-brand {
    display:
        flex;

    align-items:
        center;

    gap:
        0.85rem;

    margin:
        0.15rem 0 2rem 0;
}


.sidebar-logo {
    width:
        46px;

    height:
        46px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        13px;

    background:
        linear-gradient(
            145deg,
            #9c43ff,
            #315dff,
            #08dcff
        );

    color:
        white;

    font-size:
        1.55rem;

    box-shadow:
        0 0 25px
        rgba(82, 92, 255, 0.42);
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


.sidebar-brand-subtitle {
    color:
        #abb7d0;

    font-size:
        0.84rem;

    line-height:
        1.2;

    margin-top:
        0.3rem;
}


.sidebar-footer {
    margin-top:
        3rem;

    padding-top:
        1rem;

    border-top:
        1px solid
        rgba(99, 130, 190, 0.20);

    color:
        #aeb9d0;

    font-size:
        0.84rem;
}


/* ==========================================================
   PAGE HEADERS
========================================================== */

.page-header {
    display:
        flex;

    align-items:
        center;

    gap:
        0.9rem;

    margin-bottom:
        1.3rem;
}


.page-header-icon {
    width:
        49px;

    height:
        49px;

    border-radius:
        14px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    color:
        white;

    font-size:
        1.5rem;

    background:
        linear-gradient(
            145deg,
            #8e47ff,
            #345fff,
            #12d7ee
        );

    box-shadow:
        0 0 28px
        rgba(93, 85, 255, 0.39);
}


.page-header-title {
    color:
        white;

    font-size:
        2.05rem;

    font-weight:
        790;

    line-height:
        1.05;

    letter-spacing:
        -0.035em;
}


.page-header-subtitle {
    color:
        #9dabca;

    font-size:
        0.95rem;

    margin-top:
        0.35rem;
}


/* ==========================================================
   NATIVE STREAMLIT CONTAINERS
========================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        linear-gradient(
            145deg,
            rgba(15, 31, 66, 0.93),
            rgba(7, 20, 44, 0.90)
        ) !important;

    border:
        1px solid
        rgba(101, 138, 207, 0.29) !important;

    border-radius:
        16px !important;

    box-shadow:
        0 16px 34px
        rgba(0, 0, 0, 0.19);

    overflow:
        hidden;
}


div[data-testid="stVerticalBlockBorderWrapper"]
> div {
    padding:
        0.25rem;
}


/* ==========================================================
   SECTION HEADERS
========================================================== */

.section-heading {
    display:
        flex;

    align-items:
        center;

    gap:
        0.65rem;

    margin-bottom:
        0.75rem;
}


.section-number {
    width:
        29px;

    height:
        29px;

    display:
        inline-flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        8px;

    color:
        white;

    font-weight:
        800;

    background:
        linear-gradient(
            145deg,
            #974cff,
            #5355ff
        );

    box-shadow:
        0 0 15px
        rgba(125, 69, 255, 0.34);
}


.section-title {
    color:
        white;

    font-size:
        1.06rem;

    font-weight:
        720;
}


/* ==========================================================
   FORM CONTROLS
========================================================== */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background:
        rgba(6, 17, 39, 0.80) !important;

    border:
        1px solid
        rgba(106, 139, 201, 0.39) !important;

    border-radius:
        11px !important;
}


div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color:
        rgba(40, 216, 255, 0.83) !important;

    box-shadow:
        0 0 0 2px
        rgba(35, 196, 255, 0.09),
        0 0 18px
        rgba(30, 199, 255, 0.10);
}


input,
textarea {
    color:
        white !important;
}


input::placeholder,
textarea::placeholder {
    color:
        #71809e !important;
}


div[data-baseweb="select"] span {
    color:
        #edf3ff !important;
}


label {
    color:
        #d9e2f5 !important;

    font-weight:
        590 !important;
}


/* ==========================================================
   BUTTONS
========================================================== */

.stButton > button {
    width:
        100%;

    min-height:
        3rem;

    border:
        1px solid
        rgba(114, 95, 255, 0.68);

    border-radius:
        12px;

    background:
        linear-gradient(
            105deg,
            #7934f5 0%,
            #6b54ff 39%,
            #159ff9 74%,
            #09d5dc 100%
        );

    color:
        white;

    font-weight:
        750;

    box-shadow:
        0 0 22px
        rgba(103, 64, 255, 0.25),
        0 0 18px
        rgba(0, 205, 255, 0.12);

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}


.stButton > button:hover {
    color:
        white;

    transform:
        translateY(-1px);

    border-color:
        rgba(79, 226, 255, 0.86);

    box-shadow:
        0 0 30px
        rgba(111, 70, 255, 0.34),
        0 0 24px
        rgba(0, 216, 255, 0.20);
}


/* ==========================================================
   METRIC CARDS
========================================================== */

.metric-card {
    min-height:
        132px;

    padding:
        1.15rem;

    border-radius:
        16px;

    border:
        1px solid
        rgba(105, 141, 214, 0.30);

    background:
        linear-gradient(
            145deg,
            rgba(20, 39, 80, 0.97),
            rgba(10, 24, 52, 0.92)
        );

    box-shadow:
        0 15px 34px
        rgba(0, 0, 0, 0.20);
}


.metric-label {
    color:
        #b8c4dc;

    font-size:
        0.94rem;
}


.metric-value {
    color:
        white;

    font-size:
        2.5rem;

    line-height:
        1;

    font-weight:
        790;

    margin-top:
        0.75rem;
}


.metric-purple {
    border-color:
        rgba(151, 83, 255, 0.48);

    box-shadow:
        0 0 30px
        rgba(130, 73, 255, 0.10);
}


.metric-green {
    border-color:
        rgba(54, 228, 158, 0.44);

    box-shadow:
        0 0 30px
        rgba(54, 228, 158, 0.08);
}


.metric-orange {
    border-color:
        rgba(255, 157, 49, 0.44);

    box-shadow:
        0 0 30px
        rgba(255, 157, 49, 0.08);
}


.metric-blue {
    border-color:
        rgba(46, 139, 255, 0.50);

    box-shadow:
        0 0 30px
        rgba(46, 139, 255, 0.09);
}


/* ==========================================================
   PREVIEW PANEL
========================================================== */

.preview-panel {
    min-height:
        270px;

    padding:
        1.05rem;

    border:
        1px solid
        rgba(27, 218, 255, 0.62);

    border-radius:
        13px;

    background:
        #061329;

    color:
        #8ce8ff;

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    line-height:
        1.7;

    white-space:
        pre-wrap;

    box-shadow:
        inset 0 0 20px
        rgba(0, 184, 255, 0.04),
        0 0 25px
        rgba(0, 190, 255, 0.08);
}


/* ==========================================================
   DATAFRAMES
========================================================== */

div[data-testid="stDataFrame"] {
    border:
        1px solid
        rgba(92, 128, 202, 0.28);

    border-radius:
        14px;

    overflow:
        hidden;

    background:
        rgba(7, 18, 40, 0.74);
}


/* ==========================================================
   EXPANDERS
========================================================== */

details[data-testid="stExpander"] {
    background:
        rgba(7, 19, 42, 0.73);

    border:
        1px solid
        rgba(94, 128, 194, 0.25);

    border-radius:
        13px;

    margin-bottom:
        0.65rem;
}


details[data-testid="stExpander"] summary {
    color:
        white;

    font-weight:
        650;
}


/* ==========================================================
   PROGRESS BARS
========================================================== */

div[data-testid="stProgress"] > div > div {
    background:
        linear-gradient(
            90deg,
            #7d45ff,
            #1cb8ff,
            #18dfca
        );
}


/* ==========================================================
   GENERAL TEXT
========================================================== */

h1,
h2,
h3 {
    color:
        white;
}


p,
span {
    color:
        #d7e0f2;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE HELPERS
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


# ============================================================
# DATABASE SETUP
# ============================================================

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
# PROJECT-SPECIFIC REQUIREMENT FUNCTIONS
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


# ============================================================
# STANDARD REQUIREMENT FUNCTIONS
# ============================================================

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
    latest_revision_id = get_latest_revision_id(
        project_name
    )


    if latest_revision_id is None:

        return {}


    items = load_standard_revision_items(
        latest_revision_id
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
                    row[
                        "notes"
                    ]
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
        set(
            previous_dictionary.keys()
        )
        |
        set(
            current_dictionary.keys()
        )
    )


    changed_ids = []


    for question_id in all_ids:

        if (
            previous_dictionary.get(
                question_id
            )
            !=
            current_dictionary.get(
                question_id
            )
        ):

            changed_ids.append(
                question_id
            )


    return changed_ids


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
# DASHBOARD COMPLETION FUNCTIONS
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


    return (
        bool(
            row[0]
        ),
        row[1] or "",
    )


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
# ELECTRICAL REQUIREMENT LOOKUP
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


# ============================================================
# STANDARD REQUIREMENT TABLE GENERATOR
# ============================================================

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
                    "The project shall use the "
                    "selected project reference."
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
                    "The ISV system shall use the "
                    "selected ISV product variant."
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
                    "Not applicable when a "
                    "non-MK3 variant is selected."
                ),
        },

        {
            "Question ID":
                "STD-006",

            "Requirement Area":
                "Valve Configuration",

            "Requirement":
                (
                    "The ISV spraybar shall use the "
                    "selected valve pitching configuration."
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
    html = (
        '<div class="page-header">'
        f'<div class="page-header-icon">{icon}</div>'
        '<div>'
        f'<div class="page-header-title">{title}</div>'
        f'<div class="page-header-subtitle">{subtitle}</div>'
        '</div>'
        '</div>'
    )


    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_section_heading(
    number,
    title,
):
    html = (
        '<div class="section-heading">'
        f'<div class="section-number">{number}</div>'
        f'<div class="section-title">{title}</div>'
        '</div>'
    )


    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label,
    value,
    style_class,
):
    html = (
        f'<div class="metric-card {style_class}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        '</div>'
    )


    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# INITIALISE DATABASE
# ============================================================

create_or_update_database()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    sidebar_brand_html = (
        '<div class="sidebar-brand">'
        '<div class="sidebar-logo">⬢</div>'
        '<div>'
        '<div class="sidebar-brand-name">ISV</div>'
        '<div class="sidebar-brand-subtitle">'
        'Requirements<br>Management'
        '</div>'
        '</div>'
        '</div>'
    )


    st.markdown(
        sidebar_brand_html,
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
        (
            '<div class="sidebar-footer">'
            '<strong>Engineering Team</strong>'
            '<br>'
            'Internal engineering tool'
            '</div>'
        ),
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
            1.8,
            1,
        ]
    )


    with top_left:

        with st.container(
            border=True
        ):

            render_section_heading(
                "1",
                "Requirement Details",
            )


            detail_column_1, detail_column_2 = (
                st.columns(2)
            )


            with detail_column_1:

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


            with detail_column_2:

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
                        placeholder="Enter your name",
                        key="project_submitter",
                    )
                )


    with top_right:

        with st.container(
            border=True
        ):

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
                    "matches this requirement."
                )
            )


    requirement_left, preview_right = (
        st.columns(
            [
                1.7,
                1,
            ]
        )
    )


    generated_requirement = ""

    stakeholder_input = ""

    requirement_complete = False

    internal_category = "Other"


    with requirement_left:

        with st.container(
            border=True
        ):

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
                    height=125,
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
                    placeholder="Example: spray zones",
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
                == "Performance level"
            ):

                internal_category = (
                    "Performance"
                )


                equipment = st.text_input(
                    "Equipment or system *",
                    value="ISV spraybar",
                    key="performance_equipment",
                )


                action = st.text_input(
                    "Required action *",
                    placeholder=(
                        "Example: deliver cooling fluid"
                    ),
                    key="performance_action",
                )


                required_value = st.number_input(
                    "Minimum required value *",
                    min_value=0.0,
                    step=1.0,
                    key="performance_value",
                )


                engineering_unit = st.text_input(
                    "Engineering unit *",
                    placeholder=(
                        "Example: litres per minute"
                    ),
                    key="performance_unit",
                )


                requirement_complete = all(
                    [
                        equipment.strip(),
                        action.strip(),
                        required_value > 0,
                        engineering_unit.strip(),
                    ]
                )


                value_text = (
                    f"{required_value:g}"
                    if required_value > 0
                    else
                    "[minimum value]"
                )


                generated_requirement = (
                    f"The "
                    f"{equipment.strip() or '[equipment]'} "
                    f"shall "
                    f"{action.strip() or '[required action]'} "
                    f"at a minimum value of "
                    f"{value_text} "
                    f"{engineering_unit.strip() or '[unit]'}."
                )


                stakeholder_input = (
                    f"Equipment: {equipment}\n"
                    f"Action: {action}\n"
                    f"Value: {required_value}\n"
                    f"Unit: {engineering_unit}"
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
                        "Example: receiving a control signal"
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
                        "Describe the requirement, "
                        "constraint, performance expectation, "
                        "interface, or customer need."
                    ),
                    height=210,
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


    with preview_right:

        with st.container(
            border=True
        ):

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
                (
                    '<div class="preview-panel">'
                    f'{preview_text}'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )


    with st.container(
        border=True
    ):

        render_section_heading(
            "5",
            "Verification and Validation",
        )


        verification_column_1, verification_column_2 = (
            st.columns(2)
        )


        with verification_column_1:

            verification_point = (
                st.selectbox(
                    "V&V point *",
                    VERIFICATION_POINTS,
                    key="project_vv_point",
                )
            )


            st.caption(
                (
                    "The stage where this "
                    "requirement will be checked."
                )
            )


        with verification_column_2:

            verification_method = (
                st.selectbox(
                    "V&V method *",
                    VERIFICATION_METHODS,
                    key="project_vv_method",
                )
            )


            st.caption(
                (
                    "The method used to demonstrate "
                    "that the requirement has been met."
                )
            )


    submit_button = st.button(
        "✈ Submit Requirement",
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
                (
                    "Please complete: "
                    +
                    ", ".join(
                        errors
                    )
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


    with st.container(
        border=True
    ):

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


    project_column, revision_column = (
        st.columns(
            [
                3,
                1,
            ]
        )
    )


    with project_column:

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


    with revision_column:

        render_metric_card(
            "Next Revision",
            next_revision,
            "metric-purple",
        )


    latest_values = (
        load_latest_standard_values(
            standard_project
        )
    )


    history_column, information_column = (
        st.columns(
            [
                1.45,
                1,
            ]
        )
    )


    with history_column:

        with st.container(
            border=True
        ):

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


    with information_column:

        with st.container(
            border=True
        ):

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


    valve_column, pitching_column = (
        st.columns(
            [
                0.85,
                1.75,
            ]
        )
    )


    with valve_column:

        with st.container(
            border=True
        ):

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


    with pitching_column:

        with st.container(
            border=True
        ):

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

                uniform_column_1, uniform_column_2 = (
                    st.columns(2)
                )


                with uniform_column_1:

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


                with uniform_column_2:

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

                hybrid_column_1, hybrid_column_2 = (
                    st.columns(2)
                )


                with hybrid_column_1:

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


                with hybrid_column_2:

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


    with st.container(
        border=True
    ):

        st.subheader(
            "Operating Fluid"
        )


        saved_fluid = get_text_value(
            latest_values,
            "STD-013",
            "Water",
        )


        fluid_selection = st.selectbox(
            "Operating fluid *",
            OPERATING_FLUIDS,
            index=selectbox_index(
                OPERATING_FLUIDS,
                (
                    saved_fluid
                    if saved_fluid
                    in OPERATING_FLUIDS
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
                    not in OPERATING_FLUIDS
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


    review_column, commit_column = (
        st.columns(
            [
                1.7,
                0.8,
            ]
        )
    )


    with review_column:

        with st.container(
            border=True
        ):

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


    with commit_column:

        with st.container(
            border=True
        ):

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
            "Track requirement compliance, "
            "V&V completion, and engineering deliverables."
        ),
    )


    dashboard_project_column, revision_column = (
        st.columns(
            [
                3,
                1,
            ]
        )
    )


    with dashboard_project_column:

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


    with revision_column:

        render_metric_card(
            "Current Standard Revision",
            latest_revision,
            "metric-blue",
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

        reference = str(
            row[
                "requirement_id"
            ]
        )


        complete, comment = (
            get_requirement_completion(
                dashboard_project,
                "Standard",
                reference,
            )
        )


        combined_rows.append(
            {

                "Source":
                    "Standard",

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


    metric_column_1, metric_column_2, metric_column_3, metric_column_4 = (
        st.columns(4)
    )


    with metric_column_1:

        render_metric_card(
            "Total Requirements",
            total_requirements,
            "metric-purple",
        )


    with metric_column_2:

        render_metric_card(
            "Requirements Met",
            completed_requirements,
            "metric-green",
        )


    with metric_column_3:

        render_metric_card(
            "Requirements Open",
            open_requirements,
            "metric-orange",
        )


    with metric_column_4:

        render_metric_card(
            "Overall Completion",
            f"{completion_percentage}%",
            "metric-blue",
        )


    checklist_column, progress_column = (
        st.columns(
            [
                1.7,
                1,
            ]
        )
    )


    with checklist_column:

        with st.container(
            border=True
        ):

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

                available_points = sorted(
                    combined_requirements[
                        "V&V Point"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )


                selected_vv_point = (
                    st.selectbox(
                        "Filter by V&V point",
                        [
                            "All V&V points"
                        ]
                        +
                        available_points,
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


                for _, row in (
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

                        details_column_1, details_column_2 = (
                            st.columns(2)
                        )


                        with details_column_1:

                            st.caption(
                                (
                                    f"V&V Point: "
                                    f"{row['V&V Point']}"
                                )
                            )


                        with details_column_2:

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


    with progress_column:

        with st.container(
            border=True
        ):

            st.subheader(
                "V&V Progress by Point"
            )


            if combined_requirements.empty:

                st.info(
                    "No V&V data available."
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
                    grouped[
                        "Met"
                    ]
                )


                grouped["Completion"] = (
                    (
                        grouped[
                            "Met"
                        ]
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


                for _, row in grouped.iterrows():

                    st.markdown(
                        (
                            f"**{row['V&V Point']}** "
                            f"— {int(row['Completion'])}%"
                        )
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


    deliverables_column, completion_column = (
        st.columns(
            [
                1.25,
                1,
            ]
        )
    )


    with deliverables_column:

        with st.container(
            border=True
        ):

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


    with completion_column:

        with st.container(
            border=True
        ):

            st.subheader(
                "Overall Completion"
            )


            ring_html = (
                '<div style="'
                'min-height:280px;'
                'display:flex;'
                'align-items:center;'
                'justify-content:center;'
                'flex-direction:column;'
                '">'
                '<div style="'
                'width:185px;'
                'height:185px;'
                'border-radius:50%;'
                'display:flex;'
                'align-items:center;'
                'justify-content:center;'
                'flex-direction:column;'
                'background:'
                'radial-gradient('
                'circle,'
                '#07152d 55%,'
                'transparent 57%'
                '),'
                'conic-gradient('
                f'#16d8ff 0% {completion_percentage}%,'
                f'#192b4d {completion_percentage}% 100%'
                ');'
                'box-shadow:'
                '0 0 34px '
                'rgba(29,190,255,0.20);'
                '">'
                '<div style="'
                'color:white;'
                'font-size:2.7rem;'
                'font-weight:800;'
                '">'
                f'{completion_percentage}%'
                '</div>'
                '<div style="'
                'color:#aebbd5;'
                '">'
                'Complete'
                '</div>'
                '</div>'
                '<div style="'
                'margin-top:1.2rem;'
                'color:#9eacc7;'
                '">'
                f'{completed_requirements} met'
                '&nbsp;·&nbsp;'
                f'{open_requirements} open'
                '</div>'
                '</div>'
            )


            st.markdown(
                ring_html,
                unsafe_allow_html=True,
            )