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
    page_title="Smart Question Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stAlert {
        margin-top: 1rem;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for history
if 'question_history' not in st.session_state:
    st.session_state.question_history = []

# Streamlit UI
st.title("🎓 Smart Question Solver")
st.write("Input your question as text, image, or both!")

# Sidebar with instructions
with st.sidebar:
    st.header("How to Use")
    st.markdown("""
    ### Input Options:
    1. **Text Question**
       - Type your question directly
       - Best for theoretical questions
    
    2. **Image Upload**
       - Upload clear images of problems
       - Supports JPG, JPEG, PNG
    
    3. **Combined Input**
       - Use both text and image
       - Great for detailed explanations
    
    ### Tips for Best Results:
    - 📸 Ensure images are clear and well-lit
    - 📝 Be specific in text descriptions
    - 🔍 Choose appropriate help type
    """)
    
    # View History Toggle
    if st.toggle("View Question History"):
        st.markdown("### Recent Questions")
        for idx, item in enumerate(reversed(st.session_state.question_history[-5:])):
            with st.expander(f"Question {len(st.session_state.question_history)-idx}"):
                if item['text']:
                    st.write("Text:", item['text'])
                if item['image'] is not None:
                    st.image(item['image'], width=200)
                st.write("Response:", item['response'][:200] + "...")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    # Text input
    text_question = st.text_area(
        "Type your question here (optional)", 
        height=100,
        placeholder="Enter your question text here..."
    )
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload question image (optional)", 
        type=['jpg', 'jpeg', 'png']
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Question", use_column_width=True)
    
    help_type = st.selectbox(
        "What kind of help do you need?",
        ["Simplify and explain the question",
         "Provide step-by-step solution",
         "Give hints without full solution",
         "Explain core concepts involved",
         "Practice problems and examples"]
    )

with col2:
    if text_question or uploaded_file:
        try:
            models = initialize_gemini()
            
            # Prepare input data
            input_data = []
            if uploaded_file:
                image = image_to_bytes(uploaded_file)
                input_data.append(image)
            if text_question:
                input_data.append(text_question)
            
            if len(input_data) == 1:
                input_data = input_data[0]
            
            prompts = {
                "Simplify and explain the question": """
                Analyze this question and:
                1. Simplify it into easier language
                2. Identify the key points to focus on
                3. Explain what the question is really asking
                4. Highlight any important terms or concepts
                """,
                
                "Provide step-by-step solution": """
                Solve this question by:
                1. Breaking it down into simple steps
                2. Explaining each step clearly
                3. Showing all work and calculations
                4. Providing the final answer with explanation
                5. Adding tips for similar problems
                """,
                
                "Give hints without full solution": """
                Provide helpful hints by:
                1. Identifying the key concepts needed
                2. Suggesting an approach without giving the answer
                3. Pointing out important things to consider
                4. Offering guiding questions
                """,
                
                "Explain core concepts involved": """
                Explain the core concepts by:
                1. Identifying the main topics involved
                2. Explaining each concept in simple terms
                3. Providing real-world examples
                4. Connecting these concepts to the question
                5. Suggesting related topics to explore
                """,
                
                "Practice problems and examples": """
                Help with practice by:
                1. Creating 2-3 similar practice problems
                2. Providing partially worked examples
                3. Including problems of varying difficulty
                4. Explaining how to approach each type
                """
            }

            if st.button("Get Help", type="primary"):
                with st.spinner("Analyzing your question..."):
                    response = get_gemini_response(models, input_data, prompts[help_type])
                    
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
                        st.markdown("### Response:")
                        st.markdown(response)
                        
                        # Additional help options
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Need more examples?"):
                                followup = get_gemini_response(
                                    models,
                                    input_data,
                                    "Please provide additional similar examples and detailed explanations."
                                )
                                if followup:
                                    st.markdown("### Additional Examples:")
                                    st.markdown(followup)
                        
                        with col_b:
                            if st.button("Simplify further?"):
                                simplify = get_gemini_response(
                                    models,
                                    input_data,
                                    "Please explain this in even simpler terms, as if explaining to a beginner."
                                )
                                if simplify:
                                    st.markdown("### Simplified Explanation:")
                                    st.markdown(simplify)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please make sure your input is clear and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📚 Get help with any academic question - text or image based!</p>
    <p>💡 For best results, provide clear images and detailed text descriptions</p>
</div>
""", unsafe_allow_html=True)
