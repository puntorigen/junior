import os
from pathlib import Path
from typing import Dict
import json
#import click
from .storage import EncryptedJSONStorage
from .system_helper import SystemInfo
from .docker_helper import DockerHelper
from .llm_configs import llm_configs
from ..cli_manager import CLIManager
click = CLIManager(domain="setup")
class Setup:
    def __init__(self, language="en"):
        """Initialize the Setup class."""
        self.home_settings_path = Path.home() / ".m" / "settings.json"
        self.local_settings_path = Path.cwd() / ".m.json"
        self.encrypted_storage = EncryptedJSONStorage(str(self.home_settings_path))
        self.system = SystemInfo()
        self.docker_helper = DockerHelper()
        self.docker_image_ollama = "ollama/ollama"
        self.local_container_name = "ollama_server"
        click.setup_language(language=language)
        self.llm_configs = llm_configs
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
            specs = {
                "memory":self.system.get_memory_info(),
                "disk":self.system.get_disk_info()
            }
            ram_ok = specs["memory"]["total"] >= 16
            disk_ok = specs["disk"]["free"] >= 100

            click.echo("System specs: RAM: {total} GB, Free Disk Space: {free} GB",total=specs['memory']['total'],free=specs['disk']['free'])

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
        specs = {
            "memory":self.system.get_memory_info(),
            "disk":self.system.get_disk_info()
        }
        click.echo(f"System specs: RAM: {specs['memory']['total']} GB, Free Disk Space: {specs['disk']['free']} GB")

        # Ensure Docker requirements
        self.check_docker_requirements()

        # Start Ollama server if not already running
        if not self.docker_helper.container_exists(self.local_container_name):
            click.echo("Starting Ollama Docker instance...")
            self.docker_helper.create_instance(name=self.local_container_name, network="bridge")

        # Configure and download local models
        for name, config in self.llm_configs.items():
            if config["local"]:
                meets_memory = specs["memory"]["total"] >= (config["minimum_ram_required"] or 0)
                meets_disk_space = specs["disk"]["free"] >= (config["required_disk_space"] or 0)
                meets_gpu = (not config["minimum_gpu_required"] or specs["gpu"])

                if meets_memory and meets_disk_space and meets_gpu:
                    click.echo(f"Downloading and configuring local model '{name}'...")
                    # Simulate model download and configuration
                    self.settings["LLM"] = self.settings.get("LLM", {})
                    self.settings["LLM"]["local"] = self.settings["LLM"].get("local", {})
                    self.settings["LLM"]["local"][name] = {"model": name}
                else:
                    click.echo(f"Insufficient system resources for local model '{name}'.")

    def setup_remote_models(self):
        """Set up remote models with API keys."""
        click.echo("Please enter your API keys for remote LLMs:")
        for name in ["Anthropic", "OpenAI", "Groq"]:
            self.settings["LLM"] = self.settings.get("LLM", {})
            self.settings["LLM"]["remote"] = self.settings["LLM"].get("remote", {})
            self.settings["LLM"]["remote"][name] = click.prompt(
                ("Enter {name} API Key",{ "name":name }),
                default=self.settings["LLM"]["remote"].get(name, "")
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
            click.echo("Unknown command: {command}",command=command)

# Example usage
if __name__ == "__main__":
    setup = Setup()
    setup.run_initial_setup()
