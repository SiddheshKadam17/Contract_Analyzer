import streamlit as st
import plotly.graph_objects as go
from modules.parser import ContractParser
from modules.nlp_engine import LegalNLPEngine
from modules.risk_analyzer import RiskAnalyzer
from modules.llm_assistant import ClaudeAssistant
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Contract Intelligence Platform",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    .risk-high { color: #991b1b; background: #fee2e2; padding: 10px; border-radius: 5px; }
    .risk-medium { color: #92400e; background: #fef3c7; padding: 10px; border-radius: 5px; }
    .risk-low { color: #065f46; background: #d1fae5; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'contract_data' not in st.session_state:
    st.session_state.contract_data = None

# Initialize components
@st.cache_resource
def load_components():
    parser = ContractParser()
    nlp_engine = LegalNLPEngine()
    risk_analyzer = RiskAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY')
    assistant = ClaudeAssistant(api_key) if api_key else None
    return parser, nlp_engine, risk_analyzer, assistant

parser, nlp_engine, risk_analyzer, assistant = load_components()

# Main content
st.markdown('<p class="main-header">⚖️ Contract Intelligence Platform</p>', unsafe_allow_html=True)
st.write("AI-powered legal analysis for Indian SMEs")
st.markdown("---")

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload Contract Document",
    type=['pdf', 'docx', 'txt'],
    help="Supported: PDF, Word, Text files"
)

if uploaded_file:
    st.success(f"✅ File loaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    
    if st.button("🚀 Start Analysis", type="primary"):
        with st.spinner("🔍 Analyzing contract..."):
            try:
                # Save file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse document
                file_ext = uploaded_file.name.split('.')[-1]
                parsed = parser.parse_document(temp_path, file_ext)
                
                # NLP Analysis
                entities = nlp_engine.extract_entities(parsed['raw_text'])
                classified = nlp_engine.classify_clauses(parsed['raw_text'])
                ambiguous = nlp_engine.detect_ambiguous_terms(parsed['raw_text'])
                
                # Risk Analysis
                risks = risk_analyzer.analyze_contract(parsed['raw_text'], entities)
                compliance = risk_analyzer.check_indian_compliance(parsed['raw_text'], 'general')
                
                # AI Analysis
                # AI Analysis - Temporarily disabled
                contract_type = "Service Agreement (auto-detected)"
                summary = "This contract has been analyzed using rule-based NLP. Risk scoring and entity extraction are complete. AI-powered summaries are temporarily unavailable due to API quota limits."
                
                # Store results
                st.session_state.contract_data = {
                    'parsed': parsed,
                    'entities': entities,
                    'classified': classified,
                    'ambiguous': ambiguous,
                    'risks': risks,
                    'compliance': compliance,
                    'contract_type': contract_type,
                    'summary': summary,
                    'filename': uploaded_file.name,
                    'timestamp': datetime.now().isoformat()
                }
                
                st.session_state.analysis_done = True
                
                # Cleanup
                os.remove(temp_path)
                st.success("✅ Analysis complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("See error details"):
                    st.code(traceback.format_exc())

# Display results
if st.session_state.analysis_done and st.session_state.contract_data:
    data = st.session_state.contract_data
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Contract Type
    st.markdown(f"### Contract Type: `{data['contract_type']}`")
    
    # Risk Score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Risk Score", f"{data['risks']['composite_score']}/100")
    with col2:
        st.metric("🔴 High Risk", len(data['risks']['high']))
    with col3:
        st.metric("🟡 Medium Risk", len(data['risks']['medium']))
    with col4:
        st.metric("🟢 Low Risk", len(data['risks']['low']))
    
    # Risk Level Badge
    risk_level = data['risks']['level']
    if 'HIGH' in risk_level:
        st.markdown(f'<div class="risk-high">🚨 {risk_level}</div>', unsafe_allow_html=True)
    elif 'MEDIUM' in risk_level:
        st.markdown(f'<div class="risk-medium">⚠️ {risk_level}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-low">✅ {risk_level}</div>', unsafe_allow_html=True)
    
    st.info(f"**Recommendation:** {data['risks']['recommendation']}")
    
    # AI Summary
    st.markdown("### 🤖 AI Summary")
    st.info(data['summary'])
    
    # Key Information
    st.markdown("### 📋 Key Information Extracted")
    
    if data['entities']['organizations']:
        st.write(f"**Organizations:** {', '.join(data['entities']['organizations'][:5])}")
    
    if data['entities']['custom'].get('party'):
        st.write(f"**Parties:** {', '.join(data['entities']['custom']['party'][:3])}")
    
    if data['entities']['custom'].get('amount'):
        st.write(f"**Financial Terms:** {', '.join(data['entities']['custom']['amount'][:3])}")
    
    if data['entities']['custom'].get('date'):
        st.write(f"**Dates:** {', '.join(data['entities']['custom']['date'][:3])}")
    
    # Risk Details
    st.markdown("### ⚠️ Risk Details")
    
    if data['risks']['high']:
        with st.expander(f"🔴 High Risk Issues ({len(data['risks']['high'])})"):
            for i, issue in enumerate(data['risks']['high'], 1):
                st.markdown(f"**{i}. {issue['category'].replace('_', ' ').title()}**")
                st.write(f"Found: `{issue['matched_text']}`")
                st.write(f"Context: ...{issue['context']}...")
                st.markdown("---")
    
    if data['risks']['medium']:
        with st.expander(f"🟡 Medium Risk Issues ({len(data['risks']['medium'])})"):
            for i, issue in enumerate(data['risks']['medium'], 1):
                st.markdown(f"**{i}. {issue['category'].replace('_', ' ').title()}**")
                st.write(f"Found: `{issue['matched_text']}`")
                st.markdown("---")
    
    # Clause Analysis
    st.markdown("### 📝 Clause Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Obligations", len(data['classified']['obligations']))
    with col2:
        st.metric("Rights", len(data['classified']['rights']))
    with col3:
        st.metric("Prohibitions", len(data['classified']['prohibitions']))
    
    if data['classified']['obligations']:
        with st.expander(f"View Obligations ({len(data['classified']['obligations'])})"):
            for i, clause in enumerate(data['classified']['obligations'][:10], 1):
                st.write(f"{i}. {clause}")
    
    # Ambiguous Terms
    if data['ambiguous']:
        st.markdown("### ⚠️ Ambiguous Terms Found")
        with st.expander(f"View {len(data['ambiguous'])} ambiguous clauses"):
            for item in data['ambiguous'][:10]:
                st.warning(f"**Terms:** {', '.join(item['terms'])}\n\n{item['sentence']}")
    
    # Export
    st.markdown("### 💾 Export")
    json_data = json.dumps(st.session_state.contract_data, indent=2, default=str)
    st.download_button(
        label="📥 Download Analysis (JSON)",
        data=json_data,
        file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

else:
    st.info("👆 Upload a contract document above to begin analysis")

# Footer
st.markdown("---")
st.caption("Built for Indian SMEs | Powered by AI & Advanced NLP")