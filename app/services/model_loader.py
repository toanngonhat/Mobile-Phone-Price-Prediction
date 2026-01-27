"""Model loader service for loading trained ML models"""
import os
import pickle
from pathlib import Path


class ModelLoader:
    """Handles loading and managing ML models"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize model loader
        
        Args:
            model_path: Path to the trained model file
        """
        if model_path is None:
            # Default model path
            root_dir = Path(__file__).parent.parent.parent
            model_path = root_dir / "ml" / "trained_model.pkl"
        
        self.model_path = model_path
        self.model = None
    
    def load_model(self):
        """
        Load the trained model from disk
        
        Returns:
            Loaded model object or None if model doesn't exist
        """
        if not os.path.exists(self.model_path):
            print(f"Model file not found at {self.model_path}")
            return None
        
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Model loaded successfully from {self.model_path}")
            return self.model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    
    def save_model(self, model, path: str = None):
        """
        Save a trained model to disk
        
        Args:
            model: Trained model object
            path: Optional custom path to save the model
        """
        save_path = path if path else self.model_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Model saved successfully to {save_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
            raise
    
    def get_model(self):
        """
        Get the currently loaded model
        
        Returns:
            Current model object or None
        """
        return self.model
