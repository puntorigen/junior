import os, time
from pathlib import Path
from typing import Dict
import json
#import click
from junior.utils.storage import EncryptedJSONStorage
from junior.utils.system_helper import SystemInfo
from junior.utils.docker_helper import DockerHelper
from junior.utils.llm_configs import llm_configs
from junior.cli_manager import CLIManager
click = CLIManager(domain="setup")
class Setup:
    def __init__(self, language="en"):
        """Initialize the Setup class."""
        self.home_settings_path = Path.home() / ".junior" / "settings.json"
        self.local_settings_path = Path.cwd() / ".junior.json"
        self.encrypted_storage = EncryptedJSONStorage(str(self.home_settings_path))
        self.system = SystemInfo()
        self.docker_image_ollama = "ollama/ollama"
        self.local_container_name = "ollama_server"
        click.setup_language(language=language)
        self.llm_configs = llm_configs
        self.settings = self.load_settings()
        self.docker_helper = DockerHelper()
        if self.docker_helper.is_docker_running == False:
            click.warn_("Docker is not running. Please start Docker and rerun 'junior' if you want to use local LLMs.")

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
            click.echo("Docker is not installed. Please install Docker and rerun 'junior'.")
            exit(1)

        if docker_status == "not running":
            click.echo("Docker is not running. Please start Docker and rerun 'junior'.")
            exit(1)

    def check_llm_settings(self):
        """Check and configure LLM settings."""
        # remove 'local' models if Docker is not running
        if not self.docker_helper.is_docker_running:
            if self.settings and "LLM" in self.settings and "local" in self.settings["LLM"]:
                self.settings["LLM"].pop("local", None)

        # if self.settings["LLM"]["local"] is not empty and docker is running, setup local models if needed
        if self.settings and "LLM" in self.settings and "local" in self.settings["LLM"]:
            self.setup_local_models()

        # check if we have any LLMs available
        llm_available = self.settings["LLM"] if self.settings and "LLM" in self.settings else None

        if not llm_available:
            specs = self.system.get_basic_info()
            ram_ok = specs["memory"]["total"] >= 16
            disk_ok = specs["disk"]["free"] >= 100

            if ram_ok and disk_ok:
                state = self.docker_helper.check_docker_status()
                if state == "running":
                    llm_choice = click.select(
                        "Do you prefer to use only local LLMs, a combination of remote and local, or just remote?",
                        choices=['local', 'remote', 'remote and local'],
                        default="remote and local"
                    )
                    if llm_choice in ["local", "remote and local"]:
                        click.echo("Setting up *local* LLMs...")
                        self.setup_local_models()
                    if llm_choice in ["remote", "remote and local"]:
                        click.echo("Setting up *remote* LLMs...")
                        self.setup_remote_models()
                elif state == "not installed" or state == "not running":
                    click.echoDim("Docker is not installed or running. Please install Docker and rerun 'junior' if you want to use local LLMs.")
                    click.echo("Setting up *remote* LLMs...")
                    self.setup_remote_models()
            else:
                click.echoDim("System specs: RAM: {total} GB, Free Disk Space: {free} GB",total=specs['memory']['total'],free=specs['disk']['free'])
                click.echo("Your system does not meet the minimum requirements for *local* models.")
                self.setup_remote_models()

        if "LLM" not in self.settings:
            click.echo("At least one LLM API key is required.")
            exit(1)

    def local_llm_models_installed(self):
        """Check which local LLM models are installed."""
        query = self.docker_helper.execute_command(f"ollama list")
        # Splitting the query into lines
        lines = query.strip().split('\n')
        # Extract the model names from each line, except the header
        model_names = []
        for line in lines[1:]:  # Start from 1 to skip the header
            model_name = line.split()[0]  # Split the line and get the first element
            model_names.append(model_name)
        
        return model_names

    def parse_last_pull_status(self, output):
        """Parse the last line of docker pull output and extract details including byte size."""
        import re
        # Split the output into lines
        lines = output.strip().split('\n')
        
        # Get the last non-empty line
        last_line = lines[-1]
        
        # Regular expression to parse the line including byte size
        pattern = r"(pulling\s+([0-9a-f]+))\.\.\.\s+(\d+)%.*?(\d+\s+[BKMG]B)"
        match = re.search(pattern, last_line)
        
        if match:
            # Extract relevant parts
            message = match.group(1)  # 'pulling xxx'
            percentage = int(match.group(3))  # Percentage as integer
            byte_size = match.group(4)  # Byte size as string
            return {
                "message": message,
                "percentage": percentage,
                "byte_size": byte_size
            }
        else:
            return None
        
    def setup_local_models(self):
        """Set up local models using Docker and Ollama."""
        specs = self.system.get_basic_info()
        click.debug_("System specs: RAM: {total} GB, Free Disk Space: {free} GB",total=specs['memory']['total'],free=specs['disk']['free'])

        # Ensure Docker requirements
        self.check_docker_requirements()

        # Start Ollama server if not already running
        if not self.docker_helper.container_exists(self.local_container_name):
            click.echoDim("Starting Ollama Docker instance...")
            self.docker_helper.create_instance(image=self.docker_image_ollama, command="", name=self.local_container_name, network="bridge")
        else:
            click.debug_("Searching Ollama Docker instance...")
            state = self.docker_helper.search_and_start_container(self.local_container_name)
            if not state:
                click.warn_("Error: Could not find the existing Ollama Docker instance.")
                exit(1)
            if state == "started":
                click.echoDim("Starting Ollama server. Waiting 20 seconds for it to be ready...")
                time.sleep(20)

        # Configure and download local models
        for name, config in self.llm_configs.items():
            if config["local"]:
                meets_memory = specs["memory"]["total"] >= (config["minimum_ram_required"] or 0)
                meets_disk_space = specs["disk"]["free"] >= (config["required_disk_space"] or 0)
                meets_gpu = (not config["minimum_gpu_required"] or specs["gpu"])

                if meets_memory and meets_disk_space and meets_gpu:
                    just_model = name.replace("ollama/","")
                    installed = self.local_llm_models_installed()
                    self.settings["LLM"] = self.settings.get("LLM", {})
                    self.settings["LLM"]["local"] = self.settings["LLM"].get("local", {})
                    if just_model not in installed:
                        click.echo("Downloading and configuring local model '{name}'...",name=just_model)
                        try:
                            from rich.progress import track
                            for output in track(self.docker_helper.execute_command_stream(f"ollama pull {just_model}"), description=f"Downloading {just_model}..."):
                                #print(output, end="")
                                # show custom progress bar updates
                                try:
                                    data = self.parse_last_pull_status(output)
                                    if data:
                                        print(data)
                                except Exception as e:
                                    print(e)
                                    
                            self.settings["LLM"]["local"][name] = {"model": just_model}                            
                        except Exception as e:
                            click.warn_("An error ocurred downloading model: {model}",model=just_model)
                            # remove the model from the settings if failed downloading and exists on settings
                            if name in self.settings["LLM"]["local"]:
                                self.settings["LLM"]["local"].pop(name)

                else:
                    click.echo("Insufficient system resources for local model '{name}'.",name=name)

    def setup_remote_models(self):
        """Set up remote models with API keys."""
        click.echo("Please enter your *API keys* for *remote* LLMs:")
        for name in ["Anthropic", "OpenAI", "Groq"]:
            self.settings["LLM"] = self.settings.get("LLM", {})
            self.settings["LLM"]["remote"] = self.settings["LLM"].get("remote", {})
            self.settings["LLM"]["remote"][name] = click.prompt(
                ("Enter *{name}* API Key",{ "name":name }),
                default=self.settings["LLM"]["remote"].get(name, "")
            )
            # if self.settings["LLM"]["remote"][name] empty, remove it
            if not self.settings["LLM"]["remote"][name]:
                self.settings["LLM"]["remote"].pop(name)
        # if no remote LLMs, remove the key 'remote'
        if not self.settings["LLM"]["remote"]:
            self.settings["LLM"].pop("remote")

    def run_initial_setup(self):
        """Run the initial setup."""
        # if self.settings has no keys, run initial setup
        if not self.settings:
            click.debug_("Running initial setup...")
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
