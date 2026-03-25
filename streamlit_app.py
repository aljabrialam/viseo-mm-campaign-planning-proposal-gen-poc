import streamlit as st
import requests
import json
from fpdf import FPDF
from io import BytesIO
import pandas as pd
import os

FUNCTION_URL = st.secrets["AZURE_FUNCTION_URL"]
FUNCTION_KEY = st.secrets["AZURE_FUNCTION_KEY"]


class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 16)
        self.cell(0, 10, "Media Planner Proposal Generator", 0, 1, "C")
        self.ln(5)

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title="Media Planner Proposal Generator", layout="wide")
st.title("Media Planner Proposal Generator")
st.subheader("AI Campaign Planning + Proposal Generator")

# Logo placeholder
st.image("logo.png", width=350)  # replace with your actual logo path

# ---------------------------
# Sample Prompts
# ---------------------------
sample_prompts = [
    "Client wants 120,000 impressions with 60,000 SGD budget for May 1–15.",
    "Client wants 80,000 impressions with 40,000 SGD budget for June 1–30.",
    "Client wants 200,000 impressions with 100,000 SGD budget for July 1–15."
]

selected_prompt = st.selectbox(
    "Select a sample campaign prompt:",
    options=sample_prompts
)

prompt = st.text_area("Or edit your campaign prompt:", value=selected_prompt)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date")
with col2:
    end_date = st.date_input("End Date")

def clean_text(text):
    if not text:
        return ""
    return str(text).replace("–", "-").replace("—", "-")

# ---------------------------
# Architecture Image & Description
# ---------------------------
st.subheader("Architecture Overview")
st.image("media-planner-ai-architecture.png", width=700, caption="POC Architecture: Cognitive Search + AI Model")
st.markdown("""
This POC demonstrates an AI-powered media planning system. The **architecture** combines:

- **Azure Cognitive Search**: Stores media inventory and enables efficient search queries.
- **AI Models (OpenAI / Anthropic)**: Extract campaign requirements from free-text prompts.
- The system **selects media** under budget and generates a proposal with rationale and recommendations.
""")

# ---------------------------
# Sample Media Inventory Table
# ---------------------------
st.subheader("Sample Media Inventory Data (POC)")
sample_data = [
  {
    "id": "1",
    "type": "digital",
    "location": "bus interchange screen - Orchard Road",
    "total_slots": 10,
    "used_slots": 5,
    "unit_cost": 5000,
    "impressions": 22000,
    "audience_score": 0.92,
    "demographics": "urban adults, commuters",
    "reach_score": 0.87,
    "available_slots": 5,
    "start_date": "2026-03-25",
    "end_date": "2026-06-30"
  },
  {
    "id": "2",
    "type": "bus exterior",
    "location": "city bus #12 - Downtown Route",
    "total_slots": 12,
    "used_slots": 6,
    "unit_cost": 4500,
    "impressions": 18000,
    "audience_score": 0.88,
    "demographics": "urban adults, commuters",
    "reach_score": 0.82,
    "available_slots": 6,
    "start_date": "2026-04-01",
    "end_date": "2026-06-30"
  },
  {
    "id": "3",
    "type": "digital",
    "location": "mall digital screen - Marina Bay Sands",
    "total_slots": 8,
    "used_slots": 3,
    "unit_cost": 4000,
    "impressions": 15000,
    "audience_score": 0.85,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.8,
    "available_slots": 5,
    "start_date": "2026-03-15",
    "end_date": "2026-05-31"
  },
  {
    "id": "4",
    "type": "digital",
    "location": "rail station screen - Raffles Place",
    "total_slots": 6,
    "used_slots": 2,
    "unit_cost": 3500,
    "impressions": 12000,
    "audience_score": 0.9,
    "demographics": "urban adults, commuters",
    "reach_score": 0.83,
    "available_slots": 4,
    "start_date": "2026-03-20",
    "end_date": "2026-06-15"
  },
  {
    "id": "5",
    "type": "bus exterior",
    "location": "city bus #23 - East Coast Route",
    "total_slots": 10,
    "used_slots": 7,
    "unit_cost": 4000,
    "impressions": 16000,
    "audience_score": 0.86,
    "demographics": "urban adults, commuters",
    "reach_score": 0.81,
    "available_slots": 3,
    "start_date": "2026-04-05",
    "end_date": "2026-06-30"
  },
  {
    "id": "6",
    "type": "digital",
    "location": "taxi tablet screen - CBD Area",
    "total_slots": 15,
    "used_slots": 10,
    "unit_cost": 3000,
    "impressions": 10000,
    "audience_score": 0.78,
    "demographics": "urban adults, professionals",
    "reach_score": 0.75,
    "available_slots": 5,
    "start_date": "2026-03-10",
    "end_date": "2026-05-31"
  },
  {
    "id": "7",
    "type": "static",
    "location": "rail exterior - Circle Line Train",
    "total_slots": 8,
    "used_slots": 3,
    "unit_cost": 6000,
    "impressions": 25000,
    "audience_score": 0.89,
    "demographics": "urban adults, commuters",
    "reach_score": 0.86,
    "available_slots": 5,
    "start_date": "2026-03-01",
    "end_date": "2026-06-30"
  },
  {
    "id": "8",
    "type": "digital",
    "location": "bus interchange screen - VivoCity",
    "total_slots": 6,
    "used_slots": 1,
    "unit_cost": 4500,
    "impressions": 20000,
    "audience_score": 0.91,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.85,
    "available_slots": 5,
    "start_date": "2026-03-25",
    "end_date": "2026-06-30"
  },
  {
    "id": "9",
    "type": "digital",
    "location": "mall digital screen - Bugis Junction",
    "total_slots": 5,
    "used_slots": 2,
    "unit_cost": 3800,
    "impressions": 14000,
    "audience_score": 0.84,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.78,
    "available_slots": 3,
    "start_date": "2026-04-01",
    "end_date": "2026-05-31"
  },
  {
    "id": "10",
    "type": "taxi rooftop",
    "location": "taxi #452 - Orchard Area",
    "total_slots": 5,
    "used_slots": 0,
    "unit_cost": 2500,
    "impressions": 8000,
    "audience_score": 0.75,
    "demographics": "urban adults, commuters",
    "reach_score": 0.7,
    "available_slots": 5,
    "start_date": "2026-03-20",
    "end_date": "2026-06-15"
  },
  {
    "id": "11",
    "type": "bus exterior",
    "location": "city bus #45 - Marina Bay Route",
    "total_slots": 12,
    "used_slots": 4,
    "unit_cost": 4700,
    "impressions": 21000,
    "audience_score": 0.9,
    "demographics": "urban adults, commuters",
    "reach_score": 0.88,
    "available_slots": 8,
    "start_date": "2026-04-05",
    "end_date": "2026-06-30"
  },
  {
    "id": "12",
    "type": "digital",
    "location": "mall digital screen - Suntec City",
    "total_slots": 7,
    "used_slots": 2,
    "unit_cost": 4200,
    "impressions": 18000,
    "audience_score": 0.87,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.82,
    "available_slots": 5,
    "start_date": "2026-03-15",
    "end_date": "2026-06-15"
  },
  {
    "id": "13",
    "type": "digital",
    "location": "bus interchange screen - Bugis",
    "total_slots": 5,
    "used_slots": 0,
    "unit_cost": 4000,
    "impressions": 16000,
    "audience_score": 0.88,
    "demographics": "urban adults, commuters",
    "reach_score": 0.81,
    "available_slots": 5,
    "start_date": "2026-03-25",
    "end_date": "2026-05-31"
  },
  {
    "id": "14",
    "type": "taxi rooftop",
    "location": "taxi #765 - Marina Bay",
    "total_slots": 6,
    "used_slots": 1,
    "unit_cost": 2600,
    "impressions": 9000,
    "audience_score": 0.76,
    "demographics": "urban adults, commuters",
    "reach_score": 0.72,
    "available_slots": 5,
    "start_date": "2026-03-20",
    "end_date": "2026-06-10"
  },
  {
    "id": "15",
    "type": "rail exterior",
    "location": "Downtown Line Train #3",
    "total_slots": 8,
    "used_slots": 2,
    "unit_cost": 5800,
    "impressions": 24000,
    "audience_score": 0.88,
    "demographics": "urban adults, commuters",
    "reach_score": 0.85,
    "available_slots": 6,
    "start_date": "2026-03-15",
    "end_date": "2026-06-30"
  },
  {
    "id": "16",
    "type": "digital",
    "location": "mall digital screen - City Square",
    "total_slots": 6,
    "used_slots": 2,
    "unit_cost": 3500,
    "impressions": 13000,
    "audience_score": 0.83,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.8,
    "available_slots": 4,
    "start_date": "2026-04-01",
    "end_date": "2026-06-15"
  },
  {
    "id": "17",
    "type": "bus exterior",
    "location": "city bus #88 - West Coast Route",
    "total_slots": 10,
    "used_slots": 5,
    "unit_cost": 4300,
    "impressions": 17000,
    "audience_score": 0.87,
    "demographics": "urban adults, commuters",
    "reach_score": 0.82,
    "available_slots": 5,
    "start_date": "2026-04-05",
    "end_date": "2026-06-30"
  },
  {
    "id": "18",
    "type": "digital",
    "location": "taxi tablet screen - Marina Bay",
    "total_slots": 12,
    "used_slots": 8,
    "unit_cost": 3100,
    "impressions": 12000,
    "audience_score": 0.79,
    "demographics": "urban adults, professionals",
    "reach_score": 0.75,
    "available_slots": 4,
    "start_date": "2026-03-25",
    "end_date": "2026-06-10"
  },
  {
    "id": "19",
    "type": "static",
    "location": "rail exterior - North-East Line Train",
    "total_slots": 6,
    "used_slots": 3,
    "unit_cost": 5800,
    "impressions": 23000,
    "audience_score": 0.87,
    "demographics": "urban adults, commuters",
    "reach_score": 0.83,
    "available_slots": 3,
    "start_date": "2026-03-20",
    "end_date": "2026-06-30"
  },
  {
    "id": "20",
    "type": "digital",
    "location": "bus interchange screen - Suntec",
    "total_slots": 5,
    "used_slots": 1,
    "unit_cost": 4200,
    "impressions": 15000,
    "audience_score": 0.85,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.8,
    "available_slots": 4,
    "start_date": "2026-03-25",
    "end_date": "2026-06-15"
  },
  {
    "id": "21",
    "type": "taxi rooftop",
    "location": "taxi #112 - Orchard Area",
    "total_slots": 5,
    "used_slots": 1,
    "unit_cost": 2600,
    "impressions": 9500,
    "audience_score": 0.77,
    "demographics": "urban adults, commuters",
    "reach_score": 0.72,
    "available_slots": 4,
    "start_date": "2026-03-15",
    "end_date": "2026-06-15"
  },
  {
    "id": "22",
    "type": "bus exterior",
    "location": "city bus #90 - East Coast Route",
    "total_slots": 8,
    "used_slots": 4,
    "unit_cost": 4400,
    "impressions": 18000,
    "audience_score": 0.86,
    "demographics": "urban adults, commuters",
    "reach_score": 0.81,
    "available_slots": 4,
    "start_date": "2026-04-01",
    "end_date": "2026-06-30"
  },
  {
    "id": "23",
    "type": "digital",
    "location": "mall digital screen - VivoCity Extension",
    "total_slots": 6,
    "used_slots": 3,
    "unit_cost": 3900,
    "impressions": 16000,
    "audience_score": 0.84,
    "demographics": "urban adults, shoppers",
    "reach_score": 0.79,
    "available_slots": 3,
    "start_date": "2026-03-20",
    "end_date": "2026-06-10"
  },
  {
    "id": "24",
    "type": "digital",
    "location": "rail station screen - Chinatown",
    "total_slots": 5,
    "used_slots": 1,
    "unit_cost": 3600,
    "impressions": 14000,
    "audience_score": 0.82,
    "demographics": "urban adults, commuters",
    "reach_score": 0.78,
    "available_slots": 4,
    "start_date": "2026-03-25",
    "end_date": "2026-06-15"
  },
  {
    "id": "25",
    "type": "bus exterior",
    "location": "city bus #100 - North-South Route",
    "total_slots": 10,
    "used_slots": 5,
    "unit_cost": 4700,
    "impressions": 20000,
    "audience_score": 0.88,
    "demographics": "urban adults, commuters",
    "reach_score": 0.85,
    "available_slots": 5,
    "start_date": "2026-04-01",
    "end_date": "2026-06-30"
  }
]

sample_df = pd.DataFrame(sample_data)
# Select key columns for display
display_cols = ["id", "type", "location", "unit_cost", "impressions", "audience_score", "reach_score", "available_slots", "start_date", "end_date"]
sample_df_display = sample_df[display_cols]
sample_df_display.columns = ["ID", "Type", "Location", "Cost", "Impressions", "Audience Score", "Reach Score", "Available Slots", "Start Date", "End Date"]

st.dataframe(sample_df_display, use_container_width=True)
st.markdown("""
This table shows the **sample data** used by Cognitive Search in the POC. 
The AI model selects media based on **budget, impressions, and availability**, and generates a campaign proposal.
""")

# ---------------------------
# Generate Campaign
# ---------------------------
if st.button("Generate Campaign Proposal"):
    if not prompt.strip():
        st.warning("Please enter a campaign prompt.")
    else:
        with st.spinner("Generating campaign proposal..."):
            try:
                payload = {
                    "prompt": prompt,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                response = requests.post(
                    f"{FUNCTION_URL}?code={FUNCTION_KEY}",
                    json=payload
                )

                st.text("Backend raw response:")
                st.text(response.text)

                try:
                    data = response.json()
                except json.JSONDecodeError:
                    st.error(f"Invalid response from backend:\n{response.text}")
                    st.stop()

                if response.status_code != 200:
                    st.error(f"Error from backend: {data.get('error')}")
                else:
                    # Selected Media Table
                    st.subheader("Selected Media")
                    if data["selected_media"]:
                        media_df = pd.DataFrame(data["selected_media"])
                        media_df = media_df[["id", "type", "location", "unit_cost", "impressions"]]
                        media_df.columns = ["ID", "Type", "Location", "Cost", "Impressions"]
                        st.dataframe(media_df, use_container_width=True)
                    else:
                        st.info("No media selected for this campaign.")

                    st.markdown(f"**Total Impressions:** {data['total_impressions']}")
                    st.markdown(f"**Total Cost:** {data['total_cost']} SGD")

                    # Campaign Proposal Table
                    st.subheader("Campaign Proposal")
                    proposal = data["proposal"]
                    proposal_dict = {
                        "Summary": proposal.get('summary'),
                        "Rationale": proposal.get('rationale'),
                        "Recommendations": proposal.get('recommendations'),
                        "Goal Impressions": proposal.get('goal_impressions')
                    }
                    proposal_df = pd.DataFrame(proposal_dict.items(), columns=["Field", "Details"])
                    st.table(proposal_df)

                    # Generate PDF
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=10)
                    pdf.add_page()

                    # ✅ Proper font registration (IMPORTANT)
                    font_path = "DejaVuSans.ttf"  # Make sure this file exists in your project
                    bold_font_path = "DejaVuSans-Bold.ttf"

                    pdf.add_font("DejaVu", "", font_path, uni=True)
                    pdf.add_font("DejaVu", "B", bold_font_path, uni=True)

                    # ---------------------------
                    # Title
                    # ---------------------------
                    pdf.set_font("DejaVu", "B", 16)
                    pdf.cell(0, 10, "Media Planner Proposal Generator", ln=True)

                    pdf.set_font("DejaVu", "", 12)
                    pdf.cell(0, 8, "AI Campaign Planning + Proposal Generator", ln=True)
                    pdf.ln(5)

                    # ---------------------------
                    # Summary
                    # ---------------------------
                    pdf.set_font("DejaVu", "", 11)
                    pdf.cell(0, 8, f"Goal Impressions: {proposal.get('goal_impressions')}", ln=True)
                    pdf.cell(0, 8, f"Total Cost: {data['total_cost']} SGD", ln=True)
                    pdf.ln(5)

                    # ---------------------------
                    # Table Header
                    # ---------------------------
                    pdf.set_font("DejaVu", "B", 10)
                    col_widths = [10, 25, 80, 30, 30]

                    headers = ["ID", "Type", "Location", "Cost", "Impressions"]
                    for i, h in enumerate(headers):
                        pdf.cell(col_widths[i], 8, h, border=1)
                    pdf.ln()

                    # ---------------------------
                    # Table Rows (SAFE WRAP)
                    # ---------------------------
                    pdf.set_font("DejaVu", "", 9)

                    for m in data["selected_media"]:
                        row = [
                            str(m["id"]),
                            clean_text(m["type"]),
                            clean_text(m["location"]),
                            f"{m['unit_cost']}",
                            f"{m['impressions']}"
                        ]

                        # Calculate max height for row
                        max_lines = 1
                        for i, cell in enumerate(row):
                            lines = pdf.multi_cell(col_widths[i], 5, cell, border=0, split_only=True)
                            max_lines = max(max_lines, len(lines))

                        row_height = 5 * max_lines

                        x_start = pdf.get_x()
                        y_start = pdf.get_y()

                        for i, cell in enumerate(row):
                            x_current = pdf.get_x()
                            y_current = pdf.get_y()

                            pdf.multi_cell(col_widths[i], 5, cell, border=1)
                            pdf.set_xy(x_current + col_widths[i], y_current)

                        pdf.ln(row_height)

                    pdf.ln(5)

                    # ---------------------------
                    # Proposal Section
                    # ---------------------------
                    pdf.set_font("DejaVu", "B", 12)
                    pdf.cell(0, 8, "Campaign Proposal", ln=True)

                    pdf.set_font("DejaVu", "", 10)

                    pdf.multi_cell(0, 6, f"Summary: {clean_text(proposal.get('summary'))}")
                    pdf.ln(1)

                    pdf.multi_cell(0, 6, f"Rationale: {clean_text(proposal.get('rationale'))}")
                    pdf.ln(1)

                    pdf.multi_cell(0, 6, f"Recommendations: {clean_text(proposal.get('recommendations'))}")

                    # ---------------------------
                    # Output FIX (NO encode!!)
                    # ---------------------------
                    pdf_bytes = pdf.output(dest="S")  # already bytes-like
                    pdf_buffer = BytesIO(pdf_bytes)

                    st.download_button(
                        label="Download Campaign Proposal PDF",
                        data=pdf_buffer,
                        file_name="campaign_proposal.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
st.write("") 
st.write("") 
# Engineered by 
st.markdown("Engineered By:")               
st.image("alj-sig.png", width=250)