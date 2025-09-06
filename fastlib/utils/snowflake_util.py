"""Snowflake utils to generate unique id"""

import time
import threading
from typing import Optional


class SnowflakeIDGenerator:
    """
    Snowflake ID Generator
    
    Snowflake ID structure (64 bits):
    - Sign bit: 1 bit, always 0
    - Timestamp: 41 bits, millisecond precision
    - Worker ID: 10 bits (5 bits datacenter ID + 5 bits machine ID)
    - Sequence number: 12 bits, auto-increment within the same millisecond
    
    Features:
    - Monotonically increasing
    - Globally unique
    - Distributed system support
    - High performance
    """

    def __init__(self, datacenter_id: int = 1, worker_id: int = 1, sequence: int = 0):
        """
        Initialize the Snowflake ID generator
        
        Args:
            datacenter_id: Datacenter ID (0-31)
            worker_id: Worker ID (0-31)
            sequence: Initial sequence number
            
        Raises:
            ValueError: If datacenter_id or worker_id is out of valid range
        """
        # Bit allocation
        self.TIMESTAMP_BITS = 41
        self.DATACENTER_ID_BITS = 5
        self.WORKER_ID_BITS = 5
        self.SEQUENCE_BITS = 12

        # Maximum values
        self.MAX_DATACENTER_ID = -1 ^ (-1 << self.DATACENTER_ID_BITS)
        self.MAX_WORKER_ID = -1 ^ (-1 << self.WORKER_ID_BITS)
        self.MAX_SEQUENCE = -1 ^ (-1 << self.SEQUENCE_BITS)

        # Shift offsets
        self.WORKER_ID_SHIFT = self.SEQUENCE_BITS
        self.DATACENTER_ID_SHIFT = self.SEQUENCE_BITS + self.WORKER_ID_BITS
        self.TIMESTAMP_LEFT_SHIFT = (
            self.SEQUENCE_BITS + self.WORKER_ID_BITS + self.DATACENTER_ID_BITS
        )

        # Validate parameters
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(
                f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}"
            )
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"Worker ID must be between 0 and {self.MAX_WORKER_ID}")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence

        # Epoch (2023-01-01 00:00:00 UTC)
        self.EPOCH = 1672531200000

        # Last timestamp used for ID generation
        self.last_timestamp = -1

        # Thread lock for thread safety
        self.lock = threading.Lock()

    def _get_timestamp(self) -> int:
        """
        Get current timestamp in milliseconds
        
        Returns:
            Current timestamp in milliseconds
        """
        return int(time.time() * 1000)

    def _wait_for_next_millis(self, last_timestamp: int) -> int:
        """
        Wait until the next millisecond
        
        Args:
            last_timestamp: Last timestamp used
            
        Returns:
            New timestamp in the next millisecond
        """
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp

    def generate_id(self) -> int:
        """
        Generate a Snowflake ID
        
        Returns:
            64-bit Snowflake ID
            
        Raises:
            RuntimeError: If clock moves backwards (clock drift detected)
        """
        with self.lock:
            timestamp = self._get_timestamp()

            # Check for clock drift
            if timestamp < self.last_timestamp:
                raise RuntimeError(
                    f"Clock moved backwards. Refusing to generate id for {self.last_timestamp - timestamp} milliseconds"
                )

            # Same millisecond
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                # Wait for next millisecond if sequence overflows
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                # Different millisecond, reset sequence
                self.sequence = 0

            self.last_timestamp = timestamp

            # Generate ID
            snowflake_id = (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_LEFT_SHIFT)
                | (self.datacenter_id << self.DATACENTER_ID_SHIFT)
                | (self.worker_id << self.WORKER_ID_SHIFT)
                | self.sequence
            )

            return snowflake_id

    def generate_id_str(self) -> str:
        """
        Generate a Snowflake ID as string
        
        Returns:
            Snowflake ID as string
        """
        return str(self.generate_id())

    def parse_id(self, snowflake_id: int) -> dict:
        """
        Parse a Snowflake ID into its components
        
        Args:
            snowflake_id: Snowflake ID to parse
            
        Returns:
            Dictionary containing parsed components:
            - timestamp: Original timestamp
            - datacenter_id: Datacenter ID
            - worker_id: Worker ID
            - sequence: Sequence number
            - datetime: Human-readable datetime string
        """
        timestamp = (snowflake_id >> self.TIMESTAMP_LEFT_SHIFT) + self.EPOCH
        datacenter_id = (
            snowflake_id >> self.DATACENTER_ID_SHIFT
        ) & self.MAX_DATACENTER_ID
        worker_id = (snowflake_id >> self.WORKER_ID_SHIFT) & self.MAX_WORKER_ID
        sequence = snowflake_id & self.MAX_SEQUENCE

        return {
            "timestamp": timestamp,
            "datacenter_id": datacenter_id,
            "worker_id": worker_id,
            "sequence": sequence,
            "datetime": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)
            ),
        }


# Global Snowflake ID generator instance
_snowflake_generator: Optional[SnowflakeIDGenerator] = None
_generator_lock = threading.Lock()


def get_snowflake_generator(
    datacenter_id: int = 1, worker_id: int = 1
) -> SnowflakeIDGenerator:
    """
    Get the global Snowflake ID generator instance (singleton pattern)
    
    Args:
        datacenter_id: Datacenter ID
        worker_id: Worker ID
        
    Returns:
        Snowflake ID generator instance
    """
    global _snowflake_generator

    if _snowflake_generator is None:
        with _generator_lock:
            if _snowflake_generator is None:
                _snowflake_generator = SnowflakeIDGenerator(datacenter_id, worker_id)

    return _snowflake_generator


def generate_snowflake_id() -> int:
    """
    Generate a Snowflake ID using default configuration
    
    Returns:
        64-bit Snowflake ID
    """
    return get_snowflake_generator().generate_id()


def generate_snowflake_id_str() -> str:
    """
    Generate a Snowflake ID as string using default configuration
    
    Returns:
        Snowflake ID as string
    """
    return get_snowflake_generator().generate_id_str()


def parse_snowflake_id(snowflake_id: int) -> dict:
    """
    Parse a Snowflake ID into its components
    
    Args:
        snowflake_id: Snowflake ID to parse
        
    Returns:
        Dictionary containing parsed components
    """
    return get_snowflake_generator().parse_id(snowflake_id)


# Convenience functions
def snowflake_id() -> int:
    """
    Convenience function for quick Snowflake ID generation
    
    Returns:
        64-bit Snowflake ID
    """
    return generate_snowflake_id()


def snowflake_id_str() -> str:
    """
    Convenience function for quick Snowflake ID generation as string
    
    Returns:
        Snowflake ID as string
    """
    return generate_snowflake_id_str()