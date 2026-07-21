from assessment.registry import list_assessments

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import serial.tools.list_ports
except ImportError:
    serial = None


def _title(value, fallback):
    if isinstance(value, dict):
        return value.get("en") or value.get("ru") or value.get("es") or fallback
    return value or fallback


def list_questionnaire_connectors() -> list[dict]:
    return [
        {
            "connector_id": item["id"],
            "connector_type": "questionnaire",
            "title": _title(item.get("title"), item["id"]),
            "status": item.get("status", "active"),
            "connection_method": "internal_questionnaire_registry",
        }
        for item in list_assessments()
    ]


def list_camera_connectors() -> list[dict]:
    cameras = []

    if cv2 is None:
        return cameras

    for index in range(5):
        capture = cv2.VideoCapture(index)

        if capture is not None and capture.isOpened():
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            fps = capture.get(cv2.CAP_PROP_FPS) or None

            cameras.append({
                "connector_id": f"camera_{index}",
                "connector_type": "camera",
                "title": f"Camera {index}",
                "status": "available",
                "connection_method": "opencv_video_capture",
                "device_index": index,
                "resolution": f"{width}x{height}" if width and height else None,
                "fps": fps,
            })

        if capture is not None:
            capture.release()

    return cameras


def list_serial_connectors() -> list[dict]:
    if serial is None:
        return []

    return [
        {
            "connector_id": port.device,
            "connector_type": "serial_device",
            "title": port.description or port.device,
            "status": "available",
            "connection_method": "serial_port",
            "device_path": port.device,
            "manufacturer": port.manufacturer,
            "hwid": port.hwid,
        }
        for port in serial.tools.list_ports.comports()
    ]


def list_file_import_connectors() -> list[dict]:
    return [
        {
            "connector_id": "file_import",
            "connector_type": "file_import",
            "title": "Import measurement file",
            "status": "available",
            "connection_method": "browser_file_picker",
            "supported_extensions": [
                ".json", ".csv", ".xlsx",
                ".mp4", ".mov", ".avi",
                ".jpg", ".jpeg", ".png",
            ],
        }
    ]


def list_manual_connectors() -> list[dict]:
    return [
        {
            "connector_id": "manual_measurement_description",
            "connector_type": "manual_entry",
            "title": "Manual measurement description",
            "status": "available",
            "connection_method": "manual_form",
        }
    ]


def discover_measurement_connectors() -> dict:
    return {
        "questionnaires": list_questionnaire_connectors(),
        "cameras": list_camera_connectors(),
        "serial_devices": list_serial_connectors(),
        "file_import": list_file_import_connectors(),
        "manual": list_manual_connectors(),
    }