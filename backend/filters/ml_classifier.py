"""
ML-based Content Classifier
"""
import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


@dataclass
class ClassificationResult:
    """Classification result"""
    is_blocked: bool
    category: Optional[str]
    confidence: float
    scores: Dict[str, float]


class ContentClassifier:
    """ML-based content classifier"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.categories: List[str] = []
        self._loaded = False
        self._model_path = settings.FILTER_ML_MODEL_PATH
    
    def load(self, model_path: Optional[str] = None) -> None:
        """Load trained model"""
        if self._loaded:
            return
        
        path = model_path or self._model_path
        
        try:
            model_file = Path(path)
            if not model_file.exists():
                logger.warning("ML model not found, using fallback classifier")
                self._use_fallback()
                return
            
            with open(model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data.get('model')
                self.vectorizer = data.get('vectorizer')
                self.categories = data.get('categories', [])
            
            self._loaded = True
            logger.info("ML model loaded", categories=self.categories)
            
        except Exception as e:
            logger.error("Failed to load ML model", error=str(e))
            self._use_fallback()
    
    def _use_fallback(self) -> None:
        """Use simple fallback classifier"""
        self.categories = ["extremism", "terrorism", "propaganda", "spam"]
        
        # Simple keyword-based fallback
        self.fallback_keywords = {
            "extremism": [
                "extremist", "radical", "supremacist", "hate group",
                "neo-nazi", "violent extremism"
            ],
            "terrorism": [
                "terrorist", "bomb", "attack", "militant", "jihad"
            ],
            "propaganda": [
                "fake news", "conspiracy", "disinformation", "propaganda"
            ],
            "spam": [
                "click here", "buy now", "free money", "act now"
            ]
        }
        
        self._loaded = True
        logger.info("Using fallback classifier")
    
    def _fallback_classify(self, text: str) -> ClassificationResult:
        """Fallback classification using keywords"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.fallback_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score / len(keywords)
        
        max_category = max(scores, key=scores.get) if scores else None
        max_score = scores.get(max_category, 0) if max_category else 0
        
        is_blocked = max_score >= settings.FILTER_CONFIDENCE_THRESHOLD
        
        return ClassificationResult(
            is_blocked=is_blocked,
            category=max_category if is_blocked else None,
            confidence=max_score,
            scores=scores
        )
    
    def classify(self, text: str) -> ClassificationResult:
        """Classify text content"""
        if not self._loaded:
            self.load()
        
        # Use fallback if no real model
        if not hasattr(self, 'model') or self.model is None:
            return self._fallback_classify(text)
        
        try:
            # Vectorize text
            features = self.vectorizer.transform([text])
            
            # Get predictions
            probabilities = self.model.predict_proba(features)[0]
            
            # Build scores dict
            scores = {}
            for idx, category in enumerate(self.categories):
                scores[category] = float(probabilities[idx])
            
            # Find max
            max_category = max(scores, key=scores.get)
            max_score = scores[max_category]
            
            is_blocked = max_score >= settings.FILTER_CONFIDENCE_THRESHOLD
            
            return ClassificationResult(
                is_blocked=is_blocked,
                category=max_category if is_blocked else None,
                confidence=max_score,
                scores=scores
            )
            
        except Exception as e:
            logger.error("Classification failed", error=str(e))
            return self._fallback_classify(text)
    
    def classify_batch(self, texts: List[str]) -> List[ClassificationResult]:
        """Classify multiple texts"""
        return [self.classify(text) for text in texts]
    
    def filter_results(
        self,
        results: List[Dict],
        text_fields: List[str] = None,
        threshold: float = None
    ) -> List[Dict]:
        """Filter search results using ML classifier"""
        if not self._loaded:
            self.load()
        
        if text_fields is None:
            text_fields = ["title", "snippet"]
        
        filtered = []
        threshold = threshold or settings.FILTER_CONFIDENCE_THRESHOLD
        
        for result in results:
            # Combine text from all fields
            text_parts = []
            for field in text_fields:
                if field in result and result[field]:
                    text_parts.append(str(result[field]))
            
            combined_text = " ".join(text_parts)
            
            # Classify
            classification = self.classify(combined_text)
            
            if not classification.is_blocked:
                filtered.append(result)
            else:
                # Mark as filtered
                result["filtered"] = True
                result["filter_reason"] = [classification.category]
                result["filter_confidence"] = classification.confidence
        
        return filtered
    
    def train(
        self,
        training_data: List[Tuple[str, str]],
        output_path: str
    ) -> None:
        """
        Train new model
        
        Args:
            training_data: List of (text, category) tuples
            output_path: Path to save trained model
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report
            
            logger.info("Training content classifier", samples=len(training_data))
            
            # Prepare data
            texts = [text for text, _ in training_data]
            labels = [category for _, category in training_data]
            self.categories = list(set(labels))
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42
            )
            
            # Create pipeline
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    stop_words='english'
                )),
                ('clf', LogisticRegression(
                    max_iter=1000,
                    class_weight='balanced',
                    multi_class='multinomial'
                ))
            ])
            
            # Train
            pipeline.fit(X_train, y_train)
            
            # Evaluate
            y_pred = pipeline.predict(X_test)
            report = classification_report(y_test, y_pred)
            logger.info("Training complete\n" + report)
            
            # Save model
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                pickle.dump({
                    'model': pipeline,
                    'vectorizer': None,  # Included in pipeline
                    'categories': self.categories
                }, f)
            
            self.model = pipeline
            self.categories = list(set(labels))
            self._loaded = True
            
            logger.info("Model saved", path=output_path)
            
        except ImportError:
            logger.error("sklearn not available for training")
            raise
        except Exception as e:
            logger.error("Training failed", error=str(e))
            raise


# Global classifier instance
content_classifier = ContentClassifier()


def get_content_classifier() -> ContentClassifier:
    """Get content classifier dependency"""
    if not content_classifier._loaded:
        content_classifier.load()
    return content_classifier
