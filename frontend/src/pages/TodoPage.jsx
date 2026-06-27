import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TodoForm from '../components/TodoForm';
import TodoCard from '../components/TodoCard';
import { getAllTodos, createTodo, toggleComplete, deleteTodo } from '../api';

export default function TodoPage() {
  const [todos,   setTodos]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const navigate = useNavigate();

  const username = localStorage.getItem('username') || 'there';

  const fetchTodos = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await getAllTodos();
      setTodos(data);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        handleLogout();
      } else {
        setError('Could not connect to the server. Check your internet connection or try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTodos(); }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    navigate('/login', { replace: true });
  };

  const handleCreate = async (title, description) => {
    const { data } = await createTodo(title, description);
    setTodos(prev => [data, ...prev]);
  };

  const handleToggle = async (id) => {
    const { data } = await toggleComplete(id);
    setTodos(prev => prev.map(t => t.id === id ? data : t));
  };

  const handleDelete = async (id) => {
    await deleteTodo(id);
    setTodos(prev => prev.filter(t => t.id !== id));
  };

  const completedCount = todos.filter(t => t.is_completed).length;

  return (
    <div>
      <header className="header">
        <div className="header-inner">
          <div className="header-logo">✓</div>
          <div className="header-text">
            <h1 className="header-title">My Todo List</h1>
            <p className="header-sub">Welcome back, {username}!</p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <main className="main">
        <TodoForm onSubmit={handleCreate} />

        {todos.length > 0 && !loading && (
          <div className="stats">
            <span>{todos.length} total</span>
            <span className="stats-dot">·</span>
            <span className="stats-done">{completedCount} completed</span>
            <span className="stats-dot">·</span>
            <span className="stats-todo">{todos.length - completedCount} pending</span>
          </div>
        )}

        {loading && (
          <div className="spinner-wrap">
            <div className="spinner" />
            <p className="spinner-label">Loading your todos…</p>
          </div>
        )}

        {error && !loading && (
          <div className="error-banner">
            <span>⚠ {error}</span>
            <button className="retry-btn" onClick={fetchTodos}>Retry</button>
          </div>
        )}

        {!loading && !error && todos.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p className="empty-text">No todos yet!</p>
            <p className="empty-hint">Use the form above to add your first task.</p>
          </div>
        )}

        {!loading && !error && (
          <ul className="todo-list">
            {todos.map(todo => (
              <li key={todo.id}>
                <TodoCard
                  todo={todo}
                  onToggle={handleToggle}
                  onDelete={handleDelete}
                />
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
