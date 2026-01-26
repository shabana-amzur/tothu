# 🚀 Testing Agent Mode in the Chatbot

## ✅ Servers Running

- **Backend**: http://localhost:8001
- **Frontend**: http://localhost:3000
- **Agent Test Page**: http://localhost:3000/agent

## 🎯 How to Test Agent Mode

### Option 1: Dedicated Agent Test Page (Recommended)

1. **Open the Agent Test Page**: http://localhost:3000/agent

2. **Try these example queries**:
   - **Math calculations**:
     - "What is 45 + 67?"
     - "Calculate 100 - 37"
     - "What's 523 + 189?"
   
   - **Text manipulation**:
     - "Reverse the word 'Hello'"
     - "Reverse 'LangChain'"
     - "How many words are in 'Hello World from LangChain'"
   
   - **General knowledge** (no agent needed):
     - "What is artificial intelligence?"
     - "Explain machine learning"

3. **Toggle between modes**:
   - **🤖 Agent Mode**: Uses tools (calculator, text utilities)
   - **💬 Chat Mode**: Direct LLM response without tools

### Option 2: Use the Main Chat Interface

You can also test agent mode from the regular chat by sending a POST request:

```bash
# Get your auth token first (login at http://localhost:3000/login)

# Test with agent mode
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "What is 45 + 67?",
    "use_agent": true
  }'

# Test without agent mode
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "What is 45 + 67?",
    "use_agent": false
  }'
```

## 🔍 What to Observe

### Agent Mode Behavior:

When you send: **"What is 45 + 67?"** with agent mode:

1. **Backend logs** show:
   ```
   🤖 Using AGENT mode for user xxx@email.com
   ================================================================================
   🤖 AGENT STARTING
   ================================================================================
   📝 User Input: What is 45 + 67?
   
   🧠 STEP 1: Agent Reasoning...
   💭 Thought: This is a math problem, I should use the calculator
   ⚡ Action: calculator
   🔧 Action Input: 45+67
   
   ⚙️ STEP 2: Executing Tool...
   👁️ Observation: 112
   
   🧠 STEP 3: Generating Final Answer...
   ================================================================================
   ✅ AGENT FINISHED
   ================================================================================
   💡 Final Answer: 45 + 67 equals 112
   ```

2. **Response** includes: "45 + 67 equals 112"
3. **Model** shows: "gemini-2.5-flash (Agent Mode)"

### Chat Mode Behavior:

When you send the same message **without agent mode**:

1. LLM responds directly without using tools
2. May give a correct answer, but doesn't use the calculator tool
3. Model shows: "gemini-2.5-flash"

## 📋 Test Cases

### ✅ Tasks that Work BEST with Agent:

| Query | Tool Used | Expected Result |
|-------|-----------|-----------------|
| "What is 45 + 67?" | Calculator | "112" |
| "Calculate 100 - 37" | Calculator | "63" |
| "Reverse the word 'Python'" | Text Utility | "nohtyP" |
| "Count words in 'Hello World'" | Text Utility | "2 words" |

### ✅ Tasks that Work WITHOUT Agent:

| Query | Mode | Expected Result |
|-------|------|-----------------|
| "What is AI?" | Direct Chat | Explanation of AI |
| "Explain Python" | Direct Chat | Description of Python |
| "Tell me a joke" | Direct Chat | A joke |

## 🎨 Frontend Features

The Agent Test Page (`/agent`) includes:

- **Mode Toggle**: Switch between Agent and Chat mode
- **Example Queries**: Pre-built examples you can click
- **Real-time Response**: See agent thinking and results
- **Visual Feedback**: Loading states and mode indicators
- **Info Section**: Explanation of how it works

## 🔧 Backend Changes Made

### 1. **ChatRequest Model** (`backend/app/models/chat.py`)
Added `use_agent` boolean field:
```python
use_agent: bool = Field(
    default=False,
    description="Use agent mode with tools"
)
```

### 2. **Chat Endpoint** (`backend/app/api/chat.py`)
Added routing logic:
```python
if request.use_agent:
    logger.info(f"🤖 Using AGENT mode")
    agent_response = run_basic_agent(request.message)
    result = {"message": agent_response, "model": "gemini-2.5-flash (Agent Mode)"}
else:
    # Normal chat flow
```

## 🚀 Quick Test Commands

```bash
# 1. Make sure you're logged in at http://localhost:3000/login

# 2. Open the agent test page
open http://localhost:3000/agent

# 3. Try these queries:
#    - "What is 45 + 67?"           → Should use calculator
#    - "Reverse 'Hello'"            → Should use text utility
#    - "What is Python?"            → Can answer directly
```

## 📊 Monitoring Agent Decisions

Watch the **backend terminal** to see the agent's reasoning in real-time:

```bash
# Watch backend logs
tail -f /tmp/backend.log

# Or run backend in foreground to see live logs:
cd /Users/ferozshaik/Desktop/Tothu/backend
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 🎓 Learning Points

1. **Agent vs Chain**:
   - Agent: Makes decisions, uses tools dynamically
   - Chain: Fixed sequence, no tool usage

2. **ReAct Pattern** (visible in logs):
   - **Thought**: Agent analyzes the problem
   - **Action**: Chooses a tool (or none)
   - **Observation**: Reviews tool results
   - **Final Answer**: Generates response

3. **When to Use Agent**:
   - ✅ Math calculations
   - ✅ Text manipulation
   - ✅ Tasks requiring external tools
   - ❌ Simple knowledge questions (use direct chat)

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ Agent test page loads at http://localhost:3000/agent
2. ✅ Math queries return correct calculations
3. ✅ Text queries show reversed text or word counts
4. ✅ Backend logs show agent reasoning steps
5. ✅ Response indicates "Agent Mode" in the model field

## 🐛 Troubleshooting

**If agent test page shows error:**
- Make sure you're logged in first at http://localhost:3000/login
- Check that backend is running: `curl http://localhost:8001/docs`

**If agent doesn't use tools:**
- Check backend logs: `tail -f /tmp/backend.log`
- Verify `use_agent: true` in the request
- Make sure query requires a tool (math or text manipulation)

**If servers aren't running:**
```bash
cd /Users/ferozshaik/Desktop/Tothu
./start_all.sh
```

---

**Ready to test!** 🎯

Start at: **http://localhost:3000/agent**
