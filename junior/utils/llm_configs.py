from junior.utils.system_helper import SystemInfo

llm_configs = {
    "openai/gpt3.5": {
        "context_window_tokens": 4096,
        "max_output_tokens": 1024,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,  # Not required for remote models
        "minimum_gpu_required": None,  # Not required for remote models
        "required_disk_space": None,   # Not required for remote models
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 6000,
            "tokens_per_day": 864000,
        },
        "fallback": "openai/gpt3.5-turbo"
    },
    "openai/gpt3.5-turbo": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 6000,
            "tokens_per_day": 864000,
        },
        "fallback": "openai/gpt-4"
    },
    "openai/gpt-4": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["everything", "reasoning", "coding", "translating", "math"],
        "languages": ["en","es","fr"],
        "coding": ["javascript", "typescript", "python", "java", "c++", "c#", "rust", "go"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 6000,
            "tokens_per_day": 864000,
        },
        "fallback": None
    },
    "openai/gpt-4-vision": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "vision", "coding", "translating"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 6000,
            "tokens_per_day": 864000,
        },
        "fallback": None
    },
    "anthropic/claude-1": {
        "context_window_tokens": 100000,
        "max_output_tokens": 2048,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 10000,
            "tokens_per_day": 1200000,
        },
        "fallback": "anthropic/claude-2"
    },
    "anthropic/claude-2": {
        "context_window_tokens": 100000,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 10000,
            "tokens_per_day": 1200000,
        },
        "fallback": None
    },
    "groq/llama3-70b-8192": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "math", "coding"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 6000,
            "tokens_per_day": 864000,
        },
        "fallback": "groq/llama3-8b-8192"
    },
    "groq/llama3-8b-8192": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "math", "coding"],
        "languages": ["en", "fr", "de", "es"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 30000,
            "tokens_per_day": 1000000,
        },
        "fallback": "groq/mixtral-8x7b-32768"
    },
    "groq/mixtral-8x7b-32768": {
        "context_window_tokens": 32768,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "math", "coding"],
        "languages": ["en", "fr", "de", "es"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
        "limits": {
            "requests_per_minute": 30,
            "requests_per_day": 14400,
            "tokens_per_minute": 5000,
            "tokens_per_day": 864000,
        },
        "fallback": None
    },
    "ollama/mistral:instruct": {
        "context_window_tokens": 32000,
        "max_output_tokens": 8192,
        "expert_for": ["everything", "reasoning", "coding"],
        "languages": ["en"],
        "local": True,
        "minimum_ram_required": 16,  # GB
        "minimum_gpu_required": False,
        "required_disk_space": 4.1,  # GB
        "limits": {
            "requests_per_minute": None,
            "requests_per_day": None,
            "tokens_per_minute": None,
            "tokens_per_day": None,
        },
        "fallback": "ollama/llama3:instruct"
    },
    "ollama/llama3:instruct": {
        "context_window_tokens": 8192,
        "max_output_tokens": 2048,
        "expert_for": ["everything", "reasoning", "coding"],
        "local": True,
        "minimum_ram_required": 16,  # GB
        "minimum_gpu_required": False,
        "required_disk_space": 4.7,  # GB
        "limits": {
            "requests_per_minute": None,
            "requests_per_day": None,
            "tokens_per_minute": None,
            "tokens_per_day": None,
        },
        "fallback": "ollama/phi3:instruct"
    },
    "ollama/phi3:instruct": {
        "context_window_tokens": 128000,
        "max_output_tokens": 2048,
        "expert_for": ["coding", "python"],
        "local": True,
        "minimum_ram_required": 16,  # GB
        "minimum_gpu_required": False,
        "required_disk_space": 2.3,  # GB
        "limits": {
            "requests_per_minute": None,
            "requests_per_day": None,
            "tokens_per_minute": None,
            "tokens_per_day": None,
        },
        "fallback": None
    },
}

# overwrite the local flag based on the system info
if SystemInfo.is_silicon_mac():
    llm_configs["ollama/phi3:instruct"]["minimum_ram_required"] = 8
    llm_configs["ollama/mistral:instruct"]["minimum_ram_required"] = 8
