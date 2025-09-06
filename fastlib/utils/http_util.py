"""
HTTP utility functions for making synchronous and asynchronous HTTP requests.

This module provides a unified interface for HTTP operations using httpx,
with proper error handling, timeout configuration, and retry logic.
"""

import asyncio
import os
import time
import uuid
from typing import Any, Dict, Optional

import httpx
from loguru import logger



class HTTPError(Exception):
    """Custom exception for HTTP-related errors."""

    def __init__(self, status_code: int, message: str, url: str):
        self.status_code = status_code
        self.message = message
        self.url = url
        super().__init__(f"HTTP {status_code}: {message} for {url}")


def _create_timeout(timeout: float = 10.0) -> httpx.Timeout:
    """Create a timeout configuration for HTTP requests."""
    return httpx.Timeout(timeout, connect=5.0)


def _handle_response(response: httpx.Response, url: str) -> Any:
    """Handle HTTP response and raise appropriate exceptions."""
    if response.status_code == 200:
        return response.json()

    logger.error(f"HTTP request failed: {response.status_code} for {url}")
    raise HTTPError(
        status_code=response.status_code,
        message=f"Request failed with status {response.status_code}",
        url=url,
    )


async def async_http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 10.0,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Make an asynchronous HTTP GET request.

    Args:
        url: The URL to make the request to
        params: Query parameters to include in the request
        timeout: Request timeout in seconds
        headers: Optional headers to include in the request

    Returns:
        The JSON response from the server

    Raises:
        HTTPError: If the request fails
        httpx.RequestError: If there's a network error
    """
    timeout_config = _create_timeout(timeout)
    start_time = time.time()

    async with httpx.AsyncClient(timeout=timeout_config) as client:
        response = await client.get(url=url, params=params, headers=headers)
        duration = time.time() - start_time

        # Log the API call
        logger.log_api_call("GET", url, response.status_code, duration)

        return _handle_response(response, url)


def http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 10.0,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Make a synchronous HTTP GET request.

    Args:
        url: The URL to make the request to
        params: Query parameters to include in the request
        timeout: Request timeout in seconds
        headers: Optional headers to include in the request

    Returns:
        The JSON response from the server

    Raises:
        HTTPError: If the request fails
        httpx.RequestError: If there's a network error
    """
    timeout_config = _create_timeout(timeout)
    start_time = time.time()

    with httpx.Client(timeout=timeout_config) as client:
        response = client.get(url=url, params=params, headers=headers)
        duration = time.time() - start_time

        # Log the API call
        logger.log_api_call("GET", url, response.status_code, duration)

        return _handle_response(response, url)


def http_post(
    url: str, data: Any, headers: Optional[Dict[str, Any]] = None, timeout: float = 10.0
) -> Any:
    """
    Make a synchronous HTTP POST request.

    Args:
        url: The URL to make the request to
        data: The data to send in the request body
        headers: Optional headers to include in the request
        timeout: Request timeout in seconds

    Returns:
        The JSON response from the server

    Raises:
        HTTPError: If the request fails
        httpx.RequestError: If there's a network error
    """
    timeout_config = _create_timeout(timeout)
    start_time = time.time()

    with httpx.Client(timeout=timeout_config) as client:
        response = client.post(url=url, json=data, headers=headers)
        duration = time.time() - start_time

        # Log the API call
        logger.log_api_call("POST", url, response.status_code, duration)

        return _handle_response(response, url)


async def async_http_post(
    url: str,
    data: Any,
    headers: Optional[Dict[str, Any]] = None,
    timeout: float = 10.0,
    max_retries: int = 3,
    retry_delay: float = 0.5,
) -> Any:
    """
    Make an asynchronous HTTP POST request with retry logic.

    Args:
        url: The URL to make the request to
        data: The data to send in the request body
        headers: Optional headers to include in the request
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        The JSON response from the server

    Raises:
        HTTPError: If the request fails after all retries
        httpx.RequestError: If there's a network error
    """
    timeout_config = _create_timeout(timeout)

    async with httpx.AsyncClient(timeout=timeout_config) as client:
        for attempt in range(1, max_retries + 1):
            try:
                start_time = time.time()
                response = await client.post(url=url, json=data, headers=headers)
                duration = time.time() - start_time

                # Log the API call
                logger.log_api_call("POST", url, response.status_code, duration)

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(
                        f"HTTP POST failed (attempt {attempt}/{max_retries}): "
                        f"{response.status_code} for {url}"
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay)
                    else:
                        raise HTTPError(
                            status_code=response.status_code,
                            message=f"Request failed after {max_retries} attempts",
                            url=url,
                        )
            except httpx.RequestError as e:
                logger.error(f"Network error on attempt {attempt}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                else:
                    raise HTTPError(
                        status_code=0,
                        message=f"Network error after {max_retries} attempts: {str(e)}",
                        url=url,
                    ) from e

    raise HTTPError(
        status_code=0,
        message=f"Failed to fetch data from {url} after {max_retries} attempts",
        url=url,
    )


def download_file(
    file_url: str, directory_path: str, timeout: int = 60, verify_ssl: bool = True
) -> Optional[str]:
    """
    Download a file from a URL to a local directory.

    Args:
        file_url: The URL of the file to download
        directory_path: The directory to save the file in
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates

    Returns:
        The path to the downloaded file, or None if download failed
    """
    # Extract file extension from URL
    file_extension = file_url.split(".")[-1].split("?")[0]  # Remove query params
    random_filename = f"{uuid.uuid4()}.{file_extension}"

    # Create directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, random_filename)

    try:
        with httpx.Client(timeout=timeout, verify=verify_ssl) as client:
            with client.stream("GET", file_url) as response:
                if response.status_code == 200:
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            file.write(chunk)
                    logger.info(f"Successfully downloaded file to {file_path}")
                    return file_path
                else:
                    logger.error(
                        f"Download failed with status code: {response.status_code}"
                    )
                    return None
    except httpx.TimeoutException:
        logger.error("Download request timed out")
        return None
    except httpx.RequestError as e:
        logger.error(f"Download request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during download: {e}")
        return None


# Backward compatibility functions
async def async_http_post_legacy(url: str, params: dict) -> Any:
    """
    Legacy async HTTP POST function for backward compatibility.

    This function maintains the old interface but uses the new implementation.
    """
    return await async_http_post(url=url, data=params)
