import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../api';

const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());

const PASSWORD_RULES = [
  { id: 'len',   label: 'At least 8 characters',              test: (p) => p.length >= 8 },
  { id: 'upper', label: 'At least 1 uppercase letter (A–Z)',  test: (p) => /[A-Z]/.test(p) },
  { id: 'lower', label: 'At least 1 lowercase letter (a–z)',  test: (p) => /[a-z]/.test(p) },
  { id: 'digit', label: 'At least 1 number (0–9)',            test: (p) => /[0-9]/.test(p) },
  { id: 'spec',  label: 'At least 1 special character (!@#$%^&*)', test: (p) => /[!@#$%^&*]/.test(p) },
];

function getStrength(password) {
  const passed = PASSWORD_RULES.filter(r => r.test(password)).length;
  if (passed <= 2) return { label: 'Weak',   cls: 'strength--weak',   width: '33%' };
  if (passed <= 4) return { label: 'Medium', cls: 'strength--medium', width: '66%' };
  return             { label: 'Strong',  cls: 'strength--strong', width: '100%' };
}

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [confirm,  setConfirm]  = useState('');
  const [errors,   setErrors]   = useState({});
  const [apiError, setApiError] = useState('');
  const [loading,  setLoading]  = useState(false);
  const [touched,  setTouched]  = useState({ password: false });
  const navigate = useNavigate();

  const strength = getStrength(password);
  const allRulesPassed = PASSWORD_RULES.every(r => r.test(password));

  const validate = () => {
    const e = {};
    if (!username.trim())           e.username = 'Username is required.';
    else if (username.trim().length < 3) e.username = 'Username must be at least 3 characters.';

    if (!email.trim())              e.email = 'Email is required.';
    else if (!isValidEmail(email))  e.email = 'Enter a valid email (e.g. name@domain.com).';

    if (!password)                  e.password = 'Password is required.';
    else if (!allRulesPassed)       e.password = 'Password does not meet all requirements.';

    if (!confirm)                   e.confirm = 'Please confirm your password.';
    else if (confirm !== password)  e.confirm = 'Passwords do not match.';

    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    setTouched({ password: true });
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    try {
      await registerUser(username.trim(), email.trim(), password);
      navigate('/login', { replace: true });
    } catch (err) {
      console.error('Register error status:', err.response?.status);
      console.error('Register error data:',   err.response?.data);
      console.error('Register error message:', err.message);

      const data = err.response?.data;
      const message =
        data?.message ||
        data?.errors?.email ||
        data?.errors?.username ||
        (err.message === 'Network Error'
          ? 'Cannot reach the server. Check that the backend is running on port 8080.'
          : `Registration failed (${err.response?.status ?? 'unknown error'}). Please try again.`);

      setApiError(message);
    } finally {
      setLoading(false);
    }
  };

  const clear = (field) => setErrors(prev => ({ ...prev, [field]: '' }));

  return (
    <div className="auth-page">
      <div className="auth-card auth-card--wide">
        <div className="auth-logo-badge">✓</div>
        <h1 className="auth-title">Create account</h1>
        <p className="auth-sub">Start organizing your tasks today</p>

        {apiError && <div className="auth-api-error">⚠ {apiError}</div>}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>

          {/* Username */}
          <div className="field-group">
            <label className="field-label" htmlFor="reg-username">Username</label>
            <input
              id="reg-username"
              type="text"
              className={`field-input ${errors.username ? 'field-input--err' : ''}`}
              placeholder="Min. 3 characters"
              value={username}
              onChange={(e) => { setUsername(e.target.value); clear('username'); }}
              disabled={loading}
              autoFocus
            />
            {errors.username && <p className="field-error">✗ {errors.username}</p>}
          </div>

          {/* Email */}
          <div className="field-group">
            <label className="field-label" htmlFor="reg-email">Email address</label>
            <input
              id="reg-email"
              type="email"
              className={`field-input ${errors.email ? 'field-input--err' : ''}`}
              placeholder="you@example.com"
              value={email}
              onChange={(e) => { setEmail(e.target.value); clear('email'); }}
              disabled={loading}
              autoComplete="email"
            />
            {errors.email && <p className="field-error">✗ {errors.email}</p>}
          </div>

          {/* Password */}
          <div className="field-group">
            <label className="field-label" htmlFor="reg-password">Password</label>
            <input
              id="reg-password"
              type="password"
              className={`field-input ${errors.password ? 'field-input--err' : ''}`}
              placeholder="Create a strong password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setTouched(p => ({ ...p, password: true }));
                clear('password');
              }}
              disabled={loading}
              autoComplete="new-password"
            />
            {errors.password && <p className="field-error">✗ {errors.password}</p>}

            {/* Strength bar — shown as soon as user starts typing */}
            {touched.password && password.length > 0 && (
              <div className="strength-wrap">
                <div className="strength-bar">
                  <div
                    className={`strength-fill ${strength.cls}`}
                    style={{ width: strength.width }}
                  />
                </div>
                <span className={`strength-label ${strength.cls}`}>
                  {strength.label}
                </span>
              </div>
            )}

            {/* Per-rule checklist */}
            {touched.password && (
              <ul className="rules-list">
                {PASSWORD_RULES.map(rule => {
                  const ok = rule.test(password);
                  return (
                    <li key={rule.id} className={`rule ${ok ? 'rule--pass' : 'rule--fail'}`}>
                      <span className="rule-icon">{ok ? '✓' : '✗'}</span>
                      {rule.label}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* Confirm password */}
          <div className="field-group">
            <label className="field-label" htmlFor="reg-confirm">Confirm password</label>
            <input
              id="reg-confirm"
              type="password"
              className={`field-input ${errors.confirm ? 'field-input--err' : ''}`}
              placeholder="Re-enter your password"
              value={confirm}
              onChange={(e) => { setConfirm(e.target.value); clear('confirm'); }}
              disabled={loading}
              autoComplete="new-password"
            />
            {errors.confirm && <p className="field-error">✗ {errors.confirm}</p>}
          </div>

          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
