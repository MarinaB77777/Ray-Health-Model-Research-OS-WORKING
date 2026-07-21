from measurement_graph.instruments.connected_store import (
    connect_instrument,
    disconnect_instrument,
    load_connected_instruments,
    find_connected_instrument_by_connector,
)


def list_connected_instruments() -> list[dict]:
    return load_connected_instruments()


def is_connector_connected(
    *,
    connector_id: str,
    connector_type: str,
) -> bool:
    return find_connected_instrument_by_connector(
        connector_id=connector_id,
        connector_type=connector_type,
    ) is not None