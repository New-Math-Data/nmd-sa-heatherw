"""Bedrock service — embedding generation and field extraction via AWS Bedrock."""

import json
import logging
from typing import Any

import boto3

logger = logging.getLogger(__name__)


class BedrockService:
    """Service for interacting with AWS Bedrock models.

    This class provides methods for generating vector embeddings and extracting
    structured fields from document content using AWS Bedrock foundation models.
    """

    def __init__(self, region: str = "us-west-2", profile: str | None = None) -> None:
        """Initialize the Bedrock service.

        Args:
            region: AWS region where Bedrock is available (e.g. "us-west-2").
            profile: Optional AWS profile name for credential resolution.
        """
        self.region = region
        self.profile = profile

    def _get_client(self):
        """Create a bedrock-runtime client with optional profile."""
        session = boto3.Session(
            region_name=self.region,
            profile_name=self.profile,
        )
        return session.client("bedrock-runtime")

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a 1024-dimensional vector embedding for the given text.

        Uses Amazon Titan Embeddings V2 via the Bedrock Runtime invoke_model API.

        Args:
            text: The input text to embed. Titan V2 supports up to 8,192 tokens.

        Returns:
            A list of 1024 floats representing the text embedding vector.
        """
        client = self._get_client()

        request_body = json.dumps({
            "inputText": text,
            "dimensions": 1024,
            "normalize": True,
        })

        response = client.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            contentType="application/json",
            accept="application/json",
            body=request_body,
        )

        response_body = json.loads(response["body"].read())
        embedding: list[float] = response_body["embedding"]

        logger.info("Generated embedding with %d dimensions", len(embedding))
        return embedding

    async def extract_fields(
        self, content: str, fields: list[str]
    ) -> dict[str, Any]:
        """Extract structured fields from document content using Claude via Bedrock.

        Args:
            content: The document text to extract fields from.
            fields: List of field names to extract (e.g. ["title", "author", "date"]).

        Returns:
            A dictionary mapping each requested field name to its extracted value,
            or None if the field was not found in the content.
        """
        client = self._get_client()

        fields_str = ", ".join(fields)
        prompt = (
            f"Extract the following fields from the document content below: {fields_str}\n\n"
            f"Document content:\n{content}\n\n"
            "Return ONLY a valid JSON object mapping each field name to its extracted value. "
            "If a field cannot be found in the content, set its value to null. "
            "Do not include any other text or explanation."
        )

        request_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        })

        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=request_body,
        )

        response_body = json.loads(response["body"].read())

        # Parse Claude's response — extract the text content
        response_text = response_body["content"][0]["text"]

        # Parse the JSON from Claude's response
        extracted: dict[str, Any] = json.loads(response_text)

        # Ensure all requested fields are present (set to None if missing)
        for field in fields:
            if field not in extracted:
                extracted[field] = None

        logger.info("Extracted %d fields from document", len(extracted))
        return extracted
