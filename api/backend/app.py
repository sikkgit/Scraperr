# STL
import uuid
import logging
from io import BytesIO
from openpyxl import Workbook

# PDM
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import docker
from api.backend.schemas import User

from api.backend.auth.auth_utils import get_current_user

client = docker.from_env()

# LOCAL
from api.backend.job import (
    average_elements_per_link,
    get_jobs_per_day,
    query,
    insert,
    delete_jobs,
    update_job,
)
from api.backend.models import (
    DownloadJob,
    GetStatistics,
    SubmitScrapeJob,
    DeleteScrapeJobs,
    RetrieveScrapeJobs,
    UpdateJobs,
)
from api.backend.auth.auth_router import auth_router
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(asctime)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

LOG = logging.getLogger(__name__)

app = FastAPI(title="api")
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/update", response_model=User)
async def update(update_jobs: UpdateJobs, user: User = Depends(get_current_user)):
    """Used to update jobs"""
    await update_job(update_jobs.ids, update_jobs.field, update_jobs.value)


@app.post("/api/submit-scrape-job")
async def submit_scrape_job(job: SubmitScrapeJob, background_tasks: BackgroundTasks):
    LOG.info(f"Recieved job: {job}")
    try:
        job.id = uuid.uuid4().hex

        if job.user:
            job_dict = job.model_dump()
            await insert(job_dict)

        return JSONResponse(content=f"Job queued for scraping: {job.id}")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/retrieve-scrape-jobs")
async def retrieve_scrape_jobs(retrieve: RetrieveScrapeJobs):
    LOG.info(f"Retrieving jobs for account: {retrieve.user}")
    try:
        results = await query({"user": retrieve.user})
        return JSONResponse(content=jsonable_encoder(results[::-1]))
    except Exception as e:
        LOG.error(f"Exception occurred: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


def clean_text(text: str):
    text = text.replace("\r\n", "\n")  # Normalize newlines
    text = text.replace("\n", "\\n")  # Escape newlines
    text = text.replace('"', '\\"')  # Escape double quotes
    return text


@app.post("/api/download")
async def download(download_job: DownloadJob):
    LOG.info(f"Downloading job with ids: {download_job.ids}")
    try:
        results = await query({"id": {"$in": download_job.ids}})

        flattened_results = []
        for result in results:
            for res in result["result"]:
                for url, elements in res.items():
                    for element_name, values in elements.items():
                        for value in values:
                            text = clean_text(value.get("text", ""))
                            flattened_results.append(
                                {
                                    "id": result.get("id", None),
                                    "url": url,
                                    "element_name": element_name,
                                    "xpath": value.get("xpath", ""),
                                    "text": text,
                                    "user": result.get("user", ""),
                                    "time_created": result.get("time_created", ""),
                                }
                            )

        # Create an Excel workbook and sheet
        workbook = Workbook()
        sheet = workbook.active
        assert sheet
        sheet.title = "Results"

        # Write the header
        headers = ["id", "url", "element_name", "xpath", "text", "user", "time_created"]
        sheet.append(headers)

        # Write the rows
        for row in flattened_results:
            sheet.append(
                [
                    row["id"],
                    row["url"],
                    row["element_name"],
                    row["xpath"],
                    row["text"],
                    row["user"],
                    row["time_created"],
                ]
            )

        # Save the workbook to a BytesIO buffer
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        _ = excel_buffer.seek(0)

        # Create the response
        response = StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
        return response

    except Exception as e:
        LOG.error(f"Exception occurred: {e}")
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/api/delete-scrape-jobs")
async def delete(delete_scrape_jobs: DeleteScrapeJobs):
    result = await delete_jobs(delete_scrape_jobs.ids)
    return (
        JSONResponse(content={"message": "Jobs successfully deleted."})
        if result
        else JSONResponse({"error": "Jobs not deleted."})
    )


@app.get("/api/logs")
async def get_own_logs():
    container_id = "scraperr_api"
    try:
        container = client.containers.get(container_id)
        log_stream = container.logs(stream=True, follow=True)

        def log_generator():
            try:
                for log in log_stream:
                    yield f"data: {log.decode('utf-8')}\n\n"
            except Exception as e:
                yield f"data: {str(e)}\n\n"

        return StreamingResponse(log_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/statistics/get-average-element-per-link")
async def get_average_element_per_link(get_statistics: GetStatistics):
    return await average_elements_per_link(get_statistics.user)


@app.post("/api/statistics/get-average-jobs-per-day")
async def average_jobs_per_day(get_statistics: GetStatistics):
    data = await get_jobs_per_day(get_statistics.user)
    return data
