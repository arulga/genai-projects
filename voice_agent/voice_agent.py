import asyncio
import logging
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import openai, silero

# Load environment variables from .env.local or .env
load_dotenv(".env.local")
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceAssistant(Agent):
    """
    Voice AI Assistant powered by OpenAI
    """
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful voice assistant. Your interface with users is voice. "
                "You support both Tamil and English languages. "
                "If the user speaks Tamil, reply in Tamil. If English, reply in English. "
                "Keep your responses extemely concise and immediate. "
                "Avoid using special characters or formatting that don't translate well to speech."
            ),
        )


# Create the agent server
server = AgentServer()


@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    """
    Main entry point for the voice agent.
    This function is called when a participant joins a LiveKit room.
    """
    logger.info(f"Room connected: {ctx.room.name}")
    
    # Create an agent session with STT-LLM-TTS pipeline
    session = AgentSession(
        # Speech-to-Text: Using OpenAI Whisper
        stt=openai.STT(
            model="whisper-1",
        ),
        
        # Large Language Model: Using OpenAI GPT
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),
        
        # Text-to-Speech: Using OpenAI TTS
        tts=openai.TTS(
            model="tts-1",
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            speed=1.0
        ),
        
        # Voice Activity Detection: Using Silero with faster settings
        vad=silero.VAD.load(
            min_silence_duration=0.5,
        ),
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=VoiceAssistant(),
    )
    
    # Greet the user
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )
    
    logger.info("Voice agent started successfully")


if __name__ == "__main__":
    # Run the agent server
    agents.cli.run_app(server)