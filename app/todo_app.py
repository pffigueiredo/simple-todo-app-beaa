from nicegui import ui
from app.todo_service import TodoService
from app.models import TodoItemCreate


def create():
    """Create the todo application pages."""

    # Apply modern theme
    ui.colors(
        primary="#2563eb",  # Professional blue
        secondary="#64748b",  # Subtle gray
        accent="#10b981",  # Success green
        positive="#10b981",
        negative="#ef4444",  # Error red
        warning="#f59e0b",  # Warning amber
        info="#3b82f6",  # Info blue
    )

    todo_service = TodoService()

    @ui.page("/")
    def todo_page():
        """Main todo application page."""

        # Page header
        with ui.row().classes("w-full justify-center mb-8"):
            ui.label("📝 Todo App").classes("text-4xl font-bold text-primary")

        # Main container
        with ui.column().classes("w-full max-w-4xl mx-auto p-6"):
            # Add new todo section
            with ui.card().classes("w-full p-6 mb-6 shadow-lg rounded-xl bg-white"):
                ui.label("Add New Todo").classes("text-xl font-bold mb-4 text-gray-800")

                with ui.row().classes("w-full gap-4"):
                    title_input = ui.input(placeholder="Enter todo title...").classes("flex-1").props("outlined dense")

                    description_input = (
                        ui.input(placeholder="Description (optional)...").classes("flex-1").props("outlined dense")
                    )

                    ui.button("Add Todo", on_click=lambda: add_todo()).classes(
                        "bg-primary text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                    )

            # Todo list container
            todo_list_container = ui.column().classes("w-full gap-4")

            def refresh_todos():
                """Refresh the todo list display."""
                todo_list_container.clear()
                todos = todo_service.get_all_todos()

                if not todos:
                    with todo_list_container:
                        with ui.card().classes("w-full p-8 text-center shadow-md rounded-lg bg-gray-50"):
                            ui.label("No todos yet! Add one above to get started.").classes("text-gray-500 text-lg")
                    return

                with todo_list_container:
                    for todo in todos:
                        create_todo_card(todo)

            def create_todo_card(todo):
                """Create a card for a single todo item."""
                with ui.card().classes("w-full p-4 shadow-md rounded-lg bg-white hover:shadow-lg transition-shadow"):
                    with ui.row().classes("w-full items-center gap-4"):
                        # Completion checkbox
                        ui.checkbox(
                            value=todo.completed,
                            on_change=lambda e, todo_id=todo.id: toggle_completion(todo_id) if todo_id else None,
                        ).classes("flex-shrink-0")

                        # Todo content
                        with ui.column().classes("flex-1"):
                            # Title with strikethrough if completed
                            title_classes = "text-lg font-semibold"
                            if todo.completed:
                                title_classes += " line-through text-gray-400"
                            else:
                                title_classes += " text-gray-800"

                            ui.label(todo.title).classes(title_classes)

                            # Description if exists
                            if todo.description.strip():
                                desc_classes = "text-sm text-gray-600"
                                if todo.completed:
                                    desc_classes += " line-through text-gray-400"
                                ui.label(todo.description).classes(desc_classes)

                            # Created date
                            created_date = todo.created_at.strftime("%B %d, %Y at %I:%M %p")
                            ui.label(f"Created: {created_date}").classes("text-xs text-gray-400 mt-1")

                        # Action buttons
                        with ui.row().classes("gap-2 flex-shrink-0"):
                            ui.button(
                                "🗑️", on_click=lambda e, todo_id=todo.id: delete_todo(todo_id) if todo_id else None
                            ).classes("text-red-500 hover:bg-red-50 rounded-full p-2").props("flat dense")

            async def add_todo():
                """Add a new todo item."""
                title = title_input.value.strip()
                description = description_input.value.strip()

                if not title:
                    ui.notify("Please enter a todo title", type="warning")
                    return

                try:
                    todo_data = TodoItemCreate(title=title, description=description)
                    todo_service.create_todo(todo_data)

                    # Clear inputs
                    title_input.set_value("")
                    description_input.set_value("")

                    # Refresh the list
                    refresh_todos()

                    ui.notify("Todo added successfully!", type="positive")

                except Exception as e:
                    ui.notify(f"Error adding todo: {str(e)}", type="negative")

            def toggle_completion(todo_id: int):
                """Toggle the completion status of a todo."""
                try:
                    todo_service.toggle_todo_completion(todo_id)
                    refresh_todos()
                    ui.notify("Todo updated!", type="positive")
                except Exception as e:
                    ui.notify(f"Error updating todo: {str(e)}", type="negative")

            async def delete_todo(todo_id: int):
                """Delete a todo item with confirmation."""
                with ui.dialog() as dialog, ui.card():
                    ui.label("Delete Todo").classes("text-lg font-bold mb-4")
                    ui.label("Are you sure you want to delete this todo item?").classes("mb-4")

                    with ui.row().classes("gap-2 justify-end"):
                        ui.button("Cancel", on_click=lambda: dialog.submit("cancel")).props("outline")
                        ui.button("Delete", on_click=lambda: dialog.submit("delete")).classes("bg-red-500 text-white")

                result = await dialog

                if result == "delete":
                    try:
                        success = todo_service.delete_todo(todo_id)
                        if success:
                            refresh_todos()
                            ui.notify("Todo deleted successfully!", type="positive")
                        else:
                            ui.notify("Todo not found", type="warning")
                    except Exception as e:
                        ui.notify(f"Error deleting todo: {str(e)}", type="negative")

            # Handle Enter key for quick add
            title_input.on("keydown.enter", lambda: add_todo())
            description_input.on("keydown.enter", lambda: add_todo())

            # Initial load
            refresh_todos()
