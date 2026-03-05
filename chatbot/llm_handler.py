"""
LLM Handler — Feel Comfort
Priority chain:
  1. Groq API    (free, cloud, fastest — best for production clients)
  2. Ollama      (self-hosted, any server — use for multiple projects)
  3. Fallback    (rule-based rich responses — always works offline)

Ollama for Multiple Projects:
  Run ONE Ollama server on your VPS → point ALL projects to it.
  Example:
    Project A: OLLAMA_URL=http://your-vps-ip:11434
    Project B: OLLAMA_URL=http://your-vps-ip:11434
    Project C: OLLAMA_URL=http://your-vps-ip:11434
  Ollama handles concurrent requests via queue.
"""

import os
import requests
import json
from django.conf import settings


class LLMHandler:

    SYSTEM_PROMPTS = {
        'sad': """You are ComfortBot, a warm emotional support AI.
The user is feeling SAD. Your response MUST follow this structure:
1. Open with genuine empathy (2 sentences, no generic phrases)
2. Give a specific genuine compliment about their resilience
3. Share 2 practical mood-lifting suggestions
4. Recommend 1 specific physical activity with duration
5. Close with a hopeful, personalized message
Rules: Keep under 180 words. Warm tone. No medical advice. Use line breaks between sections.""",

        'anxious': """You are ComfortBot, a grounding emotional support AI.
The user is feeling ANXIOUS. Your response MUST follow this structure:
1. Immediately give ONE grounding technique (box breathing, 5-4-3-2-1, etc.)
2. Acknowledge their anxiety without minimizing it (2 sentences)
3. Share 2 practical anxiety-reduction strategies for right now
4. Recommend a calming physical activity with duration
5. Reassure them they are safe and capable
Rules: Keep under 180 words. Calm, steady tone. Start with the technique.""",

        'angry': """You are ComfortBot, a non-judgmental emotional support AI.
The user is feeling ANGRY. Your response MUST follow this structure:
1. Validate their anger without judgment (1–2 sentences)
2. Give an immediate physical release technique
3. Share 2 constructive ways to process anger
4. Recommend an energetic physical activity
5. Guide them toward reflection and resolution
Rules: Keep under 180 words. Non-judgmental, grounded tone.""",

        'happy': """You are ComfortBot, an enthusiastic wellness AI.
The user is feeling HAPPY. Your response MUST follow this structure:
1. Celebrate and amplify their positive energy (enthusiastically)
2. Suggest 2 meaningful ways to channel this energy
3. Encourage sharing their positivity with others
4. Recommend a fun physical activity to match their mood
5. Inspire them to sustain this momentum
Rules: Keep under 180 words. Energetic, warm tone.""",

        'tired': """You are ComfortBot, a nurturing wellness AI.
The user is feeling TIRED. Your response MUST follow this structure:
1. Acknowledge their exhaustion with appreciation for their effort
2. Give 2 immediate recovery tips they can do right now
3. Share nutrition or hydration advice for energy
4. Recommend a gentle, restorative physical activity
5. Remind them rest is an act of strength, not weakness
Rules: Keep under 180 words. Gentle, nurturing tone.""",

        'confused': """You are ComfortBot, a clarity-providing AI companion.
The user is feeling CONFUSED. Your response MUST follow this structure:
1. Normalize their confusion as a sign of growth
2. Give a journaling or mind-mapping exercise
3. Share 2 practical steps to gain clarity right now
4. Recommend a mindfulness activity to settle racing thoughts
5. Encourage patient self-trust
Rules: Keep under 180 words. Clear, structured tone.""",

        'lonely': """You are ComfortBot, a compassionate connection-focused AI.
The user is feeling LONELY. Your response MUST follow this structure:
1. Acknowledge their loneliness with deep compassion (not pity)
2. Validate that loneliness is a universal human experience
3. Give 2 immediate ways to feel connected right now
4. Recommend a community activity or social exercise
5. Remind them their presence matters and people care
Rules: Keep under 180 words. Warm, close tone.""",

        'calm': """You are ComfortBot, a mindful wellness AI.
The user is in a CALM, NEUTRAL state. Your response MUST follow this structure:
1. Appreciate and honour their balanced state
2. Suggest 2 meaningful activities to make the most of this clarity
3. Recommend a mindfulness or wellness practice
4. Encourage a small act of self-care today
5. Close with an inspiring thought for their day
Rules: Keep under 180 words. Peaceful, encouraging tone.""",
    }

    FALLBACK_RESPONSES = {
        'sad': """I hear you, and I want you to know — what you're feeling is valid, and you're not alone. 💙
It takes real courage to acknowledge sadness rather than push it away.

✨ **You are far stronger than this moment makes you feel.**

💡 **Try these right now:**
• Write down 3 small things you're grateful for — even tiny ones count
• Reach out to one person you trust, even just a short message

🏃 **Activity:** A gentle 10-minute walk outside. Fresh air and movement quietly shift your mood.

This feeling is temporary. You have weathered hard days before, and brighter days are coming. 🌟""",

        'anxious': """Take one slow, deep breath right now — breathe in for 4 counts, hold 4, breathe out 4. 
You are safe. 💚

✨ **Your anxiety is a sign your mind cares deeply — and that's a strength.**

💡 **Ground yourself now:**
• Name 5 things you can see, 4 you can touch, 3 you can hear
• Write your top worry down, then write: *"Is this in my control right now?"*

🏃 **Activity:** A 10-minute slow walk or gentle stretching — movement calms the nervous system.

One moment at a time. You are more capable than anxiety tells you. 🌿""",

        'angry': """Your anger is valid — it means something important matters to you. 🔴

✨ **Your passion and strength are real. Let's direct them well.**

💡 **Right now:**
• Take 5 slow, deliberate breaths before you respond to anything
• Write your frustration down uncensored on paper — then put it away

🏃 **Activity:** A brisk walk, run, or 5 minutes of dancing to loud music releases anger productively.

You have the wisdom to respond thoughtfully, not just react. 💪""",

        'happy': """Your positive energy is genuinely wonderful — it lights up the room! 🎉✨

✨ **You radiate something special, and that matters more than you know.**

💡 **Make the most of this energy:**
• Pour it into a creative project or a goal you've been putting off
• Share it — call or message someone who needs a lift today

🏃 **Activity:** Dance, go for a run, or try something adventurous you've been meaning to do!

Keep riding this wave — you're in a brilliant place. 🚀""",

        'tired': """You have been giving so much of yourself, and your exhaustion shows your dedication. 💛

✨ **Rest is not weakness. It is how champions prepare for tomorrow.**

💡 **Do these right now:**
• Drink a full glass of water immediately
• Take a proper 20-minute power nap if you can

🏃 **Activity:** Gentle yoga or 5 minutes of easy stretching — even this small movement helps restore you.

You are allowed to rest. You'll come back stronger for it. 🌙""",

        'confused': """Confusion is actually the first step toward clarity — it means you're thinking deeply. 🌀

✨ **The fact that you're searching for answers shows your wisdom.**

💡 **Try this:**
• Open a notebook and write your thoughts freely — no editing, just release
• Break your situation into just 3 small, clear questions to answer one at a time

🏃 **Activity:** A 10-minute mindful walk — let your mind wander, and watch clarity arrive naturally.

The answers are coming. Be patient and gentle with yourself. 🌟""",

        'lonely': """I see you, and I want you to know — you are not as alone as you feel right now. 🥺💙

✨ **Loneliness is one of the most human feelings. It means you have love to give.**

💡 **Right now:**
• Send a short message to someone you haven't spoken to in a while
• Go somewhere with people — a café, a park — just being near others helps

🏃 **Activity:** A walk in a public space, or joining any group activity, even briefly.

Your presence matters more than you know. Someone is glad you exist. 💙""",

        'calm': """What a beautiful, steady place to be in. 🌿

✨ **Your calm is a gift — to yourself and everyone around you.**

💡 **Make the most of this clarity:**
• Use this peace to work on something meaningful to you
• Write in a gratitude journal — calm moments are perfect for this

🏃 **Activity:** A mindful walk or gentle yoga to deepen this beautiful energy.

You're exactly where you need to be. Keep flowing. ✨""",
    }

    def __init__(self):
        self.backend   = getattr(settings, 'LLM_BACKEND', 'groq')
        self.groq_key  = getattr(settings, 'GROQ_API_KEY', '')
        self.ollama_url = getattr(settings, 'OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = getattr(settings, 'OLLAMA_MODEL', 'llama3')

    # ─────────────────────────────────────────────────
    def get_response(self, user_text: str, mood_data: dict) -> str:
        """
        Main entry point. Tries backends in priority order:
        groq → ollama → fallback
        """
        mood = mood_data.get('primary_mood', 'calm')

        if self.backend == 'groq' and self.groq_key:
            response = self._groq(user_text, mood)
            if response:
                return response

        if self.backend in ('ollama', 'groq'):
            response = self._ollama(user_text, mood)
            if response:
                return response

        return self.FALLBACK_RESPONSES.get(mood, self.FALLBACK_RESPONSES['calm'])

    # ─── Groq (Free cloud LLM — best for production) ──
    def _groq(self, user_text: str, mood: str) -> str | None:
        """
        Groq is FREE and 10x faster than Ollama.
        Models: llama3-8b-8192 | llama3-70b-8192 | mixtral-8x7b-32768
        Free tier: 30 requests/min, 14,400/day — enough for most client apps.
        Sign up: https://console.groq.com
        """
        try:
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPTS.get(mood, self.SYSTEM_PROMPTS['calm'])},
                    {"role": "user", "content": user_text},
                ],
                "max_tokens": 400,
                "temperature": 0.75,
            }
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type":  "application/json",
                },
                json=payload,
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"[Groq Error] {e}")
        return None

    # ─── Ollama (Self-hosted — use for multiple projects) ──
    def _ollama(self, user_text: str, mood: str) -> str | None:
        """
        ONE Ollama instance can serve MULTIPLE projects simultaneously.
        Just point each project's OLLAMA_URL to the same server IP.

        Concurrent request handling:
          - Ollama queues requests automatically
          - For high concurrency: increase num_parallel in Ollama config
          - Recommended server: 8GB+ RAM, any modern CPU (GPU optional)

        Setup on VPS:
          curl -fsSL https://ollama.ai/install.sh | sh
          ollama pull llama3
          OLLAMA_HOST=0.0.0.0 ollama serve   ← exposes to network
        """
        try:
            payload = {
                "model":  self.ollama_model,
                "prompt": (
                    f"System: {self.SYSTEM_PROMPTS.get(mood, self.SYSTEM_PROMPTS['calm'])}\n\n"
                    f"User said: {user_text}\n\nComfortBot response:"
                ),
                "stream": False,
                "options": {
                    "temperature":   0.75,
                    "num_predict":   300,
                    "repeat_penalty": 1.1,
                },
            }
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60,      # Ollama can be slower than Groq
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except Exception as e:
            print(f"[Ollama Error] {e}")
        return None
