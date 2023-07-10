import requests
import json
import os

from errors import YandexAPIError, FolderIdNotSpecified

GET_IAM_TOKEN_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"


def get_yandex_iam_token():
    # specify yandex OAuth-token through command prompt as $Env:OAUTH_TOKEN = "<token value>" - for Windows 11
    oauth_token = os.environ.get('OAUTH_TOKEN')

    response = requests.post(
        url=GET_IAM_TOKEN_URL,
        data=json.dumps({"yandexPassportOauthToken": oauth_token})
    )

    if response.status_code == 200:
        return response.json().get('iamToken')
    else:
        raise YandexAPIError("Yandex API error while getting iam-token")


def get_folder_id():
    # specify yandex folder through command prompt as $Env:FOLDER_ID = "<folder id>" - for Windows 11
    folder_id = os.environ.get("FOLDER_ID")
    if folder_id:
        return folder_id
    else:
        raise FolderIdNotSpecified
