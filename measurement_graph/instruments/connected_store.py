import json
from pathlib import Path
from datetime import datetime, timezone


CONNECTED_INSTRUMENTS_PATH = Path(
    "data/connected_measurement_instruments.json"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_connected_instruments() -> list[dict]:
    if not CONNECTED_INSTRUMENTS_PATH.exists():
        return []

    raw = CONNECTED_INSTRUMENTS_PATH.read_text(
        encoding="utf-8"
    ).strip()

    if not raw:
        return []

    return json.loads(raw)


def save_connected_instruments(
    instruments: list[dict],
) -> None:
    CONNECTED_INSTRUMENTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CONNECTED_INSTRUMENTS_PATH.write_text(
        json.dumps(
            instruments,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def connect_instrument(
    *,
    instrument_id: str,
    connector: dict,
    measurement_type: str,
    study_id: str,
    context: dict | None = None,
) -> dict:
    instruments = load_connected_instruments()

    instruments = [
        item for item in instruments
        if item.get("instrument_id") != instrument_id
    ]

    instrument = {
        "instrument_id": instrument_id,
        "status": "connected",
        "connector": connector,
        "measurement_type": measurement_type,
        "study_id": study_id,
        "context": context or {},
        "connected_at": utc_now(),
        "disconnected_at": None,
    }

    instruments.append(instrument)
    save_connected_instruments(instruments)

    return instrument


def disconnect_instrument(
    instrument_id: str,
) -> dict:
    instruments = load_connected_instruments()

    found = None
    updated = []

    for item in instruments:
        if item.get("instrument_id") == instrument_id:
            found = {
                **item,
                "status": "disconnected",
                "disconnected_at": utc_now(),
            }
        else:
            updated.append(item)

    if found is None:
        raise ValueError(
            f"Instrument is not connected: {instrument_id}"
        )

    save_connected_instruments(updated)

    return found


def find_connected_instrument_by_connector(
    *,
    connector_id: str,
    connector_type: str,
) -> dict | None:
    for instrument in load_connected_instruments():
        connector = instrument.get("connector", {})

        if (
            connector.get("connector_id") == connector_id
            and connector.get("connector_type") == connector_type
            and instrument.get("status") == "connected"
        ):
            return instrument

    return None