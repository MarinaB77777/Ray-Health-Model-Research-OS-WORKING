from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import json
import re
from typing import Any
from uuid import uuid4


TRAINING_RUN_SCHEMA_VERSION = "health-model-training-run-1"
DATASET_MANIFEST_SCHEMA_VERSION = "paired-image-mask-manifest-1"
MODEL_ARTIFACT_SCHEMA_VERSION = "binary-segmentation-model-artifact-1"
SUPPORTED_LANGUAGES = frozenset({"ru", "en", "es"})
FOLDER_ID_RE = re.compile(r"(?:/folders/|[?&]id=)([A-Za-z0-9_-]{10,})")


class ModelTrainingError(Exception):
    def __init__(self, code: str, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def _required_text(value: Any, code: str, maximum: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelTrainingError(code)
    result = value.strip()
    if len(result) > maximum:
        raise ModelTrainingError(f"{code}_TOO_LONG")
    return result


def drive_folder_id(value: str) -> str | None:
    value = str(value or "").strip()
    match = FOLDER_ID_RE.search(value)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", value):
        return value
    return None


def validate_training_configuration(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ModelTrainingError("TRAINING_CONFIGURATION_MUST_BE_OBJECT")
    language = str(raw.get("language") or "ru").lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ModelTrainingError("TRAINING_LANGUAGE_UNSUPPORTED")
    sources = _required_text(raw.get("source_folder"), "SOURCE_FOLDER_REQUIRED")
    masks = _required_text(raw.get("mask_folder"), "MASK_FOLDER_REQUIRED")
    output = _required_text(raw.get("output_folder"), "OUTPUT_FOLDER_REQUIRED")
    if sources == masks:
        raise ModelTrainingError("SOURCE_AND_MASK_FOLDERS_MUST_DIFFER")
    target = str(raw.get("task_type") or "grayscale_binary_segmentation")
    if target != "grayscale_binary_segmentation":
        raise ModelTrainingError("TRAINING_TASK_TYPE_UNSUPPORTED")
    pairing = str(raw.get("pairing_strategy") or "relative_path_and_normalized_stem")
    if pairing not in {"relative_path_and_normalized_stem", "same_relative_name"}:
        raise ModelTrainingError("PAIRING_STRATEGY_UNSUPPORTED")
    group_regex = str(raw.get("group_regex") or "").strip()
    if len(group_regex) > 500:
        raise ModelTrainingError("GROUP_REGEX_TOO_LONG")
    if group_regex:
        try:
            re.compile(group_regex)
        except re.error as exc:
            raise ModelTrainingError("GROUP_REGEX_INVALID") from exc
    image_height = int(raw.get("image_height") or 256)
    image_width = int(raw.get("image_width") or 256)
    if not (32 <= image_height <= 2048 and 32 <= image_width <= 2048):
        raise ModelTrainingError("TRAINING_IMAGE_SIZE_OUT_OF_RANGE")
    batch_size = int(raw.get("batch_size") or 8)
    epochs = int(raw.get("epochs") or 50)
    seed = int(raw.get("seed") or 20260719)
    if not 1 <= batch_size <= 256:
        raise ModelTrainingError("TRAINING_BATCH_SIZE_OUT_OF_RANGE")
    if not 1 <= epochs <= 5000:
        raise ModelTrainingError("TRAINING_EPOCHS_OUT_OF_RANGE")
    return {
        "schema_version": TRAINING_RUN_SCHEMA_VERSION,
        "run_id": str(uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "language": language,
        "task_type": target,
        "source_folder": sources,
        "mask_folder": masks,
        "output_folder": output,
        "pairing_strategy": pairing,
        "group_regex": group_regex or None,
        "image_size": [image_height, image_width],
        "batch_size": batch_size,
        "epochs": epochs,
        "seed": seed,
        "source_channel_contract": "single_channel_grayscale",
        "target_contract": "binary_mask_0_1",
        "time_binding": "source_frame_index_and_source_video_time_preserved",
        "split_contract": "group_exclusive_train_validation_test",
        "threshold_policy": "selected_on_validation_once_then_locked_for_test",
        "raw_data_policy": "immutable",
    }


def training_contract(language: str = "ru") -> dict[str, Any]:
    if language not in SUPPORTED_LANGUAGES:
        raise ModelTrainingError("TRAINING_LANGUAGE_UNSUPPORTED")
    labels = {
        "ru": {
            "title": "Обучение модели: изображение → бинарная маска",
            "description": "Воспроизводимое обучение сегментации по изображениям в градациях серого и ручным бинарным маскам.",
        },
        "en": {
            "title": "Model training: image → binary mask",
            "description": "Reproducible segmentation training from grayscale images and manually created binary masks.",
        },
        "es": {
            "title": "Entrenamiento: imagen → máscara binaria",
            "description": "Entrenamiento reproducible con imágenes en escala de grises y máscaras binarias manuales.",
        },
    }[language]
    return {
        "schema_version": TRAINING_RUN_SCHEMA_VERSION,
        **labels,
        "task_types": ["grayscale_binary_segmentation"],
        "accepted_sources": ["png", "tif", "tiff", "bmp", "jpg", "jpeg"],
        "accepted_masks": ["png", "tif", "tiff", "bmp"],
        "required_outputs": [
            "dataset_manifest.json", "split_manifest.json", "preprocessing.json",
            "best_model.keras", "training_history.json", "threshold.json",
            "test_metrics.json", "model_card.json", "training_run.json",
        ],
        "scientific_guards": [
            "exact_source_mask_pairing",
            "grayscale_input_validation",
            "binary_mask_validation",
            "group_exclusive_split",
            "train_only_preprocessing_fit",
            "validation_only_threshold_selection",
            "single_final_test_evaluation",
            "immutable_raw_inputs",
        ],
    }


def _cell(cell_type: str, source: str) -> dict[str, Any]:
    cell: dict[str, Any] = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(True)}
    if cell_type == "code":
        cell.update({"execution_count": None, "outputs": []})
    return cell


def build_colab_notebook(raw: dict[str, Any], *, author: dict[str, Any] | None = None) -> dict[str, Any]:
    config = validate_training_configuration(raw)
    author = deepcopy(author or {})
    config["authorship"] = {
        "schema_version": "research-object-authorship-1",
        "author_identity_id": author.get("author_identity_id"),
        "display_name": author.get("display_name"),
        "preservation_policy": "authorship_survives_account_deletion",
    }
    config_json = json.dumps(config, ensure_ascii=False, indent=2)
    setup = r'''# Runtime, authorization and reproducibility
from google.colab import auth
auth.authenticate_user()
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io, json, os, pathlib, random, re, shutil, hashlib, platform
import numpy as np
import tensorflow as tf
import cv2
from sklearn.model_selection import GroupShuffleSplit

CONFIG = json.loads(CONFIG_JSON)
random.seed(CONFIG["seed"]); np.random.seed(CONFIG["seed"]); tf.random.set_seed(CONFIG["seed"])
creds, _ = google.auth.default()
drive_api = build("drive", "v3", credentials=creds, cache_discovery=False)
WORK = pathlib.Path("/content/health_model_training")
if WORK.exists(): shutil.rmtree(WORK)
(WORK/"sources").mkdir(parents=True); (WORK/"masks").mkdir(); (WORK/"artifacts").mkdir()
print("Ray: authorization complete; source files are copied to the temporary runtime and originals remain unchanged.")
'''
    drive_io = r'''FOLDER_RE = re.compile(r"(?:/folders/|[?&]id=)([A-Za-z0-9_-]{10,})")
def folder_id(ref):
    m = FOLDER_RE.search(ref)
    if m: return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", ref): return ref
    return None

def safe_name(name):
    name = pathlib.Path(str(name)).name
    if name in {"", ".", ".."}: raise ValueError("UNSAFE_DRIVE_NAME")
    return name

def download_drive_folder(ref, target):
    fid=folder_id(ref)
    if not fid: raise ValueError("A Google Drive folder URL or folder ID is required")
    def walk(parent, destination):
        token=None
        while True:
            result=drive_api.files().list(q=f"'{parent}' in parents and trashed=false", fields="nextPageToken,files(id,name,mimeType,md5Checksum,size)", pageToken=token, pageSize=1000).execute()
            for item in result.get("files",[]):
                name=safe_name(item["name"]); path=destination/name
                if item["mimeType"]=="application/vnd.google-apps.folder":
                    path.mkdir(exist_ok=True); walk(item["id"],path)
                else:
                    request=drive_api.files().get_media(fileId=item["id"])
                    with path.open("wb") as fh:
                        downloader=MediaIoBaseDownload(fh,request)
                        done=False
                        while not done: _,done=downloader.next_chunk()
            token=result.get("nextPageToken")
            if not token: break
    walk(fid,pathlib.Path(target)); return fid

SOURCE_FOLDER_ID=download_drive_folder(CONFIG["source_folder"],WORK/"sources")
MASK_FOLDER_ID=download_drive_folder(CONFIG["mask_folder"],WORK/"masks")
OUTPUT_FOLDER_ID=folder_id(CONFIG["output_folder"])
if not OUTPUT_FOLDER_ID: raise ValueError("OUTPUT_FOLDER_MUST_BE_GOOGLE_DRIVE_FOLDER")
print("Ray: folders copied; building an immutable manifest and validating exact pairs.")
'''
    validation = r'''IMAGE_EXT={".png",".tif",".tiff",".bmp",".jpg",".jpeg"}
MASK_EXT={".png",".tif",".tiff",".bmp"}
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def canonical(stem):
    parts=re.split(r"[_\-\s]+",stem.lower())
    ignored={"frame","image","img","mask","binary","label","seg","segmentation"}
    return "_".join(x for x in parts if x not in ignored)
def key(path,root):
    rel=path.relative_to(root)
    stem=rel.stem if CONFIG["pairing_strategy"]=="same_relative_name" else canonical(rel.stem)
    return str(rel.parent).lower()+"/"+stem
def index_files(root,extensions):
    result={}; collisions={}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in extensions:
            k=key(p,root)
            if k in result: collisions.setdefault(k,[str(result[k])]).append(str(p))
            else: result[k]=p
    if collisions: raise ValueError("AMBIGUOUS_PAIR_KEYS:"+json.dumps(collisions,ensure_ascii=False))
    return result
sources=index_files(WORK/"sources",IMAGE_EXT); masks=index_files(WORK/"masks",MASK_EXT)
missing_masks=sorted(set(sources)-set(masks)); missing_sources=sorted(set(masks)-set(sources))
if missing_masks or missing_sources:
    raise ValueError("PAIRING_INCOMPLETE:"+json.dumps({"without_mask":missing_masks[:100],"without_source":missing_sources[:100]},ensure_ascii=False))
if not sources: raise ValueError("NO_IMAGE_MASK_PAIRS")

group_re=re.compile(CONFIG["group_regex"]) if CONFIG.get("group_regex") else None
def group_for(path):
    rel=str(path.relative_to(WORK/"sources"))
    if group_re:
        m=group_re.search(rel)
        if not m: raise ValueError("GROUP_REGEX_DID_NOT_MATCH:"+rel)
        return m.group(1) if m.groups() else m.group(0)
    parts=path.relative_to(WORK/"sources").parts
    return parts[0] if len(parts)>1 else re.sub(r"[_-]?\d+$","",path.stem)

manifest=[]
for k,src in sources.items():
    mask=masks[k]
    x=cv2.imread(str(src),cv2.IMREAD_UNCHANGED); y=cv2.imread(str(mask),cv2.IMREAD_GRAYSCALE)
    if x is None or y is None: raise ValueError("UNREADABLE_PAIR:"+k)
    if x.ndim==3:
        if x.shape[2] not in {3,4} or not np.all(x[...,0]==x[...,1]) or not np.all(x[...,0]==x[...,2]):
            raise ValueError("SOURCE_IS_NOT_GRAYSCALE:"+k)
    elif x.ndim!=2: raise ValueError("SOURCE_DIMENSION_UNSUPPORTED:"+k)
    unique=np.unique(y)
    if len(unique)>2: raise ValueError("MASK_IS_NOT_BINARY:"+k+":"+str(unique[:20]))
    manifest.append({"pair_key":k,"source":str(src),"mask":str(mask),"group_id":group_for(src),"source_sha256":sha256(src),"mask_sha256":sha256(mask),"mask_values":[int(v) for v in unique]})
groups=sorted({x["group_id"] for x in manifest})
if len(groups)<3: raise ValueError("AT_LEAST_THREE_INDEPENDENT_GROUPS_REQUIRED_FOR_TRAIN_VALIDATION_TEST")
json.dump({"schema_version":"paired-image-mask-manifest-1","pairs":manifest},open(WORK/"artifacts/dataset_manifest.json","w"),ensure_ascii=False,indent=2)
print(f"Ray: {len(manifest)} exact pairs, {len(groups)} independent groups; validation passed.")
'''
    split_and_data = r'''idx=np.arange(len(manifest)); group_values=np.array([x["group_id"] for x in manifest])
outer=GroupShuffleSplit(n_splits=1,test_size=0.15,random_state=CONFIG["seed"])
train_val_idx,test_idx=next(outer.split(idx,groups=group_values))
inner=GroupShuffleSplit(n_splits=1,test_size=0.1764705882,random_state=CONFIG["seed"]+1)
train_rel,val_rel=next(inner.split(train_val_idx,groups=group_values[train_val_idx]))
train_idx=train_val_idx[train_rel]; val_idx=train_val_idx[val_rel]
split={"train":[manifest[i]["pair_key"] for i in train_idx],"validation":[manifest[i]["pair_key"] for i in val_idx],"test":[manifest[i]["pair_key"] for i in test_idx]}
split_groups={name:sorted({manifest[i]["group_id"] for i in ids}) for name,ids in {"train":train_idx,"validation":val_idx,"test":test_idx}.items()}
assert not(set(split_groups["train"])&set(split_groups["validation"])|set(split_groups["train"])&set(split_groups["test"])|set(split_groups["validation"])&set(split_groups["test"]))
json.dump({"split":split,"groups":split_groups,"seed":CONFIG["seed"]},open(WORK/"artifacts/split_manifest.json","w"),ensure_ascii=False,indent=2)

H,W=CONFIG["image_size"]
class PairSequence(tf.keras.utils.Sequence):
    def __init__(self,indices,shuffle): self.indices=np.array(indices); self.shuffle=shuffle; self.on_epoch_end()
    def __len__(self): return int(np.ceil(len(self.indices)/CONFIG["batch_size"]))
    def on_epoch_end(self):
        if self.shuffle: np.random.default_rng(CONFIG["seed"]).shuffle(self.indices)
    def __getitem__(self,n):
        batch=self.indices[n*CONFIG["batch_size"]:(n+1)*CONFIG["batch_size"]]; xs=[];ys=[]
        for i in batch:
            item=manifest[int(i)]; x=cv2.imread(item["source"],cv2.IMREAD_GRAYSCALE); y=cv2.imread(item["mask"],cv2.IMREAD_GRAYSCALE)
            x=cv2.resize(x,(W,H),interpolation=cv2.INTER_AREA).astype("float32")/255.0
            y=cv2.resize(y,(W,H),interpolation=cv2.INTER_NEAREST); values=np.unique(y); high=int(values[-1]); y=(y==high).astype("float32")
            xs.append(x[...,None]);ys.append(y[...,None])
        return np.asarray(xs),np.asarray(ys)
train=PairSequence(train_idx,True); validation=PairSequence(val_idx,False); test=PairSequence(test_idx,False)
json.dump({"input":"grayscale","scale":[0,1],"resize":[H,W],"image_interpolation":"area","mask_interpolation":"nearest","mask":"higher observed binary value maps to 1"},open(WORK/"artifacts/preprocessing.json","w"),indent=2)
'''
    model_training = r'''def dice_metric(y_true,y_pred,smooth=1e-6):
    y_true=tf.reshape(y_true,[-1]);y_pred=tf.reshape(y_pred,[-1]);return (2*tf.reduce_sum(y_true*y_pred)+smooth)/(tf.reduce_sum(y_true)+tf.reduce_sum(y_pred)+smooth)
def dice_loss(y_true,y_pred): return 1-dice_metric(y_true,y_pred)
def block(x,n):
    x=tf.keras.layers.Conv2D(n,3,padding="same",activation="relu")(x);x=tf.keras.layers.BatchNormalization()(x)
    x=tf.keras.layers.Conv2D(n,3,padding="same",activation="relu")(x);return tf.keras.layers.BatchNormalization()(x)
inp=tf.keras.Input((H,W,1));c1=block(inp,32);p1=tf.keras.layers.MaxPool2D()(c1);c2=block(p1,64);p2=tf.keras.layers.MaxPool2D()(c2);c3=block(p2,128);p3=tf.keras.layers.MaxPool2D()(c3);b=block(p3,256)
u3=tf.keras.layers.UpSampling2D()(b);u3=tf.keras.layers.Concatenate()([u3,c3]);c4=block(u3,128)
u2=tf.keras.layers.UpSampling2D()(c4);u2=tf.keras.layers.Concatenate()([u2,c2]);c5=block(u2,64)
u1=tf.keras.layers.UpSampling2D()(c5);u1=tf.keras.layers.Concatenate()([u1,c1]);c6=block(u1,32)
out=tf.keras.layers.Conv2D(1,1,activation="sigmoid",name="probability_mask")(c6)
model=tf.keras.Model(inp,out,name="generic_grayscale_binary_unet")
def combined_loss(y_true,y_pred): return tf.keras.losses.binary_crossentropy(y_true,y_pred)+dice_loss(y_true,y_pred)
model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),loss=combined_loss,metrics=[dice_metric,tf.keras.metrics.BinaryIoU(target_class_ids=[1],threshold=0.5,name="iou")])
callbacks=[tf.keras.callbacks.ModelCheckpoint(WORK/"artifacts/best_model.keras",monitor="val_loss",save_best_only=True),tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=10,restore_best_weights=True),tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",patience=5,factor=.5)]
history=model.fit(train,validation_data=validation,epochs=CONFIG["epochs"],callbacks=callbacks,verbose=1)
json.dump({k:[float(x) for x in v] for k,v in history.history.items()},open(WORK/"artifacts/training_history.json","w"),indent=2)
'''
    evaluation = r'''def collect(sequence):
    truths=[];probs=[]
    for i in range(len(sequence)):
        x,y=sequence[i];truths.append(y);probs.append(model.predict(x,verbose=0))
    return np.concatenate(truths).reshape(-1),np.concatenate(probs).reshape(-1)
yv,pv=collect(validation)
def scores(y,p,t):
    z=p>=t; y=y.astype(bool);tp=np.sum(z&y);tn=np.sum(~z&~y);fp=np.sum(z&~y);fn=np.sum(~z&y)
    div=lambda a,b:float(a/b) if b else None
    return {"threshold":float(t),"dice":div(2*tp,2*tp+fp+fn),"iou":div(tp,tp+fp+fn),"sensitivity":div(tp,tp+fn),"specificity":div(tn,tn+fp),"precision":div(tp,tp+fp),"tp":int(tp),"tn":int(tn),"fp":int(fp),"fn":int(fn)}
candidates=[scores(yv,pv,t) for t in np.linspace(.05,.95,19)];best=max(candidates,key=lambda x:x["dice"] if x["dice"] is not None else -1);threshold=best["threshold"]
json.dump({"selection_set":"validation","criterion":"maximum_dice","selected_threshold":threshold,"candidates":candidates},open(WORK/"artifacts/threshold.json","w"),indent=2)
yt,pt=collect(test);test_metrics=scores(yt,pt,threshold)
json.dump({"evaluation_set":"held_out_test_used_after_threshold_lock","metrics":test_metrics},open(WORK/"artifacts/test_metrics.json","w"),indent=2)
run={**CONFIG,"status":"trial_completed","software":{"python":platform.python_version(),"tensorflow":tf.__version__,"opencv":cv2.__version__},"pair_count":len(manifest),"group_count":len(groups),"selected_threshold":threshold}
json.dump(run,open(WORK/"artifacts/training_run.json","w"),ensure_ascii=False,indent=2)
json.dump({"schema_version":"binary-segmentation-model-artifact-1","intended_use":"grayscale image to binary mask","limitations":["Validation is limited to the registered held-out groups","Threshold is dataset-version specific"],"metrics":test_metrics,"authorship":CONFIG.get("authorship")},open(WORK/"artifacts/model_card.json","w"),ensure_ascii=False,indent=2)
print("Ray: training and held-out evaluation completed. Uploading the complete registered artifact set.")
'''
    upload = r'''def upload_file(path,parent_id):
    media=MediaFileUpload(str(path),resumable=True)
    return drive_api.files().create(body={"name":path.name,"parents":[parent_id]},media_body=media,fields="id,name").execute()
uploaded=[]
for path in sorted((WORK/"artifacts").iterdir()): uploaded.append(upload_file(path,OUTPUT_FOLDER_ID))
print("Ray: complete.",json.dumps(uploaded,ensure_ascii=False,indent=2))
'''
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
            "accelerator": "GPU",
            "colab": {"name": f"Health Model Training {config['run_id']}.ipynb", "provenance": []},
            "health_model_training": {
                "schema_version": TRAINING_RUN_SCHEMA_VERSION,
                "run_id": config["run_id"],
                "task_type": config["task_type"],
            },
        },
        "cells": [
            _cell("markdown", "# Health Model · Model Training Block\n\nGrayscale images → manually annotated binary masks. Raw inputs are immutable; all transformations and splits are registered.\n\nDesigned and developed collaboratively by Marina Boronenko and Ray, AI research and engineering colleagues."),
            _cell("code", f"CONFIG_JSON = {json.dumps(config_json, ensure_ascii=False)}\nprint(CONFIG_JSON)"),
            _cell("code", setup), _cell("code", drive_io), _cell("code", validation),
            _cell("code", split_and_data), _cell("code", model_training),
            _cell("code", evaluation), _cell("code", upload),
        ],
    }
