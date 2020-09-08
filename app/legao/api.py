from pydantic import BaseModel
from starlette.responses import FileResponse
from fastapi import UploadFile, File, BackgroundTasks
import hashlib
import os
import json
from ..main import app
from .maker import legofy, LEGO
from ..legao import STATS_FILE_PATH, UPLOAD_DIR


def stats():
    with open(STATS_FILE_PATH, 'r') as f:
        data = json.load(f)
        imagesUploaded = data.get('imagesUploaded')
        imagesMade = data.get('imagesMade')
    return imagesUploaded, imagesMade


def updateStats(imagesUploaded, imagesMade):
    with open(STATS_FILE_PATH, 'w+') as f:
        json.dump({"imagesUploaded": imagesUploaded,
                   "imagesMade": imagesMade}, f)


@app.get("/legao/palettes")
def query_palettes():
    lego = LEGO()
    imagesUploaded, imagesMade = stats()
    return {'imagesUploaded': imagesUploaded, 'imagesMade': imagesMade,
            'palettes': lego.palettes.get('all'), 'names': lego.color_names}


@app.post("/legao/upload")
async def receive_image(bg_tasks: BackgroundTasks, file: UploadFile = File(...)):
    contents = await file.read()
    md5 = hashlib.md5(contents).hexdigest()
    _, ext = os.path.splitext(file.filename)
    file_path = os.path.join(UPLOAD_DIR, "".join([md5, ext]))
    with open(file_path, 'wb') as f:
        f.write(contents)
    imagesUploaded, imagesMade = stats()
    bg_tasks.add_task(updateStats, imagesUploaded+1, imagesMade)
    return {'status': 'received', 'md5': md5+ext, 'imagesUploaded': imagesUploaded}


class Params(BaseModel):
    maxLength: int = 100
    brickEffect: str = "all"
    uploadedImageMD5: str = None


@app.post("/legao/submit")
def make_image(params: Params, bg_tasks: BackgroundTasks):
    imageName, ext = os.path.splitext(params.uploadedImageMD5)
    output_fileName = f'{imageName}_output_{params.maxLength}_{params.brickEffect}.png'
    output_path = os.path.join(UPLOAD_DIR, output_fileName)
    print(f'make_image: {output_path}')
    try:
        lego_stats = legofy(
            imageName+ext, output_path, params.brickEffect, params.maxLength)
        imagesUploaded, imagesMade = stats()
        bg_tasks.add_task(updateStats, imagesUploaded+1, imagesMade+1)
        return {'status': 'done', 'stats': lego_stats, 'resultImage': output_fileName, 'imagesMade': imagesMade+1}
    except Exception as e:
        print(e)
        return {'status': 'failed'}


def remove_old_files():
    """Delete files that are 5min old."""
    bash = f"find {UPLOAD_DIR} -name '*.*' -mmin +5 -delete"
    os.system(bash)


@app.get("/legao/result/{imageName}")
def send_result_image(imageName, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(remove_old_files)
    filepath = os.path.join(UPLOAD_DIR, imageName)
    if os.path.isfile(filepath):
        return FileResponse(filepath,  media_type="image/png")
    else:
        return {'status': 'not found'}
