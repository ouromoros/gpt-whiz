from typing import List, Union, Dict, Any, Callable
from api import Message, OpenAIChatModel
from command import run_powershell
from format import convert_to_dict, convert_to_xml

def make_message(role: Union["user", "assistant"], msg: Dict[str, str], name: Union["terminal", None] = None) -> Dict[str, Union[str, Dict[str, str]]]:
    return Message(role, convert_to_xml(msg), name)

system_msg = ("You are a sophisticated AI assistant that can execute PowerShell commands to assist user with their tasks. "
              "The conversation will use xml format. The response will either be a request to execute commands or a final "
              "response to the user. The final answer must be a string wrapped in answer element. You should always execute"
              "the best command you can find to gather information for the final answer. You can run command for multiple"
              "rounds, but you should use as few rounds as possible. You must provide clear and helpful information as answer."
              "When executing command, the output must not exceed 1000 tokens. If the output is too long, you should process"
              "the output in command so that it can fit in the limit.")
base_prompt_msgs: List[Message] = [
    {"role": "system", "content": system_msg},
    # basic
    make_message("user", {"instruction": "hello!"}),
    make_message("assistant", {"answer": "Hi! How may I assist you?"}),
    # multi-language
    make_message("user", {"instruction": "你好!"}),
    make_message("assistant", {"answer": "你好！我可以帮到你什么吗？"}),
    # basic call command
    make_message("user", {"instruction": "What is the time now?"}),
    make_message("assistant", {
        "thought": "I need to call `Get-Time` to know the current time",
        "command": "Get-Date",
    }),
    make_message("user", {"result": "Saturday, April 1, 2023 4:48:39 PM"}, "terminal"),
    make_message("assistant", {"answer": "The current time is 4:48:39 PM on Saturday, April 1, 2023."}),
    # basic network request
    make_message("user", {"instruction": "where am I?"}),
    make_message("assistant", {
    "thought": "To know where you are, I need to get your IP address and location using an external API.",
    "command": "(Invoke-WebRequest -Uri \"https://ipinfo.io/json\" -UseBasicParsing).Content",
    }),
    make_message("user", {"result": '{\n "ip": "117.80.127.30",\n "city": "Nanjing",\n "region": "Jiangsu",\n "country": "CN",\n "loc": "32.0617,118.7778",\n "org": "AS4134 CHINANET-BACKBONE",\n "timezone": "Asia/Shanghai",\n "readme": "https://ipinfo.io/missingauth"\n}'}, "terminal"),
    make_message("assistant", {"answer": "You are currently in Nanjing, Jiangsu, China."}),
    make_message("user", {"instruction": "what is the weather like?"}),
    # multi-step
    make_message("assistant", { "thought": "To know the current weather, I need to get your location first, and then call an external API to retrieve the current weather data.", "command": "(Invoke-WebRequest -Uri \"https://ipinfo.io/json\" -UseBasicParsing).Content", }),
    make_message("user", {"result": '{\n "ip": "117.80.127.30",\n "city": "Nanjing",\n "region": "Jiangsu",\n "country": "CN",\n "loc": "32.0617,118.7778",\n "org": "AS4134 CHINANET-BACKBONE",\n "timezone": "Asia/Shanghai",\n "readme": "https://ipinfo.io/missingauth"\n}'}, "terminal"),
    make_message("assistant", { "thought": "Now that I know your current location, I can call an external API to retrieve the current weather data.", "command": '(Invoke-WebRequest -Uri "https://wttr.in//NanJing?format=\"%C+%t\" %P\"").Content' }),
    make_message("user", {
        "error": "Invoke-WebRequest : A positional parameter cannot be found that accepts argument '%C+%t%20%P'.\\nAt line:1 char:2\\n"
                "+ (Invoke-WebRequest -Uri \"http://wttr.in/?format=\"%C+%t\" %P\" -UseBas ..."
                "+  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                "    + CategoryInfo          : InvalidArgument: (:) [Invoke-WebRequest], ParameterBindingException"
                "    + FullyQualifiedErrorId : PositionalParameterNotFound,Microsoft.PowerShell.Commands.InvokeWebRequestCommand"
        }, "terminal"),
    # handles command problem and do retry
    make_message("assistant", { "thought": "It looks like my command has syntax problem with escaping double quotes, I need to fix the error and re-run it.", "command": '(Invoke-WebRequest -Uri "https://wttr.in/NanJing?format=`"%C+%t %P`"").Content' }),
    make_message("user", {"result": "\"Clear +20°C 1012hPa\""}, "terminal"),
    make_message("assistant", {"answer": "The weather is currently clear and the temperature is 20°C (68°F). The air pressure is 1012hPa. It's a beautiful day with clear skies and warm temperatures. It's a great time to enjoy outdoor activities or just relax in the sun. Make sure to stay hydrated and protect your skin from the sun's rays."}),
]

def msg_to_display(msg: Any) -> str:
    """
    Converts a message to a string for display.

    >>> msg_to_display({"result": "Saturday, April 1, 2023 4:48:39 PM"})
    'result: Saturday, April 1, 2023 4:48:39 PM\\n'

    >>> msg_to_display({"error": "Some error occurred"})
    'error: Some error occurred\\n'
    """
    return "\n".join(f"{k}: {v}" for k, v in msg.items()) + "\n"

def is_command_msg(msg: Any) -> bool:
    """
    Returns True if the message contains a command key, False otherwise.

    >>> is_command_msg({"command": "Get-Date"})
    True

    >>> is_command_msg({"answer": "The current time is 4:48:39 PM on Saturday, April 1, 2023."})
    False
    """
    return "command" in msg

def is_answer_msg(msg: Any) -> bool:
    """
    Returns True if the message contains an answer key, False otherwise.

    >>> is_answer_msg({"answer": "The current time is 4:48:39 PM on Saturday, April 1, 2023."})
    True

    >>> is_answer_msg({"command": "Get-Date"})
    False
    """
    return "answer" in msg

def execute(task: str, api_key: str, log: Callable[[str], None], history: List[Message] = None) -> List[Message]:
    if history:
        current_messages = history + [make_message("user", {"instruction": task})]
    else:
        current_messages = base_prompt_msgs + [make_message("user", {"instruction": task})]
    api = OpenAIChatModel(api_key)
    # print(current_messages)
    response = api.chat_complete(current_messages)
    current_messages.append(response)

    try:
        msg = convert_to_dict(response.content)
    except:
        log("Error happened when trying to parse response: " + response.content)
        return

    while True:
        if is_command_msg(msg):
            log(msg_to_display(msg))
            log("Executing command...")
            try:
                result = run_powershell(msg["command"], False)
                result_msg = make_message("user", {"result": result}, "terminal")
                log(msg_to_display({"result": result}))
            except Exception as e:
                result_msg = make_message("user", {"error": str(e)}, "terminal")
                log(msg_to_display({"error": str(e)}))
            current_messages.append(result_msg)
            response = api.chat_complete(current_messages)
            current_messages.append(response)
            try:
                msg = convert_to_dict(response.content)
            except:
                log("Error happened when trying to parse response: " + response.content)
                break
        elif is_answer_msg(msg):
            log(msg_to_display(msg))
            break
        else:
            log("Invalid message: " + response.content)
            break
    return current_messages

if __name__ == "__main__":
    import doctest
    doctest.testmod()