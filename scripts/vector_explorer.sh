#!/bin/bash
# Vector Database Explorer Scripts
# Unix/Linux/macOS shell script to run vector database exploration commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "================================================"
echo "SportzVillage Vector Database Explorer"
echo "================================================"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1. Explore vector database collections"
    echo "2. Test semantic search (predefined queries)"
    echo "3. Test custom semantic search query"
    echo "4. Show database statistics"
    echo "5. Populate/refresh vector database"
    echo "6. Reset vector database (DANGER!)"
    echo "7. Exit"
    echo ""
}

while true; do
    show_menu
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            echo ""
            echo "================================================"
            echo "Exploring Vector Database Collections"
            echo "================================================"
            python scripts/explore_vectordb.py
            read -p "Press Enter to continue..."
            ;;
        2)
            echo ""
            echo "================================================"
            echo "Testing Semantic Search"
            echo "================================================"
            python scripts/test_semantic_search.py
            read -p "Press Enter to continue..."
            ;;
        3)
            echo ""
            echo "================================================"
            echo "Custom Semantic Search"
            echo "================================================"
            read -p "Enter your search query: " query
            python scripts/test_semantic_search.py --query "$query"
            read -p "Press Enter to continue..."
            ;;
        4)
            echo ""
            echo "================================================"
            echo "Vector Database Statistics"
            echo "================================================"
            python scripts/manage_vectordb.py stats
            read -p "Press Enter to continue..."
            ;;
        5)
            echo ""
            echo "================================================"
            echo "Populating Vector Database"
            echo "================================================"
            python scripts/manage_vectordb.py populate
            read -p "Press Enter to continue..."
            ;;
        6)
            echo ""
            echo "================================================"
            echo "DANGER: Reset Vector Database"
            echo "================================================"
            python scripts/manage_vectordb.py reset
            read -p "Press Enter to continue..."
            ;;
        7)
            echo ""
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done