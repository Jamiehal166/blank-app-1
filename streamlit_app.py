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


STANDARD_REQUIREMENT_CATEGORIES = [
    "General",
    "Mechanical",
    "Electrical",
    "Controls",
    "Hydraulic / Fluid",
    "Performance",
    "Environmental",
    "Interface",
    "Installation",
    "Manufacturing",
    "Maintenance",
    "Safety",
    "Documentation",
]


VERIFICATION_METHODS = [
    "Not assigned",
    "Drawing review",
    "Design review",
    "Calculation",
    "Inspection",
    "Simulation",
    "Testing",
    "Document review",
]


STANDARD_REQUIREMENT_COLUMNS = [
    "Requirement ID",
    "Category",
    "Requirement title",
    "Requirement statement",
    "Verification method",
    "Notes",
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_connection():
    """
    Open a connection to the SQLite database.

    row_factory allows database rows to be accessed
    using their column names.
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALISATION
# ============================================================

def get_existing_columns(
    connection,
    table_name,
):
    """
    Return the existing columns for a database table.
    """

    table_information = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [
        column["name"]
        for column in table_information
    ]


def create_or_update_database():
    """
    Create all tables required by the application.

    Existing project-specific requirements are preserved.
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


    existing_requirement_columns = (
        get_existing_columns(
            connection,
            "requirements",
        )
    )


    if (
        "boilerplate_name"
        not in existing_requirement_columns
    ):

        connection.execute(
            """
            ALTER TABLE requirements
            ADD COLUMN boilerplate_name TEXT
            """
        )


    if (
        "stakeholder_input"
        not in existing_requirement_columns
    ):

        connection.execute(
            """
            ALTER TABLE requirements
            ADD COLUMN stakeholder_input TEXT
            """
        )


    # --------------------------------------------------------
    # STANDARD REQUIREMENT DRAFTS
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS
        standard_requirement_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            row_order INTEGER NOT NULL,
            requirement_id TEXT,
            category TEXT,
            requirement_title TEXT,
            requirement_statement TEXT,
            verification_method TEXT,
            notes TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )


    # --------------------------------------------------------
    # STANDARD REQUIREMENT REVISION HEADERS
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS
        standard_requirement_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            revision_number INTEGER NOT NULL,
            committed_by TEXT NOT NULL,
            committed_at TEXT NOT NULL,
            revision_comment TEXT,
            is_locked INTEGER NOT NULL DEFAULT 1,
            UNIQUE (
                project_name,
                revision_number
            )
        )
        """
    )


    # --------------------------------------------------------
    # STANDARD REQUIREMENT REVISION ITEMS
    # --------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS
        standard_requirement_revision_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            revision_id INTEGER NOT NULL,
            row_order INTEGER NOT NULL,
            requirement_id TEXT NOT NULL,
            category TEXT NOT NULL,
            requirement_title TEXT NOT NULL,
            requirement_statement TEXT NOT NULL,
            verification_method TEXT,
            notes TEXT,
            FOREIGN KEY (
                revision_id
            )
            REFERENCES
            standard_requirement_revisions(id)
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
    Save a stakeholder-generated project requirement.
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
    Load project-specific requirements.
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
# STANDARD REQUIREMENT HELPER FUNCTIONS
# ============================================================

def create_empty_standard_requirements():
    """
    Create an initial empty standard-requirement table.

    Five blank rows are provided initially.
    Additional rows can be added in the data editor.
    """

    return pd.DataFrame(
        [
            {
                "Requirement ID": "",
                "Category": "General",
                "Requirement title": "",
                "Requirement statement": "",
                "Verification method": (
                    "Not assigned"
                ),
                "Notes": "",
            }
            for _ in range(5)
        ],
        columns=STANDARD_REQUIREMENT_COLUMNS,
    )


def normalise_standard_requirements(
    requirements_dataframe,
):
    """
    Ensure the standard requirements contain the
    expected columns and clean empty values.
    """

    dataframe = (
        requirements_dataframe.copy()
    )


    for column in STANDARD_REQUIREMENT_COLUMNS:

        if column not in dataframe.columns:

            dataframe[column] = ""


    dataframe = dataframe[
        STANDARD_REQUIREMENT_COLUMNS
    ]


    dataframe = dataframe.fillna("")


    for column in STANDARD_REQUIREMENT_COLUMNS:

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
        )


    return dataframe


def remove_completely_blank_rows(
    requirements_dataframe,
):
    """
    Remove rows which contain no meaningful requirement data.
    """

    dataframe = normalise_standard_requirements(
        requirements_dataframe
    )


    meaningful_columns = [
        "Requirement ID",
        "Requirement title",
        "Requirement statement",
    ]


    row_contains_information = (

        dataframe[
            meaningful_columns
        ]

        .apply(
            lambda row:
            any(
                str(value).strip()
                for value in row
            ),
            axis=1,
        )
    )


    return (
        dataframe[
            row_contains_information
        ]
        .reset_index(
            drop=True
        )
    )


def validate_standard_requirements(
    requirements_dataframe,
):
    """
    Validate requirements before they are committed.

    Returns a list of validation messages.
    """

    dataframe = remove_completely_blank_rows(
        requirements_dataframe
    )

    errors = []


    if dataframe.empty:

        errors.append(
            "At least one standard requirement "
            "must be entered."
        )

        return errors


    required_columns = [
        "Requirement ID",
        "Category",
        "Requirement title",
        "Requirement statement",
    ]


    for row_number, row in dataframe.iterrows():

        displayed_row_number = (
            row_number + 1
        )


        for column in required_columns:

            if not str(
                row[column]
            ).strip():

                errors.append(
                    f"Row {displayed_row_number}: "
                    f"{column} is required."
                )


    requirement_ids = (

        dataframe[
            "Requirement ID"
        ]

        .str.upper()

        .tolist()
    )


    duplicate_ids = {

        requirement_id

        for requirement_id
        in requirement_ids

        if requirement_ids.count(
            requirement_id
        ) > 1
    }


    if duplicate_ids:

        errors.append(
            "Requirement IDs must be unique. "
            "Duplicates found: "
            + ", ".join(
                sorted(
                    duplicate_ids
                )
            )
        )


    return errors


# ============================================================
# STANDARD REQUIREMENT DRAFT FUNCTIONS
# ============================================================

def save_standard_requirement_draft(
    project_name,
    requirements_dataframe,
):
    """
    Save or replace the editable draft for one project.
    """

    dataframe = remove_completely_blank_rows(
        requirements_dataframe
    )

    connection = get_database_connection()


    connection.execute(
        """
        DELETE FROM
        standard_requirement_drafts
        WHERE project_name = ?
        """,
        (
            project_name,
        ),
    )


    current_time = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    )


    for row_order, row in dataframe.iterrows():

        connection.execute(
            """
            INSERT INTO
            standard_requirement_drafts (
                project_name,
                row_order,
                requirement_id,
                category,
                requirement_title,
                requirement_statement,
                verification_method,
                notes,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_name,
                row_order,
                row["Requirement ID"],
                row["Category"],
                row["Requirement title"],
                row[
                    "Requirement statement"
                ],
                row[
                    "Verification method"
                ],
                row["Notes"],
                current_time,
            ),
        )


    connection.commit()
    connection.close()


def load_standard_requirement_draft(
    project_name,
):
    """
    Load the saved editable draft for one project.
    """

    connection = get_database_connection()

    dataframe = pd.read_sql_query(
        """
        SELECT
            requirement_id
                AS "Requirement ID",

            category
                AS "Category",

            requirement_title
                AS "Requirement title",

            requirement_statement
                AS "Requirement statement",

            verification_method
                AS "Verification method",

            notes
                AS "Notes"

        FROM standard_requirement_drafts

        WHERE project_name = ?

        ORDER BY row_order
        """,
        connection,
        params=(
            project_name,
        ),
    )

    connection.close()


    if dataframe.empty:

        return (
            create_empty_standard_requirements()
        )


    return normalise_standard_requirements(
        dataframe
    )


def delete_standard_requirement_draft(
    project_name,
):
    """
    Delete the editable draft for one project.
    """

    connection = get_database_connection()

    connection.execute(
        """
        DELETE FROM
        standard_requirement_drafts

        WHERE project_name = ?
        """,
        (
            project_name,
        ),
    )

    connection.commit()
    connection.close()


# ============================================================
# STANDARD REQUIREMENT REVISION FUNCTIONS
# ============================================================

def get_latest_revision_number(
    project_name,
):
    """
    Return the latest revision number for a project.

    Returns None when the project has no committed revision.
    """

    connection = get_database_connection()

    result = connection.execute(
        """
        SELECT
            MAX(revision_number)
                AS latest_revision

        FROM standard_requirement_revisions

        WHERE project_name = ?
        """,
        (
            project_name,
        ),
    ).fetchone()

    connection.close()


    if (
        result is None
        or result["latest_revision"] is None
    ):

        return None


    return int(
        result["latest_revision"]
    )


def get_next_revision_number(
    project_name,
):
    """
    Return the next revision number.

    The first revision is 00.
    """

    latest_revision = (
        get_latest_revision_number(
            project_name
        )
    )


    if latest_revision is None:

        return 0


    return latest_revision + 1


def format_revision(
    revision_number,
):
    """
    Format revisions as 00, 01, 02, etc.
    """

    return (
        f"{revision_number:02d}"
    )


def commit_standard_requirement_revision(
    project_name,
    requirements_dataframe,
    committed_by,
    revision_comment,
):
    """
    Commit and lock a standard-requirement revision.

    A new revision header and immutable requirement
    records are inserted into the database.
    """

    dataframe = remove_completely_blank_rows(
        requirements_dataframe
    )


    revision_number = (
        get_next_revision_number(
            project_name
        )
    )


    connection = get_database_connection()


    cursor = connection.execute(
        """
        INSERT INTO
        standard_requirement_revisions (
            project_name,
            revision_number,
            committed_by,
            committed_at,
            revision_comment,
            is_locked
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
            revision_comment,
            1,
        ),
    )


    revision_id = cursor.lastrowid


    for row_order, row in dataframe.iterrows():

        connection.execute(
            """
            INSERT INTO
            standard_requirement_revision_items (
                revision_id,
                row_order,
                requirement_id,
                category,
                requirement_title,
                requirement_statement,
                verification_method,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                revision_id,
                row_order,
                row[
                    "Requirement ID"
                ],
                row[
                    "Category"
                ],
                row[
                    "Requirement title"
                ],
                row[
                    "Requirement statement"
                ],
                row[
                    "Verification method"
                ],
                row[
                    "Notes"
                ],
            ),
        )


    connection.execute(
        """
        DELETE FROM
        standard_requirement_drafts

        WHERE project_name = ?
        """,
        (
            project_name,
        ),
    )


    connection.commit()
    connection.close()


    return revision_number


def load_revision_history(
    project_name,
):
    """
    Load the committed revision history for one project.
    """

    connection = get_database_connection()

    revision_history = pd.read_sql_query(
        """
        SELECT
            id,
            revision_number,
            committed_by,
            committed_at,
            revision_comment,
            is_locked

        FROM standard_requirement_revisions

        WHERE project_name = ?

        ORDER BY revision_number DESC
        """,
        connection,
        params=(
            project_name,
        ),
    )

    connection.close()

    return revision_history


def load_standard_revision_items(
    revision_id,
):
    """
    Load the locked standard requirements belonging
    to one committed revision.
    """

    connection = get_database_connection()

    dataframe = pd.read_sql_query(
        """
        SELECT
            requirement_id
                AS "Requirement ID",

            category
                AS "Category",

            requirement_title
                AS "Requirement title",

            requirement_statement
                AS "Requirement statement",

            verification_method
                AS "Verification method",

            notes
                AS "Notes"

        FROM
        standard_requirement_revision_items

        WHERE revision_id = ?

        ORDER BY row_order
        """,
        connection,
        params=(
            revision_id,
        ),
    )

    connection.close()

    return dataframe


def create_draft_from_revision(
    project_name,
    revision_id,
):
    """
    Copy a locked revision into a new editable draft.

    The committed revision remains unchanged.
    """

    revision_items = (
        load_standard_revision_items(
            revision_id
        )
    )


    save_standard_requirement_draft(
        project_name,
        revision_items,
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
    maintain controlled standard requirement baselines for
    individual ISV projects.
    """
)


# ============================================================
# MAIN TABS
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

    st.info(
        """
        This section continues to use the simplified stakeholder
        requirement workflow developed previously.
        """
    )


    # --------------------------------------------------------
    # REQUIREMENT DETAILS
    # --------------------------------------------------------

    st.subheader(
        "1. Requirement Details"
    )


    details_column_1, details_column_2 = (
        st.columns(2)
    )


    with details_column_1:

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


    with details_column_2:

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
            options=REQUIREMENT_CATEGORIES,
            key="project_requirement_category",
        )
    )


    # --------------------------------------------------------
    # SIMPLIFIED INPUT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "3. Tell Us What Is Needed"
    )


    stakeholder_description = st.text_area(
        (
            "Describe the requirement in plain language. "
            "*"
        ),
        placeholder=(
            "Example: The spraybar must operate between "
            "5°C and 45°C."
        ),
        height=130,
        key="project_stakeholder_description",
    )


    generated_requirement = (
        stakeholder_description.strip()
    )


    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "4. Requirement Preview"
    )


    requirement_preview = (

        generated_requirement

        if generated_requirement

        else (
            "[Describe what is required "
            "in Section 3]"
        )
    )


    st.code(
        requirement_preview,
        language=None,
    )


    # --------------------------------------------------------
    # SUBMIT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "5. Submit for Project-Owner Review"
    )


    submit_project_requirement = st.button(
        "Submit Project Requirement",
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


        if not generated_requirement:

            missing_fields.append(
                "Requirement description"
            )


        if missing_fields:

            st.error(
                "Please complete: "
                + ", ".join(
                    missing_fields
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
                    selected_requirement_category
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
                    stakeholder_description.strip()
                ),
            )


            st.success(
                """
                Requirement submitted successfully.

                Status: **Pending**
                """
            )


    # --------------------------------------------------------
    # SAVED REQUIREMENTS
    # --------------------------------------------------------

    st.divider()

    st.header(
        "Project Requirements Dashboard"
    )


    project_requirements = (
        load_project_requirements()
    )


    if project_requirements.empty:

        st.info(
            "No project-specific requirements "
            "have been submitted."
        )


    else:

        st.dataframe(
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

                    "source_department":
                        "Source",

                    "submitted_by":
                        "Submitted By",

                    "date_submitted":
                        "Date Submitted",

                    "status":
                        "Status",

                    "boilerplate_name":
                        "Requirement Type",
                }
            ),
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
        Complete the standard requirement set for the selected
        project. The requirement set remains editable while it is
        a draft. When committed, it becomes a locked project
        revision.
        """
    )


    st.info(
        """
        The first committed requirement baseline is
        **Revision 00**.

        A committed revision cannot be edited. Later changes must
        be made through a new revision.
        """
    )


    # --------------------------------------------------------
    # PROJECT SELECTION
    # --------------------------------------------------------

    st.subheader(
        "1. Select Project"
    )


    standard_project = st.selectbox(
        "Project *",
        options=ALLOWED_PROJECTS,
        key="standard_requirement_project",
    )


    revision_history = (
        load_revision_history(
            standard_project
        )
    )


    latest_revision_number = (
        get_latest_revision_number(
            standard_project
        )
    )


    next_revision_number = (
        get_next_revision_number(
            standard_project
        )
    )


    # --------------------------------------------------------
    # REVISION STATUS
    # --------------------------------------------------------

    status_column_1, status_column_2, status_column_3 = (
        st.columns(3)
    )


    with status_column_1:

        st.metric(
            "Selected Project",
            standard_project,
        )


    with status_column_2:

        if latest_revision_number is None:

            latest_revision_text = (
                "No revision"
            )

        else:

            latest_revision_text = (
                format_revision(
                    latest_revision_number
                )
            )


        st.metric(
            "Latest Locked Revision",
            latest_revision_text,
        )


    with status_column_3:

        st.metric(
            "Next Revision",
            format_revision(
                next_revision_number
            ),
        )


    # --------------------------------------------------------
    # LOAD DRAFT INTO SESSION
    # --------------------------------------------------------

    draft_session_key = (
        f"standard_draft_"
        f"{standard_project}"
    )


    if (
        draft_session_key
        not in st.session_state
    ):

        st.session_state[
            draft_session_key
        ] = (
            load_standard_requirement_draft(
                standard_project
            )
        )


    # --------------------------------------------------------
    # EDITABLE DRAFT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "2. Edit Standard Requirements Draft"
    )


    st.write(
        f"""
        You are preparing **Revision
        {format_revision(next_revision_number)}**
        for project **{standard_project}**.
        """
    )


    st.caption(
        """
        Add or remove rows as required. Requirement IDs should be
        unique within the project requirement set.
        """
    )


    edited_standard_requirements = (
        st.data_editor(
            st.session_state[
                draft_session_key
            ],
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key=(
                f"standard_editor_"
                f"{standard_project}"
            ),
            column_config={

                "Requirement ID":

                    st.column_config.TextColumn(
                        "Requirement ID",
                        help=(
                            "Example: STD-001"
                        ),
                        width="small",
                    ),


                "Category":

                    st.column_config.SelectboxColumn(
                        "Category",
                        options=(
                            STANDARD_REQUIREMENT_CATEGORIES
                        ),
                        required=True,
                        width="medium",
                    ),


                "Requirement title":

                    st.column_config.TextColumn(
                        "Requirement title",
                        width="medium",
                    ),


                "Requirement statement":

                    st.column_config.TextColumn(
                        "Requirement statement",
                        help=(
                            "Use a clear shall statement."
                        ),
                        width="large",
                    ),


                "Verification method":

                    st.column_config.SelectboxColumn(
                        "Verification method",
                        options=(
                            VERIFICATION_METHODS
                        ),
                        width="medium",
                    ),


                "Notes":

                    st.column_config.TextColumn(
                        "Notes",
                        width="medium",
                    ),
            },
        )
    )


    st.session_state[
        draft_session_key
    ] = (
        edited_standard_requirements
    )


    # --------------------------------------------------------
    # DRAFT ACTIONS
    # --------------------------------------------------------

    draft_button_column_1, draft_button_column_2 = (
        st.columns(2)
    )


    with draft_button_column_1:

        save_draft_button = st.button(
            "Save Draft",
            use_container_width=True,
            key=(
                f"save_standard_draft_"
                f"{standard_project}"
            ),
        )


    with draft_button_column_2:

        clear_draft_button = st.button(
            "Clear Draft",
            use_container_width=True,
            key=(
                f"clear_standard_draft_"
                f"{standard_project}"
            ),
        )


    if save_draft_button:

        save_standard_requirement_draft(
            standard_project,
            edited_standard_requirements,
        )


        st.success(
            f"""
            Draft saved for project
            **{standard_project}**.

            No revision has been created.
            """
        )


    if clear_draft_button:

        delete_standard_requirement_draft(
            standard_project
        )


        st.session_state[
            draft_session_key
        ] = (
            create_empty_standard_requirements()
        )


        st.success(
            "The editable draft has been cleared."
        )


        st.rerun()


    # --------------------------------------------------------
    # COMMIT REVISION
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "3. Commit and Lock Revision"
    )


    st.warning(
        f"""
        Committing will create locked
        **Revision {format_revision(next_revision_number)}**
        for project **{standard_project}**.

        The committed revision cannot be edited.
        """
    )


    commit_column_1, commit_column_2 = (
        st.columns(2)
    )


    with commit_column_1:

        committed_by = st.text_input(
            "Committed by *",
            placeholder="Enter your name",
            key=(
                f"standard_committed_by_"
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
                f"standard_revision_comment_"
                f"{standard_project}"
            ),
        )


    confirm_commit = st.checkbox(
        (
            "I confirm that this requirement set "
            "is complete and should be locked."
        ),
        key=(
            f"confirm_standard_commit_"
            f"{standard_project}"
        ),
    )


    commit_revision_button = st.button(
        (
            "Commit Revision "
            f"{format_revision(next_revision_number)}"
        ),
        type="primary",
        use_container_width=True,
        key=(
            f"commit_standard_revision_"
            f"{standard_project}"
        ),
    )


    if commit_revision_button:

        validation_errors = (
            validate_standard_requirements(
                edited_standard_requirements
            )
        )


        if not committed_by.strip():

            validation_errors.append(
                "Committed by is required."
            )


        if not confirm_commit:

            validation_errors.append(
                (
                    "You must confirm that the "
                    "revision should be locked."
                )
            )


        if validation_errors:

            st.error(
                "The revision could not be committed."
            )


            for validation_error in validation_errors:

                st.write(
                    f"- {validation_error}"
                )


        else:

            committed_revision_number = (
                commit_standard_requirement_revision(
                    project_name=(
                        standard_project
                    ),
                    requirements_dataframe=(
                        edited_standard_requirements
                    ),
                    committed_by=(
                        committed_by.strip()
                    ),
                    revision_comment=(
                        revision_comment.strip()
                    ),
                )
            )


            st.session_state[
                draft_session_key
            ] = (
                create_empty_standard_requirements()
            )


            st.success(
                f"""
                Project **{standard_project}**
                standard requirements were committed
                successfully.

                Locked revision:
                **{format_revision(committed_revision_number)}**
                """
            )


            st.rerun()


    # --------------------------------------------------------
    # LOCKED REVISION HISTORY
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "4. Locked Revision History"
    )


    revision_history = (
        load_revision_history(
            standard_project
        )
    )


    if revision_history.empty:

        st.info(
            """
            This project does not yet have a committed
            standard-requirement revision.

            The first committed revision will be **00**.
            """
        )


    else:

        revision_options = {}


        for _, revision_row in (
            revision_history.iterrows()
        ):

            revision_label = (

                "Revision "

                + format_revision(
                    int(
                        revision_row[
                            "revision_number"
                        ]
                    )
                )

                + " — "

                + revision_row[
                    "committed_at"
                ]

                + " — "

                + revision_row[
                    "committed_by"
                ]
            )


            revision_options[
                revision_label
            ] = int(
                revision_row["id"]
            )


        selected_revision_label = (
            st.selectbox(
                "View locked revision",
                options=list(
                    revision_options.keys()
                ),
                key=(
                    f"revision_history_"
                    f"{standard_project}"
                ),
            )
        )


        selected_revision_id = (
            revision_options[
                selected_revision_label
            ]
        )


        selected_revision_record = (

            revision_history[

                revision_history["id"]
                == selected_revision_id
            ]

            .iloc[0]
        )


        selected_revision_number = (

            int(
                selected_revision_record[
                    "revision_number"
                ]
            )
        )


        revision_detail_column_1, \
        revision_detail_column_2, \
        revision_detail_column_3 = (
            st.columns(3)
        )


        with revision_detail_column_1:

            st.metric(
                "Revision",
                format_revision(
                    selected_revision_number
                ),
            )


        with revision_detail_column_2:

            st.metric(
                "Status",
                "Locked",
            )


        with revision_detail_column_3:

            st.metric(
                "Committed By",
                selected_revision_record[
                    "committed_by"
                ],
            )


        st.write(
            "**Committed:** "
            + selected_revision_record[
                "committed_at"
            ]
        )


        revision_comment_value = (

            selected_revision_record[
                "revision_comment"
            ]

            if pd.notna(
                selected_revision_record[
                    "revision_comment"
                ]
            )

            else ""
        )


        if revision_comment_value:

            st.write(
                "**Revision comment:** "
                + revision_comment_value
            )


        locked_revision_items = (
            load_standard_revision_items(
                selected_revision_id
            )
        )


        st.dataframe(
            locked_revision_items,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Requirement statement":

                    st.column_config.TextColumn(
                        "Requirement statement",
                        width="large",
                    ),
            },
        )


        st.info(
            """
            This revision is locked and displayed as
            read-only.
            """
        )


        # ----------------------------------------------------
        # CREATE NEXT REVISION
        # ----------------------------------------------------

        st.subheader(
            "Create a New Revision"
        )


        st.write(
            f"""
            Copy Revision
            **{format_revision(selected_revision_number)}**
            into the editable draft for project
            **{standard_project}**.

            The locked source revision will not be changed.
            """
        )


        create_new_revision_button = st.button(
            (
                "Create Editable Draft from "
                f"Revision "
                f"{format_revision(selected_revision_number)}"
            ),
            use_container_width=True,
            key=(
                f"create_revision_draft_"
                f"{standard_project}_"
                f"{selected_revision_id}"
            ),
        )


        if create_new_revision_button:

            create_draft_from_revision(
                project_name=(
                    standard_project
                ),
                revision_id=(
                    selected_revision_id
                ),
            )


            st.session_state[
                draft_session_key
            ] = (
                load_standard_requirement_draft(
                    standard_project
                )
            )


            st.success(
                f"""
                Revision
                **{format_revision(selected_revision_number)}**
                was copied into the editable draft.

                The next committed revision will be
                **{format_revision(next_revision_number)}**.
                """
            )


            st.rerun()