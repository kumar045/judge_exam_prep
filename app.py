import streamlit as st
import google.generativeai as genai
import PIL.Image
from io import BytesIO

# Configure page settings
st.set_page_config(page_title="Smart Question Solver", layout="wide")

# Initialize Gemini models
def initialize_gemini(api_key):
    genai.configure(api_key=api_key)
    return {
        'vision': genai.GenerativeModel('gemini-pro-vision'),
        'text': genai.GenerativeModel('gemini-pro')
    }

def get_gemini_response(models, input_data, prompt):
    if isinstance(input_data, (list, tuple)):
        # For combined image and text
        return models['vision'].generate_content([prompt] + list(input_data)).text
    elif isinstance(input_data, PIL.Image.Image):
        # For image only
        return models['vision'].generate_content([prompt, input_data]).text
    else:
        # For text only
        return models['text'].generate_content(f"{prompt}\n\nQuestion: {input_data}").text

def image_to_bytes(upload):
    if upload is not None:
        bytes_data = upload.getvalue()
        img = PIL.Image.open(BytesIO(bytes_data))
        return img
    return None

# Streamlit UI
st.title("🎓 Smart Question Solver")
st.write("Input your question as text, image, or both!")

# Sidebar for API key and instructions
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Google API Key", type="password")
    
    st.markdown("""
    ### How to use:
    1. Enter your Google API key
    2. Choose input method(s):
       - Type your question
       - Upload image
       - Or both!
    3. Select the type of help needed
    4. Get detailed explanations
    
    ### Tips:
    - For math problems, clear images work best
    - For conceptual questions, try using text
    - Combine both for complex problems
    """)

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
    
    # Input validation
    if not text_question and not uploaded_file:
        st.warning("Please provide either text question or image or both.")
    
    help_type = st.selectbox(
        "What kind of help do you need?",
        ["Simplify and explain the question",
         "Provide step-by-step solution",
         "Give hints without full solution",
         "Explain core concepts involved",
         "Practice problems and examples"]
    )

with col2:
    if (text_question or uploaded_file) and api_key:
        try:
            models = initialize_gemini(api_key)
            
            # Prepare input data
            input_data = []
            if uploaded_file:
                image = image_to_bytes(uploaded_file)
                input_data.append(image)
            if text_question:
                input_data.append(text_question)
            
            # Use single input if only one type provided
            if len(input_data) == 1:
                input_data = input_data[0]
            
            # Different prompts based on help type
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

            if st.button("Get Help"):
                with st.spinner("Analyzing your question..."):
                    response = get_gemini_response(models, input_data, prompts[help_type])
                    
                    st.success("Analysis complete!")
                    st.markdown("### Response:")
                    st.markdown(response)
                    
                    # Additional options
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Need more examples?"):
                            followup = get_gemini_response(
                                models,
                                input_data,
                                "Please provide additional similar examples and detailed explanations."
                            )
                            st.markdown("### Additional Examples:")
                            st.markdown(followup)
                    
                    with col_b:
                        if st.button("Simplify further?"):
                            simplify = get_gemini_response(
                                models,
                                input_data,
                                "Please explain this in even simpler terms, as if explaining to a beginner."
                            )
                            st.markdown("### Simplified Explanation:")
                            st.markdown(simplify)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please make sure you've entered a valid API key and provided clear input.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📚 Get help with any academic question - text or image based!</p>
    <p>💡 For best results, provide clear images and detailed text descriptions</p>
</div>
""", unsafe_allow_html=True)

# Session state management for history
if 'question_history' not in st.session_state:
    st.session_state.question_history = []

# Save question and response to history
def save_to_history(question_text, question_image, response):
    st.session_state.question_history.append({
        'text': question_text,
        'image': question_image,
        'response': response,
        'timestamp': datetime.now()
    })
