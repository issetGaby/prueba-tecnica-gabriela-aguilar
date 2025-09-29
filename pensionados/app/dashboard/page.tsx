"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import Title from "@/components/UI/Title";
import Button from "@/components/UI/Button";
import Link from "next/link";
export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="min-h-screen">
      <div className="bg-[var(--GrisFondo)] ">
        <div className="max-w-6xl mx-auto md:px-[50px] px-[16px] py-10 ">
          <Title
            titulo="Bienvenido al "
            destacado="área protegida"
            className="text-left"
          />
        </div>
      </div>
      <div className="max-w-6xl mx-auto md:px-[50px] px-[16px] py-10 flex gap-2 md:gap-10 flex-col sm:flex-row justify-start">
        <Link href="/me">
          <Button
            type="button"
            className="bg-[var(--AzulPrincipal)] hover:bg-[var(--NaranjaPrincipal)] noMargin"
            icon={false}
          >
            Mi Perfil
          </Button>
        </Link>

        <Button
          type="button"
          onClick={() => {
            localStorage.clear();
            router.push("/login");
          }}
          className="hover:bg-[var(--AzulPrincipal)] bg-[var(--NaranjaPrincipal)] noMargin"
            icon={false}
        >
          Cerrar sesión
        </Button>
      </div>
    </div>
  );
}
