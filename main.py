import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.agent_factory import create_agent
from src.database.interface import get_database

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SportzVillage AI Assistant",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-badge {
        background-color: #ff6b35;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_agent' not in st.session_state:
        st.session_state.user_agent = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def login_page():
    """Display login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🏆 SportzVillage AI Assistant</h1>
        <p>Intelligent Sports Program Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Please Login")
    
    with st.form("login_form"):
        user_id = st.text_input("User ID", placeholder="Enter your user ID")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if user_id and password:
                # Authenticate user
                db = get_database()
                user = db.authenticate_user(user_id, password)
                
                if user:
                    try:
                        st.session_state.user_agent = create_agent(user_id)
                        st.session_state.authenticated = True
                        st.success(f"Welcome, {user['name']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error initializing agent: {str(e)}")
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("Please enter both User ID and password.")
    
    # Demo credentials
    with st.expander("Demo Credentials"):
        st.markdown("""
        **Try these demo accounts:**
        - **Resident**: ID: `R001`, Password: `r123`
        - **Delivery Manager**: ID: `DM001`, Password: `dm123`
        - **Regional Manager**: ID: `RM001`, Password: `rm123`
        - **Head Office**: ID: `HO001`, Password: `ho123`
        - **Principal**: ID: `P001`, Password: `p123`
        """)


def main_app():
    """Main application interface"""
    agent = st.session_state.user_agent
    user_context = agent.get_user_context()
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="main-header">
            <h2>Welcome, {user_context['name']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <span class="role-badge">{user_context['role']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_agent = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Role-specific interface
    role = user_context['role']
    
    if role == "R":
        resident_interface()
    elif role in ["DM", "RM"]:
        manager_interface()
    elif role == "HO":
        head_office_interface()
    elif role == "PRINCIPAL":
        principal_interface()


def resident_interface():
    """Interface for Residents"""
    st.markdown('<div class="section-header"><h3>🏃‍♂️ Resident Dashboard</h3></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Activities", "❓ Ask Questions", "📊 Quick Reports", "💬 Chat"])
    
    with tab1:
        st.subheader("Log Your Activities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Lesson Completion")
            with st.form("lesson_form"):
                class_name = st.selectbox("Class", ["Nursery", "LKG", "UKG", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"])
                section = st.selectbox("Section", ["A", "B", "C", "D", "E"])
                period = st.number_input("Period Number", min_value=1, max_value=10, value=1)
                lesson_id = st.text_input("Lesson ID", placeholder="e.g., L001")
                notes = st.text_area("Notes (optional)")
                
                if st.form_submit_button("Log Lesson Completion"):
                    if class_name and section and lesson_id:
                        query = f"Log lesson completion: Class {class_name}-{section}, Period {period}, Lesson {lesson_id}. Notes: {notes}"
                        response = st.session_state.user_agent.chat(query)
                        st.success(response)
                    else:
                        st.error("Please fill in all required fields")
        
        with col2:
            st.markdown("#### Prop Update")
            with st.form("prop_form"):
                prop_id = st.text_input("Prop ID", placeholder="e.g., PROP001")
                prop_status = st.selectbox("Status", ["good", "damaged", "missing", "needs_repair"])
                prop_notes = st.text_area("Notes about prop condition")
                
                if st.form_submit_button("Update Prop Status"):
                    if prop_id and prop_status:
                        query = f"Update prop {prop_id} status to {prop_status}. Notes: {prop_notes}"
                        response = st.session_state.user_agent.chat(query)
                        st.success(response)
                    else:
                        st.error("Please fill in required fields")
    
    with tab2:
        st.subheader("Ask Questions")
        
        # Enhanced AI search section
        st.markdown("**🧠 Smart Search (AI-Powered):**")
        search_query = st.text_input(
            "Ask anything about your school's sports program:", 
            placeholder="e.g., What football equipment do we have? When are my PE classes?"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Smart Search", type="primary", key="resident_smart_search"):
                if search_query:
                    response = st.session_state.user_agent.chat(f"Use semantic search to find: {search_query}")
                    st.write("**AI Response:**", response)
        
        with col2:
            if st.button("📊 Enhanced Report", key="resident_enhanced_report"):
                response = st.session_state.user_agent.chat("Generate smart weekly report for my school")
                st.text_area("Smart Report", response, height=300)
        
        st.divider()
        
        quick_questions = [
            "Show me today's timetable for my school",
            "What lesson plans are available for my school?",
            "What props are available in my school?",
            "Show me the PE periods for Class V this week"
        ]
        
        st.markdown("**Quick Questions:**")
        for question in quick_questions:
            if st.button(question, key=f"q_{question}"):
                response = st.session_state.user_agent.chat(question)
                st.write("**Answer:**", response)
    
    with tab3:
        st.subheader("Smart Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📈 AI Weekly Report", key="resident_ai_weekly"):
                response = st.session_state.user_agent.chat("Generate smart weekly report with AI insights for my school")
                st.text_area("AI-Enhanced Weekly Report", response, height=300)
        
        with col2:
            if st.button("🤖 Intelligent Props Report", key="resident_ai_props"):
                response = st.session_state.user_agent.chat("Generate intelligent props analysis for my school")
                st.text_area("Smart Props Analysis", response, height=300)
        
        # Vector cache status
        st.divider()
        st.markdown("**🔧 System Status:**")
        if st.button("Check AI System Status", key="resident_system_status"):
            response = st.session_state.user_agent.chat("Check vector cache status and refresh if needed")
            st.info(response)
    
    with tab4:
        chat_interface("resident")


def manager_interface():
    """Interface for Delivery Managers and Regional Managers"""
    user_context = st.session_state.user_agent.get_user_context()
    role_title = "Delivery Manager" if user_context['role'] == "DM" else "Regional Manager"
    
    st.markdown(f'<div class="section-header"><h3>👨‍💼 {role_title} Dashboard</h3></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Smart Reports", "🤖 AI Analytics", "👥 Team Management", "🔍 Monitor Schools", "💬 Chat"])
    
    with tab1:
        st.subheader("AI-Enhanced Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox("Report Type", [
                "smart_weekly", "smart_monthly", "intelligent_props", "weekly_lessons", "monthly_lessons", "resident_activity"
            ])
            
            if report_type.startswith("smart_") or report_type == "intelligent_props":
                school_id = st.text_input("School ID", placeholder="e.g., SCH001")
                context = st.text_input("Additional Context (optional)", placeholder="e.g., focus on football activities")
                
                if st.button("🧠 Generate Smart Report", key="manager_smart_report"):
                    query = f"Generate {report_type} report for school {school_id}"
                    if context:
                        query += f" with context: {context}"
                    response = st.session_state.user_agent.chat(query)
                    st.text_area("AI-Enhanced Report", response, height=400)
            
            else:  # Traditional reports
                school_id = st.text_input("School ID", placeholder="e.g., SCH001")
                date_range = st.text_input("Date Range", placeholder="e.g., 2024-10-01 to 2024-10-07")
                
                if st.button("Generate Report", key="manager_traditional_report"):
                    query = f"Generate {report_type} report for school {school_id} for period {date_range}"
                    response = st.session_state.user_agent.chat(query)
                    st.text_area("Report", response, height=300)
    
    with tab2:
        st.subheader("🤖 AI Analytics & LLM Insights")
        
        # Create sub-tabs for different analytics views
        analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["📊 System Analytics", "🧠 LLM Metrics", "🔍 Smart Search"])
        
        with analytics_tab1:
            st.markdown("#### System-wide Analytics")
            try:
                analytics = st.session_state.user_agent.get_session_analytics()
                
                # Display key metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Interactions", analytics.get('total_interactions', 0))
                
                with col2:
                    avg_response_time = analytics.get('average_response_time', 0)
                    st.metric("Avg Response Time", f"{avg_response_time:.2f}s")
                
                with col3:
                    st.metric("Active Users", analytics.get('unique_users', 0))
                
                with col4:
                    st.metric("Total Sessions", analytics.get('total_sessions', 0))
                
                # Show user role distribution
                if 'user_roles' in analytics:
                    st.markdown("#### User Activity by Role")
                    role_data = analytics['user_roles']
                    for role, count in role_data.items():
                        st.write(f"**{role}**: {count} interactions")
                
            except Exception as e:
                st.error(f"Failed to load system analytics: {e}")
        
        with analytics_tab2:
            st.markdown("#### LLM Performance Metrics")
            try:
                analytics = st.session_state.user_agent.get_session_analytics()
                
                if 'llm_analytics' in analytics:
                    llm_data = analytics['llm_analytics']
                    
                    # Token usage overview
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_prompt_tokens = llm_data.get('total_prompt_tokens', 0)
                        st.metric("Total Prompt Tokens", f"{total_prompt_tokens:,}")
                    
                    with col2:
                        total_completion_tokens = llm_data.get('total_completion_tokens', 0)
                        st.metric("Total Completion Tokens", f"{total_completion_tokens:,}")
                    
                    with col3:
                        total_tokens = llm_data.get('total_tokens', 0)
                        st.metric("Total Tokens", f"{total_tokens:,}")
                    
                    # Cost estimation
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        estimated_cost_gpt4 = llm_data.get('estimated_cost_gpt4', 0)
                        st.metric("Est. Cost (GPT-4)", f"${estimated_cost_gpt4:.4f}")
                    
                    with col2:
                        estimated_cost_gpt35 = llm_data.get('estimated_cost_gpt35', 0)
                        st.metric("Est. Cost (GPT-3.5)", f"${estimated_cost_gpt35:.4f}")
                    
                    # Token efficiency metrics
                    if llm_data.get('total_interactions', 0) > 0:
                        avg_tokens = llm_data.get('tokens_per_interaction', 0)
                        st.metric("Avg Tokens/Interaction", f"{avg_tokens:.1f}")
                    
                    # Model usage breakdown
                    if 'models_used' in llm_data:
                        st.markdown("#### Model Usage")
                        for model, count in llm_data['models_used'].items():
                            st.write(f"**{model}**: {count} calls")
                    
                    # Show recent LLM interactions with prompts
                    st.markdown("#### Recent LLM Interactions")
                    history = st.session_state.user_agent.get_chat_history(limit=5)
                    
                    for interaction in history:
                        # Check for llm_analytics at top level (new format)
                        llm_info = interaction.get('llm_analytics', {})
                        # Fallback to old format if needed
                        if not llm_info or llm_info.get('total_tokens', 0) == 0:
                            llm_info = interaction.get('interaction', {}).get('llm_analytics', {})
                        
                        if llm_info and llm_info.get('total_tokens', 0) > 0:
                            timestamp = interaction['timestamp'][:19]
                            
                            with st.expander(f"🧠 {timestamp} - {llm_info.get('model_used', 'unknown')} - {llm_info.get('total_tokens', 0)} tokens"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**Prompt:**")
                                    prompt_text = llm_info.get('llm_prompt', 'No prompt captured')
                                    
                                    # Enhanced display logic to prioritize user messages
                                    if len(prompt_text) > 1000:
                                        # Split by message blocks
                                        sections = prompt_text.split('[USER]:')
                                        
                                        if len(sections) > 1:
                                            # There are user messages - show the last few interactions
                                            display_parts = []
                                            
                                            # Show system message (abbreviated)
                                            system_part = sections[0].replace('[SYSTEM]:', '').strip()
                                            if len(system_part) > 200:
                                                display_parts.append(f"[SYSTEM]: {system_part[:200]}...\n")
                                            else:
                                                display_parts.append(f"[SYSTEM]: {system_part}\n")
                                            
                                            # Show all user messages
                                            for user_section in sections[1:]:
                                                display_parts.append(f"[USER]: {user_section}")
                                            
                                            display_text = "\n".join(display_parts)
                                        else:
                                            # No user messages, show truncated
                                            display_text = prompt_text[:1000] + "..."
                                    else:
                                        display_text = prompt_text
                                    
                                    # Show the prompt in a text area
                                    st.text_area("Prompt Content", display_text, height=250, key=f"prompt_{timestamp}", label_visibility="collapsed")
                                    
                                    # Also show a summary
                                    lines = prompt_text.split('\n')
                                    user_lines = [line for line in lines if '[USER]:' in line]
                                    if user_lines:
                                        st.markdown("**User Messages:**")
                                        for i, user_line in enumerate(user_lines[-3:]):  # Last 3 user messages
                                            user_content = user_line.replace('[USER]:', '').strip()
                                            st.markdown(f"• {user_content}")
                                    else:
                                        st.info("No user messages captured")
                                
                                with col2:
                                    st.markdown("**Token Breakdown:**")
                                    st.write(f"Prompt Tokens: {llm_info.get('prompt_tokens', 0)}")
                                    st.write(f"Completion Tokens: {llm_info.get('completion_tokens', 0)}")
                                    st.write(f"Temperature: {llm_info.get('temperature', 0)}")
                                    st.write(f"Model: {llm_info.get('model_used', 'unknown')}")
                        else:
                            # Show that no LLM data was captured for this interaction
                            timestamp = interaction['timestamp'][:19]
                            with st.expander(f"❌ {timestamp} - No LLM data captured"):
                                st.write("This interaction did not capture LLM analytics data.")
                else:
                    st.info("No LLM analytics data available yet. Start a conversation to see metrics.")
                    
            except Exception as e:
                st.error(f"Failed to load LLM analytics: {e}")
        
        with analytics_tab3:
            st.markdown("#### AI-Powered Smart Search")
            search_query = st.text_input(
                "Ask AI about your operations:", 
                placeholder="e.g., Which schools need more props? What are the performance trends?"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔍 Smart Search", key="manager_smart_search"):
                    if search_query:
                        response = st.session_state.user_agent.chat(f"Use semantic search and analysis: {search_query}")
                        st.write("**AI Analysis:**", response)
            
            with col2:
                if st.button("📊 Performance Insights", key="manager_performance_insights"):
                    manager_id = user_context['user_id']
                    response = st.session_state.user_agent.chat(f"Generate intelligent performance analysis for manager {manager_id}")
                    st.text_area("Performance Insights", response, height=200)
            
            with col3:
                if st.button("🔄 Refresh AI Cache", key="manager_refresh_cache"):
                    response = st.session_state.user_agent.chat("Refresh vector cache with latest data")
                    st.success(response)
    
    with tab3:
        st.subheader("Team Management")
        
        if st.button("Show My Residents", key="manager_show_residents"):
            manager_id = user_context['user_id']
            query = f"Show all residents under manager {manager_id}"
            response = st.session_state.user_agent.chat(query)
            st.write(response)
    
    with tab4:
        st.subheader("Monitor Schools")
        
        school_id = st.text_input("School ID to Monitor", placeholder="e.g., SCH001")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("View Timetable", key="manager_view_timetable"):
                if school_id:
                    query = f"Show timetable for school {school_id}"
                    response = st.session_state.user_agent.chat(query)
                    st.text_area("Timetable", response, height=200)
        
        with col2:
            if st.button("Check Props", key="manager_check_props"):
                if school_id:
                    query = f"Show props status for school {school_id}"
                    response = st.session_state.user_agent.chat(query)
                    st.text_area("Props Status", response, height=200)
        
        with col3:
            if st.button("Lesson Plans", key="manager_lesson_plans"):
                if school_id:
                    query = f"Show lesson plans for school {school_id}"
                    response = st.session_state.user_agent.chat(query)
                    st.text_area("Lesson Plans", response, height=200)
    
    with tab5:
        chat_interface("manager")


def head_office_interface():
    """Interface for Head Office"""
    st.markdown('<div class="section-header"><h3>🏢 Head Office Dashboard</h3></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 System Overview", "📊 Comprehensive Reports", "💬 Chat"])
    
    with tab1:
        st.subheader("System-wide Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Schools", "25", "+2")
            st.metric("Active Residents", "48", "+1")
        
        with col2:
            st.metric("Lessons This Week", "1,250", "+50")
            st.metric("Props Reported Issues", "3", "-2")
        
        with col3:
            st.metric("System Uptime", "99.9%", "+0.1%")
            st.metric("Data Accuracy", "99.8%", "0%")
    
    with tab2:
        st.subheader("Generate Comprehensive Reports")
        
        report_scope = st.selectbox("Report Scope", ["Single School", "Regional", "System-wide"])
        
        if report_scope == "Single School":
            school_id = st.text_input("School ID", placeholder="e.g., SCH001")
            if st.button("Generate School Report", key="ho_school_report"):
                query = f"Generate comprehensive report for school {school_id}"
                response = st.session_state.user_agent.chat(query)
                st.text_area("School Report", response, height=400)
        
        elif report_scope == "System-wide":
            if st.button("Generate System Report", key="ho_system_report"):
                query = "Generate system-wide performance report"
                response = st.session_state.user_agent.chat(query)
                st.text_area("System Report", response, height=400)
    
    with tab3:
        chat_interface("head_office")


def principal_interface():
    """Interface for School Principals"""
    user_context = st.session_state.user_agent.get_user_context()
    school_id = user_context.get('school_id', 'Unknown')
    
    st.markdown('<div class="section-header"><h3>🎓 Principal Dashboard</h3></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 School Reports", "👥 SV Activities", "💬 Chat"])
    
    with tab1:
        st.subheader(f"Reports for School {school_id}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Weekly SV Report", key="principal_weekly_report"):
                query = f"Generate weekly SV activities report for school {school_id}"
                response = st.session_state.user_agent.chat(query)
                st.text_area("Weekly Report", response, height=300)
        
        with col2:
            if st.button("Monthly SV Report", key="principal_monthly_report"):
                query = f"Generate monthly SV activities report for school {school_id}"
                response = st.session_state.user_agent.chat(query)
                st.text_area("Monthly Report", response, height=300)
    
    with tab2:
        st.subheader("SV Activities in Your School")
        
        if st.button("Current Timetable", key="principal_timetable"):
            query = f"Show current PE timetable for school {school_id}"
            response = st.session_state.user_agent.chat(query)
            st.write(response)
        
        if st.button("Props Status", key="principal_props_status"):
            query = f"Show sports equipment status for school {school_id}"
            response = st.session_state.user_agent.chat(query)
            st.write(response)
    
    with tab3:
        chat_interface("principal")


def chat_interface(context_id: str = "general"):
    """General chat interface with logging capabilities"""
    st.subheader("💬 Chat with AI Assistant")
    
    # Add sidebar for chat history and analytics
    with st.sidebar:
        st.markdown("### 📊 Chat Management")
        
        # Chat history toggle
        if st.button("📜 View Full History", key=f"history_btn_{context_id}"):
            st.session_state.show_full_history = not st.session_state.get('show_full_history', False)
        
        # Analytics for managers/HO
        user_context = st.session_state.user_agent.get_user_context()
        if user_context['role'] in ['HO', 'RM', 'DM']:
            if st.button("📊 Chat Analytics", key=f"analytics_btn_{context_id}"):
                try:
                    analytics = st.session_state.user_agent.get_session_analytics()
                    st.json(analytics)
                except Exception as e:
                    st.error(f"Analytics error: {e}")
        
        if st.button("🧹 Clear Session", key=f"clear_btn_{context_id}"):
            st.session_state.chat_history = []
            st.session_state.user_agent.memory.clear()
            st.success("Session cleared!")
    
    # Show full history if requested
    if st.session_state.get('show_full_history', False):
        st.markdown("### 📚 Complete Chat History")
        try:
            history = st.session_state.user_agent.get_chat_history(limit=20)
            
            if history:
                for interaction in history:
                    # Handle different data structures
                    timestamp = interaction.get('timestamp', 'Unknown time')[:19]
                    
                    # Try to get response time safely
                    response_time = 0.0
                    if 'interaction' in interaction:
                        response_time = interaction['interaction'].get('response_time_seconds', 0.0)
                    elif 'response_time' in interaction:
                        response_time = interaction.get('response_time', 0.0)
                    
                    with st.expander(f"💬 {timestamp} - Response: {response_time:.2f}s"):
                        # Get message and response safely
                        message = ""
                        response = ""
                        tools_used = []
                        message_length = 0
                        
                        if 'interaction' in interaction:
                            message = interaction['interaction'].get('message', '')
                            response = interaction['interaction'].get('response', '')
                            tools_used = interaction['interaction'].get('tools_used', [])
                            message_length = interaction['interaction'].get('message_length', len(message))
                        else:
                            message = interaction.get('message', '')
                            response = interaction.get('response', '')
                            tools_used = interaction.get('tools_used', [])
                            message_length = len(message)
                        
                        # Get user role safely
                        user_role = "Unknown"
                        if 'user' in interaction:
                            user_role = interaction['user'].get('role', 'Unknown')
                        elif 'user_role' in interaction:
                            user_role = interaction.get('user_role', 'Unknown')
                        
                        st.markdown(f"**User ({user_role}):** {message}")
                        st.markdown(f"**Assistant:** {response[:200]}...")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tools Used", len(tools_used))
                        with col2:
                            st.metric("Message Length", message_length)
                        with col3:
                            session_id = interaction.get('session_id', 'unknown')
                            st.metric("Session", session_id[:8] if len(session_id) > 8 else session_id)
            else:
                st.info("No chat history found yet.")
                
        except Exception as e:
            st.error(f"Failed to load history: {e}")
            st.error(f"Error details: {str(e)}")
        
        st.divider()
    
    # Display current session chat history
    for message in st.session_state.chat_history:
        if message.get("content", "").strip():  # Only display non-empty messages
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input - using a dynamic key to avoid session state modification issues
    input_key = f"input_counter_{context_id}"
    if input_key not in st.session_state:
        st.session_state[input_key] = 0
    
    prompt = st.text_input(
        "Ask me anything about your SportzVillage activities...", 
        key=f"chat_input_{context_id}_{st.session_state[input_key]}",
        placeholder="Type your question here..."
    )
    
    if st.button("Send", key=f"send_btn_{context_id}") and prompt:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.user_agent.chat(prompt)
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Increment counter to create a new input widget on next run
        st.session_state[input_key] += 1
        
        # Refresh the page to show new input
        st.rerun()


def main():
    """Main application entry point"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()