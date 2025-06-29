# app.py
import gradio as gr
import os
import uuid

from config import (
    DEFAULT_REFERENCE_IMAGE_GCS_URI,
    CUSTOM_CSS,
    GCS_BUCKET_NAME
)
from gcp_utils import initialize_gcp_clients, upload_to_gcs, get_mime_type, storage_client
from model_inference import generate_image_from_gcs_references

def gradio_interface_fn(uploaded_product_file_path: str, product_attributes_text: str):
    """Main function for the Gradio interface."""
    # Ensure GCP clients are initialized
    if not initialize_gcp_clients():
        print("Error: GCP client not initialized. Check server logs.")
        return None # Or return a placeholder error image/message in UI

    if not uploaded_product_file_path or not product_attributes_text:
        print("Error: Product image and attributes are required.")
        return None

    print("\n Starting new image generation process...")

    try:
        print("  - Uploading files to GCS...")
        unique_id = str(uuid.uuid4())
        
        # Upload product image
        gcs_product_image_blob_name = f"gradio_uploads/product_image/{unique_id}_{os.path.basename(uploaded_product_file_path)}"
        product_mime_type = get_mime_type(uploaded_product_file_path)
        product_image_gcs_uri = upload_to_gcs(uploaded_product_file_path, gcs_product_image_blob_name)
        
        # Upload product attributes text
        gcs_text_blob_name = f"gradio_uploads/text/{unique_id}_attributes.txt"
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_text_blob_name)
        blob.upload_from_string(product_attributes_text.strip().encode('utf-8'))
        text_gcs_uri = f"gs://{bucket.name}/{gcs_text_blob_name}"

    except Exception as e:
        print(f"Error during GCS upload: {e}")
        return None

    generated_image_path, error_message = generate_image_from_gcs_references(
        DEFAULT_REFERENCE_IMAGE_GCS_URI,
        product_image_gcs_uri,
        text_gcs_uri,
        "image/png", # Mime type for the default reference image
        product_mime_type
    )

    if error_message:
        print(f"Process failed. Reason: {error_message}")
        # The UI will just show an empty image box, the detailed error is in the terminal.
        return None
        
    print(" Process completed successfully!")
    return generated_image_path


# --- Gradio UI Definition ---
with gr.Blocks(title="AI Product Ad Generator", css=CUSTOM_CSS) as demo:
    gr.Markdown(
        """
        # 🛍️ AI Product Advertisement Image Generator
        Upload a **product image** for its shape, and provide its attributes to create a stunning ad!
        """
    )
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Image Inputs & Attributes")
            product_image_input = gr.Image(type="filepath", label="Upload Product Image (Required for silhouette)")
            product_attributes_input = gr.Textbox(
                lines=5,
                label="Provide the description of the product where it highlights its attributes.",
                value="Example : Unleash peak performance with our ultra-light, durable, and waterproof adventure backpack, designed for the most demanding trails.",
            )
            generate_button = gr.Button("Generate Ad Image", variant="primary")
        with gr.Column():
            gr.Markdown("### Generated Output")
            generated_image_output = gr.Image(label="Generated Product Advertisement", interactive=False)

    gr.Markdown(
        """
        ### How it works:
        1.  You upload a **product image** and enter its **description with key attributes**.
        2.  Click on **Generate Ad Image**.
        3.  The generated advertisement image will appear in a few moments.
        """
    )

    generate_button.click(
        fn=gradio_interface_fn,
        inputs=[product_image_input, product_attributes_input],
        outputs=[generated_image_output],
        show_progress="full"
    )

if __name__ == "__main__":
    demo.launch(debug=True, share=False)