import asyncio
import logging
import os
from random import randint
from time import sleep

import backend.config_manager as config_manager
import backend.data_manager as data_manager
from PIL import Image
import requests

# Initialize logger
logger = logging.getLogger(__name__)

# Function to open and display images based on a given prompt.
def open_images(prompt):
    folder_path = data_manager._resolve_path("data")  # Folder where the images are stored.
    prompt = prompt.replace(" ", "_")  # Replace spaces in the prompt with underscores.
    
    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)] 
    
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second before showing the next image.
            
        except IOError as e:
            logger.error(f"Unable to open {image_path}: {e}", exc_info=True)
            
# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {config_manager.get_api_key('HuggingFaceAPIKey')}"}

# Async function to send a query to the Hugging Face API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            if "image" in response.headers.get("Content-Type", ""):
                return response.content
            else:
                logger.error(f"[ImageGen] API returned non-image content: {response.text}")
        else:
            logger.error(f"[ImageGen] API error {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"[ImageGen] Request exception: {e}", exc_info=True)
    return None

# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []
    
    # Create 4 images generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Ensure Data directory exists
    folder_path = data_manager._resolve_path("data")
    os.makedirs(folder_path, exist_ok=True)
    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            filename = f"{prompt.replace(' ', '_')}{i + 1}.jpg"
            image_path = os.path.join(folder_path, filename)
            with open(image_path, "wb") as f:
                f.write(image_bytes)
        else:
            logger.warning(f"[ImageGen] Skipping image {i + 1} due to generation failure.")
            
# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  # Run the async image generation.
    open_images(prompt)  # Open the generated images
    
# Main loop to monitor for image generation requests
if __name__ == "__main__":
    image_data_path = os.path.join("frontend", "Files", "ImageGeneration.data")
    while True:
        
        try:
            # Read the status and prompt from the data file
            Data = data_manager.read_text(image_data_path, default="False,False").strip()
                
            if "," in Data:
                Prompt, Status = Data.rsplit(",", 1)
            else:
                Prompt, Status = "False", "False"
            
            # If the status indicates an image generation request
            if Status == "True":
                print("Generating Images...")
                try:
                    GenerateImages(prompt=Prompt)
                finally:
                    # Reset the status in the data file after generating images
                    data_manager.write_text(image_data_path, "False,False")
                break  # Exit the loop after processing the request.
                
            else:
                sleep(1)  # Wait for 1 second before checking the status again.
                
        except Exception as e:
            logger.error(f"Error in ImageGeneration: {e}", exc_info=True)
            sleep(1)