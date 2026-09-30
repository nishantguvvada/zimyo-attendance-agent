"""LangGraph agent for attendance automation."""
from datetime import datetime
from typing import Dict, Any, Literal, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import pytz

from zimyo_attendance.config.settings import get_settings
from zimyo_attendance.tools.zimyo_client import create_zimyo_client, AttendanceData
from zimyo_attendance.storage.json_file import create_storage


class AgentState(BaseModel):
    """State for the attendance agent."""
    action: Literal["clock_in", "clock_out", "status", "auto"] = "auto"
    uae_time: str = ""
    current_status: str = ""
    attendance_data: Optional[AttendanceData] = None
    result: str = ""
    success: bool = False
    error: Optional[str] = None


def get_uae_time(state: AgentState) -> AgentState:
    """Get current UAE time."""
    tz = pytz.timezone("Asia/Dubai")
    now = datetime.now(tz)
    state.uae_time = now.strftime("%Y-%m-%d %H:%M:%S")
    state.attendance_data = None  # Will be fetched in next step
    return state


def check_status(state: AgentState) -> AgentState:
    """Check current attendance status from Zimyo."""
    client = create_zimyo_client()
    try:
        attendance = client.get_attendance_status()
        
        if attendance:
            state.attendance_data = attendance
            state.current_status = "CLOCKED_IN" if attendance.is_clocked_in else "CLOCKED_OUT"
        else:
            state.error = "Failed to fetch attendance data"
            state.current_status = "ERROR"
    except Exception as e:
        state.error = f"Status check error: {e}"
        state.current_status = "ERROR"
    finally:
        client.close()
    
    return state


def decide_action(state: AgentState) -> AgentState:
    """Decide what action to take based on time and current status."""
    if state.error:
        state.action = "status"
        return state
    
    if not state.attendance_data:
        state.error = "Unable to determine attendance status; no punch sent"
        state.action = "status"
        return state

    if state.action != "auto":
        # Client guards also recheck status immediately before manual punches.
        return state
    
    # Parse UAE time
    tz = pytz.timezone("Asia/Dubai")
    now = datetime.now(tz)
    current_hour = now.hour
    current_minute = now.minute
    current_time_minutes = current_hour * 60 + current_minute
    
    # Parse window times
    settings = get_settings()
    clock_in_start = _parse_time_to_minutes(settings.clock_in_window_start)
    clock_in_end = _parse_time_to_minutes(settings.clock_in_window_end)
    clock_out_start = _parse_time_to_minutes(settings.clock_out_window_start)
    clock_out_end = _parse_time_to_minutes(settings.clock_out_window_end)
    
    # Check if weekend (UAE: Friday=5, Saturday=6)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6 in Python
        state.result = f"Weekend ({now.strftime('%A')}) - no attendance action needed"
        state.success = True
        state.action = "status"
        return state
    
    # Decision logic
    if state.current_status == "CLOCKED_OUT":
        if clock_in_start <= current_time_minutes <= clock_in_end:
            state.action = "clock_in"
        elif current_time_minutes < clock_in_start:
            state.result = f"Too early for clock-in (window: {settings.clock_in_window_start}-{settings.clock_in_window_end})"
            state.success = True
            state.action = "status"
        else:
            state.result = "Already clocked out; outside the clock-in window"
            state.success = True
            state.action = "status"
    
    elif state.current_status == "CLOCKED_IN":
        if clock_out_start <= current_time_minutes <= clock_out_end:
            state.action = "clock_out"
        elif current_time_minutes < clock_out_start:
            state.result = f"Still in work hours, clock-out window: {settings.clock_out_window_start}-{settings.clock_out_window_end}"
            state.success = True
            state.action = "status"
        else:
            state.action = "clock_out"  # Past clock-out window, clock out anyway
    
    else:
        state.action = "status"
    
    return state


def execute_clock_in(state: AgentState) -> AgentState:
    """Execute guarded clock in."""
    return _execute_punch(state, "clock_in")


def execute_clock_out(state: AgentState) -> AgentState:
    """Execute guarded clock out."""
    return _execute_punch(state, "clock_out")


def _execute_punch(state: AgentState, action: str) -> AgentState:
    client = create_zimyo_client()
    try:
        state.success = client.clock_in() if action == "clock_in" else client.clock_out()
        state.result = client.last_action_message
        state.error = None if state.success else state.result
        state.attendance_data = client.last_attendance
    except Exception as e:
        state.result = "Attendance action could not be completed"
        state.error = str(e)
        state.success = False
    finally:
        client.close()
    return state


def format_response(state: AgentState) -> AgentState:
    """Format final response and save to storage."""
    storage = create_storage(get_settings().storage_path)
    
    record = {
        "date": state.uae_time.split()[0] if state.uae_time else datetime.now().strftime("%Y-%m-%d"),
        "action": state.action,
        "uae_time": state.uae_time,
        "status_before": state.current_status,
        "result": state.result,
        "success": state.success,
        "error": state.error,
    }
    
    if state.attendance_data:
        record["punch_in_time"] = state.attendance_data.punch_in_time
        record["punch_out_time"] = state.attendance_data.punch_out_time
        record["shift_name"] = state.attendance_data.shift_name
    
    storage.add_record(record)
    
    # Build final message
    if state.error:
        state.result = f"❌ Error: {state.error}"
    elif state.success:
        state.result = f"✅ {state.result}"
    else:
        state.result = f"ℹ️ {state.result}"
    
    return state


def _parse_time_to_minutes(time_str: str) -> int:
    """Parse HH:MM time string to minutes since midnight."""
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def create_attendance_graph() -> StateGraph:
    """Create the LangGraph workflow for attendance automation."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("get_time", get_uae_time)
    workflow.add_node("check_status", check_status)
    workflow.add_node("decide", decide_action)
    workflow.add_node("clock_in", execute_clock_in)
    workflow.add_node("clock_out", execute_clock_out)
    workflow.add_node("respond", format_response)
    
    # Define edges
    workflow.set_entry_point("get_time")
    workflow.add_edge("get_time", "check_status")
    workflow.add_edge("check_status", "decide")
    
    # Conditional edges from decide
    workflow.add_conditional_edges(
        "decide",
        lambda s: s.action,
        {
            "clock_in": "clock_in",
            "clock_out": "clock_out",
            "status": "respond",
        }
    )
    
    workflow.add_edge("clock_in", "respond")
    workflow.add_edge("clock_out", "respond")
    workflow.add_edge("respond", END)
    
    return workflow.compile()


# Convenience function to run the agent
def run_attendance_agent(action: str = "auto") -> Dict[str, Any]:
    """Run the attendance agent with specified action."""
    graph = create_attendance_graph()
    
    initial_state = AgentState(action=action)
    final_state = graph.invoke(initial_state)
    
    return {
        "success": final_state.get("success", False),
        "result": final_state.get("result", ""),
        "action": final_state.get("action", ""),
        "uae_time": final_state.get("uae_time", ""),
        "error": final_state.get("error"),
    }
