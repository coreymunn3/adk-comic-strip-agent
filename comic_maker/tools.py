from google import genai
from google.genai import types
from google.adk.tools import ToolContext
from google import genai
from google.genai import types

client = genai.Client(vertexai=True)

def exit_loop(tool_context: ToolContext):
    """Call this function to exit the loop."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}

async def generate_comic_strip_tool(prompt: str, tool_context: ToolContext):
    """
    Generates a comic strip based on the provided prompt.

    Args:
        prompt: The text prompt to generate the comic strip from.
        tool_context: The context for the tool.

    Returns:
        A dictionary with the status and message.
    """
    try:
        response = client.models.generate_images(
            # model="imagen-3.0-generate-002",
            model='imagen-4.0-generate-preview-06-06',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",  # A square aspect ratio is better for a 2x2 grid
                safety_filter_level="block_low_and_above",
                person_generation="allow_adult",
            ),
        )
        if response.generated_images is not None:
            for generated_image in response.generated_images:
                image_bytes = generated_image.image.image_bytes
                artifact_name = "comic_strip.png"
                report_artifact = types.Part.from_bytes(
                    data=image_bytes, mime_type="image/png"
                )
                await tool_context.save_artifact(artifact_name, report_artifact)
                return {
                    "status": "success",
                    "message": f"Image generated. ADK artifact: {artifact_name}.",
                    "artifact_name": artifact_name,
                }
        else:
            error_details = str(response)
            return {
                "status": "error",
                "message": f"No images generated. Response: {error_details}",
            }
    except Exception as e:
        return {"status": "error", "message": f"No images generated. {e}"}
