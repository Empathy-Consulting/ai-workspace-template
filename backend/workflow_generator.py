#!/usr/bin/env python3
"""
n8n Workflow Generator
Генерация workflows из описаний процессов
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


def create_workflow_template(name: str, description: str = "") -> Dict[str, Any]:
    """Создать базовый шаблон workflow"""
    return {
        "name": name,
        "nodes": [],
        "connections": {},
        "active": False,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": "1",
        "meta": {
            "instanceId": "ai-workspace",
            "description": description,
            "createdAt": datetime.now().isoformat()
        }
    }


def add_trigger_node(workflow: Dict, trigger_type: str, config: Dict = None) -> str:
    """Добавить триггер в workflow"""
    node_id = f"trigger_{len(workflow['nodes'])}"
    
    triggers = {
        "email": {
            "type": "n8n-nodes-base.gmailTrigger",
            "name": "Gmail Trigger",
            "parameters": {
                "pollTimes": {"item": [{"mode": "everyMinute"}]},
                "simple": False
            }
        },
        "schedule": {
            "type": "n8n-nodes-base.scheduleTrigger",
            "name": "Schedule Trigger",
            "parameters": {
                "rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}
            }
        },
        "webhook": {
            "type": "n8n-nodes-base.webhook",
            "name": "Webhook",
            "parameters": {
                "httpMethod": "POST",
                "path": "webhook"
            }
        },
        "form": {
            "type": "n8n-nodes-base.formTrigger",
            "name": "Form Trigger",
            "parameters": {}
        }
    }
    
    node = {
        "id": node_id,
        "position": [250, 300],
        **triggers.get(trigger_type, triggers["webhook"])
    }
    
    if config:
        node["parameters"].update(config)
    
    workflow["nodes"].append(node)
    return node_id


def add_action_node(workflow: Dict, action_type: str, config: Dict = None, position: int = 1) -> str:
    """Добавить действие в workflow"""
    node_id = f"action_{len(workflow['nodes'])}"
    
    actions = {
        "notion_create": {
            "type": "n8n-nodes-base.notion",
            "name": "Create Notion Page",
            "parameters": {
                "operation": "create",
                "resource": "page"
            }
        },
        "slack_message": {
            "type": "n8n-nodes-base.slack",
            "name": "Send Slack Message",
            "parameters": {
                "operation": "message",
                "resource": "message"
            }
        },
        "gmail_send": {
            "type": "n8n-nodes-base.gmail",
            "name": "Send Email",
            "parameters": {
                "operation": "send",
                "resource": "message"
            }
        },
        "sheets_append": {
            "type": "n8n-nodes-base.googleSheets",
            "name": "Append to Sheet",
            "parameters": {
                "operation": "append",
                "resource": "sheet"
            }
        },
        "http_request": {
            "type": "n8n-nodes-base.httpRequest",
            "name": "HTTP Request",
            "parameters": {
                "method": "POST"
            }
        }
    }
    
    node = {
        "id": node_id,
        "position": [250 + (position * 200), 300],
        **actions.get(action_type, actions["http_request"])
    }
    
    if config:
        node["parameters"].update(config)
    
    workflow["nodes"].append(node)
    return node_id


def add_condition_node(workflow: Dict, conditions: List[Dict], position: int = 1) -> str:
    """Добавить условие IF в workflow"""
    node_id = f"condition_{len(workflow['nodes'])}"
    
    node = {
        "id": node_id,
        "type": "n8n-nodes-base.if",
        "name": "IF",
        "position": [250 + (position * 200), 300],
        "parameters": {
            "conditions": {
                "string": conditions
            }
        }
    }
    
    workflow["nodes"].append(node)
    return node_id


def connect_nodes(workflow: Dict, from_node: str, to_node: str, output_index: int = 0):
    """Соединить два узла"""
    if from_node not in workflow["connections"]:
        workflow["connections"][from_node] = {"main": [[]]}
    
    while len(workflow["connections"][from_node]["main"]) <= output_index:
        workflow["connections"][from_node]["main"].append([])
    
    workflow["connections"][from_node]["main"][output_index].append({
        "node": to_node,
        "type": "main",
        "index": 0
    })


def save_workflow(workflow: Dict, filename: str):
    """Сохранить workflow в файл"""
    os.makedirs("backend/workflows", exist_ok=True)
    filepath = f"backend/workflows/{filename}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Workflow сохранен: {filepath}")
    return filepath


def generate_email_to_notion_workflow(
    workflow_name: str,
    email_filter: str = "",
    notion_database: str = "",
    slack_channel: str = ""
) -> Dict:
    """Генерация workflow: Email → Notion + Slack"""
    
    workflow = create_workflow_template(
        name=workflow_name,
        description="Автоматическое создание задач из писем"
    )
    
    # Trigger
    trigger_id = add_trigger_node(workflow, "email", {
        "filters": {"subject": email_filter} if email_filter else {}
    })
    
    # Create Notion page
    notion_id = add_action_node(workflow, "notion_create", {
        "databaseId": notion_database,
        "title": "={{ $json.subject }}",
        "content": "={{ $json.body }}"
    }, position=1)
    
    connect_nodes(workflow, trigger_id, notion_id)
    
    # Send Slack notification
    if slack_channel:
        slack_id = add_action_node(workflow, "slack_message", {
            "channel": slack_channel,
            "text": "📧 Новая заявка: {{ $json.subject }}"
        }, position=2)
        
        connect_nodes(workflow, notion_id, slack_id)
    
    return workflow


# Пример использования
if __name__ == "__main__":
    # Создаем пример workflow
    workflow = generate_email_to_notion_workflow(
        workflow_name="Обработка заявок",
        email_filter="support",
        slack_channel="#support"
    )
    
    save_workflow(workflow, "email-to-notion")
    
    print("\n📋 Созданный workflow:")
    print(json.dumps(workflow, indent=2, ensure_ascii=False))
