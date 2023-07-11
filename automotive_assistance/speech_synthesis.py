import io
import grpc
import pydub

import yandex.cloud.ai.tts.v3.tts_pb2 as tts_pb2
import yandex.cloud.ai.tts.v3.tts_service_pb2_grpc as tts_service_pb2_grpc

from token_service import get_yandex_iam_token, get_folder_id
from errors import YandexAPIError, FolderIdNotSpecified


# Определить параметры запроса.
def synthesize(text) -> pydub.AudioSegment or None:
    try:
        iam_token = get_yandex_iam_token()
        folder_id = get_folder_id()
    except (YandexAPIError, FolderIdNotSpecified) as e:
        print(e)
        return

    request = tts_pb2.UtteranceSynthesisRequest(
        text=text,
        output_audio_spec=tts_pb2.AudioFormatOptions(
            container_audio=tts_pb2.ContainerAudio(
                container_audio_type=tts_pb2.ContainerAudio.WAV
            )
        ),
        loudness_normalization_type=tts_pb2.UtteranceSynthesisRequest.LUFS
    )

    # Установить соединение с сервером.
    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('tts.api.cloud.yandex.net:443', cred)
    stub = tts_service_pb2_grpc.SynthesizerStub(channel)

    # Отправить данные для синтеза.
    it = stub.UtteranceSynthesis(request, metadata=(
        ('authorization', f'Bearer {iam_token}'),
        ('x-folder-id', folder_id)
    ))

    # Собрать аудиозапись по чанкам.
    try:
        audio = io.BytesIO()
        for response in it:
            audio.write(response.audio_chunk.data)
        audio.seek(0)
        return pydub.AudioSegment.from_wav(audio)
    except grpc._channel._Rendezvous as err:
        print(f'Error code {err._state.code}, message: {err._state.details}')
        raise err


if __name__ == '__main__':
    text_ = 'Я Яндекс Спичк+ит. Я могу превратить любой текст в речь. Теперь и в+ы — можете!'
    audio = synthesize(text_)
    with open('speech.wav', 'wb') as fp:
        audio.export(fp, format='wav')
