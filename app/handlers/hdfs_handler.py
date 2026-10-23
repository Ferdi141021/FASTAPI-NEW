from fastapi import APIRouter, HTTPException
import subprocess

router = APIRouter(prefix="/hdfs", tags=["HDFS"])

@router.post("/upload-via-cli")
async def upload_via_cli(local_file: str, hdfs_dir: str = "/lab/day2/"):
    """
    Upload file ke HDFS dengan eksekusi command `hdfs dfs -put`.
    local_file = path file di host yang sudah di-mount ke /datasets di container namenode
    """
    try:
        # Jalankan command di dalam container namenode
        result = subprocess.run(
            [
                "docker", "exec", "namenode",
                "hdfs", "dfs", "-put", "-f",
                f"/datasets/{local_file}",   # path di container
                hdfs_dir
            ],
            capture_output=True,
            text=True,
            check=True
        )

        return {
            "status": "success",
            "local_file": local_file,
            "hdfs_path": f"hdfs://namenode:8020{hdfs_dir}{local_file}"
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exec hdfs: {e.stderr.strip()}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
