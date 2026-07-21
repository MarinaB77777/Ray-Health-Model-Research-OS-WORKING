from __future__ import annotations

import hashlib
import json
import os
import platform
import secrets
import shutil
import subprocess
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from research.storage_paths import application_data_directory


FIJI_INTEGRATION_SCHEMA_VERSION = "health-model-fiji-integration-1"
FIJI_PIPELINE_SCHEMA_VERSION = "health-model-image-pipeline-1"
FIJI_RUN_SCHEMA_VERSION = "health-model-image-processing-run-1"
BRIDGE_SCRIPT_NAME = "Health_Model_Research_OS_Bridge_.groovy"
SUPPORTED_LANGUAGES = frozenset({"ru", "en", "es"})


class FijiIntegrationError(Exception):
    def __init__(self, code: str, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _root() -> Path:
    root = application_data_directory() / "fiji_integration"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _json_load(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def _json_save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _candidate_launchers() -> list[Path]:
    system = platform.system()
    home = Path.home()
    candidates: list[Path] = []
    if system == "Darwin":
        for root in (Path("/Applications/Fiji.app"), home / "Applications/Fiji.app"):
            candidates.extend((root / "Contents/MacOS/ImageJ-macosx", root / "ImageJ-macosx"))
    elif system == "Windows":
        roots = [
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Fiji.app",
            Path(os.environ.get("LOCALAPPDATA", str(home / "AppData/Local"))) / "Fiji.app",
            home / "Fiji.app",
        ]
        for root in roots:
            candidates.extend((root / "ImageJ-win64.exe", root / "ImageJ-win32.exe"))
    else:
        for root in (Path("/opt/Fiji.app"), Path("/usr/local/Fiji.app"), home / "Fiji.app"):
            candidates.extend((root / "ImageJ-linux64", root / "ImageJ-linux32", root / "fiji"))
    for name in ("fiji", "ImageJ-linux64", "ImageJ-macosx", "ImageJ-win64.exe"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.expanduser())
        if key not in seen:
            seen.add(key)
            unique.append(candidate.expanduser())
    return unique


def _fiji_root_from_launcher(launcher: Path) -> Path:
    resolved = launcher.expanduser().resolve()
    if resolved.parent.name == "MacOS" and resolved.parent.parent.name == "Contents":
        return resolved.parent.parent.parent
    return resolved.parent


def inspect_installation(path: str | Path) -> dict[str, Any]:
    raw = Path(path).expanduser()
    if raw.is_dir():
        possible = [
            raw / "Contents/MacOS/ImageJ-macosx",
            raw / "ImageJ-macosx",
            raw / "ImageJ-linux64",
            raw / "ImageJ-linux32",
            raw / "ImageJ-win64.exe",
            raw / "ImageJ-win32.exe",
            raw / "fiji",
        ]
        launcher = next((item for item in possible if item.is_file()), None)
    else:
        launcher = raw if raw.is_file() else None
    if launcher is None:
        raise FijiIntegrationError("FIJI_LAUNCHER_NOT_FOUND", 404)
    if launcher.name not in {
        "ImageJ-macosx", "ImageJ-linux64", "ImageJ-linux32",
        "ImageJ-win64.exe", "ImageJ-win32.exe", "fiji",
    }:
        raise FijiIntegrationError("FIJI_LAUNCHER_NAME_UNRECOGNIZED")
    root = _fiji_root_from_launcher(launcher)
    jars = root / "jars"
    plugins = root / "plugins"
    scripts = root / "scripts"
    markers = {
        "jars_directory": jars.is_dir(),
        "plugins_directory": plugins.is_dir(),
        "scripts_directory": scripts.is_dir(),
        "imagej_common_present": bool(list(jars.glob("imagej-common-*.jar"))) if jars.is_dir() else False,
        "scijava_common_present": bool(list(jars.glob("scijava-common-*.jar"))) if jars.is_dir() else False,
    }
    valid = markers["jars_directory"] and (
        markers["imagej_common_present"] or markers["scijava_common_present"]
    )
    return {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "valid": valid,
        "launcher_path": str(launcher.resolve()),
        "installation_root": str(root.resolve()),
        "platform": platform.system(),
        "launcher_sha256": _sha256(launcher),
        "launcher_modified_at": datetime.fromtimestamp(launcher.stat().st_mtime, UTC).isoformat(),
        "markers": markers,
        "bridge_installed": (scripts / "Plugins" / BRIDGE_SCRIPT_NAME).is_file(),
    }


def discover_installations() -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    for candidate in _candidate_launchers():
        try:
            item = inspect_installation(candidate)
        except FijiIntegrationError:
            continue
        if item["valid"] and not any(x["launcher_path"] == item["launcher_path"] for x in found):
            found.append(item)
    configured = _json_load(_root() / "configuration.json", {})
    return {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "detected": found,
        "configured_launcher": configured.get("launcher_path"),
        "detected_at": _now(),
    }


def configure_installation(path: str) -> dict[str, Any]:
    installation = inspect_installation(path)
    if not installation["valid"]:
        raise FijiIntegrationError("FIJI_INSTALLATION_MARKERS_MISSING")
    configuration = {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "launcher_path": installation["launcher_path"],
        "installation_root": installation["installation_root"],
        "configured_at": _now(),
    }
    _json_save(_root() / "configuration.json", configuration)
    return {**installation, "configured": True}


def configured_installation() -> dict[str, Any]:
    configuration = _json_load(_root() / "configuration.json", {})
    launcher = configuration.get("launcher_path")
    if not launcher:
        raise FijiIntegrationError("FIJI_INSTALLATION_NOT_CONFIGURED", 409)
    return inspect_installation(launcher)


def launch_fiji() -> dict[str, Any]:
    installation = configured_installation()
    process = subprocess.Popen(  # noqa: S603 - executable was validated as a Fiji launcher
        [installation["launcher_path"]],
        cwd=installation["installation_root"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "status": "started",
        "process_id": process.pid,
        "started_at": _now(),
        "launcher_sha256": installation["launcher_sha256"],
    }


def _bridge_script(callback_url: str, token: str) -> str:
    callback = json.dumps(callback_url)
    secret = json.dumps(token)
    return f'''#@script(language="Groovy", menuPath="Plugins>Health Model Research OS>Connect Ray bridge", headless=false)
import groovy.json.JsonOutput
import ij.CommandListener
import ij.Executer
import ij.IJ
import ij.ImageListener
import ij.ImagePlus
import ij.WindowManager

final String callbackUrl = {callback}
final String bridgeToken = {secret}

def sendEvent = {{ Map event ->
    try {{
        event.schema_version = "health-model-fiji-bridge-event-1"
        event.occurred_at = java.time.Instant.now().toString()
        def connection = new URL(callbackUrl).openConnection()
        connection.setRequestMethod("POST")
        connection.setRequestProperty("Content-Type", "application/json; charset=utf-8")
        connection.setRequestProperty("Authorization", "Bearer " + bridgeToken)
        connection.setDoOutput(true)
        connection.outputStream.withWriter("UTF-8") {{ it << JsonOutput.toJson(event) }}
        int status = connection.responseCode
        if (status < 200 || status >= 300) IJ.log("Health Model bridge HTTP " + status)
        connection.disconnect()
    }} catch (Exception error) {{
        IJ.log("Health Model bridge error: " + error.getMessage())
    }}
}}

def imageSnapshot = {{ ImagePlus image ->
    if (image == null) return [image_present:false]
    return [image_present:true, image_id:image.getID(), title:image.getTitle(), width:image.getWidth(),
            height:image.getHeight(), channels:image.getNChannels(), slices:image.getNSlices(),
            frames:image.getNFrames(), bit_depth:image.getBitDepth()]
}}

class HMCommandListener implements CommandListener {{
    Closure sender; Closure snapshot
    String commandExecuting(String command) {{ sender([event_type:"command_started", command:command, image:snapshot(WindowManager.getCurrentImage())]); return command }}
}}
class HMImageListener implements ImageListener {{
    Closure sender; Closure snapshot; long lastUpdateAt = 0L
    void imageOpened(ImagePlus image) {{ sender([event_type:"image_opened", image:snapshot(image)]) }}
    void imageClosed(ImagePlus image) {{ sender([event_type:"image_closed", image:snapshot(image)]) }}
    void imageUpdated(ImagePlus image) {{
        long now = System.currentTimeMillis()
        if (now - lastUpdateAt >= 750L) {{ lastUpdateAt = now; sender([event_type:"image_updated", image:snapshot(image)]) }}
    }}
}}

def commandListener = new HMCommandListener(sender:sendEvent, snapshot:imageSnapshot)
def imageListener = new HMImageListener(sender:sendEvent, snapshot:imageSnapshot)
Executer.addCommandListener(commandListener)
ImagePlus.addImageListener(imageListener)
sendEvent([event_type:"bridge_connected", fiji_version:IJ.getVersion(), image:imageSnapshot(WindowManager.getCurrentImage())])
IJ.showStatus("Health Model Research OS: Ray bridge connected")
'''


def install_bridge(callback_base: str) -> dict[str, Any]:
    installation = configured_installation()
    callback = callback_base.rstrip("/") + "/research/fiji/bridge/events"
    if not callback.startswith("http://127.0.0.1:") and not callback.startswith("http://localhost:"):
        raise FijiIntegrationError("FIJI_BRIDGE_CALLBACK_MUST_BE_LOCAL")
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    target = Path(installation["installation_root"]) / "scripts" / "Plugins" / BRIDGE_SCRIPT_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_bridge_script(callback, token), encoding="utf-8")
    bridge = {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "token_sha256": token_hash,
        "callback_url": callback,
        "script_path": str(target),
        "installed_at": _now(),
        "installation_launcher_sha256": installation["launcher_sha256"],
    }
    _json_save(_root() / "bridge.json", bridge)
    return {**bridge, "token_sha256": token_hash, "installed": True}


def remove_bridge() -> dict[str, Any]:
    installation = configured_installation()
    target = Path(installation["installation_root"]) / "scripts" / "Plugins" / BRIDGE_SCRIPT_NAME
    removed = False
    if target.exists():
        target.unlink()
        removed = True
    bridge_file = _root() / "bridge.json"
    if bridge_file.exists():
        bridge_file.unlink()
    return {"schema_version": FIJI_INTEGRATION_SCHEMA_VERSION, "removed": removed, "removed_at": _now()}


def record_bridge_event(authorization: str | None, event: dict[str, Any]) -> dict[str, Any]:
    bridge = _json_load(_root() / "bridge.json", {})
    if not bridge:
        raise FijiIntegrationError("FIJI_BRIDGE_NOT_INSTALLED", 409)
    if not authorization or not authorization.startswith("Bearer "):
        raise FijiIntegrationError("FIJI_BRIDGE_AUTHORIZATION_REQUIRED", 401)
    supplied = authorization[7:].strip()
    supplied_hash = hashlib.sha256(supplied.encode("utf-8")).hexdigest()
    if not secrets.compare_digest(supplied_hash, bridge.get("token_sha256", "")):
        raise FijiIntegrationError("FIJI_BRIDGE_TOKEN_INVALID", 403)
    event_type = str(event.get("event_type") or "").strip()
    if event_type not in {"bridge_connected", "command_started", "image_opened", "image_closed", "image_updated"}:
        raise FijiIntegrationError("FIJI_BRIDGE_EVENT_TYPE_UNSUPPORTED")
    raw_image = event.get("image") if isinstance(event.get("image"), dict) else {}
    image: dict[str, Any] = {}
    for key in ("image_present", "image_id", "title", "width", "height", "channels", "slices", "frames", "bit_depth"):
        if key in raw_image:
            value = raw_image[key]
            image[key] = str(value)[:500] if key == "title" else value
    normalized = {
        "schema_version": "health-model-fiji-bridge-event-1",
        "event_id": str(uuid4()),
        "event_type": event_type,
        "occurred_at": str(event.get("occurred_at") or _now()),
        "received_at": _now(),
        "command": str(event.get("command") or "")[:500],
        "fiji_version": str(event.get("fiji_version") or "")[:100],
        "image": image,
    }
    event_path = _root() / "bridge_events.jsonl"
    if event_path.exists() and event_path.stat().st_size > 5 * 1024 * 1024:
        recent = event_path.read_text(encoding="utf-8").splitlines()[-2000:]
        event_path.write_text("\n".join(recent) + "\n", encoding="utf-8")
    with event_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(normalized, ensure_ascii=False, separators=(",", ":")) + "\n")
    return normalized


def bridge_status(limit: int = 25) -> dict[str, Any]:
    bridge = _json_load(_root() / "bridge.json", {})
    events: list[dict[str, Any]] = []
    path = _root() / "bridge_events.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines()[-max(1, min(limit, 100)):]:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    last = events[-1] if events else None
    return {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "installed": bool(bridge),
        "script_path": bridge.get("script_path"),
        "last_event": last,
        "events": events,
    }


OPERATIONS: dict[str, dict[str, Any]] = {
    "convert_8bit": {"parameters": {}, "macro": 'run("8-bit");'},
    "subtract_background": {"parameters": {"rolling_radius": (0.1, 100000.0)}, "macro": 'run("Subtract Background...", "rolling={rolling_radius}{stack}");'},
    "median_filter": {"parameters": {"radius": (0.0, 1000.0)}, "macro": 'run("Median...", "radius={radius}{stack}");'},
    "gaussian_blur": {"parameters": {"sigma": (0.0, 1000.0)}, "macro": 'run("Gaussian Blur...", "sigma={sigma}{stack}");'},
    "enhance_contrast": {"parameters": {"saturated_percent": (0.0, 100.0)}, "macro": 'run("Enhance Contrast", "saturated={saturated_percent}{normalize}{stack}");'},
    "auto_threshold": {"parameters": {"method": {"Default", "Huang", "Intermodes", "IsoData", "Li", "MaxEntropy", "Mean", "MinError", "Minimum", "Moments", "Otsu", "Percentile", "RenyiEntropy", "Shanbhag", "Triangle", "Yen"}, "background": {"Dark", "Light"}}, "macro": 'setAutoThreshold("{method} {background}");'},
    "convert_to_mask": {"parameters": {"background": {"Dark", "Light"}}, "macro": 'run("Convert to Mask", "background={background} black{stack}");'},
}


def integration_contract(language: str = "ru") -> dict[str, Any]:
    lang = language if language in SUPPORTED_LANGUAGES else "ru"
    labels = {
        "ru": "Fiji — воспроизводимая обработка изображений",
        "en": "Fiji reproducible image processing",
        "es": "Procesamiento reproducible de imágenes con Fiji",
    }
    return {
        "schema_version": FIJI_INTEGRATION_SCHEMA_VERSION,
        "language": lang,
        "title": labels[lang],
        "execution_modes": ["interactive_with_bridge", "headless_reproducible_pipeline"],
        "operations": [{"code": code, "parameters": value["parameters"]} for code, value in OPERATIONS.items()],
        "input_contract": {
            "accepted": ["single_image", "image_stack", "avi_video_openable_by_fiji"],
            "raw_input_immutable": True,
            "global_time_binding": "required_when_frames_represent_time",
        },
        "output_contract": {
            "schema_version": FIJI_RUN_SCHEMA_VERSION,
            "artifacts": ["processed_image_or_stack", "pipeline.json", "run_manifest.json", "stdout.log", "stderr.log"],
            "provenance_required": ["fiji_launcher_sha256", "operations", "input_sha256", "timestamps_utc"],
        },
        "safety": [
            "explicit_user_confirmation_for_install_launch_and_execution",
            "no_shell_interpolation",
            "raw_input_never_overwritten",
            "unknown_version_is_not_invented",
            "errors_are_recorded_not_hidden",
        ],
    }


def validate_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    input_path = Path(str(payload.get("input_path") or "")).expanduser()
    output_path = Path(str(payload.get("output_path") or "")).expanduser()
    if not input_path.is_file():
        raise FijiIntegrationError("FIJI_PIPELINE_INPUT_NOT_FOUND", 404)
    if input_path.resolve() == output_path.resolve():
        raise FijiIntegrationError("FIJI_PIPELINE_MUST_NOT_OVERWRITE_RAW_INPUT")
    if output_path.exists():
        raise FijiIntegrationError("FIJI_PIPELINE_OUTPUT_ALREADY_EXISTS", 409)
    if not output_path.parent.is_dir():
        raise FijiIntegrationError("FIJI_PIPELINE_OUTPUT_DIRECTORY_NOT_FOUND", 404)
    if output_path.suffix.lower() not in {".tif", ".tiff"}:
        raise FijiIntegrationError("FIJI_PIPELINE_OUTPUT_MUST_BE_TIFF")
    operations = payload.get("operations")
    if not isinstance(operations, list) or not operations:
        raise FijiIntegrationError("FIJI_PIPELINE_OPERATIONS_REQUIRED")
    normalized: list[dict[str, Any]] = []
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict):
            raise FijiIntegrationError(f"FIJI_PIPELINE_OPERATION_INVALID:{index}")
        code = str(operation.get("code") or "")
        definition = OPERATIONS.get(code)
        if definition is None:
            raise FijiIntegrationError(f"FIJI_PIPELINE_OPERATION_UNSUPPORTED:{code}")
        parameters = operation.get("parameters") or {}
        if not isinstance(parameters, dict):
            raise FijiIntegrationError(f"FIJI_PIPELINE_PARAMETERS_INVALID:{code}")
        allowed = definition["parameters"]
        if set(parameters) - set(allowed):
            raise FijiIntegrationError(f"FIJI_PIPELINE_PARAMETER_UNSUPPORTED:{code}")
        clean: dict[str, Any] = {}
        for key, rule in allowed.items():
            if key not in parameters:
                raise FijiIntegrationError(f"FIJI_PIPELINE_PARAMETER_REQUIRED:{code}:{key}")
            value = parameters[key]
            if isinstance(rule, tuple):
                try:
                    value = float(value)
                except (TypeError, ValueError) as exc:
                    raise FijiIntegrationError(f"FIJI_PIPELINE_PARAMETER_NOT_NUMERIC:{code}:{key}") from exc
                if not rule[0] <= value <= rule[1]:
                    raise FijiIntegrationError(f"FIJI_PIPELINE_PARAMETER_OUT_OF_RANGE:{code}:{key}")
            elif value not in rule:
                raise FijiIntegrationError(f"FIJI_PIPELINE_PARAMETER_CHOICE_INVALID:{code}:{key}")
            clean[key] = value
        normalized.append({"code": code, "parameters": clean})
    time_reference = payload.get("time_reference")
    if time_reference is not None and not isinstance(time_reference, dict):
        raise FijiIntegrationError("FIJI_PIPELINE_TIME_REFERENCE_INVALID")
    if time_reference:
        if time_reference.get("axis") != "UTC":
            raise FijiIntegrationError("FIJI_PIPELINE_TIME_AXIS_MUST_BE_UTC")
        interval = time_reference.get("frame_interval_seconds")
        if interval is not None:
            try:
                interval = float(interval)
            except (TypeError, ValueError) as exc:
                raise FijiIntegrationError("FIJI_PIPELINE_FRAME_INTERVAL_INVALID") from exc
            if interval <= 0:
                raise FijiIntegrationError("FIJI_PIPELINE_FRAME_INTERVAL_INVALID")
            time_reference = {**time_reference, "frame_interval_seconds": interval}
    if input_path.suffix.lower() == ".avi" and not (
        time_reference and time_reference.get("origin_utc") and time_reference.get("frame_interval_seconds")
    ):
        raise FijiIntegrationError("FIJI_AVI_GLOBAL_TIME_REFERENCE_REQUIRED")
    codes = [item["code"] for item in normalized]
    if "convert_to_mask" in codes and "auto_threshold" not in codes[:codes.index("convert_to_mask")]:
        raise FijiIntegrationError("FIJI_MASK_REQUIRES_PRECEDING_THRESHOLD")
    return {
        "schema_version": FIJI_PIPELINE_SCHEMA_VERSION,
        "input_path": str(input_path.resolve()),
        "output_path": str(output_path.resolve()),
        "input_sha256": _sha256(input_path),
        "apply_to_stack": bool(payload.get("apply_to_stack", False)),
        "operations": normalized,
        "time_reference": time_reference or {},
    }


def _macro_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_macro(pipeline: dict[str, Any]) -> str:
    stack = " stack" if pipeline["apply_to_stack"] else ""
    lines = [
        'setBatchMode(true);',
        f'open("{_macro_escape(pipeline["input_path"])}");',
        'if (nImages == 0) exit("INPUT_COULD_NOT_BE_OPENED");',
    ]
    for operation in pipeline["operations"]:
        code = operation["code"]
        parameters = dict(operation["parameters"])
        parameters["stack"] = stack
        parameters["normalize"] = " normalize" if parameters.pop("normalize", False) else ""
        lines.append(OPERATIONS[code]["macro"].format(**parameters))
    output = _macro_escape(pipeline["output_path"])
    lines.extend((f'saveAs("Tiff", "{output}");', 'close();', 'setBatchMode(false);'))
    return "\n".join(lines) + "\n"


_RUN_PROCESSES: dict[str, subprocess.Popen] = {}
_RUN_LOCK = threading.RLock()


def _run_record_path(run_id: str) -> Path:
    return _root() / "runs" / run_id / "run_manifest.json"


def _finalize_run(run_id: str, process: subprocess.Popen, output_path: Path) -> None:
    exit_code = process.wait()
    with _RUN_LOCK:
        record = _json_load(_run_record_path(run_id), {})
        record["status"] = "completed" if exit_code == 0 and output_path.is_file() else "failed"
        record["exit_code"] = exit_code
        record["finished_at"] = _now()
        if output_path.is_file():
            record["output_sha256"] = _sha256(output_path)
            record["output_size"] = output_path.stat().st_size
        elif exit_code == 0:
            record["failure_code"] = "FIJI_FINISHED_WITHOUT_EXPECTED_OUTPUT"
            record["status"] = "failed"
        _json_save(_run_record_path(run_id), record)
        _RUN_PROCESSES.pop(run_id, None)


def execute_pipeline(payload: dict[str, Any], *, actor_id: str, authorship: dict[str, Any] | None = None) -> dict[str, Any]:
    installation = configured_installation()
    pipeline = validate_pipeline(payload)
    run_id = str(uuid4())
    run_directory = _root() / "runs" / run_id
    run_directory.mkdir(parents=True, exist_ok=False)
    macro_path = run_directory / "pipeline.ijm"
    macro_path.write_text(build_macro(pipeline), encoding="utf-8")
    _json_save(run_directory / "pipeline.json", pipeline)
    stdout_path = run_directory / "stdout.log"
    stderr_path = run_directory / "stderr.log"
    stdout = stdout_path.open("wb")
    stderr = stderr_path.open("wb")
    command = [installation["launcher_path"], "--headless", "--run", str(macro_path)]
    try:
        process = subprocess.Popen(  # noqa: S603 - validated Fiji launcher, no shell
            command, cwd=installation["installation_root"], stdout=stdout, stderr=stderr,
            start_new_session=True,
        )
    except OSError as exc:
        stdout.close()
        stderr.close()
        raise FijiIntegrationError("FIJI_PIPELINE_PROCESS_START_FAILED", 500) from exc
    finally:
        stdout.close()
        stderr.close()
    record = {
        "schema_version": FIJI_RUN_SCHEMA_VERSION,
        "run_id": run_id,
        "status": "running",
        "actor_id": actor_id,
        "authorship": authorship or {},
        "started_at": _now(),
        "process_id": process.pid,
        "fiji_launcher_path": installation["launcher_path"],
        "fiji_launcher_sha256": installation["launcher_sha256"],
        "pipeline": pipeline,
        "artifacts": {
            "pipeline": str(run_directory / "pipeline.json"),
            "macro": str(macro_path),
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
        },
    }
    _json_save(_run_record_path(run_id), record)
    with _RUN_LOCK:
        _RUN_PROCESSES[run_id] = process
    threading.Thread(target=_finalize_run, args=(run_id, process, Path(pipeline["output_path"])), daemon=True).start()
    return record


def get_run(run_id: str) -> dict[str, Any]:
    if not run_id or any(character not in "0123456789abcdef-" for character in run_id.lower()):
        raise FijiIntegrationError("FIJI_RUN_ID_INVALID")
    record = _json_load(_run_record_path(run_id), None)
    if record is None:
        raise FijiIntegrationError("FIJI_RUN_NOT_FOUND", 404)
    return record
