"""Utility functions for the CV MCP server."""

import os
import yaml
from loguru import logger


def load_prompt(prompt_name: str) -> dict:
    """Load complete prompt data from the prompts directory.

    Args:
        prompt_name: Name of the prompt file (without .yaml extension)

    Returns:
        dict: The complete prompt data

    Raises:
        FileNotFoundError: If the prompt file is not found
        yaml.YAMLError: If the YAML file is malformed
    """
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
    prompt_file = os.path.join(prompts_dir, f"{prompt_name}.yaml")

    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML in '{prompt_file}': {e}")
        raise