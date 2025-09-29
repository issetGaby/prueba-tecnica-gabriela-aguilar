"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User } from "@/types/auth";
import { authService } from "@/services/auth-service";
import Title from "@/components/UI/Title";
import Button from "@/components/UI/Button";
import FormInput from "@/components/UI/FormInput";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const token = await authService.getValidToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const userData = await authService.getCurrentUser(token);
      setUser(userData);
      setFormData({
        name: userData.name,
        email: userData.email,
      });
    } catch (error) {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setUpdating(true);
    try {
      const token = await authService.getValidToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const updatedUser = await authService.updateUser(token, { 
        name: formData.name 
      });
      setUser(updatedUser);
      setEditing(false);
    } catch (error) {
      console.error("Error actualizando usuario:", error);
    } finally {
      setUpdating(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || "",
      email: user?.email || "",
    });
    setEditing(false);
  };

  const handleLogout = () => {
    authService.clearTokens();
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>No se pudo cargar el usuario</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="bg-[var(--GrisFondo)]">
        <div className="max-w-6xl mx-auto md:px-[50px] px-[16px] py-10">
          <Title titulo="Mi Perfil" className="text-left" />
        </div>
      </div>
      
      <div className="max-w-6xl mx-auto md:px-[50px] px-[16px] py-10">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-sm p-6 md:p-8">
          {/* Información del perfil */}
          {!editing ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-sm font-medium text-gray-500 block mb-1">
                    Nombre
                  </label>
                  <p className="text-gray-900 font-medium">{user.name}</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-sm font-medium text-gray-500 block mb-1">
                    Email
                  </label>
                  <p className="text-gray-900 font-medium">{user.email}</p>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <label className="text-sm font-medium text-gray-500 block mb-1">
                  Fecha de creación
                </label>
                <p className="text-gray-900 font-medium">
                  {new Date(user.createdAt).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <Button
                  onClick={() => setEditing(true)}
                  className="bg-[var(--AzulPrincipal)] hover:bg-blue-700"
                >
                  Editar Perfil
                </Button>
                
                <Button
                  onClick={() => router.push("/dashboard")}
                  type="button"
                  className="bg-gray-500 hover:bg-gray-600"
                >
                  Volver al Dashboard
                </Button>
                
                <Button
                  onClick={handleLogout}
                  type="button"
                  className="bg-red-500 hover:bg-red-600"
                >
                  Cerrar Sesión
                </Button>
              </div>
            </div>
          ) : (
            /* Formulario de edición */
            <form onSubmit={handleUpdate} className="space-y-6">
              <div className="grid grid-cols-1 gap-6">
                <FormInput
                  label="Nombre"
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required={true}
                  placeholder="Ingresa tu nombre"
                  icon="/email-icon.svg"
                />

                <FormInput
                  label="Email"
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required={true}
                  placeholder="Ingresa tu email"
                   icon="/email-icon.svg"
                />

                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-sm font-medium text-gray-500 block mb-1">
                    Fecha de creación
                  </label>
                  <p className="text-gray-900 font-medium">
                    {new Date(user.createdAt).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <Button
                  type="submit"
                  loading={updating}
                  disabled={updating}
                  className="bg-green-600 hover:bg-green-700"
                >
                  Guardar Cambios
                </Button>
                
                <Button
                  type="button"
                  onClick={handleCancel}
                  disabled={updating}
                  className="bg-gray-500 hover:bg-gray-600"
                >
                  Cancelar
                </Button>
                
                <Button
                  type="button"
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600"
                >
                  Cerrar Sesión
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}