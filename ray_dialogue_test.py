import json
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


def post_json(path: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    lang = input("Выберите язык / Choose language / Elige idioma (ru/en/es): ").strip()

    if lang not in {"ru", "en", "es"}:
        lang = "ru"

    start = post_json(
        "/ray/start",
        {
            "participant_id": "dialogue_terminal_test",
            "lang": lang,
        },
    )

    session_id = start["session_id"]

    print("\nРэй:")
    print(start["ray"]["message"])

    while True:
        user_message = input("\nВы: ").strip()

        if user_message.lower() in {"exit", "quit", "stop", "выход"}:
            print("\nРэй:")
            print("Остановились. Сессию можно продолжить позже.")
            break

        response = post_json(
            f"/ray/chat/{session_id}",
            {
                "message": user_message,
                "lang": lang,
            },
        )

        ray = response["ray"]

        print("\nРэй:")
        print(ray["message"])

        if ray.get("status") == "complete":
            break


if __name__ == "__main__":
    main()