from flask import Blueprint, request, jsonify
from auth.utils import token_required
from models import ToDo, db

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/create', methods=['POST'])
@token_required
def create_todo(current_user):
    try:
        if not request.is_json:
            return jsonify({'message': 'Missing JSON in request', 'success': False}), 400

        todo_data = request.get_json()

        task = todo_data.get('taskName')
        if not task:
            return jsonify({'message': 'Task is required', 'success': False}), 400
        
        due_date = todo_data.get('dueDate')
        
        if not due_date:
            due_date = None
            
        priority = todo_data.get('priority')    

        user_todos = ToDo.query.filter_by(user_id=current_user.id).all()
        order = len(user_todos) + 1

        new_todo = ToDo(task=task, due_date=due_date, priority=priority, order=order, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()

        return jsonify({
            'id': new_todo.id,
            'task': new_todo.task,
            'due_date': new_todo.due_date,
            'is_completed': new_todo.is_completed,
            'priority': new_todo.priority,
            'created_at': new_todo.created_at.isoformat(),
            'message': 'Todo Created Successfully!',
            'success': True
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}', 'success': False}), 500
    
@todos_bp.route('/all', methods=['GET'])
@token_required
def get_all_todos(current_user):
    try:
        sort_order = request.args.get('sortOrder')
        
        if sort_order == 'priority-asc':
            todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.priority.asc(), ToDo.order).all()
        elif sort_order == 'priority-desc':
            todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.priority.desc(), ToDo.order).all()
        elif sort_order == 'due-date-asc':
            todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.due_date.asc(), ToDo.order).all()
        elif sort_order == 'due-date-desc':
            todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.due_date.desc(), ToDo.order).all()
        else:
            todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.order).all()
            
        todo_list = []
        for todo in todos:
            todo_list.append({
                "id": todo.id,
                "task": todo.task,
                "due_date": todo.due_date if todo.due_date else None,
                "is_completed": todo.is_completed,
                "priority": todo.priority,
                "order": todo.order,
                "created_at": todo.created_at
            })
        
        username = current_user.username
            
        return jsonify({"todos": todo_list, "username": username, "success": True}), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}', 'success': False}), 500

@todos_bp.route('/toggle-completion', methods=['PUT'])
@token_required
def toggle_completion(current_user):
    try:
        if not request.is_json:
            return jsonify({'message': 'Missing JSON in request', 'success': False}), 400

        todo_data = request.get_json()
        todo_id = todo_data.get('id')
        current_completion_status = todo_data.get('completed')

        todo_item = ToDo.query.filter_by(id=todo_id, user_id=current_user.id).first()
        if not todo_item:
            return jsonify({'message': 'ToDo item not found', 'success': False}), 404

        todo_item.is_completed = not current_completion_status

        db.session.commit()

        return jsonify({'message': 'ToDo updated successfully', 'todo': {
            'id': todo_item.id,
            'completed': todo_item.completed
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@todos_bp.route('/<int:todoId>', methods=['GET'])
@token_required
def get_todo_by_id(current_user, todoId):
    try:
        todo = ToDo.query.filter_by(id=todoId, user_id=current_user.id).first()
        
        if not todo:
            return jsonify({'message': 'Todo item not found', 'success': False}), 404
        return({
                "id": todo.id,
                "task": todo.task,
                "due_date": todo.due_date if todo.due_date else None,
                "is_completed": todo.is_completed,
                "priority": todo.priority,
                "order": todo.order,
                "created_at": todo.created_at, 
                "success": True
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@todos_bp.route('edit-todo', methods=['PUT'])
@token_required
def edit_todo(current_user):
    try:
        if not request.is_json:
            return jsonify({'message': 'Missing JSON in request', 'success': False}), 400

        todo_data = request.get_json()
        todo_id = todo_data.get('id')
        task = todo_data.get('task')
        if not task:
            return jsonify({'message': 'Task is required', 'success': False}), 400
        due_date = todo_data.get('due_date')
        if not due_date:
            due_date = None
        priority = todo_data.get('priority')    
                
        todo = ToDo.query.filter_by(id=todo_id, user_id=current_user.id).first()
        if not todo:
            return jsonify({'message': 'Todo not found', 'success': False}), 404
        todo.task = task
        todo.due_date = due_date
        todo.priority = priority
        
        db.session.commit()

        return jsonify({'message': 'Todo updated successfully', 'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@todos_bp.route('/remove-todo', methods=['PUT'])
@token_required
def remove_todo(current_user):
    try:
        todo_data = request.json
        if not todo_data:
            return jsonify({'message': 'Missing JSON in request', 'success': False}), 400

        todo_item_id = todo_data.get('todoId')
        todo_item = ToDo.query.filter_by(id=todo_item_id, user_id=current_user.id).first()

        if not todo_item:
            return jsonify({'message': 'ToDo item not found', 'success': False}), 404

        db.session.delete(todo_item)

        remaining_todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.order).all()

        for index, todo in enumerate(remaining_todos):
            todo.order = index + 1

        db.session.commit()

        return jsonify({
            'message': 'Todo removed and remaining todos reordered successfully!',
            'success': True,
            'todos': [{'id': todo.id, 'order': todo.order} for todo in remaining_todos]
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

    
@todos_bp.route('/reorder', methods=['PUT'])
@token_required
def reorder_todos(current_user):
    try:
        if not request.is_json:
            return jsonify({'message': 'Missing JSON in request', 'success': False}), 400

        todo_data = request.get_json()
        todo_id = todo_data.get('todoId')
        move_up = todo_data.get('moveUp')

        if todo_id is None or move_up is None:
            return jsonify({'message': 'Invalid data', 'success': False}), 400

        todo_item = ToDo.query.get(todo_id)
        if not todo_item:
            return jsonify({'message': 'ToDo item not found', 'success': False}), 404


        todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.order).all()

        current_index = todos.index(todo_item)

        if move_up and current_index > 0:
            swap_index = current_index - 1
        elif not move_up and current_index < len(todos) - 1:
            swap_index = current_index + 1
        else:
            return jsonify({'message': 'No change in order', 'success': False}), 200

        swap_item = todos[swap_index]
        todo_item.order, swap_item.order = swap_item.order, todo_item.order

        db.session.commit()

        updated_todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.order).all()
        updated_todo_list = [{                
                "id": todo.id,
                "task": todo.task,
                "due_date": todo.due_date if todo.due_date else None,
                "is_completed": todo.is_completed,
                "priority": todo.priority,
                "order": todo.order,
                "created_at": todo.created_at
                } 
                for todo in updated_todos
            ]

        return jsonify({
            'message': 'ToDo reordered successfully',
            'success': True,
            'todos': updated_todo_list
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500