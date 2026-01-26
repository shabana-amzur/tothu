# World Time Tool - Agent Enhancement

## Overview
Added a timezone tool to the LangChain Agent that can tell the current time for any country or major city.

## Tool Details

**Function:** `world_time(country: str) -> str`

**Description:** Gets current time and date for different countries and major cities around the world.

**Supported Locations:**
- Countries: USA, UK, India, Japan, China, Australia, Germany, France, Canada, Brazil, Russia, Mexico, Italy, Spain, South Korea, Singapore, UAE
- Major Cities: New York, London, Tokyo, Sydney, Paris, Los Angeles, Chicago, Hong Kong, Dubai

## Usage Examples

### In Chat (Agent Mode ON):
```
User: "What time is it in India?"
Agent: India: 11:48 PM on Monday, January 26, 2026 (Asia/Kolkata)

User: "Tell me the current time in Japan and USA"
Agent: 
Japan: 03:18 AM on Tuesday, January 27, 2026 (Asia/Tokyo)
USA: 01:18 PM on Monday, January 26, 2026 (America/New_York)

User: "What's the time in London?"
Agent: Uk: 06:18 PM on Monday, January 26, 2026 (Europe/London)
```

### Direct Function Call:
```python
from app.services.basic_agent import world_time

# Test different countries
print(world_time("India"))    # India: 11:48 PM on Monday, January 26, 2026
print(world_time("Japan"))    # Japan: 03:18 AM on Tuesday, January 27, 2026
print(world_time("usa"))      # Usa: 01:18 PM on Monday, January 26, 2026
print(world_time("London"))   # London: 06:18 PM on Monday, January 26, 2026
```

## Technical Implementation

### Dependencies:
- `pytz` - For timezone conversions
- `datetime` - For time operations

### Key Features:
1. **Case-insensitive input** - Accepts "USA", "usa", "United States"
2. **Multiple timezone support** - 30+ countries and cities mapped
3. **12-hour format** - User-friendly time display (02:30 PM)
4. **Full date context** - Shows day of week, date, and timezone name
5. **Error handling** - Provides helpful error messages for unsupported locations

### Country-to-Timezone Mapping:
```python
country_tz_map = {
    'usa': 'America/New_York',
    'india': 'Asia/Kolkata',
    'japan': 'Asia/Tokyo',
    'uk': 'Europe/London',
    'australia': 'Australia/Sydney',
    # ... 25+ more mappings
}
```

## Agent Integration

### 1. Tool Registry (`TOOLS` dictionary):
```python
"world_time": {
    "function": world_time,
    "description": "Get current time for any country/city. Input: country or city name like 'India', 'Japan', 'USA', 'London'"
}
```

### 2. Agent Prompt:
```
- world_time: Get time for countries. Input: country name like "India", "Japan", "USA", "London"
```

### 3. Action Execution:
```python
elif action == 'world_time':
    if isinstance(action_input, dict):
        country = action_input.get('country', action_input)
    else:
        country = action_input
    observation = world_time(country)
```

## Frontend Update

Updated [page.tsx](frontend/app/page.tsx#L1004) to show:
```tsx
{useAgent ? '12 tools: math, text, date, validation, random, units, world time & more' : 'Standard chat mode'}
```

## Testing

### Backend Test:
```bash
cd backend
source ../venv/bin/activate
python -c "from app.services.basic_agent import world_time; print(world_time('India'))"
```

### Full Agent Test (when API quota available):
```bash
python -c "
from app.services.basic_agent import run_basic_agent
print(run_basic_agent('What time is it in Tokyo?'))
"
```

### Live Chat Test:
1. Open http://localhost:3000
2. Toggle "Agent Mode" ON (should show 12 tools)
3. Ask: "What's the current time in India?"
4. Ask: "Tell me the time in Japan, USA, and UK"

## Total Agent Tools: 12

1. calculator - Basic arithmetic
2. text_utility - Text operations
3. datetime_tool - Local date/time
4. string_analyzer - Text analysis
5. temperature_converter - Temperature conversion
6. list_helper - List operations
7. case_converter - Case conversion
8. number_operations - Number operations
9. validator - Format validation
10. random_generator - Random values
11. unit_converter - Unit conversion
12. **world_time** - World clock ⭐ NEW

## Notes

- Tool uses pytz library for accurate timezone handling
- Returns time in 12-hour format for better readability
- Includes full date context and timezone name
- Case-insensitive country/city matching
- Supports both full country names and abbreviations
- Clear error messages for unsupported locations

## Future Enhancements

Potential additions:
- More cities and countries
- Time zone offset calculations
- Daylight saving time indicators
- Business hours checker
- Meeting time finder across zones
