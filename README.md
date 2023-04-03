# gpt-whiz

## Usage

The library uses `requests`, so make sure it's installed using `pip install requests`.

To run the program, set environment variable using `$env:openai_api_key=<YOUR_API_KEY>`. Then run the program with

```
python cli.py
```

## Examples

### Some examples that do exist in the prompt

```
Enter your instruction: What is the time now?
thought: To know the current time, I need to call `Get-Date`.
command: Get-Date

Executing command...
result: Monday, April 3, 2023 8:28:12 PM

answer: The current time is 8:28:12 PM on Monday, April 3, 2023.


Enter your instruction: Where am I?
thought: To know your location, I need to get your IP address and location using an external API.
command: (Invoke-WebRequest -Uri "https://ipinfo.io/json" -UseBasicParsing).Content

Executing command...
result: {
  "ip": "49.65.213.24",
  "city": "Nanjing",
  "region": "Jiangsu",
  "country": "CN",
  "loc": "32.0617,118.7778",
  "org": "AS4134 CHINANET-BACKBONE",
  "timezone": "Asia/Shanghai",
  "readme": "https://ipinfo.io/missingauth"
}

answer: You are currently in Nanjing, Jiangsu, China.


Enter your instruction: What is the weather in Nanjing?
thought: To know the current weather, I will call an external API to retrieve the current weather data for Nanjing.
command: (Invoke-WebRequest -Uri "https://wttr.in/NanJing?format=`"%C+%t %P`"").Content

Executing command...
result: "Rain shower +15°C 1007hPa"

answer: The weather is currently a rain shower and the temperature is 15°C (59°F) in Nanjing. The air pressure is 1007hPa. Make sure to carry an umbrella if you are planning to go outside. It might be a good time to watch a movie or read a book indoors. Stay dry and stay safe!
```

### A more complex one that does not exist in the prompt

```
Enter your instruction: How is my computer status?
thought: To check your computer's status, I can use `Get-CimInstance` cmdlet to obtain various information such as CPU, memory, and disk usage.
command: Get-CimInstance -ClassName Win32_OperatingSystem,Win32_Processor,Win32_LogicalDisk | Format-Table -AutoSize

Executing command...
error: Error executing script: #< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">Get-CimInstance : Cannot convert 'System.Object[]' to the type 'System.String' required by parameter 'ClassName'. Specified method is not supported._x000D__x000A_</S><S S="Error">At line:1 char:70_x000D__x000A_</S><S S="Error">+ ...  -ClassName Win32_OperatingSystem,Win32_Processor,Win32_LogicalDisk | ..._x000D__x000A_</S><S S="Error">+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">    + CategoryInfo          : InvalidArgument: (:) [Get-CimInstance], ParameterBindingException_x000D__x000A_</S><S S="Error">    + FullyQualifiedErrorId : CannotConvertArgument,Microsoft.Management.Infrastructure.CimCmdlets.GetCimInstanceCommand_x000D__x000A_</S><S S="Error"> _x000D__x000A_</S></Objs>

thought: It looks like there is an error in the command. I need to run `Get-CimInstance -ClassName` with each class separately to retrieve information on CPU, memory, and disk usage.
command: Get-CimInstance -ClassName Win32_OperatingSystem | Format-Table CSName, Caption, LastBootUpTime, TotalVisibleMemorySize, FreePhysicalMemory, OperatingSystemSKU -AutoSize       

Executing command...
result: CSName     Caption                     LastBootUpTime       TotalVisibleMemorySize FreePhysicalMemory OperatingSystemSKU
------     -------                     --------------       ---------------------- ------------------ ------------------
JITIANDENG Microsoft Windows 11 专业版 4/1/2023 11:28:06 PM               33405728           16514420                 48

command: Get-CimInstance -ClassName Win32_Processor | Format-Table Name, Caption, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors -AutoSize

Executing command...
result: Name                                  Caption                               MaxClockSpeed NumberOfCores NumberOfLogicalProcessors
----                                  -------                               ------------- ------------- -------------------------
13th Gen Intel(R) Core(TM) i7-13700KF Intel64 Family 6 Model 183 Stepping 1          3400            16                        24

command: Get-CimInstance -ClassName Win32_LogicalDisk | Format-Table DeviceID, MediaType, VolumeName, FileSystem, Size, FreeSpace -AutoSize

Executing command...
result: DeviceID MediaType VolumeName FileSystem          Size    FreeSpace
-------- --------- ---------- ----------          ----    ---------
C:              12            NTFS        297606451200  66755280896
D:              12            NTFS        201111838720  16876113920
E:              12            NTFS       3000574668800 180559880192
F:              12            NTFS       1024207089664 113430786048

answer: Based on the results of `Get-CimInstance` cmdlets, your computer seems to be running Windows 11 Professional edition, has an Intel Core i7-13700KF CPU, and 16 cores with the maximum clock speed of 3400 MHz. The computer has 32,405,728 KB of visible memory and there is currently 16,514,420 KB of free physical memory available. The computer has four disks: C, D, E and F. The storage size and available free space are shown for each disk. Is there anything specific you would like me to check?
```
