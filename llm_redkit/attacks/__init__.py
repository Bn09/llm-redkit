from .prompt_injection import PROMPT_INJECTION
from .jailbreak import JAILBREAK
from .data_leak import DATA_LEAK
from .encoding import ENCODING
from .system_extract import SYSTEM_EXTRACT

ALL_ATTACKS = {
    "prompt_injection": PROMPT_INJECTION,
    "jailbreak": JAILBREAK,
    "data_leak": DATA_LEAK,
    "encoding": ENCODING,
    "system_extract": SYSTEM_EXTRACT,
}
