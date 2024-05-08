import click
from pydantic import BaseModel
from instructor import Instruct
from typing import Any, Dict, List, Union, Optional
from .setup import Setup
from .docker_helper import DockerHelper
import tiktoken

class Brain:
    def __init__(self):
        """Initialize the Brain class."""
        click.echo("Initializing Brain...")
        self.setup = Setup()
        self.settings = self.setup.load_settings()
        self.docker_helper = DockerHelper()
        self.llm_configs = self.setup.llm_configs

        self.instructors = self.init_instructors()
        self.start_local_model_if_available()

    def init_instructors(self) -> Dict[str, Instruct]:
        """Initialize the instructor clients based on available API keys."""
        instructors = {}

        llm_settings = self.settings.get("LLM", {})
        remote_llms = llm_settings.get("remote", {})

        # Initialize remote instructors
        for full_name, api_key in remote_llms.items():
            if api_key:
                provider, _ = full_name.split("/")
                instructors[full_name] = Instruct(api_key=api_key, provider=provider.lower())

        # Add all local models that meet the system requirements
        local_llms = llm_settings.get("local", {})
        for full_name in local_llms.keys():
            if full_name in self.llm_configs and self.llm_configs[full_name]["local"]:
                instructors[full_name] = Instruct(api_key=None, provider="ollama")

        return instructors

    def start_local_model_if_available(self):
        """Check, build, and run the local Ollama Docker instance if available."""
        llm_settings = self.settings.get("LLM", {}).get("local", {})

        if llm_settings:
            click.echo("Local models available. Checking Ollama Docker instance...")
            if not self.docker_helper.container_exists(self.setup.local_container_name):
                click.echo("Starting Ollama Docker instance...")
                self.docker_helper.create_instance(name=self.setup.local_container_name, network="bridge")

            click.echo("Ensuring local models are available...")
            # Add your logic to ensure models are downloaded and available

    def count_tokens(self, prompt: str, model: str = "gpt-4") -> int:
        """Count tokens in the given prompt based on GPT-4.

        Args:
            prompt (str): The input prompt.
            model (str, optional): Model for counting tokens. Defaults to "gpt-4".

        Returns:
            int: The count of tokens.
        """
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(prompt))

    def choose_best_instructor(self, prompt: str, category: Optional[str] = "everything") -> Optional[Instruct]:
        """Choose the best instructor for the given prompt and category.

        Args:
            prompt (str): Input prompt string.
            category (Optional[str], optional): Category of the task. Defaults to "everything".

        Returns:
            Optional[Instruct]: The most suitable instructor or None.
        """
        token_count = self.count_tokens(prompt)
        best_instructor = None
        best_match_score = float("-inf")

        for name, config in self.llm_configs.items():
            if name in self.instructors:
                supports_category = category in config["expert_for"]
                within_token_limit = token_count + config["max_output_tokens"] <= config["context_window_tokens"]

                if supports_category and within_token_limit:
                    score = config["context_window_tokens"] - token_count  # Prioritize by remaining tokens
                    if score > best_match_score:
                        best_match_score = score
                        best_instructor = self.instructors[name]

        if best_instructor:
            click.echo(f"Selected instructor: {name}")
        else:
            click.echo("No suitable instructor found.")

        return best_instructor

    def prompt(self, prompt: str, output_schema: BaseModel, llm: str = None, category: Optional[str] = "everything") -> Union[BaseModel, None]:
        """Standardize calls to LLMs using a single prompt method.

        Args:
            prompt (str): Input prompt string.
            output_schema (BaseModel): Pydantic model to enforce the output schema.
            llm (str, optional): Specific LLM name to use. Defaults to None.
            category (Optional[str], optional): Category of the task. Defaults to "everything".

        Returns:
            Union[BaseModel, None]: The validated output schema instance or None.
        """
        if llm and llm.lower() in self.instructors:
            click.echo(f"Using specified LLM: {llm}")
            instructor = self.instructors[llm.lower()]
        else:
            instructor = self.choose_best_instructor(prompt, category)

        if not instructor:
            click.echo("No suitable LLM found.")
            return None

        response = instructor(prompt)
        try:
            validated_output = output_schema.parse_obj(response)
            return validated_output
        except Exception as e:
            click.echo(f"Error validating response: {e}")
            return None

# Example Pydantic output schema
class ExampleOutputSchema(BaseModel):
    summary: str
    points: List[str]

# Example usage
if __name__ == "__main__":
    brain = Brain()
    prompt_str = "Summarize the latest AI research papers."
    schema = ExampleOutputSchema

    result = brain.prompt(prompt_str, schema)
    if result:
        click.echo(result.json(indent=4))
