import logging
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from src.extractors.preprocessor import clean_text_for_ml

logger = logging.getLogger(__name__)

# Small mocked dataset of legal clauses for training the Naive Bayes model.
# In a real-world scenario, this would be loaded from a CSV/DB with thousands of examples.
TRAINING_DATA = [
    # Confidentiality
    ("The receiving party shall keep all proprietary information confidential.", "Confidentiality"),
    ("Neither party shall disclose the terms of this Agreement to any third party.", "Confidentiality"),
    ("Confidential information includes trade secrets, financial data, and source code.", "Confidentiality"),
    ("The parties agree not to disclose any confidential information to third parties.", "Confidentiality"),
    ("All proprietary data shall remain the property of the disclosing party.", "Confidentiality"),
    
    # Termination
    ("This agreement may be terminated by either party with 30 days written notice.", "Termination"),
    ("In the event of a material breach, the non-breaching party may terminate immediately.", "Termination"),
    ("Either party may end this contract at any time for convenience.", "Termination"),
    ("Upon termination, all licenses granted hereunder shall immediately cease.", "Termination"),
    
    # Payment
    ("The client shall pay the contractor the sum of $10,000 within 15 days.", "Payment"),
    ("Invoices are due net 30 from the date of receipt.", "Payment"),
    ("Late payments will accrue interest at a rate of 1.5% per month.", "Payment"),
    ("The receiving party agrees to pay the sum of $50,000 for the consulting services rendered.", "Payment"),
    ("Payment must be made in USD via wire transfer.", "Payment"),
    
    # Liability
    ("In no event shall either party be liable for any indirect or consequential damages.", "Liability"),
    ("The total liability of the vendor shall not exceed the total fees paid under this agreement.", "Liability"),
    ("Neither party shall be held liable for failure to perform due to force majeure.", "Liability"),
    ("The contractor indemnifies the client against all third party claims of IP infringement.", "Liability"),
    
    # General
    ("This agreement constitutes the entire understanding between the parties.", "General"),
    ("Any amendments to this contract must be made in writing.", "General"),
    ("This contract shall be governed by the laws of the State of Delaware.", "General"),
    ("The headings in this document are for convenience only.", "General"),
    ("Notices shall be sent via certified mail.", "General")
]

class ClauseClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', MultinomialNB())
        ])
        self.is_trained = False
        
    def train(self):
        """Trains the Naive Bayes classifier on the mocked dataset."""
        logger.info("Training Naive Bayes Clause Classifier...")
        
        # Preprocess the training text just as we do during inference
        X_train = [clean_text_for_ml(text) for text, _ in TRAINING_DATA]
        y_train = [label for _, label in TRAINING_DATA]
        
        # Train model
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True
        logger.info("Training complete.")

    def predict(self, text: str, clean_text: str = None) -> Tuple[str, float]:
        """
        Predicts the category of a clause.
        Returns the category label and the confidence probability.
        """
        if not self.is_trained:
            self.train()
            
        if not clean_text:
            clean_text = clean_text_for_ml(text)
            
        # If the text is completely empty or stripped to nothing
        if not clean_text.strip():
            return "General", 0.0

        prediction = self.pipeline.predict([clean_text])[0]
        
        # Get probability
        probabilities = self.pipeline.predict_proba([clean_text])[0]
        classes = self.pipeline.classes_
        confidence = probabilities[list(classes).index(prediction)]
        
        return prediction, float(confidence)

# Singleton instance to be loaded once
classifier = ClauseClassifier()

def get_clause_classifier() -> ClauseClassifier:
    if not classifier.is_trained:
        classifier.train()
    return classifier
