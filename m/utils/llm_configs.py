llm_configs = {
    "openai/gpt3.5": {
        "context_window_tokens": 4096,
        "max_output_tokens": 1024,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,  # Not required for remote models
        "minimum_gpu_required": None,  # Not required for remote models
        "required_disk_space": None,   # Not required for remote models
    },
    "openai/gpt3.5-turbo": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
    },
    "openai/gpt-4": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["everything", "reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
    },
    "openai/gpt-4-vision": {
        "context_window_tokens": 8192,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "vision", "coding", "translating"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
    },
    "anthropic/claude-1": {
        "context_window_tokens": 100000,
        "max_output_tokens": 2048,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
    },
    "anthropic/claude-2": {
        "context_window_tokens": 100000,
        "max_output_tokens": 4096,
        "expert_for": ["reasoning", "coding", "translating", "math"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
    },
    "groq/gpt3.5": {
        "context_window_tokens": 4000,
        "max_output_tokens": 1024,
        "expert_for": ["reasoning", "math", "coding"],
        "local": False,
        "minimum_ram_required": None,
        "minimum_gpu_required": None,
        "required_disk_space": None,
    },
    "ollama/minstral": {
        "context_window_tokens": 2048,
        "max_output_tokens": 1024,
        "expert_for": ["everything", "reasoning", "coding"],
        "local": True,
        "minimum_ram_required": 16,  # GB
        "minimum_gpu_required": False,
        "required_disk_space": 40,  # GB
    },
}
