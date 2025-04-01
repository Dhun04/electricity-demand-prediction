import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import numpy as np
import math
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to your Firebase service account key file (you'll need to download this from Firebase console)
# For now, we'll use a placeholder that you'll need to replace
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "https://electricity-a1e47-default-rtdb.firebaseio.com")

def connect_to_firebase():
    """Connect to Firebase Realtime Database"""
    try:
        # Check if app is already initialized
        if not firebase_admin._apps:
            # Initialize the Firebase app with credentials
            if os.path.exists(FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': FIREBASE_DATABASE_URL
                })
                print("Successfully connected to Firebase Realtime Database!")
            else:
                print(f"Firebase credentials file not found at: {FIREBASE_CREDENTIALS_PATH}")
                print("Please follow the instructions to set up Firebase:")
                print("1. Go to Firebase Console (https://console.firebase.google.com/)")
                print("2. Create a new project or use an existing one")
                print("3. Go to Project Settings > Service accounts")
                print("4. Generate a new private key (this will download a JSON file)")
                print("5. Save the JSON file to your project directory")
                print("6. Update the .env file with the path to this file")
                return None
        
        # Return the database reference
        return db.reference('/')
        
    except Exception as e:
        print(f"Failed to connect to Firebase: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

def clean_for_json(value):
    """Clean values for JSON compatibility (handling NaN, Infinity, etc.)"""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0.0  # Replace NaN and Infinity with 0.0
    return value

def import_csv_to_firebase(csv_path):
    """Import CSV data into Firebase Realtime Database"""
    # Read CSV file
    try:
        df = pd.read_csv(csv_path)
        
        # Replace NaN values with 0
        df = df.fillna(0)
        
        # Connect to Firebase
        ref = connect_to_firebase()
        if ref is None:
            print("Using CSV file directly since Firebase connection failed")
            return df
        
        try:
            # Convert DataFrame to dictionary format suitable for Firebase
            # Use timestamp as the key for each record
            data_dict = {}
            for idx, row in df.iterrows():
                # Create a unique key for each record
                key = f"record_{idx}"
                
                # Convert row to dict and clean values for JSON compatibility
                row_dict = {}
                for column, value in row.items():
                    row_dict[column] = clean_for_json(value)
                
                data_dict[key] = row_dict
            
            # Update Firebase with the data
            # Note: This will overwrite existing data!
            print("Uploading data to Firebase...")
            ref.child('electricity_demand').set(data_dict)
            
            print(f"Data successfully imported into Firebase! Imported {len(data_dict)} records.")
            return df
        except Exception as e:
            print(f"Error importing data to Firebase: {e}")
            return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def get_data_from_firebase():
    """Retrieve data from Firebase Realtime Database"""
    # Connect to Firebase
    ref = connect_to_firebase()
    if ref is None:
        print("Using CSV file directly since Firebase connection failed")
        return pd.read_csv('Final 2023.csv')
    
    try:
        # Get all records from Firebase
        demand_ref = ref.child('electricity_demand')
        data_dict = demand_ref.get()
        
        if not data_dict:
            print("No data found in Firebase. Using CSV file as fallback.")
            return pd.read_csv('Final 2023.csv')
        
        # Convert the nested dictionary to a list of dictionaries
        records = [record_data for record_data in data_dict.values()]
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        return df
    except Exception as e:
        print(f"Error retrieving data from Firebase: {e}")
        # Fall back to CSV file
        return pd.read_csv('Final 2023.csv')

if __name__ == "__main__":
    # Import CSV data into Firebase
    csv_path = "Final 2023.csv"
    import_csv_to_firebase(csv_path) 