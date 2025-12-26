"""SEO Content Generator - Streamlit App"""
import streamlit as st
import os
from datetime import datetime
import hashlib
from config import Config
from seo_analyzer import SEOAnalyzer
from database import init_database, save_session

# Page config
st.set_page_config(
    page_title="SEO Content Generator",
    page_icon="📝",
    layout="wide"
)

# Initialize
init_database()

# Session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(
        str(datetime.now()).encode()
    ).hexdigest()

# Header
st.title("📝 SEO Content Generator")
st.markdown("*AI-Powered SEO Content Creation*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=Config.OPENAI_API_KEY,
        help="Enter your OpenAI API key"
    )
    
    if api_key:
        Config.OPENAI_API_KEY = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.markdown("---")
    
    st.info("""
    **Quick Start:**
    
    1. Enter your API key above
    2. Enter a topic
    3. Set target SEO score
    4. Click Generate!
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input(
        "🎯 Topic",
        placeholder="e.g., Digital Marketing Strategies",
        help="Enter the topic for content generation"
    )

with col2:
    target_score = st.slider(
        "🎯 Target SEO Score",
        min_value=1.0,
        max_value=10.0,
        value=8.0,
        step=0.5
    )

st.markdown("---")

# Generate button
if st.button("🚀 Generate Content", type="primary", use_container_width=True):
    if not topic:
        st.error("❌ Please enter a topic")
    elif not Config.OPENAI_API_KEY:
        st.error("❌ Please enter your OpenAI API key in the sidebar")
    else:
        # Show demo mode message
        st.warning("""
        ⚠️ **Demo Mode - AutoGen Setup Required**
        
        To use the full multi-agent system:
        1. Install AutoGen: `pip install pyautogen`
        2. Configure agents in `agents.py`
        3. The system will automatically use the multi-agent workflow
        
        This demo generates sample content to show the UI.
        """)
        
        with st.spinner("Generating content..."):
            # Demo content generation
            demo_content = f"""# {topic}

## Introduction

{topic} is an essential aspect of modern business strategy. This comprehensive guide explores the key concepts, best practices, and implementation strategies.

## Key Concepts

Understanding {topic} requires knowledge of several fundamental principles:

- **Concept 1**: Core foundation of {topic}
- **Concept 2**: Advanced techniques and methodologies
- **Concept 3**: Practical applications in real-world scenarios

## Best Practices

### Strategy 1: Planning and Preparation

Successful implementation of {topic} begins with thorough planning. Organizations must assess their current capabilities and define clear objectives.

### Strategy 2: Execution and Monitoring

Effective execution requires continuous monitoring and adjustment. Regular performance reviews ensure alignment with business goals.

### Strategy 3: Optimization and Scaling

As systems mature, focus shifts to optimization. Scaling strategies enable growth while maintaining quality standards.

## Implementation Guide

Follow these steps for successful implementation:

1. **Assessment Phase**: Evaluate current state
2. **Planning Phase**: Define goals and roadmap
3. **Execution Phase**: Implement solutions
4. **Review Phase**: Monitor and optimize

## Conclusion

{topic} represents a critical component of organizational success. By following these guidelines and best practices, businesses can achieve their strategic objectives.

## Key Takeaways

- Understanding fundamentals is crucial
- Implementation requires careful planning
- Continuous optimization drives results
- Success depends on strategic execution
"""
            
            # Calculate SEO score
            keywords = [topic.lower(), "strategy", "implementation", "success"]
            seo_analysis = SEOAnalyzer.calculate_overall_seo_score(
                demo_content,
                keywords
            )
            
            # Save session
            session_data = {
                'session_id': st.session_state.session_id,
                'topic': topic,
                'target_seo_score': target_score,
                'generated_content': demo_content,
                'achieved_seo_score': seo_analysis['overall_score']
            }
            save_session(session_data)
            
            # Display results
            st.success(f"✅ Content Generated! SEO Score: {seo_analysis['overall_score']}/10")
            
            # Tabs
            tab1, tab2 = st.tabs(["📄 Content", "📊 SEO Analysis"])
            
            with tab1:
                st.markdown("### Generated Content")
                st.markdown(demo_content)
                
                st.download_button(
                    "📥 Download",
                    demo_content,
                    file_name=f"{topic.replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with tab2:
                st.markdown("### SEO Analysis")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Overall", f"{seo_analysis['overall_score']}/10")
                with col2:
                    st.metric("Keywords", f"{seo_analysis['keyword_score']}/10")
                with col3:
                    st.metric("Readability", f"{seo_analysis['readability_score']}/10")
                with col4:
                    st.metric("Structure", f"{seo_analysis['structure_score']}/10")
                
                st.json(seo_analysis['breakdown'])

# Footer
st.markdown("---")
st.caption("SEO Content Generator - Powered by AI")