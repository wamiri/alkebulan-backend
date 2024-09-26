from pathlib import Path

from pydantic.types import SecretStr
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.processes.connectors.local import (
    LocalConnectionConfig,
    LocalDownloaderConfig,
    LocalIndexerConfig,
    LocalUploaderConfig,
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig

from src.utils.config import get_env_var


async def run_pipeline():
    Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=LocalIndexerConfig(
            input_path=Path(get_env_var("LOCAL_FILE_INPUT_DIR"))
        ),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=SecretStr(get_env_var("UNSTRUCTURED_API_KEY")),
            partition_endpoint=get_env_var("UNSTRUCTURED_API_URL"),
            strategy="hi_res",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15,
            },
        ),
        uploader_config=LocalUploaderConfig(
            output_dir=get_env_var("LOCAL_FILE_OUTPUT_DIR")
        ),
    ).run()
