"use client";

import React from "react";
import Image, { StaticImageData } from "next/image";
//import iconButton from "@/public/boton-icon.svg";
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  loading?: boolean;
  disabled?: boolean;
  className?: string;
  icon?: boolean; 
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = "button",
  loading = false,
  disabled = false,
  className,
  icon = true
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={loading || disabled}
      className={`flex gap-2 opacity-100 px-[30px] py-3 rounded-[7px] border font-semibold text-[14px] 
      text-center text-white w-fit m-auto
      cursor-pointer items-center 
      transition-transform duration-200 ease-in-out
      hover:scale-105
      disabled:opacity-50 disabled:cursor-not-allowed flex-row-reverse
      ${className}`}
    >
      {icon && (
        <Image
          src="/boton-icon.svg"
          alt="Flecha"
          width={18}
          height={18}
          className="inline-block"
        />
      )}
      {loading ? "Cargando..." : children}
    </button>
  );
};

export default Button;
