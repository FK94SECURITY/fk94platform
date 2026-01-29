import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FK94 Security - Cybersecurity & Personal Privacy",
  description:
    "FK94 Security - Plataforma de ciberseguridad y OSINT. Escaneá tu email, detectá passwords filtrados, analizá tu huella digital.",
  keywords: ["cybersecurity", "OPSEC", "privacy", "security audit", "OSINT"],
  openGraph: {
    title: "FK94 Security - Cybersecurity & Personal Privacy",
    description:
      "FK94 Security - Plataforma de ciberseguridad y OSINT. Escaneá tu email, detectá passwords filtrados, analizá tu huella digital.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "FK94 Security - Cybersecurity & Personal Privacy",
    description:
      "FK94 Security - Plataforma de ciberseguridad y OSINT. Escaneá tu email, detectá passwords filtrados, analizá tu huella digital.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-black text-white antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
