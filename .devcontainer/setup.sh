#!/bin/bash
set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           🚀 AI Automation Workspace Setup                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════
# 1. SYSTEM UPDATES
# ═══════════════════════════════════════════════════════════
echo "📦 [1/5] Обновление системы..."
sudo apt-get update -qq

# ═══════════════════════════════════════════════════════════
# 2. BMAD METHOD (Core Framework)
# ═══════════════════════════════════════════════════════════
echo "🧠 [2/5] Установка BMAD Method..."
if npx bmad-method@alpha install --quiet; then
    echo "   ✅ BMAD Method установлен"
else
    echo "   ⚠️  BMAD Method: установка продолжится в фоне"
fi

# ═══════════════════════════════════════════════════════════
# 3. COMPOSIO (Integration Layer)
# ═══════════════════════════════════════════════════════════
echo "🔗 [3/5] Установка Composio..."

# Node CLI
if npm install -g @composio/cli; then
    echo "   ✅ Composio CLI установлен"
else
    echo "   ⚠️  Composio CLI: ошибка установки"
fi

# Python SDK
if pip install composio-core composio-langchain --break-system-packages -q; then
    echo "   ✅ Composio Python SDK установлен"
else
    echo "   ⚠️  Composio Python: ошибка установки"
fi

# ═══════════════════════════════════════════════════════════
# 4. ADDITIONAL DEPENDENCIES
# ═══════════════════════════════════════════════════════════
echo "🔧 [4/5] Дополнительные зависимости..."

# Python packages for workflow generation
pip install python-dotenv requests --break-system-packages -q 2>/dev/null || true

echo "   ✅ Зависимости установлены"

# ═══════════════════════════════════════════════════════════
# 5. CONFIGURATION
# ═══════════════════════════════════════════════════════════
echo "⚙️  [5/5] Настройка окружения..."

# Create .env if not exists
if [ ! -f ".env" ]; then
    cat > .env << EOF
# ═══════════════════════════════════════════════════════════
# AI Workspace Configuration
# ═══════════════════════════════════════════════════════════

# Composio API Key
# Получи на: https://app.composio.dev/settings
# После регистрации скопируй ключ сюда:
COMPOSIO_API_KEY=

# User ID (автоматически определяется)
USER_ID=${GITHUB_USER:-${CODESPACE_NAME:-default_user}}

# ═══════════════════════════════════════════════════════════
EOF
    echo "   ✅ Файл .env создан"
fi

# Make scripts executable
chmod +x backend/*.py 2>/dev/null || true

# ═══════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ Workspace готов!                       ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  📖 Следующие шаги:                                        ║"
echo "║                                                            ║"
echo "║  1. Открой чат (панель снизу или Ctrl+Shift+I)            ║"
echo "║  2. Напиши: 'Привет, помоги настроить'                    ║"
echo "║  3. Агент проведет тебя через подключение сервисов        ║"
echo "║                                                            ║"
echo "║  💡 Или открой README.md для инструкций                   ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
