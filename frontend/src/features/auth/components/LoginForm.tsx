import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import InputField from '../../../components/common/InputField';
import SocialButton from '../../../components/common/SocialButton';

const DEFAULT_USERNAME = 'admin';
const DEFAULT_PASSWORD = 'admin123';

const LoginForm: React.FC = () => {
  const [username, setUsername] = useState(DEFAULT_USERNAME);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    if (username !== DEFAULT_USERNAME || password !== DEFAULT_PASSWORD) {
      setError('Sai tai khoan hoac mat khau.');
      return;
    }

    setError('');
    navigate('/dashboard');
  };

  return (
    <div className="max-w-md w-full mx-auto">
      <div className="mb-10">
        <h2 className="text-3xl font-headline font-bold text-on-surface mb-2">Welcome back</h2>
        <p className="text-on-surface-variant">Dang nhap voi tai khoan mac dinh de truy cap he thong.</p>
      </div>
      <form className="space-y-6" onSubmit={handleLogin}>
        <InputField
          label="Tai Khoan"
          icon="person"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="admin"
        />
        <InputField
          label="Mat Khau"
          icon="lock"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="admin123"
        />
        {error ? <p className="text-sm text-red-500">{error}</p> : null}
        <p className="text-sm text-on-surface-variant">Tai khoan: admin | Mat khau: admin123</p>
        <button type="submit" className="w-full py-4 bg-primary text-on-primary font-bold rounded-full shadow-lg">
          Log In
        </button>
        <SocialButton text="Continue with Google" icon="Google" />
      </form>
    </div>
  );
};

export default LoginForm;
