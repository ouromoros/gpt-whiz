import subprocess
import base64
from typing import List

dangerous_commands = [
    'Remove-Item',
    'rmdir',
    'rm',
    'del',
    'Delete',
    'Format',
    'Set-Content',
    'Add-Content',
    'Clear-Content',
    'Copy-Item',
    'Move-Item',
    'Rename-Item',
]

def is_safe_script(script: str) -> bool:
    """
    >>> is_safe_script("Get-Process")
    True
    >>> is_safe_script("rmdir C:\\test")
    False
    """
    return not any(command in script for command in dangerous_commands)

def run_powershell(script: str, safe_mode: bool, length_limit: int = 10000) -> str:
    """
    >>> run_powershell("Write-Output 'Hello, World!'", True)
    'Hello, World!'
    >>> run_powershell("Remove-Item C:\\test", True)  # doctest: +SKIP
    Traceback (most recent call last):
      ...
    Exception: The script contains potentially dangerous commands and cannot be executed in safe mode.
    """
    if safe_mode and not is_safe_script(script):
        raise Exception('The script contains potentially dangerous commands and cannot be executed in safe mode.')

    wrapped_script = f'$ProgressPreference = \'SilentlyContinue\'; {script}'
    encoded_script = base64.b64encode(wrapped_script.encode('utf-16le')).decode('ascii')
    command = f'powershell.exe -ExecutionPolicy Bypass -NoProfile -NonInteractive -EncodedCommand "{encoded_script}"'

    result = subprocess.run(command, text=True, capture_output=True, shell=True, check=False)

    if result.returncode != 0:
        raise Exception(f'Error executing script: {result.stderr}')
    elif len(result.stdout.strip()) > length_limit:
        raise Exception(f'The script output exceeded length limit {length_limit}')
    else:
        return result.stdout.strip()

if __name__ == "__main__":
    import doctest
    doctest.testmod()