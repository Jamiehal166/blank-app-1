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
    page_icon="📋",
    layout="wide",
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


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_connection():
    """
    Open a SQLite database connection.
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# DATABASE SETUP
# ============================================================

def get_existing_columns(
    connection,
    table_name,
):
    """
    Return all columns currently present in a table.
    """

    table_information = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [
        column[1]
        for column in table_information
    ]


def create_or_update_database():
    """
    Create all required database tables.

    Existing data is preserved.
    """

    connection = get_database_connection()


    # --------------------------------------------------------
    # PROJECT-SPECIFIC REQUIREMENTS
    # --------------------------------------------------------

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
            stakeholder_input TEXT
        )
        """
    )


    requirement_columns = get_existing_columns(
        connection,
        "requirements",
    )


    if "boilerplate_name" not in requirement_columns:

        connection.execute(
            """
            ALTER TABLE requirements
            ADD COLUMN boilerplate_name TEXT
            """
        )


    if "stakeholder_input" not in requirement_columns:

        connection.execute(
            """
            ALTER TABLE requirements
            ADD COLUMN stakeholder_input TEXT
            """
        )


    # --------------------------------------------------------
    # STANDARD REQUIREMENT REVISION HEADERS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # STANDARD REQUIREMENT REVISION ITEMS
    # --------------------------------------------------------

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
            verification_method TEXT,
            notes TEXT,
            locked TEXT NOT NULL,
            FOREIGN KEY(revision_id)
                REFERENCES standard_requirement_revisions(id)
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
):
    """
    Save a stakeholder-submitted project requirement.
    """

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
            stakeholder_input
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        ),
    )


    connection.commit()
    connection.close()


def load_project_requirements():
    """
    Load all project-specific requirements.
    """

    connection = get_database_connection()


    requirements = pd.read_sql_query(
        """
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
            stakeholder_input
        FROM requirements
        WHERE requirement_type = 'Customer specific'
        ORDER BY id DESC
        """,
        connection,
    )


    connection.close()

    return requirements


# ============================================================
# STANDARD REQUIREMENT REVISION FUNCTIONS
# ============================================================

def load_standard_revisions(
    project_name,
):
    """
    Load all committed standard requirement revisions
    for one project.
    """

    connection = get_database_connection()


    revisions = pd.read_sql_query(
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

    return revisions


def load_standard_revision_items(
    revision_id,
):
    """
    Load every requirement item belonging to one revision.
    """

    connection = get_database_connection()


    items = pd.read_sql_query(
        """
        SELECT
            requirement_id,
            requirement_area,
            requirement_text,
            required_value,
            unit_or_limit,
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

    return items


def get_next_revision_number(
    project_name,
):
    """
    Return the next revision number.

    The first revision is 00.
    """

    revisions = load_standard_revisions(
        project_name
    )


    if revisions.empty:

        return "00"


    latest_revision = (
        revisions["revision_number"]
        .astype(int)
        .max()
    )


    return f"{latest_revision + 1:02d}"


def get_latest_revision_id(
    project_name,
):
    """
    Return the database ID of the latest revision.
    """

    revisions = load_standard_revisions(
        project_name
    )


    if revisions.empty:

        return None


    return int(
        revisions.iloc[-1]["id"]
    )


def load_latest_standard_values(
    project_name,
):
    """
    Load the most recent values for a project.

    These values populate the next revision.
    """

    latest_revision_id = get_latest_revision_id(
        project_name
    )


    if latest_revision_id is None:

        return {}


    latest_items = load_standard_revision_items(
        latest_revision_id
    )


    latest_values = {}


    for _, row in latest_items.iterrows():

        latest_values[
            str(
                row["requirement_id"]
            )
        ] = str(
            row["required_value"]
        )


    return latest_values


def commit_standard_revision(
    project_name,
    revision_number,
    committed_by,
    revision_comment,
    requirements_dataframe,
):
    """
    Save and lock a complete standard requirements revision.
    """

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
                verification_method,
                notes,
                locked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                revision_id,
                str(
                    row["Question ID"]
                ),
                str(
                    row["Requirement Area"]
                ),
                str(
                    row["Requirement"]
                ),
                str(
                    row["Required Value"]
                ),
                str(
                    row["Unit / Limit"]
                ),
                str(
                    row["Verification Method"]
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
# REVISION COMPARISON FUNCTIONS
# ============================================================

def revision_items_to_dictionary(
    revision_items,
):
    """
    Convert revision rows into a comparison dictionary.
    """

    revision_dictionary = {}


    for _, row in revision_items.iterrows():

        question_id = str(
            row["requirement_id"]
        )


        revision_dictionary[
            question_id
        ] = {

            "requirement_area":
                str(
                    row["requirement_area"]
                ),

            "requirement_text":
                str(
                    row["requirement_text"]
                ),

            "required_value":
                str(
                    row["required_value"]
                ),

            "unit_or_limit":
                str(
                    row["unit_or_limit"]
                ),

            "verification_method":
                str(
                    row["verification_method"]
                ),

            "notes":
                str(
                    row["notes"]
                ),
        }


    return revision_dictionary


def find_changed_question_ids(
    previous_revision_items,
    current_revision_items,
):
    """
    Compare two revisions and return changed IDs.
    """

    previous_dictionary = (
        revision_items_to_dictionary(
            previous_revision_items
        )
    )


    current_dictionary = (
        revision_items_to_dictionary(
            current_revision_items
        )
    )


    all_question_ids = sorted(

        set(
            previous_dictionary.keys()
        )

        |

        set(
            current_dictionary.keys()
        )
    )


    changed_question_ids = []


    for question_id in all_question_ids:

        if (
            previous_dictionary.get(
                question_id
            )
            !=
            current_dictionary.get(
                question_id
            )
        ):

            changed_question_ids.append(
                question_id
            )


    return changed_question_ids


def build_revision_history_summary(
    project_name,
):
    """
    Create the compact revision history.

    Revision 00 is shown as Initial issue.
    """

    revisions = load_standard_revisions(
        project_name
    )


    if revisions.empty:

        return pd.DataFrame()


    history_rows = []

    previous_revision_items = None


    for _, revision in revisions.iterrows():

        current_revision_items = (
            load_standard_revision_items(
                int(
                    revision["id"]
                )
            )
        )


        if previous_revision_items is None:

            changed_questions = (
                "Initial issue"
            )


        else:

            changed_ids = (
                find_changed_question_ids(
                    previous_revision_items,
                    current_revision_items,
                )
            )


            if changed_ids:

                changed_questions = (
                    ", ".join(
                        changed_ids
                    )
                )


            else:

                changed_questions = (
                    "No requirement changes"
                )


        history_rows.append(
            {

                "Revision":
                    str(
                        revision[
                            "revision_number"
                        ]
                    ),

                "Changed Question IDs":
                    changed_questions,

                "Committed By":
                    revision[
                        "committed_by"
                    ],

                "Committed Date":
                    revision[
                        "committed_date"
                    ],

                "Revision Comment":
                    revision[
                        "revision_comment"
                    ],
            }
        )


        previous_revision_items = (
            current_revision_items
        )


    return pd.DataFrame(
        history_rows
    )


# ============================================================
# VALUE HELPER FUNCTIONS
# ============================================================

def get_text_value(
    latest_values,
    question_id,
    default_value="",
):
    """
    Return a stored text value or a default.
    """

    value = latest_values.get(
        question_id,
        default_value,
    )


    if value in [
        "None",
        "nan",
    ]:

        return default_value


    return str(
        value
    )


def get_integer_value(
    latest_values,
    question_id,
    default_value=0,
):
    """
    Safely convert a stored value to an integer.
    """

    value = latest_values.get(
        question_id,
        default_value,
    )


    try:

        return int(
            float(
                value
            )
        )


    except (
        TypeError,
        ValueError,
    ):

        return default_value


def get_float_value(
    latest_values,
    question_id,
    default_value=0.0,
):
    """
    Safely convert a stored value to a float.
    """

    value = latest_values.get(
        question_id,
        default_value,
    )


    try:

        return float(
            value
        )


    except (
        TypeError,
        ValueError,
    ):

        return default_value


def selectbox_index(
    options,
    saved_value,
    default_index=0,
):
    """
    Return the correct selectbox position.
    """

    if saved_value in options:

        return options.index(
            saved_value
        )


    return default_index


# ============================================================
# ELECTRICAL REQUIREMENT LOOKUP
# ============================================================

def get_electrical_requirement(
    product_variant,
):
    """
    Return the electrical requirement implied
    by the selected valve variant.

    These descriptions can be replaced later with
    the approved technical specifications.
    """

    electrical_requirements = {

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


    return electrical_requirements.get(
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
    """
    Convert the standard questionnaire answers into
    a formal requirements table.
    """

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

            "Verification Method":
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

            "Verification Method":
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

            "Verification Method":
                "Document review",

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

            "Verification Method":
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

            "Verification Method":
                "Design review",

            "Notes":
                (
                    "Not applicable when an ISV product "
                    "variant other than ISV - MK3 is selected."
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

            "Verification Method":
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

            "Verification Method":
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
                    "The ISV spraybar shall use the "
                    "specified uniform valve pitch."
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

            "Verification Method":
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

            "Verification Method":
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

            "Verification Method":
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

            "Verification Method":
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

            "Verification Method":
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

            "Verification Method":
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
                    "shall comply with the electrical "
                    "requirements applicable to the "
                    "selected valve variant."
                ),

            "Required Value":
                electrical_requirement,

            "Unit / Limit":
                "",

            "Verification Method":
                "Electrical design review",

            "Notes":
                (
                    "Automatically generated from "
                    "the selected product variant."
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

            "Verification Method":
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

            "Verification Method":
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
# INITIALISE DATABASE
# ============================================================

create_or_update_database()


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "📋 ISV Requirements Management"
)


st.write(
    """
    Capture project requirements and maintain controlled,
    project-specific standard requirement revisions.
    """
)


# ============================================================
# APPLICATION TABS
# ============================================================

project_specific_tab, standard_requirements_tab = (
    st.tabs(
        [
            "Project-Specific Requirements",
            "Standard Requirements",
        ]
    )
)


# ============================================================
# PROJECT-SPECIFIC REQUIREMENTS TAB
# ============================================================

with project_specific_tab:


    st.header(
        "Project-Specific Requirement Capture"
    )


    st.write(
        """
        Select the type of requirement and answer the guided
        questions. The requirement statement is generated
        automatically.
        """
    )


    st.info(
        """
        New requirements are submitted with a status of
        **Pending** for project-owner review.
        """
    )


    # --------------------------------------------------------
    # REQUIREMENT DETAILS
    # --------------------------------------------------------

    st.subheader(
        "1. Requirement Details"
    )


    detail_column_1, detail_column_2 = (
        st.columns(2)
    )


    with detail_column_1:


        selected_project = st.selectbox(
            "Project *",
            options=ALLOWED_PROJECTS,
            key="project_specific_project",
        )


        requirement_title = st.text_input(
            "Requirement title *",
            placeholder=(
                "Example: Ambient operating temperature"
            ),
            key="project_requirement_title",
        )


    with detail_column_2:


        source_department = st.selectbox(
            "Where did this requirement come from? *",
            options=[
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
            key="project_requirement_source",
        )


        submitted_by = st.text_input(
            "Submitted by *",
            placeholder="Enter your name",
            key="project_requirement_submitter",
        )


    # --------------------------------------------------------
    # REQUIREMENT TYPE
    # --------------------------------------------------------

    st.divider()


    st.subheader(
        "2. What Type of Requirement Is This?"
    )


    selected_requirement_category = (
        st.selectbox(
            "Requirement type *",
            options=(
                PROJECT_REQUIREMENT_CATEGORIES
            ),
            key="project_requirement_category",
        )
    )


    # --------------------------------------------------------
    # GUIDED INPUT
    # --------------------------------------------------------

    st.divider()


    st.subheader(
        "3. Tell Us What Is Needed"
    )


    generated_requirement = ""

    requirement_preview = ""

    stakeholder_input = ""

    required_inputs_complete = False

    database_category = "Other"


    if (
        selected_requirement_category
        == "Operating condition"
    ):


        database_category = "Environmental"


        input_column_1, input_column_2 = (
            st.columns(2)
        )


        with input_column_1:


            equipment_name = st.text_input(
                (
                    "What equipment or system "
                    "does this apply to? *"
                ),
                value="ISV spraybar",
                key="operating_equipment",
            )


            required_action = st.text_input(
                "What must it do? *",
                placeholder=(
                    "Example: operate continuously"
                ),
                key="operating_action",
            )


        with input_column_2:


            operating_condition = st.text_area(
                (
                    "Under what condition "
                    "must it operate? *"
                ),
                placeholder=(
                    "Example: at an ambient temperature "
                    "between 5°C and 45°C"
                ),
                key="operating_condition",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                required_action.strip(),
                operating_condition.strip(),
            ]
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall "
            f"{required_action.strip() or '[required action]'} "
            f"{operating_condition.strip() or '[operating condition]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"{operating_condition.strip()}."
        )


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Action: {required_action.strip()}\n"
            f"Condition: {operating_condition.strip()}"
        )


    elif (
        selected_requirement_category
        == "Capacity or quantity"
    ):


        database_category = "Capacity"


        input_column_1, input_column_2 = (
            st.columns(2)
        )


        with input_column_1:


            equipment_name = st.text_input(
                (
                    "What equipment or system "
                    "does this apply to? *"
                ),
                value="ISV spraybar",
                key="capacity_equipment",
            )


            required_action = st.text_input(
                "What must it do? *",
                placeholder="Example: control",
                key="capacity_action",
            )


        with input_column_2:


            minimum_quantity = st.number_input(
                (
                    "What is the minimum "
                    "quantity required? *"
                ),
                min_value=0,
                step=1,
                key="capacity_quantity",
            )


            item_name = st.text_input(
                "What is being counted? *",
                placeholder="Example: spray zones",
                key="capacity_item",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                required_action.strip(),
                minimum_quantity > 0,
                item_name.strip(),
            ]
        )


        quantity_preview = (
            str(
                minimum_quantity
            )
            if minimum_quantity > 0
            else
            "[minimum quantity]"
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall "
            f"{required_action.strip() or '[required action]'} "
            f"a minimum of "
            f"{quantity_preview} "
            f"{item_name.strip() or '[item]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"a minimum of "
            f"{minimum_quantity} "
            f"{item_name.strip()}."
        )


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Action: {required_action.strip()}\n"
            f"Quantity: {minimum_quantity}\n"
            f"Item: {item_name.strip()}"
        )


    else:


        stakeholder_description = (
            st.text_area(
                "Describe what is needed *",
                placeholder=(
                    "Describe the requirement "
                    "in your own words."
                ),
                key="general_project_requirement",
            )
        )


        required_inputs_complete = bool(
            stakeholder_description.strip()
        )


        requirement_preview = (
            stakeholder_description.strip()
            or
            "[Describe the requirement]"
        )


        generated_requirement = (
            stakeholder_description.strip()
        )


        stakeholder_input = (
            stakeholder_description.strip()
        )


    # --------------------------------------------------------
    # LIVE PREVIEW
    # --------------------------------------------------------

    st.divider()


    st.subheader(
        "4. Live Requirement Preview"
    )


    st.code(
        requirement_preview,
        language=None,
    )


    if required_inputs_complete:


        st.success(
            (
                "The requirement is complete "
                "and ready to submit."
            )
        )


    else:


        st.info(
            (
                "Fields shown in square brackets "
                "still need to be completed."
            )
        )


    # --------------------------------------------------------
    # SUBMIT PROJECT REQUIREMENT
    # --------------------------------------------------------

    st.divider()


    st.subheader(
        "5. Submit for Project-Owner Review"
    )


    submit_project_requirement = st.button(
        "Submit Requirement",
        type="primary",
        use_container_width=True,
        key="submit_project_requirement",
    )


    if submit_project_requirement:


        errors = []


        if not requirement_title.strip():

            errors.append(
                "Requirement title"
            )


        if not submitted_by.strip():

            errors.append(
                "Submitted by"
            )


        if not required_inputs_complete:

            errors.append(
                "All required questions"
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
                    database_category
                ),
                source_department=(
                    source_department
                ),
                submitted_by=(
                    submitted_by.strip()
                ),
                requirement_category=(
                    selected_requirement_category
                ),
                stakeholder_input=(
                    stakeholder_input
                ),
            )


            st.success(
                (
                    "Requirement submitted successfully. "
                    "Its status is Pending."
                )
            )


    # --------------------------------------------------------
    # PROJECT REQUIREMENTS TABLE
    # --------------------------------------------------------

    project_requirements = (
        load_project_requirements()
    )


    st.divider()


    st.header(
        "Project Requirements Dashboard"
    )


    if project_requirements.empty:


        st.info(
            (
                "No project-specific requirements "
                "have been submitted."
            )
        )


    else:


        project_display = (
            project_requirements.rename(
                columns={
                    "id":
                        "ID",

                    "project_name":
                        "Project",

                    "requirement_title":
                        "Title",

                    "requirement_text":
                        "Requirement",

                    "boilerplate_name":
                        "Requirement Type",

                    "status":
                        "Status",
                }
            )
        )


        st.dataframe(
            project_display[
                [
                    "ID",
                    "Project",
                    "Title",
                    "Requirement",
                    "Requirement Type",
                    "Status",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# STANDARD REQUIREMENTS TAB
# ============================================================

with standard_requirements_tab:


    st.header(
        "Standard Project Requirements"
    )


    st.write(
        """
        Complete the guided ISV project questions. The
        application converts the answers into a standard
        requirements table. Committed revisions are locked.
        """
    )


    st.info(
        """
        The first revision for each project is **Revision 00**.
        New revisions begin using the latest committed values.
        """
    )


    # ========================================================
    # SECTION 1
    # SELECT PROJECT
    # ========================================================

    st.subheader(
        "1. Select Project"
    )


    standard_project = st.selectbox(
        "Project *",
        options=ALLOWED_PROJECTS,
        key="standard_project",
    )


    latest_standard_values = (
        load_latest_standard_values(
            standard_project
        )
    )


    next_revision_number = (
        get_next_revision_number(
            standard_project
        )
    )


    # ========================================================
    # SECTION 2
    # REVISION HISTORY
    # ========================================================

    st.divider()


    st.subheader(
        "2. Revision History"
    )


    revision_history = (
        build_revision_history_summary(
            standard_project
        )
    )


    if revision_history.empty:


        st.info(
            (
                f"No standard requirements revision "
                f"has been committed for "
                f"{standard_project}."
            )
        )


    else:


        st.dataframe(
            revision_history,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Revision":
                    st.column_config.TextColumn(
                        "Revision",
                        width="small",
                    ),

                "Changed Question IDs":
                    st.column_config.TextColumn(
                        "Changed Question IDs",
                        width="large",
                    ),

                "Committed By":
                    st.column_config.TextColumn(
                        "Committed By",
                        width="medium",
                    ),

                "Committed Date":
                    st.column_config.TextColumn(
                        "Committed Date",
                        width="medium",
                    ),

                "Revision Comment":
                    st.column_config.TextColumn(
                        "Revision Comment",
                        width="large",
                    ),
            },
        )


    # ========================================================
    # SECTION 3
    # STANDARD REQUIREMENT QUESTIONS
    # ========================================================

    st.divider()


    st.subheader(
        "3. Complete Standard Project Requirements"
    )


    st.write(
        (
            f"These answers will create Revision "
            f"**{next_revision_number}** for "
            f"**{standard_project}**."
        )
    )


    # --------------------------------------------------------
    # PROJECT INFORMATION
    # --------------------------------------------------------

    with st.expander(
        "Project Information",
        expanded=True,
    ):


        project_column_1, project_column_2 = (
            st.columns(2)
        )


        with project_column_1:


            customer_name = st.text_input(
                "Customer name *",
                value=get_text_value(
                    latest_standard_values,
                    "STD-002",
                ),
                placeholder=(
                    "Enter the customer name"
                ),
                key=(
                    f"customer_"
                    f"{standard_project}"
                ),
            )


        saved_mill_type = (
            get_text_value(
                latest_standard_values,
                "STD-003",
                "FFM",
            )
        )


        with project_column_2:


            mill_type_selection = (
                st.selectbox(
                    "Mill type *",
                    options=MILL_TYPES,
                    index=selectbox_index(
                        MILL_TYPES,
                        (
                            saved_mill_type
                            if saved_mill_type
                            in MILL_TYPES
                            else
                            "Other"
                        ),
                        0,
                    ),
                    key=(
                        f"mill_type_"
                        f"{standard_project}"
                    ),
                )
            )


        if mill_type_selection == "Other":


            default_other_mill = (
                saved_mill_type
                if saved_mill_type
                not in MILL_TYPES
                else
                ""
            )


            other_mill_type = st.text_input(
                "Specify the mill type *",
                value=default_other_mill,
                key=(
                    f"other_mill_"
                    f"{standard_project}"
                ),
            )


            final_mill_type = (
                other_mill_type.strip()
            )


        else:


            final_mill_type = (
                mill_type_selection
            )


    # --------------------------------------------------------
    # VALVE CONFIGURATION
    # --------------------------------------------------------

    with st.expander(
        "Valve Configuration",
        expanded=True,
    ):


        saved_product_variant = (
            get_text_value(
                latest_standard_values,
                "STD-004",
                "ISV - MK3",
            )
        )


        product_variant = st.selectbox(
            "ISV product variant *",
            options=ISV_PRODUCT_VARIANTS,
            index=selectbox_index(
                ISV_PRODUCT_VARIANTS,
                saved_product_variant,
                0,
            ),
            key=(
                f"product_variant_"
                f"{standard_project}"
            ),
        )


        if product_variant == "ISV - MK3":


            saved_mk3_configuration = (
                get_text_value(
                    latest_standard_values,
                    "STD-005",
                    "Standard",
                )
            )


            mk3_configuration = (
                st.selectbox(
                    "MK3 configuration *",
                    options=(
                        MK3_CONFIGURATIONS
                    ),
                    index=selectbox_index(
                        MK3_CONFIGURATIONS,
                        saved_mk3_configuration,
                        0,
                    ),
                    key=(
                        f"mk3_configuration_"
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
                "Electrical requirements are generated "
                "automatically from the selected valve type."
            )
        )


    # --------------------------------------------------------
    # VALVE PITCHING
    # --------------------------------------------------------

    with st.expander(
        "Valve Pitching",
        expanded=True,
    ):


        saved_pitching_type = (
            get_text_value(
                latest_standard_values,
                "STD-006",
                "Uniform pitching",
            )
        )


        pitching_type = st.selectbox(
            "Pitch configuration *",
            options=PITCHING_TYPES,
            index=selectbox_index(
                PITCHING_TYPES,
                saved_pitching_type,
                0,
            ),
            key=(
                f"pitching_type_"
                f"{standard_project}"
            ),
        )


        if pitching_type == "Uniform pitching":


            pitching_column_1, pitching_column_2 = (
                st.columns(2)
            )


            with pitching_column_1:


                total_valves = (
                    st.number_input(
                        "Total number of valves *",
                        min_value=1,
                        step=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_standard_values,
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


            with pitching_column_2:


                uniform_pitch = (
                    st.number_input(
                        "Uniform valve pitch *",
                        min_value=0.0,
                        step=1.0,
                        value=get_float_value(
                            latest_standard_values,
                            "STD-008",
                            52.0,
                        ),
                        help="Value in millimetres.",
                        key=(
                            f"uniform_pitch_"
                            f"{standard_project}"
                        ),
                    )
                )


            edge_valves_per_side = 0

            edge_pitch = 0.0

            centre_valves = 0

            centre_pitch = 0.0


        else:


            hybrid_column_1, hybrid_column_2 = (
                st.columns(2)
            )


            with hybrid_column_1:


                edge_valves_per_side = (
                    st.number_input(
                        (
                            "Number of edge valves "
                            "per side *"
                        ),
                        min_value=1,
                        step=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_standard_values,
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
                        "Edge valve pitch *",
                        min_value=0.0,
                        step=1.0,
                        value=get_float_value(
                            latest_standard_values,
                            "STD-010",
                            26.0,
                        ),
                        help="Value in millimetres.",
                        key=(
                            f"edge_pitch_"
                            f"{standard_project}"
                        ),
                    )
                )


            with hybrid_column_2:


                centre_valves = (
                    st.number_input(
                        "Number of centre valves *",
                        min_value=1,
                        step=1,
                        value=max(
                            1,
                            get_integer_value(
                                latest_standard_values,
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
                        "Centre valve pitch *",
                        min_value=0.0,
                        step=1.0,
                        value=get_float_value(
                            latest_standard_values,
                            "STD-012",
                            52.0,
                        ),
                        help="Value in millimetres.",
                        key=(
                            f"centre_pitch_"
                            f"{standard_project}"
                        ),
                    )
                )


            total_valves = (
                (
                    edge_valves_per_side
                    * 2
                )
                +
                centre_valves
            )


            uniform_pitch = 0.0


            st.metric(
                "Calculated total valves",
                total_valves,
            )


            st.caption(
                (
                    f"{edge_valves_per_side} valves "
                    f"on the left edge + "
                    f"{centre_valves} centre valves + "
                    f"{edge_valves_per_side} valves "
                    f"on the right edge."
                )
            )


    # --------------------------------------------------------
    # OPERATING FLUID
    # --------------------------------------------------------

    with st.expander(
        "Operating Fluid",
        expanded=True,
    ):


        saved_fluid = (
            get_text_value(
                latest_standard_values,
                "STD-013",
                "Water",
            )
        )


        fluid_selection = st.selectbox(
            "Operating fluid *",
            options=OPERATING_FLUIDS,
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
                f"operating_fluid_"
                f"{standard_project}"
            ),
        )


        if fluid_selection == "Other":


            default_other_fluid = (
                saved_fluid
                if saved_fluid
                not in OPERATING_FLUIDS
                else
                ""
            )


            other_fluid = st.text_input(
                "Specify the operating fluid *",
                value=default_other_fluid,
                key=(
                    f"other_fluid_"
                    f"{standard_project}"
                ),
            )


            final_operating_fluid = (
                other_fluid.strip()
            )


        else:


            final_operating_fluid = (
                fluid_selection
            )


    # ========================================================
    # GENERATE STANDARD REQUIREMENTS
    # ========================================================

    generated_standard_requirements = (
        build_standard_requirement_table(

            project_name=(
                standard_project
            ),

            customer_name=(
                customer_name.strip()
            ),

            mill_type=(
                final_mill_type
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
                edge_valves_per_side
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
                final_operating_fluid
            ),
        )
    )


    # ========================================================
    # SECTION 4
    # GENERATED REQUIREMENT TABLE
    # ========================================================

    st.divider()


    st.subheader(
        "4. Review Generated Standard Requirements"
    )


    st.write(
        """
        This read-only table has been generated from the
        project answers above.
        """
    )


    st.dataframe(
        generated_standard_requirements,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Question ID":
                st.column_config.TextColumn(
                    "Question ID",
                    width="small",
                ),

            "Requirement Area":
                st.column_config.TextColumn(
                    "Requirement Area",
                    width="medium",
                ),

            "Requirement":
                st.column_config.TextColumn(
                    "Requirement",
                    width="large",
                ),

            "Required Value":
                st.column_config.TextColumn(
                    "Required Value",
                    width="medium",
                ),

            "Verification Method":
                st.column_config.TextColumn(
                    "Verification Method",
                    width="medium",
                ),
        },
    )


    # ========================================================
    # SECTION 5
    # COMMIT LOCKED REVISION
    # ========================================================

    st.divider()


    st.subheader(
        "5. Commit Locked Revision"
    )


    commit_column_1, commit_column_2 = (
        st.columns(2)
    )


    with commit_column_1:


        committed_by = st.text_input(
            "Committed by *",
            placeholder="Enter your name",
            key=(
                f"committed_by_"
                f"{standard_project}"
            ),
        )


    with commit_column_2:


        revision_comment = st.text_input(
            "Revision comment",
            placeholder=(
                "Example: Initial project baseline"
            ),
            key=(
                f"revision_comment_"
                f"{standard_project}"
            ),
        )


    st.warning(
        (
            f"Committing will permanently save and lock "
            f"Revision **{next_revision_number}** for "
            f"project **{standard_project}**."
        )
    )


    commit_button = st.button(
        (
            f"Commit Locked Revision "
            f"{next_revision_number}"
        ),
        type="primary",
        use_container_width=True,
        key=(
            f"commit_revision_"
            f"{standard_project}"
        ),
    )


    if commit_button:


        errors = []


        if not customer_name.strip():

            errors.append(
                "Customer name"
            )


        if not final_mill_type.strip():

            errors.append(
                "Mill type"
            )


        if not final_operating_fluid.strip():

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
                "Uniform valve pitch"
            )


        if (
            pitching_type
            == "Hybrid pitching"
            and
            edge_pitch <= 0
        ):

            errors.append(
                "Edge valve pitch"
            )


        if (
            pitching_type
            == "Hybrid pitching"
            and
            centre_pitch <= 0
        ):

            errors.append(
                "Centre valve pitch"
            )


        if errors:


            st.error(
                (
                    "The revision cannot be committed. "
                    "Please complete or correct: "
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
                        next_revision_number
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
                        f"{next_revision_number} "
                        f"has been committed and locked "
                        f"for {standard_project}."
                    )
                )


                st.rerun()


            except sqlite3.IntegrityError:


                st.error(
                    (
                        "The revision could not be committed "
                        "because the revision number already "
                        "exists. Refresh the page and try again."
                    )
                )