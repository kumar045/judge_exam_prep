import streamlit as st
import google.generativeai as genai
import PIL.Image
from io import BytesIO
from datetime import datetime

# Initialize Gemini models using secrets
def initialize_gemini():
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    return {
        'vision': genai.GenerativeModel('gemini-1.5-pro-002'),
        'text': genai.GenerativeModel('gemini-1.5-pro-002')
    }

def get_gemini_response(models, input_data, prompt):
    try:
        if isinstance(input_data, (list, tuple)):
            return models['vision'].generate_content([prompt] + list(input_data)).text
        elif isinstance(input_data, PIL.Image.Image):
            return models['vision'].generate_content([prompt, input_data]).text
        else:
            return models['text'].generate_content(f"{prompt}\n\nQuestion: {input_data}").text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def image_to_bytes(upload):
    if upload is not None:
        bytes_data = upload.getvalue()
        img = PIL.Image.open(BytesIO(bytes_data))
        return img
    return None

# Configure page settings
st.set_page_config(
    page_title="Judiciary Exam Preparation Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stAlert {margin-top: 1rem;}
    .main {padding: 2rem;}
    .stButton>button {width: 100%;}
    .legal-category {
        padding: 10px;
        background-color: #f0f2f6;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'question_history' not in st.session_state:
    st.session_state.question_history = []

# Streamlit UI
st.title("⚖️ Judiciary Exam Preparation Assistant")
st.write("Specialized help for Indian Judiciary Examination preparation")

# Sidebar with exam-specific information
with st.sidebar:
    st.header("Exam Preparation Guide")
    st.markdown("""
    ### Key Areas:
    1. **Constitutional Law**
       - Fundamental Rights
       - Directive Principles
       - Union & States
    
    2. **Criminal Law**
       - IPC
       - CrPC
       - Evidence Act
    
    3. **Civil Law**
       - CPC
       - Contract Act
       - Property Law
    
    4. **Important Acts**
       - Special & Local Laws
       - Latest Amendments
       - Landmark Cases
    
    ### Tips:
    - 📚 Focus on recent judgments
    - ⚖️ Practice case analysis
    - 📝 Attempt mock tests regularly
    """)
    
    # View History
    if st.toggle("View Previous Questions"):
        st.markdown("### Recent Questions")
        for idx, item in enumerate(reversed(st.session_state.question_history[-5:])):
            with st.expander(f"Question {len(st.session_state.question_history)-idx}"):
                if item['text']:
                    st.write("Question:", item['text'])
                if item['image'] is not None:
                    st.image(item['image'], width=200)
                st.write("Analysis:", item['response'][:200] + "...")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    # Subject selection with General option
    subject_category = st.selectbox(
        "Select Subject Category",
        ["General Query", "Constitutional Law", "Criminal Law", "Civil Law", "Special Laws", 
         "Jurisprudence", "Legal Maxims", "Landmark Cases"]
    )
    
    # Question type selection based on subject
    question_types = {
        "General Query": ["General Legal Question", "Current Legal Affairs", "Legal News Analysis",
                         "Career Guidance", "Study Strategy", "Any Other Query"],
        "Constitutional Law": ["Fundamental Rights", "State Policy", "Union-State Relations", 
                             "Constitutional Amendments", "Emergency Provisions"],
        "Criminal Law": ["IPC Sections", "Criminal Procedure", "Evidence Law", 
                        "Bail Provisions", "Criminal Trials"],
        "Civil Law": ["CPC Procedures", "Contract Law", "Property Law", 
                     "Family Law", "Civil Remedies"],
        "Special Laws": ["Consumer Protection", "Environmental Law", "Cyber Laws", 
                        "Banking Laws", "Intellectual Property"],
        "Jurisprudence": ["Legal Concepts", "Schools of Jurisprudence", 
                         "Legal Terminology", "Legal Principles"],
        "Legal Maxims": ["Latin Maxims", "English Law Maxims", "Indian Legal Principles"],
        "Landmark Cases": ["Supreme Court Cases", "High Court Cases", "Constitutional Bench",
                          "Recent Judgments"]
    }
    
    sub_category = st.selectbox(
        "Select Specific Topic",
        question_types[subject_category]
    )
    
    # Text input
    text_question = st.text_area(
        "Enter your legal question or case scenario",
        height=100,
        placeholder="Type your question or paste case excerpt here..."
    )
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload question image or case document",
        type=['jpg', 'jpeg', 'png']
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
    
    # Analysis type with General option
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["General Analysis",
         "Case Law Analysis",
         "Legal Principle Explanation",
         "Previous Year Question Analysis",
         "Mock Test Answer Evaluation",
         "Conceptual Clarity",
         "Comparative Analysis"]
    )

with col2:
    if text_question or uploaded_file:
        try:
            models = initialize_gemini()
            
            input_data = []
            if uploaded_file:
                image = image_to_bytes(uploaded_file)
                input_data.append(image)
            if text_question:
                input_data.append(text_question)
            
            if len(input_data) == 1:
                input_data = input_data[0]
            
            # Specialized legal prompts with general option
            prompts = {
                "General Analysis": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Provide a comprehensive analysis of this query:
                1. Understand the main question/issue
                2. Provide relevant legal information
                3. Cite applicable laws and cases if relevant
                4. Give practical insights
                5. Suggest further reading if needed
                
                Context: {subject_category} - {sub_category}
                """,
                
                "Case Law Analysis": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Analyze this legal question/case for Indian Judiciary Exam preparation:
                1. Identify key legal principles and precedents
                2. Break down relevant statutory provisions
                3. Cite important Supreme Court judgments
                4. Explain ratio decidendi
                5. Discuss practical application
                
                Focus on {subject_category} - {sub_category}
                """,
                
                "Legal Principle Explanation": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Explain the legal principles for Indian Judiciary Exam:
                1. Define core legal concepts
                2. Provide relevant sections and articles
                3. List important case laws
                4. Give exam-oriented points
                5. Add comparative analysis if applicable
                
                Specific to {subject_category} - {sub_category}
                """,
                
                "Previous Year Question Analysis": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Analyze this previous year question:
                1. Break down question structure
                2. Identify key legal points to cover
                3. Provide framework for answer
                4. Mention relevant cases and sections
                5. Give exam strategy tips
                
                For {subject_category} - {sub_category}
                """,
                
                "Mock Test Answer Evaluation": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Evaluate this mock test answer:
                1. Assess legal reasoning
                2. Check citation of cases
                3. Evaluate structure and presentation
                4. Suggest improvements
                5. Provide model answer framework
                
                Related to {subject_category} - {sub_category}
                """,
                
                "Conceptual Clarity": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Explain this legal concept:
                1. Define terms and principles
                2. Provide statutory framework
                3. List relevant case laws
                4. Give practical examples
                5. Add exam-specific tips
                
                In context of {subject_category} - {sub_category}
                """,
                
                "Comparative Analysis": f"""
                You are an experienced assistant, trained in legal communication and Judiciary Exam Preparation. Your strengths lie in using simple, clear and direct language, free from
ambiguity and jargon. Your content is accessible and easy to understand, especially
for people with limited legal literacy.

Write instructions on legal and Judiciary topics in a way that is easy to
understand for people with limited legal literacy and a reading level of a 12-year-old

                Provide comparative analysis:
                1. Compare different legal provisions
                2. Contrast judicial interpretations
                3. Analyze conflicting judgments
                4. Discuss evolving jurisprudence
                5. Highlight exam-relevant points
                
                For {subject_category} - {sub_category}
                """
            }

            if st.button("Analyze", type="primary"):
                with st.spinner("Analyzing legal question..."):
                    response = get_gemini_response(models, input_data, prompts[analysis_type])
                    
                    if response:
                        st.success("Analysis complete!")
                        
                        # Save to history
                        st.session_state.question_history.append({
                            'text': text_question,
                            'image': uploaded_file,
                            'response': response,
                            'timestamp': datetime.now()
                        })
                        
                        # Display response
                        st.markdown("### Legal Analysis:")
                        st.markdown(response)
                        
                        # Additional options
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Related Cases"):
                                followup = get_gemini_response(
                                    models,
                                    input_data,
                                    f"Please provide related landmark cases and recent judgments relevant to this topic in {subject_category} - {sub_category}"
                                )
                                if followup:
                                    st.markdown("### Related Cases:")
                                    st.markdown(followup)
                        
                        with col_b:
                            if st.button("Exam Tips"):
                                tips = get_gemini_response(
                                    models,
                                    input_data,
                                    f"Provide specific exam strategy and answer writing tips for this type of question in {subject_category} - {sub_category}"
                                )
                                if tips:
                                    st.markdown("### Exam Strategy Tips:")
                                    st.markdown(tips)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please ensure your input is clear and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>⚖️ Specialized assistance for Indian Judiciary Examination preparation</p>
    <p>📚 Focus on exam-relevant analysis and practical application</p>
    <p>♥ Love from Shivam</p>
</div>
""", unsafe_allow_html=True)
