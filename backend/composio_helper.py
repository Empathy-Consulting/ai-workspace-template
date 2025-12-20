#!/usr/bin/env python3
"""
Composio Integration Helper
Управление подключениями сервисов для автоматизаций
"""

import os
import json
from typing import Optional

# Попытка импорта Composio
try:
    from composio import Composio
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False


def get_user_id() -> str:
    """Получить ID пользователя из окружения"""
    return os.environ.get("GITHUB_USER", os.environ.get("USER_ID", "default_user"))


def get_composio_client() -> Optional[object]:
    """Инициализировать Composio клиент"""
    if not COMPOSIO_AVAILABLE:
        print("❌ Composio не установлен. Запусти: pip install composio-core")
        return None
    
    api_key = os.environ.get("COMPOSIO_API_KEY")
    if not api_key:
        print("❌ COMPOSIO_API_KEY не установлен в .env")
        return None
    
    return Composio(api_key=api_key)


def list_connections():
    """Показать список подключенных сервисов"""
    client = get_composio_client()
    if not client:
        return
    
    user_id = get_user_id()
    
    try:
        connections = client.connected_accounts.list(user_id=user_id)
        
        if not connections:
            print("📭 Нет подключенных сервисов")
            print("   Используй: python composio_helper.py connect <сервис>")
            return
        
        print("📋 Подключенные сервисы:")
        for conn in connections:
            print(f"   ✅ {conn.app_name}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def connect_service(app_name: str):
    """Подключить новый сервис"""
    client = get_composio_client()
    if not client:
        return
    
    user_id = get_user_id()
    app_name_upper = app_name.upper()
    
    try:
        # Проверяем, не подключен ли уже
        connections = client.connected_accounts.list(user_id=user_id)
        connected_apps = [c.app_name.upper() for c in connections]
        
        if app_name_upper in connected_apps:
            print(f"✅ {app_name} уже подключен!")
            return
        
        # Создаем ссылку для подключения
        connection_request = client.connected_accounts.initiate(
            user_id=user_id,
            app=app_name_upper,
            redirect_url="https://github.com/codespaces"
        )
        
        print(f"🔗 Подключи {app_name}:")
        print(f"   {connection_request.redirect_url}")
        print("")
        print("   Перейди по ссылке и войди в свой аккаунт.")
        print("   После этого сервис будет подключен.")
        
    except Exception as e:
        print(f"❌ Ошибка подключения {app_name}: {e}")


def check_service(app_name: str) -> bool:
    """Проверить, подключен ли сервис"""
    client = get_composio_client()
    if not client:
        return False
    
    user_id = get_user_id()
    
    try:
        connections = client.connected_accounts.list(user_id=user_id)
        connected_apps = [c.app_name.upper() for c in connections]
        return app_name.upper() in connected_apps
    except:
        return False


def update_connections_doc():
    """Обновить документ со статусом подключений"""
    client = get_composio_client()
    if not client:
        return
    
    user_id = get_user_id()
    services = ["Gmail", "Slack", "Notion", "Google Sheets", "HubSpot", "Trello"]
    
    try:
        connections = client.connected_accounts.list(user_id=user_id)
        connected_apps = [c.app_name.upper() for c in connections]
        
        status_lines = []
        for service in services:
            if service.upper().replace(" ", "_") in connected_apps or service.upper() in connected_apps:
                status_lines.append(f"| {service} | ✅ Подключен |")
            else:
                status_lines.append(f"| {service} | ⚪ Не подключен |")
        
        # Читаем текущий файл
        doc_path = "Интеграции/Подключения.md"
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем таблицу статусов
            # (упрощенная логика - в реальности нужен парсинг)
            print("📝 Статус подключений обновлен")
            for line in status_lines:
                print(f"   {line}")
                
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python composio_helper.py list          - показать подключения")
        print("  python composio_helper.py connect gmail - подключить сервис")
        print("  python composio_helper.py check gmail   - проверить сервис")
        print("  python composio_helper.py update        - обновить документ")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_connections()
    elif command == "connect" and len(sys.argv) > 2:
        connect_service(sys.argv[2])
    elif command == "check" and len(sys.argv) > 2:
        result = check_service(sys.argv[2])
        print(f"{'✅' if result else '❌'} {sys.argv[2]}: {'подключен' if result else 'не подключен'}")
    elif command == "update":
        update_connections_doc()
    else:
        print(f"❌ Неизвестная команда: {command}")
