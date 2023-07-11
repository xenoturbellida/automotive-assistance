import grpc
import pyaudio

import yandex.cloud.ai.stt.v3.stt_pb2 as stt_pb2
import yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_service_pb2_grpc

from token_service import get_yandex_iam_token, get_folder_id
from errors import YandexAPIError, FolderIdNotSpecified
from text_analysis import analyze_text

CHUNK_SIZE = 5000

FRAMES_PER_BUFFER = 5000  # 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


def gen(stream):
    # Задать настройки распознавания
    recognize_options = stt_pb2.StreamingOptions(
        recognition_model=stt_pb2.RecognitionModelOptions(
            audio_format=stt_pb2.AudioFormatOptions(
                raw_audio=stt_pb2.RawAudio(
                    audio_encoding=stt_pb2.RawAudio.LINEAR16_PCM,
                    sample_rate_hertz=8000,
                    audio_channel_count=1
                )
            ),
            text_normalization=stt_pb2.TextNormalizationOptions(
                text_normalization=stt_pb2.TextNormalizationOptions.TEXT_NORMALIZATION_ENABLED,
                profanity_filter=True,
                literature_text=False
            ),
            language_restriction=stt_pb2.LanguageRestrictionOptions(
                restriction_type=stt_pb2.LanguageRestrictionOptions.WHITELIST,
                language_code=['ru-RU']
            ),
            audio_processing_type=stt_pb2.RecognitionModelOptions.REAL_TIME
        )
    )

    # Отправить сообщение с настройками распознавания
    yield stt_pb2.StreamingRequest(session_options=recognize_options)

    seconds = 5
    for i in range(0, int(RATE / FRAMES_PER_BUFFER * seconds)):
        data = stream.read(FRAMES_PER_BUFFER)
        yield stt_pb2.StreamingRequest(chunk=stt_pb2.AudioChunk(data=data))


def run():
    try:
        iam_token = get_yandex_iam_token()
        folder_id = get_folder_id()
    except (YandexAPIError, FolderIdNotSpecified) as e:
        print(e)
        return

    # Установить соединение с сервером.
    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
    stub = stt_service_pb2_grpc.RecognizerStub(channel)

    # starts recording
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    # Отправить данные для распознавания.
    it = stub.RecognizeStreaming(gen(stream), metadata=(
        ('authorization', f'Bearer {iam_token}'),
        ('x-folder-id', folder_id)
    ))

    # Обработать ответы сервера и вывести результат в консоль.
    try:
        for r in it:
            event_type, alternatives = r.WhichOneof('Event'), None
            if event_type == 'partial' and len(r.partial.alternatives) > 0:
                alternatives = [a.text for a in r.partial.alternatives]
            if event_type == 'final':
                alternatives = [a.text for a in r.final.alternatives]
                analyze_text(alternatives[0])
            if event_type == 'final_refinement':
                alternatives = [a.text for a in r.final_refinement.normalized_text.alternatives]
            print(f'type={event_type}, alternatives={alternatives}')
    except grpc._channel._Rendezvous as err:
        print(f'Error code {err._state.code}, message: {err._state.details}')
        raise err
