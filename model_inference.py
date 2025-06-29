# model_inference.py
import os
import uuid
import tempfile
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai.vision_models import ImageGenerationModel, Image

from gcp_utils import download_from_gcs
from config import SYSTEM_INSTRUCTION_FOR_GEMINI, BASE_USER_IMAGE_PROMPT

def generate_image_from_gcs_references(
    reference_image_gcs_uri: str,
    product_image_gcs_uri: str,
    text_gcs_uri: str,
    reference_mime_type: str,
    product_mime_type: str
) -> tuple[str | None, str | None]:
    """
    Generates an image using Gemini and Imagen based on GCS references.
    Returns (path_to_image, None) on success.
    Returns (None, error_message) on failure.
    """
    # --- Step 1: Generate prompt with Gemini ---
    try:
        print("\n--- Step 1: Analyzing inputs with Gemini ---")
        vision_model = GenerativeModel("gemini-2.5-flash")
        
        reference_image_data = download_from_gcs(reference_image_gcs_uri)
        product_image_data = download_from_gcs(product_image_gcs_uri)
        text_data = download_from_gcs(text_gcs_uri).decode('utf-8')

        reference_part = Part.from_data(data=reference_image_data, mime_type=reference_mime_type)
        product_image_part = Part.from_data(data=product_image_data, mime_type=product_mime_type)

        gemini_input_prompt = f"""{SYSTEM_INSTRUCTION_FOR_GEMINI}
        **Reference Image Context:** The first image is a style reference for filling a silhouette with a word cloud.
        **Extract product attributes from:** {text_data}
        **User's Request:** {BASE_USER_IMAGE_PROMPT}
        Based on the reference style, the product image's silhouette, and its attributes, generate a detailed prompt for an image generation model. This prompt should describe the visual elements for creating a word cloud within the product's silhouette."""

        gemini_response = vision_model.generate_content(
            [reference_part, product_image_part, gemini_input_prompt],
            generation_config={"temperature": 0.2}
        )
        generated_imagen_prompt = gemini_response.text
        print(f"Gemini generated prompt successfully.")
        print(f"--- Generated Imagen Prompt ---\n{generated_imagen_prompt}\n-----------------------------")

    except Exception as e:
        error_message = f"Error during Gemini prompt generation: {e}"
        print(error_message)
        return None, error_message

    # --- Step 2: Generate image with Imagen ---
    try:
        print("\n--- Step 2: Generating product ad image with Imagen ---")
        imagen_model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-06-06")
        imagen_response = imagen_model.generate_images(
            prompt=generated_imagen_prompt,
            number_of_images=1,
        )

        if not imagen_response.images:
            error_message = "Imagen generation failed: The model did not return any images. This is often due to safety filters blocking the generated prompt. Try modifying your attributes or the base prompt."
            print(error_message)
            return None, error_message

        generated_image = imagen_response.images[0]
        temp_dir = tempfile.mkdtemp()
        output_image_path = os.path.join(temp_dir, f"generated_ad_{uuid.uuid4()}.png")
        generated_image.save(output_image_path)
        print(f"Generated image saved locally to: {output_image_path}")
        return output_image_path, None # Success!

    except Exception as e:
        error_message = f"An exception occurred during Imagen generation: {e}"
        print(error_message)
        return None, error_message