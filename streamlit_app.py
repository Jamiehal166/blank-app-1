import streamlit as st

st.set_page_config(page_title="Requirements Generator", layout="wide")

st.title("📋 Boilerplate Requirements Generator")

templates = {
    "Performance / Capability":
        "The <system> shall be able to <function> <object> not less than <performance> times per <unit>",

    "Performance / Capacity":
        "The <system> shall be able to <function> <object> of <quantity> <unit>",

    "Environmental":
        "The <system> shall be able to <function> while <condition>"
}

template = st.selectbox(
    "Select a requirements template",
    list(templates.keys())
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    system = st.text_input("System")

    function = st.text_input("Function")

    obj = st.text_input("Object")

with col2:

    performance = st.text_input("Performance")

    unit = st.text_input("Units")

    condition = st.text_input("Condition")

sentence = templates[template]

sentence = sentence.replace("<system>", system)
sentence = sentence.replace("<function>", function)
sentence = sentence.replace("<object>", obj)
sentence = sentence.replace("<performance>", performance)
sentence = sentence.replace("<unit>", unit)
sentence = sentence.replace("<quantity>", performance)
sentence = sentence.replace("<condition>", condition)

st.markdown("## Requirement Preview")

st.success(sentence)

st.markdown("---")

priority = st.selectbox(
    "Priority",
    ["High", "Medium", "Low"]
)

verification = st.selectbox(
    "Verification",
    ["Inspection", "Test", "Analysis", "Demonstration"]
)

if st.button("Submit Requirement"):

    st.success("Requirement Saved")

    st.write({
        "Requirement": sentence,
        "Priority": priority,
        "Verification": verification
    })