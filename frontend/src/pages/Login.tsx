import React from 'react';
import BrandSection from '../features/auth/components/BrandSection';
import LoginForm from '../features/auth/components/LoginForm';

const Login: React.FC = () => {
  return (
    <main className="min-h-screen flex items-center justify-center p-6 bg-editorial-gradient relative overflow-hidden font-body">
      <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 bg-surface-container-low rounded-[2.5rem] overflow-hidden shadow-2xl z-10">
        <BrandSection />
        <section className="flex flex-col justify-center p-8 md:p-16 bg-surface-container-low">
          <LoginForm />
        </section>
      </div>
    </main>
  );
};

export default Login;