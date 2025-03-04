@echo off
setlocal enabledelayedexpansion

REM Create the .log directory (if it doesn't exist)
if not exist ".log" (
    mkdir .log
)

REM Check if any parameters are provided
if "%~1"=="" (
    set start_all=1
) else (
    set start_all=0
)

REM Start the appropriate Python scripts based on the parameters
if "%start_all%"=="1" (
    REM Start all Python scripts
    set script_list=actor gui_parser step_check planner_critic actor_critic
) else (
    REM Start only the specified Python scripts
    set script_list=%*
)

for %%s in (%script_list%) do (
    if "%%s"=="actor" (
        set log_file=.log\actor_server.log
        echo Starting agent\actor\server.py... > !log_file!
        start /B python -u agent\actor\server.py >> !log_file! 2>>&1
    )
    
    if "%%s"=="gui_parser" (
        set log_file=.log\gui_parser_server.log
        echo Starting agent\gui_parser\server.py... > !log_file!
        start /B python -u agent\gui_parser\server.py >> !log_file! 2>>&1
    )

    if "%%s"=="step_check" (
        set log_file=.log\step_check_server.log
        echo Starting agent\step_check\server.py... > !log_file!
        start /B python -u agent\step_check\server.py >> !log_file! 2>>&1
    )

    if "%%s"=="planner_critic" (
        set log_file=.log\planner_critic_server.log
        echo Starting agent\planner_critic\server.py... > !log_file!
        start /B python -u agent\planner_critic\server.py >> !log_file! 2>>&1
    )

    if "%%s"=="actor_critic" (
        set log_file=.log\actor_critic_server.log
        echo Starting agent\actor_critic\server.py... > !log_file!
        start /B python -u agent\actor_critic\server.py >> !log_file! 2>>&1
    )
)

echo Servers have been started based on your input, logs can be found in the .log directory.