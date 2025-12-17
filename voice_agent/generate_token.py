#!/usr/bin/env python3
"""
Generate a LiveKit access token for testing the voice agent.
Usage: python generate_token.py [room_name] [participant_name]
"""
import sys
import os
from dotenv import load_dotenv
from livekit import api

# Load environment variables
load_dotenv(".env.local")
load_dotenv()


def generate_token(room_name: str = "voice-room", participant_name: str = "test-user") -> str:
    """
    Generate a LiveKit access token for a participant to join a room.
    
    Args:
        room_name: The name of the room to join
        participant_name: The identity of the participant
        
    Returns:
        The generated JWT token
    """
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env.local or environment variables"
        )
    
    # Create an access token
    token = api.AccessToken(api_key, api_secret) \
        .with_identity(participant_name) \
        .with_name(participant_name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))
    
    return token.to_jwt()


if __name__ == "__main__":
    # Parse command line arguments
    room = sys.argv[1] if len(sys.argv) > 1 else "voice-room"
    participant = sys.argv[2] if len(sys.argv) > 2 else "test-user"
    
    try:
        token = generate_token(room, participant)
        print(f"\n🎫 Generated LiveKit Access Token:")
        print(f"   Room: {room}")
        print(f"   Participant: {participant}")
        print(f"\n{token}\n")
        print("Copy this token and use it in your client application.")
    except Exception as e:
        print(f"❌ Error generating token: {e}", file=sys.stderr)
        sys.exit(1)
