import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { todosAPI } from '../services/api';

export function useTodos() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await todosAPI.getAll();
      setTodos(data);
    } catch {
      toast.error('Failed to load todos');
    } finally {
      setLoading(false);
    }
  }, []);

  const createTodo = async (title, description) => {
    const { data } = await todosAPI.create(title, description);
    setTodos((prev) => [data, ...prev]);
    toast.success('Todo created!');
    return data;
  };

  const updateTodo = async (id, updates) => {
    const { data } = await todosAPI.update(id, updates);
    setTodos((prev) => prev.map((t) => (t.id === id ? data : t)));
    toast.success('Todo updated!');
    return data;
  };

  const deleteTodo = async (id) => {
    await todosAPI.delete(id);
    setTodos((prev) => prev.filter((t) => t.id !== id));
    toast.success('Todo deleted!');
  };

  const toggleTodo = async (todo) => {
    const { data } = await todosAPI.update(todo.id, { completed: !todo.completed });
    setTodos((prev) => prev.map((t) => (t.id === todo.id ? data : t)));
  };

  return { todos, loading, fetchTodos, createTodo, updateTodo, deleteTodo, toggleTodo };
}
