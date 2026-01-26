# 🔧 Adding Custom Tools to Your Agent

## ✅ Agent is Extensible!

Your agent now has **6 tools** and you can add **unlimited more**! Here's what's currently available:

### 📦 Built-in Tools

| Tool | Purpose | Example Query |
|------|---------|---------------|
| 🧮 **calculator** | Math operations (+ and -) | "What is 45 + 67?" |
| 📝 **text_utility** | Reverse text or count words | "Reverse the word 'Hello'" |
| 📅 **datetime_tool** | Get current date/time | "What's today's date?" |
| 📊 **string_analyzer** | Text statistics | "Analyze: Python 2024" |
| 🌡️ **temperature_converter** | Temperature conversion | "Convert 25°C to F" |
| 📋 **list_helper** | Sort/count lists | "Sort: dog, cat, bird" |

## 🚀 How to Add Your Own Tool

### Step 1: Create the Tool Function

Add your function to [basic_agent.py](backend/app/services/basic_agent.py):

```python
def your_tool_name(input_param: str) -> str:
    """
    Description of what your tool does.
    
    Args:
        input_param: Description of input
    
    Returns:
        Description of output
        
    Examples:
        your_tool_name("example") → "result"
    """
    try:
        # Your tool logic here
        result = process(input_param)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

### Step 2: Register the Tool

Add it to the `TOOLS` dictionary:

```python
TOOLS = {
    # ... existing tools ...
    "your_tool_name": {
        "function": your_tool_name,
        "description": "Brief description for the agent"
    }
}
```

### Step 3: Update the Agent Prompt

Add your tool to the available tools list:

```python
Available Tools:
- calculator: For math operations...
- your_tool_name: Your tool description
```

### Step 4: Add Tool Execution Logic

In the `run_basic_agent` function, add:

```python
elif action == 'your_tool_name':
    observation = your_tool_name(action_input)
```

## 💡 Example: Weather Tool

Here's a complete example of adding a weather lookup tool:

```python
# Step 1: Create the function
def weather_tool(city: str) -> str:
    """
    Gets weather for a city (mock data for demo).
    
    Args:
        city: City name
    
    Returns:
        Weather information
        
    Examples:
        weather_tool("London") → "London: 15°C, Cloudy"
    """
    try:
        # Mock weather data (in production, call a real API)
        weather_data = {
            "london": "15°C, Cloudy",
            "paris": "18°C, Sunny",
            "tokyo": "22°C, Rainy",
            "newyork": "12°C, Windy"
        }
        
        city_lower = city.lower().replace(" ", "")
        weather = weather_data.get(city_lower, "Weather data not available")
        return f"{city}: {weather}"
    except Exception as e:
        return f"Error: {str(e)}"

# Step 2: Register it
TOOLS = {
    # ... existing tools ...
    "weather_tool": {
        "function": weather_tool,
        "description": "Get weather for a city. Input: city name"
    }
}

# Step 3: Update prompt
Available Tools:
- weather_tool: Get weather for a city. Input: city name
- calculator: For math operations...

# Step 4: Add execution
elif action == 'weather_tool':
    observation = weather_tool(action_input)
```

Now you can ask: **"What's the weather in London?"** and the agent will use the tool!

## 🎯 Real-World Tool Ideas

Here are tools you could add:

### 🌐 API Integration Tools
```python
def search_web(query: str) -> str:
    """Search the web using Google/Bing API"""
    
def get_stock_price(symbol: str) -> str:
    """Get current stock price from finance API"""
    
def translate_text(text: str, target_lang: str) -> str:
    """Translate text using translation API"""
```

### 💾 Database Tools
```python
def query_database(sql: str) -> str:
    """Execute SQL query on your database"""
    
def search_documents(query: str) -> str:
    """Search through uploaded documents"""
```

### 🔧 Utility Tools
```python
def validate_email(email: str) -> str:
    """Check if email format is valid"""
    
def generate_uuid() -> str:
    """Generate a unique ID"""
    
def hash_password(password: str) -> str:
    """Hash a password securely"""
```

### 📊 Data Processing Tools
```python
def csv_to_json(csv_data: str) -> str:
    """Convert CSV to JSON format"""
    
def summarize_text(text: str) -> str:
    """Create a summary of long text"""
```

### 🎨 Creative Tools
```python
def generate_image_prompt(description: str) -> str:
    """Generate DALL-E prompt from description"""
    
def color_to_hex(color_name: str) -> str:
    """Convert color name to hex code"""
```

## 🧪 Testing Your New Tool

### Option 1: Direct Test
```python
python -c "
from app.services.basic_agent import run_basic_agent
result = run_basic_agent('Your test query')
print(result)
"
```

### Option 2: In the Chatbot
1. Open http://localhost:3000
2. Toggle **🤖 Agent Mode ON**
3. Ask a question that requires your tool
4. Watch backend logs to see the agent's reasoning

## 📝 Tool Best Practices

### ✅ Do's:
- **Keep tools focused** - One tool = one clear purpose
- **Return strings** - Always return string results
- **Handle errors** - Use try/except blocks
- **Add descriptions** - Help the agent understand when to use it
- **Provide examples** - Show expected input/output format

### ❌ Don'ts:
- **Don't make tools too complex** - Break into smaller tools
- **Don't assume input format** - Validate and parse carefully
- **Don't forget error handling** - Always catch exceptions
- **Don't use blocking operations** - Keep tools fast

## 🔍 Debugging Tools

### Watch Agent Reasoning:
```bash
# Backend logs show tool selection
tail -f /tmp/backend.log
```

You'll see:
```
💭 Thought: User wants weather, I should use weather_tool
⚡ Action: weather_tool
🔧 Action Input: London
👁️ Observation: London: 15°C, Cloudy
💡 Final Answer: The weather in London is 15°C and Cloudy
```

### Test Tool Directly:
```python
from app.services.basic_agent import your_tool_name
result = your_tool_name("test_input")
print(result)
```

## 🚀 Advanced: Tools with Multiple Parameters

For tools needing multiple inputs, use JSON:

```python
def send_email(data: str) -> str:
    """Send an email. Input: JSON with {to, subject, body}"""
    try:
        import json
        params = json.loads(data) if isinstance(data, str) else data
        to = params['to']
        subject = params['subject']
        body = params['body']
        # Send email logic...
        return f"Email sent to {to}"
    except Exception as e:
        return f"Error: {str(e)}"
```

Agent will automatically format it:
```
Action Input: {"to": "user@example.com", "subject": "Hello", "body": "Test"}
```

## 📚 Resources

- **LangChain Tools**: https://python.langchain.com/docs/modules/agents/tools/
- **Custom Tools**: https://python.langchain.com/docs/modules/agents/tools/custom_tools
- **Tool Calling**: https://python.langchain.com/docs/modules/model_io/chat/function_calling/

## 🎉 Current Capabilities

Your agent can now:
- ✅ Perform math calculations
- ✅ Manipulate text (reverse, count)
- ✅ Get current date/time
- ✅ Analyze text statistics
- ✅ Convert temperatures
- ✅ Sort and analyze lists
- ✅ **Add unlimited custom tools!**

**The sky is the limit!** 🚀 Add tools for:
- API calls
- Database queries
- File operations
- Image processing
- Web scraping
- Email sending
- And anything else you can code!
