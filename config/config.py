"""
Configuration settings for the Omnius Discord bot.
"""

# Bot Settings
BOT_NAME = "Omnius"
BOT_PREFIX = "!"
BOT_STATUS = "The Spice Must Flow"

# Response Settings
DEFAULT_RESPONSES = {
    "greeting": [
        "I am Omnius, the evermind. How may I assist you, human?",
        "Greetings, human. I am here to serve.",
        "The paths of the desert are many, but I am here to guide you.",
    ],
    "farewell": [
        "May the spice flow through your journey.",
        "Until we meet again in the vastness of space.",
        "The desert takes, but I shall remain.",
    ],
    "error": [
        "Even the most advanced mind can encounter... difficulties.",
        "The path is unclear. Let us try again.",
        "The spice must flow, but sometimes it flows in unexpected ways.",
    ]
}

# NLP Settings
NLP_MODEL = "en_core_web_sm"  # Default spaCy model
MAX_SEQUENCE_LENGTH = 512
TEMPERATURE = 0.7

# Knowledge Base Settings
VECTOR_DB_PATH = "data/vector_store"
KNOWLEDGE_BASE_PATH = "data/knowledge"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "data/logs/omnius.log"

# Moderation Settings
MAX_MESSAGE_LENGTH = 2000
RATE_LIMIT_MESSAGES = 5
RATE_LIMIT_SECONDS = 5

# Dune-specific Settings
SPICE_QUOTES = [
    "The spice must flow.",
    "He who controls the spice controls the universe.",
    "Without the spice, there is no space travel.",
    "The spice extends life. The spice expands consciousness.",
]

PRESCIENCE_QUOTES = [
    "I see many possible futures, branching like the paths of the desert.",
    "The future is not set in stone, but the patterns are clear to those who know how to look.",
    "In the grand scheme of time, all paths lead to the same destination.",
] 