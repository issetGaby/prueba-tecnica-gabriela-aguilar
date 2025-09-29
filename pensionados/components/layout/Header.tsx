"use cliente";
import Image from "next/image";
//import logoPortal from "@/public/logo-portal.svg"
function Header() {
    return (
        <header className="w-full">
  <div className="max-w-6xl mx-auto px-[50px] max-[500px]:px-[16px] py-[15px] flex justify-start">
    <Image
      src="/logo-portal.svg"
      width={462}
      height={60}
      alt="logo de Portal de positiva"
    />
  </div>

  <div className="flex w-full">
    <div className="bg-[var(--AzulPrincipal)] h-2.5 w-1/2"></div>
    <div className="bg-[var(--NaranjaPrincipal)] h-2.5 w-1/2"></div>
  </div>
</header>

      );
}

export default Header;