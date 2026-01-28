# Django + Claude Opus 4.5 Agent Integration - Implementation Guide

## Overview
I want to add a genAI assistant to OpenHEXA. I would like this to live in a new Django app called "assistant".
This app should integrate Claude Opus 4.5 as an intelligent agent with access to user-specific file systems (FUSE-mounted buckets) and PostgreSQL databases.

## Architecture Summary

### Request Flow
```
User Message → Django View → Agent Service → Anthropic API (Claude Opus 4.5)
                                ↓
                    Tool Execution (Files/Database)
                                ↓
                    Tool Results → Claude → Final Response
                                ↓
                    Save to Database → Return to User
```

## Core Components

### 1. Database Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Cost tracking
    total_input_tokens = models.IntegerField(default=0)
    total_output_tokens = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10)  # 'user' or 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Usage tracking per message
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    class Meta:
        ordering = ['created_at']

class ToolExecution(models.Model):
    """Track tool usage for debugging and analytics"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    tool_name = models.CharField(max_length=100)
    tool_input = models.JSONField()
    tool_output = models.JSONField()
    executed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
```

### 2. Tool Definitions

```python
# tools.py

def get_file_system_tools():
    """Define tools for interacting with user's file system"""
    return [
        {
            "name": "list_files",
            "description": "List files and directories in the user's file system",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to directory, e.g., '/documents'"
                    }
                },
                "required": []
            }
        },
        {
            "name": "read_file",
            "description": "Read contents of a text file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full path to file"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Create or overwrite a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "search_files",
            "description": "Search for files by pattern",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern like '*.pdf'"
                    },
                    "path": {"type": "string"}
                },
                "required": ["pattern"]
            }
        }
    ]

def get_database_tools():
    """Define tools for database operations"""
    return [
        {
            "name": "query_database",
            "description": "Execute SELECT query on user's PostgreSQL database. Only SELECT queries allowed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 100}
                },
                "required": ["query"]
            }
        },
        {
            "name": "describe_tables",
            "description": "Get schema information for database tables",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"}
                },
                "required": []
            }
        }
    ]
```

### 3. Tool Executors

Analyze the codebase and make a first draft implementation of these tools.

### 4. Agent Service

```python
# services/agent_service.py
from anthropic import Anthropic
from django.conf import settings
import json
from ..models import Message, ToolExecution
from ..tools import get_file_system_tools, get_database_tools
from ..tool_executors import UserFileSystemTools, UserDatabaseTools

class AgentService:
    INPUT_PRICE_PER_MILLION = 5.00
    OUTPUT_PRICE_PER_MILLION = 25.00

    def __init__(self, user, conversation):
        self.user = user
        self.conversation = conversation
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.fs_tools = UserFileSystemTools(user)
        self.db_tools = UserDatabaseTools(user)

    def execute_tool(self, tool_name, tool_input):
        """Route tool execution to appropriate handler"""

        # File system tools
        if tool_name == "list_files":
            result = self.fs_tools.list_files(tool_input.get('path', ''))
        elif tool_name == "read_file":
            result = self.fs_tools.read_file(tool_input['path'])
        elif tool_name == "write_file":
            result = self.fs_tools.write_file(tool_input['path'], tool_input['content'])
        elif tool_name == "search_files":
            result = self.fs_tools.search_files(
                tool_input['pattern'],
                tool_input.get('path', '')
            )

        # Database tools
        elif tool_name == "query_database":
            result = self.db_tools.query_database(
                tool_input['query'],
                tool_input.get('limit', 100)
            )
        elif tool_name == "describe_tables":
            result = self.db_tools.describe_tables(tool_input.get('table_name'))

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        # Log tool execution
        ToolExecution.objects.create(
            conversation=self.conversation,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=result,
            success='error' not in result
        )

        return result

    def send_message(self, user_message):
        """Send message with full tool use support"""

        # Build conversation history from database
        messages = []
        for msg in self.conversation.messages.all():
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add new user message
        messages.append({"role": "user", "content": user_message})

        # Get all tools
        tools = get_file_system_tools() + get_database_tools()

        # System prompt
        system = """You are a helpful AI assistant with access to the user's file system and PostgreSQL database.

You can:
- List, read, write, and search files in their personal file system
- Query their database with SELECT statements
- Explore database schemas

Always explain what you're doing with tools. Ask for confirmation before writing files or making changes."""

        # Initial API call
        response = self.client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=4096,
            system=system,
            tools=tools,
            messages=messages
        )

        # Track usage
        total_input_tokens = response.usage.input_tokens
        total_output_tokens = response.usage.output_tokens

        # Tool use loop - Claude might need multiple tool calls
        while response.stop_reason == "tool_use":
            # Get all tool uses from this response
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # Execute each tool
            tool_results = []
            for tool_use in tool_uses:
                result = self.execute_tool(tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result)
                })

            # Continue conversation with tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            response = self.client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=4096,
                system=system,
                tools=tools,
                messages=messages
            )

            # Accumulate token usage
            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                final_text += block.text

        # Calculate cost
        cost = (
            (total_input_tokens / 1_000_000) * self.INPUT_PRICE_PER_MILLION +
            (total_output_tokens / 1_000_000) * self.OUTPUT_PRICE_PER_MILLION
        )

        # Save user message
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content=user_message
        )

        # Save assistant message with usage data
        Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content=final_text,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            cost=cost
        )

        # Update conversation totals
        self.conversation.total_input_tokens += total_input_tokens
        self.conversation.total_output_tokens += total_output_tokens
        self.conversation.estimated_cost += cost
        self.conversation.save()

        return {
            'response': final_text,
            'usage': {
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'cost': float(cost)
            }
        }
```

### 5. Views

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Conversation
from .services.agent_service import AgentService

@login_required
@require_http_methods(["POST"])
def create_conversation(request):
    """Start a new conversation"""
    conversation = Conversation.objects.create(user=request.user)
    return JsonResponse({
        'conversation_id': conversation.id,
        'created_at': conversation.created_at
    })

@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Send a message in an existing conversation"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)

    message = request.POST.get('message')
    if not message:
        return JsonResponse({'error': 'Message required'}, status=400)

    # Create agent and send message
    agent = AgentService(request.user, conversation)
    result = agent.send_message(message)

    return JsonResponse(result)

@login_required
def get_conversation(request, conversation_id):
    """Get conversation history"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)

    messages = [
        {
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at,
            'tokens': {
                'input': msg.input_tokens,
                'output': msg.output_tokens
            } if msg.input_tokens else None
        }
        for msg in conversation.messages.all()
    ]

    return JsonResponse({
        'conversation_id': conversation.id,
        'messages': messages,
        'total_cost': float(conversation.estimated_cost),
        'total_tokens': {
            'input': conversation.total_input_tokens,
            'output': conversation.total_output_tokens
        }
    })

@login_required
def list_conversations(request):
    """List user's conversations"""
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')

    return JsonResponse({
        'conversations': [
            {
                'id': conv.id,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at,
                'message_count': conv.messages.count(),
                'cost': float(conv.estimated_cost)
            }
            for conv in conversations
        ]
    })
```

### 6. URLs

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.create_conversation, name='create_conversation'),
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('conversations/<int:conversation_id>/messages/', views.send_message, name='send_message'),
    path('conversations/list/', views.list_conversations, name='list_conversations'),
]
```

### 7. Settings

```python
# settings.py

# Anthropic API
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Install required package
# pip install anthropic
```

### 8. Django Admin

Add admin views for the conversations, allowing super users to get an overview. Also display the token use and cost on these admin pages.

### 9. Frontend

I would like a dedicated page where I can converse with the agent. Let's start with a very simple page, adhering to this project's code style.

## Key Concepts

### Conversation History Management
- **Claude is stateless** - you must send full conversation history with each request
- Store messages in database and rebuild the history for each API call

### Cost Tracking
- Every API response includes `usage.input_tokens` and `usage.output_tokens`
- Calculate cost: `(tokens / 1,000,000) * price_per_million`
- Store per-message and per-conversation totals

### Tool Use Flow
1. Claude receives message and decides to use tools
2. Your code executes the tools (file system, database operations)
3. Results sent back to Claude
4. Claude may use more tools or provide final response
5. Loop continues until `stop_reason != "tool_use"`

## Security Checklist

- [ ] Validate user owns the conversation before allowing access
- [ ] Restrict file system access to user's bucket only
- [ ] Prevent path traversal attacks (`..` in paths)
- [ ] Only allow SELECT queries (no DROP, DELETE without explicit tools)
- [ ] Set file size limits for reads
- [ ] Sanitize database query inputs
- [ ] Log all tool executions for audit trail
