import React, { useState } from 'react';
import InputField from '../../../components/common/InputField';
import SocialButton from '../../../components/common/SocialButton';
import { useNavigate } from 'react-router-dom';

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login call API with:", { email, password });
    navigate('/dashboard');
  };

  return (
    <div className="max-w-md w-full mx-auto">
      <div className="mb-10">
        <h2 className="text-3xl font-headline font-bold text-on-surface mb-2">Welcome back</h2>
        <p className="text-on-surface-variant">Enter your credentials to access your account.</p>
      </div>
      <form className="space-y-6" onSubmit={handleLogin}>
        <InputField label="Email Address" icon="mail" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="hello@wastewise.com" />
        <InputField label="Password" icon="lock" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
        <button type="submit" className="w-full py-4 bg-primary text-on-primary font-bold rounded-full shadow-lg">Log In</button>
        <SocialButton text="Continue with Google" icon="Google" />
      </form>
    </div>
  );
};

export default LoginForm;