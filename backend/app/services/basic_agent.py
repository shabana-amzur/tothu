"""
PROJECT 11: Educational LangChain Agent
========================================

LEARNING OBJECTIVE: Understand the difference between Chains and Agents

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS A CHAIN?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A Chain is a FIXED sequence of operations:
    Input → LLM → Output
    
Characteristics:
- ✓ Predictable: Always follows the same path
- ✓ Simple: Easy to understand and debug
- ✓ Fast: No decision-making overhead
- ✗ Rigid: Cannot adapt to different inputs
- ✗ Limited: Cannot use external tools

Example:
    user_query = "What is 2+2?"
    chain = prompt_template | llm | output_parser
    result = chain.invoke(user_query)
    # Always: parse input → call LLM → return output

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS AN AGENT?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

An Agent is an INTELLIGENT system that can:
    1. Think about what to do (Reasoning)
    2. Use tools to accomplish tasks (Action)
    3. Learn from results (Observation)
    4. Repeat until the task is complete

The ReAct Pattern (Reason + Act):
    Input → [LOOP: Thought → Action → Observation] → Final Answer
    
Characteristics:
- ✓ Adaptive: Chooses different paths based on input
- ✓ Powerful: Can use external tools and APIs
- ✓ Autonomous: Makes decisions on its own
- ✗ Complex: Harder to predict and debug
- ✗ Slower: Multiple LLM calls needed

Example:
    user_query = "What is 2+2?"
    agent = create_agent(llm, tools)
    
    Step 1 - Thought: "This is a math problem, I should use the calculator"
    Step 2 - Action: calculator("2+2")
    Step 3 - Observation: "4"
    Step 4 - Thought: "I have the answer"
    Final Answer: "2+2 equals 4"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY DIFFERENCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHAIN:
    - Fixed workflow
    - No tool usage
    - One LLM call
    - Deterministic path

AGENT:
    - Dynamic workflow
    - Can use tools
    - Multiple LLM calls
    - Chooses its own path

When to use what?
    - Chain: Simple tasks with predictable workflow
    - Agent: Complex tasks requiring tools and decision-making

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from langchain_google_genai import ChatGoogleGenerativeAI
import logging
import os
from dotenv import load_dotenv
import json
import re

# Configure logging to see agent's reasoning
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 1: Simple Calculator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculator(expression: str) -> str:
    """
    Performs basic math operations (addition and subtraction only).
    
    Args:
        expression: A simple math expression like "5+3" or "10-4"
    
    Returns:
        The result of the calculation
        
    Examples:
        calculator("2+2") → "4"
        calculator("10-3") → "7"
    """
    try:
        # Safety: Only allow numbers, +, -, and spaces
        allowed_chars = set('0123456789+-. ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Only use numbers, +, and - operators"
        
        # Evaluate the expression
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 2: Text Utility
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def text_utility(text: str, operation: str = "reverse") -> str:
    """
    Performs simple text operations.
    
    Args:
        text: The text to process
        operation: Either "reverse" (reverses the text) or "count" (counts words)
    
    Returns:
        The processed text or word count
        
    Examples:
        text_utility("hello", "reverse") → "olleh"
        text_utility("hello world", "count") → "2 words"
    """
    try:
        if operation == "reverse":
            return text[::-1]
        elif operation == "count":
            word_count = len(text.split())
            return f"{word_count} words"
        else:
            return "Error: operation must be 'reverse' or 'count'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIMPLE AGENT IMPLEMENTATION (without LangChain Agent framework)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 3: Date & Time
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def datetime_tool(operation: str = "current") -> str:
    """
    Provides date and time information.
    
    Args:
        operation: "current" (current datetime), "date" (current date), "time" (current time)
    
    Returns:
        Formatted datetime information
        
    Examples:
        datetime_tool("current") → "2026-01-26 15:30:45"
        datetime_tool("date") → "2026-01-26"
        datetime_tool("time") → "15:30:45"
    """
    try:
        from datetime import datetime
        now = datetime.now()
        
        if operation == "current":
            return now.strftime("%Y-%m-%d %H:%M:%S")
        elif operation == "date":
            return now.strftime("%Y-%m-%d")
        elif operation == "time":
            return now.strftime("%H:%M:%S")
        else:
            return "Error: operation must be 'current', 'date', or 'time'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 4: String Analyzer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def string_analyzer(text: str) -> str:
    """
    Analyzes a string and provides detailed statistics.
    
    Args:
        text: The text to analyze
    
    Returns:
        Statistics about the text (length, words, vowels, consonants, etc.)
        
    Examples:
        string_analyzer("Hello World") → "Length: 11, Words: 2, Vowels: 3, ..."
    """
    try:
        length = len(text)
        words = len(text.split())
        chars_no_space = len(text.replace(" ", ""))
        vowels = sum(1 for c in text.lower() if c in 'aeiou')
        consonants = sum(1 for c in text.lower() if c.isalpha() and c not in 'aeiou')
        digits = sum(1 for c in text if c.isdigit())
        uppercase = sum(1 for c in text if c.isupper())
        lowercase = sum(1 for c in text if c.islower())
        
        return (f"Length: {length} characters, "
                f"Words: {words}, "
                f"Chars (no spaces): {chars_no_space}, "
                f"Vowels: {vowels}, "
                f"Consonants: {consonants}, "
                f"Digits: {digits}, "
                f"Uppercase: {uppercase}, "
                f"Lowercase: {lowercase}")
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 5: Temperature Converter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def temperature_converter(value: str, from_unit: str, to_unit: str) -> str:
    """
    Converts temperature between Celsius, Fahrenheit, and Kelvin.
    
    Args:
        value: Temperature value as string (e.g., "25", "98.6")
        from_unit: Source unit ("C", "F", or "K")
        to_unit: Target unit ("C", "F", or "K")
    
    Returns:
        Converted temperature
        
    Examples:
        temperature_converter("25", "C", "F") → "77.0°F"
        temperature_converter("32", "F", "C") → "0.0°C"
    """
    try:
        temp = float(value)
        
        # Convert to Celsius first
        if from_unit.upper() == "C":
            celsius = temp
        elif from_unit.upper() == "F":
            celsius = (temp - 32) * 5/9
        elif from_unit.upper() == "K":
            celsius = temp - 273.15
        else:
            return "Error: from_unit must be C, F, or K"
        
        # Convert from Celsius to target
        if to_unit.upper() == "C":
            result = celsius
            unit_symbol = "°C"
        elif to_unit.upper() == "F":
            result = (celsius * 9/5) + 32
            unit_symbol = "°F"
        elif to_unit.upper() == "K":
            result = celsius + 273.15
            unit_symbol = "K"
        else:
            return "Error: to_unit must be C, F, or K"
        
        return f"{result:.2f}{unit_symbol}"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 6: List Helper
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def list_helper(items: str, operation: str = "sort") -> str:
    """
    Performs operations on comma-separated lists.
    
    Args:
        items: Comma-separated list of items (e.g., "apple,banana,cherry")
        operation: "sort" (alphabetically), "count" (number of items), "unique" (remove duplicates)
    
    Returns:
        Result of the operation
        
    Examples:
        list_helper("banana,apple,cherry", "sort") → "apple, banana, cherry"
        list_helper("a,b,a,c", "unique") → "a, b, c"
    """
    try:
        item_list = [item.strip() for item in items.split(',')]
        
        if operation == "sort":
            result = sorted(item_list)
            return ", ".join(result)
        elif operation == "count":
            return f"{len(item_list)} items"
        elif operation == "unique":
            result = list(dict.fromkeys(item_list))  # Preserves order
            return ", ".join(result)
        else:
            return "Error: operation must be 'sort', 'count', or 'unique'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 7: Case Converter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def case_converter(text: str, operation: str = "upper") -> str:
    """
    Converts text case.
    
    Args:
        text: The text to convert
        operation: "upper" (UPPERCASE), "lower" (lowercase), "title" (Title Case), "capitalize" (First word)
    
    Returns:
        Text in the specified case
        
    Examples:
        case_converter("hello world", "upper") → "HELLO WORLD"
        case_converter("HELLO WORLD", "lower") → "hello world"
        case_converter("hello world", "title") → "Hello World"
    """
    try:
        if operation == "upper":
            return text.upper()
        elif operation == "lower":
            return text.lower()
        elif operation == "title":
            return text.title()
        elif operation == "capitalize":
            return text.capitalize()
        else:
            return "Error: operation must be 'upper', 'lower', 'title', or 'capitalize'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 8: Number Operations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def number_operations(numbers: str, operation: str = "sum") -> str:
    """
    Performs operations on comma-separated numbers.
    
    Args:
        numbers: Comma-separated numbers (e.g., "10,20,30")
        operation: "sum", "average", "min", "max", "count"
    
    Returns:
        Result of the operation
        
    Examples:
        number_operations("10,20,30", "sum") → "60"
        number_operations("10,20,30", "average") → "20.0"
        number_operations("10,20,30", "max") → "30"
    """
    try:
        num_list = [float(n.strip()) for n in numbers.split(',')]
        
        if operation == "sum":
            return str(sum(num_list))
        elif operation == "average":
            return str(sum(num_list) / len(num_list))
        elif operation == "min":
            return str(min(num_list))
        elif operation == "max":
            return str(max(num_list))
        elif operation == "count":
            return str(len(num_list))
        else:
            return "Error: operation must be 'sum', 'average', 'min', 'max', or 'count'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 9: Validator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validator(value: str, validation_type: str) -> str:
    """
    Validates various data formats.
    
    Args:
        value: The value to validate
        validation_type: "email", "url", "phone", "number"
    
    Returns:
        "Valid" or "Invalid" with explanation
        
    Examples:
        validator("test@example.com", "email") → "Valid email"
        validator("abc", "number") → "Invalid number"
    """
    try:
        import re
        
        if validation_type == "email":
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, value):
                return "Valid email format"
            return "Invalid email format"
        
        elif validation_type == "url":
            pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            if re.match(pattern, value):
                return "Valid URL format"
            return "Invalid URL format"
        
        elif validation_type == "phone":
            # Simple phone validation (digits and common separators)
            pattern = r'^[\d\s\-\+\(\)]{10,}$'
            if re.match(pattern, value):
                return "Valid phone format"
            return "Invalid phone format"
        
        elif validation_type == "number":
            try:
                float(value)
                return "Valid number"
            except:
                return "Invalid number"
        
        else:
            return "Error: validation_type must be 'email', 'url', 'phone', or 'number'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 10: Random Generator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def random_generator(operation: str, param: str = "") -> str:
    """
    Generates random values.
    
    Args:
        operation: "number" (random number), "choice" (random from list), "coin" (heads/tails), "dice" (1-6)
        param: For 'number': "min,max" (e.g., "1,100"), For 'choice': comma-separated items
    
    Returns:
        Random result
        
    Examples:
        random_generator("number", "1,100") → "42"
        random_generator("choice", "red,blue,green") → "blue"
        random_generator("coin") → "Heads"
        random_generator("dice") → "5"
    """
    try:
        import random
        
        if operation == "number":
            if param:
                min_val, max_val = map(int, param.split(','))
                return str(random.randint(min_val, max_val))
            return str(random.randint(1, 100))
        
        elif operation == "choice":
            if not param:
                return "Error: provide comma-separated choices"
            choices = [item.strip() for item in param.split(',')]
            return random.choice(choices)
        
        elif operation == "coin":
            return random.choice(["Heads", "Tails"])
        
        elif operation == "dice":
            return str(random.randint(1, 6))
        
        else:
            return "Error: operation must be 'number', 'choice', 'coin', or 'dice'"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 11: Unit Converter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def unit_converter(value: str, from_unit: str, to_unit: str) -> str:
    """
    Converts between common units.
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit (km, m, cm, kg, g, lb)
        to_unit: Target unit
    
    Returns:
        Converted value
        
    Examples:
        unit_converter("5", "km", "m") → "5000 m"
        unit_converter("1000", "g", "kg") → "1.0 kg"
    """
    try:
        val = float(value)
        
        # Distance conversions to meters
        distance_to_m = {"km": 1000, "m": 1, "cm": 0.01, "mm": 0.001, "mi": 1609.34, "ft": 0.3048, "in": 0.0254}
        
        # Weight conversions to grams
        weight_to_g = {"kg": 1000, "g": 1, "mg": 0.001, "lb": 453.592, "oz": 28.3495}
        
        # Try distance conversion
        if from_unit in distance_to_m and to_unit in distance_to_m:
            meters = val * distance_to_m[from_unit]
            result = meters / distance_to_m[to_unit]
            return f"{result:.2f} {to_unit}"
        
        # Try weight conversion
        if from_unit in weight_to_g and to_unit in weight_to_g:
            grams = val * weight_to_g[from_unit]
            result = grams / weight_to_g[to_unit]
            return f"{result:.2f} {to_unit}"
        
        return f"Error: Cannot convert {from_unit} to {to_unit}"
    except Exception as e:
        return f"Error: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL 12: World Time
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def world_time(country: str) -> str:
    """
    Gets current time for different countries/timezones.
    
    Args:
        country: Country or city name
    
    Returns:
        Current time and date for that location
        
    Examples:
        world_time("India") → "India: 02:30 PM on Sunday, January 26, 2026 (Asia/Kolkata)"
        world_time("Japan") → "Japan: 06:00 PM on Sunday, January 26, 2026 (Asia/Tokyo)"
    """
    try:
        from datetime import datetime
        import pytz
        
        country = country.strip().lower()
        
        # Map countries to timezones
        country_tz_map = {
            'usa': 'America/New_York',
            'united states': 'America/New_York',
            'us': 'America/New_York',
            'uk': 'Europe/London',
            'united kingdom': 'Europe/London',
            'england': 'Europe/London',
            'india': 'Asia/Kolkata',
            'japan': 'Asia/Tokyo',
            'china': 'Asia/Shanghai',
            'australia': 'Australia/Sydney',
            'germany': 'Europe/Berlin',
            'france': 'Europe/Paris',
            'canada': 'America/Toronto',
            'brazil': 'America/Sao_Paulo',
            'russia': 'Europe/Moscow',
            'mexico': 'America/Mexico_City',
            'italy': 'Europe/Rome',
            'spain': 'Europe/Madrid',
            'south korea': 'Asia/Seoul',
            'korea': 'Asia/Seoul',
            'singapore': 'Asia/Singapore',
            'uae': 'Asia/Dubai',
            'dubai': 'Asia/Dubai',
            'new york': 'America/New_York',
            'london': 'Europe/London',
            'tokyo': 'Asia/Tokyo',
            'sydney': 'Australia/Sydney',
            'paris': 'Europe/Paris',
            'los angeles': 'America/Los_Angeles',
            'chicago': 'America/Chicago',
            'hong kong': 'Asia/Hong_Kong'
        }
        
        timezone_name = country_tz_map.get(country)
        if not timezone_name:
            return f"Error: Timezone not found for '{country}'. Try: USA, UK, India, Japan, China, Australia, Germany, France, Canada, Brazil, etc."
        
        tz = pytz.timezone(timezone_name)
        current_time = datetime.now(tz)
        
        time_str = current_time.strftime('%I:%M %p')
        date_str = current_time.strftime('%A, %B %d, %Y')
        
        return f"{country.title()}: {time_str} on {date_str} ({timezone_name})"
    except Exception as e:
        return f"Error: {str(e)}"


# Tool registry
TOOLS = {
    "calculator": {
        "function": calculator,
        "description": "Performs basic math (addition/subtraction). Input: expression like '5+3'"
    },
    "text_utility": {
        "function": text_utility,
        "description": "Text operations. Input: JSON with {\"text\": \"hello\", \"operation\": \"reverse\"} or \"count\""
    },
    "datetime_tool": {
        "function": datetime_tool,
        "description": "Get current date/time. Input: operation 'current', 'date', or 'time'"
    },
    "string_analyzer": {
        "function": string_analyzer,
        "description": "Analyze text statistics. Input: any text string"
    },
    "temperature_converter": {
        "function": temperature_converter,
        "description": "Convert temperature. Input: JSON with {\"value\": \"25\", \"from_unit\": \"C\", \"to_unit\": \"F\"}"
    },
    "list_helper": {
        "function": list_helper,
        "description": "Sort/analyze lists. Input: JSON with {\"items\": \"a,b,c\", \"operation\": \"sort\"}"
    },
    "case_converter": {
        "function": case_converter,
        "description": "Convert text case. Input: JSON with {\"text\": \"hello\", \"operation\": \"upper/lower/title\"}"
    },
    "number_operations": {
        "function": number_operations,
        "description": "Math on number lists. Input: JSON with {\"numbers\": \"10,20,30\", \"operation\": \"sum/average/min/max\"}"
    },
    "validator": {
        "function": validator,
        "description": "Validate data formats. Input: JSON with {\"value\": \"test@email.com\", \"validation_type\": \"email/url/phone/number\"}"
    },
    "random_generator": {
        "function": random_generator,
        "description": "Generate random values. Input: JSON with {\"operation\": \"number/choice/coin/dice\", \"param\": \"optional\"}"
    },
    "unit_converter": {
        "function": unit_converter,
        "description": "Convert units. Input: JSON with {\"value\": \"5\", \"from_unit\": \"km\", \"to_unit\": \"m\"}"
    },
    "world_time": {
        "function": world_time,
        "description": "Get current time for any country/city. Input: country or city name like 'India', 'Japan', 'USA', 'London'"
    }
}


def run_basic_agent(user_input: str) -> str:
    """
    Run the educational agent with a user query.
    
    This function demonstrates how an agent works by:
    1. Receiving user input
    2. Letting the agent think and choose tools
    3. Executing tool actions if needed
    4. Returning the final answer
    
    The agent's reasoning steps are logged to the console for learning.
    
    Args:
        user_input: The user's question or request
        
    Returns:
        The agent's final answer
        
    Examples:
        >>> run_basic_agent("What is 15 + 27?")
        # Agent uses calculator tool
        "15 + 27 equals 42"
        
        >>> run_basic_agent("Reverse the word 'python'")
        # Agent uses text_utility tool
        "The word 'python' reversed is 'nohtyp'"
        
        >>> run_basic_agent("What is the capital of France?")
        # Agent answers directly (no tools needed)
        "The capital of France is Paris"
    """
    
    logger.info("\n" + "="*80)
    logger.info("🤖 AGENT STARTING")
    logger.info("="*80)
    logger.info(f"📝 User Input: {user_input}\n")
    
    try:
        # Initialize the LLM
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            return "Error: GOOGLE_GEMINI_API_KEY not found in environment"
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,  # Low temperature for consistent reasoning
            google_api_key=api_key
        )
        
        # Create the ReAct prompt
        prompt = f"""You are an AI agent that can use tools. You follow the ReAct pattern:
Thought → Action → Observation → Thought → ... → Final Answer

Available Tools:
- calculator: For math operations (addition/subtraction). Input: expression like "5+3"
- text_utility: For text operations. Input: JSON like {{"text": "hello", "operation": "reverse"}} or "count"
- datetime_tool: Get current date/time. Input: operation "current", "date", or "time"
- string_analyzer: Analyze text statistics. Input: any text string
- temperature_converter: Convert temperatures. Input: JSON like {{"value": "25", "from_unit": "C", "to_unit": "F"}}
- list_helper: Sort/analyze comma-separated lists. Input: JSON like {{"items": "a,b,c", "operation": "sort"}}
- case_converter: Convert text case. Input: JSON like {{"text": "hello", "operation": "upper"}}
- number_operations: Operations on number lists. Input: JSON like {{"numbers": "10,20,30", "operation": "sum"}}
- validator: Validate formats. Input: JSON like {{"value": "test@email.com", "validation_type": "email"}}
- random_generator: Generate random values. Input: JSON like {{"operation": "dice", "param": ""}}
- unit_converter: Convert units. Input: JSON like {{"value": "5", "from_unit": "km", "to_unit": "m"}}
- world_time: Get time for countries. Input: country name like "India", "Japan", "USA", "London"
- none: If you can answer directly without tools

User Question: {user_input}

Think step by step. Respond in this JSON format:
{{
  "thought": "your reasoning about what to do",
  "action": "tool_name" or "none",
  "action_input": "the input for the tool (if action is not none)",
  "final_answer": "only fill this if action is none"
}}"""
        
        logger.info("🧠 STEP 1: Agent Reasoning...\n")
        
        # Get agent's decision
        response = llm.invoke(prompt)
        response_text = response.content
        
        # Parse JSON response
        try:
            # Extract JSON from markdown if present
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            elif '```' in response_text:
                response_text = response_text.replace('```', '').strip()
            
            decision = json.loads(response_text)
        except:
            # Fallback: try to parse as is
            decision = json.loads(response_text)
        
        logger.info(f"💭 Thought: {decision.get('thought', 'N/A')}")
        logger.info(f"⚡ Action: {decision.get('action', 'none')}")
        
        # Execute action if needed
        if decision.get('action') == 'none' or not decision.get('action'):
            final_answer = decision.get('final_answer', 'I can answer directly.')
            logger.info(f"✅ Direct Answer (no tools needed)\n")
        else:
            action = decision['action']
            action_input = decision.get('action_input', '')
            
            logger.info(f"🔧 Action Input: {action_input}")
            logger.info(f"\n⚙️  STEP 2: Executing Tool...\n")
            
            # Execute the tool
            if action == 'calculator':
                observation = calculator(action_input)
            elif action == 'text_utility':
                # Parse text_utility input
                if isinstance(action_input, str) and action_input.startswith('{'):
                    input_data = json.loads(action_input)
                    observation = text_utility(input_data['text'], input_data.get('operation', 'reverse'))
                else:
                    observation = text_utility(action_input)
            elif action == 'datetime_tool':
                observation = datetime_tool(action_input)
            elif action == 'string_analyzer':
                observation = string_analyzer(action_input)
            elif action == 'temperature_converter':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = temperature_converter(
                    input_data['value'],
                    input_data['from_unit'],
                    input_data['to_unit']
                )
            elif action == 'list_helper':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = list_helper(
                    input_data['items'],
                    input_data.get('operation', 'sort')
                )
            elif action == 'case_converter':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = case_converter(
                    input_data['text'],
                    input_data.get('operation', 'upper')
                )
            elif action == 'number_operations':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = number_operations(
                    input_data['numbers'],
                    input_data.get('operation', 'sum')
                )
            elif action == 'validator':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = validator(
                    input_data['value'],
                    input_data['validation_type']
                )
            elif action == 'random_generator':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = random_generator(
                    input_data['operation'],
                    input_data.get('param', '')
                )
            elif action == 'unit_converter':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    input_data = action_input
                else:
                    input_data = json.loads(action_input)
                observation = unit_converter(
                    input_data['value'],
                    input_data['from_unit'],
                    input_data['to_unit']
                )
            elif action == 'world_time':
                # Handle both dict and string input
                if isinstance(action_input, dict):
                    country = action_input.get('country', action_input)
                else:
                    country = action_input
                observation = world_time(country)
            else:
                observation = f"Unknown tool: {action}"
            
            logger.info(f"👁️  Observation: {observation}\n")
            logger.info(f"🧠 STEP 3: Generating Final Answer...\n")
            
            # Get final answer based on observation
            final_prompt = f"""Based on this information:

User Question: {user_input}
Tool Used: {action}
Tool Result: {observation}

Provide a clear, concise final answer to the user."""

            final_response = llm.invoke(final_prompt)
            final_answer = final_response.content
        
        logger.info("="*80)
        logger.info("✅ AGENT FINISHED")
        logger.info("="*80)
        logger.info(f"💡 Final Answer: {final_answer}\n")
        
        return final_answer
        
    except Exception as e:
        error_msg = f"Agent error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        import traceback
        logger.error(traceback.format_exc())
        return error_msg


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE USAGE & TESTING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("\n" + "🎓 EDUCATIONAL AGENT DEMO".center(80, "="))
    print("This demo shows how an agent thinks and uses tools\n")
    
    # Test Case 1: Calculator tool
    print("\n📋 TEST 1: Math Problem (calculator tool)")
    print("-" * 80)
    result1 = run_basic_agent("What is 45 + 67?")
    print(f"\nResult: {result1}")
    
    # Test Case 2: Text tool
    print("\n\n📋 TEST 2: Text Manipulation (text_utility tool)")
    print("-" * 80)
    result2 = run_basic_agent("Reverse the word 'LangChain'")
    print(f"\nResult: {result2}")
    
    # Test Case 3: DateTime tool
    print("\n\n📋 TEST 3: Current Date/Time (datetime_tool)")
    print("-" * 80)
    result3 = run_basic_agent("What is the current date and time?")
    print(f"\nResult: {result3}")
    
    # Test Case 4: String analyzer
    print("\n\n📋 TEST 4: Text Analysis (string_analyzer)")
    print("-" * 80)
    result4 = run_basic_agent("Analyze the text 'Hello World 123'")
    print(f"\nResult: {result4}")
    
    # Test Case 5: Temperature converter
    print("\n\n📋 TEST 5: Temperature Conversion (temperature_converter)")
    print("-" * 80)
    result5 = run_basic_agent("Convert 25 Celsius to Fahrenheit")
    print(f"\nResult: {result5}")
    
    # Test Case 6: List helper
    print("\n\n📋 TEST 6: List Operations (list_helper)")
    print("-" * 80)
    result6 = run_basic_agent("Sort this list: banana, apple, cherry, date")
    print(f"\nResult: {result6}")
    
    # Test Case 7: No tool needed
    print("\n\n📋 TEST 7: General Knowledge (no tools needed)")
    print("-" * 80)
    result7 = run_basic_agent("What is an agent in LangChain?")
    print(f"\nResult: {result7}")
    
    print("\n\n" + "="*80)
    print("🎉 DEMO COMPLETE - Now you can see agents with multiple tools!")
    print("="*80 + "\n")
