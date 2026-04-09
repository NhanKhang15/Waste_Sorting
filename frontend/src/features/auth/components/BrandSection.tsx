import React from 'react';

const BrandSection: React.FC = () => {
  return (
    <section className="hidden md:flex flex-col justify-between p-12 bg-surface-container-lowest relative overflow-hidden">
      <div className="z-10">
        <div className="flex items-center gap-2 mb-12">
          <span className="material-symbols-outlined text-primary text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
          <span className="text-2xl font-headline font-bold text-primary tracking-tighter">WasteWise</span>
        </div>
        <h1 className="text-6xl font-headline font-extrabold text-on-surface tracking-tight leading-[1.1] mb-8">
          Rooted in <br/><span className="text-primary-container">Sustainability.</span>
        </h1>
        <p className="text-on-surface-variant text-lg leading-relaxed max-w-sm">
          Join our digital arboretum and transform the way you manage waste through intelligent classification.
        </p>
      </div>
      {/* ... Phần Avatar và icon trang trí ... */}
    </section>
  );
};

export default BrandSection;