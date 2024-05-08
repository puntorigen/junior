Example Processing Sequence for CLI
current folder: 
/Documents/code/m
- user issues: p "refactor to typescript"

0) check if we have the CLI setup: 
    - Check if we have a file on the user homedir .m/settings.json. Read it if so.
    - Check if a file named .m.json exists on current folder. If we do, overwrite general settings with the ones here.
    - Check if we have any LLM APIs on our settings. 
        - if we don't, check user system specs to see if he can run an LLM locally
            - test if user has enought RAM and disk for local models such as Minstral 8B
            - test if user has 'docker' installed; we need it for litellm
            - if the test pass, ask the user if he would prefer to use only local LLMs, a combination of remote and local, or just remote.
        - if user doesn't have enought specs, request supported LLMs API keys available: Anthropic, OpenAI, Groq. At least one has to be set up, but best to have them all. Save them on .m/settings.json (encrypted)
        - if user has sufficient specs, but doesn't have 'docker', request user to install it first and re-run 'm'.
        - if user has sufficient specs and 'docker' installed but not running, request user to run the docker server and re-run 'm'.
        - if user has sufficient specs and 'docker' running:
            - if the user requested to use 'local' or 'remote & local' models:
                - build the ollama docker image if needed and run it.
                    - download the supported Minstral model
                    - add 'ollama/minstral' to the available models on .m/settings.json (encrypted).
            - if the user requested to use 'remote' or 'remote & local' models:
                - ask/prompt the user for supported LLM API keys:  Anthropic, OpenAI, Groq. At least one needs to be define, but best if we can have them all. Save them to .m/settings.json (encrypted)
            - configure the litellm docker image to use all available models on .m/settings.json (or overwritten by the local .m.json file). Build image if needed and run it (if needed).
    - If the user issues "m 'setup local'", we re-run the above steps and save the settings on the local .m.json file). If the user issues "m 'setup'", we re-run the above steps even if they exists.
    - (always run) If .m settings (or overwritten by local .m.json) specifies we have local models support, check 'docker' is running. Also start required docker images if needed (ollama and litellm, etc).

1) extract objective from user prompt: "refactor to typescript"
2) ask brain (LLM with instructor) to expand the objective, showing it can make
use of certain custom methods for querying more info (generating context), defaulting assuming always the action refers to something to be made on the current folder. For example, the brain can request more data by issuing (a 'buildMoreContext' cmd, internally saving this session until 'ready' into a hashed key with the prompt; this context will be cached on the folder .m for some default minutes or until we make changes (which should issue a re-execution of the commands used to build the context)) commands for the folder such as 'get source_tree', 'read files on folder x', 'read file x', 'executeBash', 'searchWeb for xx', where the 'objective' class will return the data from the requested methods (essentially all these methods are 'read only'; these steps are going to be saved as a context request array, getting re-processed if changes are made to the files in the folder), building a 'live' context for an improved baseline prompt. When the 'brain' doesn't need more info it can issue a command 'ready' to let know that the gathered info is enought for the requested task. When that is 'ready', we'll request the brain to take the built context and break the objective into a series of action steps, considering the 'write' actions available such as 'summarize file x', 'edit file x' (with gitdiff if plain, or custom parser if other type),'create git branch x', 'create commit', 'rollback commit', 'create PR request', 'refactor file x into y', 'create file x with contents y' (if the file is a binary it uses a custom parser to read and write; e.g. excel files, docx files, etc)