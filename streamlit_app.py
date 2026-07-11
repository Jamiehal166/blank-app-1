import streamlit as st

# ------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------

st.set_page_config(
    page_title="Requirements Generator",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Boilerplate Requirements Generator")
st.write(
    "Select a requirement template, complete the highlighted inputs, "
    "and review the full requirement before submitting it."
)

# ------------------------------------------------------------
# REQUIREMENT TEMPLATES
# ------------------------------------------------------------

templates = {
    "Performance / Capability": {
        "description": (
            "Use this template when a system, product, or component must perform "
            "a defined function to a measurable level. The requirement should "
            "identify the responsible system, the required action, the object of "
            "the action, and a measurable performance value."
        ),
        "template": (
            "The <system> shall be able to <function> <object> "
            "not less than <performance> times per <unit>."
        ),
        "fields": [
            "system",
            "function",
            "object",
            "performance",
            "unit"
        ]
    },

    "Performance / Capacity": {
        "description": (
            "Use this template when defining the amount, volume, quantity, load, "
            "or capacity that a system must handle. The value should be measurable "
            "and include an appropriate engineering unit."
        ),
        "template": (
            "The <system> shall be able to <function> <object> "
            "with a capacity of <quantity> <unit>."
        ),
        "fields": [
            "system",
            "function",
            "object",
            "quantity",
            "unit"
        ]
    },

    "Environmental": {
        "description": (
            "Use this template when a system must continue to perform under a "
            "specific environmental or operating condition. The condition should "
            "be clear, measurable, and relevant to the intended operating environment."
        ),
        "template": (
            "The <system> shall be able to <function> <object> "
            "while operating under <condition>."
        ),
        "fields": [
            "system",
            "function",
            "object",
            "condition"
        ]
    },

    "Interface": {
        "description": (
            "Use this template when defining a physical, electrical, pneumatic, "
            "hydraulic, software, or information interface between two items. "
            "The interface type and connection details should be unambiguous."
        ),
        "template": (
            "The <system> shall interface with <external_system> "
            "using <interface_type>."
        ),
        "fields": [
            "system",
            "external_system",
            "interface_type"
        ]
    },

    "Supply Requirement": {
        "description": (
            "Use this template when defining a utility or customer supply needed "
            "by the system, such as coolant, compressed air, or electrical power. "
            "The required value and unit should be measurable."
        ),
        "template": (
            "The <supplier> shall provide <supply> at <value> <unit> "
            "at the connection to the <system>."
        ),
        "fields": [
            "supplier",
            "supply",
            "value",
            "unit",
            "system"
        ]
    }
}

# ------------------------------------------------------------
# FIELD LABELS
# ------------------------------------------------------------

field_labels = {
    "system": "System",
    "function": "Function",
    "object": "Object",
    "performance": "Performance",
    "quantity": "Quantity",
    "unit": "Unit",
    "condition": "Condition",
    "external_system": "External System",
    "interface_type": "Interface Type",
    "supplier": "Supplier",
    "supply": "Supply",
    "value": "Value"
}

# ------------------------------------------------------------
# TEMPLATE SELECTION
# ------------------------------------------------------------

st.subheader("1. Select Requirement Template")

selected_template_name = st.selectbox(
    "Requirement template",
    list(templates.keys())
)

selected_template = templates[selected_template_name]

# ------------------------------------------------------------
# LONG REFERENCE TEXT
# ------------------------------------------------------------

st.subheader("2. Template Reference")

st.info(selected_template["description"])

st.markdown("**Boilerplate template**")

st.code(
    selected_template["template"],
    language=None
)

# ------------------------------------------------------------
# INPUT FIELDS
# ------------------------------------------------------------

st.subheader("3. Complete Requirement Inputs")

values = {}

columns = st.columns(2)

for index, field_name in enumerate(selected_template["fields"]):

    label = field_labels.get(
        field_name,
        field_name.replace("_", " ").title()
    )

    with columns[index % 2]:

        if field_name == "unit":

            values[field_name] = st.selectbox(
                label,
                [
                    "minute",
                    "second",
                    "hour",
                    "mm",
                    "m",
                    "L/min",
                    "bar",
                    "°C",
                    "VDC",
                    "kW",
                    "Other"
                ],
                key=f"input_{field_name}"
            )

            if values[field_name] == "Other":

                values[field_name] = st.text_input(
                    "Enter unit",
                    key="custom_unit"
                )

        elif field_name == "supplier":

            values[field_name] = st.selectbox(
                label,
                [
                    "The customer",
                    "Primetals",
                    "The customer utility supply",
                    "Other"
                ],
                key=f"input_{field_name}"
            )

            if values[field_name] == "Other":

                values[field_name] = st.text_input(
                    "Enter supplier",
                    key="custom_supplier"
                )

        else:

            values[field_name] = st.text_input(
                label,
                key=f"input_{field_name}"
            )

# ------------------------------------------------------------
# GENERATE REQUIREMENT
# ------------------------------------------------------------

requirement = selected_template["template"]

for field_name, value in values.items():

    replacement = value.strip() if isinstance(value, str) else str(value)

    if not replacement:

        replacement = f"<{field_name}>"

    requirement = requirement.replace(
        f"<{field_name}>",
        replacement
    )

# ------------------------------------------------------------
# FULL REQUIREMENT PREVIEW
# ------------------------------------------------------------

st.subheader("4. Full Requirement")

st.success(requirement)

# ------------------------------------------------------------
# REQUIREMENT METADATA
# ------------------------------------------------------------

st.subheader("5. Requirement Information")

column_1, column_2, column_3 = st.columns(3)

with column_1:

    requirement_id = st.text_input(
        "Requirement ID",
        value="REQ-001"
    )

    category = st.selectbox(
        "Category",
        [
            "Performance",
            "Capacity",
            "Environmental",
            "Interface",
            "Supply",
            "Safety",
            "Electrical",
            "Pneumatic",
            "Mechanical",
            "Other"
        ]
    )

with column_2:

    priority = st.selectbox(
        "Priority",
        [
            "High",
            "Medium",
            "Low"
        ]
    )

    owner = st.selectbox(
        "Owner",
        [
            "Engineering",
            "Project Management",
            "Customer",
            "Sales",
            "Operations",
            "Other"
        ]
    )

with column_3:

    verification = st.selectbox(
        "Verification Method",
        [
            "Inspection",
            "Test",
            "Analysis",
            "Demonstration",
            "Drawing Review",
            "Design Review",
            "Document Review",
            "Other"
        ]
    )

    status = st.selectbox(
        "Status",
        [
            "Draft",
            "Submitted",
            "Approved",
            "Rejected"
        ]
    )

# ------------------------------------------------------------
# QUALITY CHECK
# ------------------------------------------------------------

st.subheader("6. Requirement Quality Check")

checks = {
    'Uses "shall"': "shall" in requirement.lower(),
    "All placeholders completed": "<" not in requirement and ">" not in requirement,
    "Ends with a full stop": requirement.strip().endswith("."),
    "Verification method selected": bool(verification)
}

for check_name, passed in checks.items():

    if passed:

        st.write(f"✅ {check_name}")

    else:

        st.write(f"⚠️ {check_name}")

# ------------------------------------------------------------
# SUBMIT
# ------------------------------------------------------------

st.subheader("7. Submit Requirement")

if "requirements" not in st.session_state:

    st.session_state.requirements = []

if st.button(
    "Submit Requirement",
    type="primary",
    use_container_width=True
):

    record = {
        "Requirement ID": requirement_id,
        "Requirement": requirement,
        "Template": selected_template_name,
        "Category": category,
        "Priority": priority,
        "Owner": owner,
        "Verification": verification,
        "Status": status
    }

    st.session_state.requirements.append(record)

    st.success(
        f"{requirement_id} has been added to the requirements register."
    )

# ------------------------------------------------------------
# REQUIREMENTS REGISTER
# ------------------------------------------------------------

if st.session_state.requirements:

    st.divider()

    st.subheader("Requirements Register")

    st.dataframe(
        st.session_state.requirements,
        use_container_width=True,
        hide_index=True
    )