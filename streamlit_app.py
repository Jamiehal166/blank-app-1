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


REQUIREMENT_CATEGORIES = [
    "Operating condition",
    "Capacity or quantity",
    "Performance level",
    "Response time",
    "Compatibility or interface",
    "Product type or standard",
    "Reliability or maintenance",
    "Other requirement",
]


STANDARD_REQUIREMENT_TEMPLATE = [
    {
        "Requirement ID": "STD-001",
        "Requirement Area": "Project Definition",
        "Requirement": "Project number",
        "Required Value": "",
        "Unit / Limit": "",
        "Verification Method": "Document review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-002",
        "Requirement Area": "Project Definition",
        "Requirement": "Customer name",
        "Required Value": "",
        "Unit / Limit": "",
        "Verification Method": "Document review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-003",
        "Requirement Area": "Product Configuration",
        "Requirement": "ISV product variant",
        "Required Value": "",
        "Unit / Limit": "",
        "Verification Method": "Design review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-004",
        "Requirement Area": "Mechanical",
        "Requirement": "Number of spray zones",
        "Required Value": "",
        "Unit / Limit": "zones",
        "Verification Method": "Drawing review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-005",
        "Requirement Area": "Mechanical",
        "Requirement": "Spraybar overall length",
        "Required Value": "",
        "Unit / Limit": "mm",
        "Verification Method": "Drawing review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-006",
        "Requirement Area": "Mechanical",
        "Requirement": "Zone pitch",
        "Required Value": "",
        "Unit / Limit": "mm",
        "Verification Method": "Drawing review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-007",
        "Requirement Area": "Fluid",
        "Requirement": "Operating fluid",
        "Required Value": "",
        "Unit / Limit": "",
        "Verification Method": "Document review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-008",
        "Requirement Area": "Fluid",
        "Requirement": "Maximum operating pressure",
        "Required Value": "",
        "Unit / Limit": "bar",
        "Verification Method": "Design review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-009",
        "Requirement Area": "Fluid",
        "Requirement": "Minimum flow rate",
        "Required Value": "",
        "Unit / Limit": "litres per minute",
        "Verification Method": "Calculation / design review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-010",
        "Requirement Area": "Electrical",
        "Requirement": "Solenoid valve voltage",
        "Required Value": "",
        "Unit / Limit": "V",
        "Verification Method": "Document review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-011",
        "Requirement Area": "Controls",
        "Requirement": "Control interface type",
        "Required Value": "",
        "Unit / Limit": "",
        "Verification Method": "Design review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-012",
        "Requirement Area": "Installation",
        "Requirement": "Installation side",
        "Required Value": "",
        "Unit / Limit": "",
        "Verification Method": "Drawing review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-013",
        "Requirement Area": "Environment",
        "Requirement": "Ambient operating temperature range",
        "Required Value": "",
        "Unit / Limit": "°C",
        "Verification Method": "Document review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-014",
        "Requirement Area": "Documentation",
        "Requirement": "Customer approval drawing required",
        "Required Value": "",
        "Unit / Limit": "Yes / No",
        "Verification Method": "Document review",
        "Notes": "",
    },
    {
        "Requirement ID": "STD-015",
        "Requirement Area": "Documentation",
        "Requirement": "Manufacturing drawing required",
        "Required Value": "",
        "Unit / Limit": "Yes / No",
        "Verification Method": "Document review",
        "Notes": "",
    },
]


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_database_connection():
    return sqlite3.connect(DATABASE_FILE)


def get_existing_columns(connection, table_name):
    table_information = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [
        column[1]
        for column in table_information
    ]


def table_exists(connection, table_name):
    result = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return result is not None


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
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Pending",
            requirement_category,
            stakeholder_input,
        ),
    )

    connection.commit()
    connection.close()


def load_project_requirements():
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
# STANDARD REQUIREMENT FUNCTIONS
# ============================================================

def load_standard_revisions(project_name):
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
        ORDER BY revision_number DESC
        """,
        connection,
        params=(project_name,),
    )

    connection.close()

    return revisions


def load_standard_revision_items(revision_id):
    connection = get_database_connection()

    items = pd.read_sql_query(
        """
        SELECT
            requirement_id AS "Requirement ID",
            requirement_area AS "Requirement Area",
            requirement_text AS "Requirement",
            required_value AS "Required Value",
            unit_or_limit AS "Unit / Limit",
            verification_method AS "Verification Method",
            notes AS "Notes"
        FROM standard_requirement_items
        WHERE revision_id = ?
        ORDER BY requirement_id ASC
        """,
        connection,
        params=(revision_id,),
    )

    connection.close()

    return items


def get_next_standard_revision_number(project_name):
    revisions = load_standard_revisions(project_name)

    if revisions.empty:
        return "00"

    latest_revision_number = (
        revisions["revision_number"]
        .astype(int)
        .max()
    )

    return f"{latest_revision_number + 1:02d}"


def get_latest_standard_revision_id(project_name):
    revisions = load_standard_revisions(project_name)

    if revisions.empty:
        return None

    latest_revision = revisions.sort_values(
        "revision_number",
        ascending=False,
    ).iloc[0]

    return int(latest_revision["id"])


def get_standard_revision_starting_data(project_name):
    latest_revision_id = get_latest_standard_revision_id(
        project_name
    )

    if latest_revision_id is None:
        return pd.DataFrame(STANDARD_REQUIREMENT_TEMPLATE)

    latest_items = load_standard_revision_items(
        latest_revision_id
    )

    if latest_items.empty:
        return pd.DataFrame(STANDARD_REQUIREMENT_TEMPLATE)

    return latest_items


def commit_standard_requirement_revision(
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
            datetime.now().strftime("%Y-%m-%d %H:%M"),
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
                str(row["Requirement ID"]).strip(),
                str(row["Requirement Area"]).strip(),
                str(row["Requirement"]).strip(),
                str(row["Required Value"]).strip(),
                str(row["Unit / Limit"]).strip(),
                str(row["Verification Method"]).strip(),
                str(row["Notes"]).strip(),
                "Yes",
            ),
        )

    connection.commit()
    connection.close()


# ============================================================
# SMALL HELPER FUNCTIONS
# ============================================================

def is_complete_text(value):
    return bool(str(value).strip())


def clean_dataframe_text(dataframe):
    cleaned_dataframe = dataframe.copy()

    for column in cleaned_dataframe.columns:
        cleaned_dataframe[column] = (
            cleaned_dataframe[column]
            .fillna("")
            .astype(str)
        )

    return cleaned_dataframe


# ============================================================
# INITIALISE DATABASE
# ============================================================

create_or_update_database()


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📋 ISV Requirements Management")

st.write(
    """
    Capture project-specific stakeholder requirements and standard
    project requirements in a structured, traceable format.
    """
)


# ============================================================
# APPLICATION TABS
# ============================================================

project_specific_tab, standard_requirements_tab = st.tabs(
    [
        "Project-Specific Requirements",
        "Standard Requirements",
    ]
)


# ============================================================
# PROJECT-SPECIFIC REQUIREMENTS TAB
# ============================================================

with project_specific_tab:

    st.header("Project-Specific Requirement Capture")

    st.write(
        """
        Select the type of requirement you want to add and answer
        the questions shown. The complete requirement will be
        generated automatically.
        """
    )

    st.info(
        """
        You do not need systems-engineering experience to use
        this form. New requirements are submitted with a
        status of **Pending** for project-owner review.
        """
    )

    st.subheader("1. Requirement Details")

    information_column_1, information_column_2 = st.columns(2)

    with information_column_1:

        selected_project = st.selectbox(
            "Project *",
            options=ALLOWED_PROJECTS,
            help="Select the project to which this requirement applies.",
            key="project_specific_project",
        )

        requirement_title = st.text_input(
            "Requirement title *",
            placeholder="Example: Ambient operating temperature",
            help="Enter a short title that makes the requirement easy to identify.",
        )

    with information_column_2:

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
        )

        submitted_by = st.text_input(
            "Submitted by *",
            placeholder="Enter your name",
        )

    st.divider()

    st.subheader("2. What Type of Requirement Is This?")

    selected_requirement_category = st.selectbox(
        "Requirement type *",
        options=REQUIREMENT_CATEGORIES,
        help="Select the option that most closely describes what is needed.",
    )

    category_descriptions = {
        "Operating condition":
            "Use this when equipment must operate under a particular environmental or operating condition.",
        "Capacity or quantity":
            "Use this when a minimum quantity, capacity, or number of items is required.",
        "Performance level":
            "Use this when a minimum output, rate, pressure, flow, speed, or other performance value is required.",
        "Response time":
            "Use this when an action must happen within a specified time after an event.",
        "Compatibility or interface":
            "Use this when the ISV must connect to or operate with another system.",
        "Product type or standard":
            "Use this when a particular type, grade, standard, material, or specification is required.",
        "Reliability or maintenance":
            "Use this when equipment must operate for a defined period or meet a maintenance requirement.",
        "Other requirement":
            "Use this when the requirement does not fit one of the predefined categories.",
    }

    st.caption(
        category_descriptions[selected_requirement_category]
    )

    st.divider()

    st.subheader("3. Tell Us What Is Needed")

    generated_requirement = ""
    requirement_preview = ""
    stakeholder_input = ""
    required_inputs_complete = False
    database_category = "Other"

    if selected_requirement_category == "Operating condition":

        database_category = "Environmental"

        st.write(
            """
            Example: The ISV spraybar shall operate continuously
            at an ambient temperature between 5°C and 45°C.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="operating_equipment",
            )

            required_action = st.text_input(
                "What must it do? *",
                placeholder="Example: operate continuously",
                key="operating_action",
            )

        with column_2:
            operating_condition = st.text_area(
                "Under what condition must it operate? *",
                placeholder="Example: at an ambient temperature between 5°C and 45°C",
                height=125,
                key="operating_condition",
            )

        required_inputs_complete = all(
            [
                equipment_name.strip(),
                required_action.strip(),
                operating_condition.strip(),
            ]
        )

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        action_preview = required_action.strip() or "[required action]"
        condition_preview = operating_condition.strip() or "[operating condition]"

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
            f"Required action: {required_action.strip()}\n"
            f"Operating condition: {operating_condition.strip()}"
        )

    elif selected_requirement_category == "Capacity or quantity":

        database_category = "Capacity"

        st.write(
            """
            Example: The ISV spraybar shall control a minimum
            of 64 spray zones.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="capacity_equipment",
            )

            required_action = st.text_input(
                "What must it do? *",
                placeholder="Example: control",
                key="capacity_action",
            )

        with column_2:
            minimum_quantity = st.number_input(
                "What is the minimum quantity required? *",
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

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        action_preview = required_action.strip() or "[required action]"
        quantity_preview = str(minimum_quantity) if minimum_quantity > 0 else "[minimum quantity]"
        item_preview = item_name.strip() or "[item being counted]"

        requirement_preview = (
            f"The {equipment_preview} shall "
            f"{action_preview} "
            f"a minimum of {quantity_preview} "
            f"{item_preview}."
        )

        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"a minimum of {minimum_quantity} "
            f"{item_name.strip()}."
        )

        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Required action: {required_action.strip()}\n"
            f"Minimum quantity: {minimum_quantity}\n"
            f"Item: {item_name.strip()}"
        )

    elif selected_requirement_category == "Performance level":

        database_category = "Performance"

        st.write(
            """
            Example: The ISV spraybar shall deliver cooling fluid
            at a minimum rate of 120 litres per minute.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="performance_equipment",
            )

            required_action = st.text_input(
                "What must it do? *",
                placeholder="Example: deliver cooling fluid",
                key="performance_action",
            )

        with column_2:
            required_value = st.number_input(
                "What is the minimum required value? *",
                min_value=0.0,
                step=1.0,
                key="performance_value",
            )

            engineering_unit = st.text_input(
                "What unit is used? *",
                placeholder="Example: litres per minute",
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

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        action_preview = required_action.strip() or "[required action]"
        value_preview = f"{required_value:g}" if required_value > 0 else "[minimum value]"
        unit_preview = engineering_unit.strip() or "[engineering unit]"

        requirement_preview = (
            f"The {equipment_preview} shall "
            f"{action_preview} "
            f"at a minimum value of {value_preview} "
            f"{unit_preview}."
        )

        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"at a minimum value of {required_value:g} "
            f"{engineering_unit.strip()}."
        )

        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Required action: {required_action.strip()}\n"
            f"Minimum value: {required_value:g}\n"
            f"Unit: {engineering_unit.strip()}"
        )

    elif selected_requirement_category == "Response time":

        database_category = "Performance"

        st.write(
            """
            Example: The ISV spraybar shall begin coolant delivery
            within 2 seconds of receiving a control signal.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="response_equipment",
            )

            required_action = st.text_input(
                "What action must happen? *",
                placeholder="Example: begin coolant delivery",
                key="response_action",
            )

            trigger_event = st.text_input(
                "What triggers the action? *",
                placeholder="Example: receiving a control signal",
                key="response_trigger",
            )

        with column_2:
            maximum_time = st.number_input(
                "What is the maximum permitted time? *",
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

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        action_preview = required_action.strip() or "[required action]"
        time_preview = f"{maximum_time:g}" if maximum_time > 0 else "[maximum time]"
        trigger_preview = trigger_event.strip() or "[triggering event]"

        requirement_preview = (
            f"The {equipment_preview} shall "
            f"{action_preview} "
            f"within {time_preview} "
            f"{time_unit} of {trigger_preview}."
        )

        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"within {maximum_time:g} "
            f"{time_unit} of {trigger_event.strip()}."
        )

        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Required action: {required_action.strip()}\n"
            f"Trigger event: {trigger_event.strip()}\n"
            f"Maximum response time: {maximum_time:g} {time_unit}"
        )

    elif selected_requirement_category == "Compatibility or interface":

        database_category = "Interface"

        st.write(
            """
            Example: The ISV spraybar shall interface with the
            mill control system using a minimum of 64 digital outputs.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="interface_equipment",
            )

            external_system = st.text_input(
                "What other equipment must it connect to? *",
                placeholder="Example: mill control system",
                key="interface_external_system",
            )

        with column_2:
            interface_description = st.text_input(
                "What connection or interface is required? *",
                placeholder="Example: a minimum of 64 digital outputs",
                key="interface_description",
            )

        required_inputs_complete = all(
            [
                equipment_name.strip(),
                external_system.strip(),
                interface_description.strip(),
            ]
        )

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        external_preview = external_system.strip() or "[external equipment or system]"
        interface_preview = interface_description.strip() or "[required connection or interface]"

        requirement_preview = (
            f"The {equipment_preview} shall "
            f"interface with the {external_preview} "
            f"using {interface_preview}."
        )

        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"interface with the {external_system.strip()} "
            f"using {interface_description.strip()}."
        )

        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"External equipment: {external_system.strip()}\n"
            f"Required interface: {interface_description.strip()}"
        )

    elif selected_requirement_category == "Product type or standard":

        database_category = "Specification"

        st.write(
            """
            Example: The ISV spraybar shall use ISO VG 32
            cooling fluid at a maximum operating pressure of 10 bar.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="standard_equipment",
            )

            specified_item = st.text_input(
                "What item is being specified? *",
                placeholder="Example: cooling fluid",
                key="standard_item",
            )

        with column_2:
            required_standard = st.text_input(
                "What type, grade, or standard is required? *",
                placeholder="Example: ISO VG 32",
                key="standard_grade",
            )

            operating_limit = st.text_input(
                "Are there any operating limits?",
                placeholder="Example: at a maximum operating pressure of 10 bar",
                key="standard_limit",
            )

        required_inputs_complete = all(
            [
                equipment_name.strip(),
                specified_item.strip(),
                required_standard.strip(),
            ]
        )

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        standard_preview = required_standard.strip() or "[required type, grade, or standard]"
        item_preview = specified_item.strip() or "[specified item]"
        limit_preview = operating_limit.strip() or "[optional operating limit]"

        requirement_preview = (
            f"The {equipment_preview} shall use "
            f"{standard_preview} "
            f"{item_preview} "
            f"{limit_preview}."
        )

        generated_requirement = (
            f"The {equipment_name.strip()} shall use "
            f"{required_standard.strip()} "
            f"{specified_item.strip()}"
        )

        if operating_limit.strip():
            generated_requirement += f" {operating_limit.strip()}"

        generated_requirement += "."

        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Specified item: {specified_item.strip()}\n"
            f"Required type, grade, or standard: {required_standard.strip()}\n"
            f"Operating limit: {operating_limit.strip()}"
        )

    elif selected_requirement_category == "Reliability or maintenance":

        database_category = "Maintenance"

        st.write(
            """
            Example: The ISV spraybar shall operate for a minimum
            of 8,000 operating hours without planned maintenance.
            """
        )

        column_1, column_2 = st.columns(2)

        with column_1:
            equipment_name = st.text_input(
                "What equipment or system does this apply to? *",
                value="ISV spraybar",
                key="reliability_equipment",
            )

            required_action = st.text_input(
                "What must continue operating? *",
                placeholder="Example: operate",
                key="reliability_action",
            )

        with column_2:
            minimum_duration = st.number_input(
                "What is the minimum required duration? *",
                min_value=0.0,
                step=100.0,
                key="reliability_duration",
            )

            duration_unit = st.text_input(
                "What unit is used? *",
                placeholder="Example: operating hours",
                key="reliability_unit",
            )

            maintenance_condition = st.text_input(
                "What maintenance limitation applies?",
                placeholder="Example: without planned maintenance",
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

        equipment_preview = equipment_name.strip() or "[equipment or system]"
        action_preview = required_action.strip() or "[required action]"
        duration_preview = f"{minimum_duration:g}" if minimum_duration > 0 else "[minimum duration]"
        unit_preview = duration_unit.strip() or "[duration unit]"
        maintenance_preview = maintenance_condition.strip() or "[optional maintenance condition]"

        requirement_preview = (
            f"The {equipment_preview} shall "
            f"{action_preview} "
            f"for a minimum of {duration_preview} "
            f"{unit_preview} "
            f"{maintenance_preview}."
        )

        generated_requirement = (
            f"The {equipment_name.strip()} shall "
            f"{required_action.strip()} "
            f"for a minimum of {minimum_duration:g} "
            f"{duration_unit.strip()}"
        )

        if maintenance_condition.strip():
            generated_requirement += f" {maintenance_condition.strip()}"

        generated_requirement += "."

        stakeholder_input = (
            f"Equipment: {equipment_name.strip()}\n"
            f"Required action: {required_action.strip()}\n"
            f"Minimum duration: {minimum_duration:g} {duration_unit.strip()}\n"
            f"Maintenance condition: {maintenance_condition.strip()}"
        )

    elif selected_requirement_category == "Other requirement":

        database_category = "Other"

        st.write(
            """
            Describe the requirement in your own words.
            The project owner can refine the wording during review.
            """
        )

        stakeholder_description = st.text_area(
            "Describe what is needed *",
            placeholder="Example: The spraybar must be accessible from the operator side for maintenance.",
            height=150,
            key="other_description",
        )

        required_inputs_complete = bool(
            stakeholder_description.strip()
        )

        requirement_preview = (
            stakeholder_description.strip()
            if stakeholder_description.strip()
            else "[Describe the requirement in your own words]"
        )

        generated_requirement = stakeholder_description.strip()
        stakeholder_input = stakeholder_description.strip()

    st.divider()

    st.subheader("4. Live Requirement Preview")

    st.write(
        """
        The requirement below updates as you complete the
        questions in Section 3.
        """
    )

    st.code(
        requirement_preview,
        language=None,
    )

    if required_inputs_complete:
        st.success(
            "The requirement is complete and ready to submit."
        )
    else:
        st.info(
            """
            Fields shown in square brackets still need to be
            completed.
            """
        )

    st.divider()

    st.subheader("5. Submit for Project-Owner Review")

    save_requirement_button = st.button(
        "Submit Requirement",
        type="primary",
        use_container_width=True,
    )

    if save_requirement_button:

        missing_information = []

        if not requirement_title.strip():
            missing_information.append("Requirement title")

        if not submitted_by.strip():
            missing_information.append("Submitted by")

        if not required_inputs_complete:
            missing_information.append("All required questions")

        if missing_information:
            st.error(
                "Please complete: "
                + ", ".join(missing_information)
            )
        else:
            save_project_requirement(
                project_name=selected_project,
                requirement_title=requirement_title.strip(),
                requirement_text=generated_requirement,
                category=database_category,
                source_department=source_department,
                submitted_by=submitted_by.strip(),
                requirement_category=selected_requirement_category,
                stakeholder_input=stakeholder_input,
            )

            st.success(
                """
                Requirement submitted successfully.

                Its review status has been set to **Pending**.
                """
            )

    project_requirements = load_project_requirements()

    st.divider()

    st.header("Project Requirements Dashboard")

    if project_requirements.empty:

        st.info(
            """
            No project-specific requirements have
            been submitted.
            """
        )

    else:

        total_requirements = len(project_requirements)

        pending_requirements = (
            project_requirements["status"]
            .eq("Pending")
            .sum()
        )

        number_of_projects = (
            project_requirements["project_name"]
            .nunique()
        )

        number_of_sources = (
            project_requirements["source_department"]
            .nunique()
        )

        metric_1, metric_2, metric_3, metric_4 = st.columns(4)

        metric_1.metric(
            "Project Requirements",
            total_requirements,
        )

        metric_2.metric(
            "Pending Review",
            int(pending_requirements),
        )

        metric_3.metric(
            "Projects",
            number_of_projects,
        )

        metric_4.metric(
            "Stakeholder Sources",
            number_of_sources,
        )

        st.subheader("Search and Filter Requirements")

        filter_column_1, filter_column_2, filter_column_3 = st.columns(3)

        with filter_column_1:
            search_text = st.text_input(
                "Search requirements",
                placeholder="Search title or requirement text",
                key="requirement_search",
            )

        with filter_column_2:
            project_filter = st.selectbox(
                "Filter by project",
                options=["All Projects"] + ALLOWED_PROJECTS,
                key="project_filter",
            )

        with filter_column_3:
            requirement_category_filter = st.selectbox(
                "Filter by requirement type",
                options=["All Types"] + REQUIREMENT_CATEGORIES,
                key="requirement_category_filter",
            )

        filtered_requirements = project_requirements.copy()

        if search_text.strip():

            search_value = search_text.strip().lower()

            search_matches = (
                filtered_requirements["requirement_title"]
                .str.lower()
                .str.contains(
                    search_value,
                    na=False,
                    regex=False,
                )
                |
                filtered_requirements["requirement_text"]
                .str.lower()
                .str.contains(
                    search_value,
                    na=False,
                    regex=False,
                )
            )

            filtered_requirements = filtered_requirements[
                search_matches
            ]

        if project_filter != "All Projects":

            filtered_requirements = filtered_requirements[
                filtered_requirements["project_name"]
                == project_filter
            ]

        if requirement_category_filter != "All Types":

            filtered_requirements = filtered_requirements[
                filtered_requirements["boilerplate_name"]
                == requirement_category_filter
            ]

        st.subheader("Saved Project Requirements")

        st.caption(
            f"Showing {len(filtered_requirements)} "
            f"of {len(project_requirements)} "
            f"project requirements."
        )

        display_requirements = filtered_requirements.rename(
            columns={
                "id": "ID",
                "project_name": "Project",
                "requirement_title": "Title",
                "requirement_text": "Generated Requirement",
                "category": "Internal Category",
                "source_department": "Source",
                "submitted_by": "Submitted By",
                "date_submitted": "Date Submitted",
                "status": "Status",
                "boilerplate_name": "Requirement Type",
                "stakeholder_input": "Original Stakeholder Input",
            }
        )

        st.dataframe(
            display_requirements,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID",
                    format="REQ-%04d",
                ),
                "Generated Requirement": st.column_config.TextColumn(
                    "Generated Requirement",
                    width="large",
                ),
                "Original Stakeholder Input": st.column_config.TextColumn(
                    "Original Stakeholder Input",
                    width="large",
                ),
                "Requirement Type": st.column_config.TextColumn(
                    "Requirement Type",
                    width="medium",
                ),
            },
        )


# ============================================================
# STANDARD REQUIREMENTS TAB
# ============================================================

with standard_requirements_tab:

    st.header("Standard Product Requirements")

    st.write(
        """
        Use this page to define the standard requirement set for
        a specific project. Once committed, the requirement set is
        saved as a locked revision.
        """
    )

    st.info(
        """
        The first committed standard requirements set for each
        project will be saved as **Revision 00**. Locked revisions
        are retained as project records and cannot be edited.
        """
    )

    st.subheader("1. Select Project")

    standard_project = st.selectbox(
        "Project *",
        options=ALLOWED_PROJECTS,
        key="standard_project",
    )

    standard_revisions = load_standard_revisions(
        standard_project
    )

    next_revision_number = get_next_standard_revision_number(
        standard_project
    )

    st.divider()

    st.subheader("2. Existing Locked Revisions")

    if standard_revisions.empty:

        st.info(
            f"No standard requirement revisions have been committed for {standard_project}."
        )

    else:

        st.write(
            f"Locked revisions already committed for **{standard_project}**:"
        )

        revision_summary = standard_revisions.rename(
            columns={
                "revision_number": "Revision",
                "committed_by": "Committed By",
                "committed_date": "Committed Date",
                "revision_status": "Status",
                "revision_comment": "Comment",
            }
        )

        st.dataframe(
            revision_summary[
                [
                    "Revision",
                    "Committed By",
                    "Committed Date",
                    "Status",
                    "Comment",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        selected_revision_number = st.selectbox(
            "View locked revision",
            options=standard_revisions["revision_number"].tolist(),
            key="view_standard_revision",
        )

        selected_revision_id = int(
            standard_revisions[
                standard_revisions["revision_number"]
                == selected_revision_number
            ]["id"].iloc[0]
        )

        selected_revision_items = load_standard_revision_items(
            selected_revision_id
        )

        st.write(
            f"Viewing locked standard requirements for **{standard_project}**, "
            f"Revision **{selected_revision_number}**."
        )

        st.dataframe(
            selected_revision_items,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("3. Create New Locked Revision")

    st.write(
        f"""
        Complete the standard requirement table below. When committed,
        it will be saved as locked Revision **{next_revision_number}**
        for project **{standard_project}**.
        """
    )

    if standard_revisions.empty:
        starting_standard_data = pd.DataFrame(
            STANDARD_REQUIREMENT_TEMPLATE
        )
    else:
        starting_standard_data = get_standard_revision_starting_data(
            standard_project
        )

    edited_standard_data = st.data_editor(
        starting_standard_data,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Requirement ID": st.column_config.TextColumn(
                "Requirement ID",
                help="Unique standard requirement reference.",
                required=True,
            ),
            "Requirement Area": st.column_config.SelectboxColumn(
                "Requirement Area",
                options=[
                    "Project Definition",
                    "Product Configuration",
                    "Mechanical",
                    "Fluid",
                    "Electrical",
                    "Controls",
                    "Installation",
                    "Environment",
                    "Documentation",
                    "Safety",
                    "Maintenance",
                    "Other",
                ],
                required=True,
            ),
            "Requirement": st.column_config.TextColumn(
                "Requirement",
                help="The standard requirement being defined.",
                required=True,
                width="large",
            ),
            "Required Value": st.column_config.TextColumn(
                "Required Value",
                help="The project-specific value for this requirement.",
            ),
            "Unit / Limit": st.column_config.TextColumn(
                "Unit / Limit",
                help="The unit, limit, or allowed value.",
            ),
            "Verification Method": st.column_config.SelectboxColumn(
                "Verification Method",
                options=[
                    "Document review",
                    "Drawing review",
                    "Design review",
                    "Calculation / design review",
                    "Inspection",
                    "Test",
                    "Not defined",
                ],
            ),
            "Notes": st.column_config.TextColumn(
                "Notes",
                width="medium",
            ),
        },
    )

    edited_standard_data = clean_dataframe_text(
        edited_standard_data
    )

    st.divider()

    st.subheader("4. Commit Locked Revision")

    commit_column_1, commit_column_2 = st.columns(2)

    with commit_column_1:
        standard_committed_by = st.text_input(
            "Committed by *",
            placeholder="Enter your name",
            key="standard_committed_by",
        )

    with commit_column_2:
        standard_revision_comment = st.text_input(
            "Revision comment",
            placeholder="Example: Initial standard requirements baseline",
            key="standard_revision_comment",
        )

    st.warning(
        f"""
        Committing will lock Revision **{next_revision_number}**
        for project **{standard_project}**. This revision will be
        stored as a project record and should not be edited later.
        """
    )

    commit_standard_revision_button = st.button(
        f"Commit Locked Revision {next_revision_number}",
        type="primary",
        use_container_width=True,
    )

    if commit_standard_revision_button:

        missing_commit_information = []

        if not standard_committed_by.strip():
            missing_commit_information.append("Committed by")

        required_columns = [
            "Requirement ID",
            "Requirement Area",
            "Requirement",
        ]

        for column in required_columns:
            if edited_standard_data[column].str.strip().eq("").any():
                missing_commit_information.append(
                    f"Blank values in '{column}'"
                )

        duplicate_requirement_ids = (
            edited_standard_data["Requirement ID"]
            .str.strip()
            .duplicated()
            .any()
        )

        if duplicate_requirement_ids:
            missing_commit_information.append(
                "Duplicate Requirement IDs"
            )

        if missing_commit_information:

            st.error(
                "The revision cannot be committed yet. Please resolve: "
                + ", ".join(sorted(set(missing_commit_information)))
            )

        else:

            try:
                commit_standard_requirement_revision(
                    project_name=standard_project,
                    revision_number=next_revision_number,
                    committed_by=standard_committed_by.strip(),
                    revision_comment=standard_revision_comment.strip(),
                    requirements_dataframe=edited_standard_data,
                )

                st.success(
                    f"""
                    Standard requirements committed successfully.

                    Project: **{standard_project}**

                    Locked revision: **{next_revision_number}**
                    """
                )

                st.rerun()

            except sqlite3.IntegrityError:

                st.error(
                    """
                    This revision could not be committed because a
                    revision with the same number already exists for
                    this project. Refresh the page and try again.
                    """
                )