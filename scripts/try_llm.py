import os
import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv

from veille_ia.llm import complete, parse_models

load_dotenv()
models = parse_models(os.environ["LLM_MODELS_CLUSTER"])[:1]
print(complete("Réponds uniquement par : ok", models))
