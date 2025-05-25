

import openai
from openai import OpenAI

client = OpenAI(api_key="")  # Your real key here

# Stores conversation history per video_id
conversation_context = {}

def chat_with_gpt(video_id, user_input, script=None):
    print(script)
    # If new conversation for this video, create with script
    if video_id not in conversation_context:
        if script is None:
            raise ValueError("Script must be provided for new video context.")
        conversation_context[video_id] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"This is the video script:\n{script}"}
        ]

    # Append user input to the history
    conversation_context[video_id].append({"role": "user", "content": user_input})
    print(conversation_context[video_id])
    # Send to GPT
    response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation_context[video_id]
    )

    reply = response.choices[0].message.content
    conversation_context[video_id].append({"role": "assistant", "content": reply})
    return reply        