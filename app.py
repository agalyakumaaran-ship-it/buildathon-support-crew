
import os
import re
import streamlit as st
import pandas as pd

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from crewai_tools import SerperDevTool

from database import (
    initialize_database,
    save_ticket,
    get_all_tickets
)


# =====================================================
# 1. CONFIGURATION
# =====================================================

load_dotenv()

st.set_page_config(
    page_title="YAAZHI AI",
    page_icon="🎵",
    layout="wide"
)

initialize_database()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is missing from your .env file.")
    st.stop()

if not os.getenv("SERPER_API_KEY"):
    st.error("SERPER_API_KEY is missing from your .env file.")
    st.stop()


# =====================================================
# 2. YAAZHI AI DESIGN
# =====================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #f4f8ff,
        #fff3fa,
        #f1fff5
    );
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #172554;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #475569;
    font-size: 17px;
}

.section-title {
    color: #1e3a8a;
    font-size: 23px;
    font-weight: 700;
}

.info-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border-left: 6px solid #3b82f6;
    box-shadow: 0 5px 15px rgba(0,0,0,0.07);
    margin-bottom: 15px;
}

.success-card {
    background: #dcfce7;
    padding: 18px;
    border-radius: 14px;
    color: #14532d;
}

.warning-card {
    background: #fef3c7;
    padding: 18px;
    border-radius: 14px;
    color: #78350f;
}

.stButton > button {
    background: linear-gradient(
        90deg,
        #2563eb,
        #db2777
    );
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
    padding: 10px 20px;
}

.stButton > button:hover {
    color: white;
    border: 1px solid #2563eb;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. APPLICATION HEADER
# =====================================================


# =====================================================
# 3. APPLICATION HEADER WITH YAAZHI IMAGE
# =====================================================


# =====================================================
# 3. APPLICATION HEADER WITH SIDE-BY-SIDE IMAGE
# =====================================================

import os

image_path = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "yaazhi_reference.png"
)

col1, col2 = st.columns([1, 3])

with col1:
    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
        st.image(image_path, width=160)
    else:
        st.warning("Please add a valid Yaazhi image to assets.")

with col2:
    st.markdown(
        '<div class="main-title" style="text-align:left;">'
        '🎵 YAAZHI AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle" style="text-align:left;">'
        'Where Every Conversation Finds Its Harmony'
        '</div>',
        unsafe_allow_html=True
    )

st.write("")

st.markdown("""
<div class="info-card">
Welcome to YAAZHI AI — your intelligent customer support
assistant powered by three collaborative AI agents.
</div>
""", unsafe_allow_html=True)


# =====================================================
# 4. CREWAI TOOL
# =====================================================

@tool("Save Customer Support Interaction")
def save_support_interaction(
    customer_query: str,
    assistant_answer: str,
    web_search_answer: str
) -> str:
    """
    Save the customer query, internal assistant answer,
    and web search answer into answers.txt.
    """

    with open("answers.txt", "a", encoding="utf-8") as file:
        file.write("\n" + "=" * 60 + "\n")
        file.write("YAAZHI AI CUSTOMER SUPPORT INTERACTION\n")
        file.write("=" * 60 + "\n")

        file.write("\nCUSTOMER QUERY:\n")
        file.write(customer_query + "\n")

        file.write("\nCUSTOMER SUPPORT ASSISTANT ANSWER:\n")
        file.write(assistant_answer + "\n")

        file.write("\nWEB SEARCH ASSISTANT ANSWER:\n")
        file.write(web_search_answer + "\n")

    return "Customer interaction successfully saved to answers.txt."


# =====================================================
# 5. AI MODEL AND SEARCH TOOL
# =====================================================

llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.2
)

search_tool = SerperDevTool()


# =====================================================
# 6. THREE CREWAI AGENTS
# =====================================================

# AGENT 1: Customer Support Assistant

support_agent = Agent(
    role="Customer Support Assistant",

    goal=(
        "Provide accurate, clear and helpful answers "
        "to customer questions using your own knowledge."
    ),

    backstory=(
        "You are an experienced customer support specialist. "
        "You communicate professionally, understand customer "
        "problems and provide practical solutions."
    ),

    llm=llm,
    verbose=True,
    allow_delegation=False
)


# AGENT 2: Web Search Customer Support Assistant

web_agent = Agent(
    role="Web Search Customer Support Assistant",

    goal=(
        "Research the customer's question using web search "
        "and provide an accurate answer supported by current information."
    ),

    backstory=(
        "You are a research-oriented customer support specialist. "
        "You use online information to validate and improve "
        "customer support responses."
    ),

    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)


# AGENT 3: Customer Support Entry Agent

entry_agent = Agent(
    role="Customer Support Entry Agent",

    goal=(
        "Record customer support interactions, identify customer "
        "sentiment and prepare professional customer email drafts."
    ),

    backstory=(
        "You manage customer support records. You ensure that "
        "customer queries and both AI responses are saved. "
        "You also identify sentiment and prepare customer-friendly "
        "email responses."
    ),

    tools=[save_support_interaction],
    llm=llm,
    verbose=True,
    allow_delegation=False
)


# =====================================================
# 7. CUSTOMER SUPPORT FORM
# =====================================================

support_tab, history_tab, analytics_tab = st.tabs([
    "💬 Customer Support",
    "🎫 Ticket History",
    "📊 Analytics Dashboard"
])


with support_tab:

    st.markdown(
        '<div class="section-title">Customer Information</div>',
        unsafe_allow_html=True
    )

    with st.form("customer_support_form"):

        col1, col2 = st.columns(2)

        with col1:
            customer_name = st.text_input(
                "Customer Name",
                placeholder="Enter customer name"
            )

            customer_email = st.text_input(
                "Customer Email",
                placeholder="Enter email address"
            )

            category = st.selectbox(
                "Issue Category",
                [
                    "Technical Support",
                    "Billing",
                    "Account Access",
                    "Product Information",
                    "Order or Delivery",
                    "Other"
                ]
            )

        with col2:
            priority = st.selectbox(
                "Ticket Priority",
                [
                    "Low",
                    "Medium",
                    "High",
                    "Critical"
                ]
            )

            st.info(
                "The AI agents will analyse the customer "
                "query and prepare a response."
            )

        customer_query = st.text_area(
            "Customer Query",
            placeholder="Describe your issue here...",
            height=150
        )

        submit_button = st.form_submit_button(
            "🚀 Submit Customer Query",
            use_container_width=True
        )


    # =================================================
    # 8. PROCESS CUSTOMER QUERY
    # =================================================

    if submit_button:

        if not customer_name.strip():
            st.error("Please enter the customer name.")

        elif not customer_email.strip() or not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            customer_email.strip()
        ):
            st.error("Please enter a valid email address.")

        elif not customer_query.strip():
            st.error("Please enter the customer query.")

        else:

            try:

                with st.spinner(
                    "YAAZHI AI agents are working on your query..."
                ):

                    # ---------------------------------
                    # TASK 1: INTERNAL SUPPORT ANSWER
                    # ---------------------------------

                    task1 = Task(
                        description=(
                            "Answer the following customer question "
                            "using your own knowledge.\n\n"
                            "Customer query: {customer_query}\n\n"
                            "Category: {category}\n"
                            "Priority: {priority}\n\n"
                            "Give a clear, helpful and professional answer. "
                            "Do not invent company-specific policies."
                        ),

                        expected_output=(
                            "A clear and professional customer support answer."
                        ),

                        agent=support_agent
                    )


                    # ---------------------------------
                    # TASK 2: WEB SEARCH ANSWER
                    # ---------------------------------

                    task2 = Task(
                        description=(
                            "Research the following customer question "
                            "using the web search tool.\n\n"
                            "Customer query: {customer_query}\n\n"
                            "Category: {category}\n\n"
                            "Use relevant and reliable information. "
                            "Explain the findings clearly and include "
                            "source links when available."
                        ),

                        expected_output=(
                            "A researched answer with relevant information "
                            "and source links when available."
                        ),

                        agent=web_agent
                    )


                    # ---------------------------------
                    # TASK 3: ENTRY, SENTIMENT AND EMAIL
                    # ---------------------------------

                    task3 = Task(
                        description=(
                            "You are the Customer Support Entry Agent.\n\n"

                            "Customer name: {customer_name}\n"
                            "Customer email: {customer_email}\n"
                            "Customer category: {category}\n"
                            "Customer priority: {priority}\n"
                            "Customer query: {customer_query}\n\n"

                            "First, review the outputs from the two "
                            "previous agents.\n\n"

                            "You MUST call the "
                            "Save Customer Support Interaction tool "
                            "with the exact customer query and both "
                            "agent answers.\n\n"

                            "Then analyse the customer's sentiment. "
                            "Choose only Positive, Neutral or Negative.\n\n"

                            "Generate a professional and empathetic "
                            "email response to the customer. Address "
                            "the customer by name and respond to their issue.\n\n"

                            "Return your final response in this format:\n\n"

                            "SENTIMENT: Positive / Neutral / Negative\n\n"

                            "EMAIL_DRAFT:\n"
                            "Subject: ...\n"
                            "Dear ...\n"
                            "Email body...\n"
                            "Regards,\nYAAZHI AI Support Team"
                        ),

                        expected_output=(
                            "Confirmation of saved interaction, customer "
                            "sentiment and a professional customer email draft."
                        ),

                        agent=entry_agent,

                        context=[task1, task2]
                    )


                    # ---------------------------------
                    # EXECUTE THREE AGENTS SEQUENTIALLY
                    # ---------------------------------

                    support_crew = Crew(
                        agents=[
                            support_agent,
                            web_agent,
                            entry_agent
                        ],

                        tasks=[
                            task1,
                            task2,
                            task3
                        ],

                        process=Process.sequential,
                        verbose=True
                    )

                    result = support_crew.kickoff(
                        inputs={
                            "customer_name": customer_name,
                            "customer_email": customer_email,
                            "category": category,
                            "priority": priority,
                            "customer_query": customer_query
                        }
                    )


                    # ---------------------------------
                    # GET INDIVIDUAL AGENT ANSWERS
                    # ---------------------------------

                    agent1_answer = task1.output.raw
                    agent2_answer = task2.output.raw
                    agent3_answer = task3.output.raw


                    # ---------------------------------
                    # EXTRACT SENTIMENT
                    # ---------------------------------

                    sentiment_match = re.search(
                        r"SENTIMENT:\s*(Positive|Neutral|Negative)",
                        agent3_answer,
                        re.IGNORECASE
                    )

                    sentiment = (
                        sentiment_match.group(1).capitalize()
                        if sentiment_match
                        else "Neutral"
                    )


                    # ---------------------------------
                    # EXTRACT EMAIL DRAFT
                    # ---------------------------------

                    email_match = re.search(
                        r"EMAIL_DRAFT:\s*(.*)",
                        agent3_answer,
                        re.IGNORECASE | re.DOTALL
                    )

                    email_draft = (
                        email_match.group(1).strip()
                        if email_match
                        else agent3_answer
                    )


                    # ---------------------------------
                    # SAVE TICKET IN SQLITE DATABASE
                    # ---------------------------------

                    ticket_id = save_ticket(
                        customer_name=customer_name,
                        customer_email=customer_email,
                        category=category,
                        priority=priority,
                        sentiment=sentiment,
                        customer_query=customer_query,
                        assistant_answer=agent1_answer,
                        web_search_answer=agent2_answer,
                        email_draft=email_draft
                    )


                    # ---------------------------------
                    # STORE RESULTS IN SESSION
                    # ---------------------------------

                    st.session_state["latest_ticket"] = {
                        "ticket_id": ticket_id,
                        "customer_name": customer_name,
                        "customer_email": customer_email,
                        "category": category,
                        "priority": priority,
                        "sentiment": sentiment,
                        "customer_query": customer_query,
                        "agent1_answer": agent1_answer,
                        "agent2_answer": agent2_answer,
                        "agent3_answer": agent3_answer,
                        "email_draft": email_draft
                    }

                st.success("Customer support request processed successfully!")

            except Exception as error:
                st.error(f"An error occurred: {error}")


    # =================================================
    # 9. DISPLAY LATEST SUPPORT RESULTS
    # =================================================

    if "latest_ticket" in st.session_state:

        data = st.session_state["latest_ticket"]

        st.divider()

        st.markdown(
            '<div class="section-title">Support Results</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="success-card">
                <h3>🎫 Ticket Created Successfully</h3>
                <h2>{data['ticket_id']}</h2>
                <p>Customer: {data['customer_name']}</p>
                <p>Priority: {data['priority']}</p>
                <p>Category: {data['category']}</p>
                <p>Sentiment: {data['sentiment']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander(
            "🤖 Agent 1 - Customer Support Assistant",
            expanded=True
        ):
            st.write(data["agent1_answer"])

        with st.expander(
            "🌐 Agent 2 - Web Search Customer Support Assistant",
            expanded=True
        ):
            st.write(data["agent2_answer"])

        with st.expander(
            "📋 Agent 3 - Customer Support Entry Agent",
            expanded=True
        ):
            st.write(data["agent3_answer"])

        st.markdown("### 📧 AI-Generated Customer Email")

        st.text_area(
            "Email Draft",
            value=data["email_draft"],
            height=220,
            key="latest_email_display"
        )

        st.caption(
            "Review the AI-generated email before sending it to the customer."
        )


# =====================================================
# 10. TICKET HISTORY
# =====================================================

with history_tab:

    st.markdown(
        '<div class="section-title">🎫 Customer Ticket History</div>',
        unsafe_allow_html=True
    )

    tickets = get_all_tickets()

    if tickets:

        ticket_data = [
            dict(ticket) for ticket in tickets
        ]

        df = pd.DataFrame(ticket_data)

        st.metric(
            "Total Support Tickets",
            len(df)
        )

        display_columns = [
            "ticket_id",
            "created_at",
            "customer_name",
            "category",
            "priority",
            "sentiment"
        ]

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        selected_ticket = st.selectbox(
            "Select a ticket to view details",
            df["ticket_id"].tolist()
        )

        selected_data = df[
            df["ticket_id"] == selected_ticket
        ].iloc[0]

        st.markdown("### Ticket Details")

        st.write("**Customer:**", selected_data["customer_name"])
        st.write("**Email:**", selected_data["customer_email"])
        st.write("**Category:**", selected_data["category"])
        st.write("**Priority:**", selected_data["priority"])
        st.write("**Sentiment:**", selected_data["sentiment"])

        st.markdown("### Customer Query")
        st.write(selected_data["customer_query"])

        st.markdown("### Customer Support Assistant")
        st.write(selected_data["assistant_answer"])

        st.markdown("### Web Search Assistant")
        st.write(selected_data["web_search_answer"])

        st.markdown("### Generated Email")
        st.text_area(
            "Saved Email Draft",
            value=selected_data["email_draft"] or "",
            height=180,
            disabled=True,
            key="history_email_display"
        )

    else:
        st.info("No support tickets available yet.")


# =====================================================
# 11. ANALYTICS DASHBOARD
# =====================================================

with analytics_tab:

    st.markdown(
        '<div class="section-title">📊 YAAZHI AI Analytics</div>',
        unsafe_allow_html=True
    )

    tickets = get_all_tickets()

    if tickets:

        df = pd.DataFrame([
            dict(ticket) for ticket in tickets
        ])

        total_tickets = len(df)

        critical_tickets = len(
            df[df["priority"] == "Critical"]
        )

        high_priority_tickets = len(
            df[df["priority"] == "High"]
        )

        negative_sentiment = len(
            df[df["sentiment"] == "Negative"]
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Tickets",
            total_tickets
        )

        col2.metric(
            "Critical Tickets",
            critical_tickets
        )

        col3.metric(
            "High Priority",
            high_priority_tickets
        )

        col4.metric(
            "Negative Sentiment",
            negative_sentiment
        )

        st.divider()

        chart1, chart2 = st.columns(2)

        with chart1:

            st.markdown("### Tickets by Category")

            category_counts = (
                df["category"]
                .value_counts()
            )

            st.bar_chart(category_counts)

        with chart2:

            st.markdown("### Tickets by Priority")

            priority_counts = (
                df["priority"]
                .value_counts()
            )

            st.bar_chart(priority_counts)

        st.markdown("### Customer Sentiment")

        sentiment_counts = (
            df["sentiment"]
            .value_counts()
        )

        st.bar_chart(sentiment_counts)

    else:
        st.info(
            "Analytics will appear after your first customer support ticket."
        )


# =====================================================
# 12. FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#64748b; padding:15px;">
        🎵 <b>YAAZHI AI</b><br>
        Where Every Conversation Finds Its Harmony.
    </div>
    """,
    unsafe_allow_html=True
)
