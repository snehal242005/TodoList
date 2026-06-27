import { useState } from 'react';

export default function TodoForm({ onSubmit }) {
  const [title,       setTitle]       = useState('');
  const [description, setDescription] = useState('');
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await onSubmit(title.trim(), description.trim());
      setTitle('');
      setDescription('');
    } catch {
      setError('Failed to add todo. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="todo-form" onSubmit={handleSubmit}>
      <h2 className="todo-form-heading">
        Add New Todo
      </h2>

      {error && <p className="form-error">⚠ {error}</p>}

      <div className="form-fields">
        <input
          className="form-input"
          type="text"
          placeholder="What needs to be done? *"
          value={title}
          onChange={(e) => { setTitle(e.target.value); setError(''); }}
          disabled={loading}
          maxLength={255}
          autoFocus
        />
        <input
          className="form-input"
          type="text"
          placeholder="Add a description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={loading}
          maxLength={1000}
        />
        <button className="form-submit" type="submit" disabled={loading}>
          {loading ? 'Adding…' : '+ Add Todo'}
        </button>
      </div>
    </form>
  );
}
