import axios from 'axios';

const API = 'http://localhost:8080';

const token = () => localStorage.getItem('token');
const auth  = () => ({ headers: { Authorization: `Bearer ${token()}` } });

// ── Auth ──────────────────────────────────────────────────────
export const loginUser    = (email, password)            =>
  axios.post(`${API}/auth/login`,    { email, password });

export const registerUser = (username, email, password)  =>
  axios.post(`${API}/auth/register`, { full_name: username, email, password });

// ── Todos (all require JWT) ───────────────────────────────────
const T = `${API}/todos/`;

export const getAllTodos     = ()                  => axios.get(T, auth());
export const createTodo     = (title, description)=> axios.post(T, { title, description }, auth());
export const updateTodo     = (id, data)          => axios.patch(`${API}/todos/${id}`, data, auth());
export const toggleComplete = (id)                => axios.patch(`${API}/todos/${id}/complete`, {}, auth());
export const deleteTodo     = (id)                => axios.delete(`${API}/todos/${id}`, auth());
