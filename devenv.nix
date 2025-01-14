{ pkgs, lib, config, ... }:

{
  packages = [
    pkgs.ffmpeg-headless
  ];

  env = {
    "LANGSMITH_TRACING_V2"="true";
    "LANGSMITH_ENDPOINT"="https://api.smith.langchain.com";
    "LANGSMITH_PROJECT"="LLM-tools";
    "OPENAI_API_URL"="https://open.bigmodel.cn/api/paas/v4";
  };

  enterShell = ''
    export OPENAI_API_KEY=`cat ./secrets/glm_api_key.txt`
    export ZHIPUAI_API_KEY=`cat ./secrets/glm_api_key.txt`
    export LANGSMITH_API_KEY=`cat ./secrets/langsmith_api_key.txt`
  '';

  languages.javascript.enable = true;
    

  languages.python = {
    enable = true;
    venv.enable = true;
    venv.requirements = ./requirements.txt;
  };
}