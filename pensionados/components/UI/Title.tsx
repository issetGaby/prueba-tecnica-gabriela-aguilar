import React from "react";

interface TitleProps {
  titulo: string;
  destacado?: string;
  className?: string;
}

const Title: React.FC<TitleProps> = ({ titulo, destacado, className }) => {
  return (
  <h1 className={`text-center font-bold text-2xl md:text-4xl text-[var(--AzulPrincipal)] ${className}`}>
      {titulo}{" "}
      <span className="text-[var(--NaranjaPrincipal)]">{destacado}</span>
    </h1>
  );
};

export default Title;
