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


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_database_connection():
    """
    Open a connection to the SQLite database.
    """

    return sqlite3.connect(
        DATABASE_FILE
    )


def get_existing_columns(connection):
    """
    Return the names of all columns currently stored
    in the requirements table.
    """

    table_information = connection.execute(
        "PRAGMA table_info(requirements)"
    ).fetchall()

    return [
        column[1]
        for column in table_information
    ]


def create_or_update_database():
    """
    Create the requirements table if it does not exist.

    New columns are added automatically without deleting
    requirements saved by earlier versions of the application.
    """

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

    existing_columns = get_existing_columns(
        connection
    )

    if "boilerplate_name" not in existing_columns:

        connection.execute(
            """
            ALTER TABLE requirements
            ADD COLUMN boilerplate_name TEXT
            """
        )

    if "stakeholder_input" not in existing_columns:

        connection.execute(
            """
            ALTER TABLE requirements
            ADD COLUMN stakeholder_input TEXT
            """
        )

    connection.commit()

    connection.close()


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
    Save a project-specific requirement.

    The requirement type is stored automatically as
    Customer specific.

    New requirements are automatically assigned
    a Pending review status.
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
    Load project-specific requirements only.
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
    Capture project requirements using simple guided questions.
    The application will convert the information into a clear,
    structured requirement statement.
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
        Select the type of requirement you want to add and answer
        the questions shown. The complete requirement will be
        written automatically.
        """
    )

    st.info(
        """
        You do not need systems-engineering experience to use
        this form. New requirements will be submitted with a
        status of **Pending** for project-owner review.
        """
    )


    # ========================================================
    # SECTION 1
    # REQUIREMENT DETAILS
    # ========================================================

    st.subheader(
        "1. Requirement Details"
    )

    information_column_1, information_column_2 = (
        st.columns(2)
    )


    with information_column_1:

        selected_project = st.selectbox(
            "Project *",
            options=ALLOWED_PROJECTS,
            help=(
                "Select the project to which this "
                "requirement applies."
            ),
        )

        requirement_title = st.text_input(
            "Requirement title *",
            placeholder=(
                "Example: Ambient operating temperature"
            ),
            help=(
                "Enter a short title that makes the "
                "requirement easy to identify."
            ),
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


    # ========================================================
    # SECTION 2
    # REQUIREMENT CATEGORY
    # ========================================================

    st.divider()

    st.subheader(
        "2. What Type of Requirement Is This?"
    )

    selected_requirement_category = st.selectbox(
        "Requirement type *",
        options=REQUIREMENT_CATEGORIES,
        help=(
            "Select the option that most closely describes "
            "what is needed."
        ),
    )


    category_descriptions = {

        "Operating condition":
            (
                "Use this when equipment must operate under "
                "a particular environmental or operating condition."
            ),

        "Capacity or quantity":
            (
                "Use this when a minimum quantity, capacity, "
                "or number of items is required."
            ),

        "Performance level":
            (
                "Use this when a minimum output, rate, pressure, "
                "flow, speed, or other performance value is required."
            ),

        "Response time":
            (
                "Use this when an action must happen within "
                "a specified time after an event."
            ),

        "Compatibility or interface":
            (
                "Use this when the ISV must connect to or "
                "operate with another system."
            ),

        "Product type or standard":
            (
                "Use this when a particular type, grade, "
                "standard, material, or specification is required."
            ),

        "Reliability or maintenance":
            (
                "Use this when equipment must operate for a "
                "defined period or meet a maintenance requirement."
            ),

        "Other requirement":
            (
                "Use this when the requirement does not fit "
                "one of the predefined categories."
            ),
    }


    st.caption(
        category_descriptions[
            selected_requirement_category
        ]
    )


    # ========================================================
    # SECTION 3
    # GUIDED QUESTIONS
    # ========================================================

    st.divider()

    st.subheader(
        "3. Tell Us What Is Needed"
    )


    generated_requirement = ""

    stakeholder_input = ""

    required_inputs_complete = False

    database_category = "Other"


    # ========================================================
    # OPERATING CONDITION
    # ========================================================

    if (
        selected_requirement_category
        == "Operating condition"
    ):

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
                placeholder=(
                    "Example: operate continuously"
                ),
                key="operating_action",
            )


        with column_2:

            operating_condition = st.text_area(
                "Under what condition must it operate? *",
                placeholder=(
                    "Example: at an ambient temperature "
                    "between 5°C and 45°C"
                ),
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


        generated_requirement = (

            f"The {equipment_name.strip()} shall "

            f"{required_action.strip()} "

            f"{operating_condition.strip()}."
        )


        stakeholder_input = (

            f"Equipment: {equipment_name.strip()}\n"

            f"Required action: {required_action.strip()}\n"

            f"Operating condition: "
            f"{operating_condition.strip()}"
        )


    # ========================================================
    # CAPACITY OR QUANTITY
    # ========================================================

    elif (
        selected_requirement_category
        == "Capacity or quantity"
    ):

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
                placeholder=(
                    "Example: control"
                ),
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
                placeholder=(
                    "Example: spray zones"
                ),
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


        generated_requirement = (

            f"The {equipment_name.strip()} shall "

            f"{required_action.strip()} "

            f"a minimum of "

            f"{minimum_quantity} "

            f"{item_name.strip()}."
        )


        stakeholder_input = (

            f"Equipment: {equipment_name.strip()}\n"

            f"Required action: {required_action.strip()}\n"

            f"Minimum quantity: {minimum_quantity}\n"

            f"Item: {item_name.strip()}"
        )


    # ========================================================
    # PERFORMANCE LEVEL
    # ========================================================

    elif (
        selected_requirement_category
        == "Performance level"
    ):

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
                placeholder=(
                    "Example: deliver cooling fluid"
                ),
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


        generated_requirement = (

            f"The {equipment_name.strip()} shall "

            f"{required_action.strip()} "

            f"at a minimum value of "

            f"{required_value:g} "

            f"{engineering_unit.strip()}."
        )


        stakeholder_input = (

            f"Equipment: {equipment_name.strip()}\n"

            f"Required action: {required_action.strip()}\n"

            f"Minimum value: {required_value:g}\n"

            f"Unit: {engineering_unit.strip()}"
        )


    # ========================================================
    # RESPONSE TIME
    # ========================================================

    elif (
        selected_requirement_category
        == "Response time"
    ):

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

            f"Required action: {required_action.strip()}\n"

            f"Trigger event: {trigger_event.strip()}\n"

            f"Maximum response time: "
            f"{maximum_time:g} {time_unit}"
        )


    # ========================================================
    # COMPATIBILITY OR INTERFACE
    # ========================================================

    elif (
        selected_requirement_category
        == "Compatibility or interface"
    ):

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
                placeholder=(
                    "Example: mill control system"
                ),
                key="interface_external_system",
            )


        with column_2:

            interface_description = st.text_input(
                "What connection or interface is required? *",
                placeholder=(
                    "Example: a minimum of 64 digital outputs"
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


        generated_requirement = (

            f"The {equipment_name.strip()} shall "

            f"interface with the "

            f"{external_system.strip()} "

            f"using "

            f"{interface_description.strip()}."
        )


        stakeholder_input = (

            f"Equipment: {equipment_name.strip()}\n"

            f"External equipment: {external_system.strip()}\n"

            f"Required interface: "
            f"{interface_description.strip()}"
        )


    # ========================================================
    # PRODUCT TYPE OR STANDARD
    # ========================================================

    elif (
        selected_requirement_category
        == "Product type or standard"
    ):

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
                placeholder=(
                    "Example: cooling fluid"
                ),
                key="standard_item",
            )


        with column_2:

            required_standard = st.text_input(
                "What type, grade, or standard is required? *",
                placeholder=(
                    "Example: ISO VG 32"
                ),
                key="standard_grade",
            )

            operating_limit = st.text_input(
                "Are there any operating limits?",
                placeholder=(
                    "Example: at a maximum operating "
                    "pressure of 10 bar"
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


        generated_requirement = (

            f"The {equipment_name.strip()} shall use "

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

            f"Specified item: {specified_item.strip()}\n"

            f"Required type, grade, or standard: "
            f"{required_standard.strip()}\n"

            f"Operating limit: "
            f"{operating_limit.strip()}"
        )


    # ========================================================
    # RELIABILITY OR MAINTENANCE
    # ========================================================

    elif (
        selected_requirement_category
        == "Reliability or maintenance"
    ):

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
                placeholder=(
                    "Example: operate"
                ),
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
                placeholder=(
                    "Example: operating hours"
                ),
                key="reliability_unit",
            )

            maintenance_condition = st.text_input(
                "What maintenance limitation applies?",
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


        generated_requirement = (

            f"The {equipment_name.strip()} shall "

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

            f"Required action: {required_action.strip()}\n"

            f"Minimum duration: "
            f"{minimum_duration:g} "
            f"{duration_unit.strip()}\n"

            f"Maintenance condition: "
            f"{maintenance_condition.strip()}"
        )


    # ========================================================
    # OTHER REQUIREMENT
    # ========================================================

    elif (
        selected_requirement_category
        == "Other requirement"
    ):

        database_category = "Other"

        st.write(
            """
            Describe the requirement in your own words.
            The project owner can refine the wording during review.
            """
        )

        stakeholder_description = st.text_area(
            "Describe what is needed *",
            placeholder=(
                "Example: The spraybar must be accessible "
                "from the operator side for maintenance."
            ),
            height=150,
            key="other_description",
        )


        required_inputs_complete = (
            bool(
                stakeholder_description.strip()
            )
        )


        generated_requirement = (
            stakeholder_description.strip()
        )


        stakeholder_input = (
            stakeholder_description.strip()
        )


    # ========================================================
    # SECTION 4
    # REVIEW GENERATED REQUIREMENT
    # ========================================================

    st.divider()

    st.subheader(
        "4. Review the Generated Requirement"
    )


    if required_inputs_complete:

        st.success(
            generated_requirement
        )

        st.caption(
            """
            Review the wording before submitting. The project
            owner will be able to approve, reject, or request
            clarification in a later development stage.
            """
        )


    else:

        st.info(
            """
            Complete all required fields above. The finished
            requirement will appear here automatically.
            """
        )


    # ========================================================
    # SECTION 5
    # SUBMIT REQUIREMENT
    # ========================================================

    st.divider()

    st.subheader(
        "5. Submit for Project-Owner Review"
    )


    save_requirement_button = st.button(
        "Submit Requirement",
        type="primary",
        use_container_width=True,
    )


    if save_requirement_button:

        missing_information = []


        if not requirement_title.strip():

            missing_information.append(
                "Requirement title"
            )


        if not submitted_by.strip():

            missing_information.append(
                "Submitted by"
            )


        if not required_inputs_complete:

            missing_information.append(
                "All required questions"
            )


        if missing_information:

            st.error(
                "Please complete: "
                + ", ".join(
                    missing_information
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
                """
                Requirement submitted successfully.

                Its review status has been set to **Pending**.
                """
            )


    # ========================================================
    # LOAD SAVED PROJECT REQUIREMENTS
    # ========================================================

    project_requirements = (
        load_project_requirements()
    )


    # ========================================================
    # PROJECT REQUIREMENTS DASHBOARD
    # ========================================================

    st.divider()

    st.header(
        "Project Requirements Dashboard"
    )


    if project_requirements.empty:

        st.info(
            """
            No project-specific requirements have
            been submitted.
            """
        )


    else:

        total_requirements = len(
            project_requirements
        )


        pending_requirements = (

            project_requirements["status"]

            .eq("Pending")

            .sum()
        )


        number_of_projects = (

            project_requirements[
                "project_name"
            ]

            .nunique()
        )


        number_of_sources = (

            project_requirements[
                "source_department"
            ]

            .nunique()
        )


        metric_1, metric_2, metric_3, metric_4 = (
            st.columns(4)
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


        metric_3.metric(
            "Projects",
            number_of_projects,
        )


        metric_4.metric(
            "Stakeholder Sources",
            number_of_sources,
        )


        # ====================================================
        # SEARCH AND FILTER
        # ====================================================

        st.subheader(
            "Search and Filter Requirements"
        )


        filter_column_1, filter_column_2, filter_column_3 = (
            st.columns(3)
        )


        with filter_column_1:

            search_text = st.text_input(
                "Search requirements",
                placeholder=(
                    "Search title or requirement text"
                ),
                key="requirement_search",
            )


        with filter_column_2:

            project_filter = st.selectbox(
                "Filter by project",
                options=[
                    "All Projects"
                ] + ALLOWED_PROJECTS,
                key="project_filter",
            )


        with filter_column_3:

            requirement_category_filter = (
                st.selectbox(
                    "Filter by requirement type",
                    options=[
                        "All Types"
                    ] + REQUIREMENT_CATEGORIES,
                    key="requirement_category_filter",
                )
            )


        # ====================================================
        # APPLY FILTERS
        # ====================================================

        filtered_requirements = (
            project_requirements.copy()
        )


        if search_text.strip():

            search_value = (
                search_text
                .strip()
                .lower()
            )


            search_matches = (

                filtered_requirements[
                    "requirement_title"
                ]

                .str.lower()

                .str.contains(
                    search_value,
                    na=False,
                    regex=False,
                )

                |

                filtered_requirements[
                    "requirement_text"
                ]

                .str.lower()

                .str.contains(
                    search_value,
                    na=False,
                    regex=False,
                )
            )


            filtered_requirements = (

                filtered_requirements[
                    search_matches
                ]
            )


        if project_filter != "All Projects":

            filtered_requirements = (

                filtered_requirements[

                    filtered_requirements[
                        "project_name"
                    ]

                    == project_filter
                ]
            )


        if (
            requirement_category_filter
            != "All Types"
        ):

            filtered_requirements = (

                filtered_requirements[

                    filtered_requirements[
                        "boilerplate_name"
                    ]

                    == requirement_category_filter
                ]
            )


        # ====================================================
        # REQUIREMENTS TABLE
        # ====================================================

        st.subheader(
            "Saved Project Requirements"
        )


        st.caption(

            f"Showing "

            f"{len(filtered_requirements)} "

            f"of "

            f"{len(project_requirements)} "

            f"project requirements."
        )


        display_requirements = (

            filtered_requirements.rename(

                columns={

                    "id":
                        "ID",

                    "project_name":
                        "Project",

                    "requirement_title":
                        "Title",

                    "requirement_text":
                        "Generated Requirement",

                    "category":
                        "Internal Category",

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

                    "stakeholder_input":
                        "Original Stakeholder Input",
                }
            )
        )


        st.dataframe(

            display_requirements,

            use_container_width=True,

            hide_index=True,

            column_config={

                "ID":

                    st.column_config.NumberColumn(
                        "ID",
                        format="REQ-%04d",
                    ),

                "Generated Requirement":

                    st.column_config.TextColumn(
                        "Generated Requirement",
                        width="large",
                    ),

                "Original Stakeholder Input":

                    st.column_config.TextColumn(
                        "Original Stakeholder Input",
                        width="large",
                    ),

                "Requirement Type":

                    st.column_config.TextColumn(
                        "Requirement Type",
                        width="medium",
                    ),
            },
        )


# ============================================================
# STANDARD REQUIREMENTS TAB
# ============================================================

with standard_requirements_tab:

    st.header(
        "Standard Product Requirements"
    )

    st.info(
        """
        This section is reserved for the standard ISV
        requirements workflow.
        """
    )

    st.write(
        """
        The intended future process is:

        1. Select an ISV product or product variant.

        2. Load the approved standard requirement library.

        3. Enter project-specific values where required.

        4. Add the selected standard requirements to the
        project requirement baseline.
        """
    )