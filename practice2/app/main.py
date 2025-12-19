# -*- coding: utf-8 -*-

"""
Video Processing API - Practice 2
FastAPI with video conversion endpoints using FFmpeg in Docker.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import shutil  
from typing import List

app = FastAPI(title="Video Processing API", version="1.0.0")

# Ruta del video de entrada (carpetas de input_files y output_files en practice2)
INPUT_VIDEO = "input_files/input.mp4"

# Rutas de salida
OUTPUT_DIR = "output_files"
OUTPUT_VP8 = f"{OUTPUT_DIR}/output_vp8.webm"
OUTPUT_VP9 = f"{OUTPUT_DIR}/output_vp9.webm"
OUTPUT_H265 = f"{OUTPUT_DIR}/output_h265.mp4"
OUTPUT_AV1 = f"{OUTPUT_DIR}/output_av1.mkv"

# Mapeo de codecs a los parametros de FFmpeg
CODEC_MAP = {
    "vp8": {"output_file": OUTPUT_VP8, "vcodec": "libvpx", "extension": ".webm"},
    "vp9": {"output_file": OUTPUT_VP9, "vcodec": "libvpx-vp9", "extension": ".webm"},
    "h265": {"output_file": OUTPUT_H265, "vcodec": "libx265", "extension": ".mp4"},
    "av1": {"output_file": OUTPUT_AV1, "vcodec": "libaom-av1", "extension": ".mkv"},
}

def convert_video(input_path: str, output_path: str, vcodec: str, extra_params: List[str] = None) -> bool:
    """
    Convierte un video copiando el archivo de entrada a /tmp primero para
    solucionar el error de lectura del volumen (error 234).
    Acepta 'extra_params' para anadir bitrate, resolucion, etc. (Ladder).
    """
    if extra_params is None:
        extra_params = []
        
    volume_input_path = f"/code/app/{input_path}"
    volume_output_path = f"/code/app/{output_path}"
    temp_input_path = "/tmp/input_temp.mp4" 
    
    try:
       
        print(f"Copiando {volume_input_path} a {temp_input_path}...")
        shutil.copyfile(volume_input_path, temp_input_path)
        print("Copia exitosa. Ejecutando FFmpeg...")
        
        
        cmd = [
            'ffmpeg', '-y', 
            '-analyzeduration', '2147483647', 
            '-probesize', '2147483647', 
            '-fflags', '+genpts',           
            '-i', temp_input_path,          
            '-c:v', vcodec,
            *extra_params, 
            '-c:a', 'libopus',              # Recodificacion de audio forzada a OPUS
            '-b:a', '96k',                  # Bitrate de audio
            volume_output_path              # Salida al volumen
        ]
       
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
      
        os.remove(temp_input_path)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with return code {e.returncode}:")
        
        # DEBUGGING: IMPRIME EL ERROR COMPLETO DE FFmpeg 
        print("\n--- DEBUG FFmpeg Output ---")
        print("Cuerpo del Error (Stderr):")
        print(e.stderr)
        print("\nSalida Normal (Stdout):")
        print(e.stdout)
        print("---------------------------\n")
        

        if os.path.exists(temp_input_path):
             os.remove(temp_input_path)
        return False
    except Exception as e:
        print(f"An unexpected error occurred during copy or FFmpeg execution: {e}")
        return False


class VideoConvertRequest(BaseModel):
    """Modelo para especificar el codec de conversion."""
    codec: str # Debe ser uno de: 'vp8', 'vp9', 'h265', 'av1'
    

class EncodingProfile(BaseModel):
    """Define un perfil de codificacion dentro del ladder."""
    
    codec: str 
    bitrate: str 
    resolution: str = None 
    output_prefix: str 

class EncodingLadderRequest(BaseModel):
    """Modelo para solicitar la conversion de multiples perfiles (ladder)."""
    
    profiles: List[EncodingProfile]

# Endpoints

@app.get("/")
def home():
    """Endpoint de bienvenida."""
    return {"message": "Video Processing API - Practice 2"}

@app.post("/video/convert")
def convert_video_endpoint(request: VideoConvertRequest):
    """
    Endpoint para convertir un video de entrada al codec especificado.
    """
    codec_key = request.codec.lower()
    
    if codec_key not in CODEC_MAP:
        raise HTTPException(status_code=400, detail=f"Codec '{request.codec}' no soportado. Codecs validos: {list(CODEC_MAP.keys())}")
        
    if not os.path.exists(f"app/{INPUT_VIDEO}"):
        raise HTTPException(status_code=404, detail=f"Video de entrada no encontrado en: app/{INPUT_VIDEO}")

    # Obtener los parametros de conversion
    params = CODEC_MAP[codec_key]
    output_path = params["output_file"]
    vcodec = params["vcodec"]
    
    # Ejecutamos la funcion de conversion
    success = convert_video(
        input_path=INPUT_VIDEO,
        output_path=output_path,
        vcodec=vcodec
    )
    
    if success:
        return {
            "status": "success", 
            "message": f"Video convertido a {codec_key}", 
            "output": output_path
        }
    else:
        raise HTTPException(status_code=500, detail="Fallo en el procesamiento con FFmpeg. Revisa los logs para el detalle del error.")

@app.post("/video/ladder")
def convert_video_ladder_endpoint(request: EncodingLadderRequest):
    """
    Endpoint para generar una escalera de codificacion (multiples bitrates/resoluciones)
    en una sola llamada, reutilizando convert_video.
    """
    # Archivo de entrada
    if not os.path.exists(f"app/{INPUT_VIDEO}"):
        raise HTTPException(status_code=404, detail=f"Video de entrada no encontrado en: app/{INPUT_VIDEO}")

    results = []
    
    # Iterar sobre cada perfil solicitado
    for profile in request.profiles:
        codec_key = profile.codec.lower()
        
        # Validacion de codec
        if codec_key not in CODEC_MAP:
            results.append({
                "profile": profile.output_prefix,
                "status": "skipped",
                "detail": f"Codec '{profile.codec}' no soportado."
            })
            continue

        params = CODEC_MAP[codec_key]
        
        # Construir el nombre del archivo de salida
        output_filename = f"{profile.output_prefix}_{profile.bitrate}_{codec_key}{params['extension']}"
        output_path = f"{OUTPUT_DIR}/{output_filename}"
        
        vcodec = params["vcodec"]
        
        # Construir los parametros extras para FFmpeg (bitrate y resolucion)
        extra_params = [
            '-b:v', profile.bitrate # Bitrate
        ]
        if profile.resolution:
            extra_params.extend(['-s', profile.resolution]) # Resolucion
        
        # Conversion
        success = convert_video(
            input_path=INPUT_VIDEO,
            output_path=output_path,
            vcodec=vcodec,
            extra_params=extra_params # Pasamos los parametros de bitrate/resolucion
        )
        
        # Registrar el resultado
        if success:
            results.append({
                "profile": profile.output_prefix,
                "status": "success",
                "codec": vcodec,
                "output": output_path
            })
        else:
            results.append({
                "profile": profile.output_prefix,
                "status": "failed",
                "detail": "Error en FFmpeg. Revisa los logs del contenedor 'api'."
            })

    # Retorno Final
    return {
        "status": "completed",
        "message": f"Encoding Ladder finalizado. {len(results)} perfiles procesados.",
        "results": results
    }