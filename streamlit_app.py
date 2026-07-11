from __future__ import annotations

import io
import json
import re
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ISV Requirements Capture",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7fa;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    .app-header {
        background: linear-gradient(135deg, #0b4f6c 0%, #1d6f91 100%);
        padding: 1.4rem 1.8rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
    }

    .app-header h1 {
        margin: 0;
        font-size: 2rem;
    }

    .app-header p {
        margin: 0.35rem 0 0 0;
        opacity: 0.92;
    }

    .section-card {
        background: white;
        border: 1px solid #d9e2ea;
        border-left: 6px solid #1d6f91;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 7px rgba(0, 0, 0, 0.05);
    }

    .reference-box {
        background: #eef6fa;
        border: 1px solid #b8d6e5;
        border-radius: 9px;
        padding: 0.9rem 1rem;
        margin: 0.4rem 0 1rem 0;
    }

    .requirement-box {
        background: #eaf6e4;
        border: 2px solid #4cae2b;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        font-size: 1.08rem;
        line-height: 1.7;
        margin-top: 0.5rem;
    }

    .warning-box {
        background: #fff5df;
        border: 2px solid #e3a92f;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        font-size: 1.08rem;
        line-height: 1.7;
        margin-top: 0.5rem;
    }

    .small-muted {
        color: #667785;
        font-size: 0.88rem;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"] {
        background: #4cae2b;
        border-color: #3c9221;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INPUT DEFINITIONS
# Everything is contained in this single Python file.
# ============================================================

STANDARD_SECTIONS = {
    "Project Information": [
        {
            "id": "PRJ-001",
            "field": "Customer",
            "type": "text",
            "required": True,
            "help": "Customer or end-user organisation.",
        },
        {
            "id": "PRJ-002",
            "field": "Project Name",
            "type": "text",
            "required": True,
            "help": "Internal or contractual project name.",
        },
        {
            "id": "PRJ-003",
            "field": "Project Number",
            "type": "text",
            "required": True,
            "help": "Unique internal project reference.",
        },
        {
            "id": "PRJ-004",
            "field": "Mill Name / Reference",
            "type": "text",
            "required": True,
            "help": "Customer mill name, line number or equipment reference.",
        },
        {
            "id": "PRJ-005",
            "field": "Revision",
            "type": "revision",
            "required": True,
            "help": "Automatically controlled. First version 00, then 01, 02, 03, etc.",
        },
    ],

    "Mill Data": [
        {
            "id": "MIL-001",
            "field": "Material / Material Grades",
            "type": "textarea",
            "required": True,
            "help": "Enter all strip materials and grades. Use one line per material or grade.",
        },
        {
            "id": "MIL-002",
            "field": "Maximum Exit Strip Thickness",
            "type": "number",
            "unit": "mm",
            "required": True,
        },
        {
            "id": "MIL-003",
            "field": "Minimum Exit Strip Thickness",
            "type": "number",
            "unit": "mm",
            "required": True,
        },
        {
            "id": "MIL-004",
            "field": "Maximum Strip Width",
            "type": "number",
            "unit": "mm",
            "required": True,
        },
        {
            "id": "MIL-005",
            "field": "Minimum Strip Width",
            "type": "number",
            "unit": "mm",
            "required": True,
        },
        {
            "id": "MIL-006",
            "field": "Maximum Strip Speed",
            "type": "number",
            "unit": "m/min",
            "required": False,
        },
        {
            "id": "MIL-007",
            "field": "Minimum Strip Speed",
            "type": "number",
            "unit": "m/min",
            "required": False,
        },
        {
            "id": "MIL-008",
            "field": "Mill Drive Power",
            "type": "number",
            "unit": "kW",
            "required": False,
        },
        {
            "id": "MIL-009",
            "field": "Maximum Mill Force",
            "type": "number",
            "unit": "kN",
            "required": False,
        },
        {
            "id": "MIL-010",
            "field": "Existing Spraybar Capacity",
            "type": "number",
            "unit": "L/min",
            "required": False,
        },
        {
            "id": "MIL-011",
            "field": "Available Coolant Pressure",
            "type": "number",
            "unit": "bar",
            "required": True,
        },
        {
            "id": "MIL-012",
            "field": "Coolant Type",
            "type": "select_other",
            "options": ["Water", "Emulsion", "Kerosene", "Other"],
            "required": True,
        },
        {
            "id": "MIL-013",
            "field": "Maximum Work Roll Diameter",
            "type": "number",
            "unit": "mm",
            "required": True,
        },
        {
            "id": "MIL-014",
            "field": "Minimum Work Roll Diameter",
            "type": "number",
            "unit": "mm",
            "required": True,
        },
        {
            "id": "MIL-015",
            "field": "Work Roll Barrel Length",
            "type": "number",
            "unit": "mm",
            "required": False,
        },
        {
            "id": "MIL-016",
            "field": "Available Installation Envelope",
            "type": "text",
            "required": False,
            "help": "Enter dimensions or a drawing reference.",
        },
        {
            "id": "MIL-017",
            "field": "Installation Environment",
            "type": "select_other",
            "options": ["Indoor", "Outdoor", "Other"],
            "required": True,
        },
        {
            "id": "MIL-018",
            "field": "Minimum Ambient Temperature",
            "type": "number",
            "unit": "°C",
            "required": False,
        },
        {
            "id": "MIL-019",
            "field": "Maximum Ambient Temperature",
            "type": "number",
            "unit": "°C",
            "required": False,
        },
    ],

    "Spraybar as Sold Data": [
        {
            "id": "SPR-001",
            "field": "Type of Spraybar",
            "type": "select_other",
            "options": [
                "Work Roll Spray Bars",
                "Backup Roll Spray Bars",
                "Intermediate Roll Spray Bars",
                "Other",
            ],
            "required": True,
        },
        {
            "id": "SPR-002",
            "field": "Number of Spraybars",
            "type": "integer",
            "default": 2,
            "required": True,
        },
        {
            "id": "SPR-003",
            "field": "Spraybar Material",
            "type": "select_other",
            "options": ["Aluminium", "Stainless Steel", "Other"],
            "required": True,
        },
        {
            "id": "SPR-004",
            "field": "Spraybar Variant",
            "type": "select_other",
            "options": ["Standard", "Project Specific", "Other"],
            "required": False,
        },
        {
            "id": "SPR-005",
            "field": "Number of Valve Rows",
            "type": "select_other",
            "options": ["Single Row", "Double Row", "Other"],
            "required": True,
        },
        {
            "id": "SPR-006",
            "field": "Valve Pitching",
            "type": "text",
            "default": "37 x 52 mm",
            "required": True,
        },
        {
            "id": "SPR-007",
            "field": "Type of Valve",
            "type": "select_other",
            "options": ["ISV (Mk3)", "Other"],
            "required": True,
        },
        {
            "id": "SPR-008",
            "field": "Valve Operation",
            "type": "select_other",
            "options": ["Air Operated", "Electrically Operated", "Other"],
            "required": True,
        },
        {
            "id": "SPR-009",
            "field": "Normally Open or Closed",
            "type": "select",
            "options": ["Normally Open", "Normally Closed"],
            "required": True,
        },
        {
            "id": "SPR-010",
            "field": "Solenoid Voltage",
            "type": "number",
            "unit": "VDC",
            "default": 24.0,
            "required": True,
        },
        {
            "id": "SPR-011",
            "field": "Solenoid Power",
            "type": "number",
            "unit": "W",
            "default": 2.0,
            "required": True,
        },
        {
            "id": "SPR-012",
            "field": "Solenoid Current",
            "type": "number",
            "unit": "A",
            "default": 0.083,
            "required": True,
        },
        {
            "id": "SPR-013",
            "field": "Solenoid Duty Rating",
            "type": "text",
            "default": "100% Continuous Use",
            "required": True,
        },
        {
            "id": "SPR-014",
            "field": "Maximum Solenoid Switching Time",
            "type": "number",
            "unit": "ms",
            "default": 12.0,
            "required": True,
        },
        {
            "id": "SPR-015",
            "field": "Total Number of Nozzles",
            "type": "integer",
            "default": 284,
            "required": True,
        },
        {
            "id": "SPR-016",
            "field": "Maximum Spraybar Flow Rate",
            "type": "number",
            "unit": "L/min",
            "default": 3200.0,
            "required": True,
        },
        {
            "id": "SPR-017",
            "field": "Flow Rate Reference Pressure",
            "type": "number",
            "unit": "bar",
            "default": 6.0,
            "required": True,
        },
    ],

    "Top Spraybar": [
        {
            "id": "TOP-001",
            "field": "Top Spraybar Included",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "TOP-002",
            "field": "Top Spraybar Number of Valves",
            "type": "integer",
            "default": 37,
            "required": False,
            "parent": "TOP-001",
        },
        {
            "id": "TOP-003",
            "field": "Top Spraybar Nozzles per Valve",
            "type": "text",
            "default": "1 x 4 vertical rows",
            "required": False,
            "parent": "TOP-001",
        },
        {
            "id": "TOP-004",
            "field": "Top Spraybar Nozzle Pitch",
            "type": "number",
            "unit": "mm",
            "default": 52.0,
            "required": False,
            "parent": "TOP-001",
        },
        {
            "id": "TOP-005",
            "field": "Top Spraybar Number of Nozzles",
            "type": "integer",
            "default": 148,
            "required": False,
            "parent": "TOP-001",
        },
        {
            "id": "TOP-006",
            "field": "Top BUR Lubrication Included",
            "type": "yesno",
            "default": "No",
            "required": False,
            "parent": "TOP-001",
        },
        {
            "id": "TOP-007",
            "field": "Additional Top Lubrication Nozzles",
            "type": "integer",
            "required": False,
            "parent": "TOP-006",
        },
    ],

    "Bottom Spraybar": [
        {
            "id": "BTM-001",
            "field": "Bottom Spraybar Included",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "BTM-002",
            "field": "Bottom Spraybar Number of Valves",
            "type": "integer",
            "default": 37,
            "required": False,
            "parent": "BTM-001",
        },
        {
            "id": "BTM-003",
            "field": "Additional Lubrication Valve",
            "type": "yesno",
            "default": "Yes",
            "required": False,
            "parent": "BTM-001",
        },
        {
            "id": "BTM-004",
            "field": "Remote Nozzle Bar",
            "type": "yesno",
            "default": "Yes",
            "required": False,
            "parent": "BTM-001",
        },
        {
            "id": "BTM-005",
            "field": "Bottom Spraybar Nozzles per Valve",
            "type": "text",
            "default": "1 x 3 vertical rows",
            "required": False,
            "parent": "BTM-001",
        },
        {
            "id": "BTM-006",
            "field": "Bottom Spraybar Nozzle Pitch",
            "type": "number",
            "unit": "mm",
            "default": 52.0,
            "required": False,
            "parent": "BTM-001",
        },
        {
            "id": "BTM-007",
            "field": "Bottom Spraybar Number of Nozzles",
            "type": "integer",
            "default": 111,
            "required": False,
            "parent": "BTM-001",
        },
    ],

    "Bottom Work Roll Lube Bar": [
        {
            "id": "LUB-001",
            "field": "Bottom Work Roll Lube Bar Included",
            "type": "yesno",
            "default": "Yes",
            "required": False,
        },
        {
            "id": "LUB-002",
            "field": "Lube Bar Number of Nozzles",
            "type": "integer",
            "default": 25,
            "required": False,
            "parent": "LUB-001",
        },
        {
            "id": "LUB-003",
            "field": "Lube Bar Control",
            "type": "select_other",
            "options": ["Remote Mounted Valve", "Integrated Valve", "Other"],
            "required": False,
            "parent": "LUB-001",
        },
    ],

    "Signal Cable Data": [
        {
            "id": "CBL-001",
            "field": "Signal Cable Required",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "CBL-002",
            "field": "Cable Type",
            "type": "select_other",
            "options": ["ISV Cable", "Customer Specified", "Other"],
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-003",
            "field": "Cable Length",
            "type": "number",
            "unit": "m",
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-004",
            "field": "Cable Quantity",
            "type": "integer",
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-005",
            "field": "Connector Angle",
            "type": "select_other",
            "options": ["0°", "30°", "45°", "60°", "90°", "Other"],
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-006",
            "field": "Spraybar Connection End",
            "type": "text",
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-007",
            "field": "Junction Box Connection End",
            "type": "text",
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-008",
            "field": "Cable Supplied By",
            "type": "select_other",
            "options": ["Primetals", "Customer", "Other"],
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-009",
            "field": "Cable Identification / Reference",
            "type": "text",
            "required": False,
            "parent": "CBL-001",
        },
        {
            "id": "CBL-010",
            "field": "Additional Cable Requirements",
            "type": "textarea",
            "required": False,
            "parent": "CBL-001",
        },
    ],

    "Junction Box Data": [
        {
            "id": "JBX-001",
            "field": "Junction Box Required",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "JBX-002",
            "field": "Junction Box Type",
            "type": "select_other",
            "options": ["Standard", "Project Specific", "Customer Specified", "Other"],
            "required": False,
            "parent": "JBX-001",
        },
        {
            "id": "JBX-003",
            "field": "Junction Box Quantity",
            "type": "integer",
            "required": False,
            "parent": "JBX-001",
        },
        {
            "id": "JBX-004",
            "field": "Junction Box Material",
            "type": "select_other",
            "options": ["Stainless Steel", "Painted Steel", "GRP", "Other"],
            "required": False,
            "parent": "JBX-001",
        },
        {
            "id": "JBX-005",
            "field": "IP Rating",
            "type": "select_other",
            "options": ["IP54", "IP65", "IP66", "Other"],
            "required": False,
            "parent": "JBX-001",
        },
        {
            "id": "JBX-006",
            "field": "Installation Location",
            "type": "text",
            "required": False,
            "parent": "JBX-001",
        },
        {
            "id": "JBX-007",
            "field": "Mounting Orientation",
            "type": "select_other",
            "options": ["Horizontal", "Vertical", "Other"],
            "required": False,
            "parent": "JBX-001",
        },
        {
            "id": "JBX-008",
            "field": "Cable Entry Orientation",
            "type": "select_other",
            "options": ["Bottom", "Side", "Top", "Other"],
            "required": False,
            "parent": "JBX-001",
        },
    ],

    "Pneumatic Control Panel": [
        {
            "id": "PCP-001",
            "field": "Pneumatic Control Panel Required",
            "type": "yesno",
            "default": "No",
            "required": True,
        },
        {
            "id": "PCP-002",
            "field": "Panel Quantity",
            "type": "integer",
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-003",
            "field": "Panel Type",
            "type": "select_other",
            "options": ["Standard", "Custom", "Customer Specified", "Other"],
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-004",
            "field": "Mounting Arrangement",
            "type": "select_other",
            "options": ["Wall Mounted", "Floor Mounted", "Machine Mounted", "Other"],
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-005",
            "field": "Supply Pressure",
            "type": "number",
            "unit": "bar",
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-006",
            "field": "Required Output Pressure",
            "type": "number",
            "unit": "bar",
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-007",
            "field": "Number of Controlled Spraybars",
            "type": "integer",
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-008",
            "field": "Panel Solenoid Voltage",
            "type": "select_other",
            "options": ["24 VDC", "Other"],
            "required": False,
            "parent": "PCP-001",
        },
        {
            "id": "PCP-009",
            "field": "Enclosure Rating",
            "type": "select_other",
            "options": ["IP54", "IP65", "IP66", "Other"],
            "required": False,
            "parent": "PCP-001",
        },
    ],

    "Air Intensifier": [
        {
            "id": "AIR-001",
            "field": "Air Intensifier Required",
            "type": "yesno",
            "default": "No",
            "required": True,
        },
        {
            "id": "AIR-002",
            "field": "Air Intensifier Quantity",
            "type": "integer",
            "required": False,
            "parent": "AIR-001",
        },
        {
            "id": "AIR-003",
            "field": "Air Intensifier Type",
            "type": "select_other",
            "options": ["Standard", "Project Specific", "Customer Specified", "Other"],
            "required": False,
            "parent": "AIR-001",
        },
        {
            "id": "AIR-004",
            "field": "Inlet Air Pressure",
            "type": "number",
            "unit": "bar",
            "required": False,
            "parent": "AIR-001",
        },
        {
            "id": "AIR-005",
            "field": "Required Outlet Pressure",
            "type": "number",
            "unit": "bar",
            "required": False,
            "parent": "AIR-001",
        },
        {
            "id": "AIR-006",
            "field": "Required Air Flow",
            "type": "number",
            "unit": "m³/h FAD",
            "required": False,
            "parent": "AIR-001",
        },
        {
            "id": "AIR-007",
            "field": "Number of Spraybars Supplied",
            "type": "integer",
            "required": False,
            "parent": "AIR-001",
        },
    ],

    "Supply Requirements": [
        {
            "id": "CLT-001",
            "field": "Coolant Pressure",
            "type": "number",
            "unit": "bar",
            "default": 6.0,
            "required": True,
        },
        {
            "id": "CLT-002",
            "field": "Coolant Pressure Tolerance",
            "type": "number",
            "unit": "± bar",
            "default": 0.3,
            "required": True,
        },
        {
            "id": "CLT-003",
            "field": "Maximum Coolant Flow Rate",
            "type": "number",
            "unit": "L/min",
            "default": 3200.0,
            "required": True,
        },
        {
            "id": "CLT-004",
            "field": "Maximum Particle Size",
            "type": "number",
            "unit": "µm",
            "default": 800.0,
            "required": True,
        },
        {
            "id": "CLT-005",
            "field": "Filter Mesh",
            "type": "number",
            "unit": "mesh",
            "default": 20.0,
            "required": False,
        },
        {
            "id": "CLT-006",
            "field": "Minimum Coolant Temperature",
            "type": "number",
            "unit": "°C",
            "default": 25.0,
            "required": True,
        },
        {
            "id": "CLT-007",
            "field": "Maximum Coolant Temperature",
            "type": "number",
            "unit": "°C",
            "default": 50.0,
            "required": True,
        },
        {
            "id": "CLT-008",
            "field": "Pressure Maintained Regardless of Flow",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "PNE-001",
            "field": "Pneumatic Supply Required",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "PNE-002",
            "field": "Maximum Air Consumption per Spraybar",
            "type": "number",
            "unit": "m³/h FAD",
            "default": 0.85,
            "required": True,
            "parent": "PNE-001",
        },
        {
            "id": "PNE-003",
            "field": "Minimum Air Pressure Above Coolant",
            "type": "number",
            "unit": "bar",
            "default": 2.0,
            "required": True,
            "parent": "PNE-001",
        },
        {
            "id": "PNE-004",
            "field": "Air Cleanliness Standard",
            "type": "text",
            "default": "ISO 8573-1 Class 3.4.2 or better",
            "required": True,
            "parent": "PNE-001",
        },
        {
            "id": "ELE-001",
            "field": "Electrical Supply Required",
            "type": "yesno",
            "default": "Yes",
            "required": True,
        },
        {
            "id": "ELE-002",
            "field": "Operating Voltage",
            "type": "number",
            "unit": "VDC",
            "default": 24.0,
            "required": True,
            "parent": "ELE-001",
        },
        {
            "id": "ELE-003",
            "field": "Solenoid Power",
            "type": "number",
            "unit": "W",
            "default": 2.0,
            "required": True,
            "parent": "ELE-001",
        },
        {
            "id": "ELE-004",
            "field": "Duty Rating",
            "type": "text",
            "default": "100% Continuous Use",
            "required": True,
            "parent": "ELE-001",
        },
    ],

    "Connections": [
        {
            "id": "CON-001",
            "field": "Number of Coolant Connections",
            "type": "integer",
            "required": True,
        },
        {
            "id": "CON-002",
            "field": "Coolant Block Angle",
            "type": "select_other",
            "options": ["30°", "45°", "60°", "90°", "Other"],
            "required": True,
        },
        {
            "id": "CON-003",
            "field": "Coolant Connection Size",
            "type": "text",
            "default": "M52 x 2",
            "required": True,
        },
        {
            "id": "CON-004",
            "field": "Coolant Connection Type",
            "type": "text",
            "default": "24° Cone",
            "required": True,
        },
        {
            "id": "CON-005",
            "field": "Number of Electrical Connections",
            "type": "integer",
            "required": True,
        },
        {
            "id": "CON-006",
            "field": "Electrical Block Angle",
            "type": "select_other",
            "options": ["0°", "30°", "45°", "60°", "90°", "Other"],
            "required": True,
        },
        {
            "id": "CON-007",
            "field": "Customer Electrical Connection",
            "type": "text",
            "default": "ISV Cable (PTUK Supply)",
            "required": True,
        },
        {
            "id": "CON-008",
            "field": "Number of Air Connections",
            "type": "integer",
            "required": True,
        },
        {
            "id": "CON-009",
            "field": "Air Block Angle",
            "type": "select_other",
            "options": ["45°", "90°", "Other"],
            "required": True,
        },
        {
            "id": "CON-010",
            "field": "Air Connection Size",
            "type": "text",
            "default": "M18 x 1.5",
            "required": True,
        },
        {
            "id": "CON-011",
            "field": "Air Connection Type",
            "type": "text",
            "default": "24° Cone",
            "required": True,
        },
    ],
}


CUSTOMER_SPECIFIC_FIELDS = [
    {
        "id": "CUS-001",
        "field": "Requirement Title",
        "type": "text",
        "required": True,
        "help": "Short name for the customer-specific requirement.",
    },
    {
        "id": "CUS-002",
        "field": "Requirement Category",
        "type": "select_other",
        "options": [
            "Performance",
            "Interface",
            "Environmental",
            "Electrical",
            "Pneumatic",
            "Mechanical",
            "Safety",
            "Installation",
            "Documentation",
            "Other",
        ],
        "required": True,
    },
    {
        "id": "CUS-003",
        "field": "System / Item",
        "type": "text",
        "required": True,
        "help": "The item responsible for satisfying the requirement.",
    },
    {
        "id": "CUS-004",
        "field": "Required Function",
        "type": "text",
        "required": True,
        "help": "Use an active verb, for example provide, withstand, connect, fit or operate.",
    },
    {
        "id": "CUS-005",
        "field": "Object / Subject",
        "type": "text",
        "required": True,
        "help": "The object or subject affected by the function.",
    },
    {
        "id": "CUS-006",
        "field": "Constraint / Measurable Value",
        "type": "text",
        "required": True,
        "help": "Enter a measurable value, limit, range or acceptance criterion.",
    },
    {
        "id": "CUS-007",
        "field": "Operating Condition",
        "type": "text",
        "required": False,
        "help": "Optional condition under which the requirement applies.",
    },
    {
        "id": "CUS-008",
        "field": "Requirement Source",
        "type": "select_other",
        "options": [
            "Customer Specification",
            "Customer Email",
            "Purchase Order",
            "Offer Letter",
            "Technical Clarification",
            "Site Survey",
            "Stakeholder Input",
            "Other",
        ],
        "required": True,
    },
    {
        "id": "CUS-009",
        "field": "Source Reference",
        "type": "text",
        "required": False,
        "help": "Document number, email subject, drawing number or clarification reference.",
    },
    {
        "id": "CUS-010",
        "field": "Owner",
        "type": "select_other",
        "options": [
            "Project Manager",
            "Engineering",
            "Electrical Engineering",
            "Mechanical Engineering",
            "Sales",
            "Customer",
            "Other",
        ],
        "required": True,
    },
    {
        "id": "CUS-011",
        "field": "Priority",
        "type": "select",
        "options": ["High", "Medium", "Low"],
        "required": True,
    },
    {
        "id": "CUS-012",
        "field": "Verification Method",
        "type": "select_other",
        "options": [
            "Inspection",
            "Drawing Review",
            "Analysis",
            "Calculation",
            "Demonstration",
            "Functional Test",
            "Pressure Test",
            "Flow Test",
            "Electrical Test",
            "Design Review",
            "Document Review",
            "Other",
        ],
        "required": True,
    },
    {
        "id": "CUS-013",
        "field": "Parent Requirement ID",
        "type": "text",
        "required": False,
        "help": "Optional parent requirement for traceability.",
    },
    {
        "id": "CUS-014",
        "field": "Additional Notes",
        "type": "textarea",
        "required": False,
    },
]


STANDARD_REQUIREMENT_TEMPLATES = [
    {
        "id": "STD-001",
        "name": "Maximum strip width",
        "category": "Mill Data",
        "reference": (
            "Defines the maximum strip width that the spraybar system must "
            "accommodate. The value should be taken from approved customer or mill data."
        ),
        "template": (
            "The spraybar system shall accommodate a maximum strip width of "
            "<Maximum Strip Width> mm."
        ),
        "verification": "Drawing Review",
    },
    {
        "id": "STD-002",
        "name": "Spraybar quantity and type",
        "category": "Product Configuration",
        "reference": (
            "Defines the number and application of spraybars included in the sold solution."
        ),
        "template": (
            "The system shall include <Number of Spraybars> <Type of Spraybar>."
        ),
        "verification": "Inspection",
    },
    {
        "id": "STD-003",
        "name": "Spraybar material",
        "category": "Material",
        "reference": (
            "Defines the approved main spraybar body material. The selected material "
            "should be compatible with the coolant and installation environment."
        ),
        "template": (
            "The spraybars shall be manufactured from <Spraybar Material>."
        ),
        "verification": "Material Certification / Inspection",
    },
    {
        "id": "STD-004",
        "name": "Maximum coolant flow",
        "category": "Performance",
        "reference": (
            "Defines the maximum coolant flow capability at the stated reference pressure."
        ),
        "template": (
            "The spraybar system shall support a maximum coolant flow rate of "
            "<Maximum Spraybar Flow Rate> L/min at "
            "<Flow Rate Reference Pressure> bar at the connection to the spraybar."
        ),
        "verification": "Flow Test / Calculation",
    },
    {
        "id": "STD-005",
        "name": "Signal cable supply",
        "category": "Electrical Interface",
        "reference": (
            "Defines signal cable quantity, finished length and connector angle."
        ),
        "template": (
            "The system shall be supplied with <Cable Quantity> signal cable(s), "
            "each with a length of <Cable Length> m and a connector angle of "
            "<Connector Angle>."
        ),
        "verification": "Inspection",
        "condition": ("Signal Cable Required", "Yes"),
    },
    {
        "id": "STD-006",
        "name": "Junction box supply",
        "category": "Electrical Interface",
        "reference": (
            "Defines junction-box quantity and type where junction boxes are included."
        ),
        "template": (
            "The system shall include <Junction Box Quantity> "
            "<Junction Box Type> junction box(es)."
        ),
        "verification": "Inspection",
        "condition": ("Junction Box Required", "Yes"),
    },
    {
        "id": "STD-007",
        "name": "Pneumatic control panel",
        "category": "Pneumatic System",
        "reference": (
            "Defines the pneumatic control-panel supply where a panel is included."
        ),
        "template": (
            "The system shall include <Panel Quantity> <Panel Type> pneumatic "
            "control panel(s) configured for <Number of Controlled Spraybars> spraybar(s)."
        ),
        "verification": "Inspection / Functional Test",
        "condition": ("Pneumatic Control Panel Required", "Yes"),
    },
    {
        "id": "STD-008",
        "name": "Air intensifier performance",
        "category": "Pneumatic System",
        "reference": (
            "Defines required air-intensifier outlet pressure and flow."
        ),
        "template": (
            "The system shall include an air intensifier capable of providing "
            "<Required Outlet Pressure> bar at a flow rate of "
            "<Required Air Flow> m³/h FAD."
        ),
        "verification": "Pressure / Flow Test",
        "condition": ("Air Intensifier Required", "Yes"),
    },
    {
        "id": "STD-009",
        "name": "Coolant pressure",
        "category": "Supply",
        "reference": (
            "Defines customer coolant pressure at the spraybar connection, including tolerance."
        ),
        "template": (
            "The customer coolant supply shall provide coolant at "
            "<Coolant Pressure> bar ± <Coolant Pressure Tolerance> bar at the "
            "connection to the spraybar."
        ),
        "verification": "Pressure Test",
    },
    {
        "id": "STD-010",
        "name": "Coolant filtration",
        "category": "Supply / Cleanliness",
        "reference": (
            "Controls maximum particle size entering the spraybar."
        ),
        "template": (
            "The customer coolant supply shall be filtered to "
            "<Maximum Particle Size> µm, equivalent to <Filter Mesh> mesh, or better."
        ),
        "verification": "Filter Specification Review",
    },
    {
        "id": "STD-011",
        "name": "Coolant temperature range",
        "category": "Environmental / Supply",
        "reference": (
            "Defines the acceptable coolant temperature range for operation."
        ),
        "template": (
            "The customer coolant supply shall maintain a temperature between "
            "<Minimum Coolant Temperature> °C and "
            "<Maximum Coolant Temperature> °C."
        ),
        "verification": "Temperature Measurement",
    },
    {
        "id": "STD-012",
        "name": "Pneumatic consumption",
        "category": "Pneumatic Supply",
        "reference": (
            "Defines maximum free-air delivery required by each spraybar."
        ),
        "template": (
            "The pneumatic supply shall provide a maximum air consumption of "
            "<Maximum Air Consumption per Spraybar> m³/h FAD per spraybar."
        ),
        "verification": "Flow Test / Datasheet Review",
        "condition": ("Pneumatic Supply Required", "Yes"),
    },
    {
        "id": "STD-013",
        "name": "Pneumatic pressure margin",
        "category": "Pneumatic Supply",
        "reference": (
            "Ensures that air pressure remains above coolant pressure by the required margin."
        ),
        "template": (
            "The pneumatic supply pressure shall be maintained at least "
            "<Minimum Air Pressure Above Coolant> bar above the coolant pressure."
        ),
        "verification": "Pressure Test",
        "condition": ("Pneumatic Supply Required", "Yes"),
    },
    {
        "id": "STD-014",
        "name": "Air cleanliness",
        "category": "Pneumatic Supply",
        "reference": (
            "Defines minimum cleanliness class for supplied compressed air."
        ),
        "template": (
            "The pneumatic supply shall comply with <Air Cleanliness Standard>."
        ),
        "verification": "Certification / Document Review",
        "condition": ("Pneumatic Supply Required", "Yes"),
    },
    {
        "id": "STD-015",
        "name": "Electrical operating voltage",
        "category": "Electrical Supply",
        "reference": (
            "Defines nominal DC supply voltage for the ISV electrical system."
        ),
        "template": (
            "The system electrical supply shall provide <Operating Voltage> VDC."
        ),
        "verification": "Electrical Test",
        "condition": ("Electrical Supply Required", "Yes"),
    },
]


# ============================================================
# SESSION STATE
# ============================================================

if "revision" not in st.session_state:
    st.session_state.revision = "00"

if "customer_requirements" not in st.session_state:
    st.session_state.customer_requirements = []

if "saved_snapshots" not in st.session_state:
    st.session_state.saved_snapshots = []


# ============================================================
# HELPERS
# ============================================================

def key_for(input_id: str) -> str:
    return f"input__{input_id}"


def all_standard_fields() -> list[dict[str, Any]]:
    output = []
    for section_name, fields in STANDARD_SECTIONS.items():
        for field in fields:
            item = field.copy()
            item["section"] = section_name
            output.append(item)
    return output


def field_is_active(field: dict[str, Any]) -> bool:
    parent = field.get("parent")
    if not parent:
        return True
    return st.session_state.get(key_for(parent), "No") == "Yes"


def display_label(field: dict[str, Any]) -> str:
    label = field["field"]
    if field.get("required"):
        label += " *"
    if field.get("unit"):
        label += f" ({field['unit']})"
    return label


def render_widget(field: dict[str, Any], namespace: str = "std") -> Any:
    input_id = f"{namespace}_{field['id']}"
    key = key_for(input_id)
    label = display_label(field)
    help_text = field.get("help")
    default = field.get("default")
    field_type = field["type"]

    if field_type == "revision":
        st.text_input(
            label,
            value=st.session_state.revision,
            key=key,
            disabled=True,
            help=help_text,
        )
        return st.session_state.revision

    if field_type == "yesno":
        options = ["No", "Yes"]
        default_value = default if default in options else "No"
        return st.radio(
            label,
            options,
            index=options.index(default_value),
            horizontal=True,
            key=key,
            help=help_text,
        )

    if field_type == "select":
        return st.selectbox(
            label,
            field["options"],
            key=key,
            help=help_text,
        )

    if field_type == "select_other":
        selected = st.selectbox(
            label,
            field["options"],
            key=key,
            help=help_text,
        )
        if selected == "Other":
            return st.text_input(
                f"Specify other — {field['field']}",
                key=f"{key}__other",
            )
        return selected

    if field_type == "number":
        return st.number_input(
            label,
            value=float(default) if default is not None else None,
            step=0.1,
            format="%.3f",
            key=key,
            help=help_text,
        )

    if field_type == "integer":
        return st.number_input(
            label,
            min_value=0,
            value=int(default) if default is not None else None,
            step=1,
            key=key,
            help=help_text,
        )

    if field_type == "textarea":
        return st.text_area(
            label,
            value=str(default or ""),
            key=key,
            help=help_text,
            height=110,
        )

    return st.text_input(
        label,
        value=str(default or ""),
        key=key,
        help=help_text,
    )


def get_value(field: dict[str, Any], namespace: str) -> Any:
    key = key_for(f"{namespace}_{field['id']}")
    value = st.session_state.get(key, "")
    if value == "Other":
        value = st.session_state.get(f"{key}__other", "")
    return value


def collect_standard_values() -> dict[str, Any]:
    values = {}
    for field in all_standard_fields():
        value = get_value(field, "std")
        values[field["id"]] = value
        values[field["field"]] = value
    values["Revision"] = st.session_state.revision
    return values


def collect_customer_form_values() -> dict[str, Any]:
    values = {}
    for field in CUSTOMER_SPECIFIC_FIELDS:
        value = get_value(field, "cus")
        values[field["id"]] = value
        values[field["field"]] = value
    return values


def value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:g}"
    return str(value).strip()


def fill_template(template: str, values: dict[str, Any]) -> tuple[str, list[str]]:
    missing = []

    def replace(match: re.Match) -> str:
        field_name = match.group(1).strip()
        value = value_text(values.get(field_name, ""))
        if not value:
            missing.append(field_name)
            return f"⟦{field_name}⟧"
        return value

    result = re.sub(r"<([^>]+)>", replace, template)
    result = re.sub(r"\s+", " ", result).strip()
    return result, missing


def generate_standard_requirements(values: dict[str, Any]) -> pd.DataFrame:
    rows = []

    for template in STANDARD_REQUIREMENT_TEMPLATES:
        condition = template.get("condition")
        if condition:
            field_name, required_value = condition
            if value_text(values.get(field_name, "")) != required_value:
                continue

        requirement, missing = fill_template(template["template"], values)

        rows.append(
            {
                "Requirement ID": template["id"],
                "Type": "Standard",
                "Name": template["name"],
                "Category": template["category"],
                "Requirement": requirement,
                "Verification Method": template["verification"],
                "Status": "Complete" if not missing else "Needs Input",
                "Missing Inputs": ", ".join(missing),
                "Source": "Standard Requirement Template",
                "Owner": "Engineering",
                "Priority": "Standard",
                "Parent Requirement ID": "",
                "Notes": "",
            }
        )

    return pd.DataFrame(rows)


def build_customer_requirement(values: dict[str, Any]) -> str:
    system = value_text(values.get("System / Item"))
    function = value_text(values.get("Required Function"))
    obj = value_text(values.get("Object / Subject"))
    constraint = value_text(values.get("Constraint / Measurable Value"))
    condition = value_text(values.get("Operating Condition"))

    requirement = f"The {system} shall {function} {obj} {constraint}".strip()

    if condition:
        requirement += f" when {condition}"

    requirement = re.sub(r"\s+", " ", requirement).strip()

    if not requirement.endswith("."):
        requirement += "."

    return requirement


def next_customer_requirement_id() -> str:
    return f"CUS-{len(st.session_state.customer_requirements) + 1:03d}"


def customer_form_missing(values: dict[str, Any]) -> list[str]:
    missing = []
    for field in CUSTOMER_SPECIFIC_FIELDS:
        if field.get("required") and not value_text(values.get(field["field"], "")):
            missing.append(field["field"])
    return missing


def quality_checks(requirement: str) -> list[tuple[str, bool]]:
    lower = requirement.lower()

    ambiguous_terms = [
        "adequate",
        "appropriate",
        "as required",
        "etc.",
        "user-friendly",
        "sufficient",
        "normally",
        "where possible",
        "if necessary",
    ]

    return [
        ("Uses mandatory language ('shall')", "shall" in lower),
        ("Contains no unresolved placeholders", "⟦" not in requirement and "<" not in requirement),
        ("Avoids common ambiguous wording", not any(term in lower for term in ambiguous_terms)),
        ("Ends with a full stop", requirement.rstrip().endswith(".")),
        ("Is reasonably concise", len(requirement.split()) <= 60),
    ]


def standard_missing_required() -> list[str]:
    missing = []

    for field in all_standard_fields():
        if not field.get("required"):
            continue

        parent = field.get("parent")
        if parent:
            parent_field = next(
                (item for item in all_standard_fields() if item["id"] == parent),
                None,
            )
            if parent_field and value_text(get_value(parent_field, "std")) != "Yes":
                continue

        value = get_value(field, "std")
        if not value_text(value):
            missing.append(f"{field['id']} — {field['field']}")

    return missing


def combined_requirements_df() -> pd.DataFrame:
    standard_values = collect_standard_values()
    standard_df = generate_standard_requirements(standard_values)

    customer_df = pd.DataFrame(st.session_state.customer_requirements)

    if customer_df.empty:
        return standard_df

    return pd.concat([standard_df, customer_df], ignore_index=True)


def project_snapshot() -> dict[str, Any]:
    standard_values = collect_standard_values()

    return {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "revision": st.session_state.revision,
        "project": {
            "Customer": standard_values.get("Customer", ""),
            "Project Name": standard_values.get("Project Name", ""),
            "Project Number": standard_values.get("Project Number", ""),
            "Mill Name / Reference": standard_values.get("Mill Name / Reference", ""),
        },
        "standard_inputs": {
            field["field"]: standard_values.get(field["field"], "")
            for field in all_standard_fields()
        },
        "requirements": combined_requirements_df().fillna("").to_dict(orient="records"),
    }


def increment_revision() -> None:
    current = int(st.session_state.revision)
    st.session_state.revision = f"{current + 1:02d}"


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def json_bytes(data: Any) -> bytes:
    return json.dumps(data, indent=2, default=str).encode("utf-8")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="app-header">
      <h1>ISV Requirements Capture</h1>
      <p>Standard project requirements and customer-specific requirements in one controlled workflow.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

with st.sidebar:
    page = st.radio(
        "Navigate",
        [
            "Home",
            "Standard Requirements",
            "Customer-Specific Requirements",
            "Generated Requirements",
            "Review & Export",
        ],
    )

    st.divider()

    st.caption(
        "All fields, dropdowns, templates and logic are contained directly "
        "inside this single Python file."
    )


# ============================================================
# HOME
# ============================================================

if page == "Home":
    st.subheader("Requirements Capture Workflow")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="section-card">
              <h3>1. Standard Requirements</h3>
              <p>
                Capture repeatable project, mill, spraybar, cable, junction-box,
                pneumatic, supply and connection data.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="section-card">
              <h3>2. Customer-Specific Requirements</h3>
              <p>
                Capture project-specific requirements using a structured
                boilerplate sentence with source, owner, priority and verification.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            """
            <div class="section-card">
              <h3>3. Generated Requirements</h3>
              <p>
                Review standard and customer-specific requirements together,
                including long references and requirement-quality checks.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class="section-card">
              <h3>4. Review and Export</h3>
              <p>
                Check missing data, create a revision snapshot and download the
                complete requirements register as CSV or JSON.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# STANDARD REQUIREMENTS PAGE
# ============================================================

elif page == "Standard Requirements":
    st.subheader("Standard Requirement Inputs")

    section = st.selectbox(
        "Select an input section",
        list(STANDARD_SECTIONS.keys()),
    )

    st.markdown(
        f"""
        <div class="section-card">
          <h3 style="margin-top:0">{section}</h3>
          <div class="small-muted">
            Complete the applicable project data below.
            Required fields are marked with *.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    visible_fields = [
        field
        for field in STANDARD_SECTIONS[section]
        if field_is_active(field)
    ]

    col1, col2 = st.columns(2)
    columns = [col1, col2]
    column_index = 0

    for field in visible_fields:
        if field["type"] == "textarea":
            render_widget(field, namespace="std")
        else:
            with columns[column_index % 2]:
                render_widget(field, namespace="std")
            column_index += 1

    st.info(
        "Move through the sections using the selector above. "
        "Your entries remain available during the current app session."
    )


# ============================================================
# CUSTOMER-SPECIFIC REQUIREMENTS PAGE
# ============================================================

elif page == "Customer-Specific Requirements":
    st.subheader("Customer-Specific Requirement Capture")

    st.markdown(
        """
        <div class="section-card">
          <h3 style="margin-top:0">Structured Customer Requirement</h3>
          <div class="small-muted">
            Build a project-specific requirement using a controlled boilerplate.
            The completed requirement is displayed before it is added to the register.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    for index, field in enumerate(CUSTOMER_SPECIFIC_FIELDS):
        if field["type"] == "textarea":
            render_widget(field, namespace="cus")
        elif index % 2 == 0:
            with col1:
                render_widget(field, namespace="cus")
        else:
            with col2:
                render_widget(field, namespace="cus")

    customer_values = collect_customer_form_values()
    preview = build_customer_requirement(customer_values)

    st.markdown("### Long Reference")

    st.markdown(
        """
        <div class="reference-box">
          This boilerplate should be used for requirements that are specific to
          the customer, project, installation environment or sold solution.
          A good requirement should identify the responsible system or item,
          use mandatory language, state a clear function and include a measurable
          constraint or acceptance criterion. The source, owner and verification
          method are captured separately to support traceability.
          <br><br>
          <b>Boilerplate structure</b><br>
          The &lt;system / item&gt; shall &lt;required function&gt;
          &lt;object / subject&gt; &lt;constraint / measurable value&gt;
          [when &lt;operating condition&gt;].
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Full Requirement Preview")

    preview_missing = customer_form_missing(customer_values)

    preview_class = "warning-box" if preview_missing else "requirement-box"

    st.markdown(
        f'<div class="{preview_class}">{preview}</div>',
        unsafe_allow_html=True,
    )

    if preview_missing:
        st.warning("Complete the required fields: " + ", ".join(preview_missing))

    st.markdown("### Requirement Quality Check")

    for text, passed in quality_checks(preview):
        st.write(("✅" if passed else "⚠️") + " " + text)

    if st.button(
        "Add Customer Requirement",
        type="primary",
        use_container_width=True,
        disabled=bool(preview_missing),
    ):
        record = {
            "Requirement ID": next_customer_requirement_id(),
            "Type": "Customer-Specific",
            "Name": value_text(customer_values.get("Requirement Title")),
            "Category": value_text(customer_values.get("Requirement Category")),
            "Requirement": preview,
            "Verification Method": value_text(customer_values.get("Verification Method")),
            "Status": "Draft",
            "Missing Inputs": "",
            "Source": value_text(customer_values.get("Requirement Source")),
            "Owner": value_text(customer_values.get("Owner")),
            "Priority": value_text(customer_values.get("Priority")),
            "Parent Requirement ID": value_text(customer_values.get("Parent Requirement ID")),
            "Notes": value_text(customer_values.get("Additional Notes")),
            "Source Reference": value_text(customer_values.get("Source Reference")),
        }

        st.session_state.customer_requirements.append(record)

        st.success(
            f"{record['Requirement ID']} added to the customer-specific requirements register."
        )

    if st.session_state.customer_requirements:
        st.divider()
        st.markdown("### Customer-Specific Requirements Register")

        customer_df = pd.DataFrame(st.session_state.customer_requirements)

        st.dataframe(
            customer_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Requirement": st.column_config.TextColumn(width="large"),
                "Notes": st.column_config.TextColumn(width="medium"),
            },
        )

        delete_options = [
            item["Requirement ID"]
            for item in st.session_state.customer_requirements
        ]

        selected_delete = st.selectbox(
            "Select a customer requirement to remove",
            [""] + delete_options,
        )

        if st.button(
            "Remove Selected Requirement",
            disabled=not selected_delete,
        ):
            st.session_state.customer_requirements = [
                item
                for item in st.session_state.customer_requirements
                if item["Requirement ID"] != selected_delete
            ]
            st.success(f"{selected_delete} removed.")
            st.rerun()


# ============================================================
# GENERATED REQUIREMENTS PAGE
# ============================================================

elif page == "Generated Requirements":
    standard_values = collect_standard_values()
    standard_df = generate_standard_requirements(standard_values)
    customer_df = pd.DataFrame(st.session_state.customer_requirements)

    st.subheader("Generated Requirements")

    tab1, tab2, tab3 = st.tabs(
        [
            "Standard Requirements",
            "Customer-Specific Requirements",
            "Combined Register",
        ]
    )

    with tab1:
        if standard_df.empty:
            st.info("No standard requirements are available.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Generated", len(standard_df))
            m2.metric(
                "Complete",
                int((standard_df["Status"] == "Complete").sum()),
            )
            m3.metric(
                "Needs Input",
                int((standard_df["Status"] == "Needs Input").sum()),
            )

            selected_index = st.selectbox(
                "Select a standard requirement",
                range(len(standard_df)),
                format_func=lambda i: (
                    f"{standard_df.iloc[i]['Requirement ID']} — "
                    f"{standard_df.iloc[i]['Name']}"
                ),
            )

            selected_row = standard_df.iloc[selected_index]

            selected_template = next(
                template
                for template in STANDARD_REQUIREMENT_TEMPLATES
                if template["id"] == selected_row["Requirement ID"]
            )

            st.markdown("### Long Reference")

            st.markdown(
                f"""
                <div class="reference-box">
                    {selected_template['reference']}
                    <br><br>
                    <b>Boilerplate template</b><br>
                    {selected_template['template']}
                    <br><br>
                    <span class="small-muted">
                        Suggested verification: {selected_template['verification']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### Full Requirement")

            box_class = (
                "requirement-box"
                if selected_row["Status"] == "Complete"
                else "warning-box"
            )

            st.markdown(
                f'<div class="{box_class}">{selected_row["Requirement"]}</div>',
                unsafe_allow_html=True,
            )

            if selected_row["Missing Inputs"]:
                st.warning(
                    f"Missing input(s): {selected_row['Missing Inputs']}"
                )

            st.markdown("### Requirement Quality Check")

            for text, passed in quality_checks(selected_row["Requirement"]):
                st.write(("✅" if passed else "⚠️") + " " + text)

            st.divider()

            st.dataframe(
                standard_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Requirement": st.column_config.TextColumn(width="large"),
                    "Missing Inputs": st.column_config.TextColumn(width="medium"),
                },
            )

    with tab2:
        if customer_df.empty:
            st.info(
                "No customer-specific requirements have been added yet."
            )
        else:
            st.dataframe(
                customer_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Requirement": st.column_config.TextColumn(width="large"),
                    "Notes": st.column_config.TextColumn(width="medium"),
                },
            )

    with tab3:
        combined_df = combined_requirements_df()

        st.dataframe(
            combined_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Requirement": st.column_config.TextColumn(width="large"),
                "Notes": st.column_config.TextColumn(width="medium"),
            },
        )


# ============================================================
# REVIEW AND EXPORT PAGE
# ============================================================

else:
    standard_missing = standard_missing_required()
    combined_df = combined_requirements_df()

    st.subheader("Review and Export")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Standard Requirements",
        int((combined_df["Type"] == "Standard").sum())
        if not combined_df.empty
        else 0,
    )

    c2.metric(
        "Customer-Specific Requirements",
        int((combined_df["Type"] == "Customer-Specific").sum())
        if not combined_df.empty
        else 0,
    )

    c3.metric(
        "Missing Required Standard Inputs",
        len(standard_missing),
    )

    if standard_missing:
        with st.expander("Missing Required Standard Inputs", expanded=True):
            for item in standard_missing:
                st.write("⚠️", item)
    else:
        st.success("All currently applicable required standard inputs are complete.")

    standard_values = collect_standard_values()

    st.markdown("### Project Summary")

    st.json(
        {
            "Customer": value_text(standard_values.get("Customer")),
            "Project Name": value_text(standard_values.get("Project Name")),
            "Project Number": value_text(standard_values.get("Project Number")),
            "Mill Name / Reference": value_text(
                standard_values.get("Mill Name / Reference")
            ),
            "Revision": st.session_state.revision,
        }
    )

    left, middle, right = st.columns(3)

    with left:
        if st.button(
            "Save Revision in Session",
            type="primary",
            use_container_width=True,
        ):
            snapshot = project_snapshot()
            st.session_state.saved_snapshots.append(snapshot)

            saved_revision = st.session_state.revision
            increment_revision()

            st.success(
                f"Revision {saved_revision} saved in the current session. "
                f"Working revision is now {st.session_state.revision}."
            )

    with middle:
        st.download_button(
            "Download Requirements CSV",
            data=csv_bytes(combined_df),
            file_name="isv_requirements_register.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with right:
        st.download_button(
            "Download Full Project JSON",
            data=json_bytes(project_snapshot()),
            file_name="isv_project_data.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("### Complete Requirements Register")

    if combined_df.empty:
        st.info("No requirements are available.")
    else:
        st.dataframe(
            combined_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Requirement": st.column_config.TextColumn(width="large"),
                "Notes": st.column_config.TextColumn(width="medium"),
            },
        )

    if st.session_state.saved_snapshots:
        st.divider()
        st.markdown("### Revisions Saved in This Session")

        revision_table = pd.DataFrame(
            [
                {
                    "Revision": item["revision"],
                    "Saved At": item["saved_at"],
                    "Project Number": item["project"]["Project Number"],
                    "Project Name": item["project"]["Project Name"],
                }
                for item in st.session_state.saved_snapshots
            ]
        )

        st.dataframe(
            revision_table,
            use_container_width=True,
            hide_index=True,
        )