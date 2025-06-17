from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import streamlit_shadcn_ui as ui
from streamlit_extras.switch_page_button import switch_page
from menu import menu_home
import requests

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Home",
    page_icon="🌍",
)

# --- Menu ---
menu_home()

# --- Path Settings ---
THIS_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
STYLES_DIR = THIS_DIR / "styles"
CSS_FILE = STYLES_DIR / "main.css"

# --- Global Variables ---
CONTACT_EMAIL = "andersonb97@gmail.com"
APP_URL = "https://saas-starter.streamlit.app"

# --- User Authentication ---
if 'user' in st.session_state and st.session_state['user']:
    st.sidebar.markdown(f"*Welcome **{st.session_state['user']['email']}***")

# --- Load CSS ---
def load_css_file(css_file_path):
    with open(css_file_path) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css_file(CSS_FILE)

# --- Helper Functions ---
def add_vertical_space(height):
    st.markdown(f'<div style="height: {height}px;"></div>', unsafe_allow_html=True)


# --- Logo and Title ---
logo = "public/smartr-logo.png"
with st.columns(3)[1]:
    st.image(logo)

st.markdown(
    f"""
    <div style="text-align: center;">
        <h1 style="margin-top: 10px;">SaaS Template</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style="text-align: center;">
        <h3 style="margin-top: 10px;">
            Smartr is your personal, real-time interview coach—powered by AI to simulate live interviews and deliver tailored feedback that helps you get better, faster.
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Load SVG ---
def load_svg(svg_file):
    return Path(svg_file).read_text()


add_vertical_space(200)

# --- Cloud Logo ---
github_svg_url = "https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg"
streamlit_svg_url = "https://streamlit.io/images/brand/streamlit-mark-color.svg"
stripe_svg_url = "https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg"
supabase_svg_url = "https://www.vectorlogo.zone/logos/supabase/supabase-icon.svg"

cloud_logo_html = f"""
<div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 10px;">
    <div style="flex-basis: 10%; text-align: center;">
        <img src="{github_svg_url}" alt="GitHub Logo" style="width: 50px; height: auto;">
    </div>
    <div style="flex-basis: 10%; text-align: center;">
        <img src="{streamlit_svg_url}" alt="Streamlit Logo" style="width: 50px; height: auto;">
    </div>
    <div style="flex-basis: 10%; text-align: center;">
        <img src="{stripe_svg_url}" alt="Stripe Logo" style="width: 50px; height: auto;">
    </div>
    <div style="flex-basis: 10%; text-align: center;">
        <img src="{supabase_svg_url}" alt="Supabase Logo" style="width: 50px; height: auto;">
    </div>
</div>
"""

st.markdown(f'<div style="text-align: center;">Built with the following brands: </div>', unsafe_allow_html=True)
st.markdown(cloud_logo_html, unsafe_allow_html=True)

add_vertical_space(50)

# --- Features Section ---
st.write("")
st.write("---")
st.subheader("Features")

# Feature 1: Live Interview Experience
cols1 = st.columns(2)
with cols1[0]:
    st.markdown("#### Live Interview Experience")
    st.markdown("##### Real-Time AI-Powered Simulation")
    st.markdown("""
Smartr uses cutting-edge large language models to simulate realistic interview conversations in real time.

Key Features:
- **Interactive Interview Practice**: Engage in live Q&A with an AI interviewer that adapts dynamically.
- **Voice and Text Input**: Practice naturally with voice responses.
- **Instant Response Generation**: The AI reacts immediately to keep the flow realistic.
- **Boost Confidence**: Experience the pressure and pace of real interviews from anywhere.
    """)
with cols1[1]:
    st.image("public/demo-1.png", use_column_width=True)

add_vertical_space(50)

# Feature 2: Tailored Feedback for Growth
st.write("")
st.write("---")

cols2 = st.columns(2)
with cols2[0]:
    st.markdown("#### Tailored Feedback for Growth")
    st.markdown("##### Personalized Insights to Prepare You")
    st.markdown("""
After every practice session, Smartr delivers customized feedback designed to help you improve faster and build confidence.

Key Features:
- **Detailed Performance Analysis**: Understand your strengths and areas to improve.
- **Actionable Tips**: Get specific, personalized suggestions on how to refine your answers.
- **Track Your Progress**: Review past feedback to measure improvement over time.
- **Motivate Your Journey**: Stay engaged with meaningful growth milestones.
    """)
with cols2[1]:
    st.image("public/demo-2.png", use_column_width=True)


# # --- Demo Section ---
# st.write("")
# st.write("---")
# st.subheader("Demo")
# DEMO_VIDEO = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# st.video(DEMO_VIDEO, format="video/mp4", start_time=0)

# # --- Pricing Section ---
# st.write("")
# st.write("---")
# st.subheader("Pricing")

# stripe_link_starter = st.secrets["stripe_link_starter"]
# stripe_link_teams = st.secrets["stripe_link_teams"]
# stripe_link_enterprise = st.secrets["stripe_link_enterprise"]

# cols = st.columns(3)
# with cols[0]:
#     with ui.card(key="pricing1"):
#         ui.element("span", children=["Starter"], className="text-sm font-medium m-2", key="pricing_starter_0")
#         ui.element("h1", children=["$0 per month"], className="text-2xl font-bold m-2", key="pricing_starter_1")
#         ui.element("link_button", key="nst2_btn", text="Subscribe", variant="default", className="h-10 w-full rounded-md m-2", url=stripe_link_starter)
#         ui.element("p", children=["Ideal for individual users who want to get started with the Streamlit SaaS Template."], 
#                     className="text-xs font-medium m-2 mt-2 mb-2", key="pricing_starter_2")
#         ui.element("p", children=["This includes: "], 
#                     className="text-muted-foreground text-xs font-medium m-2", key="pricing_starter_3")
#         ui.element("p", children=["- Access to all basic features."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_starter_4")
#         ui.element("p", children=["- Community support."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_starter_5")
#         ui.element("p", children=["- 1 active project."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_starter_6")

# with cols[1]:
#     with ui.card(key="pricing2"):
#         ui.element("span", children=["Teams"], className="text-sm font-medium m-2", key="pricing_pro_0")
#         ui.element("h1", children=["$100 per month"], className="text-2xl font-bold m-2", key="pricing_pro_1")
#         ui.element("link_button", key="nst2_btn", text="Subscribe", variant="default", className="h-10 w-full rounded-md m-2", url=stripe_link_teams)
#         ui.element("p", children=["Perfect for small businesses requiring advanced features."], 
#                     className="text-xs font-medium m-2 mt-2 mb-2", key="pricing_pro_2")
#         ui.element("p", children=["This includes: "], 
#                     className="text-muted-foreground text-xs font-medium m-2", key="pricing_pro_3")
#         ui.element("p", children=["- 10GB Storage Access."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_pro_4")
#         ui.element("p", children=["- 625,000 API calls per month."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_pro_5")
#         ui.element("p", children=["- 10 active projects."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_pro_6")
#         ui.element("p", children=["- Priority email support."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_pro_7")

# with cols[2]:
#     with ui.card(key="pricing3"):
#         ui.element("span", children=["Enterprise"], className="text-sm font-medium m-2", key="pricing_enterprise_0")
#         ui.element("h1", children=["$500 per month"], className="text-2xl font-bold m-2", key="pricing_enterprise_1")
#         ui.element("link_button", key="nst2_btn", text="Subscribe", variant="default", className="h-10 w-full rounded-md m-2", url=stripe_link_enterprise)
#         ui.element("p", children=["Designed for large companies and teams with specific needs."], 
#                     className="text-xs font-medium m-2", key="pricing_enterprise_2")
#         ui.element("p", children=["This includes: "], 
#                     className="text-muted-foreground text-xs font-medium m-2", key="pricing_enterprise_3")        
#         ui.element("p", children=["- 50GB Storage Access."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_enterprise_4")
#         ui.element("p", children=["- Unlimited API calls per month."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_enterprise_5")
#         ui.element("p", children=["- Unlimited active projects."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_enterprise_6")
#         ui.element("p", children=["- Dedicated account manager."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_enterprise_7")
#         ui.element("p", children=["- 24/7 priority support."], 
#                     className="text-muted-foreground text-xs font-medium m-1", key="pricing_enterprise_8")

# --- FAQ Section ---
st.write("")
st.write("---")
st.subheader("FAQ")

faq = {
    "What is Smartr?": (
        "Smartr is an AI-powered platform designed to help you practice real-time technical "
        "interviews and receive personalized feedback, so you can confidently prepare and "
        "ace your next interview."
    ),
    "How does Smartr work?": (
        "Smartr simulates live interview experiences using advanced language models, allowing "
        "you to practice answering questions in real-time. After each session, Smartr provides "
        "tailored feedback to help you identify strengths and areas for improvement."
    ),
    "Who can benefit from Smartr?": (
        "Whether you're a new grad, an experienced professional, or switching careers, Smartr "
        "helps anyone preparing for technical interviews gain confidence and improve their skills."
    ),
    "What makes Smartr different from other interview prep tools?": (
        "Unlike static question banks, Smartr offers dynamic, interactive interview simulations "
        "and personalized feedback driven by AI, making your practice sessions more realistic and actionable."
    ),
    "Is Smartr easy to use for non-technical users?": (
        "Absolutely! Smartr is designed with simplicity in mind, offering an intuitive interface "
        "that’s welcoming for both technical and non-technical users."
    ),
    "How do I get started with Smartr?": (
        "Simply sign up for an account, upload your target job description, and start practicing "
        "right away with live AI-powered simulations."
    )
}

for question, answer in faq.items():
    with st.expander(question):
        st.write(answer)

# --- Contact Form ---
# video tutorial: https://youtu.be/FOULV9Xij_8
st.write("")
st.write("---")
st.subheader(":mailbox: Have A Question? Ask Away!")
# Create the form using ui.input and ui.textarea
name_input = ui.input(default_value="", placeholder="Your name", key="name_input")
email_input = ui.input(default_value="", placeholder="Your email", key="email_input")
message_input = ui.textarea(default_value="", placeholder="Your Message Here", key="message_input")

st.write("---")  # Separator
submit_button = st.button("Submit")

# Check if the submit button is clicked
if submit_button:
    st.write("Message sent!")
    # st.write("Name:", name_input)
    # st.write("Email:", email_input)
    # st.write("Message:", message_input)

    # JavaScript to dynamically create a hidden form and submit it
    st.markdown(
        f"""
        <script>
        // Create a hidden form
        var form = document.createElement("form");
        form.setAttribute("method", "post");
        form.setAttribute("action", "https://formsubmit.co/{CONTACT_EMAIL}");

        // Add hidden input fields
        var inputName = document.createElement("input");
        inputName.setAttribute("type", "hidden");
        inputName.setAttribute("name", "name");
        inputName.setAttribute("value", "{name_input}");
        form.appendChild(inputName);

        var inputEmail = document.createElement("input");
        inputEmail.setAttribute("type", "hidden");
        inputEmail.setAttribute("name", "email");
        inputEmail.setAttribute("value", "{email_input}");
        form.appendChild(inputEmail);

        var inputMessage = document.createElement("input");
        inputMessage.setAttribute("type", "hidden");
        inputMessage.setAttribute("name", "message");
        inputMessage.setAttribute("value", "{message_input}");
        form.appendChild(inputMessage);

        // Add the hidden form to the body and submit it
        document.body.appendChild(form);
        form.submit();
        </script>
        """,
        unsafe_allow_html=True
    )