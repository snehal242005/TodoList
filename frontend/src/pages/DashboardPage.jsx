import { useEffect } from 'react';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import TodoForm from '../components/TodoForm';
import TodoCard from '../components/TodoCard';
import Loader from '../components/Loader';
import { useTodos } from '../hooks/useTodos';
import { getErrorMessage } from '../utils/helpers';
import '../styles/dashboard.css';

export default function DashboardPage() {
  const { todos, loading, fetchTodos, createTodo, updateTodo, deleteTodo, toggleTodo } =
    useTodos();

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleCreate = async (title, description) => {
    await createTodo(title, description);
  };

  const handleUpdate = async (id, data) => {
    await updateTodo(id, data);
  };

  const handleDelete = async (id) => {
    await deleteTodo(id);
  };

  const handleToggle = async (todo) => {
    try {
      await toggleTodo(todo);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const pending = todos.filter((t) => !t.completed);
  const completed = todos.filter((t) => t.completed);

  return (
    <div className="dashboard">
      <Navbar />

      <main className="dashboard-main">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1 className="dashboard-title">My Todos</h1>
            <span className="dashboard-count">
              {pending.length} pending · {completed.length} done
            </span>
          </div>

          <TodoForm onCreate={handleCreate} />

          {loading ? (
            <div className="dashboard-loader">
              <Loader />
            </div>
          ) : todos.length === 0 ? (
            <div className="empty-state">
              <p className="empty-icon">📋</p>
              <p className="empty-text">No todos yet!</p>
              <p className="empty-sub">Add your first todo above to get started.</p>
            </div>
          ) : (
            <div className="todo-list">
              {pending.length > 0 && (
                <section>
                  <h3 className="section-label">Pending ({pending.length})</h3>
                  {pending.map((todo) => (
                    <TodoCard
                      key={todo.id}
                      todo={todo}
                      onUpdate={handleUpdate}
                      onDelete={handleDelete}
                      onToggle={handleToggle}
                    />
                  ))}
                </section>
              )}

              {completed.length > 0 && (
                <section>
                  <h3 className="section-label section-label--done">
                    Completed ({completed.length})
                  </h3>
                  {completed.map((todo) => (
                    <TodoCard
                      key={todo.id}
                      todo={todo}
                      onUpdate={handleUpdate}
                      onDelete={handleDelete}
                      onToggle={handleToggle}
                    />
                  ))}
                </section>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
