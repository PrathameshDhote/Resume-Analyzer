import os
import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# LangChain imports for LLM prompting
from langchain_openai import ChatOpenAI 
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_core.messages import BaseMessage, AIMessage

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Models for Resume Analysis ---
class ResumeAnalysis(BaseModel):
    overall_fit_score: float = Field(description="Overall fit score between 0-100")
    missing_skills: List[str] = Field(description="List of skills missing from the resume but required for the job")
    matching_skills: List[str] = Field(description="List of skills that match between resume and job description")
    experience_gap: str = Field(description="Analysis of experience gaps or mismatches")
    improvement_suggestions: List[str] = Field(description="Concrete suggestions to improve the resume")
    suggested_bullet_points: Dict[str, List[str]] = Field(description="Improved bullet points for each resume section")
    ats_optimization: List[str] = Field(description="ATS (Applicant Tracking System) optimization suggestions")
    confidence_score: Literal["High", "Medium", "Low"] = Field(description="Confidence in the analysis")

class AgentState(BaseModel):
    query: str
    resume_text: str = Field(description="Extracted text from the uploaded resume")
    job_description: str = Field(description="Job description provided by user")
    chat_history: List[BaseMessage] = Field(default_factory=list)

# --- Initialize LLMs (OpenRouter Free Models) ---
llms: Dict[str, Any] = {}

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    logger.error("OPENROUTER_API_KEY not found. No LLMs can be initialized without it.")
    raise ValueError("OPENROUTER_API_KEY is required to initialize free OpenRouter models.")

logger.info("Initializing LLMs using OpenRouter (free models prioritized).")

# Primary LLM
if openrouter_api_key:
    try:
        llms["google/gemini-flash-1.5"] = ChatOpenAI(
            model="google/gemini-flash-1.5",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.0  
        )
        logger.info("Initialized google/gemini-flash-1.5 via OpenRouter (free).")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini Flash: {e}. Skipping.")
        llms["google/gemini-flash-1.5"] = None

    # Fallback LLM
    try:
        llms["z-ai/glm-4.5-air:free"] = ChatOpenAI(
            model="z-ai/glm-4.5-air:free",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.0
        )
        logger.info("Initialized z-ai/glm-4.5-air:free via OpenRouter (free).")
    except Exception as e:
        logger.warning(f"Failed to initialize Qwen: {e}. Skipping.")
        llms["z-ai/glm-4.5-air:free"] = None

# --- Resume Analysis Prompt ---
RESUME_ANALYSIS_PROMPT = """You are an expert resume analyst and career coach with extensive experience in recruitment and ATS systems.

Your task is to analyze the provided resume against the given job description and provide comprehensive feedback.

**Analysis Guidelines:**
1. **Scoring**: Provide an overall fit score (0-100) based on skills match, experience relevance, and role alignment.
2. **Skills Analysis**: Identify missing skills from the job requirements and highlight matching skills.
3. **Experience Gap**: Analyze any experience mismatches or gaps compared to job requirements.
4. **Improvement Suggestions**: Provide actionable advice to strengthen the resume.
5. **ATS Optimization**: Suggest keywords and formatting improvements for ATS compatibility.
6. **Bullet Points**: Rewrite key bullet points to be more impactful and relevant.

**Resume Content:**
{resume_text}

**Job Description:**
{job_description}

**Output Requirements:**
- Return your analysis in the exact JSON format specified in the schema
- Be specific and actionable in your suggestions
- Use industry-standard terminology
- Ensure all suggestions are realistic and implementable
- Focus on measurable improvements

{format_instructions}"""

# Get the primary and fallback LLMs
primary_llm = llms.get("google/gemini-flash-1.5")
fallback_llm = llms.get("qwen/qwen3-14b:free")

if not primary_llm and not fallback_llm:
    logger.error("No LLMs available. Cannot proceed with resume analysis.")
    raise RuntimeError("At least one LLM must be available for resume analysis.")

# Use primary if available, otherwise fallback
analysis_llm = primary_llm if primary_llm else fallback_llm
logger.info(f"Using {analysis_llm.model_name} for resume analysis.")

# --- Resume Analysis Function ---
async def analyze_resume(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes a resume against a job description and returns structured feedback.
    """
    logger.info(f"Starting resume analysis for query: '{state.query[:50]}...'")
    
    if not state.resume_text.strip():
        logger.error("No resume text provided for analysis.")
        return {
            "analysis_result": None,
            "error": "No resume text provided for analysis."
        }
    
    if not state.job_description.strip():
        logger.error("No job description provided for analysis.")
        return {
            "analysis_result": None,
            "error": "No job description provided for analysis."
        }

    try:
        # Create JSON output parser
        parser = JsonOutputParser(pydantic_object=ResumeAnalysis)
        
        # Create output fixing parser to handle malformed JSON
        output_fixing_parser = OutputFixingParser.from_llm(
            parser=parser,
            llm=analysis_llm
        )
        
        # Create the analysis prompt template
        analysis_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(RESUME_ANALYSIS_PROMPT),
            HumanMessagePromptTemplate.from_template("Please analyze this resume and provide your detailed assessment in JSON format.")
        ])
        
        # Create the analysis chain
        analysis_chain = analysis_template | analysis_llm | output_fixing_parser
        
        # Execute the analysis
        analysis_result = await analysis_chain.ainvoke({
            "resume_text": state.resume_text,
            "job_description": state.job_description,
            "format_instructions": parser.get_format_instructions()
        })
        
        if analysis_result is None:
            logger.warning("Analysis result is None after LLM invocation.")
            return {
                "analysis_result": None,
                "error": "Analysis failed to generate results."
            }
        
        logger.info(f"Resume analysis completed successfully. Overall fit score: {analysis_result.get('overall_fit_score', 'N/A')}")
        
        return {
            "analysis_result": analysis_result,
            "final_response": format_analysis_response(analysis_result),
            "error": None
        }
        
    except OutputParserException as e:
        logger.error(f"Resume analysis: LLM output parsing failed: {e.llm_output}", exc_info=True)
        return {
            "analysis_result": None,
            "error": f"Analysis failed due to output format error: {str(e)}",
            "raw_output": getattr(e, 'llm_output', 'No raw output available')
        }
    
    except Exception as e:
        logger.error(f"Resume analysis: General error: {e}", exc_info=True)
        return {
            "analysis_result": None,
            "error": f"An unexpected error occurred during analysis: {str(e)}"
        }

def format_analysis_response(analysis: Dict[str, Any]) -> str:
    """
    Format the analysis result into a human-readable response.
    """
    try:
        response_parts = []
        
        # Overall Score
        score = analysis.get('overall_fit_score', 0)
        response_parts.append(f" **Overall Fit Score: {score}/100**")
        
        if score >= 80:
            response_parts.append(" Excellent match for this role!")
        elif score >= 60:
            response_parts.append(" Good match with room for improvement")
        else:
            response_parts.append(" Significant improvements needed")
        
        # Matching Skills
        matching_skills = analysis.get('matching_skills', [])
        if matching_skills:
            response_parts.append(f"\n **Matching Skills ({len(matching_skills)}):**")
            for skill in matching_skills[:5]:  # Show top 5
                response_parts.append(f"• {skill}")
        
        # Missing Skills
        missing_skills = analysis.get('missing_skills', [])
        if missing_skills:
            response_parts.append(f"\n **Skills to Develop ({len(missing_skills)}):**")
            for skill in missing_skills[:5]:  # Show top 5
                response_parts.append(f"• {skill}")
        
        # Experience Gap
        exp_gap = analysis.get('experience_gap', '')
        if exp_gap:
            response_parts.append(f"\n **Experience Analysis:**\n{exp_gap}")
        
        # Top Improvements
        improvements = analysis.get('improvement_suggestions', [])
        if improvements:
            response_parts.append(f"\n **Top Improvement Suggestions:**")
            for i, suggestion in enumerate(improvements[:3], 1):
                response_parts.append(f"{i}. {suggestion}")
        
        # ATS Optimization
        ats_tips = analysis.get('ats_optimization', [])
        if ats_tips:
            response_parts.append(f"\n **ATS Optimization Tips:**")
            for tip in ats_tips[:3]:
                response_parts.append(f"• {tip}")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error formatting analysis response: {e}")
        return f"Analysis completed with score: {analysis.get('overall_fit_score', 'N/A')}/100. See detailed results for more information."

# --- Example Usage ---
async def main():
    print("--- Testing Resume Analysis ---")
    
    # Sample resume text (you would extract this from PDF)
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    • 3 years Python development
    • Built web applications using Django and Flask
    • Experience with PostgreSQL databases
    • Worked in agile development teams
    
    Skills:
    Python, JavaScript, SQL, Git, Linux
    
    Education:
    Bachelor's in Computer Science
    """
    
    # Sample job description
    sample_jd = """
    Senior Python Developer
    
    Requirements:
    • 5+ years Python experience
    • FastAPI or Django expertise
    • AWS cloud experience
    • Docker containerization
    • Team leadership experience
    • Bachelor's degree in CS or related field
    """
    
    # Create test state
    test_state = AgentState(
        query="Analyze my resume for this Senior Python Developer position",
        resume_text=sample_resume,
        job_description=sample_jd
    )
    
    print(f"Query: {test_state.query}")
    print("Analyzing resume...")
    
    result = await analyze_resume(test_state)
    
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print("\n--- Analysis Result ---")
        print(result.get("final_response", "No formatted response available"))
        
        print("\n--- Raw JSON ---")
        if result.get("analysis_result"):
            print(json.dumps(result["analysis_result"], indent=2))

if __name__ == "__main__":
    asyncio.run(main())
