import sys
import os
import gradio as gr

# Add the 'app' directory to the Python path so inner modules can be found
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.main import app as fastapi_app

# Create a basic Gradio interface
demo = gr.Blocks()

with demo:
    gr.Markdown("# 🚀 Project Sahakar FastAPI Backend is Running!")
    gr.Markdown("The backend is serving APIs perfectly. You can visit `/docs` in the URL to see the FastAPI Swagger UI.")

# Mount the FastAPI app onto Gradio (this is what Hugging Face will serve)
app = gr.mount_gradio_app(fastapi_app, demo, path="/")
