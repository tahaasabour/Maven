from typing import Any, Dict
from transformers import pipeline

class hugging_face_moderator:
    def __init__(self):
        self.classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)

    def moderate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        text = data.get("body", "")
        if not text:
            return data
        try:
            results = self.classifier(text)
            if isinstance(results, list) and len(results) > 0 and isinstance(results[0], list):
                results = results[0]
            toxic_labels = [r['label'] for r in results if r['score'] >= 0.5] 
            toxic = len(toxic_labels) > 0
            if toxic:
                data["moderation_flags"] = toxic_labels
                data["citations"] = data.get("citations", []) + ["abstain: moderation"]
                data["body"] = ""  

            return data

        except Exception as e:
            raise RuntimeError(f"Hugging Face moderation failed: {e}")
