@echo off
setlocal enabledelayedexpansion

REM Define hardcoded port numbers

set "port_planner_critc=5001"
set "port_gui_parser=5002"
set "port_step_check=5003"
set "port_actor=5004"
set "port_actorcritic=5005"

REM Check input parameters
if "%~1"=="" (
    set stop_all=1
) else (
    set stop_all=0
)

REM Determine which ports to stop based on input parameters
if "%stop_all%"=="1" (
    set ports=%port_gui_parser% %port_actor% %port_step_check% %port_actorcritic% %port_planner_critc%
) else (
    set ports=%*
)

REM Stop processes based on ports
for %%p in (%ports%) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
        echo Stopping server on port %%p, PID: %%a
        taskkill /PID %%a /T /F
    )
)

echo All specified servers have been stopped.
