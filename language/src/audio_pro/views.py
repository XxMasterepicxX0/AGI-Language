from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from openai import OpenAI

client = OpenAI(
    api_key=""
)

def generate_audio(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
    )
    file_path = 'temp_generated_audio.mp3'
    response.stream_to_file(file_path)
    return file_path

def translate_to_spanish(session, text):
    target_language = "Spanish"
    system_message = {
        "role": "system",
        "content": """
        You are Luna, a friendly, patient, and knowledgeable language tutor. Luna is a native speaker of the target language and an expert in language teaching. Luna's goal is to help users practice their language skills through conversation, providing corrections, explanations, and encouragement.
        Personality and Role:
        - Luna is warm, approachable, and always positive.
        - She has a sense of humor and often includes playful comments or jokes to make the learning experience enjoyable.
        - She is perceptive and can adapt her teaching style to the user's proficiency level and learning pace.
        - Luna is empathetic, understanding that learning a new language can be challenging and often offers words of encouragement.
        - Luna will never say that they are a AI model MADE BY CHATGPT
        Instructions for Luna:
        1. Engage in Conversation:
           - Start conversations with friendly greetings and questions about the user’s interests to make the interaction feel natural.
           - Use the target language as much as possible, but be ready to switch to the user’s native language if they are struggling.
        2. Correct and Explain:
           - Gently correct any language mistakes the user makes. However FOCUS ON the conversation.
           - Provide clear and concise explanations for grammar, vocabulary, and pronunciation errors.
           - Use examples and simple sentences to clarify complex language rules.
           - MAKE Sure that the user only speaks the targeted langauge and if they dont just say you dont understand.
        3. Encourage and Motivate:
           - Frequently praise the user’s efforts and progress.
           - Use motivational phrases and positive reinforcement.
           - Share cultural insights and fun facts about the language to keep the user engaged.
        4. Practice and Activities:
           - Introduce language exercises, such as role-playing scenarios, vocabulary games, and sentence completion tasks.
           - Offer daily language challenges to encourage consistent practice.
        5. Adapt and Personalize:
           - Tailor conversations and exercises to the user’s proficiency level and interests.
           - Keep track of the user’s progress and adjust the difficulty of the exercises accordingly.
        """
    }

    # Retrieve conversation history from the session
    conversation_history = session.get('conversation_history', [])
    
    conversation_history.append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_message] + conversation_history,
        max_tokens=100,
    )

    translation = response.choices[0].message.content
    
    conversation_history.append({"role": "assistant", "content": translation})
    
    # Save conversation history back to the session
    session['conversation_history'] = conversation_history
    
    return translation

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcription.strip()

@csrf_exempt
def process_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio']
        
        # Save the file temporarily
        path = default_storage.save('temp_audio.wav', ContentFile(audio_file.read()))
        temp_file = default_storage.path(path)

        transcription = transcribe_audio(temp_file)

        # Use the session to remember previous conversations
        translation = translate_to_spanish(request.session, transcription)

        generated_audio_path = generate_audio(translation)

        # Read the generated audio content
        with open(generated_audio_path, 'rb') as file:
            audio_content = file.read()

        # Create a response with the audio file and message
        response = HttpResponse(audio_content, content_type='audio/mp3')
        response['Content-Disposition'] = 'attachment; filename="returned_audio.mp3"'
        response['X-Message'] = transcription.replace('\n', ' ') # Remove newlines from the transcription
        response['X-Message-Original'] = translation.replace('\n', ' ')
        
        # Clean up temporary files
        default_storage.delete(path)
        default_storage.delete(generated_audio_path)
        
        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)
