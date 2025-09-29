"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth-service";
//import passwordIcon from "@/public/lock.svg";
//import emailIcon from "@/public/email-icon.svg"
import FormInput from "../UI/FormInput";
import Button from "../UI/Button";
export default function LoginForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (!formData.email || !formData.password) {
      setError("Todos los campos son requeridos");
      setLoading(false);
      return;
    }

    try {
      const response = await authService.login(formData);
      authService.setTokens(response.accessToken, response.refreshToken);

      router.push("/dashboard");
    } catch (err) {
      setError("Credenciales inválidas");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full flex flex-col gap-[20px]">
      <FormInput
        label="Correo electrónico*"
        type="email"
        id="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        required
        placeholder="Ingresa tu correo electrónico"
        icon="/email-icon.svg"
      />

      <FormInput
        label="Contraseña*"
        type="password"
        id="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        required
        placeholder="Ingresa tu contraseña"
        icon="/lock.svg"
      />
      {error && <div>{error}</div>}

       <Button type="submit" loading={loading}  className="hover:bg-[var(--AzulPrincipal)] bg-[var(--NaranjaPrincipal)] " >
        Iniciar sesión
      </Button>
    </form>
  );
}
