"""
NLP Mood Analyzer — Feel Comfort
Techniques used:
  1. VADER Sentiment Analysis       (NLTK)
  2. TextBlob Polarity & Subjectivity
  3. Emotion keyword dictionary matching
  4. Composite scoring with intensity weighting
"""

import re
import nltk
from textblob import TextBlob

# Download NLTK data (safe to run multiple times)
for resource in ['vader_lexicon', 'punkt', 'stopwords']:
    try:
        nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else resource)
    except LookupError:
        nltk.download(resource, quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer


class MoodAnalyzer:
    """
    Multi-technique NLP mood detector.
    Returns mood label + intensity + full score breakdown.
    """

    MOOD_KEYWORDS = {
        'sad': [
            'sad', 'cry', 'crying', 'depressed', 'depression', 'unhappy',
            'miserable', 'heartbroken', 'lonely', 'hopeless', 'worthless',
            'empty', 'grief', 'sorrow', 'mourn', 'down', 'blue', 'gloomy',
            'tearful', 'devastated', 'broken', 'pain', 'hurt', 'ache',
        ],
        'anxious': [
            'anxious', 'anxiety', 'worried', 'worry', 'nervous', 'panic',
            'fear', 'scared', 'stressed', 'stress', 'overwhelmed', 'tension',
            'restless', 'uneasy', 'dread', 'terrified', 'phobia', 'paranoid',
            'overthinking', 'overthink', 'pressure', 'burden',
        ],
        'angry': [
            'angry', 'anger', 'furious', 'mad', 'frustrated', 'frustration',
            'irritated', 'rage', 'annoyed', 'hate', 'upset', 'bitter',
            'resentful', 'outraged', 'livid', 'disgusted', 'hostile',
        ],
        'happy': [
            'happy', 'happiness', 'joy', 'joyful', 'excited', 'great',
            'wonderful', 'amazing', 'love', 'fantastic', 'cheerful', 'glad',
            'thrilled', 'ecstatic', 'delighted', 'blessed', 'grateful',
            'content', 'satisfied', 'proud', 'positive', 'good',
        ],
        'tired': [
            'tired', 'exhausted', 'fatigue', 'sleepy', 'weary', 'drained',
            'burnout', 'worn out', 'no energy', 'lethargic', 'sluggish',
            'dull', 'bored', 'unmotivated', 'lazy', 'heavy',
        ],
        'confused': [
            'confused', 'confusion', 'lost', 'unclear', 'uncertain',
            'doubt', 'unsure', 'perplexed', 'puzzled', 'bewildered',
            'stuck', 'clueless', 'overwhelmed', 'scattered',
        ],
        'calm': [
            'calm', 'peaceful', 'relaxed', 'serene', 'content', 'balanced',
            'okay', 'fine', 'alright', 'neutral', 'stable', 'composed',
        ],
        'lonely': [
            'lonely', 'loneliness', 'alone', 'isolated', 'abandoned',
            'no one', 'nobody', 'left out', 'disconnected', 'empty',
        ],
    }

    MOOD_EMOJIS = {
        'sad':      '😢', 'anxious': '😰', 'angry':   '😡',
        'happy':    '😊', 'tired':   '😴', 'confused': '😕',
        'calm':     '😌', 'lonely':  '🥺',
    }

    ACTIVITY_SUGGESTIONS = {
        'sad': [
            '🚶 Take a slow 10-minute walk in fresh air',
            "📓 Write 3 things you're grateful for today",
            '🎵 Listen to your favourite uplifting playlist',
            '📞 Call someone who makes you feel safe',
        ],
        'anxious': [
            '🌬️ Try box breathing: 4 counts in → hold 4 → out 4',
            '🧘 Do a 5-minute body scan meditation',
            '📝 Write your worries then ask "is this in my control?"',
            '🌿 Grounding: name 5 things you can see, 4 touch, 3 hear',
        ],
        'angry': [
            '🏃 Go for a brisk walk or run to release tension',
            '✍️ Write your feelings freely on paper, then tear it up',
            '🥊 Try 2 minutes of shadow boxing or intense stretching',
            '🌬️ Take 5 slow deep breaths before responding to anything',
        ],
        'happy': [
            '🎨 Channel energy into a creative project',
            '📞 Share your positivity — call someone you love!',
            '🏋️ Try a new workout or physical challenge',
            '🌟 Write down what made you happy to remember it',
        ],
        'tired': [
            '💤 Take a proper 20-minute power nap',
            '💧 Drink a full glass of water right now',
            '🧘 Gentle yoga or simple stretching for 5 minutes',
            '🍎 Eat something nourishing — avoid sugar crash foods',
        ],
        'confused': [
            '📝 Mind-map your thoughts freely on paper',
            '🧘 10-minute meditation to settle scattered thinking',
            '🗣️ Talk it out with someone you trust',
            '🔢 Break the situation into 3 small, clear next steps',
        ],
        'calm': [
            '📚 Use this peace to learn something meaningful',
            '🙏 Practice gratitude journaling',
            '🌿 A mindful nature walk to deepen your calm',
            '🎯 Set one clear, achievable goal for today',
        ],
        'lonely': [
            '📞 Reach out to an old friend — even a text helps',
            '🐾 Spend time with a pet or plant',
            '☕ Go to a café or public space — be around people',
            '✍️ Write a letter to your future self',
        ],
    }

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def _clean(self, text: str) -> str:
        return re.sub(r'[^\w\s]', ' ', text.lower()).strip()

    def _keyword_scores(self, text: str) -> dict:
        cleaned = self._clean(text)
        scores = {mood: 0 for mood in self.MOOD_KEYWORDS}
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for kw in keywords:
                if kw in cleaned:
                    scores[mood] += 1
        return scores

    def analyze(self, text: str) -> dict:
        """
        Full mood analysis. Returns structured dict.

        Keys:
          primary_mood, intensity, sentiment,
          polarity, subjectivity, vader_compound,
          activities, emoji
        """
        if not text or not text.strip():
            return self._neutral_result()

        # 1. VADER
        vader   = self.vader.polarity_scores(text)
        compound = vader['compound']

        # 2. TextBlob
        blob        = TextBlob(text)
        polarity    = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # 3. Keywords
        kw_scores    = self._keyword_scores(text)
        kw_top_mood  = max(kw_scores, key=kw_scores.get)
        kw_top_score = kw_scores[kw_top_mood]

        # 4. Composite decision
        if kw_top_score >= 2:
            primary_mood = kw_top_mood
        elif kw_top_score == 1:
            # Keyword gives a hint; blend with VADER
            if compound >= 0.5:
                primary_mood = 'happy'
            elif compound <= -0.5:
                primary_mood = kw_top_mood      # trust keyword for negative
            else:
                primary_mood = kw_top_mood
        else:
            # No keywords — rely purely on VADER + TextBlob
            avg = (compound + polarity) / 2
            if avg >= 0.5:
                primary_mood = 'happy'
            elif avg >= 0.1:
                primary_mood = 'calm'
            elif avg >= -0.1:
                primary_mood = 'calm'
            elif avg >= -0.3:
                primary_mood = 'tired'
            elif avg >= -0.5:
                primary_mood = 'anxious'
            else:
                primary_mood = 'sad'

        # 5. Intensity
        abs_c = abs(compound)
        if abs_c >= 0.7:
            intensity = 'high'
        elif abs_c >= 0.35:
            intensity = 'medium'
        else:
            intensity = 'low'

        # 6. Sentiment label
        if compound > 0.05:
            sentiment = 'positive'
        elif compound < -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'primary_mood':  primary_mood,
            'intensity':     intensity,
            'sentiment':     sentiment,
            'polarity':      round(polarity, 4),
            'subjectivity':  round(subjectivity, 4),
            'vader_compound': round(compound, 4),
            'emoji':         self.MOOD_EMOJIS.get(primary_mood, '💭'),
            'activities':    self.ACTIVITY_SUGGESTIONS.get(primary_mood, []),
            'keyword_hits':  kw_top_score,
        }

    def _neutral_result(self) -> dict:
        return {
            'primary_mood': 'calm', 'intensity': 'low',
            'sentiment': 'neutral', 'polarity': 0.0,
            'subjectivity': 0.0, 'vader_compound': 0.0,
            'emoji': '😌', 'activities': self.ACTIVITY_SUGGESTIONS['calm'],
            'keyword_hits': 0,
        }
