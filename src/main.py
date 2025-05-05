import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import numpy as np
import os
import boto3 # Import boto3
import tempfile # To handle temporary file for model download

# Define the input data schema using Pydantic
class InferenceInput(BaseModel):
    # Example: Define the features your model expects
    # Replace with your actual feature names and types
    feature1: float
    feature2: float
    # Add more features as needed

# Define the output data schema using Pydantic
class InferenceOutput(BaseModel):
    prediction: float # Or list[float] if predicting multiple values

# Initialize FastAPI app
app = FastAPI(title="XGBoost Inference API")

# --- Configuration for S3 ---
# It's recommended to use environment variables for sensitive info like bucket names
S3_BUCKET_NAME = os.environ.get("S3_MODEL_BUCKET", "my-unique-microservice-bucket-12345") # Replace with your bucket name or env var
S3_MODEL_KEY = os.environ.get("S3_MODEL_KEY", "model/model.bst") # Replace with the key (path) in your bucket
LOCAL_MODEL_PATH = os.path.join(tempfile.gettempdir(), "model.bst") # Temporary path to store downloaded model

booster = None
s3_client = None

@app.on_event("startup")
async def load_model():
    """Loads the XGBoost model from S3 on startup."""
    global booster, s3_client
    print(f"Attempting to load model from S3 bucket '{S3_BUCKET_NAME}' with key '{S3_MODEL_KEY}'")

    try:
        s3_client = boto3.client('s3')
        # Download the model file from S3 to a temporary local path
        s3_client.download_file(S3_BUCKET_NAME, S3_MODEL_KEY, LOCAL_MODEL_PATH)
        print(f"Model downloaded successfully from S3 to {LOCAL_MODEL_PATH}")

        # Load the model from the downloaded file
        booster = xgb.Booster()
        booster.load_model(LOCAL_MODEL_PATH)
        print(f"Model loaded successfully from {LOCAL_MODEL_PATH}")

    except boto3.exceptions.S3UploadFailedError as e:
         # Handle case where key might be wrong or bucket doesn't exist, etc.
         # boto3.exceptions.ClientError is broader but NoCredentialsError, etc., might be relevant
         print(f"Error downloading model from S3: {e}. Check bucket name, key, and AWS credentials/permissions.")
         booster = None
    except xgb.core.XGBoostError as e:
        print(f"Error loading XGBoost model from downloaded file: {e}")
        booster = None
    except Exception as e:
        print(f"An unexpected error occurred during model loading: {e}")
        booster = None
    finally:
        # Clean up the downloaded file if it exists
        if os.path.exists(LOCAL_MODEL_PATH):
            try:
                os.remove(LOCAL_MODEL_PATH)
                print(f"Cleaned up temporary model file: {LOCAL_MODEL_PATH}")
            except OSError as e:
                print(f"Error removing temporary model file {LOCAL_MODEL_PATH}: {e}")


@app.post("/predict", response_model=InferenceOutput)
async def predict(input_data: InferenceInput):
    """
    Runs inference using the loaded XGBoost model.
    Takes input features and returns the prediction.
    """
    if booster is None:
        raise HTTPException(status_code=503, detail="Model is not loaded or failed to load.")

    try:
        # Convert input data to the format XGBoost expects (DMatrix or numpy array)
        # This example assumes input features are directly usable.
        # You might need preprocessing steps here.
        features = np.array([[input_data.feature1, input_data.feature2]]) # Adjust based on your features
        dmatrix = xgb.DMatrix(features)

        # Make prediction
        prediction = booster.predict(dmatrix)

        # Assuming the model returns a single prediction value
        result = float(prediction[0])

        return InferenceOutput(prediction=result)

    except xgb.core.XGBoostError as e:
        raise HTTPException(status_code=500, detail=f"XGBoost prediction error: {e}")
    except Exception as e:
        # Catch other potential errors during prediction/preprocessing
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {e}")

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    # Add more sophisticated checks if needed (e.g., model loaded status)
    model_status = "loaded" if booster is not None else "not loaded"
    return {"status": "ok", "model_status": model_status}

# --- Running the App ---
# To run the app, navigate to the 'src' directory in your terminal
# and run: uvicorn main:app --reload
#
# Example using curl to test the /predict endpoint (replace with actual features):
# curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d '{"feature1": 1.0, "feature2": 2.5}'
#
# Example using curl to test the /health endpoint:
# curl "http://127.0.0.1:8000/health"

if __name__ == "__main__":
    # This allows running the app directly using 'python main.py'
    # Uvicorn is the recommended way for development and production
    uvicorn.run(app, host="0.0.0.0", port=8000)

