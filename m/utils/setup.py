import os
from pathlib import Path
from typing import Dict
import json
import click
#from getpass import getpass
from .storage import EncryptedJSONStorage
from .system import System
from .docker_helper import DockerHelper

class Setup:
    def __init__(self):
        """Initialize the Setup class."""
        self.home_settings_path = Path.home() / ".m" / "settings.json"
        self.local_settings_path = Path.cwd() / ".m.json"
        self.encrypted_storage = EncryptedJSONStorage(str(self.home_settings_path))
        self.system = System()
        self.docker_helper = DockerHelper()
        self.docker_image_ollama = "ollama/ollama"
        self.docker_image_litellm = "litellm/litellm"
        self.min_required_ram = 16  # GB
        self.min_required_disk = 100  # GB
        self.local_model = "ollama/minstral"
        self.api_keys = {"Anthropic": None, "OpenAI": None, "Groq": None}
        self.local_settings = {}

        self.settings = self.load_settings()

    def load_settings(self) -> Dict:
        """Load settings from home or local files."""
        if self.home_settings_path.exists():
            settings = self.encrypted_storage.load()
        else:
            settings = {}

        if self.local_settings_path.exists():
            with open(self.local_settings_path, 'r') as file:
                local_settings = json.load(file)
            settings.update(local_settings)

        return settings

    def save_settings(self, path=None):
        """Save settings to the specified path."""
        if not path:
            path = self.home_settings_path

        self.encrypted_storage.save(self.settings)

    def check_docker_requirements(self):
        """Check if Docker is installed and running."""
        docker_status = self.docker_helper.check_docker_status()

        if docker_status == "not installed":
            click.echo("Docker is not installed. Please install Docker and rerun 'm'.")
            exit(1)

        if docker_status == "not running":
            click.echo("Docker is not running. Please start Docker and rerun 'm'.")
            exit(1)

    def check_llm_settings(self):
        """Check and configure LLM settings."""
        llm_available = "LLM" in self.settings

        if not llm_available:
            specs = self.system.get_specs()
            ram_ok = specs["memory"]["total"] >= self.min_required_ram
            disk_ok = specs["disk"]["free"] >= self.min_required_disk

            click.echo(f"System specs: RAM: {specs['memory']['total']} GB, Free Disk Space: {specs['disk']['free']} GB")

            if ram_ok and disk_ok:
                self.check_docker_requirements()
                llm_choice = click.prompt(
                    "Do you prefer to use only local LLMs, a combination of remote and local, or just remote?",
                    type=click.Choice(['local', 'remote', 'remote & local']),
                    default="remote & local"
                )
                if llm_choice in ["local", "remote & local"]:
                    click.echo("Setting up local LLMs...")
                    self.setup_local_models()
                if llm_choice in ["remote", "remote & local"]:
                    click.echo("Setting up remote LLMs...")
                    self.setup_remote_models()
            else:
                click.echo("Your system does not meet the minimum requirements for local models.")
                self.setup_remote_models()

        if "LLM" not in self.settings:
            click.echo("At least one LLM API key is required.")
            exit(1)

    def setup_local_models(self):
        """Set up local models using Docker and Ollama."""
        # Start Ollama if not already running
        click.echo("Checking or starting Ollama Docker image...")
        if not self.docker_helper.image_exists(self.docker_image_ollama):
            self.docker_helper.pull_image(self.docker_image_ollama)

        if not self.docker_helper.container_exists(self.docker_image_ollama):
            self.docker_helper.create_instance(name=self.docker_image_ollama)

        click.echo("Downloading Minstral model...")
        # Simulate model download and configuration
        self.settings["LLM"] = self.settings.get("LLM", {})
        self.settings["LLM"]["local"] = self.settings["LLM"].get("local", {})
        self.settings["LLM"]["local"]["ollama"] = {"model": self.local_model}

    def setup_remote_models(self):
        """Set up remote models with API keys."""
        click.echo("Please enter your API keys for remote LLMs:")
        for key in self.api_keys:
            self.settings["LLM"] = self.settings.get("LLM", {})
            self.settings["LLM"]["remote"] = self.settings["LLM"].get("remote", {})
            self.settings["LLM"]["remote"][key] = click.prompt(
                f"Enter {key} API Key",
                default=self.settings["LLM"]["remote"].get(key, "")
            )

    def run_initial_setup(self):
        """Run the initial setup."""
        click.echo("Running initial setup...")
        self.check_llm_settings()
        self.save_settings()

    def re_run_setup(self, mode: str = "global"):
        """Rerun setup steps.

        Args:
            mode (str, optional): Setup mode ('global' or 'local'). Defaults to 'global'.
        """
        click.echo(f"Re-running setup in {mode} mode...")
        self.check_llm_settings()
        if mode == "local":
            with open(self.local_settings_path, 'w') as file:
                json.dump(self.settings, file, indent=4)
        else:
            self.save_settings()

    def handle_setup_command(self, command: str):
        """Handle setup commands ('setup' and 'setup local').

        Args:
            command (str): Setup command.
        """
        if command == "setup local":
            self.re_run_setup(mode="local")
        elif command == "setup":
            self.re_run_setup(mode="global")
        else:
            click.echo(f"Unknown command: {command}")

# Example usage
if __name__ == "__main__":
    setup = Setup()
    setup.run_initial_setup()
