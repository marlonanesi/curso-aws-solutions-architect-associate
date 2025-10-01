import os
import io
import json
import boto3
from PIL import Image
from urllib.parse import unquote_plus
from PIL import ImageOps

s3 = boto3.client("s3")
MAX_SIZE = int(os.getenv("MAX_THUMB_SIZE", "256"))  # lado máximo

def lambda_handler(event, context):
    # Evento S3 PutObject
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    # Decodifica a key (suporta espaços e caracteres especiais)
    key = unquote_plus(record["s3"]["object"]["key"])

    # Ignora se já for thumbnail
    if key.startswith("thumbnails/"):
        return {"status": "ignored", "reason": "already thumbnail"}

    try:
        # Baixa a imagem
        obj = s3.get_object(Bucket=bucket, Key=key)
        img_bytes = obj["Body"].read()
        img = Image.open(io.BytesIO(img_bytes))

        # Normaliza orientação via EXIF e converte p/ RGB se necessário
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # Redimensiona preservando proporção
        img.thumbnail((MAX_SIZE, MAX_SIZE))

        # Salva em memória
        out = io.BytesIO()
        img_format = "PNG" if img.mode == "RGBA" else "JPEG"
        img.save(out, format=img_format, optimize=True)
        out.seek(0)

        # Novo key
        thumb_key = f"thumbnails/{os.path.basename(key).rsplit('.', 1)[0]}_{MAX_SIZE}.{img_format.lower()}"

        # Envia ao S3
        s3.put_object(
            Bucket=bucket,
            Key=thumb_key,
            Body=out.getvalue(),
            ContentType=f"image/{img_format.lower()}",
            Metadata={"source-key": key}
        )

        return {
            "status": "ok",
            "bucket": bucket,
            "source_key": key,
            "thumb_key": thumb_key,
            "max_size": MAX_SIZE
        }
    except Exception as e:
        print(f"Error processing object s3://{bucket}/{key}: {e}")
        return {"status": "error", "bucket": bucket, "source_key": key, "message": str(e)}

# if __name__ == "__main__":
#     with open("event-s3-sample.json") as f:
#         event = json.load(f)

#     result = lambda_handler(event, None)
#     print(result)
