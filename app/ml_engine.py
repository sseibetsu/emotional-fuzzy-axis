from transformers import pipeline


class EmotionArchitect:
    def __init__(self):
        print("Загрузка...")
        self.classifier = pipeline(
            task="text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=None
        )
        print("Нейросеть работает.")

    def get_coordinates(self, text):
        """
        Возвращает координаты и детальную разбивку по эмоциям.
        """
        results = self.classifier(text)[0]
        scores = {item['label']: item['score'] for item in results}

        # 1. Позитивчик
        val_joy = scores.get(
            'joy', 0) + scores.get('excitement', 0) + scores.get('optimism', 0)
        val_gratitude = scores.get('gratitude', 0) + \
            scores.get('admiration', 0)
        val_love = scores.get('love', 0) + scores.get('caring', 0)
        val_interest = scores.get('curiosity', 0) + scores.get('amusement', 0)

        # 2. Негативчик
        val_anger = scores.get('anger', 0) + scores.get('annoyance', 0)
        val_sadness = scores.get('sadness', 0) + scores.get('grief', 0)
        val_shame = scores.get('remorse', 0) + scores.get('embarrassment', 0)
        val_envy = scores.get('disapproval', 0) + scores.get('disgust', 0)

        # 3. Оси ХУ (Для совместимости с промптом Gemini)
        pos_x = val_gratitude * 0.5 + val_joy
        pos_y = val_interest * 0.5 + val_love

        neg_x = val_sadness * 0.5 + val_anger
        neg_y = val_shame * 0.5 + val_envy

        total_pos = pos_x + pos_y
        total_neg = neg_x + neg_y

        if total_pos > total_neg:
            return {
                "graph": "Positive",
                "dominant_emotion": max(scores, key=scores.get),
                "x_val": round(pos_x, 2),
                "y_val": round(pos_y, 2),
                "breakdown": [
                    {"label": "Joy", "value": round(val_joy, 2)},
                    {"label": "Gratitude", "value": round(val_gratitude, 2)},
                    {"label": "Interest", "value": round(val_interest, 2)},
                    {"label": "Love", "value": round(val_love, 2)}
                ]
            }
        else:
            return {
                "graph": "Negative",
                "dominant_emotion": max(scores, key=scores.get),
                "x_val": round(neg_x, 2),
                "y_val": round(neg_y, 2),
                "breakdown": [
                    {"label": "Anger", "value": round(val_anger, 2)},
                    {"label": "Sadness", "value": round(val_sadness, 2)},
                    {"label": "Shame", "value": round(val_shame, 2)},
                    {"label": "Disapproval", "value": round(val_envy, 2)}
                ]
            }
