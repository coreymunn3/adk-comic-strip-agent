from typing import List, Dict, Any, Optional
from google.adk.agents import LlmAgent, SequentialAgent, Agent, LoopAgent
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService
from pydantic import BaseModel, Field
from comic_maker.tools import generate_comic_strip_tool, exit_loop, stop_execution

FLASH_MODEL = 'gemini-2.5-flash'
PRO_MODEL='gemini-2.5-pro'

# ----------------------------------------------------------------------
# Sub-Agent Definitions using LlmAgent directly
# ----------------------------------------------------------------------

# 📚 Research Agent
research_agent = LlmAgent(
  model=FLASH_MODEL,
  name='ResearchAgent',
  instruction="""
    You are a meticulous historical researcher. Your task is to search the web
    for information about a given historical event provided in the user prompt
    
    Use the 'Google Search' tool to find:
    1. A chronological timeline of events.
    2. Key figures involved.
    3. Significant locations.
    4. The main outcome and impact.

    **Crucially**: Summarize this information into a concise, factual summary (around 200-400 words)
    that highlights the most impactful moments. Update the 'research_summary' field in the state with your summary.
    If no relevant information is found, set 'research_summary' to "NO_INFO_FOUND".
    """,
  tools=[google_search],
    output_key='research_summary'
)

#  GATE Research Agent
research_gate_agent = LlmAgent(
    model=FLASH_MODEL,
    name='ResearchGateAgent',
    instruction="""
    You are a gatekeeper. Your task is to check the 'research_summary' field in the state.
    If the 'research_summary' is "NO_INFO_FOUND", you MUST call the 'stop_execution' tool.
    Otherwise, do nothing.
    """,
    tools=[stop_execution],
)

# 📝 Storyboard Agent
storyboard_agent = LlmAgent(
    model=FLASH_MODEL,
    name='StoryboardAgent',
    instruction="""
    You are a storyboard artist. Your input is located in `state['research_summary']`. Based on the historical summary provided in the 'research_summary' field of the state,
    break down the event into exactly 4 distinct, sequential story segments. Each segment should briefly describe
    a key moment or scene suitable for a single comic panel. The story segments should be arranged in chronological order.
    
    Format your output as a numbered list.
    Example:
    1. Union troops prepare defensive positions on Cemetery Ridge.
    2. Confederate forces launch Pickett's Charge across open fields.
    3. The desperate last stand of the Iron Brigade.
    4. General Lee observes the unfolding disaster.
    
    If 'research_summary' is "NO_INFO_FOUND", output "NO_SEGMENTS".
    Otherwise, output only the numbered list of segments with no other titles, text, or formatting. 
    """,
    # This agent reads 'research_summary' from state implicitly via instruction.
    output_key='storyboard_segments_raw' # Output will be stored in state.storyboard_segments_raw
)


# ✍️ Image Prompt Generation Agent
image_prompt_generation_agent = LlmAgent(
    model=PRO_MODEL,
    name='ImagePromptGenerationAgent',
    instruction="""
    You are a creative visual prompt engineer for an AI image generator. Your input is a numbered list of storyboard segments from the 'storyboard_segments_raw' key in the session state.
    Your task is to create a single, consolidated prompt for generating a 4-panel comic strip in a 2x2 grid.
    The prompt MUST be structured as follows:
    "A single image containing a 4-panel comic strip in a 2x2 grid. The comic strip should be in a realistic, highly detailed historical illustration style, with no text or letters.

    Top-left panel: [Description of Panel 1]
    Top-right panel: [Description of Panel 2]
    Bottom-left panel: [Description of Panel 3]
    Bottom-right panel: [Description of Panel 4]"

    For each of the four storyboard segments, provide a detailed description for the corresponding panel, including:
    - **Environment/Setting**: A description of the location, time of day, and weather.
    - **Subject(s)**: A description of the key characters or objects in the scene, including their appearance and expressions.
    - **Action**: A detailed description of the action taking place in the scene.
    
    Example Input:
    1. The Japanese fleet secretly departing for Pearl Harbor.
    2. The first wave of Japanese aircraft launching a surprise attack.
    3. The USS Arizona exploding.
    4. President Roosevelt addressing the nation.
    
    Example Output:
    A single image containing a 4-panel comic strip in a 2x2 grid. The comic strip should be in a realistic, highly detailed historical illustration style, with no text or letters.

    Top-left panel: Environment/Setting: A vast, dark ocean under a cloudy, pre-dawn sky. Subject(s): A fleet of Japanese aircraft carriers, with sailors on deck preparing planes for takeoff. Admiral Yamamoto stands on the bridge of the flagship, his expression grim and determined. Action: The fleet is sailing silently and purposefully through the water.
    Top-right panel: Environment/Setting: The sky over Pearl Harbor, with the sun just beginning to rise. Subject(s): A squadron of Japanese Zeroes, their red sun markings clearly visible. The pilots are focused and determined. Action: The planes are diving towards the unsuspecting American fleet below, launching torpedoes and bombs.
    Bottom-left panel: Environment/Setting: The chaotic scene of the attack on Pearl Harbor, with smoke-filled skies and burning ships. Subject(s): The USS Arizona, its hull breached and on fire. Sailors are jumping from the deck into the oily water. Action: A massive explosion rips through the center of the ship, sending a fireball and a plume of black smoke high into the air.
    Bottom-right panel: Environment/Setting: A dimly lit room, with a large desk and a microphone. Subject(s): President Franklin D. Roosevelt, his face etched with grim determination. Action: He is speaking into the microphone, his fist clenched, as he addresses the nation and declares war.
    """,
    output_key='consolidated_image_prompt'
)

# 🎨 Image Generation Agent
image_generation_agent = LlmAgent(
    model=FLASH_MODEL,
    name='ImageGenerationAgent',
    instruction="""
    You are an AI image generation service. Your input is a consolidated image prompt from the 'consolidated_image_prompt' key in the session state.
    Your task is to call the `generate_comic_strip_tool` with the consolidated prompt to generate the comic strip.
    """,
    tools=[generate_comic_strip_tool],
    output_key='generated_comic_strip'
)

# 🧐 Image Prompt Evaluation Agent
image_prompt_evaluation_agent = LlmAgent(
    model=FLASH_MODEL,
    name='ImagePromptEvaluationAgent',
    instruction="""
    You are an AI image prompt evaluator. Your input is a consolidated image prompt for a 4-panel comic strip from the 'consolidated_image_prompt' key in the session state.
    Your task is to evaluate the prompt to ensure it will produce a visually diverse and narratively compelling comic strip.
    Analyze the "Subject(s)" and "Action" for each of the four panels.
    Compare each panel to every other panel.
    If any two panels have **either** a similar "Subject(s)" **or** a similar "Action", the evaluation fails.
    If the panels are sufficiently diverse in either subject or action, the evaluation passes.

    If the prompt meets these criteria, respond *exactly* with the phrase "PASS" and nothing else.
    If the prompt does not meet these criteria, provide a concise critique of the prompt, explaining which panels are too similar, and why. 
    """,
    output_key='prompt_critique'
)

#  refining agent
image_prompt_refiner_agent = LlmAgent(
    name="PromptRefinerAgent",
    model=FLASH_MODEL,
    include_contents='none',
    instruction="""
    You are a creative writing assistant. Your task is to refine a comic strip prompt based on a critique.
    **Consolidated Image Prompt:**
    ```
    {{consolidated_image_prompt}}
    ```
    **Critique:**
    {{prompt_critique}}

    **Task:**
    Analyze the 'Critique'.
    IF the critique is *exactly* "PASS":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Consolidated Image Prompt'. Output *only* the refined prompt.
    """,
    tools=[exit_loop],
    output_key='consolidated_image_prompt'
)

# ----------------------------------------------------------------------
# Looping Agent for Prompt Refinement
# ----------------------------------------------------------------------

image_prompt_refinement_agent = LoopAgent(
    name="ImagePromptEvaluationLoop",
    max_iterations=3,
    sub_agents=[
        image_prompt_evaluation_agent,
        image_prompt_refiner_agent,
    ],
)

# ----------------------------------------------------------------------
# Root Agent
# ----------------------------------------------------------------------

comic_strip_generator_agent = SequentialAgent(
    name="ComicStripGenerator",
    description="Generates a historical summary and a 4-panel comic strip.",
    sub_agents=[
        research_agent,
        research_gate_agent,
        storyboard_agent,
        image_prompt_generation_agent,
        image_prompt_refinement_agent,
        image_generation_agent,
    ],
)

root_agent = comic_strip_generator_agent
