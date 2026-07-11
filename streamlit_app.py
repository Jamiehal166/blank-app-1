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


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_connection():
    """
    Open a connection to the SQLite database.
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
    Return all column names for a database table.
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
    Create all required tables.

    Existing data from previous versions is preserved.
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
    # STANDARD REQUIREMENT REVISIONS
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
    # STANDARD REQUIREMENT ITEMS
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
# PROJECT-SPECIFIC DATABASE FUNCTIONS
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
    Save a project-specific stakeholder requirement.
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
# STANDARD REQUIREMENT DATABASE FUNCTIONS
# ============================================================

def load_standard_revisions(
    project_name,
):
    """
    Load all committed standard requirement revisions
    for the selected project.
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
    Load all standard requirement rows
    belonging to one revision.
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
    Return the next two-digit revision number.

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


    latest_row = revisions.iloc[-1]


    return int(
        latest_row["id"]
    )


def load_latest_standard_values(
    project_name,
):
    """
    Load the latest committed values for a project.

    These values are used as the starting point
    for the next revision.
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
            row["requirement_id"]
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
    Commit and lock a complete standard requirement revision.
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
    Convert revision rows into a dictionary.

    This makes comparison between revisions easier.
    """

    revision_dictionary = {}


    for _, row in revision_items.iterrows():

        requirement_id = str(
            row["requirement_id"]
        )


        revision_dictionary[
            requirement_id
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
    Compare two locked revisions.

    Return all question IDs which were:
    - changed;
    - added; or
    - removed.
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

        previous_value = (
            previous_dictionary.get(
                question_id
            )
        )


        current_value = (
            current_dictionary.get(
                question_id
            )
        )


        if previous_value != current_value:

            changed_question_ids.append(
                question_id
            )


    return changed_question_ids


def build_revision_history_summary(
    project_name,
):
    """
    Create a compact revision history.

    Revision 00 is labelled as Initial issue.

    Later revisions show only the question IDs
    changed from the immediately previous revision.
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


        revision_number = str(
            revision["revision_number"]
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
                    revision_number,

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
# VALUE CONVERSION HELPERS
# ============================================================

def get_text_value(
    latest_values,
    question_id,
    default_value="",
):
    """
    Return a saved text value or a default.
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
    Safely convert a saved value into an integer.
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
    Safely convert a saved value into a float.
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
    Find the correct selectbox index
    for a previously saved value.
    """

    if saved_value in options:

        return options.index(
            saved_value
        )


    return default_index


# ============================================================
# STANDARD REQUIREMENT TABLE GENERATOR
# ============================================================

def build_standard_requirement_table(
    project_name,
    customer_name,
    product_variant,
    number_of_spray_zones,
    spraybar_length,
    zone_pitch,
    operating_fluid,
    maximum_pressure,
    minimum_flow_rate,
    solenoid_voltage,
    control_interface,
    installation_side,
    minimum_temperature,
    maximum_temperature,
    approval_drawing_required,
    manufacturing_drawings_required,
):
    """
    Convert the questionnaire answers into
    a formal standard requirements table.
    """

    standard_requirements = [


        {
            "Question ID":
                "STD-001",

            "Requirement Area":
                "Project Definition",

            "Requirement":
                (
                    "The project shall use the selected "
                    "project reference."
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
                "Project Definition",

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
                "Product Configuration",

            "Requirement":
                (
                    "The ISV system shall use the "
                    "selected product variant."
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
                "STD-004",

            "Requirement Area":
                "Mechanical",

            "Requirement":
                (
                    "The ISV spraybar shall provide "
                    "the specified number of spray zones."
                ),

            "Required Value":
                str(
                    number_of_spray_zones
                ),

            "Unit / Limit":
                "zones",

            "Verification Method":
                "Drawing review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-005",

            "Requirement Area":
                "Mechanical",

            "Requirement":
                (
                    "The ISV spraybar shall have "
                    "the specified overall length."
                ),

            "Required Value":
                f"{spraybar_length:g}",

            "Unit / Limit":
                "mm",

            "Verification Method":
                "Drawing review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-006",

            "Requirement Area":
                "Mechanical",

            "Requirement":
                (
                    "The ISV spray zones shall use "
                    "the specified zone pitch."
                ),

            "Required Value":
                f"{zone_pitch:g}",

            "Unit / Limit":
                "mm",

            "Verification Method":
                "Drawing review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-007",

            "Requirement Area":
                "Fluid",

            "Requirement":
                (
                    "The ISV system shall operate "
                    "using the specified fluid."
                ),

            "Required Value":
                operating_fluid,

            "Unit / Limit":
                "",

            "Verification Method":
                "Document review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-008",

            "Requirement Area":
                "Fluid",

            "Requirement":
                (
                    "The ISV system shall be designed "
                    "for the specified maximum operating pressure."
                ),

            "Required Value":
                f"{maximum_pressure:g}",

            "Unit / Limit":
                "bar",

            "Verification Method":
                "Design review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-009",

            "Requirement Area":
                "Fluid",

            "Requirement":
                (
                    "The ISV system shall support "
                    "the specified minimum flow rate."
                ),

            "Required Value":
                f"{minimum_flow_rate:g}",

            "Unit / Limit":
                "litres per minute",

            "Verification Method":
                "Calculation / design review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-010",

            "Requirement Area":
                "Electrical",

            "Requirement":
                (
                    "The ISV solenoid valves shall use "
                    "the specified operating voltage."
                ),

            "Required Value":
                f"{solenoid_voltage:g}",

            "Unit / Limit":
                "V",

            "Verification Method":
                "Document review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-011",

            "Requirement Area":
                "Controls",

            "Requirement":
                (
                    "The ISV system shall use "
                    "the specified control interface."
                ),

            "Required Value":
                control_interface,

            "Unit / Limit":
                "",

            "Verification Method":
                "Design review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-012",

            "Requirement Area":
                "Installation",

            "Requirement":
                (
                    "The ISV spraybar shall be configured "
                    "for the specified installation side."
                ),

            "Required Value":
                installation_side,

            "Unit / Limit":
                "",

            "Verification Method":
                "Drawing review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-013",

            "Requirement Area":
                "Environment",

            "Requirement":
                (
                    "The ISV system shall operate "
                    "within the specified ambient temperature range."
                ),

            "Required Value":
                (
                    f"{minimum_temperature:g} "
                    f"to "
                    f"{maximum_temperature:g}"
                ),

            "Unit / Limit":
                "°C",

            "Verification Method":
                "Document review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-014",

            "Requirement Area":
                "Documentation",

            "Requirement":
                (
                    "The project shall provide a customer "
                    "approval drawing when required."
                ),

            "Required Value":
                approval_drawing_required,

            "Unit / Limit":
                "Yes / No",

            "Verification Method":
                "Document review",

            "Notes":
                "",
        },


        {
            "Question ID":
                "STD-015",

            "Requirement Area":
                "Documentation",

            "Requirement":
                (
                    "The project shall provide manufacturing "
                    "drawings when required."
                ),

            "Required Value":
                manufacturing_drawings_required,

            "Unit / Limit":
                "Yes / No",

            "Verification Method":
                "Document review",

            "Notes":
                "",
        },
    ]


    return pd.DataFrame(
        standard_requirements
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
    Capture project-specific stakeholder requirements and
    project standard requirements in a structured and
    traceable format.
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
        Select the type of requirement you want to add and
        answer the guided questions. The completed requirement
        will be generated automatically.
        """
    )


    st.info(
        """
        New requirements are submitted with a status of
        **Pending** for project-owner review.
        """
    )


    # ========================================================
    # PROJECT REQUIREMENT DETAILS
    # ========================================================

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


    # ========================================================
    # PROJECT REQUIREMENT TYPE
    # ========================================================

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


    # ========================================================
    # PROJECT REQUIREMENT INPUT
    # ========================================================

    st.divider()


    st.subheader(
        "3. Tell Us What Is Needed"
    )


    generated_requirement = ""

    requirement_preview = ""

    stakeholder_input = ""

    required_inputs_complete = False

    database_category = "Other"


    # --------------------------------------------------------
    # OPERATING CONDITION
    # --------------------------------------------------------

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


        equipment_preview = (
            equipment_name.strip()
            or
            "[equipment or system]"
        )


        action_preview = (
            required_action.strip()
            or
            "[required action]"
        )


        condition_preview = (
            operating_condition.strip()
            or
            "[operating condition]"
        )


        requirement_preview = (
            f"The {equipment_preview} shall "
            f"{action_preview} "
            f"{condition_preview}."
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


    # --------------------------------------------------------
    # CAPACITY OR QUANTITY
    # --------------------------------------------------------

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


        equipment_preview = (
            equipment_name.strip()
            or
            "[equipment or system]"
        )


        action_preview = (
            required_action.strip()
            or
            "[required action]"
        )


        quantity_preview = (
            str(
                minimum_quantity
            )
            if minimum_quantity > 0
            else
            "[minimum quantity]"
        )


        item_preview = (
            item_name.strip()
            or
            "[item being counted]"
        )


        requirement_preview = (
            f"The {equipment_preview} shall "
            f"{action_preview} "
            f"a minimum of "
            f"{quantity_preview} "
            f"{item_preview}."
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


    # --------------------------------------------------------
    # PERFORMANCE LEVEL
    # --------------------------------------------------------

    elif (
        selected_requirement_category
        == "Performance level"
    ):


        database_category = "Performance"


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
                key="performance_equipment",
            )


            required_action = st.text_input(
                "What must it do? *",
                placeholder=(
                    "Example: deliver cooling fluid"
                ),
                key="performance_action",
            )


        with input_column_2:


            required_value = st.number_input(
                (
                    "What is the minimum "
                    "required value? *"
                ),
                min_value=0.0,
                step=1.0,
                key="performance_value",
            )


            engineering_unit = st.text_input(
                "What unit is used? *",
                placeholder=(
                    "Example: litres per minute"
                ),
                key="performance_unit",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                required_action.strip(),
                required_value > 0,
                engineering_unit.strip(),
            ]
        )


        value_preview = (
            f"{required_value:g}"
            if required_value > 0
            else
            "[minimum value]"
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall "
            f"{required_action.strip() or '[required action]'} "
            f"at a minimum value of "
            f"{value_preview} "
            f"{engineering_unit.strip() or '[unit]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"at a minimum value of "
            f"{required_value:g} "
            f"{engineering_unit.strip()}."
        )


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Action: {required_action.strip()}\n"
            f"Value: {required_value:g}\n"
            f"Unit: {engineering_unit.strip()}"
        )


    # --------------------------------------------------------
    # RESPONSE TIME
    # --------------------------------------------------------

    elif (
        selected_requirement_category
        == "Response time"
    ):


        database_category = "Performance"


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
                key="response_equipment",
            )


            required_action = st.text_input(
                "What action must happen? *",
                placeholder=(
                    "Example: begin coolant delivery"
                ),
                key="response_action",
            )


            trigger_event = st.text_input(
                "What triggers the action? *",
                placeholder=(
                    "Example: receiving a control signal"
                ),
                key="response_trigger",
            )


        with input_column_2:


            maximum_time = st.number_input(
                (
                    "What is the maximum "
                    "permitted time? *"
                ),
                min_value=0.0,
                step=0.1,
                key="response_time",
            )


            time_unit = st.selectbox(
                "Time unit *",
                options=[
                    "milliseconds",
                    "seconds",
                    "minutes",
                    "hours",
                ],
                key="response_unit",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                required_action.strip(),
                trigger_event.strip(),
                maximum_time > 0,
            ]
        )


        time_preview = (
            f"{maximum_time:g}"
            if maximum_time > 0
            else
            "[maximum time]"
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall "
            f"{required_action.strip() or '[required action]'} "
            f"within "
            f"{time_preview} "
            f"{time_unit} of "
            f"{trigger_event.strip() or '[trigger event]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"within "
            f"{maximum_time:g} "
            f"{time_unit} of "
            f"{trigger_event.strip()}."
        )


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Action: {required_action.strip()}\n"
            f"Trigger: {trigger_event.strip()}\n"
            f"Time: {maximum_time:g} {time_unit}"
        )


    # --------------------------------------------------------
    # COMPATIBILITY OR INTERFACE
    # --------------------------------------------------------

    elif (
        selected_requirement_category
        == "Compatibility or interface"
    ):


        database_category = "Interface"


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
                key="interface_equipment",
            )


            external_system = st.text_input(
                (
                    "What other equipment "
                    "must it connect to? *"
                ),
                placeholder=(
                    "Example: mill control system"
                ),
                key="interface_external_system",
            )


        with input_column_2:


            interface_description = st.text_input(
                (
                    "What connection or "
                    "interface is required? *"
                ),
                placeholder=(
                    "Example: 64 digital outputs"
                ),
                key="interface_description",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                external_system.strip(),
                interface_description.strip(),
            ]
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall interface with the "
            f"{external_system.strip() or '[external system]'} "
            f"using "
            f"{interface_description.strip() or '[interface]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} "
            f"shall interface with the "
            f"{external_system.strip()} "
            f"using "
            f"{interface_description.strip()}."
        )


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"External system: {external_system.strip()}\n"
            f"Interface: {interface_description.strip()}"
        )


    # --------------------------------------------------------
    # PRODUCT TYPE OR STANDARD
    # --------------------------------------------------------

    elif (
        selected_requirement_category
        == "Product type or standard"
    ):


        database_category = "Specification"


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
                key="standard_equipment",
            )


            specified_item = st.text_input(
                "What item is being specified? *",
                placeholder="Example: cooling fluid",
                key="standard_item",
            )


        with input_column_2:


            required_standard = st.text_input(
                (
                    "What type, grade, or "
                    "standard is required? *"
                ),
                placeholder="Example: ISO VG 32",
                key="standard_grade",
            )


            operating_limit = st.text_input(
                "Are there any operating limits?",
                placeholder=(
                    "Example: at a maximum pressure "
                    "of 10 bar"
                ),
                key="standard_limit",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                specified_item.strip(),
                required_standard.strip(),
            ]
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall use "
            f"{required_standard.strip() or '[type or standard]'} "
            f"{specified_item.strip() or '[specified item]'} "
            f"{operating_limit.strip() or '[optional operating limit]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} "
            f"shall use "
            f"{required_standard.strip()} "
            f"{specified_item.strip()}"
        )


        if operating_limit.strip():

            generated_requirement += (
                f" {operating_limit.strip()}"
            )


        generated_requirement += "."


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Item: {specified_item.strip()}\n"
            f"Standard: {required_standard.strip()}\n"
            f"Limit: {operating_limit.strip()}"
        )


    # --------------------------------------------------------
    # RELIABILITY OR MAINTENANCE
    # --------------------------------------------------------

    elif (
        selected_requirement_category
        == "Reliability or maintenance"
    ):


        database_category = "Maintenance"


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
                key="reliability_equipment",
            )


            required_action = st.text_input(
                "What must continue operating? *",
                placeholder="Example: operate",
                key="reliability_action",
            )


        with input_column_2:


            minimum_duration = st.number_input(
                (
                    "What is the minimum "
                    "required duration? *"
                ),
                min_value=0.0,
                step=100.0,
                key="reliability_duration",
            )


            duration_unit = st.text_input(
                "What unit is used? *",
                placeholder=(
                    "Example: operating hours"
                ),
                key="reliability_unit",
            )


            maintenance_condition = st.text_input(
                (
                    "What maintenance "
                    "limitation applies?"
                ),
                placeholder=(
                    "Example: without planned maintenance"
                ),
                key="reliability_condition",
            )


        required_inputs_complete = all(
            [
                equipment_name.strip(),
                required_action.strip(),
                minimum_duration > 0,
                duration_unit.strip(),
            ]
        )


        duration_preview = (
            f"{minimum_duration:g}"
            if minimum_duration > 0
            else
            "[minimum duration]"
        )


        requirement_preview = (
            f"The "
            f"{equipment_name.strip() or '[equipment or system]'} "
            f"shall "
            f"{required_action.strip() or '[required action]'} "
            f"for a minimum of "
            f"{duration_preview} "
            f"{duration_unit.strip() or '[unit]'} "
            f"{maintenance_condition.strip() or '[optional maintenance condition]'}."
        )


        generated_requirement = (
            f"The {equipment_name.strip()} "
            f"shall "
            f"{required_action.strip()} "
            f"for a minimum of "
            f"{minimum_duration:g} "
            f"{duration_unit.strip()}"
        )


        if maintenance_condition.strip():

            generated_requirement += (
                f" {maintenance_condition.strip()}"
            )


        generated_requirement += "."


        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Action: {required_action.strip()}\n"
            f"Duration: {minimum_duration:g} "
            f"{duration_unit.strip()}\n"
            f"Maintenance: "
            f"{maintenance_condition.strip()}"
        )


    # --------------------------------------------------------
    # OTHER REQUIREMENT
    # --------------------------------------------------------

    else:


        database_category = "Other"


        stakeholder_description = (
            st.text_area(
                "Describe what is needed *",
                placeholder=(
                    "Example: The spraybar must be "
                    "accessible from the operator side."
                ),
                key="other_description",
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


    # ========================================================
    # LIVE PROJECT REQUIREMENT PREVIEW
    # ========================================================

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


    # ========================================================
    # SAVE PROJECT REQUIREMENT
    # ========================================================

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


        missing_fields = []


        if not requirement_title.strip():

            missing_fields.append(
                "Requirement title"
            )


        if not submitted_by.strip():

            missing_fields.append(
                "Submitted by"
            )


        if not required_inputs_complete:

            missing_fields.append(
                "All required questions"
            )


        if missing_fields:


            st.error(
                (
                    "Please complete: "
                    +
                    ", ".join(
                        missing_fields
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


    # ========================================================
    # PROJECT REQUIREMENTS DASHBOARD
    # ========================================================

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


        total_requirements = len(
            project_requirements
        )


        pending_requirements = (
            project_requirements[
                "status"
            ]
            .eq(
                "Pending"
            )
            .sum()
        )


        metric_1, metric_2 = (
            st.columns(2)
        )


        metric_1.metric(
            "Project Requirements",
            total_requirements,
        )


        metric_2.metric(
            "Pending Review",
            int(
                pending_requirements
            ),
        )


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
        Complete the guided project questions below. The
        application converts the answers into a standard
        requirements table. When committed, the complete table
        is saved as a locked project revision.
        """
    )


    st.info(
        """
        The first committed revision for a project is
        **Revision 00**. Each later revision starts using the
        values from the latest locked revision.
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
    # COMPACT REVISION HISTORY
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


        st.write(
            (
                "The table below shows each locked revision "
                "and the question IDs changed from the "
                "previous revision."
            )
        )


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
            f"The answers below will create "
            f"Revision **{next_revision_number}** "
            f"for project **{standard_project}**."
        )
    )


    # --------------------------------------------------------
    # PROJECT INFORMATION
    # --------------------------------------------------------

    with st.expander(
        "Project Information",
        expanded=True,
    ):


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
                f"std_customer_"
                f"{standard_project}"
            ),
        )


        product_options = [
            "MK1",
            "MK2",
            "MK3",
            "Other",
        ]


        saved_product = get_text_value(
            latest_standard_values,
            "STD-003",
            "MK3",
        )


        product_variant = st.selectbox(
            "ISV product variant *",
            options=product_options,
            index=selectbox_index(
                product_options,
                saved_product,
                2,
            ),
            key=(
                f"std_variant_"
                f"{standard_project}"
            ),
        )


    # --------------------------------------------------------
    # MECHANICAL REQUIREMENTS
    # --------------------------------------------------------

    with st.expander(
        "Mechanical Requirements",
        expanded=True,
    ):


        mechanical_column_1, mechanical_column_2 = (
            st.columns(2)
        )


        with mechanical_column_1:


            number_of_spray_zones = (
                st.number_input(
                    "Number of spray zones *",
                    min_value=1,
                    step=1,
                    value=max(
                        1,
                        get_integer_value(
                            latest_standard_values,
                            "STD-004",
                            64,
                        ),
                    ),
                    key=(
                        f"std_zones_"
                        f"{standard_project}"
                    ),
                )
            )


            spraybar_length = st.number_input(
                "Spraybar overall length *",
                min_value=0.0,
                step=10.0,
                value=get_float_value(
                    latest_standard_values,
                    "STD-005",
                    0.0,
                ),
                help="Value in millimetres.",
                key=(
                    f"std_length_"
                    f"{standard_project}"
                ),
            )


        with mechanical_column_2:


            zone_pitch = st.number_input(
                "Zone pitch *",
                min_value=0.0,
                step=1.0,
                value=get_float_value(
                    latest_standard_values,
                    "STD-006",
                    0.0,
                ),
                help="Value in millimetres.",
                key=(
                    f"std_pitch_"
                    f"{standard_project}"
                ),
            )


    # --------------------------------------------------------
    # FLUID REQUIREMENTS
    # --------------------------------------------------------

    with st.expander(
        "Fluid Requirements",
        expanded=True,
    ):


        fluid_column_1, fluid_column_2 = (
            st.columns(2)
        )


        fluid_options = [
            "Water",
            "Water / oil emulsion",
            "Rolling oil",
            "Other",
        ]


        saved_fluid = get_text_value(
            latest_standard_values,
            "STD-007",
            "Water",
        )


        with fluid_column_1:


            operating_fluid = st.selectbox(
                "Operating fluid *",
                options=fluid_options,
                index=selectbox_index(
                    fluid_options,
                    saved_fluid,
                    0,
                ),
                key=(
                    f"std_fluid_"
                    f"{standard_project}"
                ),
            )


            maximum_pressure = (
                st.number_input(
                    (
                        "Maximum operating "
                        "pressure *"
                    ),
                    min_value=0.0,
                    step=0.5,
                    value=get_float_value(
                        latest_standard_values,
                        "STD-008",
                        0.0,
                    ),
                    help="Value in bar.",
                    key=(
                        f"std_pressure_"
                        f"{standard_project}"
                    ),
                )
            )


        with fluid_column_2:


            minimum_flow_rate = (
                st.number_input(
                    "Minimum flow rate *",
                    min_value=0.0,
                    step=1.0,
                    value=get_float_value(
                        latest_standard_values,
                        "STD-009",
                        0.0,
                    ),
                    help=(
                        "Value in litres per minute."
                    ),
                    key=(
                        f"std_flow_"
                        f"{standard_project}"
                    ),
                )
            )


    # --------------------------------------------------------
    # ELECTRICAL AND CONTROLS
    # --------------------------------------------------------

    with st.expander(
        "Electrical and Control Requirements",
        expanded=True,
    ):


        electrical_column_1, electrical_column_2 = (
            st.columns(2)
        )


        with electrical_column_1:


            solenoid_voltage = (
                st.number_input(
                    "Solenoid valve voltage *",
                    min_value=0.0,
                    step=1.0,
                    value=get_float_value(
                        latest_standard_values,
                        "STD-010",
                        24.0,
                    ),
                    help="Value in volts.",
                    key=(
                        f"std_voltage_"
                        f"{standard_project}"
                    ),
                )
            )


        control_options = [
            "Digital outputs",
            "PLC interface",
            "Remote I/O",
            "Fieldbus",
            "Other",
        ]


        saved_control = get_text_value(
            latest_standard_values,
            "STD-011",
            "Digital outputs",
        )


        with electrical_column_2:


            control_interface = (
                st.selectbox(
                    "Control interface type *",
                    options=control_options,
                    index=selectbox_index(
                        control_options,
                        saved_control,
                        0,
                    ),
                    key=(
                        f"std_control_"
                        f"{standard_project}"
                    ),
                )
            )


    # --------------------------------------------------------
    # INSTALLATION REQUIREMENTS
    # --------------------------------------------------------

    with st.expander(
        "Installation Requirements",
        expanded=True,
    ):


        installation_options = [
            "Operator side",
            "Drive side",
            "Both sides",
            "To be confirmed",
        ]


        saved_installation = get_text_value(
            latest_standard_values,
            "STD-012",
            "To be confirmed",
        )


        installation_side = (
            st.selectbox(
                "Installation side *",
                options=installation_options,
                index=selectbox_index(
                    installation_options,
                    saved_installation,
                    3,
                ),
                key=(
                    f"std_installation_"
                    f"{standard_project}"
                ),
            )
        )


    # --------------------------------------------------------
    # ENVIRONMENTAL REQUIREMENTS
    # --------------------------------------------------------

    with st.expander(
        "Environmental Requirements",
        expanded=True,
    ):


        environment_column_1, environment_column_2 = (
            st.columns(2)
        )


        temperature_range = get_text_value(
            latest_standard_values,
            "STD-013",
            "",
        )


        saved_minimum_temperature = 0.0

        saved_maximum_temperature = 0.0


        if " to " in temperature_range:


            temperature_parts = (
                temperature_range.split(
                    " to "
                )
            )


            try:

                saved_minimum_temperature = float(
                    temperature_parts[0]
                )

                saved_maximum_temperature = float(
                    temperature_parts[1]
                )

            except (
                ValueError,
                IndexError,
            ):

                pass


        with environment_column_1:


            minimum_temperature = (
                st.number_input(
                    (
                        "Minimum ambient "
                        "temperature *"
                    ),
                    step=1.0,
                    value=(
                        saved_minimum_temperature
                    ),
                    help="Value in °C.",
                    key=(
                        f"std_min_temp_"
                        f"{standard_project}"
                    ),
                )
            )


        with environment_column_2:


            maximum_temperature = (
                st.number_input(
                    (
                        "Maximum ambient "
                        "temperature *"
                    ),
                    step=1.0,
                    value=(
                        saved_maximum_temperature
                    ),
                    help="Value in °C.",
                    key=(
                        f"std_max_temp_"
                        f"{standard_project}"
                    ),
                )
            )


    # --------------------------------------------------------
    # DOCUMENTATION REQUIREMENTS
    # --------------------------------------------------------

    with st.expander(
        "Documentation Requirements",
        expanded=True,
    ):


        document_column_1, document_column_2 = (
            st.columns(2)
        )


        yes_no_options = [
            "Yes",
            "No",
        ]


        saved_approval = get_text_value(
            latest_standard_values,
            "STD-014",
            "Yes",
        )


        saved_manufacturing = (
            get_text_value(
                latest_standard_values,
                "STD-015",
                "Yes",
            )
        )


        with document_column_1:


            approval_drawing_required = (
                st.selectbox(
                    (
                        "Customer approval "
                        "drawing required? *"
                    ),
                    options=yes_no_options,
                    index=selectbox_index(
                        yes_no_options,
                        saved_approval,
                        0,
                    ),
                    key=(
                        f"std_approval_"
                        f"{standard_project}"
                    ),
                )
            )


        with document_column_2:


            manufacturing_drawings_required = (
                st.selectbox(
                    (
                        "Manufacturing drawings "
                        "required? *"
                    ),
                    options=yes_no_options,
                    index=selectbox_index(
                        yes_no_options,
                        saved_manufacturing,
                        0,
                    ),
                    key=(
                        f"std_manufacturing_"
                        f"{standard_project}"
                    ),
                )
            )


    # ========================================================
    # GENERATE STANDARD REQUIREMENTS TABLE
    # ========================================================

    generated_standard_requirements = (
        build_standard_requirement_table(
            project_name=(
                standard_project
            ),
            customer_name=(
                customer_name.strip()
            ),
            product_variant=(
                product_variant
            ),
            number_of_spray_zones=(
                number_of_spray_zones
            ),
            spraybar_length=(
                spraybar_length
            ),
            zone_pitch=(
                zone_pitch
            ),
            operating_fluid=(
                operating_fluid
            ),
            maximum_pressure=(
                maximum_pressure
            ),
            minimum_flow_rate=(
                minimum_flow_rate
            ),
            solenoid_voltage=(
                solenoid_voltage
            ),
            control_interface=(
                control_interface
            ),
            installation_side=(
                installation_side
            ),
            minimum_temperature=(
                minimum_temperature
            ),
            maximum_temperature=(
                maximum_temperature
            ),
            approval_drawing_required=(
                approval_drawing_required
            ),
            manufacturing_drawings_required=(
                manufacturing_drawings_required
            ),
        )
    )


    # ========================================================
    # SECTION 4
    # REVIEW GENERATED TABLE
    # ========================================================

    st.divider()


    st.subheader(
        "4. Review Generated Standard Requirements"
    )


    st.write(
        """
        This table has been generated automatically from the
        answers in Section 3. It is read-only.
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
                f"std_committed_by_"
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
                f"std_revision_comment_"
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


    commit_revision_button = st.button(
        (
            f"Commit Locked Revision "
            f"{next_revision_number}"
        ),
        type="primary",
        use_container_width=True,
        key=(
            f"commit_standard_revision_"
            f"{standard_project}"
        ),
    )


    if commit_revision_button:


        commit_errors = []


        if not customer_name.strip():

            commit_errors.append(
                "Customer name"
            )


        if not committed_by.strip():

            commit_errors.append(
                "Committed by"
            )


        if spraybar_length <= 0:

            commit_errors.append(
                "Spraybar overall length"
            )


        if zone_pitch <= 0:

            commit_errors.append(
                "Zone pitch"
            )


        if maximum_pressure <= 0:

            commit_errors.append(
                "Maximum operating pressure"
            )


        if minimum_flow_rate <= 0:

            commit_errors.append(
                "Minimum flow rate"
            )


        if maximum_temperature <= minimum_temperature:

            commit_errors.append(
                (
                    "Maximum ambient temperature "
                    "must be greater than the minimum"
                )
            )


        if commit_errors:


            st.error(
                (
                    "The revision cannot be committed. "
                    "Please complete or correct: "
                    +
                    ", ".join(
                        commit_errors
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
                        "because this revision number already "
                        "exists. Refresh the page and try again."
                    )
                )