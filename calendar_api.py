import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import os

# This module requires credentials.json to be in the same directory.

SCOPES = ["https://www.googleapis.com/auth/calendar.app.created"]

# Map color codes to Google Calendar color IDs
COLOR_MAP = {
    'C': '7',   # Cyan
    'Y': '5',   # Yellow
    'M': '3',   # Magenta
    'G': '10',  # Green
    'R': '11',  # Red
    'B': '9',   # Blue
    'O': '6',   # Orange
    '.': '8'    # Grey
}

def get_service() -> Resource:
    """
    initialises the service object for the Google Calendar API.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


service = get_service()


def init_new_calendar(summary="Tetris Calendar", time_zone="Europe/London") -> None:
    body = {
        "summary": summary,
        "timeZone": time_zone
    }
    calendar = service.calendars().insert(body=body).execute()
    return calendar["id"]


def create_event(calendar_id: str, name: str, color: str, start: datetime.datetime, end: datetime.datetime) -> None:
    """
    Creates a Google Calendar event with the specified color, start, and end times.
    
    Args:
        color: Event color code (C=cyan, Y=yellow, M=magenta, G=green, R=red, B=blue, O=orange, .=grey)
        start: Start datetime for the event
        end: End datetime for the event
        calendar_id: Calendar ID to create the event in (default: 'primary')
    """
    
    # Validate color code
    if color not in COLOR_MAP:
        raise ValueError(f"Invalid color code '{color}'. Use one of: C, Y, M, G, R, B, O, .")
    
    # Convert datetime objects to ISO 8601 format with timezone
    # If timezone-naive, assume UTC
    if start.tzinfo is None:
        start = start.replace(tzinfo=datetime.timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=datetime.timezone.utc)
    
    start_iso = start.isoformat()
    end_iso = end.isoformat()
    
    # Get timezone string for Google Calendar API
    # Google Calendar API expects IANA timezone names like "UTC" or "America/Los_Angeles"
    def get_timezone_str(dt):
        if dt.tzinfo == datetime.timezone.utc:
            return "UTC"
        # Try to get timezone name from tzinfo
        tz_name = str(dt.tzinfo)
        # Check if it looks like an IANA timezone name (contains '/')
        if '/' in tz_name:
            return tz_name
        # For offset-based timezones, default to UTC
        # Users should use zoneinfo or pytz for proper timezone names
        return "UTC"
    
    timezone_str = get_timezone_str(start)
    
    # Create event body
    event_body = {
        'summary': name,
        'start': {
            'dateTime': start_iso,
            'timeZone': timezone_str
        },
        'end': {
            'dateTime': end_iso,
            'timeZone': timezone_str
        },
        'colorId': COLOR_MAP[color]
    }
    
    # Insert the event into the calendar
    try:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return event
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def edit_event(calendar_id: str, event_id: str, color: str) -> None:
    """
    Edits the event with the given ID to the given color.
    """
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event["colorId"] = COLOR_MAP[color]
    service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()


def set_grid(calendar_id: str, grid: list[list[str]], date: datetime.datetime) -> list[str]:
    """
    Sets the grid in the calendar for the given date.
    Returns a list of event IDs.

    Args:
        calendar_id: Calendar ID to create the events in
        grid: 24 x 10 grid of strings
        names: 24 x 10 grid of strings
        date: Date to create the events for

    Returns:
        List of event IDs
    """
    event_ids = []
    for y in range(24):
        for x in range(10):
            event = create_event(calendar_id, chr(ord('A') + x), grid[y][x], date + datetime.timedelta(hours=y), date + datetime.timedelta(hours=y+1))
            event_ids.append(event["id"])
    return event_ids


def update_grid(calendar_id: str, previous_grid: list[list[str]], previous_grid_event_ids: list[str], new_grid: list[list[str]]) -> None:
    """
    Updates the grid in the calendar for the given date.

    Args:
        previous_grid: 24 x 10 grid of strings
        previous_grid_event_ids: List of event IDs in the previous grid
        new_grid: 24 x 10 grid of strings
        date: Date to create the events for
    """
    for y in range(24):
        for x in range(10):
            print(f"Checking {y},{x}: {previous_grid[y][x]} != {new_grid[y][x]}")
            if previous_grid[y][x] != new_grid[y][x]:
                edit_event(calendar_id, previous_grid_event_ids[y * 10 + x], new_grid[y][x])