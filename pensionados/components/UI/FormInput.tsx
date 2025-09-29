// components/FormInput.tsx
import Image from "next/image";
import React from "react";

interface FormInputProps {
  label: string;
  type?: string;
  id: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  placeholder?: string;
  icon?: string; 
}

const FormInput: React.FC<FormInputProps> = ({
  label,
  type = "text",
  id,
  name,
  value,
  onChange,
  required = false,
  placeholder,
  icon,
}) => {
  return (
    <div className="flex flex-col gap-2 w-full">
      <label htmlFor={id} className="text-sm font-medium text-[var(--GrisTexCard)] font-sm">
        {label}
      </label>

      <div className="relative flex items-center w-full">
        
        {icon && (
          <span className="absolute left-3 text-gray-500 flex items-center pointer-events-none">
            {<Image src={icon} width={22} height={22} alt="icon"/>}
          </span>
        )}

        <input
          type={type}
          id={id}
          name={name}
          value={value}
          onChange={onChange}
          required={required}
          placeholder={placeholder}
          className={`
            w-full h-[39px] rounded-[7px] border border-[var(--GrisFormularios)]
            pl-10 pr-4 py-2 
            text-black placeholder-black/50
            fontRoboto font-normal
            md:text-[16px] text-[14px]
            focus:outline-none focus:ring-2 focus:ring-[var(--AzulPrincipal)]
          `}
        />
      </div>
    </div>
  );
};

export default FormInput;
