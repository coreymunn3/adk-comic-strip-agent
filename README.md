# Comic Maker Agent

This project showcases a sophisticated agent designed to automatically generate a 4-panel comic strip from a user-provided historical event. The agent is orchestrated as a sequence of specialized sub-agents, each performing a specific task in the comic creation pipeline.

## Setup

To run this project, you need to set up your environment variables. Create a `.env` file in the root of the project and add the following:

```bash
GOOGLE_CLOUD_PROJECT="agent-idk-test"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI="True"
GOOGLE_API_KEY="YOUR_API_KEY"
```

After setting up the environment variables, install the dependencies using Poetry:

```bash
poetry install
```

Then, you can run the web client:

```bash
poetry run adk web
```

## Orchestration

The `comic_strip_generator_agent` is a `SequentialAgent` that orchestrates the entire workflow. It executes the following sub-agents in order:

1.  **`research_agent`**: Researches the historical event.
2.  **`storyboard_agent`**: Creates a storyboard from the research.
3.  **`image_prompt_generation_agent`**: Generates a detailed image prompt.
4.  **`image_prompt_refinement_agent`**: A loop that refines the image prompt.
5.  **`image_generation_agent`**: Generates the final comic strip image.

## Sub-Agents

### 1. Research Agent (`research_agent`)

- **Purpose:** To gather factual information about a given historical event.
- **Functionality:** Uses Google Search to find a chronological timeline, key figures, significant locations, and the outcome of the event. It then synthesizes this information into a concise summary.

### 2. Storyboard Agent (`storyboard_agent`)

- **Purpose:** To break down the historical event into a visual narrative.
- **Functionality:** Takes the research summary and divides it into four distinct, sequential story segments, each suitable for a single comic panel.

### 3. Image Prompt Generation Agent (`image_prompt_generation_agent`)

- **Purpose:** To create a detailed, effective prompt for the AI image generator.
- **Functionality:** Converts the four storyboard segments into a single, consolidated prompt. This prompt specifies a 2x2 grid layout and provides detailed descriptions for each panel, including the environment, subjects, and action.

### 4. Image Prompt Refinement Agent (`image_prompt_refinement_agent`)

- **Purpose:** To ensure the generated comic strip is visually diverse and narratively compelling.
- **Functionality:** This is a `LoopAgent` that iteratively refines the image prompt. It consists of two sub-agents:
  - **`image_prompt_evaluation_agent`**: Evaluates the prompt to ensure that the panels are sufficiently different in terms of their subjects and actions.
  - **`image_prompt_refiner_agent`**: If the evaluation fails, this agent refines the prompt based on the critique provided by the evaluation agent. The loop continues until the prompt passes the evaluation or the maximum number of iterations is reached.

### 5. Image Generation Agent (`image_generation_agent`)

- **Purpose:** To generate the final comic strip.
- **Functionality:** Calls the `generate_comic_strip_tool` with the refined, consolidated prompt to create the 4-panel comic strip image.

## Other Agents

This project also includes a simple `test_agent` that can provide the time and weather for New York. It serves as a basic example of an agent.

## Continue Learning

While developing I found this [masterclass](https://www.youtube.com/watch?v=P4VFL9nIaIA) by a youtube channel called aiwithbrandon to be very helpful and informative,
and includes more instructions about setting up your environment and google account for api billing, which some may require.
